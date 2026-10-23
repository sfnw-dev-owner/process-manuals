"""Annotations for the manuals' figures: icons, labels and leaders.

A note is placed like a component (it goes in a component's children with a
Location and an optional "manual:..." tag), but has no solids. It's drawn
where its placement's origin lands in the figure, facing the reader; its own
sizes, offsets and rotation are in drawing units (inches) in the figure's
plane: X to the right, Y up.

Icons are the PNGs in common/clipart.
"""

from dataclasses import dataclass

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
    """A clipart icon, centered on its anchor (plus an offset)."""
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


@dataclass(frozen=True)
class Lines(Note):
    """A small line drawing (a detail or an illustration): segments
    ((x0, y0), (x1, y1)) relative to the anchor (plus an offset)."""
    segments: tuple
    dx: float = 0
    dy: float = 0
    color: tuple = (0, 0, 0)
    weight: float = 1  # line weight, relative to the usual
