"""Tiny HTTP wrapper around `libreoffice --headless` running in a sidecar container."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
import subprocess, tempfile, uuid, pathlib

app = FastAPI()

MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


@app.post("/convert/{target_ext}")
async def convert(target_ext: str, file: UploadFile = File(...)):
    if target_ext not in MIME:
        raise HTTPException(400, f"Unsupported target: {target_ext}")

    with tempfile.TemporaryDirectory() as tmp:
        inp = pathlib.Path(tmp) / f"input_{uuid.uuid4().hex}_{file.filename}"
        inp.write_bytes(await file.read())
        out_dir = pathlib.Path(tmp) / "out"
        out_dir.mkdir()

        filt = {
            "docx": "docx:MS Word 2007 XML",
            "xlsx": "xlsx:Calc MS Excel 2007 XML",
            "pptx": "pptx:Impress MS PowerPoint 2007 XML",
        }[target_ext]

        result = subprocess.run(
            ["soffice", "--headless", "--convert-to", filt, "--outdir", str(out_dir), str(inp)],
            capture_output=True, timeout=45,
        )
        if result.returncode != 0:
            raise HTTPException(500, f"LibreOffice failed: {result.stderr.decode()[:200]}")

        out_files = list(out_dir.iterdir())
        if not out_files:
            raise HTTPException(500, "LibreOffice produced no output")
        converted = out_files[0].read_bytes()
        return Response(content=converted, media_type=MIME[target_ext])