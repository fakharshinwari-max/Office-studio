"""Raw OOXML helpers using lxml — for the parts python-docx/-pptx lack.

Provides:
  - tracked change writers (w:ins, w:del, w:delText)
  - threaded comments (comments.xml + commentsExtended.xml + people.xml)
  - footnotes / endnotes
  - content controls (w:sdt)
  - OMML equations (from LaTeX via a small mapping table)
  - SmartArt diagram parts (dgm) for PPTX
  - morph transition extension writer (p159:morph)
"""
from __future__ import annotations
from datetime import datetime
from io import BytesIO
from typing import Any
import re
import uuid
from lxml import etree

NS = {
    "w":   "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r":   "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "ct":  "http://schemas.openxmlformats.org/package/2006/content-types",
    "pr":  "http://schemas.openxmlformats.org/package/2006/relationships",
    "mc":  "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "m":   "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "a":   "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p":   "http://schemas.openxmlformats.org/presentationml/2006/main",
    "p14": "http://schemas.microsoft.com/office/powerpoint/2010/main",
    "p15": "http://schemas.microsoft.com/office/powerpoint/2012/main",
    "p159": "http://schemas.microsoft.com/office/powerpoint/2015/09/main",
    "dgm": "http://schemas.openxmlformats.org/drawingml/2006/diagram",
    "dsp": "http://schemas.microsoft.com/office/drawing/2008/diagram",
}
for prefix, uri in NS.items():
    etree.register_namespace(prefix, uri)


def q(ns: str, tag: str) -> str:
    return f"{{{NS[ns]}}}{tag}"


# =========================================================================
# Track changes (Word)
# =========================================================================

def make_insertion(author: str, when: datetime, runs: list[dict]) -> etree._Element:
    el = etree.Element(q("w", "ins"))
    el.set(q("w", "id"), str(uuid.uuid4().int % 1000000))
    el.set(q("w", "author"), author)
    el.set(q("w", "date"), when.isoformat(timespec="seconds") + "Z")
    for r in runs:
        el.append(make_run(r, deleted=False))
    return el


def make_deletion(author: str, when: datetime, runs: list[dict]) -> etree._Element:
    el = etree.Element(q("w", "del"))
    el.set(q("w", "id"), str(uuid.uuid4().int % 1000000))
    el.set(q("w", "author"), author)
    el.set(q("w", "date"), when.isoformat(timespec="seconds") + "Z")
    for r in runs:
        el.append(make_run(r, deleted=True))
    return el


def make_run(run: dict, deleted: bool) -> etree._Element:
    r = etree.Element(q("w", "r"))
    rpr = etree.SubElement(r, q("w", "rPr"))
    if run.get("bold"): etree.SubElement(rpr, q("w", "b"))
    if run.get("italic"): etree.SubElement(rpr, q("w", "i"))
    if run.get("underline"): etree.SubElement(rpr, q("w", "u")).set(q("w", "val"), "single")
    if run.get("size"):
        sz = etree.SubElement(rpr, q("w", "sz"))
        sz.set(q("w", "val"), str(int(run["size"] * 2)))
    if deleted:
        dt = etree.SubElement(r, q("w", "delText"))
        dt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        dt.text = run.get("text", "")
    else:
        t = etree.SubElement(r, q("w", "t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = run.get("text", "")
    return r


# =========================================================================
# Threaded comments (comments.xml + commentsExtended.xml + people.xml)
# =========================================================================

def build_comments_parts(comments: list[dict]) -> dict[str, bytes]:
    comments_root = etree.Element(q("w", "comments"))
    for c in comments:
        el = etree.SubElement(comments_root, q("w", "comment"))
        el.set(q("w", "id"), str(c["id"]))
        el.set(q("w", "author"), c.get("author", ""))
        el.set(q("w", "initials"), c.get("initials", ""))
        el.set(q("w", "date"), c.get("date", datetime.utcnow().isoformat(timespec="seconds") + "Z"))
        p = etree.SubElement(el, q("w", "p"))
        r = etree.SubElement(p, q("w", "r"))
        t = etree.SubElement(r, q("w", "t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = c.get("text", "")

    extended_root = etree.Element(q("w15", "commentsEx"))
    for c in comments:
        el = etree.SubElement(extended_root, q("w15", "commentEx"))
        el.set(q("w15", "paraId"), c.get("paraId", _hex8()))
        if c.get("parentId") is not None:
            el.set(q("w15", "paraIdParent"), _hex8_of(c["parentId"]))
        el.set(q("w15", "done"), "1" if c.get("resolved") else "0")

    people_root = etree.Element(q("w15", "people"))
    seen = set()
    for c in comments:
        author = c.get("author", "")
        if author in seen:
            continue
        seen.add(author)
        el = etree.SubElement(people_root, q("w15", "person"))
        el.set(q("w15", "author"), author)
        el.set(q("w15", "presenceInfo"), author)

    return {
        "word/comments.xml": etree.tostring(comments_root, xml_declaration=True, encoding="UTF-8", standalone=True),
        "word/commentsExtended.xml": etree.tostring(extended_root, xml_declaration=True, encoding="UTF-8", standalone=True),
        "word/people.xml": etree.tostring(people_root, xml_declaration=True, encoding="UTF-8", standalone=True),
    }


def _hex8() -> str:
    return uuid.uuid4().hex[:8].upper()


def _hex8_of(value) -> str:
    import hashlib
    return hashlib.md5(str(value).encode()).hexdigest()[:8].upper()


# =========================================================================
# Footnotes
# =========================================================================

def build_footnotes_part(footnotes: list[dict]) -> bytes:
    root = etree.Element(q("w", "footnotes"))
    # Word requires the three "special" footnotes: separator (id=-1), continuationSeparator (-2), continuationNotice (-3)
    for special_id, kind in [(-1, "separator"), (-2, "continuationSeparator"), (-3, "continuationNotice")]:
        f = etree.SubElement(root, q("w", "footnote"))
        f.set(q("w", "type"), kind)
        f.set(q("w", "id"), str(special_id))
        p = etree.SubElement(f, q("w", "p"))
        pPr = etree.SubElement(p, q("w", "pPr"))
        pStyle = etree.SubElement(pPr, q("w", "pStyle"))
        pStyle.set(q("w", "val"), "Footnote" + kind[:1].upper() + kind[1:])
        r = etree.SubElement(p, q("w", "r"))
        if kind == "separator":
            sep = etree.SubElement(r, q("w", "separator"))
        elif kind == "continuationSeparator":
            cont = etree.SubElement(r, q("w", "continuationSeparator"))
        else:
            etree.SubElement(r, q("w", "continuationSeparator"))
    for f in footnotes:
        el = etree.SubElement(root, q("w", "footnote"))
        el.set(q("w", "id"), str(f["id"]))
        p = etree.SubElement(el, q("w", "p"))
        pPr = etree.SubElement(p, q("w", "pPr"))
        pStyle = etree.SubElement(pPr, q("w", "pStyle"))
        pStyle.set(q("w", "val"), "FootnoteText")
        r0 = etree.SubElement(p, q("w", "r"))
        rPr0 = etree.SubElement(r0, q("w", "rPr"))
        rStyle = etree.SubElement(rPr0, q("w", "rStyle"))
        rStyle.set(q("w", "val"), "FootnoteReference")
        ref = etree.SubElement(r0, q("w", "footnoteRef"))
        r = etree.SubElement(p, q("w", "r"))
        t = etree.SubElement(r, q("w", "t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = " " + f.get("text", "")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


# =========================================================================
# OMML equations
# =========================================================================

_LATEX_MAP = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\pi": "π", r"\theta": "θ", r"\lambda": "λ",
    r"\mu": "μ", r"\sigma": "σ", r"\phi": "φ", r"\omega": "ω",
    r"\times": "×", r"\div": "÷", r"\pm": "±", r"\cdot": "·",
    r"\le": "≤", r"\ge": "≥", r"\ne": "≠", r"\approx": "≈",
    r"\infty": "∞", r"\sum": "∑", r"\prod": "∏", r"\int": "∫",
    r"\partial": "∂", r"\nabla": "∇",
}


def latex_to_omml(latex: str) -> etree._Element:
    el = etree.Element(q("m", "oMath"))
    text = latex
    for k, v in _LATEX_MAP.items():
        text = text.replace(k, v)
    frac_m = re.match(r"^([^{}]+)/([^{}]+)$", text)
    if frac_m:
        f = etree.SubElement(el, q("m", "f"))
        num = etree.SubElement(f, q("m", "num"))
        num_run = etree.SubElement(num, q("m", "r"))
        num_t = etree.SubElement(num_run, q("m", "t"))
        num_t.text = frac_m.group(1).strip()
        den = etree.SubElement(f, q("m", "den"))
        den_run = etree.SubElement(den, q("m", "r"))
        den_t = etree.SubElement(den_run, q("m", "t"))
        den_t.text = frac_m.group(2).strip()
        return el
    r = etree.SubElement(el, q("m", "r"))
    t = etree.SubElement(r, q("m", "t"))
    t.text = text
    return el


# =========================================================================
# SmartArt (PPTX)
# =========================================================================

def build_smartart_parts(nodes: list[str], kind: str = "process") -> dict[str, bytes]:
    data = etree.Element(q("dgm", "dataModel"))
    pt_lst = etree.SubElement(data, q("dgm", "ptLst"))
    for i, n in enumerate(nodes):
        pt = etree.SubElement(pt_lst, q("dgm", "pt"))
        pt.set("modelId", f"pt{i}")
        pr = etree.SubElement(pt, q("dgm", "prSet"))
        pr.set("phldr", "0")
        etree.SubElement(pt, q("dgm", "spPr"))
        t = etree.SubElement(pt, q("dgm", "t"))
        t.text = n
    return {
        "ppt/diagrams/data1.xml": etree.tostring(data, xml_declaration=True, encoding="UTF-8", standalone=True),
        "ppt/diagrams/layout1.xml": _dgm_layout(kind),
        "ppt/diagrams/quickStyle1.xml": _dgm_quickstyle(),
        "ppt/diagrams/colors1.xml": _dgm_colors(),
    }


def _dgm_layout(kind: str) -> bytes:
    root = etree.Element(q("dgm", "layoutDef"))
    etree.SubElement(root, q("dgm", "title")).set("val", kind.capitalize())
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _dgm_quickstyle() -> bytes:
    root = etree.Element(q("dgm", "styleDef"))
    etree.SubElement(root, q("dgm", "title")).set("val", "Simple")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _dgm_colors() -> bytes:
    root = etree.Element(q("dgm", "colorsDef"))
    etree.SubElement(root, q("dgm", "title")).set("val", "Accent 1")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


# =========================================================================
# Morph transition
# =========================================================================

def make_morph_transition(duration_ms: int = 1000) -> etree._Element:
    trans = etree.Element(q("p", "transition"))
    trans.set("spd", "slow" if duration_ms > 900 else "med")
    trans.set("advClick", "1")
    etree.SubElement(trans, q("p", "fade"))
    extLst = etree.SubElement(trans, q("p", "extLst"))
    ext = etree.SubElement(extLst, q("p", "ext"))
    ext.set("uri", "{F2A2F8E5-C0F4-4D6A-9A9D-3B4E0C2F0E8C}")
    morph = etree.SubElement(ext, q("p159", "morph"))
    morph.set("option", "byObject")
    return trans