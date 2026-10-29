"""The front door: a prehung steel door converted to an ADA threshold, and
what goes into the doorway with it.

Per floor_door/door_manual.md and images/door_preparation.dxf.

The door swings in. The door assembly's frame: X across the doorway, from
the outside face of the hinge-side jamb (on the left, seen from inside); Y
through the wall, from the inside edge of the jambs outward (their outside
edge is flush with the siding); Z up from the bottom of the jamb legs.
"""

from build123d import Align, Box, Cylinder, Location, Pos, Rectangle, Rot, SlotCenterToCenter, Sphere, extrude

from .dimensions import PLATFORM_LENGTH
from .common import CORNER, component
from .flooring import FLOORING, INTERIOR_PLYWOOD
from .walls import DOOR_HEADER_Z, DOOR_OPENING, DOOR_X, SIDING, WALL_DEPTH, WRAP

# Frame (door_preparation.dxf, 2_Door and 5_Strike Plate).
JAMB = 3/4  # thickness
JAMB_DEPTH = 4 + 1/2  # across the wall: from the siding's face to 1/8" past the wall panels
STOP = (1 + 1/2, 1/2)  # the door-stop: width, and how far it stands off the jamb
STOP_FROM_OUTSIDE = 1  # from the jamb's outside edge
STOP_Y = JAMB_DEPTH - STOP_FROM_OUTSIDE - STOP[0]  # its inside edge, which the door closes against
FRAME_WIDTH = 37 + 3/4  # outside of the jambs; fits the 38" rough opening
FRAME_CUT = 80 + 3/4  # the legs cut this far down from the outside top of the frame
BRICKMOLD = (1, 1)  # width (as drawn), thickness
JAMB_HEIGHT = FRAME_CUT - BRICKMOLD[0]  # the brickmold stands 1" above the head jamb

# Door (door_preparation.dxf 2_Door).
SLAB = (36, 1 + 3/4, 78 + 1/2)
SLAB_GAP = 1/8  # between the door and the jambs, "about 1/8" after shimming"
HINGE = (1/2, 1/2, 4)  # a 4" hinge's knuckle, as seen from inside
HINGE_LEAF = 2  # across the jamb's face, from 1/2" inside its inside edge
HINGE_Z = [11 + 9/16, 38 + 7/16, 64 + 1/2]  # bottoms, from the bottom of the legs
KNOB = (33, 42)  # center: from the slab's hinge edge, and up from the bottom of the legs
KNOB_ROSE = 2  # radius

# ADA threshold: "pre-trimmed ... exactly 36" long", "1/4" thick".
THRESHOLD = (36, 3 + 1/2, 1/4)  # length, depth (not given in the manuals), thickness

# Strike plate, on the latch jamb (door_preparation.dxf 5_Strike Plate).
STRIKE_PLATE = (1 + 5/16, 1 + 1/4)  # across the jamb (from its inside edge), tall
LATCH_HOLE = (3/4, 1)  # wide, tall
LATCH_HOLE_FROM_INSIDE = 25/32  # center

# Screws through the frame into the framing, "pre-drilled" (3.1_ScrewLocs):
# on the hinge side 1" above each hinge, on the latch side 17" up and 10"
# down from the top; 1" above and below the latch at the strike plate, 1/2"
# from the jamb's inside edge.
HINGE_SCREW_ABOVE = 1
LATCH_SCREWS_Z = [17, JAMB_HEIGHT - 10]
STRIKE_SCREWS = 1  # above and below the latch hole's center
SCREW_FROM_EDGE = 1/2

# In the doorway: flexible flashing ("54" strip") across the bottom and
# about 8" up each side, half of it outside the building; shims; a plywood
# filler above the head jamb ("Precut plywood filler 4 1/2" x 37 1/2"").
FLASHING = (54, 4, 1/32)  # length, width (as drawn), thickness
FLASHING_UP = (FLASHING[0] - DOOR_OPENING) / 2
SHIM = (1 + 1/2, 1/8)  # wide, and thick where it's squeezed in the gap
TOP_SHIMS_IN = 9  # "8-10" in from each side"
FILLER = (37 + 1/2, 4 + 1/2, 3/4)

# Where the assembly goes in the front wall (the wall's frame, see walls.py):
# centered in the rough opening, the jambs' inside edge flush with the wall
# panels, standing on the flooring over the flashing.
FRAME_GAP = (DOOR_OPENING - FRAME_WIDTH) / 2
FRAMING_Y = JAMB_DEPTH - WRAP - SIDING - WALL_DEPTH  # the framing's inside face
FRAME_BOTTOM = FLOORING + FLASHING[2]  # above the deck


def latch_x():
    return FRAME_WIDTH - JAMB


@component
def door_assembly():
    """The prehung door as installed, with its shims, filler and flashing."""
    top = JAMB_HEIGHT
    children = [
        (jamb_leg, Location(), [], ''),
        (jamb_leg, Pos(FRAME_WIDTH, 0, 0), ['mirror'], ''),
        (head_jamb, Pos(0, 0, top - JAMB), [], ''),
        (brickmold, Location(), [], ''),
        (door_slab, Pos(JAMB + SLAB_GAP, STOP_Y - SLAB[1], THRESHOLD[2] + SLAB_GAP), [], ''),
        *[(hinge, Pos(0, 0, z), [], '') for z in HINGE_Z],
        (threshold, Pos((FRAME_WIDTH - THRESHOLD[0]) / 2, 0, 0), [], ''),
        (strike_plate, Pos(latch_x(), 0, KNOB[1] - STRIKE_PLATE[1] / 2), [], ''),
        # Shims in the gap between the jambs and the framing, trimmed flush
        # with the wall panels: above each hinge, high and low on the latch
        # side and either side of the latch, and over the head jamb.
        *[(shim, Pos(-SHIM[1], 0, z + HINGE[2] + HINGE_SCREW_ABOVE - SHIM[0] / 2), [], 'Shims') for z in HINGE_Z],
        *[(shim, Pos(FRAME_WIDTH, 0, z - SHIM[0] / 2), [], 'Shims')
          for z in LATCH_SCREWS_Z + [KNOB[1] - STRIKE_SCREWS, KNOB[1] + STRIKE_SCREWS]],
        *[(top_shim, Pos(x - SHIM[0] / 2, 0, top), [], 'Shims') for x in (TOP_SHIMS_IN, FRAME_WIDTH - TOP_SHIMS_IN)],
        (filler, Pos((FRAME_WIDTH - FILLER[0]) / 2, 0, top + top_gap()), [], ''),
        (flashing, Pos(-FRAME_GAP, JAMB_DEPTH - FLASHING[1] / 2, -FLASHING[2]), [], ''),
    ]
    return [], children


def top_gap():
    """Above the head jamb, under the plywood filler, to the header."""
    return DOOR_HEADER_Z[0] - FILLER[2] - FRAME_BOTTOM - JAMB_HEIGHT


def jamb_profile():
    """The jamb in section, X across it (0 = its back, against the framing),
    Y across the wall: the jamb, and the stop standing off its face."""
    return (Rectangle(JAMB, JAMB_DEPTH, align=CORNER)
            + Pos(JAMB, STOP_Y) * Rectangle(STOP[1], STOP[0], align=CORNER))


@component
def jamb_leg():
    return [extrude(jamb_profile(), JAMB_HEIGHT)], []


@component
def head_jamb():
    """Across the top, between the legs."""
    length = FRAME_WIDTH - 2 * JAMB
    return [Pos(JAMB, 0, JAMB) * Rot(Y=90) * extrude(Rot(Z=0) * Rectangle(JAMB, JAMB_DEPTH, align=CORNER), length)
            + Pos(JAMB, STOP_Y, 0) * Box(length, STOP[0], STOP[1], align=(Align.MIN, Align.MIN, Align.MAX))], []


@component
def brickmold():
    """Around the outside of the frame, against the siding."""
    w, t = BRICKMOLD
    y = JAMB_DEPTH  # the siding's face
    side = Box(w, t, FRAME_CUT, align=CORNER)
    head = Box(FRAME_WIDTH + 2 * w, t, w, align=CORNER)
    return [Pos(-w, y, 0) * side, Pos(FRAME_WIDTH, y, 0) * side, Pos(-w, y, FRAME_CUT - w) * head], []


@component
def door_slab():
    w, t, h = SLAB
    slab = Box(w, t, h, align=CORNER)
    rose = Pos(KNOB[0], 0, KNOB[1] - THRESHOLD[2] - SLAB_GAP) * Rot(X=90) * Cylinder(
        KNOB_ROSE, 1/8, align=(Align.CENTER, Align.CENTER, Align.MIN))  # on the inside face
    return [slab, rose], [(door_outside, Location(), [], 'Door Outside')]


# The slab's outside, as SketchUp's door had it: six panels and the knob.
# (The door manual's drawing had the slab plain, so it hides this.)
PANEL_STILE, PANEL_RAIL, PANEL_BOTTOM_RAIL = 5, 5, 9  # stiles (and the center stile), the top and lock rails, the bottom rail
PANEL_ROWS = (10, 24)  # the top and middle panels' heights; the bottom panels take the rest
PANEL_LIP = 1/4  # the panel moulding, proud of the face


@component
def door_outside():
    w, t, h = SLAB
    pw = (w - 3 * PANEL_STILE) / 2
    cols = [(PANEL_STILE, pw), (2 * PANEL_STILE + pw, pw)]
    top, mid = PANEL_ROWS
    bottom = h - PANEL_BOTTOM_RAIL - 3 * PANEL_RAIL - top - mid
    rows = [(h - PANEL_RAIL - top, top), (h - 2 * PANEL_RAIL - top - mid, mid), (PANEL_BOTTOM_RAIL, bottom)]
    panels = [Pos(x, t, z) * Box(dx, PANEL_LIP, dz, align=CORNER) for x, dx in cols for z, dz in rows]
    knob_z = KNOB[1] - THRESHOLD[2] - SLAB_GAP
    knob = [Pos(KNOB[0], t, knob_z) * Rot(X=-90) * Cylinder(KNOB_ROSE, 1/8, align=(Align.CENTER, Align.CENTER, Align.MIN)),
            Pos(KNOB[0], t + 1/8, knob_z) * Rot(X=-90) * Cylinder(KNOB_ROSE / 2, 2, align=(Align.CENTER, Align.CENTER, Align.MIN)),
            Pos(KNOB[0], t + 2 + 1/8, knob_z) * Sphere(1.1)]
    return panels + knob, []


@component
def hinge():
    """The knuckle, proud of the jamb's inside edge, and the leaf on the
    jamb's face."""
    w, d, h = HINGE
    knuckle = Pos(JAMB - w, -d, 0) * Box(w, d, h, align=CORNER)
    leaf = Pos(JAMB, -1/2, 0) * Box(1/16, HINGE_LEAF, h, align=CORNER)
    return [knuckle, leaf], []


@component
def threshold():
    return [Box(*THRESHOLD, align=CORNER)], []


@component
def strike_plate():
    """On the latch jamb's face, its latch hole through it."""
    w, h = STRIKE_PLATE
    plate = Pos(-1/16, 0, 0) * Box(1/16, w, h, align=CORNER)
    slot = (Pos(0, LATCH_HOLE_FROM_INSIDE, h / 2) * Rot(Y=90)
            * SlotCenterToCenter(LATCH_HOLE[1] - LATCH_HOLE[0], LATCH_HOLE[0]))
    return [plate - extrude(Pos(-1/8, 0, 0) * slot, 1/4)], []


@component
def shim():
    """A shim in the gap beside a jamb, trimmed flush with the wall panels."""
    return [Box(SHIM[1], JAMB_DEPTH, SHIM[0], align=CORNER)], []


@component
def top_shim():
    return [Box(SHIM[0], JAMB_DEPTH, top_gap(), align=CORNER)], []


@component
def filler():
    length, depth, t = FILLER
    return [Box(length, depth, t, align=CORNER)], []


@component
def flashing():
    """Across the bottom of the rough opening, under the frame, and up each
    side (as laid, before its outer half is folded down)."""
    length, wide, t = FLASHING
    bottom = Box(DOOR_OPENING, wide, t, align=CORNER)
    side = Box(t, wide, FLASHING_UP, align=CORNER)
    return [bottom, Pos(0, 0, t) * side, Pos(DOOR_OPENING - t, 0, t) * side], []


# Where the house puts the door assembly: in the front wall's doorway, in
# the house's frame with the deck's top at Z = 0.
DOOR_IN_HOUSE = Pos(WALL_DEPTH + DOOR_X + FRAME_GAP, PLATFORM_LENGTH - WALL_DEPTH - FRAMING_Y, FRAME_BOTTOM)


# ── where the frame is screwed to the framing ──────────────────────────────

# Pencil marks for the frame's screws, between the jamb's inside edge and the stop.
SCREW_Y = 1 + 1/2
HINGE_MARKS = [(0, SCREW_Y, z + HINGE[2] + HINGE_SCREW_ABOVE) for z in HINGE_Z]  # on the hinge jamb's face
LATCH_MARKS = [(FRAME_WIDTH, SCREW_Y, z) for z in LATCH_SCREWS_Z]  # on the latch jamb's
LATCH_Z = KNOB[1]
STRIKE_MARKS = [(FRAME_WIDTH, SCREW_FROM_EDGE, LATCH_Z + dz) for dz in (-STRIKE_SCREWS, STRIKE_SCREWS)]  # beside the latch
