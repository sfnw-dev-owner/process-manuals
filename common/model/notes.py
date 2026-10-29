"""Annotations for the manuals' figures: icons, labels, leaders, circles and
small line drawings, and the helpers that place them.

A note goes in a figure's `notes` as (x, y, note): its anchor is a point of
the figure (a drawing's frame, in model inches; or a page's, in page inches,
from the top-left corner, y down), and everything about the note itself
(its size, its offset from the anchor, a leader's points, a line's weight) is
in inches on paper, so a note looks the same whatever scale the manual prints
the drawing at. Note offsets and points are X to the right and Y up.

Figures place notes by points of the model, with the standard stand-offs
here: beside() puts a note GAP from its anchor on a given side, callout()
hangs text off a leader, aimed() points a tool icon at a joint, dimension()
measures between two points, around() circles a part, title() captions.

Icons are the PNGs in common/clipart; ICONS gives each one's size on paper.
"""

import math
from dataclasses import dataclass, replace

# ── standard sizes, inches on paper ────────────────────────────────────────

GAP = 1/16  # between a note and the part it marks
LEAD = 3/8  # a callout's text this far from what it points at
TEXT = 1/8  # a label's capital height
SMALL = 1/10
TITLE = 1/5  # a figure's caption
LINE = 1/200  # a note's line weight (and the drawings' hairline), at weight 1
ARROWHEAD = 1/14  # a leader's arrowhead, long
CIRCLED = 1/8  # radius of a circled number

# icon -> (width, height) on paper; its nose: where it points from (fractions
# of its box from the center, X right, Y up) and the direction it points
# (degrees counterclockwise from +X), as drawn
ICONS = {
    "Screw": ((0.2, 0.48), (0, -0.5), 270),
    "NailGun": ((0.58, 0.56), (-0.4, -0.47), 270),
    "Pencil": ((0.36, 0.36), (-0.45, -0.45), 225),
    "mallet": ((0.38, 0.38), (0.3, 0.35), 45),
    "Router": ((0.48, 0.48), (0, -0.5), 270),
    "staple-gun": ((0.8, 0.8), (-0.5, 0.1), 180),
    "Hurricane_Bracket": ((0.82, 1.58), (0, 0), 0),
    "drill_icon": ((0.6, 0.56), (-0.5, 0.1), 180),
}


# ── the notes ──────────────────────────────────────────────────────────────

class Note:
    """(Until every manual's notes are in its figure table: a note placed as
    a component's child, which has no solids.)"""
    def shape(self, hidden=frozenset(), mods=(), shown=frozenset()):
        from build123d import Compound
        return Compound([])

    def tags(self):
        return frozenset()

    def notes(self, shown=frozenset(), hidden=frozenset()):
        from build123d import Location
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
    height: float = TEXT  # of a capital letter
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
    weight: float = 1  # line weight, relative to LINE
    head: float = 1  # arrowhead size, relative to ARROWHEAD


@dataclass(frozen=True)
class Circle(Note):
    """A circle around its anchor (plus an offset), e.g. a detail callout."""
    radius: float
    dx: float = 0
    dy: float = 0
    fill: tuple = None  # (r, g, b), or none
    weight: float = 1  # line weight, relative to LINE


@dataclass(frozen=True)
class Lines(Note):
    """A small line drawing (a box, a cross, a dashed arc): segments
    ((x0, y0), (x1, y1)) relative to the anchor (plus an offset)."""
    segments: tuple
    dx: float = 0
    dy: float = 0
    color: tuple = (0, 0, 0)
    weight: float = 1  # line weight, relative to LINE



# ── placing notes by points of the figure ──────────────────────────────────

SIDES = {"right": 0, "above right": 45, "above": 90, "above left": 135, "left": 180,
         "below left": 225, "below": 270, "below right": 315}


def _direction(side):
    """A side's unit vector (or an angle's, in degrees)."""
    a = math.radians(SIDES[side] if isinstance(side, str) else side)
    return math.cos(a), math.sin(a)


def _attach(ux, uy, rotation=0):
    """The MTEXT attachment point of a label whose near side faces back along
    (ux, uy) (the direction from the anchor to the label), for text rotated
    `rotation` degrees: the text's own left/right/top/bottom."""
    a = math.radians(-rotation)
    tx, ty = ux * math.cos(a) - uy * math.sin(a), ux * math.sin(a) + uy * math.cos(a)
    col = 0 if tx > 0.38 else 2 if tx < -0.38 else 1  # the label's left, center, or right at the anchor
    row = 2 if ty > 0.38 else 0 if ty < -0.38 else 1  # its bottom, middle, or top
    return 1 + col + 3 * row


def rotated_extent(width, height, degrees):
    """(w, h) of the axis-aligned box of a width x height box rotated."""
    a = math.radians(degrees)
    return abs(width * math.cos(a)) + abs(height * math.sin(a)), abs(width * math.sin(a)) + abs(height * math.cos(a))


def beside(point, side, note, gap=GAP):
    """`note` placed `gap` from `point` (x, y) on `side` ("left", "above
    right", ..., or degrees counterclockwise from +X): a label by its near
    edge, an icon or a circle by its box; a leader starts at the point."""
    x, y = point
    ux, uy = _direction(side)
    if isinstance(note, Label):
        return (x, y, replace(note, attach=_attach(ux, uy, note.rotation), dx=note.dx + ux * gap, dy=note.dy + uy * gap))
    if isinstance(note, Icon):
        w, h = rotated_extent(note.width, note.height, note.rotation)
        # how far the box's center is from the point, along (ux, uy), for its edge to be `gap` off
        reach = min(w / 2 / abs(ux) if ux else math.inf, h / 2 / abs(uy) if uy else math.inf)
        return (x, y, replace(note, dx=note.dx + ux * (gap + reach), dy=note.dy + uy * (gap + reach)))
    if isinstance(note, Circle):
        return (x, y, replace(note, dx=note.dx + ux * (gap + note.radius), dy=note.dy + uy * (gap + note.radius)))
    return (x, y, note)


def at(point, note):
    """`note` right on `point`."""
    return (point[0], point[1], note)


def callout(point, text, side="above right", lead=LEAD, height=TEXT, tail=1/8, **label):
    """Text `lead` from `point` on `side`, with a leader from it to the point:
    the leader runs from the point, then (for a side off the vertical) turns
    level for `tail` into the text."""
    x, y = point
    ux, uy = _direction(side)
    px, py = ux * lead, uy * lead
    if abs(ux) > 0.01:
        tx = tail if ux > 0 else -tail
        points = ((px, py), (px + tx, py))
        attach = 4 if ux > 0 else 6
        label_at = (px + tx + (GAP if ux > 0 else -GAP), py)
    else:
        points = ((px, py),)
        attach = 8 if uy > 0 else 2
        label_at = (px, py + (GAP if uy > 0 else -GAP))
    return [(x, y, Leader(points)), (x, y, Label(text, height, dx=label_at[0], dy=label_at[1], attach=attach, **label))]


def pointer(point, dx, dy, arrow=True, weight=1):
    """A leader from (dx, dy) (paper inches) off `point` to it."""
    return (point[0], point[1], Leader(((dx, dy),), arrow=arrow, weight=weight))


def line(p, q, scale, weight=1/2, short=(0, 0)):
    """A plain line between two points of a drawing printed at `scale`,
    stopping `short` (paper inches) of each end: between two circles' edges, say."""
    dx, dy = (q[0] - p[0]) * scale, (q[1] - p[1]) * scale
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    a, b = short
    return (p[0], p[1], Leader(((ux * (length - b), uy * (length - b)),), dx=ux * a, dy=uy * a, arrow=False, weight=weight))


def _box_of(note):
    """A placed note's box (x0, y0, x1, y1), paper inches from its anchor."""
    if isinstance(note, Icon):
        w, h = rotated_extent(note.width, note.height, note.rotation)
        return note.dx - w / 2, note.dy - h / 2, note.dx + w / 2, note.dy + h / 2
    if isinstance(note, Circle):
        return note.dx - note.radius, note.dy - note.radius, note.dx + note.radius, note.dy + note.radius
    if isinstance(note, Label):  # roughly: the text's advance and its lines
        lines = note.text.split("\n")
        w, h = 0.6 * note.height * max(map(len, lines)), note.height * (1 + 5 / 3 * (len(lines) - 1))
        col, row = (note.attach - 1) % 3, (note.attach - 1) // 3
        x0, y1 = note.dx - w * col / 2, note.dy + h * row / 2
        return x0, y1 - h, x0 + w, y1
    raise TypeError(f"no box for {note}")


def next_to(placed, side, note, gap=GAP):
    """`note` placed `gap` beyond an already placed note (x, y, note) on `side`
    of it: "x2" beside a screw, say."""
    x, y, first = placed
    x0, y0, x1, y1 = _box_of(first)
    ux, uy = _direction(side)
    edge = (x1 if ux > 0.01 else x0 if ux < -0.01 else (x0 + x1) / 2, y1 if uy > 0.01 else y0 if uy < -0.01 else (y0 + y1) / 2)
    out = beside((x, y), side, note, gap)
    return (x, y, replace(out[2], dx=out[2].dx + edge[0], dy=out[2].dy + edge[1]))


def icon(name, size=1, rotation=0, flip=False):
    """A clipart icon at its standard size (times `size`)."""
    (w, h), _, _ = ICONS[name]
    return Icon(name, w * size, h * size, rotation=rotation, flip=flip)


def aimed(point, name, toward, size=1, gap=GAP, flip=None):
    """A tool icon with its nose `gap` short of `point`, pointing `toward`
    it: a side ("below": the tool is below the point, pointing up) or
    degrees counterclockwise from +X, the direction from the tool to the
    point. The icon is mirrored if that turns it less (or as `flip` says)."""
    (w, h), (nx, ny), nose = ICONS[name]
    w, h = w * size, h * size
    angle = SIDES[toward] + 180 if isinstance(toward, str) else toward
    turn = lambda rot: (rot + 180) % 360 - 180  # the least turn
    if flip is None:
        flip = abs(turn(angle - (180 - nose))) < abs(turn(angle - nose))
    if flip:
        nx, nose = -nx, 180 - nose
    rotation = turn(angle - nose)
    a = math.radians(rotation)
    # the nose, from the icon's center, once rotated
    ox, oy = nx * w, ny * h
    rx, ry = ox * math.cos(a) - oy * math.sin(a), ox * math.sin(a) + oy * math.cos(a)
    ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    cx, cy = -ux * gap - rx, -uy * gap - ry
    return (point[0], point[1], Icon(name, w, h, rotation=rotation, flip=flip, dx=cx, dy=cy))


def dimension(a, b, scale, text=None, offset=1/4):
    """A dimension between points a and b of a drawing (level or plumb)
    printed at `scale` (paper inches per drawing inch): its line `offset`
    (paper inches; negative for the other side) off them with extension
    lines from both, arrows at both ends, and its text alongside (the
    distance, unless given)."""
    (x0, y0), (x1, y1) = a, b
    level = abs(x1 - x0) >= abs(y1 - y0)
    length = math.hypot(x1 - x0, y1 - y0)
    text = inches(length) if text is None else text
    if level:
        x0, x1 = min(x0, x1), max(x0, x1)
        y = (y0 + y1) / 2
        d = (x1 - x0) * scale  # on paper
        out = [(x0, y, Leader(((d, 0),), dy=offset)), (x1, y, Leader(((-d, 0),), dy=offset)),
               (x0, y, Label(text, SMALL, dx=d / 2, dy=offset + (GAP if offset >= 0 else -GAP), attach=8 if offset >= 0 else 2))]
        out += [(x, y, Leader(((0, offset + math.copysign(GAP, offset)),), arrow=False, weight=1/2)) for x in (x0, x1)]
    else:
        y0, y1 = min(y0, y1), max(y0, y1)
        x = (x0 + x1) / 2
        d = (y1 - y0) * scale
        out = [(x, y0, Leader(((0, d),), dx=offset)), (x, y1, Leader(((0, -d),), dx=offset)),
               (x, y0, Label(text, SMALL, rotation=90, dx=offset + (GAP if offset >= 0 else -GAP), dy=d / 2,
                             attach=2 if offset >= 0 else 8))]
        out += [(x, y, Leader(((offset + math.copysign(GAP, offset), 0),), arrow=False, weight=1/2)) for y in (y0, y1)]
    return out


def around(point, radius, **kw):
    """A circle of `radius` (paper inches) centered on a point."""
    return (point[0], point[1], Circle(radius, **kw))


def circled(point, text, radius=CIRCLED, height=TEXT):
    """A circled number (or letter) centered on a point."""
    return [(point[0], point[1], Circle(radius)), (point[0], point[1], Label(text, height))]


def title(point, text, side="below", height=TITLE, gap=3/16, rotation=0, **kw):
    """A caption `gap` off a point (a drawing's extent's bottom center, say)."""
    return beside(point, side, Label(text, height, rotation=rotation, **kw), gap)


# ── line drawings ──────────────────────────────────────────────────────────

def crossed_box(width, height):
    """Lines drawing a box with both diagonals (lumber cut in section), from
    the anchor at its lower-left corner."""
    w, h = width, height
    return Lines((((0, 0), (w, 0)), ((w, 0), (w, h)), ((w, h), (0, h)), ((0, h), (0, 0)), ((0, 0), (w, h)), ((0, h), (w, 0))))


def box(width, height, weight=1, color=(0, 0, 0)):
    """A rectangle from its anchor at the top-left corner (a frame around a
    tool inset)."""
    w, h = width, height
    return Lines((((0, 0), (w, 0)), ((w, 0), (w, -h)), ((w, -h), (0, -h)), ((0, -h), (0, 0))), weight=weight, color=color)


def cross(size):
    """A + mark centered on its anchor, e.g. where a screw goes."""
    return Lines((((-size, 0), (size, 0)), ((0, -size), (0, size))))


def dashed_line(dx, dy, dash=0.06, gap=0.05, weight=1, color=(0, 0, 0)):
    """A dashed line from its anchor to (dx, dy), in dashes `dash` long with
    `gap` between them."""
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
    with `gap` between them."""
    sweep = math.radians(end - start)
    length = abs(sweep) * radius
    sign = 1 if sweep >= 0 else -1
    segments, s = [], 0
    while s < length:
        a0 = math.radians(start) + sign * s / radius
        a1 = math.radians(start) + sign * min(s + dash, length) / radius
        segments.append(((radius * math.cos(a0), radius * math.sin(a0)), (radius * math.cos(a1), radius * math.sin(a1))))
        s += dash + gap
    return Lines(tuple(segments), weight=weight, color=color)


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


# ── until every manual's notes are in its figure table (drawing-inch notes) ─

def vertical_dimension(length, text, text_offset=-1.9):
    """A dimension line up from its anchor, arrows at both ends, its text
    rotated alongside (to the left for a negative offset)."""
    return [Leader(((0, length),)), Leader(((0, -length),), dy=length),
            Label(text, 2, rotation=90, dx=text_offset, dy=length / 2, attach=8 if text_offset < 0 else 2)]


def legacy_crossed_box(width, height):
    """Leaders drawing a box with both diagonals (lumber cut in section), from
    the anchor at its lower-left corner."""
    return [Leader(((width, 0), (width, height), (0, height), (0, 0), (width, height)), arrow=False),
            Leader(((width, -height),), arrow=False, dy=height)]


def legacy_box(width, height, weight=1, color=(0, 0, 0)):
    """box(), at a legacy page's line weights (Lines draw at half a Leader's)."""
    return box(width, height, 2 * weight, color)
