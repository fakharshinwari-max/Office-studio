"""PDF export via reportlab."""
from io import BytesIO
from typing import Any
from reportlab.lib.pagesizes import LETTER, A4, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as RLTable, PageBreak
from reportlab.lib.units import inch


def export_pdf_writer(model: dict[str, Any]) -> bytes:
    page = model.get("pageSetup", {}) or {}
    size = {"Letter": LETTER, "A4": A4}.get(page.get("size", "Letter"), LETTER)
    if page.get("orientation") == "landscape":
        size = landscape(size)

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=size)
    styles = getSampleStyleSheet()
    story = []

    for block in model.get("blocks", []):
        btype = block.get("type", "paragraph")
        if btype == "heading":
            lvl = int(block.get("attrs", {}).get("level", 1))
            style = styles.get(f"Heading{lvl}", styles["Heading1"])
            story.append(Paragraph(_runs_to_html(block.get("runs", [])), style))
        elif btype == "paragraph":
            story.append(Paragraph(_runs_to_html(block.get("runs", [])), styles["Normal"]))
        elif btype == "table":
            data = [[str(c) for c in row] for row in block.get("rows", [])]
            if data:
                story.append(RLTable(data))
        elif btype == "pagebreak":
            story.append(PageBreak())
        story.append(Spacer(1, 6))

    doc.build(story)
    return buf.getvalue()


def export_pdf_slides(model: dict[str, Any]) -> bytes:
    size = landscape(LETTER)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=size)
    styles = getSampleStyleSheet()
    story = []
    for slide in model.get("slides", []):
        for obj in slide.get("objects", []):
            if obj.get("type") == "text":
                story.append(Paragraph(obj.get("props", {}).get("text", ""), styles["Title"]))
        story.append(PageBreak())
    doc.build(story)
    return buf.getvalue()


def export_pdf_sheets(model: dict[str, Any]) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=portrait(LETTER))
    styles = getSampleStyleSheet()
    story = []
    for sheet in model.get("sheets", []):
        story.append(Paragraph(sheet.get("name", "Sheet"), styles["Heading2"]))
        rows = []
        for ref, cell in (sheet.get("cells", {}) or {}).items():
            rows.append([ref, str(cell.get("v", cell.get("f", "")))])
        if rows:
            story.append(RLTable(rows[:200]))
        story.append(PageBreak())
    doc.build(story)
    return buf.getvalue()


def _runs_to_html(runs: list[dict]) -> str:
    out = []
    for r in runs:
        text = (r.get("text") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        a = r.get("attrs", {}) or {}
        if a.get("bold"):
            text = f"<b>{text}</b>"
        if a.get("italic"):
            text = f"<i>{text}</i>"
        if a.get("underline"):
            text = f"<u>{text}</u>"
        out.append(text)
    return "".join(out) or "&nbsp;"