"""Pages of views (tilt-up/tilt-up.md, post-tilt-up/*.md,
Extract_Iron_Carts/Extract_instructions.md): the page's size, the tool
insets at its corners, and cameras given logically."""

import math

from build123d import Vector

from model.notes import Icon, Label, Leader, box

from . import Viewport

PAGE = (8.203125, 5.796875)  # inches (LayOut's A5 landscape)
MARGIN = 0.2  # the page's margin
INSET = (1.27, 1.14)  # a tool inset's box
INSET_GAP = 0.13  # between insets in a row or column
INSET_LINE = 4  # an inset's frame, relative to notes.LINE
ARROW = 4  # an arrow from an inset to the model, relative to notes.LINE
STRIKE = 10  # the red stroke through an inset
RED = (255, 0, 0)
GRAY = (109, 109, 109)

# The house's corners, as the manuals name them from the rear (rhs is the
# door side, X = 0; lhs X = PLATFORM_WIDTH; rear Y = 0, front Y +).
ISO_FROM = {
    "rear rhs": (1, 1, -1), "rear lhs": (-1, 1, -1), "front rhs": (1, -1, -1), "front lhs": (-1, -1, -1),
}
ISO_DOWN = math.sqrt(2)  # the standard isometric: the view direction's rise over its run... 35.26° down


def iso(corner):
    """The direction (toward the model) of an isometric view from above one
    of the house's corners."""
    x, y, _ = ISO_FROM[corner]
    return (x / math.sqrt(2), y / math.sqrt(2), -1 / ISO_DOWN)


def main_rect(top=MARGIN):
    """The page's main view: all of it inside the margin, from `top` down."""
    w, h = PAGE
    return (MARGIN, top, w - 2 * MARGIN, h - top - MARGIN)


LOWER_RECT = main_rect(1.5)  # the main view under a row of insets


def inset_rect(corner, k=0, row=0):
    """The k-th inset's rect (x, y, w, h) along the page's edge from one of
    its corners ("top left", "top right", "bottom left", "bottom right",
    or "middle left"/"middle right", halfway down), in the row-th row in
    from the edge."""
    w, h = PAGE
    iw, ih = INSET
    x = MARGIN + k * (iw + INSET_GAP) if "left" in corner else w - MARGIN - iw - k * (iw + INSET_GAP)
    if "top" in corner:
        y = MARGIN + row * (ih + INSET_GAP)
    elif "bottom" in corner:
        y = h - MARGIN - ih - row * (ih + INSET_GAP)
    else:
        y = (h - ih) / 2
    return (x, y, iw, ih)


def inset_edge(rect, side):
    """The middle of a side ("left", "right", "top", "bottom") of a rect, in
    page coordinates: where an arrow from an inset starts."""
    x, y, w, h = rect
    return {"left": (x, y + h / 2), "right": (x + w, y + h / 2), "top": (x + w / 2, y), "bottom": (x + w / 2, y + h)}[side]


def frame(rect, weight=INSET_LINE, color=(0, 0, 0)):
    """A page note: a frame around a rect."""
    x, y, w, h = rect
    return (x, y, box(w, h, weight=weight, color=color))


def inset(name, corner, k=0, row=0, count=None, struck=False):
    """Page notes for a tool inset: the icon `name` framed in the k-th inset
    at a corner, with a count ("x3") at its lower right, struck through in
    red for "not like this"."""
    rect = inset_rect(corner, k, row)
    x, y, w, h = rect
    out = [frame(rect), (x + w / 2, y + h / 2, Icon(name, w * 0.9, h * 0.9))]
    if count:
        out.append((x + w - 0.08, y + h - 0.08, Label(count, 0.11, attach=9)))
    if struck:
        out.append((x, y + h, Leader(((x + w, y),), arrow=False, weight=STRIKE, color=RED, absolute=True)))
    return out


def arrow_to(point, rect, side, curve=0.25, weight=ARROW, color=(0, 0, 0), dash=None, head=1):
    """A viewport note: an arrow from the `side` of an inset's rect to a
    point (x, y, z) of the model, bowed by `curve`."""
    return (*point, Leader((inset_edge(rect, side),), absolute=True, curve=curve, weight=weight, color=color, dash=dash, head=head))


def pointer_to(point, page_point, weight=ARROW, color=(0, 0, 0), curve=0):
    """A viewport note: a straight arrow from a page point to a model point."""
    return (*point, Leader((page_point,), absolute=True, weight=weight, color=color, curve=curve))


def arrow_between(a, b, weight=ARROW, color=(0, 0, 0)):
    """A page note: an arrow from page point a to page point b."""
    return (b[0], b[1], Leader(((a[0] - b[0], -(a[1] - b[1])),), weight=weight, color=color))


def view(rect, corner, parts, fit=None, margin=0.05, style="hlr", notes=(), highlights=()):
    """A parallel isometric view from above one of the house's corners,
    framed on `fit` (shapes; or all the parts)."""
    return Viewport(rect, direction=iso(corner), parts=[(s, style) if not isinstance(s, tuple) else s for s in parts],
                    fit=fit, margin=margin, notes=list(notes), highlights=list(highlights))


def perspective(rect, eye, target, parts, fov=35, up=(0, 0, 1), style="hlr", notes=(), highlights=(), offset=(0, 0)):
    """A perspective view from `eye` toward `target` (fov: degrees, vertical)."""
    return Viewport(rect, eye=tuple(eye), target=tuple(target), up=tuple(up), fov=fov,
                    parts=[(s, style) if not isinstance(s, tuple) else s for s in parts], notes=list(notes),
                    highlights=list(highlights), offset=offset)


def axes_on_page(corner):
    """The page's right and up directions as model vectors, for an isometric
    view from a corner: a model vector v lands on the page as
    (v . right, v . up)."""
    d = Vector(*iso(corner))
    right = d.cross(Vector(0, 0, 1)).normalized()
    up = right.cross(d).normalized()
    return right, up


def on_page(v, corner):
    """A model vector's direction on the page (x right, y up, unit length)."""
    right, up = axes_on_page(corner)
    v = Vector(*v)
    x, y = v.dot(right), v.dot(up)
    n = math.hypot(x, y) or 1
    return x / n, y / n


def move_arrow(a, b, corner, length=1, weight=ARROW, at=1):
    """A viewport note: an arrow `length` page inches long for a move from
    model point a to b, its head `at` (a fraction) of the way along."""
    ux, uy = on_page(tuple(bi - ai for ai, bi in zip(a, b)), corner)
    head = tuple(ai + (bi - ai) * at for ai, bi in zip(a, b))
    return (*head, Leader(((-ux * length, -uy * length),), weight=weight))


def up_arrow(point, length=1, weight=ARROW):
    """A viewport note: an arrow pointing straight up the page at a point."""
    return (*point, Leader(((0, -length),), weight=weight))


def center_of(shapes):
    """The center of some shapes' bounding box, as (x, y, z)."""
    bbs = [s.bounding_box() for s in shapes]
    lo = Vector(min(b.min.X for b in bbs), min(b.min.Y for b in bbs), min(b.min.Z for b in bbs))
    hi = Vector(max(b.max.X for b in bbs), max(b.max.Y for b in bbs), max(b.max.Z for b in bbs))
    return tuple((lo + hi) / 2)
