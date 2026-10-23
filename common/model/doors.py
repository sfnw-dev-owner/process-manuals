"""The front door: a prehung steel door converted to an ADA threshold, and
what goes into the doorway with it.

Per floor_door/door_manual.md and images/door_preparation.dxf.

The door swings in. The door assembly's frame: X across the doorway, from
the outside face of the hinge-side jamb (on the left, seen from inside); Y
through the wall, from the inside edge of the jambs outward (their outside
edge is flush with the siding); Z up from the bottom of the jamb legs.
"""

from .common import *
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
        *door_manual(),
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


# ── floor_door/door_manual.md figures ──────────────────────────────────────
# Each figure looks at the assembly one way (View). Annotations are tagged
# "manual:door:<figure>", figures named after door_preparation.dxf's layers:
# door (2_Door), threshold (3_Threshold), screws (3.1_ScrewLocs), shims
# (4_Shimming), strike (5_Strike Plate); they're placed from the figure's
# drawing coordinates.

from .notes import Circle, Icon, Label, Leader, crossed_box, vertical_dimension  # noqa: E402


class View:
    """Looking at the assembly from `direction`, `up` up the page, drawn at
    `scale`, with the assembly's `point` at `at` in the drawing."""

    def __init__(self, direction, up, scale, point, at):
        z = Vector(*direction).normalized()
        x = Vector(*up).cross(z).normalized()
        self.camera = Location(Plane((0, 0, 0), x_dir=x, z_dir=z)).inverse()
        self.scale = scale
        p = (self.camera * Pos(*point)).position
        self.offset = (at[0] - scale * p.X, at[1] - scale * p.Y)

    def xy(self, point):
        """Where an assembly point is in the drawing."""
        p = (self.camera * Pos(*point)).position
        return self.offset[0] + self.scale * p.X, self.offset[1] + self.scale * p.Y

    def at(self, x, y):
        """The assembly point drawn at (x, y) (in the drawing's plane)."""
        return self.camera.inverse() * Pos((x - self.offset[0]) / self.scale, (y - self.offset[1]) / self.scale, 0)


FROM_INSIDE, UP = (0, -1, 0), (0, 0, 1)
LATCH_Z = KNOB[1]
VIEWS = {
    "door": View(FROM_INSIDE, UP, 1, (0, 0, 0), (0.12, 16)),
    # A plan section at the floor, looking down, the inside at the top.
    "threshold": View((0, 0, 1), (0, -1, 0), 1, (FRAME_WIDTH + FRAME_GAP, FRAMING_Y, 0), (0.17, -2.64)),
    # The legs' faces, seen from the doorway; and a 3x detail at the top hinge.
    "screws": View((1, 0, 0), UP, 1, (0, 0, 0), (-5.56, 8.4)),
    "screws_latch": View((-1, 0, 0), UP, 1, (FRAME_WIDTH, 0, 0), (45.12, 8.15)),
    "screws_detail": View((1, 0, 0), UP, 3, (0, -1/2, HINGE_Z[2]), (13, 69)),
    "shims": View(FROM_INSIDE, UP, 1, (0, 0, 0), (-5.44, 8.4)),
    # 4x: the latch jamb in section at the latch, from above (the outside on
    # the left, the wall running up the page); and its face, from the doorway.
    "strike": View((0, 0, 1), (1, 0, 0), 4, (FRAME_WIDTH, JAMB_DEPTH, LATCH_Z), (10, 45)),
    "strike_face": View((-1, 0, 0), UP, 4, (FRAME_WIDTH, JAMB_DEPTH, LATCH_Z), (10, 21.56)),
}
DETAIL = (16, 77, 12.21)  # screws: the detail's circle, center and radius
STRIKE_FACE_WINDOW = (LATCH_Z - 3.2, LATCH_Z + 3)  # the strike face view's height

# Pencil marks for the frame's screws, between the jamb's inside edge and the stop.
SCREW_Y = 1 + 1/2
HINGE_MARKS = [(0, SCREW_Y, z + HINGE[2] + HINGE_SCREW_ABOVE) for z in HINGE_Z]
LATCH_MARKS = [(FRAME_WIDTH, SCREW_Y, z) for z in LATCH_SCREWS_Z]


def door_manual():
    def steps(name):
        return f"manual:door:{name}"

    def view_at(name):
        return VIEWS[name].at

    def mark(view, point, size=1/2):
        """A pencil mark at an assembly point as `view` shows it."""
        return [(n, at(*VIEWS[view].xy(point)), [], t) for n in mark_cross(size)]

    out = []
    # 2_Door
    t, at = steps('door'), view_at('door')
    out += [
        (Icon('Screw', 3, 7.2), at(0.2, 100.84), [], t),
        (Icon('Screw', 3, 7.2), at(37.82, 100.9), [], t),
        (Label('Drill/countersink for each screw', 2, attach=1), at(10, 108), [], t),
        (Label('Remove plastic shields', 2, attach=1), at(1.6, 13.31), [], t),
        (Leader(((-3.5, -4), (-6.5, -4))), at(37.5, 16), [], t),
        (Leader(((-4.88, -4), (-1.88, -4))), at(0.88, 16), [], t),
        (Leader(((4.29, 9.47), (7.29, 9.47))), at(0.71, 97.53), [], t),
    ]
    # 3_Threshold
    t, at = steps('threshold'), view_at('threshold')
    out += [
        (Label('3" Flooring blocks', 2, attach=1), at(38.57, 6.76), [], t),
        (Label('Doorway', 2, attach=1), at(13, 2), [], t),
        (Label('Finished floor edge', 2, attach=1), at(38.69, 2.86), [], t),
        (Label('Flexible flashing', 2, attach=1), at(28, -10), [], t),
        (Label('Interior Plywood', 2, attach=3), at(-6.64, 2.96), [], t),
        (Leader(((-2.49, 3.59), (-4.57, 3.59))), at(-1.43, -2.03), [], t),
        (Leader(((4, -3), (8, -3))), at(19, -8.75), [], t),
        (Leader(((5.07, 5.11), (7.26, 5.11))), at(30.88, -3.36), [], t),
        (Leader(((8.68, 9.16), (12.64, 9.16))), at(25.49, -4.4), [], t),
    ]
    for x in (-1.33, 37.92):  # the door studs, cut
        out += [(n, at(x, -6.14), [], t) for n in crossed_box(1.5, 3.5)]
    # 3.1_ScrewLocs
    t, at = steps('screws'), view_at('screws')
    out += [
        (Label('1"', 2, attach=1), at(14.55, 83.28), [], t),
        (Label('1/2"', 2, attach=1), at(21.3, 84.3), [], t),
        (Label('Door Frame Screw Locations', 2.5, attach=1), at(-1.36, -2.41), [], t),
        (Label('Hinge side', 2, attach=1), at(-8.21, 5.32), [], t),
        (Label('Inside', 2, attach=1), at(-16.66, 50.09), [], t),
        (Label('Inside', 2, attach=1), at(48.16, 49.93), [], t),
        (Label('Latch side', 2, attach=1), at(38.26, 5.1), [], t),
        (Label('Outside', 2, attach=1), at(0, 50), [], t),
        (Label('Outside', 2, attach=1), at(27.41, 49.93), [], t),
        (Leader(((-2.83, 0),)), at(19.22, 84.75), [], t),
        (Leader(((0, -2.4),)), at(15.83, 81), [], t),
        (Leader(((0.02, 2.52),)), at(15.82, 83.84), [], t),
        (Leader(((2.79, 0),)), at(20.35, 84.75), [], t),
        (Circle(DETAIL[2]), at(*DETAIL[:2]), [], t),
        (Circle(3.92), at(-5.17, 75.44), [], t),
        (Leader(((5.09, 0.46),), arrow=False), at(-1.25, 75.44), [], t),
    ]
    for point in HINGE_MARKS:
        out += mark("screws", point)
    for point in LATCH_MARKS:
        out += mark("screws_latch", point)
    out += mark("screws_detail", HINGE_MARKS[2], 3/2)
    for z0, z1, text in ((0, LATCH_SCREWS_Z[0], "17"), (LATCH_SCREWS_Z[1], JAMB_HEIGHT, "10")):
        x, y0 = VIEWS["screws_latch"].xy((FRAME_WIDTH, 0, z0))
        _, y1 = VIEWS["screws_latch"].xy((FRAME_WIDTH, 0, z1))
        out += [(n, at(x + 4.38, y0), [], t) for n in vertical_dimension(y1 - y0, text)]
        out += [(Leader(((5, 0),), arrow=False), at(x - 0.12, y), [], t) for y in (y0, y1)]
    # 4_Shimming
    t, at = steps('shims'), view_at('shims')
    out += [
        (Label('Gap between door edge and jamb\n  should be about 1/8" after shimming', 2, attach=1), at(16.7, 1.95), [], t),
        (Label('Gap should be even\n  across top of door', 2, attach=1), at(2.93, 83.84), [], t),
        *[(Label('Hinge', 2.5, attach=1), at(1.43, y), [], t) for y in (19.48, 46.36, 72.4)],
        (Label('Inside of door', 2.5, attach=1), at(6.44, 60.4), [], t),
        *[(Label('Shim', 2.5, attach=1), at(-24.56, y), [], t) for y in (21.4, 48.4, 74.9)],
        *[(Label('Shim', 2.5, attach=3), at(51.44, y), [], t) for y in (21.4, 74.9)],
        (Label('Shims', 2.5, attach=1), at(-14.79, 95.98), [], t),
        (Label('Shims', 2.5, attach=1), at(31.44, 95.4), [], t),
        (Label('Shims', 2.5, attach=3), at(51.44, 50.4), [], t),
        (Leader(((-20.48, -27.31), (-16.69, -27.31))), at(31.39, 28.21), [], t),
        *[(Leader(((-5, -5), (-9, -5))), at(-5.56, y), [], t) for y in (24.4, 51.4, 78.4)],
        (Leader(((-5, -5), (-1, -5))), at(2.84, 87.88), [], t),
        (Leader(((-5, 5), (-9, 5))), at(4.44, 89.4), [], t),
        *[(Leader(((2.98, -4.06), (5.48, -4.06))), at(-4.69, y), [], t) for y in (21.97, 48.85, 74.89)],
        (Leader(((4.9, 1.97),)), at(32.54, 46.43), [], t),
        (Leader(((5, 5), (9, 5))), at(21.44, 89.4), [], t),
        *[(Leader(((5, -5), (9, -5))), at(32.44, y), [], t) for y in (24.4, 53.4, 78.4)],
    ]
    # 5_Strike Plate
    t, at = steps('strike'), view_at('strike')
    out += [
        (Icon('Screw', 3, 7.2, rotation=-150), at(25.5, 42.78), [], t),
        (Label('Drill and countersink\n  1/2" from edge,\n  at a 30° angle', 2, attach=1), at(40, 32), [], t),
        (Leader(((8.54, 12.85),)), at(26.46, 18.15), [], t),
        (Leader(((8.54, 6), (12.54, 6))), at(26.46, 25), [], t),
    ]
    out += [(n, at(11.5, 45), [], t) for n in crossed_box(14, 6)]  # the stud, cut
    for dz in (-STRIKE_SCREWS, STRIKE_SCREWS):  # where to drill, on the jamb's face
        out += mark("strike_face", (FRAME_WIDTH, SCREW_FROM_EDGE, LATCH_Z + dz), 2)
    return out


def mark_cross(size=1/2):
    """A "+" centered on its anchor."""
    return [Leader(((2 * size, 0),), arrow=False, dx=-size), Leader(((0, 2 * size),), arrow=False, dy=-size)]
