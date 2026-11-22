"""Roof/roof_manual.md figures: the start/end shingle piles, and the roof
deck's two options on a half-roof."""

from build123d import Box, Pos, Rot

from model.common import CORNER, key
from model.dimensions import SHINGLE_WIDTH, START_END_PAIR
from model.notes import Label, beside, callout, title
from model.roof import TAIL_U, TIP_U, half_roof, roof_deck
from model.roofing import SHINGLE, start_shingles

from . import GRAY, Extent, extent, table
from .half_roof import HALF_ROOF_DRAWING

MD = "Roof/roof_manual.md"
STACK = 5  # pairs cut before the sequence restarts (one pile per side)
FAN = 1  # each piece set this far up and over from the one under it
PILES_GAP = 6  # between a side's start and end piles, and between the sides' rows
OPTIONS_GAP = 20  # between the two deck options


def start_end_figure():
    """The start/end pairs for each side of the roof, fanned out in their
    piles: starts right-aligned, ends left-aligned, first cut at the bottom."""
    parts, notes = [], []
    rows = []
    for side in (0, 1):
        y0 = (1 - side) * (SHINGLE_WIDTH + FAN * STACK + PILES_GAP)
        starts, ends = [], []
        for i, start in enumerate(start_shingles(side)[:STACK]):
            end = START_END_PAIR - start
            z = i * SHINGLE
            starts.append(Pos(-FAN * i - start, y0 + FAN * i, z) * Box(start, SHINGLE_WIDTH, SHINGLE, align=CORNER))
            ends.append(Pos(PILES_GAP + FAN * i, y0 + FAN * i, z) * Box(end, SHINGLE_WIDTH, SHINGLE, align=CORNER))
        parts += [(s, "hlr_thin") for s in starts + ends]
        rows.append((Extent(*starts), Extent(*ends)))
        notes.append(beside(Extent(*starts, *ends).right, "right", Label(f"Side {'AB'[side]}", 3/16), 1/2))
    whole = extent(parts)
    notes += [title(Extent(rows[1][0], rows[0][0]).bottom, "Start", gap=3/8), title(Extent(rows[1][1], rows[0][1]).bottom, "End", gap=3/8)]
    notes.append(title(whole.top, "Start/End Shingle Sets", "above", gap=3/8))
    return parts, [], notes


def panel_options_figure(scale):
    """A half-roof from above, eave at the bottom, with each deck option."""
    framing = [loc * c.shape(frozenset(), key(m)) for c, loc, m, _ in half_roof()[1]
               if getattr(c, "__name__", "") in ("rafter", "bored_rafter", "angle_plate", "ridge_board",
                                                 "eave_board", "cross_block")]
    eave = [loc * c.shape() for c, loc, m, _ in half_roof()[1] if getattr(c, "__name__", "") == "eave_board"]
    parts, notes = [], []
    y0 = 0
    for option in (2, 3):
        at = Pos(0, y0 + TIP_U - TAIL_U, 0) * Rot(Z=-90) * HALF_ROOF_DRAWING
        option_parts = [(at * s, "bare", (242, 242, 242)) for s in eave]
        clips = []
        for comp, loc in roof_deck(option):
            shape = at * loc * comp.shape()
            if comp.__name__.startswith("deck"):
                option_parts.append((shape, "outline", "plywood"))
            else:
                option_parts.append((shape, "outline", GRAY))
                clips.append(Extent(shape))
        option_parts += [(at * s, "outline") for s in framing]
        parts += option_parts
        ext = extent(option_parts)
        notes.append(title(ext.bottom, f"{option}-panel option", gap=1/2))
        # the clips at each seam: the topmost called out
        seams = {}
        for c in clips:
            seams.setdefault(round(c.center[0]), []).append(c)
        for seam in seams.values():
            top = max(seam, key=lambda c: c.y1)
            notes += callout(top.top, "Hurricane Clips", "above right", lead=3/4)
        y0 -= ext.height + OPTIONS_GAP + 0.8 / scale  # room for the title
    return parts, [], notes


def figures(scale=1/25):
    return table(MD, {"start_end_shingles": start_end_figure(), "panel_options": panel_options_figure(scale)})
