#!/usr/bin/env python3
"""Values the manuals take from the model: a manual writes {{NAME}} and
render/go runs its text through this before pandoc, so NAME is replaced by
its value in common/model/dimensions.py and a number lives in one place.

  values.py [--deps] MANUAL.md   prints the manual with its {{values}} filled in

An expression is a name from dimensions.py (SIDING_HEIGHT), a name from
another model module (walls.AC_SIDE_BLOCK), an element of a tuple
(WINDOW_OPENING[0]) or a small Python expression over those
(RIDGE_VENT_OVERHANG-SHINGLE_OVERHANG). A number prints as the shop writes
it: whole inches and a fraction (93½, 77¾, ¹⁵⁄₃₂), or a decimal when it
isn't a sixty-fourth. The unit stays in the manual's text ({{STUD_LENGTH}}"
or {{STUD_LENGTH}} in). A feet-and-inches form takes the suffix :ft
({{TAR_PAPER_LENGTH:ft}} → 13'4"). With --deps (render/go's dependency pass),
a raw typst block reading the modules the values came from is appended, so
they count toward the manual's last-revision date like a figure's sources.
"""

import pathlib
import re
import sys
from fractions import Fraction

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "common"))

from model import dimensions  # noqa: E402

VALUE = re.compile(r"\{\{([^{}]+)\}\}")
GLYPHS = {(1, 2): "½", (1, 4): "¼", (3, 4): "¾", (1, 8): "⅛", (3, 8): "⅜", (5, 8): "⅝", (7, 8): "⅞", (1, 3): "⅓", (2, 3): "⅔"}
SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def fraction(n, d):
    return GLYPHS.get((n, d)) or f"{str(n).translate(SUPERSCRIPT)}⁄{str(d).translate(SUBSCRIPT)}"


def inches(v):
    """A length as the shop writes it: 93, 93½, ¾, ¹⁵⁄₃₂; else a decimal."""
    if isinstance(v, str):
        return v
    if isinstance(v, (tuple, list)):
        return " x ".join(inches(x) for x in v)
    sign, v = ("-" if v < 0 else ""), abs(v)
    f = Fraction(v).limit_denominator(64)
    if abs(float(f) - v) > 1e-9:
        return sign + f"{v:.4g}"
    whole, rest = divmod(f.numerator, f.denominator)
    if rest == 0:
        return sign + str(whole)
    return sign + (str(whole) if whole else "") + fraction(rest, f.denominator)


def feet(v):
    """13'4" for 160; 12' for 144 (pandoc's smart punctuation curls the marks)."""
    ft, inch = divmod(v, 12)
    return f"{int(ft)}'" + (f'{inches(inch)}"' if inch else "")


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


def expand(text):
    """`text` with its {{values}} filled in, and the model modules they came from."""
    namespace = Namespace()

    def value(m):
        expr = m.group(1)
        body, _, form = expr.partition(":")
        try:
            v = eval(body, {"__builtins__": {}}, namespace)
        except (NameError, AttributeError, IndexError, SyntaxError, TypeError) as e:
            raise SystemExit(f"values.py: {{{{{expr}}}}}: {e}")
        if form == "ft":
            return feet(v)
        if form:
            raise SystemExit(f"values.py: {{{{{expr}}}}}: unknown form '{form}'")
        return inches(v)

    return VALUE.sub(value, text), namespace.modules


def dependencies(modules):
    """A raw typst block making the modules dependencies of the document
    (the same trick render/model.lua uses for a figure's sources)."""
    paths = sorted("/" + str(pathlib.Path(m.__file__).resolve().relative_to(REPO)) for m in modules)
    reads = "\n".join(f'#let _ = read("{p}", encoding: none)' for p in paths)
    return f"\n\n```{{=typst}}\n{reads}\n```\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    deps = "--deps" in args
    (path,) = [a for a in args if a != "--deps"]
    text, modules = expand(pathlib.Path(path).read_text())
    sys.stdout.write(text + (dependencies(modules) if deps and VALUE.search(pathlib.Path(path).read_text()) else ""))
