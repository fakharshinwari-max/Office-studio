# Office Studio

Browser-based Writer / Sheets / Slides suite in the spirit of Microsoft Office,
built with FastAPI + vanilla ES modules. Runs on Windows 11, macOS, Linux,
Android (Chrome / Edge / Firefox), and iOS Safari (best-effort).

## Features (Phase 0 + Phase 1)

- **Writer**: contenteditable rich text, ribbon (Home / Insert / Layout / View +
  contextual Table Design), undo/redo, autosave, DOCX / PDF export, DOCX import,
  find & replace, context menu, keyboard shortcuts, themes (light/dark/HC),
  zoom, tables, images, page-break, cover page, date/time, page numbers.
- **Sheets**: canvas-based virtual grid (1M × 16 384 logical), formula engine
  with ~160 Tier-1 functions, dependency graph, cross-sheet refs, number-format
  engine, XLSX / CSV / JSON export, XLSX import, sorting, autofill-down,
  remove-duplicates, Insert Function, autosum, freeze panes, sheet tabs.
- **Slides**: canvas slide editor, thumbnails, drag/resize objects, shapes,
  text boxes, images, themes, transitions, animations, presenter mode,
  speaker notes, PPTX / PDF export, PPTX import.

## Folder structure

See `office-studio/` tree in the project root.

## Install & Run

### Windows 11 / macOS / Linux

```powershell
python -m venv .venv
.\.venv\Scripts\activate       # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
