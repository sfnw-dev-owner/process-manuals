"""Interior_Trim/vent_cap_install.md figure: a support block with its screws
preset (isometric, enlarged), and the vent cap's two pieces from below with
their screw holes."""

from build123d import Pos, scale

from model.interior_roof import (
    VENT_CAP_REAR, VENT_CAP_SEAM, VENT_CAP_VIEW, vent_cap, vent_cap_block, vent_cap_long, vent_cap_short,
)

from . import Figure, camera, figure_names, placed_notes

MD = "Interior_Trim/vent_cap_install.md"
BLOCK_SCALE = 4  # the block is drawn enlarged
BLOCK_AT = (52.76, 152.54)  # the enlarged block's lower-left, in the drawing


def figures():
    iso = scale(camera((1, -1, 1)) * vent_cap_block.shape(), by=BLOCK_SCALE)
    bb = iso.bounding_box()
    block = Pos(BLOCK_AT[0] - bb.min.X, BLOCK_AT[1] - bb.min.Y, 0) * iso
    # the pieces where the vent cap has them, the short one moved down under the long one
    comp = {c: loc for c, loc, _, _ in vent_cap()[1] if c in (vent_cap_long, vent_cap_short)}
    long_ = VENT_CAP_VIEW * comp[vent_cap_long] * vent_cap_long.shape()
    short = Pos(93.4 - 42 - (VENT_CAP_SEAM - VENT_CAP_REAR), 64.09 - 100, 0) * VENT_CAP_VIEW * comp[vent_cap_short] * vent_cap_short.shape()
    parts = [(block, "hlr_thin"), (long_, "outline"), (short, "outline")]
    shown = {"manual:interior_trim", "manual:interior_trim:vent_cap"}
    fig_name, = figure_names(MD)
    return [Figure(MD, fig_name, parts, placed_notes(VENT_CAP_VIEW, vent_cap, shown))]
