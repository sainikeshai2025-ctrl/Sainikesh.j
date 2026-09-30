# LegalEase: AI-Powered Legal Document Generator
## System Architecture & Technical Specifications

### 1. Overview
LegalEase leverages Generative AI (Google Gemini 1.5 Pro) to streamline legal document creation. It produces legally robust, formatted agreements (such as NDAs, Employment Contracts, and Lease Agreements) tailored to user-specified stakeholders, effective dates, and stipulations.

### 2. High-Level Architecture Flow
```
[User Browser]
       │
       ▼
[Streamlit Frontend (port 8501)]
       │
       │ HTTP POST /generate (JSON)
       ▼
[FastAPI Backend (port 8000)] ──► [legalEaseAPI/routes.py]
       │
       ▼
[ai_core/gemini_generator.py]
       │
       │ Google Generative AI SDK (gemini-1.5-pro)
       ▼
[Google Gemini AI Engine]
       │
       ▼ (Returns Structured Legal Text)
[Streamlit Dynamic Preview & Editor]
       │
       ├──► Plain Text (.txt)
       ├──► Microsoft Word (.docx with Logo, Times New Roman, Terms Table, Footer)
       └──► Branded PDF (.pdf with Header Logo, Bold Headings, Terms Bullets, Footer)
```

### 3. Component Details
- **Frontend (`frontend/app.py`):**
  - Intuitive input fields for `document_type`, `parties`, `terms`, and `dates`.
  - Responsive header featuring the centered LegalEase branding logo.
  - Interactive controls including real-time document editing window.
  - Multi-format export engine supporting `.txt`, `.docx`, and `.pdf`.

- **Backend API (`legalEaseAPI/main.py` & `legalEaseAPI/routes.py`):**
  - Built with FastAPI for high-performance async processing.
  - Pydantic validation via `DocumentRequest` schema.
  - CORS middleware enabled for seamless frontend-backend communication.
  - Interactive Swagger documentation at `/docs` and ReDoc at `/redoc`.

- **AI Core (`ai_core/gemini_generator.py` & `ai_core/generator.py`):**
  - Integrates Google Gemini 1.5 Pro (`google-generativeai`).
  - Structured prompt engineering enforcing standard legal conventions (Preamble, Definitions, Operative Clauses, Termination, Governing Law, Signature Blocks).
  - Production-grade fallback generator ensuring zero system downtime.
  - Export utilities: `sanitize_text()`, `format_docx()`, `format_pdf()`, and `format_html_preview()`.
