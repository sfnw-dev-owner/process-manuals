"""Roof/roof_manual.md figures."""

from build123d import Box, Pos

from model.common import CORNER
from model.dimensions import SHINGLE_LENGTH, SHINGLE_WIDTH, START_END_PAIR
from model.roof import SHINGLE, start_shingles

from . import Figure, figure_names, title

MD = "Roof/roof_manual.md"
STACK = 5  # pairs cut before the sequence restarts (one pile per side)
FAN = 1  # each piece set this far up and over from the one under it


def start_end_figure(fig_name):
    """The start/end pairs for each side of the roof, fanned out in their
    piles: starts right-aligned, ends left-aligned, first cut at the bottom."""
    parts = []
    for side, y0 in ((0, 22), (1, 0)):
        for i, start in enumerate(start_shingles(side)[:STACK]):
            end = START_END_PAIR - start
            z = i * SHINGLE
            parts.append((Pos(36 - FAN * i - start, y0 + FAN * i, z) * Box(start, SHINGLE_WIDTH, SHINGLE, align=CORNER), "hlr_thin"))
            parts.append((Pos(42 + FAN * i, y0 + FAN * i, z) * Box(end, SHINGLE_WIDTH, SHINGLE, align=CORNER), "hlr_thin"))
    notes = [title("Start/End Shingle Sets", 26, 52), title("Side A", 88, 34), title("Side B", 88, 12),
             title("Start", 14, -4), title("End", 52, -4)]
    return Figure(MD, fig_name, parts, notes)


def panel_options_figure(fig_name):
    """A half-roof from above, eave at the bottom, with each deck option."""
    from build123d import Rot
    from model.common import key
    from model.notes import Label, Leader
    from model.roof import HALF_ROOF_DRAWING, TAIL_U, TIP_U, half_roof, roof_deck
    from . import GRAY
    framing = [loc * c.shape(frozenset(), key(m)) for c, loc, m, _ in half_roof()[1]
               if getattr(c, "__name__", "") in ("rafter", "bored_rafter", "angle_plate", "ridge_board",
                                                 "eave_board", "cross_block")]
    eave = [loc * c.shape() for c, loc, m, _ in half_roof()[1] if getattr(c, "__name__", "") == "eave_board"]
    parts, notes = [], []
    for option, y0 in ((2, 0), (3, -100)):
        at = Pos(0, y0 + 4.54 + TIP_U - TAIL_U, 0) * Rot(Z=-90) * HALF_ROOF_DRAWING
        parts += [(at * s, "bare", (242, 242, 242)) for s in eave]
        for comp, loc in roof_deck(option):
            fill = "plywood" if comp.__name__.startswith("deck") else GRAY
            parts.append((at * loc * comp.shape(), "outline", fill))
        parts += [(at * s, "outline") for s in framing]
    notes += [title("2-panel option", 60, -10), title("3-panel option", 60, -120),
              (125.94, -34.23, Label("Hurricane Clips", 3, attach=1)),
              (30, -34, Label("Hurricane Clips", 3, attach=1)),
              (114.75, -47.25, Leader(((7.25, 11.5), (10.25, 11.5)))),
              (18.75, -47.25, Leader(((7.25, 11.5), (10.25, 11.5))))]
    return Figure(MD, fig_name, parts, notes)


def figures():
    figs = figure_names(MD)
    return [start_end_figure(figs[0]), panel_options_figure(figs[1])]
