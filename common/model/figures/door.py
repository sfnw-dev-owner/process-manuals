"""floor_door/door_manual.md figures: the door assembly (model/doors.py) as
each figure's view shows it (from inside, in plan at the floor, the jamb
legs from the doorway, details at the top hinge and the strike plate); the
wall and floor around it where the figure needs them. The notes hang on
points of the assembly, through the views."""

from build123d import Align, Box, Compound, Cylinder, Location, Plane, Pos, Vector
from build123d import scale as scaled

from model.dimensions import PLATFORM_LENGTH
from model.doors import (
    DOOR_HEADER_Z, DOOR_IN_HOUSE, FRAME_BOTTOM, FRAME_GAP, FRAME_WIDTH, FRAMING_Y, HINGE, HINGE_MARKS, HINGE_Z,
    INTERIOR_PLYWOOD, JAMB_DEPTH, JAMB_HEIGHT, LATCH_MARKS, LATCH_SCREWS_Z, LATCH_Z, SCREW_FROM_EDGE, STOP_Y,
    STRIKE_MARKS, door_assembly,
)
from model.common import key
from model.flooring import floor_rows, flooring
from model.notes import (
    SMALL, Label, aimed, around, at, beside, callout, cross, crossed_box, dimension, inches, line, next_to, pointer, title,
)
from model.walls import DOOR_OPENING, WALL_DEPTH, front_wall_framing, front_wall_skin

from . import GRAY, Extent, Figure, extent, table

MD = "floor_door/door_manual.md"

# The front wall and floor, in the assembly's frame.
HOUSE = DOOR_IN_HOUSE.inverse()  # the house's frame, with the deck at Z = 0
FRONT_WALL = HOUSE * Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, 0)
MARK = 1/40  # a pencil mark's half-size, paper inches
DETAIL_SCALE = 3  # the top hinge's screw mark, enlarged
STRIKE_SCALE = 4  # the strike plate's views


class View:
    """Looking at the assembly from `direction`, `up` up the page, drawn at
    `k` times size, with the assembly's `point` at `at` in the drawing."""

    def __init__(self, direction, up, k, point, at):
        z = Vector(*direction).normalized()
        x = Vector(*up).cross(z).normalized()
        self.camera = Location(Plane((0, 0, 0), x_dir=x, z_dir=z)).inverse()
        self.k = k
        p = (self.camera * Pos(*point)).position
        self.offset = (at[0] - k * p.X, at[1] - k * p.Y)

    def xy(self, point):
        """Where an assembly point is in the drawing."""
        p = (self.camera * Pos(*point)).position
        return self.offset[0] + self.k * p.X, self.offset[1] + self.k * p.Y

    def drawn(self, shapes, style="hlr_thin", fill=None):
        """Figure parts for assembly shapes, as this view shows them."""
        out = []
        for s in shapes:
            # (scale() scales a lone solid about its own location; a compound
            # about the origin, which is what's wanted here)
            d = Pos(*self.offset, 0) * scaled(Compound([self.camera * s]), by=self.k)
            out.append((d, style) if fill is None else (d, style, fill))
        return out


FROM_INSIDE, UP = (0, -1, 0), (0, 0, 1)
VIEWS = {
    "door": View(FROM_INSIDE, UP, 1, (0, 0, 0), (0, 0)),
    # A plan section at the floor, looking down, the inside at the top.
    "threshold": View((0, 0, 1), (0, -1, 0), 1, (0, 0, 0), (0, 0)),
    # The legs' faces, seen from the doorway (the hinge leg left, the latch leg right, 50" apart); a detail at the top hinge.
    "screws": View((1, 0, 0), UP, 1, (0, 0, 0), (0, 0)),
    "screws_latch": View((-1, 0, 0), UP, 1, (FRAME_WIDTH, 0, 0), (50, 0)),
    "screws_detail": View((1, 0, 0), UP, DETAIL_SCALE, (0, -1/2, HINGE_Z[2]), (25, 60)),
    "shims": View(FROM_INSIDE, UP, 1, (0, 0, 0), (0, 0)),
    # 4x: the latch jamb in section at the latch, from above (the outside on
    # the left, the wall running up the page); and its face, from the doorway, under it.
    "strike": View((0, 0, 1), (1, 0, 0), STRIKE_SCALE, (FRAME_WIDTH, JAMB_DEPTH, LATCH_Z), (0, 24)),
    "strike_face": View((-1, 0, 0), UP, STRIKE_SCALE, (FRAME_WIDTH, JAMB_DEPTH, LATCH_Z), (0, 0)),
}
STRIKE_FACE_WINDOW = (LATCH_Z - 3.2, LATCH_Z + 3)  # the strike face view's height


def assembly(*names):
    """The assembly's parts made from these components, in its frame."""
    # (the slab plain: no panels or knob on its outside)
    return [loc * comp.shape(frozenset({"Door Outside"}), key(mods)) for comp, loc, mods, _ in door_assembly()[1]
            if getattr(comp, "__name__", "") in names]


def box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=Align.MIN)


def clip(shapes, window):
    out = []
    for s in shapes:
        c = s & window
        if c.volume > 1e-9:
            out.append(c)
    return out


def wall_panels(x0, x1):
    """The interior wall panels either side of the doorway, between x0 and x1
    (they're not in the model yet: 1/2" plywood on the framing)."""
    y = (FRAMING_Y - INTERIOR_PLYWOOD, FRAMING_Y)
    return [box(x0, -FRAME_GAP, *y, -FRAME_BOTTOM, 90), box(FRAME_WIDTH + FRAME_GAP, x1, *y, -FRAME_BOTTOM, 90)]


def marks(view, points, size=MARK):
    """Pencil crosses at assembly points, as a view shows them."""
    return [at(view.xy(p), cross(size)) for p in points]


def figures(scale=1/16, only=None):
    V = VIEWS
    frame = assembly("jamb_leg", "head_jamb", "brickmold")
    slab, hinges = assembly("door_slab"), assembly("hinge")
    x0, x1 = -FRAME_GAP - 7.5, FRAME_WIDTH + FRAME_GAP + 6
    hinge_leg, latch_leg = assembly("jamb_leg")[:1], assembly("jamb_leg")[1:]

    # 2_Door: the frame from inside, its legs cut for the ADA threshold.
    door_parts = V["door"].drawn(frame + slab) + V["door"].drawn(hinges, "new")
    frame_ext = extent(V["door"].drawn(frame))
    door_notes = [
        aimed(frame_ext.top_left, "Screw", "above"), aimed(frame_ext.top_right, "Screw", "above"),
        *callout((frame_ext.x0 + 2, frame_ext.y1 + 0.6 / scale), "Drill/countersink for each screw", "above right", lead=1/4),
        *callout(frame_ext.bottom_left, "Remove plastic shields", "below right", lead=1/2),
        pointer(frame_ext.bottom_right, 1/4, -1/4),
    ]

    # 3_Threshold: the doorway in plan at the floor, before the door goes in.
    around_ = box(x0, x1, -1, JAMB_DEPTH + 3, -FRAME_BOTTOM - 1, -FRAME_BOTTOM + 3)
    walls = [FRONT_WALL * front_wall_framing.shape(), FRONT_WALL * front_wall_skin.shape()]
    floor_at_door = [HOUSE * loc * comp.shape() for comp, loc, _, _ in floor_rows(10)]
    strip = [HOUSE * loc * comp.shape() for comp, loc, _, _ in flooring()[1] if getattr(comp, "__name__", "") == "doorway_strip"]
    studs = clip(walls, around_ & box(x0, x1, -1, 10, 2, 3))
    panels = clip(wall_panels(x0, x1), around_)
    floor_edge = clip(floor_at_door, box(-FRAME_GAP, FRAME_WIDTH + FRAME_GAP, FRAMING_Y, 5, -5, 5))
    flashing = assembly("flashing")
    T = V["threshold"]
    threshold_parts = (T.drawn(studs) + T.drawn(panels) + T.drawn(floor_edge) + T.drawn(strip) + T.drawn(flashing, "hlr_thin", "laid"))
    strip_ext, floor_ext, flash_ext = extent(T.drawn(strip)), extent(T.drawn(floor_edge)), extent(T.drawn(flashing))
    panel_ext = extent(T.drawn(panels[:1]))
    threshold_notes = [
        *callout(strip_ext.point(0.75, 0.3), '3" Flooring blocks', "below right", lead=0.6),
        at((strip_ext.center[0], strip_ext.y1 + 0.45 / scale), Label("Doorway")),
        *callout(floor_ext.point(0.9, 1), "Finished floor edge", "above right", lead=1/2),
        *callout(flash_ext.point(0.4, 0), "Flexible flashing", "below left", lead=1/2),
        *callout(panel_ext.point(0.5, 0), "Interior Plywood", "below right", lead=1/2),
    ]
    for e in sorted((Extent(T.drawn([s])[0][0]) for s in studs[0].solids()), key=lambda e: (e.x0, e.y0)):  # the door studs, cut
        threshold_notes.append((e.x0, e.y0, crossed_box(e.width * scale, e.height * scale)))

    # 3.1_ScrewLocs: the legs from the doorway, and a detail at the top hinge.
    S, SL, SD = V["screws"], V["screws_latch"], V["screws_detail"]
    detail_center = SD.xy((0, -1/2, HINGE_Z[2]))
    detail_r = 5 * DETAIL_SCALE * scale  # paper
    detail_circle = Pos(*detail_center, 0) * Cylinder(detail_r / scale, 2000)
    detail = [s & detail_circle for s, _ in SD.drawn(hinge_leg + hinges[2:])]
    screws_parts = S.drawn(hinge_leg + hinges) + SL.drawn(latch_leg + assembly("strike_plate")) + [(s, "hlr_thin") for s in detail if s.volume > 1e-9]
    hinge_ext, latch_ext = extent(S.drawn(hinge_leg)), extent(SL.drawn(latch_leg))
    top_mark = SD.xy(HINGE_MARKS[2])
    hinge_top = S.xy(HINGE_MARKS[2])
    screws_notes = marks(S, HINGE_MARKS) + marks(SL, LATCH_MARKS) + marks(SD, [HINGE_MARKS[2]], 3 * MARK) + [
        around(hinge_top, 1/4), around(detail_center, detail_r),
        line((hinge_top[0] + 1/4 / scale, hinge_top[1]), (detail_center[0] - detail_r / scale, detail_center[1]), scale),
        *dimension((top_mark[0], SD.xy((0, -1/2, HINGE_Z[2] + HINGE[2]))[1]), top_mark, scale, '1"', offset=-1/4),
        *dimension((SD.xy((0, STOP_Y, 0))[0], top_mark[1]), top_mark, scale, '1/2"', offset=1/4),  # from the stop
        beside(hinge_ext.bottom, "below", Label("Hinge side"), 1/4), beside(latch_ext.bottom, "below", Label("Latch side"), 1/4),
        beside(hinge_ext.left, "left", Label("Inside"), 1/4), beside(hinge_ext.right, "right", Label("Outside"), 1/4),
        beside(latch_ext.left, "left", Label("Outside"), 1/4), beside(latch_ext.right, "right", Label("Inside"), 1/4),
    ]
    for z0, z1 in ((0, LATCH_SCREWS_Z[0]), (LATCH_SCREWS_Z[1], JAMB_HEIGHT)):  # the latch side's screws, from the ends
        a, b = SL.xy((FRAME_WIDTH, 0, z0)), SL.xy((FRAME_WIDTH, 0, z1))
        screws_notes += dimension((latch_ext.x1, a[1]), (latch_ext.x1, b[1]), scale, inches(z1 - z0), offset=3/8)

    # 4_Shimming: the frame in the rough opening, from inside.
    rough = (box(-FRAME_GAP, FRAME_WIDTH + FRAME_GAP, -1, 0, -FRAME_BOTTOM, DOOR_HEADER_Z[0] - FRAME_BOTTOM)
             - box(-FRAME_GAP + 0.01, FRAME_WIDTH + FRAME_GAP - 0.01, -2, 1, -FRAME_BOTTOM + 0.01,
                   DOOR_HEADER_Z[0] - FRAME_BOTTOM - 0.01))
    Sh = V["shims"]
    side_shims, top_shims = assembly("shim"), assembly("top_shim")
    shims_parts = Sh.drawn([rough] + frame + slab) + Sh.drawn(hinges, "new") + Sh.drawn(side_shims + top_shims, "new")
    slab_ext = extent(Sh.drawn(slab))
    shims_notes = [at(slab_ext.point(0.5, 0.6), Label("Inside of door"))]
    for h in Sh.drawn(hinges):
        shims_notes += callout(Extent(h[0]).right, "Hinge", "below right", lead=3/8)
    done = []
    for s in Sh.drawn(side_shims):  # (a pair close together, either side of the latch: one "Shims")
        e = Extent(s[0])
        if any(abs(e.center[1] - d) < 4 for d in done):
            continue
        done.append(e.center[1])
        pair = any(0 < abs(Extent(o[0]).center[1] - e.center[1]) < 4 for o in Sh.drawn(side_shims))
        left = e.center[0] < slab_ext.center[0]
        shims_notes += callout(e.left if left else e.right, "Shims" if pair else "Shim", "left" if left else "right", lead=1/2)
    for s in Sh.drawn(top_shims):
        shims_notes += callout(Extent(s[0]).top, "Shims", "above left", lead=3/8)
    shims_notes += callout((slab_ext.center[0], slab_ext.y1), "Gap should be even\nacross top of door", "below right", lead=1/2)
    shims_notes += callout((slab_ext.x1, slab_ext.point(0, 0.3)[1]), 'Gap between door edge and jamb\nshould be about 1/8" after shimming', "below right", lead=1)

    # 5_Strike Plate: the latch jamb in section at the latch, and its face.
    St, Sf = V["strike"], V["strike_face"]
    at_latch = box(FRAME_WIDTH - 1, FRAME_WIDTH + FRAME_GAP + 8.5, -1, JAMB_DEPTH + 1, LATCH_Z - 0.1, LATCH_Z + 0.1)
    face_window = box(FRAME_WIDTH - 1, FRAME_WIDTH + 1, -1, JAMB_DEPTH + 1, *STRIKE_FACE_WINDOW)
    section = clip(latch_leg + walls + wall_panels(x0, x1), at_latch)
    strike_parts = St.drawn(section) + Sf.drawn(clip(latch_leg + assembly("strike_plate"), face_window))
    stud = extent(St.drawn(clip(walls[:1], at_latch)))
    jamb_face = St.xy((FRAME_WIDTH, SCREW_FROM_EDGE, LATCH_Z))
    strike_notes = marks(Sf, STRIKE_MARKS, 2 * MARK) + [
        (stud.x0, stud.y0, crossed_box(stud.width * scale, stud.height * scale)),
        aimed(jamb_face, "Screw", 30 + 180, size=0.8),  # 30° off the jamb's face, toward the outside
        *callout(jamb_face, 'Drill and countersink\n1/2" from edge,\nat a 30° angle', "below right", lead=3/4),
    ]

    rows = {
        "door": (door_parts, [], door_notes),
        "threshold": (threshold_parts, [], threshold_notes),
        "screw_locations": (screws_parts, [], screws_notes + [title(extent(screws_parts).bottom, "Door Frame Screw Locations", gap=5/8)]),
        "shimming": (shims_parts, [], shims_notes),
        "strike_plate": (strike_parts, [], strike_notes),
    }
    return table(MD, rows)
