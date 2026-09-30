import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiDocumentGenerator

logger = logging.getLogger(__name__)

# Initialize FastAPI APIRouter
router = APIRouter()

# Initialize the Gemini Document Generator instance
gemini_generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    """
    Pydantic Model to validate document generation requests
    from the Streamlit frontend.
    """
    document_type: str = Field(
        ..., 
        description="Type of legal document (e.g. NDA, Employment Contract, Lease Agreement)",
        examples=["Non-Disclosure Agreement (NDA)"]
    )
    parties: str = Field(
        ..., 
        description="Names and roles of the involved stakeholders",
        examples=["Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)"]
    )
    terms: str = Field(
        ..., 
        description="Semicolon-separated contractual clauses and stipulations",
        examples=["Information must remain confidential for 2 years; Jurisdiction is Delaware"]
    )
    dates: str = Field(
        ..., 
        description="Effective date of the agreement",
        examples=["April 10, 2025"]
    )
    api_key: str = Field(
        default="", 
        description="Optional Gemini API Key provided from frontend",
        examples=["AIzaSy..."]
    )


class DocumentResponse(BaseModel):
    """
    Pydantic Model for legal document generation response
    """
    document: str
    status: str = "success"
    mode: str = "AI / Procedural"


@router.post("/generate", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
def generate_legal_document(request: DocumentRequest):
    """
    Accepts legal document parameters and returns an AI-generated,
    structured legal document ready for preview and export.
    Supports both Gemini 1.5 Pro and Offline Procedural Engine.
    """
    if not request.document_type.strip():
        raise HTTPException(status_code=400, detail="Document type is required.")
    if not request.parties.strip():
        raise HTTPException(status_code=400, detail="Parties information is required.")

    try:
        response_text = gemini_generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
            api_key=request.api_key.strip() if request.api_key else None
        )
        active_mode = "Google Gemini 3.1 Pro" if gemini_generator.model else "Procedural Legal Engine"
        return DocumentResponse(document=response_text, status="success", mode=active_mode)
    except Exception as e:
        logger.error(f"Error during document generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the document: {str(e)}"
        )


@router.get("/status")
def get_status():
    """Returns the operational status of the AI generator"""
    return {
        "status": "online",
        "model": gemini_generator.model_name,
        "ai_available": gemini_generator.model is not None or bool(gemini_generator.api_key)
    }
