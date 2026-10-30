#!/usr/bin/env python3
"""Values the manuals take from the model: a manual writes {{NAME}} and
render/model.lua replaces it with the value of NAME in
common/model/dimensions.py, so a number lives in one place.

  values.py [--deps] EXPR...   prints JSON: {"values": {EXPR: text}, "deps": [path]}

An expression is a name from dimensions.py (SIDING_HEIGHT), a name from
another model module (walls.AC_SIDE_BLOCK), an element of a tuple
(WINDOW_OPENING[0]) or a small Python expression over those
(RIDGE_VENT_OVERHANG-SHINGLE_OVERHANG). The unit comes from the model: a
number is a length in inches, printed as the shop writes it (93½”, 77¾”,
¹⁵⁄₃₂”, or a decimal when it isn't a sixty-fourth); dimensions.Degrees
prints with ° and dimensions.Count prints bare. The suffix :ft prints a
length in feet and inches ({{TAR_PAPER_LENGTH:ft}} → 13’4”). "deps" lists
the modules the values came from, for the manual's last-revision date.
"""

import json
import pathlib
import sys
from fractions import Fraction

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "common"))

from model import dimensions  # noqa: E402

INCH, FOOT = "”", "’"  # the curly marks pandoc's smart punctuation makes of a typed " and '
GLYPHS = {(1, 2): "½", (1, 4): "¼", (3, 4): "¾", (1, 8): "⅛", (3, 8): "⅜", (5, 8): "⅝", (7, 8): "⅞", (1, 3): "⅓", (2, 3): "⅔"}
SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def fraction(n, d):
    return GLYPHS.get((n, d)) or f"{str(n).translate(SUPERSCRIPT)}⁄{str(d).translate(SUBSCRIPT)}"


def number(v):
    """A number as the shop writes it: 93, 93½, ¾, ¹⁵⁄₃₂; else a decimal."""
    sign, v = ("-" if v < 0 else ""), abs(v)
    f = Fraction(v).limit_denominator(64)
    if abs(float(f) - v) > 1e-9:
        return sign + f"{v:.4g}"
    whole, rest = divmod(f.numerator, f.denominator)
    if rest == 0:
        return sign + str(whole)
    return sign + (str(whole) if whole else "") + fraction(rest, f.denominator)


def text(v):
    """A value with its unit: 84”, 18½°, 5, 48” x 96”."""
    if isinstance(v, str):
        return v
    if isinstance(v, (tuple, list)):
        return " x ".join(text(x) for x in v)
    if isinstance(v, dimensions.Degrees):
        return number(v) + "°"
    if isinstance(v, dimensions.Count):
        return str(int(v))
    return number(v) + INCH


def feet(v):
    """13’4” for 160; 12’ for 144."""
    ft, inch = divmod(v, 12)
    return f"{int(ft)}{FOOT}" + (number(inch) + INCH if inch else "")


class Namespace(dict):
    """dimensions.py's names, and any other model module by name."""

    def __init__(self):
        super().__init__({k: v for k, v in vars(dimensions).items() if not k.startswith("_")})
        self.modules = {dimensions}

    def __missing__(self, name):
        try:
            module = __import__(f"model.{name}", fromlist=[name])
        except ModuleNotFoundError:
            raise NameError(f"{name} is not in dimensions.py (nor a model module)") from None
        self.modules.add(module)
        return module


def evaluate(exprs):
    """{expr: its text} for the expressions, and the model modules they came from."""
    namespace = Namespace()
    values = {}
    for expr in exprs:
        body, _, form = expr.partition(":")
        try:
            v = eval(body, {"__builtins__": {}}, namespace)
        except (NameError, AttributeError, IndexError, SyntaxError, TypeError) as e:
            raise SystemExit(f"values.py: {{{{{expr}}}}}: {e}")
        if form == "ft":
            values[expr] = feet(v)
        elif form:
            raise SystemExit(f"values.py: {{{{{expr}}}}}: unknown form '{form}'")
        else:
            values[expr] = text(v)
    return values, namespace.modules


if __name__ == "__main__":
    exprs = [a for a in sys.argv[1:] if a != "--deps"]
    values, modules = evaluate(exprs)
    deps = sorted("/" + str(pathlib.Path(m.__file__).resolve().relative_to(REPO)) for m in modules) if "--deps" in sys.argv else []
    print(json.dumps({"values": values, "deps": deps}, ensure_ascii=False))
