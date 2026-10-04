"""Server-side formula evaluator (Python mirror of the JS engine).

This is intentionally a *subset* — it exists to cross-check results of the
JS engine in CI. Anything it can't evaluate raises ValueError, which the CI
oracle job treats as "skip this case" (with an allow-list).
"""
from __future__ import annotations
import math
import re
from typing import Any

Cell = dict[str, Any]


# ---------- Tokenizer ----------

_TOKEN = re.compile(r"""
    (?P<num>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
  | (?P<str>"(?:[^"]|"")*")
  | (?P<op><=|>=|<>|[+\-*/^&%=<>(),:!])
  | (?P<ident>[A-Za-z_$][A-Za-z0-9_$.]*)
  | (?P<ws>\s+)
""", re.VERBOSE)


def tokenize(src: str):
    out = []
    i = 0
    while i < len(src):
        m = _TOKEN.match(src, i)
        if not m:
            raise ValueError(f"Unexpected char {src[i]!r} at {i}")
        kind = m.lastgroup
        text = m.group()
        if kind == "ws":
            i = m.end(); continue
        if kind == "num":
            out.append(("num", float(text)))
        elif kind == "str":
            out.append(("str", text[1:-1].replace('""', '"')))
        elif kind == "op":
            out.append(("op", text))
        elif kind == "ident":
            out.append(("ident", text))
        i = m.end()
    return out


# ---------- Parser (recursive descent, same grammar as JS) ----------

class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0

    def peek(self):
        return self.toks[self.pos] if self.pos < len(self.toks) else None

    def eat(self, val=None):
        t = self.peek()
        if t is None or (val is not None and t[1] != val):
            raise ValueError(f"Expected {val}, got {t}")
        self.pos += 1
        return t

    def parse(self):
        ast = self.expr()
        if self.pos != len(self.toks):
            raise ValueError("Trailing tokens")
        return ast

    def expr(self):
        left = self.concat()
        while self.peek() and self.peek()[1] in ("=", "<", ">", "<=", ">=", "<>"):
            op = self.eat()[1]
            right = self.concat()
            left = ("bin", op, left, right)
        return left

    def concat(self):
        left = self.addsub()
        while self.peek() and self.peek()[1] == "&":
            self.eat("&")
            left = ("bin", "&", left, self.addsub())
        return left

    def addsub(self):
        left = self.muldiv()
        while self.peek() and self.peek()[1] in ("+", "-"):
            op = self.eat()[1]
            left = ("bin", op, left, self.muldiv())
        return left

    def muldiv(self):
        left = self.unary()
        while self.peek() and self.peek()[1] in ("*", "/"):
            op = self.eat()[1]
            left = ("bin", op, left, self.unary())
        return left

    def unary(self):
        if self.peek() and self.peek()[1] == "-":
            self.eat("-"); return ("neg", self.unary())
        if self.peek() and self.peek()[1] == "+":
            self.eat("+"); return self.unary()
        return self.pow()

    def pow(self):
        left = self.postfix()
        if self.peek() and self.peek()[1] == "^":
            self.eat("^")
            left = ("bin", "^", left, self.unary())
        return left

    def postfix(self):
        n = self.primary()
        while self.peek() and self.peek()[1] == "%":
            self.eat("%"); n = ("pct", n)
        return n

    def primary(self):
        t = self.peek()
        if not t:
            raise ValueError("Unexpected end")
        if t[0] == "num":
            self.pos += 1
            return ("num", t[1])
        if t[0] == "str":
            self.pos += 1
            return ("str", t[1])
        if t[1] == "(":
            self.eat("(")
            e = self.expr()
            self.eat(")")
            return e
        if t[0] == "ident":
            self.pos += 1
            if self.peek() and self.peek()[1] == "(":
                self.eat("(")
                args = []
                if not (self.peek() and self.peek()[1] == ")"):
                    args.append(self.expr())
                    while self.peek() and self.peek()[1] == ",":
                        self.eat(",")
                        args.append(self.expr())
                self.eat(")")
                return ("call", t[1].upper(), args)
            if self.peek() and self.peek()[1] == "!":
                self.eat("!")
                nt = self.peek()
                if nt and nt[0] == "ident":
                    self.pos += 1
                    ref = nt[1]
                    if self.peek() and self.peek()[1] == ":":
                        self.eat(":")
                        n2 = self.peek()
                        if n2 and n2[0] == "ident":
                            self.pos += 1
                            ref += ":" + n2[1]
                    return ("ref", ref, t[1])
            ref = t[1]
            if self.peek() and self.peek()[1] == ":":
                self.eat(":")
                n2 = self.peek()
                if n2 and n2[0] == "ident":
                    self.pos += 1
                    ref += ":" + n2[1]
            up = ref.upper()
            if up == "TRUE":  return ("bool", True)
            if up == "FALSE": return ("bool", False)
            return ("ref", ref, None)
        raise ValueError(f"Unexpected token {t}")


# ---------- Evaluator ----------

class EvalCtx:
    def __init__(self, cells: dict[str, Cell]):
        self.cells = cells
        self.sheets: dict[str, dict[str, Cell]] = {}
        self.visiting: set[str] = set()
        self.cache: dict[str, Any] = {}


def evaluate_formulas(formulas: dict[str, str], cells: dict[str, Cell]) -> dict[str, Any]:
    ctx = EvalCtx(cells)
    for ref, f in formulas.items():
        cells[ref] = {"f": f if f.startswith("=") else "=" + f}
    out = {}
    for ref in formulas:
        out[ref] = _get_val(ref, ctx)
    return out


def _get_val(ref: str, ctx: EvalCtx):
    if ref in ctx.cache:
        return ctx.cache[ref]
    if ref in ctx.visiting:
        return "#REF!"
    cell = ctx.cells.get(ref)
    if not cell:
        return 0
    if "f" in cell:
        ctx.visiting.add(ref)
        try:
            ast = Parser(tokenize(cell["f"][1:])).parse()
            v = _eval(ast, ctx)
        except Exception:
            v = "#VALUE!"
        finally:
            ctx.visiting.discard(ref)
        ctx.cache[ref] = v
        return v
    v = cell.get("v", 0)
    ctx.cache[ref] = v
    return v


def _eval(node, ctx: EvalCtx):
    k = node[0]
    if k == "num": return node[1]
    if k == "str": return node[1]
    if k == "bool": return node[1]
    if k == "neg": return -_to_num(_eval(node[1], ctx))
    if k == "pct": return _to_num(_eval(node[1], ctx)) / 100
    if k == "bin":
        op, l, r = node[1], _eval(node[2], ctx), _eval(node[3], ctx)
        return _binop(op, l, r)
    if k == "ref":
        ref, sheet = node[1], node[2]
        if ":" in ref:
            a, b = ref.split(":")
            return _expand_range(ctx, a, b)
        return _get_val(ref, ctx)
    if k == "call":
        args = [_eval(a, ctx) for a in node[2]]
        return _call(node[1], args)
    raise ValueError(f"Bad node {node}")


def _binop(op, a, b):
    if op == "+": return _to_num(a) + _to_num(b)
    if op == "-": return _to_num(a) - _to_num(b)
    if op == "*": return _to_num(a) * _to_num(b)
    if op == "/":
        d = _to_num(b)
        return "#DIV/0!" if d == 0 else _to_num(a) / d
    if op == "^": return _to_num(a) ** _to_num(b)
    if op == "&": return _str(a) + _str(b)
    if op == "=": return _eq(a, b)
    if op == "<>": return not _eq(a, b)
    if op == "<": return _cmp(a, b) < 0
    if op == ">": return _cmp(a, b) > 0
    if op == "<=": return _cmp(a, b) <= 0
    if op == ">=": return _cmp(a, b) >= 0
    return "#VALUE!"


def _to_num(v):
    if isinstance(v, bool): return 1 if v else 0
    if isinstance(v, (int, float)): return v
    if v is None or v == "": return 0
    try: return float(v)
    except Exception: return 0def _str(v):
    if isinstance(v, bool): return "TRUE" if v else "FALSE"
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)


def _eq(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a.lower() == b.lower()
    if isinstance(a, bool) or isinstance(b, bool):
        return _to_num(a) == _to_num(b)
    try: return _to_num(a) == _to_num(b)
    except Exception: return str(a).lower() == str(b).lower()


def _cmp(a, b):
    try: return _to_num(a) - _to_num(b)
    except Exception:
        sa, sb = str(a).lower(), str(b).lower()
        return -1 if sa < sb else (1 if sa > sb else 0)


def _expand_range(ctx, a, b):
    ma = re.match(r"^([A-Z]+)(\d+)$", a)
    mb = re.match(r"^([A-Z]+)(\d+)$", b)
    if not ma or not mb:
        return 0
    c0, r0 = _col(ma.group(1)), int(ma.group(2))
    c1, r1 = _col(mb.group(1)), int(mb.group(2))
    out = []
    for r in range(min(r0, r1), max(r0, r1) + 1):
        for c in range(min(c0, c1), max(c0, c1) + 1):
            out.append(_get_val(_name(c, r), ctx))
    return out


def _col(name):
    n = 0
    for ch in name.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _name(c, r):
    s = ""
    c += 1
    while c > 0:
        c, m = divmod(c - 1, 26)
        s = chr(65 + m) + s
    return f"{s}{r}"


# ---------- Function library (subset) ----------

def _call(name, args):
    flat = lambda x: x if isinstance(x, list) else [x]
    nums = [v for a in args for v in flat(a) if isinstance(v, (int, float)) and not isinstance(v, bool)]

    if name == "SUM":     return sum(nums)
    if name == "PRODUCT": 
        p = 1
        for v in nums: p *= v
        return p
    if name == "AVERAGE": return sum(nums) / len(nums) if nums else "#DIV/0!"
    if name == "MIN":     return min(nums) if nums else 0
    if name == "MAX":     return max(nums) if nums else 0
    if name == "COUNT":   return len(nums)
    if name == "COUNTA":
        return len([v for a in args for v in flat(a) if v not in ("", None)])
    if name == "ABS":     return abs(_to_num(args[0]))
    if name == "ROUND":
        n, d = _to_num(args[0]), int(_to_num(args[1])) if len(args) > 1 else 0
        return round(n + 1e-12, d)
    if name == "ROUNDDOWN":
        n, d = _to_num(args[0]), int(_to_num(args[1])) if len(args) > 1 else 0
        m = 10 ** d
        return math.floor(n * m) / m
    if name == "ROUNDUP":
        n, d = _to_num(args[0]), int(_to_num(args[1])) if len(args) > 1 else 0
        m = 10 ** d
        return math.ceil(n * m) / m
    if name == "SQRT":    return math.sqrt(_to_num(args[0]))
    if name == "POWER":   return _to_num(args[0]) ** _to_num(args[1])
    if name == "MOD":
        a, b = _to_num(args[0]), _to_num(args[1])
        return "#DIV/0!" if b == 0 else a - b * math.floor(a / b)
    if name == "IF":      return args[1] if _truthy(args[0]) else (args[2] if len(args) > 2 else False)
    if name == "AND":     return all(_truthy(v) for a in args for v in flat(a))
    if name == "OR":      return any(_truthy(v) for a in args for v in flat(a))
    if name == "NOT":     return not _truthy(args[0])
    if name == "IFERROR": return args[1] if isinstance(args[0], str) and args[0].startswith("#") else args[0]
    if name == "CONCAT" or name == "CONCATENATE":
        return "".join(_str(v) for a in args for v in flat(a))
    if name == "LEFT":
        return _str(args[0])[:int(_to_num(args[1])) if len(args) > 1 else 1]
    if name == "RIGHT":
        return _str(args[0])[-int(_to_num(args[1])) if len(args) > 1 else -1:] or _str(args[0])
    if name == "LEN":     return len(_str(args[0]))
    if name == "UPPER":   return _str(args[0]).upper()
    if name == "LOWER":   return _str(args[0]).lower()
    if name == "TRIM":    return " ".join(_str(args[0]).split())
    if name == "MEDIAN":
        n = sorted(nums); L = len(n)
        if not L: return "#NUM!"
        return n[L // 2] if L % 2 else (n[L // 2 - 1] + n[L // 2]) / 2
    if name == "VLOOKUP":
        lookup = args[0]
        table = args[1]
        col = int(_to_num(args[2])) - 1
        rows = table if table and isinstance(table[0], list) else [table]
        for row in rows:
            if row and _eq(row[0], lookup):
                return row[col] if col < len(row) else "#REF!"
        return "#N/A"
    if name == "SUMIF":
        rng, crit, srng = args[0], args[1], args[2] if len(args) > 2 else args[0]
        rng = rng if isinstance(rng, list) else [rng]
        srng = srng if isinstance(srng, list) else [srng]
        s = 0
        for i, v in enumerate(rng):
            if _match_crit(v, crit) and i < len(srng):
                s += _to_num(srng[i])
        return s
    if name == "COUNTIF":
        rng = args[0] if isinstance(args[0], list) else [args[0]]
        return sum(1 for v in rng if _match_crit(v, args[1]))

    raise ValueError(f"Unsupported function in server evaluator: {name}")


def _truthy(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    if isinstance(v, str): return v != "" and v.lower() != "false"
    return bool(v)


def _match_crit(v, crit):
    if not isinstance(crit, str):
        return _eq(v, crit)
    m = re.match(r"^(<=|>=|<>|=|<|>)?(.*)$", crit)
    op, val = m.group(1) or "=", m.group(2)
    try: val = float(val)
    except Exception: pass
    if op == "=":  return _eq(v, val)
    if op == "<>": return not _eq(v, val)
    if op == "<":  return _cmp(v, val) < 0
    if op == ">":  return _cmp(v, val) > 0
    if op == "<=": return _cmp(v, val) <= 0
    if op == ">=": return _cmp(v, val) >= 0
    return False