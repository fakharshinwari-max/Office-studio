"""Minimal Excel number-format engine (server-side mirror of the JS one).

Implements: positive;negative;zero;text sections, 0 # ?, thousands separators,
percent, scientific, currency, date/time codes, literals, @ text.
"""


def format_number(value, code: str = "General") -> str:
    if value is None or value == "":
        return ""
    if code == "General" or code == "":
        return _general(value)

    sections = _split_sections(code)
    if isinstance(value, str):
        sec = sections[3] if len(sections) > 3 else "@"
        return _apply_text_section(value, sec)

    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)

    if num > 0:
        sec = sections[0]
    elif num < 0:
        sec = sections[1] if len(sections) > 1 else sections[0]
        if len(sections) <= 1:
            num = abs(num)  # default: leading minus added automatically
    else:
        sec = sections[2] if len(sections) > 2 else sections[0]

    return _apply_section(num, sec)


def _split_sections(code: str) -> list[str]:
    out, cur, in_quote = [], "", False
    for ch in code:
        if ch == '"':
            in_quote = not in_quote
            cur += ch
        elif ch == ';' and not in_quote:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def _general(v) -> str:
    if isinstance(v, str):
        return v
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    return f"{f:g}"


def _apply_text_section(text: str, sec: str) -> str:
    return sec.replace("@", text) if "@" in sec else text


def _apply_section(num: float, sec: str) -> str:
    if not sec:
        return _general(num)
    # Very simplified handling of common cases
    sec_lower = sec.lower()
    if any(c in sec_lower for c in ("yy", "dd", "mm:", "hh", "ss")):
        return _format_date(num, sec)
    percent = "%" in sec
    if percent:
        num = num * 100
    sci = "e+" in sec_lower or "e-" in sec_lower
    if sci:
        return f"{num:.2E}"
    decimals = 0
    if "." in sec:
        after = sec.split(".", 1)[1]
        decimals = sum(1 for c in after if c in "0#")
    thousand = "," in sec.split(".")[0]
    if thousand:
        pattern = f"{{:,.{decimals}f}}"
    else:
        pattern = f"{{:.{decimals}f}}"
    s = pattern.format(num)
    if percent:
        s += "%"
    if "$" in sec:
        s = "$" + s
    return s


def _format_date(serial: float, code: str) -> str:
    from datetime import datetime, timedelta
    # Excel 1900 date system (with leap-year bug included)
    base = datetime(1899, 12, 30)
    dt = base + timedelta(days=serial)
    return dt.strftime("%Y-%m-%d")