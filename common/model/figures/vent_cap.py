"""Interior_Trim/vent_cap_install.md figure: a support block with its screws
preset (isometric, enlarged), and the vent cap's two pieces from below with
their screw holes dimensioned."""

from build123d import Pos

from model.dimensions import VENT_CAP_LENGTH, VENT_CAP_WIDTH
from model.interior_roof import (
    VENT_CAP_END_HOLES, VENT_CAP_HOLE_INSET, VENT_CAP_SEAM_HOLES, VENT_CAP_SHORT, vent_cap_block, vent_cap_long,
    vent_cap_short,
)
from model.lumber import thickness, width
from model.notes import Label, aimed, beside, dimension, line, title

from . import Extent, camera, enlarged, table
from .interior_panels import FLAT_VIEW

MD = "Interior_Trim/vent_cap_install.md"
PAPER_NOTES = True
BLOCK_SCALE = 4  # the block is drawn enlarged
PIECES_GAP = 40  # the short piece drawn this far below the long one
BLOCK_GAP = 24  # the block this far above the long piece
CENTERLINE_PAST = 3  # a hole's centerlines run this far past the piece's edges


def figures(scale=1/25):
    # The pieces seen from below, the rear to the left: the long one with its
    # rear end at the origin, the short one under it with its front end under
    # the long one's seam end.
    long_ = FLAT_VIEW * vent_cap_long.shape()
    short = Pos(VENT_CAP_LENGTH - VENT_CAP_SHORT, -VENT_CAP_WIDTH - PIECES_GAP, 0) * FLAT_VIEW * vent_cap_short.shape()
    long_ext, short_ext = Extent(long_), Extent(short)
    parts = [(long_, "outline"), (short, "outline")]
    notes = []
    rows = (VENT_CAP_HOLE_INSET, VENT_CAP_WIDTH - VENT_CAP_HOLE_INSET)  # the holes' rows, across a piece
    for ext, along in ((long_ext, (VENT_CAP_END_HOLES, VENT_CAP_LENGTH / 2, VENT_CAP_LENGTH - VENT_CAP_SEAM_HOLES)),
                       (short_ext, (VENT_CAP_SEAM_HOLES, VENT_CAP_SHORT - VENT_CAP_END_HOLES))):
        for y in rows:  # (drawing y = across the piece)
            notes.append(line((ext.x0 - CENTERLINE_PAST, ext.y0 + y), (ext.x1 + CENTERLINE_PAST, ext.y0 + y), scale))
        for x in along:
            notes.append(line((ext.x0 + x, ext.y0 - CENTERLINE_PAST), (ext.x0 + x, ext.y1 + CENTERLINE_PAST), scale))
    # the holes along each piece, from its ends (the middle one from the rear end)
    top = long_ext.y1
    notes += dimension((long_ext.x0, top), (long_ext.x0 + VENT_CAP_END_HOLES, top), scale, offset=3/8)
    notes += dimension((long_ext.x0, top), (long_ext.x0 + VENT_CAP_LENGTH / 2, top), scale, offset=5/8)
    notes += dimension((long_ext.x1 - VENT_CAP_SEAM_HOLES, top), (long_ext.x1, top), scale, offset=3/8)
    top = short_ext.y1
    notes += dimension((short_ext.x0, top), (short_ext.x0 + VENT_CAP_SEAM_HOLES, top), scale, offset=3/8)
    notes += dimension((short_ext.x1 - VENT_CAP_END_HOLES, top), (short_ext.x1, top), scale, offset=3/8)
    # and across, from each long edge (one at each end of the short piece)
    notes += dimension((short_ext.x1, short_ext.y0), (short_ext.x1, short_ext.y0 + rows[0]), scale, offset=3/8)
    notes += dimension((short_ext.x0, short_ext.y0 + rows[1]), (short_ext.x0, short_ext.y1), scale, offset=-3/8)
    for ext, (a, b) in ((long_ext, ("REAR", "SEAM")), (short_ext, ("SEAM", "FRONT"))):
        notes += [beside(ext.bottom_left, "below", Label(a), 3/8), beside(ext.bottom_right, "below", Label(b), 3/8)]
    # the block, enlarged, above: two screws preset in its middle
    block, to_drawing = enlarged(vent_cap_block.shape(), camera((1, -1, 1)), BLOCK_SCALE,
                                 (long_ext.x0 + 12, long_ext.y1 + BLOCK_GAP + 10))
    parts.append((block, "hlr_thin"))
    bx, by, bz = thickness("2x4") * 0 + vent_cap_block.shape().bounding_box().size.X / 2, width("2x4") / 2, thickness("2x4")
    for dx in (-1, 1):
        notes.append(aimed(to_drawing((bx + dx, by, bz)), "Screw", "above"))
    notes.append(beside(Extent(block).right, "right", Label("Block preparation", 3/16), 1/2))
    notes.append(title(short_ext.bottom, "Vent Cap Details", gap=3/4))
    return table(MD, {"vent_cap": (parts, [], notes)})
