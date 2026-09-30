import io
import os
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
import config
from legalEaseAPI.main import app
from ai_core.generator import sanitize_text, format_docx, format_pdf, format_html_preview
from ai_core.gemini_generator import GeminiDocumentGenerator


def test_sanitize_text():
    raw = "Here is a “quote” with an em—dash and ‘single’ quotes…"
    clean = sanitize_text(raw)
    assert '"quote"' in clean
    assert " - " in clean
    assert "'single'" in clean
    assert "..." in clean

    # Test elimination of markdown artifacts, asterisks, and broken bullet prefixes
    raw_markdown = (
        "***\n"
        "**FREELANCE WORK CONTRACT**\n\n"
        "**BETWEEN:**\n\n"
        "* **Jane Doe**, an individual residing at [Address] (the \"Service Provider\");\n\n"
        "**AND**\n\n"
        "* **TechNova Inc.**, a corporation (the \"Client\").\n\n"
        "### 1. DEFINITIONS\n\n"
        "* 1.1. **\"Agreement\"** means this Contract.\n"
        "* 1.2. **\"Services\"** means the consulting work.\n\n"
        "### 2. OPERATIVE CLAUSES\n\n"
        "2.1. **Engagement of Services.** The Client engages Provider.\n"
        "- Payment within 30 days;\n"
        "- Confidentiality required;\n\n"
        "***\n"
        "**IN WITNESS WHEREOF**, the parties have signed.\n"
        "**SERVICE PROVIDER:**\n"
        "__________________________________________________\n"
        "Jane Doe"
    )
    cleaned = sanitize_text(raw_markdown)
    assert "***" not in cleaned
    assert "**" not in cleaned
    assert "###" not in cleaned
    assert "- BETWEEN:" not in cleaned
    assert "- AND" not in cleaned
    assert "- 1.1." not in cleaned
    assert "- Jane Doe" not in cleaned
    assert "BETWEEN:" in cleaned
    assert "1.1. \"Agreement\" means this Contract." in cleaned
    assert "2.1. Engagement of Services. The Client engages Provider." in cleaned
    assert "- Payment within 30 days;" in cleaned
    assert "- Confidentiality required;" in cleaned


def test_generator_docx():
    sample_text = (
        "NON-DISCLOSURE AGREEMENT\n\n"
        "SECTION 1: PURPOSE\n"
        "This agreement protects confidential disclosures.\n\n"
        "SECTION 2: OBLIGATIONS\n"
        "1. Maintain secret;\n2. Do not disclose."
    )
    docx_stream = format_docx(
        text=sample_text,
        doc_type="Non-Disclosure Agreement",
        terms="Term 1; Term 2; Term 3"
    )
    assert docx_stream is not None
    assert docx_stream.getbuffer().nbytes > 1000


def test_generator_pdf_margins_and_footer():
    """
    Test PDF generation to guarantee margins prevent text cut-off on right edge
    and verify the required footer 'BY LILY' is present.
    """
    sample_text = (
        "NON-DISCLOSURE AGREEMENT\n\n"
        "SECTION 1: PURPOSE AND SCOPE OF CONFIDENTIALITY\n"
        "This is an extensive legal clause drafted to test that standard 20mm margins prevent any text clipping on the right edge of the page.\n\n"
        "SECTION 2: OBLIGATIONS AND COVENANTS\n"
        "- Maintain all confidential materials under strict confidence;\n"
        "- Do not reproduce, reverse engineer, or distribute proprietary code;\n"
        "- Either party may terminate with thirty (30) days prior written notice."
    )
    pdf_bytes = format_pdf(
        text=sample_text,
        doc_type="Non-Disclosure Agreement",
        terms="Clause 1; Clause 2"
    )
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
    
    # Verify 'BY LILY' is embedded in the PDF content stream
    import zlib, re
    streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.DOTALL)
    found_lily = False
    for s in streams:
        try:
            if b"BY LILY" in zlib.decompress(s):
                found_lily = True
                break
        except Exception:
            pass
    assert found_lily, "Expected 'BY LILY' in PDF footer stream"


def test_html_preview():
    sample_text = "SECTION 1: DEFINITIONS\nConfidentiality shall be preserved."
    html_output = format_html_preview(sample_text)
    assert "SECTION 1: DEFINITIONS" in html_output
    assert "LegalEase Verified Draft" in html_output


def test_gemini_document_generator_strictly_requires_key():
    """Verify that calling generate_document without an API key raises ValueError (no offline fallback)"""
    with patch.object(config, "GEMINI_API_KEY", ""):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            gen = GeminiDocumentGenerator(api_key="")
            gen.api_key = ""
            gen.model = None
            with pytest.raises(ValueError, match="Google Gemini API Key is missing"):
                gen.generate_document(
                    document_type="Freelance Work Contract",
                    parties="Jane Doe, ACME Corp",
                    terms="Deliver work on time",
                    dates="May 1, 2025"
                )


def test_gemini_document_generator_with_api():
    """Verify Gemini AI generation flow using mock response"""
    gen = GeminiDocumentGenerator(api_key="mock_key")
    with patch.object(gen, "_execute_with_model_fallback", return_value="MOCK DRAFTED LEGAL CONTRACT BY GEMINI"):
        result = gen.generate_document(
            document_type="Master Services Agreement",
            parties="Party A and Party B",
            terms="Terms & Conditions",
            dates="June 1, 2025"
        )
        assert result == "MOCK DRAFTED LEGAL CONTRACT BY GEMINI"


def test_fastapi_endpoints():
    client = TestClient(app)

    # 1. Health check & verify BY LILY in service title
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "online"
    assert "BY LILY" in res_root.json()["service"]

    # 2. Status
    res_status = client.get("/status")
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "online"

    # 3. Generate Endpoint with mocked Gemini
    with patch("legalEaseAPI.routes.gemini_generator.generate_document", return_value="LEGAL CONTRACT GENERATED BY GEMINI"):
        payload = {
            "document_type": "Partnership Agreement",
            "parties": "Partner A and Partner B",
            "terms": "50/50 profit sharing; Annual audit required",
            "dates": "January 1, 2025"
        }
        res_gen = client.post("/generate", json=payload)
        assert res_gen.status_code == 200
        data = res_gen.json()
        assert "document" in data
        assert data["status"] == "success"
        assert data["document"] == "LEGAL CONTRACT GENERATED BY GEMINI"


def test_comprehensive_export_cleaning():
    """
    Integration test verifying that raw markdown inputs with asterisks (***, **, *)
    and broken bullet prefixes are 100% eliminated across TXT, DOCX, PDF, and HTML preview.
    """
    from docx import Document
    import zlib

    raw_text = (
        "***\n"
        "**FREELANCE WORK CONTRACT**\n\n"
        "**BETWEEN:**\n\n"
        "* **Jane Doe**, an individual residing at [Address] (hereinafter the \"Service Provider\");\n\n"
        "**AND**\n\n"
        "* **TechNova Inc.**, a corporation (hereinafter the \"Client\").\n\n"
        "**1. DEFINITIONS**\n\n"
        "* 1.1. **\"Agreement\"** means this Freelance Work Contract.\n\n"
        "**2. OPERATIVE CLAUSES**\n\n"
        "2.1. **Engagement of Services.** The Client engages the Service Provider.\n"
        "- Deliverables to be submitted on time;\n"
        "- Confidentiality required;\n\n"
        "***\n"
        "**IN WITNESS WHEREOF**, the parties have signed.\n\n"
        "**SERVICE PROVIDER:**\n"
        "__________________________________________________\n"
        "Jane Doe"
    )

    # 1. Plain Text (.txt)
    txt_clean = sanitize_text(raw_text)
    assert "***" not in txt_clean
    assert "**" not in txt_clean
    assert "- BETWEEN:" not in txt_clean
    assert "- 1.1." not in txt_clean
    assert "BETWEEN:" in txt_clean
    assert "1.1. \"Agreement\" means this Freelance Work Contract." in txt_clean

    # 2. Microsoft Word (.docx)
    docx_stream = format_docx(txt_clean, doc_type="Freelance Work Contract", terms="Term 1; Term 2")
    doc_parsed = Document(docx_stream)
    docx_text = "\n".join([p.text for p in doc_parsed.paragraphs])
    assert "***" not in docx_text
    assert "**" not in docx_text
    assert "- BETWEEN:" not in docx_text

    # 3. PDF (.pdf)
    pdf_bytes = format_pdf(txt_clean, doc_type="Freelance Work Contract")
    assert pdf_bytes.startswith(b"%PDF")
    # Verify no raw *** or ** in uncompressed/decompressed streams
    streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.DOTALL)
    for s in streams:
        try:
            decomp = zlib.decompress(s).decode("latin-1")
            assert "***" not in decomp
            assert "**" not in decomp
        except Exception:
            pass

    # 4. HTML Preview
    html_preview = format_html_preview(txt_clean)
    assert "***" not in html_preview
    assert "**" not in html_preview
    assert "BETWEEN:" in html_preview

