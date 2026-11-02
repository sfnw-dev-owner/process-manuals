"""Insets drawn from the model instead of clipart: a tool or fastener the
model has (a screw, a clamp, a nail) or a small made-up scene ("like
this", and struck through, "not like this": two blocks flush, or not), in
a parallel view fitted in an inset's frame at a page corner, with a count
or a red strike like a clipart inset (pages.inset). The scenes are plain
boxes a few inches big, in the house's inch units."""

from build123d import Align, Box, Pos

from model import post_tilt_up as P
from model.common import driven
from model.lumber import thickness, width
from model.notes import Label, Leader

from . import Viewport
from .pages import RED, STRIKE, frame, inset_rect, iso

CORNER = (Align.MIN, Align.MIN, Align.MIN)
VIEW = iso("front lhs")  # the scenes' view, from over the house's front lhs corner like the pages
STUD, DEEP = thickness("2x4"), width("2x4")


def part_inset(shapes, corner, k=0, row=0, count=None, struck=False, direction=VIEW, fit=None, margin=0.15):
    """(viewport, page notes): the shapes in a parallel view along
    `direction`, fitted in the k-th inset at a page corner (on `fit`, or
    all of them, with `margin` of the frame around), framed, with a count
    at the lower right and struck through in red for "not like this"."""
    rect = inset_rect(corner, k, row)
    x, y, w, h = rect
    vp = Viewport(rect, direction=direction, parts=[(s, "hlr") for s in shapes], fit=fit, margin=margin)
    notes = [frame(rect)]
    if count:
        notes.append((x + w - 0.08, y + h - 0.08, Label(count, 0.11, attach=9)))
    if struck:
        notes.append((x, y + h, Leader(((x + w, y),), arrow=False, weight=STRIKE, color=RED, absolute=True)))
    return vp, notes


def fastener(component, corner, k=0, row=0, count=None, struck=False):
    """A fastener the model drives (post_tilt_up.screw_long, screw_short,
    hex_screw, ...) stood up in an inset, seen from the side."""
    return part_inset([component.shape()], corner, k, row, count, struck, direction=(0, 1, 0), margin=0.2)


# ── the scenes ─────────────────────────────────────────────────────────────

def stacked(gap=0, step=0, length=14):
    """A 2x4 block lying on another, `gap` above it, its face `step` proud:
    tight and flush, or not."""
    return [Box(length, DEEP, STUD, align=CORNER), Pos(0, step, STUD + gap) * Box(length, DEEP, STUD, align=CORNER)]


def centered(offset=0, long=24, short=14):
    """A short block centered on a long one, or `offset` off center."""
    return [Box(long, DEEP, STUD, align=CORNER), Pos((long - short) / 2 + offset, 0, STUD) * Box(short, DEEP, STUD, align=CORNER)]


def end_to_end(step=0, length=10):
    """Two boards end to end, their faces flush, or the second one `step` proud."""
    return [Box(length, STUD, DEEP, align=CORNER), Pos(length, step, 0) * Box(length, STUD, DEEP, align=CORNER)]


def corner(offset=0, length=8):
    """Two studs meeting at a corner, the end one's face flush with the side
    one's, or `offset` proud."""
    return [Box(length, STUD, DEEP, align=CORNER), Pos(-offset, STUD, 0) * Box(STUD, length, DEEP, align=CORNER)]


BAY = 16  # a stud bay, on center
BAY_SCREWS = 4  # screws down through the bottom plate in each bay


def stud_bay_screws():
    """A stud bay's bottom plate on the deck with its BAY_SCREWS screws,
    staggered along the bay (frame-completion.md "Secure Walls")."""
    deck = Pos(-3, -3, -3/4) * Box(BAY + STUD + 6, DEEP + 6, 3/4, align=CORNER)
    plate = Box(BAY + STUD, DEEP, STUD, align=CORNER)
    studs = [Pos(x, 0, STUD) * Box(STUD, DEEP, 12, align=CORNER) for x in (0, BAY)]
    screws = [driven((STUD + (BAY - STUD) * (i + 1) / (BAY_SCREWS + 1), DEEP * (0.3 if i % 2 else 0.7), STUD), (0, 0, -1)) * P.screw_long.shape()
              for i in range(BAY_SCREWS)]
    return [deck, plate, *studs, *screws]
