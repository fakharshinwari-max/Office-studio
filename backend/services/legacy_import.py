"""Legacy-format import via a LibreOffice headless sidecar."""
from __future__ import annotations
import os
import httpx
from fastapi import HTTPException

LEGACY_EXTS = {"doc", "xls", "ppt", "odt", "ods", "odp", "rtf", "wps", "et", "dps"}


async def convert_to_modern(data: bytes, filename: str) -> tuple[bytes, str]:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in LEGACY_EXTS:
        raise ValueError(f"Unsupported legacy format: {ext}")

    target_ext = {
        "doc": "docx", "odt": "docx", "rtf": "docx", "wps": "docx",
        "xls": "xlsx", "ods": "xlsx", "et": "xlsx",
        "ppt": "pptx", "odp": "pptx", "dps": "pptx",
    }.get(ext, "docx")

    host = os.environ.get("LIBREOFFICE_HOST")
    if not host:
        raise HTTPException(
            503,
            "Legacy import is not available: configure the LIBREOFFICE_HOST "
            "environment variable and run the LibreOffice sidecar (see docker-compose.yml)."
        )

    async with httpx.AsyncClient(timeout=60) as client:
        files = {"file": (filename, data)}
        r = await client.post(f"{host}/convert/{target_ext}", files=files)
        if r.status_code != 200:
            raise HTTPException(500, f"LibreOffice conversion failed: {r.text[:200]}")
        return r.content, target_ext