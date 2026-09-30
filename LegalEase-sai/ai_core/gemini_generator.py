import os
import sys
import logging
import warnings
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiDocumentGenerator:
    """
    Core AI Generator that integrates with Google Gemini (gemini-1.5-pro)
    to draft structured, professional legal documents.
    Automatically resolves and falls back to active Gemini models (like gemini-1.5-flash)
    if gemini-1.5-pro is not enabled for the specific API key tier.
    """

    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or config.DEFAULT_MODEL or "gemini-1.5-pro"
        self.model = None
        self._initialize_model()

    def _initialize_model(self, custom_key: str = None):
        """Initializes the Gemini GenerativeModel with the provided API key."""
        target_key = custom_key or self.api_key or os.getenv("GEMINI_API_KEY", "") or getattr(config, "GEMINI_API_KEY", "")
        if target_key:
            if not GENAI_AVAILABLE:
                raise ImportError("google-generativeai package is not installed. Please run: pip install google-generativeai")
            genai.configure(api_key=target_key)
            self.model = self._create_model_instance(self.model_name)
            self.api_key = target_key
            logger.info(f"Gemini GenerativeModel configured with target model: {self.model_name}")
        else:
            self.model = None

    def _create_model_instance(self, name: str):
        """Creates a GenerativeModel with consistent legal generation hyperparameters."""
        return genai.GenerativeModel(
            model_name=name,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.95,
                "max_output_tokens": 4096,
            }
        )

    def _execute_with_model_fallback(self, prompt: str) -> str:
        """
        Executes generate_content with automatic fallback if the requested model 
        returns a 404 (e.g. Free Tier keys that support gemini-1.5-flash or gemini-2.0-flash).
        """
        candidate_models = [
            self.model_name,
            "gemini-2.5-flash",
            "gemini-flash-latest",
            "gemini-3.1-pro-preview",
            "gemini-2.5-pro",
            "gemini-pro-latest"
        ]

        # Preserve order without duplicates
        candidates = []
        for c in candidate_models:
            if c and c not in candidates:
                candidates.append(c)

        last_error = None

        # 1. Try candidate models
        for candidate in candidates:
            try:
                logger.info(f"Sending legal generation request to Google Gemini model: '{candidate}'...")
                model = self._create_model_instance(candidate)
                response = model.generate_content(prompt)
                if response and response.text:
                    self.model = model
                    self.model_name = candidate
                    logger.info(f"Successfully generated legal document with model: {candidate}")
                    return response.text.strip()
            except Exception as e:
                err_str = str(e)
                last_error = e
                # If 404, not found, or limit 0 on this tier, try next candidate
                if any(phrase in err_str.lower() for phrase in ["404", "not found", "limit: 0", "quota exceeded"]):
                    logger.warning(f"Model '{candidate}' unavailable on this key tier ({err_str[:70]}...). Trying next candidate...")
                    continue
                else:
                    raise e

        # 2. Dynamic discovery via ListModels if static candidates return 404
        try:
            logger.info("Querying Google ModelService.ListModels for available models on this key...")
            available_models = [
                m.name.replace("models/", "")
                for m in genai.list_models()
                if "generateContent" in getattr(m, "supported_generation_methods", [])
            ]
            for discovered_model in available_models:
                if discovered_model not in candidates:
                    try:
                        logger.info(f"Trying discovered model: '{discovered_model}'...")
                        model = self._create_model_instance(discovered_model)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            self.model = model
                            self.model_name = discovered_model
                            return response.text.strip()
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error querying ListModels: {e}")

        # If all failed, re-raise the original error
        raise last_error

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str, api_key: str = None) -> str:
        """
        Generates a comprehensive legal document using Google Gemini AI.
        """
        if api_key:
            self._initialize_model(api_key)
        elif self.model is None:
            self._initialize_model()

        if self.model is None or not self.api_key:
            raise ValueError(
                "Google Gemini API Key is missing. Please set your GEMINI_API_KEY in the .env file "
                "or provide it in the configuration to generate legal documents."
            )

        # Formal prompt specification as defined in project documentation
        prompt = (
            f"Generate a comprehensive legal document titled '{document_type}'\n"
            f"Involved parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and conditions: {terms}\n"
            f"Ensure formal legal structure with multiple sections and legal clauses.\n"
            f"Include distinct sections: Title, Preamble/Recitals, Definitions, Operative Clauses, "
            f"Confidentiality, Termination, Governing Law, and Execution/Signatures block.\n"
            f"Do not wrap in markdown code blocks. Do not use raw markdown asterisks (*** or **) for styling."
        )

        raw_result = self._execute_with_model_fallback(prompt)

        # Clean possible markdown wrapping
        cleaned_text = raw_result
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        from ai_core.generator import sanitize_text
        return sanitize_text(cleaned_text)
