"""Import/export endpoints."""
from __future__ import annotations
import csv
import io
import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from ..auth import get_current_user
from ..models import User
from ..config import get_settings
from ..services import docx_io, xlsx_io, pptx_io, pdf_io

router = APIRouter(prefix="/api", tags=["export"])
settings = get_settings()

MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "pdf":  "application/pdf",
    "csv":  "text/csv; charset=utf-8",
    "tsv":  "text/tab-separated-values; charset=utf-8",
    "json": "application/json",
    "html": "text/html; charset=utf-8",
    "md":   "text/markdown; charset=utf-8",
    "txt":  "text/plain; charset=utf-8",
}


class ExportIn(BaseModel):
    model: dict
    name: str = "document"


@router.post("/export/{kind}/{fmt}")
def export(kind: str, fmt: str, body: ExportIn, user: User = Depends(get_current_user)):
    kind, fmt = kind.lower(), fmt.lower()

    # Binary exports
    if fmt == "docx" and kind == "word":
        data = docx_io.export_docx(body.model)
    elif fmt == "xlsx" and kind == "sheets":
        data = xlsx_io.export_xlsx(body.model)
    elif fmt == "pptx" and kind == "slides":
        data = pptx_io.export_pptx(body.model)
    elif fmt == "pdf":
        if kind == "word":   data = pdf_io.export_pdf_writer(body.model)
        elif kind == "slides": data = pdf_io.export_pdf_slides(body.model)
        elif kind == "sheets": data = pdf_io.export_pdf_sheets(body.model)
        else: raise HTTPException(400, "Unknown kind for PDF export")
    elif fmt == "csv" and kind == "sheets":
        return _csv_response(body.model, sep=",")
    elif fmt == "tsv" and kind == "sheets":
        return _csv_response(body.model, sep="\t")
    elif fmt == "json":
        data = json.dumps(body.model, ensure_ascii=False).encode("utf-8")
    else:
        raise HTTPException(400, f"Unsupported export {kind}/{fmt}")

    filename = f"{body.name}.{fmt}"
    return Response(
        content=data,
        media_type=MIME.get(fmt, "application/octet-stream"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import/{kind}")
async def import_file(kind: str, file: UploadFile = File(...),
                      user: User = Depends(get_current_user)):
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(413, "File too large")

    kind = kind.lower()
    name = (file.filename or "").lower()

    if kind == "word" or name.endswith(".docx"):
        model = docx_io.import_docx(raw)
    elif kind == "sheets" or name.endswith(".xlsx"):
        model = xlsx_io.import_xlsx(raw)
    elif kind == "slides" or name.endswith(".pptx"):
        model = pptx_io.import_pptx(raw)
    else:
        raise HTTPException(400, "Unsupported file type")

    return {"model": model}


# ---------- CSV export with formula-injection protection ----------

_DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _sanitize_cell(text: str) -> str:
    if not text:
        return text
    if text[0] in _DANGEROUS_PREFIXES:
        return "'" + text
    return text


def _csv_response(model: dict, sep: str):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=sep, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    for sheet in model.get("sheets", []) or []:
        # Header
        w.writerow([f"# Sheet: {sheet.get('name','Sheet1')}"])
        cells = sheet.get("cells", {}) or {}
        if not cells:
            continue
        # Determine bounds
        import re
        max_r = max_c = 0
        grid: dict[tuple[int,int], str] = {}
        for ref, cell in cells.items():
            m = re.match(r"^([A-Z]+)(\d+)$", ref)
            if not m: continue
            ci = xlsx_io.col_name_to_index(m.group(1))
            ri = int(m.group(2)) - 1
            max_r = max(max_r, ri); max_c = max(max_c, ci)
            v = cell.get("v", "")
            if isinstance(v, str):
                v = _sanitize_cell(v)
            grid[(ri, ci)] = v
        for r in range(max_r + 1):
            w.writerow([grid.get((r, c), "") for c in range(max_c + 1)])
        w.writerow([])  # blank between sheets

    filename = "export.csv" if sep == "," else "export.tsv"
    content_type = MIME["csv"] if sep == "," else MIME["tsv"]
    data = buf.getvalue().encode("utf-8-sig")  # BOM for Excel UTF-8
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )