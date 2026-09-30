import io
import os
import re
from pathlib import Path
from typing import Optional

# Configuration import
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing markdown formatting artifacts (***, **, *, ###),
    replacing typographic / smart quotes, unusual dashes, and unsupported unicode characters.
    Ensures clean, professional legal document formatting across PDF, Word (.docx),
    plain text (.txt), and web previews.
    """
    if not text:
        return ""

    replacements = {
        "\u2018": "'",   # Left single quotation mark
        "\u2019": "'",   # Right single quotation mark
        "\u201c": '"',   # Left double quotation mark
        "\u201d": '"',   # Right double quotation mark
        "\u00ab": '"',   # Left-pointing double angle quotation mark
        "\u00bb": '"',   # Right-pointing double angle quotation mark
        "\u2013": "-",   # En dash
        "\u2014": " - ", # Em dash
        "\u2026": "...", # Horizontal ellipsis
        "\u00a0": " ",   # Non-breaking space
        "\u200b": "",    # Zero-width space
        "\ufeff": "",    # Byte order mark
        "\u2011": "-",   # Non-breaking hyphen
        "\r\n": "\n",    # Normalize line endings
        "\r": "\n",
    }
    
    sanitized = text
    for orig, rep in replacements.items():
        sanitized = sanitized.replace(orig, rep)

    # Strip markdown code blocks if present
    sanitized = re.sub(r"^```[a-zA-Z]*\n?", "", sanitized)
    sanitized = re.sub(r"\n?```$", "", sanitized)

    # Legal section titles and headers that should NEVER be bullet points
    major_heading_pattern = re.compile(
        r"^(SECTION\s+\d+|ARTICLE\s+\d+|\d+\.\s+[A-Z\s]{3,}|"
        r"BETWEEN:?|AND\b|PREAMBLE|RECITALS|IN WITNESS WHEREOF|"
        r"SERVICE PROVIDER:?|CLIENT:?|FOR\s+(?:FIRST|SECOND)\s+PARTY:?|"
        r"SCHEDULE\s+[A-Z]:?|TERMS\s+AND\s+CONDITIONS|"
        r"(?:DEFINITIONS|OPERATIVE\s+CLAUSES|CONFIDENTIALITY|TERMINATION|GOVERNING\s+LAW)(?:\s*:|\s*$))",
        re.IGNORECASE
    )

    cleaned_lines = []
    for raw_line in sanitized.splitlines():
        line = raw_line.strip()
        if not line:
            cleaned_lines.append("")
            continue

        # 1. Remove markdown horizontal rules (***, ---, ___, * * *, etc.)
        if re.match(r"^(\*{3,}|-{3,}|_{3,}|\*\s+\*\s+\*|-\s+-\s+-)$", line):
            continue

        # 2. Strip leading markdown heading symbols (###, ##, #)
        line = re.sub(r"^#{1,6}\s*", "", line)

        # 3. Strip bold/italic markdown asterisks from anywhere in line
        # e.g., **BETWEEN:** -> BETWEEN:
        # e.g., * **Jane Doe** -> * Jane Doe
        # e.g., 2.1. **Engagement.** -> 2.1. Engagement.
        line = re.sub(r"\*{1,3}", "", line)

        # 4. Clean stray bullet points on major sections, numbered clauses, or party definitions
        if re.match(r"^[-*•]\s*", line):
            rest_of_line = re.sub(r"^[-*•]\s*", "", line).strip()
            # If rest of line is a major heading or a numbered clause, remove bullet prefix
            if major_heading_pattern.match(rest_of_line) or re.match(r"^\d+\.\d*", rest_of_line):
                line = rest_of_line
            # If line is part of BETWEEN / AND parties section
            elif re.search(r"\b(hereinafter referred to as|residing at|organized and existing under)\b", rest_of_line, re.IGNORECASE):
                line = rest_of_line
            else:
                # Keep genuine bullet point with clean standard dash
                line = f"- {rest_of_line}"

        # 5. Normalize multiple spaces
        line = re.sub(r"[ \t]+", " ", line).strip()

        # 6. Cap excessive underscores or dashes in signature lines
        line = re.sub(r"_{26,}", "_" * 25, line)
        line = re.sub(r"-{26,}", "-" * 25, line)

        cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()



def format_docx(text: str, doc_type: str, terms: Optional[str] = None, logo_path: Optional[str] = None) -> io.BytesIO:
    """
    Generate a professional Microsoft Word (.docx) document formatted with:
    - Center-aligned / Header Company Logo
    - Times New Roman font standard throughout
    - Formatted Headings and Paragraphs
    - Auto-generated Terms & Conditions Table from semicolon-separated inputs
    - Formal Confidentiality Footer
    
    Returns:
        io.BytesIO containing the document stream
    """
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
        from docx.oxml import OxmlElement, parse_xml
        from docx.oxml.ns import nsdecls, qn
    except ImportError:
        raise ImportError("python-docx is required for Word document formatting. Please install python-docx.")

    doc = Document()
    clean_text = sanitize_text(text)

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Configure Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("LegalEase AI-Powered Legal Document Generator © 2026 | Built with FastAPI & Streamlit BY LILY")
        f_run.font.name = "Times New Roman"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(128, 128, 128)

    # Set base Normal Style to Times New Roman
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Times New Roman"
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(30, 41, 59) # Deep Navy / Slate

    # 1. Embed Logo
    target_logo = logo_path or config.LOGO_PATH
    if target_logo and os.path.exists(target_logo):
        try:
            p_logo = doc.add_paragraph()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.paragraph_format.space_after = Pt(12)
            p_logo.add_run().add_picture(str(target_logo), width=Inches(2.2))
        except Exception:
            pass

    # 2. Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(18)
    run_title = p_title.add_run(doc_type.upper())
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    # 3. Document Body Parsing
    lines = clean_text.splitlines()
    skip_first_title = True
    norm_doc_type = re.sub(r"[^A-Z0-9]", "", doc_type.upper())

    heading_pattern = re.compile(
        r"^(SECTION\s+\d+|ARTICLE\s+\d+|\d+\.\s+[A-Z\s]{3,}|"
        r"BETWEEN:?|AND\b|PREAMBLE|RECITALS|IN WITNESS WHEREOF|"
        r"SERVICE PROVIDER:?|CLIENT:?|FOR\s+(?:FIRST|SECOND)\s+PARTY:?|"
        r"SCHEDULE\s+[A-Z]:?|TERMS\s+AND\s+CONDITIONS|"
        r"(?:DEFINITIONS|OPERATIVE\s+CLAUSES|CONFIDENTIALITY|TERMINATION|GOVERNING\s+LAW)(?:\s*:|\s*$))",
        re.IGNORECASE
    )

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            # Empty spacing
            continue

        # Check if line repeats title
        norm_line = re.sub(r"[^A-Z0-9]", "", line.upper())
        if skip_first_title and (norm_line == norm_doc_type or norm_doc_type in norm_line):
            skip_first_title = False
            continue

        # Heading detection (e.g. SECTION 1, RECITALS, PARTIES, IN WITNESS WHEREOF)
        is_section_heading = bool(
            heading_pattern.match(line)
            or (line.isupper() and len(line) < 60 and not line.startswith("-"))
        )

        if is_section_heading:
            p_head = doc.add_paragraph()
            p_head.paragraph_format.space_before = Pt(14)
            p_head.paragraph_format.space_after = Pt(4)
            p_head.paragraph_format.keep_with_next = True
            run_head = p_head.add_run(line)
            run_head.font.name = "Times New Roman"
            run_head.font.size = Pt(13)
            run_head.font.bold = True
            run_head.font.color.rgb = RGBColor(30, 58, 138)  # Deep Slate Blue
        elif line.startswith("- "):
            # Genuine bullet point
            p_bullet = doc.add_paragraph(style="List Bullet")
            p_bullet.paragraph_format.space_after = Pt(4)
            p_bullet.paragraph_format.line_spacing = 1.15
            run_bullet = p_bullet.add_run(line[2:].strip())
            run_bullet.font.name = "Times New Roman"
            run_bullet.font.size = Pt(11)
        elif re.match(r"^\d+\.\d+", line):
            # Numbered clause (e.g. 2.1. Engagement of Services. The Client...)
            p_clause = doc.add_paragraph()
            p_clause.paragraph_format.space_after = Pt(6)
            p_clause.paragraph_format.line_spacing = 1.15
            clause_match = re.match(r"^(\d+\.\d+\.?\s+[^.]+?\.)\s+(.*)", line)
            if clause_match:
                run_clause_head = p_clause.add_run(clause_match.group(1) + " ")
                run_clause_head.font.name = "Times New Roman"
                run_clause_head.font.size = Pt(11)
                run_clause_head.font.bold = True
                run_clause_body = p_clause.add_run(clause_match.group(2))
                run_clause_body.font.name = "Times New Roman"
                run_clause_body.font.size = Pt(11)
            else:
                num_match = re.match(r"^(\d+\.\d+\.?\s*)(.*)", line)
                if num_match:
                    run_num = p_clause.add_run(num_match.group(1))
                    run_num.font.name = "Times New Roman"
                    run_num.font.size = Pt(11)
                    run_num.font.bold = True
                    run_body = p_clause.add_run(num_match.group(2))
                    run_body.font.name = "Times New Roman"
                    run_body.font.size = Pt(11)
                else:
                    run_body = p_clause.add_run(line)
                    run_body.font.name = "Times New Roman"
                    run_body.font.size = Pt(11)
        else:
            p_body = doc.add_paragraph()
            p_body.paragraph_format.space_after = Pt(6)
            p_body.paragraph_format.line_spacing = 1.15
            run_body = p_body.add_run(line)
            run_body.font.name = "Times New Roman"
            run_body.font.size = Pt(11)

    # 4. Auto-generate Terms Table if semicolon-separated terms were supplied
    if terms and terms.strip():
        term_items = [t.strip() for t in terms.replace("\n", ";").split(";") if t.strip()]
        if term_items:
            doc.add_paragraph()
            p_tbl_title = doc.add_paragraph()
            p_tbl_title.paragraph_format.space_before = Pt(16)
            p_tbl_title.paragraph_format.space_after = Pt(6)
            run_tbl_title = p_tbl_title.add_run("SCHEDULE A: SUMMARY OF KEY TERMS & CONDITIONS")
            run_tbl_title.font.name = "Times New Roman"
            run_tbl_title.font.size = Pt(12)
            run_tbl_title.font.bold = True
            run_tbl_title.font.color.rgb = RGBColor(30, 58, 138)

            table = doc.add_table(rows=1, cols=2)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = False

            # Header row styling
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Item #"
            hdr_cells[1].text = "Contractual Stipulation / Condition"
            hdr_cells[0].width = Inches(1.0)
            hdr_cells[1].width = Inches(5.5)

            for cell in hdr_cells:
                cell.paragraphs[0].runs[0].font.bold = True
                cell.paragraphs[0].runs[0].font.name = "Times New Roman"
                cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                # Shading dark blue
                shd = parse_xml(r'<w:shd {} w:fill="1E3A8A"/>'.format(nsdecls('w')))
                cell._tc.get_or_add_tcPr().append(shd)

            # Rows
            for idx, item in enumerate(term_items, start=1):
                row_cells = table.add_row().cells
                row_cells[0].text = f"Term {idx}"
                row_cells[1].text = item
                row_cells[0].width = Inches(1.0)
                row_cells[1].width = Inches(5.5)
                for c in row_cells:
                    c.paragraphs[0].runs[0].font.name = "Times New Roman"
                    c.paragraphs[0].runs[0].font.size = Pt(10)
                    if idx % 2 == 0:
                        shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                        c._tc.get_or_add_tcPr().append(shd)

    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream


def format_pdf(text: str, doc_type: str, terms: Optional[str] = None, logo_path: Optional[str] = None) -> bytes:
    """
    Generate a branded, professional PDF document using FPDF/FPDF2.
    Features:
    - Center-aligned company logo
    - Header and Footer on all pages
    - Bold headings for sections
    - Bullet-style terms & clean typography
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf or fpdf2 is required for PDF generation. Please install fpdf2.")

    clean_text = sanitize_text(text)
    # Ensure plain ASCII/Latin-1 compatible strings for standard FPDF core fonts
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')

    target_logo = logo_path or config.LOGO_PATH
    has_logo = bool(target_logo and os.path.exists(target_logo))

    class LegalPDF(FPDF):
        def header(self):
            if has_logo:
                try:
                    # Center logo at top
                    self.image(str(target_logo), x=(210 - 45) / 2, y=8, w=45)
                    self.ln(20)
                except Exception:
                    self.ln(6)
            else:
                self.ln(6)

        def footer(self):
            self.set_y(-14)
            self.set_font("Times", "I", 8)
            self.set_text_color(100, 116, 139)
            # Permanent Footer with BY LILY
            footer_text = f"LegalEase AI-Powered Legal Document Generator © 2026 | Built with FastAPI & Streamlit BY LILY   |   Page {self.page_no()}"
            self.cell(0, 8, footer_text, align="C")

    pdf = LegalPDF(orientation="P", unit="mm", format="A4")
    # Generous 20mm standard margins prevent right-edge clipping
    pdf.set_margins(left=20.0, top=20.0, right=20.0)
    pdf.set_auto_page_break(auto=True, margin=22.0)
    pdf.add_page()
    content_width = 210.0 - 40.0  # Exactly 170.0 mm usable width

    # Document Title
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(15, 23, 42)
    pdf.set_x(pdf.l_margin)
    pdf.cell(content_width, 10, doc_type.upper(), align="C")
    pdf.ln(12)

    # Process Document Lines
    lines = clean_text.splitlines()
    skip_title = True
    norm_doc_type = re.sub(r"[^A-Z0-9]", "", doc_type.upper())

    heading_pattern = re.compile(
        r"^(SECTION\s+\d+|ARTICLE\s+\d+|\d+\.\s+[A-Z\s]{3,}|"
        r"BETWEEN:?|AND\b|PREAMBLE|RECITALS|IN WITNESS WHEREOF|"
        r"SERVICE PROVIDER:?|CLIENT:?|FOR\s+(?:FIRST|SECOND)\s+PARTY:?|"
        r"SCHEDULE\s+[A-Z]:?|TERMS\s+AND\s+CONDITIONS|"
        r"(?:DEFINITIONS|OPERATIVE\s+CLAUSES|CONFIDENTIALITY|TERMINATION|GOVERNING\s+LAW)(?:\s*:|\s*$))",
        re.IGNORECASE
    )

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            pdf.ln(3)
            continue

        norm_line = re.sub(r"[^A-Z0-9]", "", line.upper())
        if skip_title and (norm_line == norm_doc_type or norm_doc_type in norm_line):
            skip_title = False
            continue

        # Prevent long underscores or dashes from overflowing printable area
        line = re.sub(r'_{25,}', '_' * 25, line)
        line = re.sub(r'-{25,}', '-' * 25, line)

        # Heading detection
        is_heading = bool(
            heading_pattern.match(line)
            or (line.isupper() and len(line) < 60 and not line.startswith("-"))
        )

        pdf.set_x(pdf.l_margin)

        if is_heading:
            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", "B", 12)
            pdf.set_text_color(30, 58, 138)  # Deep Slate Blue
            pdf.multi_cell(content_width, 6, line)
            pdf.ln(2)
        elif line.startswith("- "):
            pdf.set_font("Times", "", 10.5)
            pdf.set_text_color(30, 41, 59)
            clean_bullet = line[2:].strip()
            pdf.multi_cell(content_width, 5.5, f"   -  {clean_bullet}")
        else:
            pdf.set_font("Times", "", 10.5)
            pdf.set_text_color(30, 41, 59)
            pdf.multi_cell(content_width, 5.5, line)

    # Output as bytes
    pdf_bytes = pdf.output()
    if isinstance(pdf_bytes, str):
        return pdf_bytes.encode("latin-1")
    return bytes(pdf_bytes)


def format_html_preview(text: str) -> str:
    """
    Format AI-generated legal text into an elegant, dark-themed, 
    scrollable semantic HTML card with styled section headers, badges, and signatures.
    """
    if not text:
        return "<p style='color: #94a3b8; text-align: center;'>No document generated yet.</p>"

    sanitized = sanitize_text(text)
    lines = sanitized.splitlines()
    html_lines = []

    heading_pattern = re.compile(
        r"^(SECTION\s+\d+|ARTICLE\s+\d+|\d+\.\s+[A-Z\s]{3,}|"
        r"BETWEEN:?|AND\b|PREAMBLE|RECITALS|IN WITNESS WHEREOF|"
        r"SERVICE PROVIDER:?|CLIENT:?|FOR\s+(?:FIRST|SECOND)\s+PARTY:?|"
        r"SCHEDULE\s+[A-Z]:?|TERMS\s+AND\s+CONDITIONS|"
        r"(?:DEFINITIONS|OPERATIVE\s+CLAUSES|CONFIDENTIALITY|TERMINATION|GOVERNING\s+LAW)(?:\s*:|\s*$))",
        re.IGNORECASE
    )

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            html_lines.append("<div style='height: 8px;'></div>")
            continue

        # Check section heading
        is_heading = bool(
            heading_pattern.match(line)
            or (line.isupper() and len(line) < 60 and not line.startswith("-"))
        )

        if is_heading:
            html_lines.append(
                f"<h4 style='color: #60a5fa; margin-top: 18px; margin-bottom: 6px; "
                f"border-bottom: 1px solid #334155; padding-bottom: 4px; font-weight: 700; "
                f"letter-spacing: 0.5px;'>{line}</h4>"
            )
        elif line.startswith("- "):
            clean_item = line[2:].strip()
            html_lines.append(
                f"<div style='margin-left: 18px; margin-bottom: 6px; color: #e2e8f0; line-height: 1.6;'>"
                f"<span style='color: #38bdf8; margin-right: 8px;'>•</span>{clean_item}</div>"
            )
        elif re.match(r"^\d+\.\d+", line):
            clause_match = re.match(r"^(\d+\.\d+\.?\s+[^.]+?\.)\s+(.*)", line)
            if clause_match:
                head = clause_match.group(1)
                body = clause_match.group(2)
                html_lines.append(
                    f"<p style='color: #e2e8f0; line-height: 1.65; margin-bottom: 8px; font-size: 14.5px;'>"
                    f"<strong style='color: #93c5fd;'>{head}</strong> {body}</p>"
                )
            else:
                html_lines.append(
                    f"<p style='color: #cbd5e1; line-height: 1.65; margin-bottom: 8px; font-size: 14.5px;'>{line}</p>"
                )
        elif line.startswith(("FOR FIRST PARTY:", "FOR SECOND PARTY:", "Signature:", "Name:", "Title:", "Date:", "By:", "SERVICE PROVIDER:", "CLIENT:")):
            html_lines.append(
                f"<div style='font-family: monospace; color: #cbd5e1; margin-bottom: 4px;'>{line}</div>"
            )
        else:
            html_lines.append(
                f"<p style='color: #cbd5e1; line-height: 1.65; margin-bottom: 8px; font-size: 14.5px;'>{line}</p>"
            )

    body_content = "\n".join(html_lines)

    html_container = f"""
    <div style="
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 28px;
        max-height: 520px;
        overflow-y: auto;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
            <div style="color: #38bdf8; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">
                LegalEase Verified Draft
            </div>
            <div style="background-color: #0369a1; color: #e0f2fe; padding: 2px 10px; border-radius: 9999px; font-size: 11px; font-weight: 600;">
                Live Preview
            </div>
        </div>
        <div>
            {body_content}
        </div>
    </div>
    """
    return html_container
