"""Legacy import route — delegates to LibreOffice sidecar."""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from ..auth import get_current_user
from ..models import User
from ..services import legacy_import, docx_io, xlsx_io, pptx_io
from ..config import get_settings

router = APIRouter(prefix="/api/import", tags=["import"])
settings = get_settings()


@router.post("/legacy")
async def import_legacy(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(413, "File too large")

    try:
        converted, new_ext = await legacy_import.convert_to_modern(raw, file.filename or "file")
    except ValueError as e:
        raise HTTPException(400, str(e))

    if new_ext == "docx":
        return {"model": docx_io.import_docx(converted), "kind": "word"}
    if new_ext == "xlsx":
        return {"model": xlsx_io.import_xlsx(converted), "kind": "sheets"}
    if new_ext == "pptx":
        return {"model": pptx_io.import_pptx(converted), "kind": "slides"}
    raise HTTPException(500, "Conversion produced an unsupported format")