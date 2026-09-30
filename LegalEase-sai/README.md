# ⚖️ LegalEase: AI-Powered Legal Document Generator

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/AI%20Core-Gemini%201.5%20Pro-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)

**LegalEase** leverages Generative AI (Google Gemini 1.5 Pro) to streamline the drafting of professional, legally binding documents. From Non-Disclosure Agreements (NDAs) to Freelance Contracts and Residential Leases, LegalEase bridges the gap between accessibility and legal precision.

---

## 📑 Table of Contents
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Directory Structure](#-directory-structure)
- [VS Code Setup & Installation](#-vs-code-setup--installation)
- [Running the Application](#-running-the-application)
- [Testing & Verification](#-testing--verification)
- [Export Formats](#-export-formats)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## ✨ Key Features
- **AI Core Integration:** Powered by Google's **Gemini 1.5 Pro** model with structured prompt engineering tailored to legal drafting.
- **FastAPI High-Performance Backend:** Validates input via Pydantic (`DocumentRequest`) and exposes clean, documented REST endpoints.
- **Interactive Streamlit Interface:** Center-aligned branding, preset contract templates, and dynamic reactive status checks.
- **Live Dark-Mode HTML Preview:** Renders an elegant scrollable card featuring semantic HTML, custom badges, and styled legal clauses.
- **In-Browser Document Editor:** Allows users to modify, refine, or append clauses before exporting.
- **Multi-Format Export Engine:**
  - **.TXT:** Clean plain-text formatted output.
  - **.DOCX:** Times New Roman, embedded logo, formal margins, styled clauses, auto-generated Terms Table (Schedule A), and confidentiality footer.
  - **.PDF:** Vector-branded PDF with logo header, bold section titles, bullet-style terms, and page numbering on all pages.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────┐
│       Streamlit Frontend        │  <--- http://localhost:8501
│ (User Input, Preview, Download) │
└────────────────┬────────────────┘
                 │ POST /generate
                 ▼
┌─────────────────────────────────┐
│         FastAPI Backend         │  <--- http://127.0.0.1:8000
│   (Pydantic Validation & CORS)  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       ai_core / Gemini AI       │  <--- Google Gemini 1.5 Pro
│   (Prompt Logic & Procedural)   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     Multi-Format Exporters      │
│   • .TXT   • .DOCX   • .PDF     │
└─────────────────────────────────┘
```

---

## 📂 Directory Structure
```
LEGALEASE/
├── ai_core/
│   ├── __init__.py               # Modular AI package imports
│   ├── gemini_generator.py       # Gemini 1.5 Pro integration & fallback engine
│   └── generator.py              # DOCX, PDF, HTML preview & text sanitization
├── frontend/
│   ├── __init__.py               # Frontend package initialization
│   └── app.py                    # Streamlit web application
├── image/
│   ├── Logo.png                  # Primary LegalEase branding logo
│   └── inverseLogo.png           # Dark-mode / inverted branding logo
├── legalEaseAPI/
│   ├── __init__.py               # Backend package initialization
│   ├── main.py                   # FastAPI app, CORS middleware & health check
│   └── routes.py                 # POST /generate & GET /status routes
├── docs/
│   ├── ARCHITECTURE.md           # System design & architectural diagrams
│   ├── API_DOCUMENTATION.md      # OpenAPI specs & cURL request examples
│   └── USER_GUIDE.md             # Scenario walkthroughs and prompt guide
├── venv/                         # Python Virtual Environment
├── .env                          # Active environment variables
├── .env.example                  # Environment configuration template
├── config.py                     # Centralized settings & path constants
├── requirements.txt              # Production-ready Python dependencies
├── run.bat                       # Windows one-click launcher
├── run.ps1                       # PowerShell one-click launcher
├── run.sh                        # Bash / Linux / macOS launcher
└── README.md                     # Comprehensive project documentation
```

---

## 💻 VS Code Setup & Installation

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **VS Code** with the **Python** extension (`ms-python.python`) installed.

### 2. Clone / Open Project in VS Code
Open the project folder in VS Code:
```bash
code c:\Users\user\Pictures\LegalEase
```

### 3. Set Up Python Virtual Environment
Open a terminal in VS Code (`Ctrl + ` `~`):
```powershell
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows Command Prompt:
.\venv\Scripts\activate.bat
# On macOS / Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Your Google Gemini API Key
Open `.env` in the root folder and paste your Google Gemini API key:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
API_HOST=127.0.0.1
API_PORT=8000
```
> **Note:** If you don't have an API key right away, LegalEase includes a built-in offline legal drafting engine so all features, previews, and exports can be tested immediately!

---

## 🚀 Running the Application

### Option A: One-Click Launch (Recommended)
- **Windows (Command Prompt / Double Click):**
  ```cmd
  run.bat
  ```
- **Windows (PowerShell):**
  ```powershell
  .\run.ps1
  ```
- **Linux / macOS:**
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

### Option B: Run Services Manually (Two Terminals)

**Terminal 1 — Launch FastAPI Backend Server:**
```powershell
.\venv\Scripts\python.exe -m uvicorn legalEaseAPI.main:app --host 127.0.0.1 --port 8000 --reload
```
*API will run at: `http://127.0.0.1:8000` (Swagger UI at `http://127.0.0.1:8000/docs`)*

**Terminal 2 — Launch Streamlit Frontend:**
```powershell
.\venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501
```
*Web App will open automatically at: `http://localhost:8501`*

---

## 🧪 Testing & Verification

### 1. Test Backend API Directly
You can verify the backend health and document generation using `curl` or Python:
```bash
curl http://127.0.0.1:8000/
```
Output:
```json
{"status":"online","service":"LegalEase: AI-Powered Legal Document Generator API","version":"1.0.0"}
```

Test `/generate` endpoint:
```bash
curl -X POST "http://127.0.0.1:8000/generate" -H "Content-Type: application/json" -d "{\"document_type\": \"Non-Disclosure Agreement\", \"parties\": \"Alice (Discloser), Bob (Recipient)\", \"terms\": \"Keep confidential for 2 years; No reverse engineering\", \"dates\": \"May 1, 2025\"}"
```

### 2. Test Frontend Workflow
1. Navigate to `http://localhost:8501`.
2. In the sidebar, select **Freelance Work Contract** or **Non-Disclosure Agreement (NDA)**.
3. Click **⚡ Generate Document**.
4. Observe the stylized dark-mode preview card.
5. Click **✏️ Click to Edit Document**, make a custom modification to a clause, and click **💾 Apply & Save Edits**.
6. Click **📄 Download .TXT**, **📘 Download .DOCX**, and **📕 Download .PDF** to verify file integrity.

---

## 📄 License & Attribution
Developed as part of the **LegalEase SmartBridge AI & Generative AI Initiative**.
Licensed under the MIT License.
