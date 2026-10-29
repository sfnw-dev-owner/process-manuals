"""Annotations for the manuals' figures: icons, labels and leaders.

A note is placed like a component (it goes in a component's children with a
Location and an optional "manual:..." tag), but has no solids. It's drawn
where its placement's origin lands in the figure, facing the reader; its own
sizes, offsets and rotation are in drawing units (inches) in the figure's
plane: X to the right, Y up.

Icons are the PNGs in common/clipart.
"""

from dataclasses import dataclass
from math import cos, radians, sin

from build123d import Compound, Location


class Note:
    def shape(self, hidden=frozenset(), mods=(), shown=frozenset()):
        return Compound([])

    def tags(self):
        return frozenset()

    def notes(self, shown=frozenset(), hidden=frozenset()):
        return [(Location(), self)]


@dataclass(frozen=True)
class Icon(Note):
    """A clipart icon, centered on its anchor (plus an offset), scaled to
    width x height."""
    name: str  # common/clipart/<name>.png
    width: float
    height: float
    rotation: float = 0  # degrees, counterclockwise
    flip: bool = False  # mirrored left-right
    dx: float = 0
    dy: float = 0


@dataclass(frozen=True)
class Label(Note):
    """Text at its anchor (plus an offset); lines separated by newlines."""
    text: str
    height: float = 2.5  # of a capital letter
    rotation: float = 0
    dx: float = 0
    dy: float = 0
    attach: int = 5  # which point of the text is at the anchor, as DXF MTEXT: 1 top-left ... 5 center ... 9 bottom-right
    # One line in pieces of different heights, ((text, height), ...) on one
    # baseline, as MTEXT's \H codes (text is then just for reference).
    runs: tuple = None
    # Bold: True for the whole label, or a tuple of the words (substrings) set bold.
    bold: object = False


@dataclass(frozen=True)
class Leader(Note):
    """A line from its anchor (plus an offset) through the given points,
    relative to the anchor, with an arrowhead at the anchor end."""
    points: tuple  # ((dx, dy), ...)
    dx: float = 0
    dy: float = 0
    arrow: bool = True
    color: tuple = (0, 0, 0)
    weight: float = 1  # line weight (and arrowhead size), relative to the usual
    head: float = 1  # arrowhead size, relative to the usual


@dataclass(frozen=True)
class Circle(Note):
    """A circle around its anchor (plus an offset), e.g. a detail callout."""
    radius: float
    dx: float = 0
    dy: float = 0
    fill: tuple = None  # (r, g, b), or none
    weight: float = 1  # line weight, relative to the usual


def crossed_box(width, height):
    """Leaders drawing a box with both diagonals (lumber cut in section), from
    the anchor at its lower-left corner."""
    return [Leader(((width, 0), (width, height), (0, height), (0, 0), (width, height)), arrow=False),
            Leader(((width, -height),), arrow=False, dy=height)]


def vertical_dimension(length, text, text_offset=-1.9):
    """A dimension line up from its anchor, arrows at both ends, its text
    rotated alongside (to the left for a negative offset)."""
    return [Leader(((0, length),)), Leader(((0, -length),), dy=length),
            Label(text, 2, rotation=90, dx=text_offset, dy=length / 2, attach=8 if text_offset < 0 else 2)]


def horizontal_dimension(length, text, text_offset=-1.9, extension=0):
    """A dimension line to the right from its anchor, arrows at both ends, its
    text alongside (below for a negative offset), and extension lines
    `extension` long up from both ends (down if negative)."""
    out = [Leader(((length, 0),)), Leader(((-length, 0),), dx=length),
           Label(text, 2, dx=length / 2, dy=text_offset, attach=2 if text_offset < 0 else 8)]
    if extension:
        out += [Leader(((0, extension),), arrow=False, dx=dx, weight=1/2) for dx in (0, length)]
    return out


def inches(x):
    """x inches as the manuals write them: 4½" (to the nearest 1/16)."""
    whole, sixteenths = divmod(round(x * 16), 16)
    if sixteenths == 0:
        return f'{whole}"'
    from fractions import Fraction
    frac = Fraction(sixteenths, 16)
    glyphs = {Fraction(1, 2): "½", Fraction(1, 4): "¼", Fraction(3, 4): "¾", Fraction(1, 8): "⅛", Fraction(3, 8): "⅜",
              Fraction(5, 8): "⅝", Fraction(7, 8): "⅞"}
    part = glyphs.get(frac)
    if part is None:  # no glyph: 4 7/16"
        part = f"{frac.numerator}/{frac.denominator}"
        return f'{whole} {part}"' if whole else f'{part}"'
    return f'{whole}{part}"' if whole else f'{part}"'


@dataclass(frozen=True)
class Lines(Note):
    """A small line drawing (a detail or an illustration): segments
    ((x0, y0), (x1, y1)) relative to the anchor (plus an offset)."""
    segments: tuple
    dx: float = 0
    dy: float = 0
    color: tuple = (0, 0, 0)
    weight: float = 1  # line weight, relative to the usual


def box(width, height, weight=1, color=(0, 0, 0)):
    """A rectangle from its anchor at the top-left corner (as LayOut drew the
    frames around tool icons; at LayOut's stroke weight: Lines draw at half a
    Leader's)."""
    w, h = width, height
    return Lines((((0, 0), (w, 0)), ((w, 0), (w, -h)), ((w, -h), (0, -h)), ((0, -h), (0, 0))), weight=2 * weight, color=color)


def cross(size):
    """A + mark centered on its anchor, e.g. where a screw goes."""
    return Lines((((-size, 0), (size, 0)), ((0, -size), (0, size))))


def dashed_line(dx, dy, dash=0.06, gap=0.05, weight=1, color=(0, 0, 0)):
    """A dashed line from its anchor to (dx, dy), in dashes `dash` long with
    `gap` between them (LayOut's dashes by default)."""
    length = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / length, dy / length
    segments, s = [], 0
    while s < length:
        e = min(s + dash, length)
        segments.append(((ux * s, uy * s), (ux * e, uy * e)))
        s += dash + gap
    return Lines(tuple(segments), weight=weight, color=color)


def dashed_arc(radius, start, end, dash=0.06, gap=0.05, weight=1, color=(0, 0, 0)):
    """A dashed arc centered on its anchor, from `start` to `end` degrees
    (counterclockwise from +X; the short way round), in dashes `dash` long
    with `gap` between them (LayOut's dashes by default)."""
    sweep = radians(end - start)
    length = abs(sweep) * radius
    sign = 1 if sweep >= 0 else -1
    segments, s = [], 0
    while s < length:
        a0 = radians(start) + sign * s / radius
        a1 = radians(start) + sign * min(s + dash, length) / radius
        segments.append(((radius * cos(a0), radius * sin(a0)), (radius * cos(a1), radius * sin(a1))))
        s += dash + gap
    return Lines(tuple(segments), weight=weight, color=color)
