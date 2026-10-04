"""XLSX import/export with Excel-365 fidelity.

- Write: XlsxWriter (native dynamic arrays, comments, tables, CF, DV).
- Read : openpyxl.
- Newer functions are automatically prefixed with `_xlfn.` / `_xlfn._xlws.`
  so Excel 365 will accept them without a #NAME? error.
- Every formula is written with a cached value computed by our engine so that
  viewers that don't recalc (previewers, pandas, mobile) show correct numbers.
- fullCalcOnLoad is enabled so Excel re-verifies on open.
"""
from __future__ import annotations
from io import BytesIO
from typing import Any
import re
import openpyxl

# ---------- Formula prefixing ----------

# Functions that Excel 365 stores with a prefix in the file (per MS-XLSX / ECMA-376).
# Note: FILTER/SORT/UNIQUE are dynamic-array aware and live in _xlfn._xlws.
_FN_PREFIX = {
    "XLOOKUP": "_xlfn.XLOOKUP",
    "XMATCH": "_xlfn.XMATCH",
    "IFS": "_xlfn.IFS",
    "SWITCH": "_xlfn.SWITCH",
    "TEXTJOIN": "_xlfn.TEXTJOIN",
    "CONCAT": "_xlfn.CONCAT",
    "MAXIFS": "_xlfn.MAXIFS",
    "MINIFS": "_xlfn.MINIFS",
    "LET": "_xlfn.LET",
    "LAMBDA": "_xlfn.LAMBDA",
    "SEQUENCE": "_xlfn.SEQUENCE",
    "RANDARRAY": "_xlfn.RANDARRAY",
    "SORTBY": "_xlfn.SORTBY",
    "TOCOL": "_xlfn.TOCOL",
    "TOROW": "_xlfn.TOROW",
    "TAKE": "_xlfn.TAKE",
    "DROP": "_xlfn.DROP",
    "CHOOSECOLS": "_xlfn.CHOOSECOLS",
    "CHOOSEROWS": "_xlfn.CHOOSEROWS",
    "HSTACK": "_xlfn.HSTACK",
    "VSTACK": "_xlfn.VSTACK",
    "WRAPCOLS": "_xlfn.WRAPCOLS",
    "WRAPROWS": "_xlfn.WRAPROWS",
    "EXPAND": "_xlfn.EXPAND",
    "TEXTAFTER": "_xlfn.TEXTAFTER",
    "TEXTBEFORE": "_xlfn.TEXTBEFORE",
    "TEXTSPLIT": "_xlfn.TEXTSPLIT",
    "ARRAYTOTEXT": "_xlfn.ARRAYTOTEXT",
    "VALUETOTEXT": "_xlfn.VALUETOTEXT",
    "GROUPBY": "_xlfn.GROUPBY",
    "PIVOTBY": "_xlfn.PIVOTBY",
    "PERCENTOF": "_xlfn.PERCENTOF",
    "TRIMRANGE": "_xlfn.TRIMRANGE",
    # Dynamic-array "worksheet functions"
    "FILTER": "_xlfn._xlws.FILTER",
    "SORT": "_xlfn._xlws.SORT",
    "UNIQUE": "_xlfn._xlws.UNIQUE",
}

_FN_NAME_RE = re.compile(r"(?<![A-Za-z0-9_.])([A-Z][A-Z0-9.]*)\s*\(")


def _prefix_formula(f: str) -> str:
    """Prefix newer function names inside a formula, skipping strings."""
    if not f or not f.startswith("="):
        return f
    # Split on string literals so we never touch them.
    parts = _split_strings(f)
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # inside a string literal
            out.append(part)
            continue
        out.append(_FN_NAME_RE.sub(lambda m: _FN_PREFIX.get(m.group(1).upper(), m.group(1)) + "(",
                                   part))
    return "".join(out)


def _split_strings(f: str) -> list[str]:
    """Alternate: [code, 'str', code, 'str', ...] so odd indices are string literals."""
    parts: list[str] = []
    cur = []
    in_str = False
    i = 0
    while i < len(f):
        ch = f[i]
        if ch == '"':
            if not in_str:
                parts.append("".join(cur)); cur = []
                in_str = True
                cur.append(ch)
            else:
                # Doubled "" inside a string is an escaped quote — stay in string.
                if i + 1 < len(f) and f[i + 1] == '"':
                    cur.append('""'); i += 2; continue
                cur.append(ch)
                parts.append("".join(cur)); cur = []
                in_str = False
        else:
            cur.append(ch)
        i += 1
    if cur:
        parts.append("".join(cur))
    return parts


# ---------- Export ----------

def export_xlsx(model: dict[str, Any]) -> bytes:
    import xlsxwriter
    buf = BytesIO()
    wb = xlsxwriter.Workbook(buf, {
        "in_memory": True,
        "use_future_functions": True,   # auto-prefixes _xlfn.* for new functions
        "default_date_format": "yyyy-mm-dd",
        "nan_inf_to_errors": True,
    })
    wb.set_properties(model.get("meta", {}) or {})

    # Workbook-level defined names
    for nr in model.get("namedRanges", []) or []:
        name = nr.get("name")
        refers = nr.get("refersTo")
        if name and refers:
            try:
                wb.define_name(name, _prefix_formula(refers) if refers.startswith("=") else refers)
            except Exception:
                pass

    for sheet in model.get("sheets", []) or []:
        ws = wb.add_worksheet((sheet.get("name") or "Sheet1")[:31])
        _write_sheet(wb, ws, sheet)

    # fullCalcOnLoad — force Excel to recalc on open.
    wb.set_calc_mode("auto")
    wb.close()
    return buf.getvalue()


def _write_sheet(wb, ws, sheet: dict):
    cells = sheet.get("cells", {}) or {}
    col_widths = sheet.get("colWidths", {}) or {}
    row_heights = sheet.get("rowHeights", {}) or {}
    merges = sheet.get("merges", []) or []
    frozen = sheet.get("frozen", {}) or {}
    cf = sheet.get("cf", []) or []
    validations = sheet.get("validations", []) or []
    hyperlinks = sheet.get("hyperlinks", {}) or {}
    comments = sheet.get("comments", {}) or {}

    # Track used range for autofilter and set_column defaults.
    max_r = 0
    max_c = 0

    # --- width / height ---
    for col_name, width in col_widths.items():
        ci = col_name_to_index(col_name)
        try:
            ws.set_column(ci, ci, float(width))
        except Exception:
            pass
    for row_num, height in row_heights.items():
        try:
            ws.set_row(int(row_num) - 1, float(height))
        except Exception:
            pass

    # --- cell styles (write a Format per style signature) ---
    style_cache: dict[str, Any] = {}

    def _fmt(s: dict | None):
        if not s:
            return None
        key = repr(sorted(s.items()))
        if key in style_cache:
            return style_cache[key]
        f = wb.add_format(_style_to_xlsxwriter(s))
        style_cache[key] = f
        return f

    for ref, cell in cells.items():
        m = re.match(r"^([A-Z]+)(\d+)$", ref)
        if not m:
            continue
        col = col_name_to_index(m.group(1))
        row = int(m.group(2)) - 1
        max_r = max(max_r, row)
        max_c = max(max_c, col)

        fmt = _fmt(cell.get("s"))
        f = cell.get("f")
        v = cell.get("v")

        if f:
            pf = _prefix_formula(f)
            # Dynamic-array formula? Heuristic: spills metadata present OR uses FILTER/UNIQUE/SORT/SEQUENCE...
            if cell.get("spill"):
                try:
                    ws.write_dynamic_array_formula(row, col, row, col, pf, fmt, None if v is None else v)
                    continue
                except Exception:
                    pass
            try:
                ws.write_formula(row, col, pf, fmt, None if v is None else v)
            except Exception:
                ws.write(row, col, v if v is not None else "", fmt)
        else:
            _write_plain(ws, row, col, v, fmt)

    for merge in merges:
        try:
            ws.merge_range(merge, "")
        except Exception:
            pass

    if hyperlinks:
        for ref, url in hyperlinks.items():
            try:
                ws.write_url(ref, url)
            except Exception:
                pass

    if comments:
        for ref, text in comments.items():
            try:
                ws.write_comment(ref, text)
            except Exception:
                pass

    if frozen.get("r") is not None or frozen.get("c") is not None:
        try:
            ws.freeze_panes(frozen.get("r", 0), frozen.get("c", 0))
        except Exception:
            pass

    # autofilter
    if max_r and max_c:
        try:
            ws.autofilter(0, 0, max_r, max_c)
        except Exception:
            pass

    # conditional formats
    for rule in cf:
        _write_cf(ws, wb, rule)

    # data validation
    for dv in validations:
        _write_dv(ws, wb, dv)

    # worksheet-level defined names
    for nr in sheet.get("namedRanges", []) or []:
        name = nr.get("name")
        refers = nr.get("refersTo")
        if name and refers:
            try:
                ws.define_name(name, refers)
            except Exception:
                pass


def _write_plain(ws, row, col, v, fmt):
    if v is None:
        ws.write_blank(row, col, None, fmt)
    elif isinstance(v, bool):
        ws.write_boolean(row, col, v, fmt)
    elif isinstance(v, (int, float)):
        ws.write_number(row, col, v, fmt)
    elif isinstance(v, str) and v.startswith("="):
        ws.write_formula(row, col, _prefix_formula(v), fmt)
    else:
        ws.write(row, col, v, fmt)


def _style_to_xlsxwriter(s: dict) -> dict:
    """Convert internal style dict -> xlsxwriter `add_format` kwargs."""
    out: dict = {}
    if s.get("bold"):     out["bold"] = True
    if s.get("italic"):   out["italic"] = True
    if s.get("underline"): out["underline"] = 1
    if s.get("font"):
        out["font_name"] = s["font"]
    if s.get("fontSize"):
        try: out["font_size"] = float(s["fontSize"])
        except Exception: pass
    if s.get("color"):
        out["font_color"] = _color(s["color"])
    if s.get("fill"):
        out["bg_color"] = _color(s["fill"])
    if s.get("align") == "left":     out["align"] = "left"
    if s.get("align") == "center":   out["align"] = "center"
    if s.get("align") == "right":    out["align"] = "right"
    if s.get("valign") == "top":     out["valign"] = "top"
    if s.get("valign") == "middle":  out["valign"] = "vcenter"
    if s.get("valign") == "bottom":  out["valign"] = "bottom"
    if s.get("wrap"):     out["text_wrap"] = True
    if s.get("numfmt"):   out["num_format"] = s["numfmt"]
    if s.get("border"):
        out["border"] = 1
    return out


def _color(c: str) -> str:
    if not c: return "#000000"
    if c.startswith("#"): return c
    return "#" + c


def _write_cf(ws, wb, rule: dict):
    """rule = {range, type, ...} — type: 'cell'|'colorScale'|'dataBar'|'iconSet'|'formula'."""
    rng = rule.get("range")
    if not rng:
        return
    try:
        r0, c0, r1, c1 = _range_to_indices(rng)
    except Exception:
        return

    t = rule.get("type")
    if t == "cell":
        crit = rule.get("criteria", ">")
        val = rule.get("value", 0)
        fmt = wb.add_format(_style_to_xlsxwriter(rule.get("format", {}) or {}))
        ws.conditional_format(r0, c0, r1, c1, {"type": "cell", "criteria": crit, "value": val, "format": fmt})
    elif t == "formula":
        fmt = wb.add_format(_style_to_xlsxwriter(rule.get("format", {}) or {}))
        ws.conditional_format(r0, c0, r1, c1, {"type": "formula", "criteria": rule.get("formula", "FALSE"), "format": fmt})
    elif t == "colorScale":
        colors = rule.get("colors") or ["#F8696B", "#FFEB84", "#63BE7B"]
        ws.conditional_format(r0, c0, r1, c1, {"type": "3_color_scale", "min_color": colors[0], "mid_color": colors[1], "max_color": colors[2]})
    elif t == "dataBar":
        ws.conditional_format(r0, c0, r1, c1, {"type": "data_bar", "bar_color": rule.get("color", "#638EC6")})
    elif t == "iconSet":
        ws.conditional_format(r0, c0, r1, c1, {"type": "icon_set", "icon_style": rule.get("style", "3_traffic_lights")})


def _write_dv(ws, wb, dv: dict):
    rng = dv.get("range")
    if not rng:
        return
    try:
        r0, c0, r1, c1 = _range_to_indices(rng)
    except Exception:
        return
    t = dv.get("type", "list")
    if t == "list":
        src = dv.get("source", "")
        if isinstance(src, list):
            ws.data_validation(r0, c0, r1, c1, {
                "validate": "list", "source": src,
                "input_title": dv.get("inputTitle", ""),
                "input_message": dv.get("inputMessage", ""),
                "error_title": dv.get("errorTitle", ""),
                "error_message": dv.get("errorMessage", ""),
            })
        elif isinstance(src, str):
            ws.data_validation(r0, c0, r1, c1, {
                "validate": "list", "source": src,
                "input_title": dv.get("inputTitle", ""),
                "input_message": dv.get("inputMessage", ""),
            })
    elif t in ("whole", "decimal", "date", "time", "length"):
        ws.data_validation(r0, c0, r1, c1, {
            "validate": t,
            "criteria": dv.get("criteria", "between"),
            "minimum": dv.get("value", 0),
            "maximum": dv.get("valueMax", 0),
        })
    elif t == "custom":
        ws.data_validation(r0, c0, r1, c1, {
            "validate": "custom", "value": dv.get("formula", "TRUE"),
        })


# ---------- Import ----------

def import_xlsx(data: bytes) -> dict[str, Any]:
    wb = openpyxl.load_workbook(BytesIO(data), data_only=False)
    wb_values = openpyxl.load_workbook(BytesIO(data), data_only=True)  # cached values

    sheets = []
    for ws in wb.worksheets:
        ws_v = wb_values[ws.title]
        cells: dict[str, dict] = {}
        for row in ws.iter_rows():
            for c in row:
                if c.value is None and not c.has_style:
                    continue
                cell = {}
                val = c.value
                if isinstance(val, str) and val.startswith("="):
                    cell["f"] = _strip_xlfn(val)
                    cached = ws_v[c.coordinate].value
                    if cached is not None:
                        cell["v"] = cached
                elif val is not None:
                    cell["v"] = val
                s = _extract_style(c)
                if s:
                    cell["s"] = s
                if cell:
                    cells[c.coordinate] = cell

        # Merges
        merges = [str(r) for r in ws.merged_cells.ranges]

        # Column widths
        col_widths: dict[str, float] = {}
        for col_letter, dim in ws.column_dimensions.items():
            if dim.width:
                col_widths[col_letter] = dim.width

        # Row heights
        row_heights: dict[str, float] = {}
        for row_num, dim in ws.row_dimensions.items():
            if dim.height:
                row_heights[str(row_num)] = dim.height

        # Freeze
        frozen = {}
        if ws.freeze_panes:
            fp = ws.freeze_panes  # e.g. "A2" or "B2"
            m = re.match(r"^([A-Z]*)(\d*)$", fp)
            if m:
                if m.group(1):
                    frozen["c"] = col_name_to_index(m.group(1))
                if m.group(2):
                    frozen["r"] = int(m.group(2)) - 1

        # Conditional formatting (basic)
        cf = []
        for rng in ws.conditional_formatting:
            for rule in rng.rules:
                cf.append({
                    "range": str(rng.sqref),
                    "type": {"cellIs": "cell", "expression": "formula",
                             "colorScale": "colorScale", "dataBar": "dataBar",
                             "iconSet": "iconSet"}.get(rule.type, "cell"),
                    "criteria": rule.operator,
                    "value": rule.formula[0] if rule.formula else None,
                    "formula": rule.formula[0] if rule.formula else None,
                })

        # Data validations
        validations = []
        for dv in ws.data_validations.dataValidation:
            validations.append({
                "range": str(dv.sqref),
                "type": dv.type,
                "criteria": dv.operator,
                "source": dv.formula1,
                "formula": dv.formula1,
            })

        # Hyperlinks
        hyperlinks = {ref: link.target for ref, link in ws._hyperlinks.items()} if hasattr(ws, "_hyperlinks") else {}

        sheets.append({
            "name": ws.title,
            "cells": cells,
            "colWidths": col_widths,
            "rowHeights": row_heights,
            "merges": merges,
            "frozen": frozen,
            "cf": cf,
            "validations": validations,
            "charts": [],
            "hyperlinks": hyperlinks,
        })

    # Defined names
    named = []
    for name, defn in wb.defined_names.items():
        try:
            named.append({"name": name, "refersTo": defn.attr_text})
        except Exception:
            pass

    return {
        "meta": {
            "title": wb.properties.title or "",
            "author": wb.properties.creator or "",
        },
        "sheets": sheets,
        "namedRanges": named,
        "schemaVersion": 2,
    }


def _strip_xlfn(f: str) -> str:
    """Remove _xlfn. / _xlfn._xlws. prefixes so the model holds clean names."""
    return f.replace("_xlfn._xlws.", "").replace("_xlfn.", "")


def _extract_style(c) -> dict:
    s: dict = {}
    f = c.font
    if f:
        if f.bold: s["bold"] = True
        if f.italic: s["italic"] = True
        if f.underline: s["underline"] = True
        if f.name: s["font"] = f.name
        if f.size: s["fontSize"] = f.size
        if f.color and f.color.rgb:
            rgb = f.color.rgb
            if isinstance(rgb, str) and len(rgb) == 8:
                s["color"] = "#" + rgb[-6:]
    fill = c.fill
    if fill and fill.fgColor and fill.fgColor.rgb and fill.patternType:
        rgb = fill.fgColor.rgb
        if isinstance(rgb, str) and len(rgb) == 8 and rgb != "00000000":
            s["fill"] = "#" + rgb[-6:]
    if c.alignment:
        if c.alignment.horizontal: s["align"] = c.alignment.horizontal
        if c.alignment.vertical: s["valign"] = c.alignment.vertical
        if c.alignment.wrap_text: s["wrap"] = True
    if c.number_format and c.number_format != "General":
        s["numfmt"] = c.number_format
    return s


# ---------- helpers ----------

def col_name_to_index(name: str) -> int:
    n = 0
    for ch in name.upper():
        if "A" <= ch <= "Z":
            n = n * 26 + (ord(ch) - 64)
    return n - 1


def _range_to_indices(rng: str):
    """Accepts 'A1:C4' or 'A1' and returns (r0,c0,r1,c1)."""
    rng = rng.replace("$", "")
    if ":" in rng:
        a, b = rng.split(":")
    else:
        a = b = rng
    ma = re.match(r"^([A-Z]+)(\d+)$", a)
    mb = re.match(r"^([A-Z]+)(\d+)$", b)
    if not ma or not mb:
        raise ValueError(rng)
    r0, c0 = int(ma.group(2)) - 1, col_name_to_index(ma.group(1))
    r1, c1 = int(mb.group(2)) - 1, col_name_to_index(mb.group(1))
    return r0, c0, r1, c1