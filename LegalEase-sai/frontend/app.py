import os
import sys
from pathlib import Path
import requests
import streamlit as st

# Configure system path for modular imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from ai_core.generator import (
    sanitize_text,
    format_docx,
    format_pdf,
    format_html_preview,
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="LegalEase - AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern, Professional Styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        font-weight: 800;
        margin-top: -10px;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        text-align: center;
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    .badge-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    .footer-note {
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "generated_document" not in st.session_state:
    st.session_state["generated_document"] = ""
if "is_editing" not in st.session_state:
    st.session_state["is_editing"] = False
if "last_doc_type" not in st.session_state:
    st.session_state["last_doc_type"] = "Freelance Work Contract"
if "last_terms" not in st.session_state:
    st.session_state["last_terms"] = ""

# ---------------------------------------------------------
# Header Section (3-Column Layout for Center-Aligned Logo)
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_path = config.LOGO_PATH
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("<h2 style='text-align: center;'>⚖️ LegalEase</h2>", unsafe_allow_html=True)

    st.markdown("<h1 class='main-title'>LegalEase</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI-Powered Legal Document Generator</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: Presets, Backend Status & Model Info
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check Backend Status
    backend_live = False
    try:
        health_resp = requests.get(config.API_BASE_URL, timeout=2)
        if health_resp.status_code == 200:
            backend_live = True
            st.success("🟢 System Engine Online")
        else:
            st.warning("🟡 System Responded with Warning")
    except Exception:
        st.error("🔴 Server Offline (Port 8000)")

    st.markdown("---")
    st.subheader("📋 Document Presets")
    preset_choice = st.selectbox(
        "Load Quick Template:",
        [
            "Select a preset...",
            "Freelance Work Contract",
            "Non-Disclosure Agreement (NDA)",
            "Residential Lease Agreement",
            "Employment Offer Letter"
        ]
    )

    # Preset templates mapping
    PRESETS = {
        "Freelance Work Contract": {
            "type": "Freelance Work Contract",
            "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
            "terms": "Payment to be made within 30 days of invoice;\nThe provider agrees to deliver work by the agreed deadline;\nConfidentiality must be maintained at all times;\nEither party may terminate with 15 days notice",
            "date": "April 10, 2025"
        },
        "Non-Disclosure Agreement (NDA)": {
            "type": "Non-Disclosure Agreement (NDA)",
            "parties": "InnovateX Solutions (Disclosing Party), John Smith (Receiving Party)",
            "terms": "Confidential information shall remain protected for a period of two (2) years;\nInformation includes technical architecture, algorithms, and financial projections;\nReceiving Party agrees not to reverse engineer disclosed intellectual property;\nRemedies include immediate injunctive relief and damages in court of competent jurisdiction",
            "date": "May 15, 2025"
        },
        "Residential Lease Agreement": {
            "type": "Residential Lease Agreement",
            "parties": "Alice Smith (Tenant), XYZ Realty Holdings (Landlord)",
            "terms": "Monthly rent of $2,200 payable on or before the 1st of every calendar month;\nSecurity deposit of $2,200 deposited upon execution of lease;\nNo subletting or alterations permitted without prior written consent;\nTenant responsible for utilities including electricity, water, and internet",
            "date": "July 01, 2025"
        },
        "Employment Offer Letter": {
            "type": "Employment Offer Letter",
            "parties": "Apex Technologies LLC (Employer), Robert Davis (Employee)",
            "terms": "Full-time position as Senior AI Software Engineer;\nAnnual base salary of $135,000 paid bi-weekly;\nStandard corporate health insurance, 401(k) match, and 20 days PTO;\nEmployment is at-will subject to standard 30-day notice period",
            "date": "September 01, 2025"
        }
    }

    # Handle preset selection
    selected_preset = PRESETS.get(preset_choice, {})

    st.markdown("---")
    st.markdown(
        """
        **System Specs:**
        - **Engine:** LegalEase Core
        - **AI Core:** Google Gemini 3.1 Pro
        - **Supported Exports:** TXT, DOCX, PDF
        """
    )

# ---------------------------------------------------------
# Main UI Layout: Input Form & Actions
# ---------------------------------------------------------
st.markdown("### 📝 Enter Agreement Details")

with st.form("legal_doc_form", clear_on_submit=False):
    col_type, col_date = st.columns([2, 1])
    
    with col_type:
        document_type = st.text_input(
            "Document Type",
            value=selected_preset.get("type", "Freelance Work Contract"),
            help="E.g., Agreement, Contract, NDA, Lease Agreement, Employment Offer Letter"
        )
    with col_date:
        dates = st.text_input(
            "Effective Date",
            value=selected_preset.get("date", "April 10, 2025"),
            help="E.g., April 10, 2025 or 10/04/2025"
        )

    parties = st.text_area(
        "Parties Involved",
        value=selected_preset.get("parties", "Jane Doe (Service Provider), TechNova Inc. (Client)"),
        height=75,
        help="Specify names and roles of all legal entities or individuals involved"
    )

    terms = st.text_area(
        "Terms & Conditions (Use semicolons for bullet points)",
        value=selected_preset.get(
            "terms",
            "Payment to be made within 30 days of invoice;\n"
            "The provider agrees to deliver work by the agreed deadline;\n"
            "Confidentiality must be maintained at all times;\n"
            "Either party may terminate with 15 days notice"
        ),
        height=130,
        help="Input specific clauses, rules, and conditions. Separate each clause with a semicolon (;)"
    )

    generate_btn = st.form_submit_button("⚡ Generate Document", use_container_width=True)

# ---------------------------------------------------------
# Handle Document Generation Request
# ---------------------------------------------------------
if generate_btn:
    if not document_type.strip() or not parties.strip():
        st.error("⚠️ Please specify both the Document Type and Parties Involved.")
    else:
        payload = {
            "document_type": document_type.strip(),
            "parties": parties.strip(),
            "terms": terms.strip(),
            "dates": dates.strip(),
            "api_key": config.GEMINI_API_KEY,
        }

        with st.spinner("🤖 Consulting Google Gemini 3.1 Pro & Drafting Legally Structured Agreement..."):
            try:
                response = requests.post(config.GENERATE_ENDPOINT, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    generated_text = data.get("document", "")
                    st.session_state["generated_document"] = sanitize_text(generated_text)
                    st.session_state["last_doc_type"] = document_type.strip()
                    st.session_state["last_terms"] = terms.strip()
                    st.session_state["is_editing"] = False
                    st.success("🎉 Legal Document successfully generated by Google Gemini 3.1 Pro!")
                else:
                    err_detail = response.json().get("detail", response.text)
                    st.error(f"❌ Document Generation Failed: {err_detail}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the Backend Server on port 8000. Please start the service first.")
            except Exception as e:
                st.error(f"❌ Error communicating with backend: {e}")

# ---------------------------------------------------------
# Document Output, Editable Area & Multi-Format Downloads
# ---------------------------------------------------------
current_doc = st.session_state.get("generated_document", "")

if current_doc:
    st.markdown("---")
    st.subheader("📄 Generated Document Preview & Controls")

    # Action Toolbar: Edit Toggle
    col_t1, col_t2 = st.columns([3, 1])
    with col_t2:
        edit_label = "✖️ Close Editor" if st.session_state["is_editing"] else "✏️ Click to Edit Document"
        if st.button(edit_label, use_container_width=True):
            st.session_state["is_editing"] = not st.session_state["is_editing"]
            st.rerun()

    # Editable Text Area Window (Activity 4.2 / Milestone 4)
    if st.session_state["is_editing"]:
        st.info("💡 You can refine or modify any clause below. Changes will immediately update download files.")
        edited_content = st.text_area(
            "Document Editor",
            value=current_doc,
            height=380,
            key="edited_doc_text"
        )
        if st.button("💾 Apply & Save Edits"):
            st.session_state["generated_document"] = sanitize_text(edited_content)
            current_doc = st.session_state["generated_document"]
            st.success("✅ Edits applied successfully!")
            st.rerun()

    # Stylized HTML Preview Rendering (Activity 4.2 Step 2)
    st.markdown(format_html_preview(current_doc), unsafe_allow_html=True)

    # Multi-Format Download Options (Activity 4.2 Step 4)
    st.markdown("### 📥 Download Document")
    st.markdown("Choose your preferred format for exporting the finalized agreement:")

    col_txt, col_docx, col_pdf = st.columns(3)

    doc_title_clean = "".join(c for c in st.session_state["last_doc_type"] if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    
    # 1. Plain Text Download
    with col_txt:
        st.download_button(
            label="📄 Download .TXT",
            data=current_doc.encode("utf-8"),
            file_name=f"{doc_title_clean}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # 2. Microsoft Word DOCX Download
    with col_docx:
        try:
            docx_stream = format_docx(
                text=current_doc,
                doc_type=st.session_state["last_doc_type"],
                terms=st.session_state.get("last_terms", ""),
                logo_path=str(config.LOGO_PATH) if config.LOGO_PATH.exists() else None
            )
            st.download_button(
                label="📘 Download .DOCX",
                data=docx_stream.getvalue(),
                file_name=f"{doc_title_clean}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"DOCX error: {e}")

    # 3. Branded PDF Download
    with col_pdf:
        try:
            pdf_bytes = format_pdf(
                text=current_doc,
                doc_type=st.session_state["last_doc_type"],
                terms=st.session_state.get("last_terms", ""),
                logo_path=str(config.LOGO_PATH) if config.LOGO_PATH.exists() else None
            )
            st.download_button(
                label="📕 Download .PDF",
                data=pdf_bytes,
                file_name=f"{doc_title_clean}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

st.markdown("<p class='footer-note' style='text-align: center; color: #64748b; font-size: 0.92rem; font-weight: 700; margin-top: 50px; padding-top: 15px; border-top: 1px solid #cbd5e1; user-select: none; pointer-events: none;'>LegalEase AI-Powered Legal Document Generator © 2026 | Built with FastAPI & Streamlit BY LILY</p>", unsafe_allow_html=True)
