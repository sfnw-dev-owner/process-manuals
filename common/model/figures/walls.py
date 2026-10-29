"""Wall figures: Side_Walls/sidewall_1.md and sidewall_3.md,
Front_Wall/front_wall_ada.md, Rear_Wall/rear_wall.md. Each wall is drawn as
it lies in its jig, outside face up:

  side walls:  drawing X = down from the top of the wall (top plate at 0), Y = along the wall
  end walls:   drawing X = along the wall as seen from outside, Y = height

Each manual is a table of its figures: the framing members (walls.py names
them, with the step that places them) drawn as the jig, in place, or new;
the jig tools; and the notes, hung on the members' extents in the drawing.
"""

from build123d import Align, Box, Location, Plane, Pos

from model.common import key
from model.dimensions import END_WALL_PLATE_LENGTH, SIDE_WALL_PLATE_LENGTH, SIDING_HEIGHT, SIDING_PANEL_WIDTH, STUD_LENGTH
from model.notes import (
    CIRCLED, GAP, SMALL, TITLE, Circle, Label, Lines, aimed, at, beside, callout, circled, crossed_box, dimension, icon,
    inches, next_to, pointer, title,
)
from model.walls import (
    DOOR_HEADER_Z, DOOR_OPENING, DOOR_X, END_SIDING_WIDTH, END_SIDING_X, SIDING, SIDING_BOTTOM, SIDING_Y, SILL_Z,
    STRETCHER_AT, STUD, WALL_DEPTH, WALL_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_X, WINDOW_Z, WRAP,
    front_wall_members, funky_board, funky_board_at, panel, rear_wall_members, side_wall_members, siding_panel_door,
    siding_panel_plain, siding_panel_window, stretcher, window_flange_flashing, window_opening_flashing,
    window_unit_at,
)

from . import TYVEK, Extent, Figure, extent, table, xy

SIDE_MD = {1: "Side_Walls/sidewall_1.md", 3: "Side_Walls/sidewall_3.md"}
FRONT_MD = "Front_Wall/front_wall_ada.md"
REAR_MD = "Rear_Wall/rear_wall.md"
PAPER_NOTES = True

SIDE_TO_DRAWING = Location(Plane((WALL_HEIGHT, SIDE_WALL_PLATE_LENGTH, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0)))
END_TO_DRAWING = Location(Plane((END_WALL_PLATE_LENGTH, 0, 0), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)))

SMALL_GUN = 0.6  # the nail gun icon, scaled down where several crowd a short board
END_SCREWS = 8  # along a side wall's end stud, into the flat stud (step 2)
SCREWS_PER_END = 2  # through a plate into each end of a flat stud (step 2)
DOUBLING_NAILS = 3  # along a pair of studs nailed together


class Framing:
    """A wall's framing members in the drawing, by name: their shapes and
    extents, and the step that places each."""

    def __init__(self, members, to_drawing):
        self.shape, self.ext, self.step = {}, {}, {}
        for name, (comp, loc, step) in members.items():
            self.shape[name] = to_drawing * loc * comp.shape()
            self.ext[name] = Extent(self.shape[name])
            self.step[name] = step

    def placed(self, *steps):
        """The members these steps place."""
        return [self.shape[n] for n, s in self.step.items() if s in steps]

    def before(self, step, order):
        """The members placed before `step` (in `order`)."""
        done = order[:order.index(step)]
        return [self.shape[n] for n, s in self.step.items() if s in done]

    @property
    def all(self):
        return list(self.shape.values())

    @property
    def whole(self):
        return extent(self.all)


def ctx(xs):
    return [(s, "context") for s in xs]


def new(xs):
    return [(s, "new") for s in xs]


def jig(xs):
    return [(s, "jig") for s in xs]


def gun(point, side, size=1):
    """A nail gun aimed at a point from a side."""
    return aimed(point, "NailGun", side, size=size)


def counted(point, side, count, size=1, label_side=None):
    """A nail gun (or screw: count ends in "screws") at a point, with how
    many nails, beside it."""
    tool = aimed(point, "Screw" if "screw" in count else "NailGun", side, size=size)
    return [tool, next_to(tool, label_side or side, Label(count))]


def crossed_out(placed):
    """A placed icon, circled and struck through: "don't"."""
    x, y, note = placed
    from model.notes import rotated_extent
    w, h = rotated_extent(note.width, note.height, note.rotation)
    r = (w * w + h * h) ** 0.5 / 2
    d = r * 0.7
    return [placed, (x, y, Circle(r, dx=note.dx, dy=note.dy)),
            (x, y, Lines((((-d, -d), (d, d)),), dx=note.dx, dy=note.dy))]


def tyvek(to_drawing, x0, width, holes=()):
    return to_drawing * Pos(x0, WALL_DEPTH, SIDING_BOTTOM) * panel(width, SIDING_HEIGHT, WRAP, holes=holes)


# ── side walls ─────────────────────────────────────────────────────────────

def side_wall_figures(wall, first_panel, scale):
    """A side wall's figures. wall: 1 or 3 (the titles, and the step-6/7
    layers); first_panel: which end the first siding panel goes on (0 or 2)."""
    md = SIDE_MD[wall]
    F = Framing(side_wall_members(), SIDE_TO_DRAWING)
    E, whole = F.ext, F.whole
    panels = [SIDE_TO_DRAWING * Pos(x, SIDING_Y, SIDING_BOTTOM) * siding_panel_plain.shape()
              for x in (0, SIDING_PANEL_WIDTH, 2 * SIDING_PANEL_WIDTH)]
    wrap = [tyvek(SIDE_TO_DRAWING, 0, SIDE_WALL_PLATE_LENGTH)]
    ab = "a" if wall == 1 else "b"
    plates = {"left": E["top_plate"], "right": E["bottom_plate"]}  # as drawn: the top of the wall at the left
    ends = {"above": E["end_stud_0"], "below": E["end_stud_1"]}  # the wall's ends, at the top and bottom of the drawing
    flats = {"above": E["flat_stud_0"], "below": E["flat_stud_1"]}
    inner = [n for n in E if n.startswith("stud_")]

    def through_plate(member, side, count=None):
        """A nail gun outside a plate, nailing through it into a member's end."""
        plate = plates[side]
        p = (plate.x0 if side == "left" else plate.x1, member.center[1])
        return counted(p, side, count) if count else [gun(p, side)]

    def mark_on_plates(member):
        """A pencil tick on each plate at a member's center line."""
        out = []
        for side, sign in (("left", -1), ("right", 1)):
            plate = plates[side]
            p = (plate.x0 if sign < 0 else plate.x1, member.center[1])
            out += [pointer(p, sign / 8, 0, arrow=False), aimed((p[0] + sign / 8 / scale, p[1]), "Pencil", side)]
        return out

    # Step 1: nail the corners (through the plates into the end studs), 2 nails each.
    step1 = [n for e in ends.values() for side in ("left", "right") for n in through_plate(e, side, "x2")]
    # Step 2: clamp each flat stud to its end stud, screw through the plates into
    # its ends and along the end stud into it; the corner in section.
    step2 = []
    for side, flat in flats.items():
        end = ends[side]
        for plate_side in ("left", "right"):
            step2 += through_plate(flat, plate_side, f"x{SCREWS_PER_END} screws")
        edge_y = end.y1 if side == "above" else end.y0
        for k in range(END_SCREWS):
            step2.append(aimed((end.x0 + (k + 1/2) / END_SCREWS * end.width, edge_y), "Screw", side))
        step2.append(beside((end.center[0], edge_y), side, Label(f"{END_SCREWS} screws"), 0.54 + GAP))
        inner_y = flat.y0 if side == "above" else flat.y1
        for fx in (1/4, 3/4):
            step2 += callout((end.x0 + fx * end.width, inner_y), "CLAMP", "below" if side == "above" else "above", lead=5/16)
    corner = (plates["right"].x1, ends["above"].y1)  # the top right corner, in section in the inset
    k = 4 * scale  # the inset's size, paper inches per inch
    section_r = (WALL_DEPTH + STUD) * k / 2 + 1/16
    inset = (corner[0] + (1 + section_r) / scale, corner[1] + (0.6 + section_r) / scale)  # clear of the screws
    step2 += [
        (corner[0], corner[1], Circle(0.3, dx=-0.15, dy=-0.15)),
        (inset[0], inset[1], Circle(section_r)),
        pointer(corner, (inset[0] - corner[0]) * scale - section_r, (inset[1] - corner[1]) * scale, arrow=False, weight=1/2),
        (inset[0], inset[1], crossed_box(STUD * k, WALL_DEPTH * k, dx=-(WALL_DEPTH + STUD) * k / 2, dy=-WALL_DEPTH * k / 2)),  # the end stud
        (inset[0], inset[1], crossed_box(WALL_DEPTH * k, STUD * k, dx=-(WALL_DEPTH + STUD) * k / 2 + STUD * k, dy=-WALL_DEPTH * k / 2)),  # the flat stud
    ]
    # Step 3: mark the inner studs' lines on the plates.
    step3 = [n for name in inner for n in mark_on_plates(E[name])]
    # Step 4: nail through the plates into the inner studs, 2 each.
    step4 = [n for name in inner for side in ("left", "right") for n in through_plate(E[name], side, "x2")]
    step4.append(at(whole.center, Label("Final QC before Tyvek")))
    # Step 5: the Tyvek.
    step5 = [at(whole.center, icon("staple-gun")), beside(whole.center, "below", Label("TYVEK"), 0.4 + GAP)]
    top = beside(plates["left"].left, "left", Label("TOP"), 1/4)
    # Step 6: the first panel, against the funky board.
    board_at = funky_board_at(SIDING_PANEL_WIDTH, -1) if first_panel == 0 else funky_board_at(2 * SIDING_PANEL_WIDTH, 1)
    board_ext = Extent(funky_board.shape().moved(SIDE_TO_DRAWING * board_at))
    step6 = callout(board_ext.left, "Funky\nBoard", "left", lead=3/8) + [at(Extent(panels[first_panel]).center, Label("Panel 1"))]
    # Step 7: the other panels; rout the siding's edges flush with the framing, jigsaw its overhang.
    skin = extent(panels)
    step7 = []
    for side, edge_y, sign in (("above", skin.y1, 1), ("below", skin.y0, -1)):
        step7.append(aimed((whole.x0 + whole.width / 4, edge_y), "Router", side))
        step7 += dimension((whole.x0, edge_y), (whole.x1, edge_y), scale, "Rout off excess edge after\nnailing down panel", offset=sign * 3/8)
        step7 += dimension((whole.x1, edge_y), (skin.x1, edge_y), scale, "Use jigsaw\nhere", offset=sign * 3/8)
    order = [1, 2, 3] if first_panel == 0 else [3, 2, 1]
    step7 += [at(Extent(p).center, Label(f"Panel {n}")) for p, n in zip(panels, order)]

    framing = F.all
    flat = F.placed(1)[-2:]  # (the flat studs, laid in at step 1 and screwed at step 2)
    s1 = [s for s in F.placed(1) if s not in flat]
    s3 = F.placed(3)
    tyv = [(s, "bare", TYVEK) for s in wrap]
    rows = {
        "step_01": (jig(framing) + new(s1) + [(s, "outline", "laid") for s in flat], [], step1),
        "step_02": (jig(framing) + ctx(s1) + new(flat), [], step2),
        "step_03": (jig(framing) + ctx(s1 + flat) + new(s3), [], step3),
        "step_04": (ctx(framing), [], step4),
        "step_05": (tyv + ctx(framing), [], step5 + [top]),
        "step_06": (tyv + ctx(framing) + ctx([panels[first_panel]]), [(funky_board, SIDE_TO_DRAWING * board_at)], step6 + [top]),
        "step_07": (ctx(framing) + ctx(panels), [], step7 + [top]),
    }
    figs = table(md, rows)
    for fig in figs:
        step = int(fig.name[-2:])
        caption = f"Step {step}\nSide Wall" + (f"\nWall #{wall}" if step >= 6 else "")
        fig.notes.append(title(whole.bottom, caption, gap={2: 1.1, 7: 1}.get(step, 3/8)))
    return figs


# ── end walls ──────────────────────────────────────────────────────────────

def end_wall_skin(window_hole, door_hole):
    """Wrap and the two panels of an end wall's skin, in its frame."""
    door = (DOOR_X - END_SIDING_X, -SIDING_BOTTOM, DOOR_OPENING, DOOR_HEADER_Z[0])
    window = (WINDOW_X - END_SIDING_X, WINDOW_Z - SIDING_BOTTOM, WINDOW_WIDTH, WINDOW_HEIGHT)
    holes = ([window] if window_hole else []) + ([door] if door_hole else [])
    return tyvek(END_TO_DRAWING, END_SIDING_X, END_SIDING_WIDTH, holes)


def end_panels(left):
    return [END_TO_DRAWING * Pos(END_SIDING_X, SIDING_Y, SIDING_BOTTOM) * left.shape(),
            END_TO_DRAWING * Pos(END_SIDING_X + SIDING_PANEL_WIDTH, SIDING_Y, SIDING_BOTTOM) * siding_panel_window.shape()]


def glass():
    """The window's lower pane, hatched (where the unit's lower sash has it;
    window_unit_at keeps the unit's X)."""
    from model.walls import lower_pane
    x, z, w, h = lower_pane()
    pane = Pos(WINDOW_X - 1/40 + x, 0, WINDOW_Z + z) * Box(w, WALL_DEPTH, h, align=Align.MIN)
    return [(END_TO_DRAWING * pane, "bare", "glass")]


def window_unit():
    comp, loc, mods, _ = window_unit_at()
    return END_TO_DRAWING * loc * comp.shape(frozenset(), key(mods))


class EndWall:
    """What an end wall's figures hang their notes on."""

    def __init__(self, members, scale):
        self.F = Framing(members, END_TO_DRAWING)
        self.E, self.whole, self.scale = self.F.ext, self.F.whole, scale
        self.top, self.bottom = self.E["top_plate"], self.E["bottom_plate"]

    def through_top(self, member, count=None, size=1, label_side="right"):
        """A nail gun above the top plate, nailing down into a member."""
        p = (member.center[0], self.top.y1)
        return counted(p, "above", count, size, label_side) if count else [gun(p, "above", size)]

    def through_bottom(self, member, count=None, size=1, label_side="right"):
        p = (member.center[0], self.bottom.y0)
        return counted(p, "below", count, size, label_side) if count else [gun(p, "below", size)]

    def into_side(self, member, target, y, count=None, size=1):
        """A nail gun against a member's side away from `target` (another
        member it's nailed to, through the member), at height y."""
        from_left = member.center[0] > target.center[0]  # the gun is to the right of the member
        p = (member.x1, y) if from_left else (member.x0, y)
        side = "right" if from_left else "left"
        return counted(p, side, count, size) if count else [gun(p, side, size)]

    def header_notes(self, headers, sill, near, far, size=SMALL_GUN):
        """Step 2 of both end walls: the three headers clamped to the top
        plate and nailed from both sides, nailed through the studs at their
        ends, and the sill nailed through the studs."""
        E = self.E
        top = extent([self.F.shape[h] for h in headers])
        out = callout((top.center[0], self.top.y1), "Clamp 3 header boards to top plate", "above", lead=0.7)
        for fx in (1/6, 1/2, 5/6):
            x = top.x0 + fx * top.width
            out += [gun((x, self.top.y1), "above", size), gun((x, top.y0), "below", size)]
        for stud_, side in ((near, "near"), (far, "far")):
            out += self.into_side(stud_, top, top.center[1], size=size)
            out += self.into_side(stud_, E[sill], E[sill].center[1], "x2", size=size)
        out.append(beside(self.into_side(far, top, top.center[1], size=size)[0][:2], "right" if far.center[0] > near.center[0] else "left",
                          Label("x1 into each header\nboth ends"), 0.6))
        return out

    def corners(self, end_a, end_b):
        """Step 1 of both end walls: the corners nailed, 2 nails each, the
        plates labeled, the studs' length dimensioned."""
        E, whole = self.E, self.whole
        out = []
        for name in (end_a, end_b):
            out += self.through_top(E[name], "x2", label_side="right" if E[name].center[0] > whole.center[0] else "left")
            out += self.through_bottom(E[name], "x2", label_side="right" if E[name].center[0] > whole.center[0] else "left")
        out += callout(self.top.point(0.45, 1), f'{inches(END_WALL_PLATE_LENGTH)} Top Plate', "above right", lead=1/2)
        out += callout(self.bottom.point(0.45, 0), f'{inches(END_WALL_PLATE_LENGTH)} Bottom Plate', "below right", lead=1/2)
        left = E[end_a] if E[end_a].x0 < E[end_b].x0 else E[end_b]
        out += dimension(left.bottom_left, left.top_left, self.scale, inches(STUD_LENGTH), offset=-3/8)
        return out


def front_wall_figures(scale):
    W = EndWall(front_wall_members(), scale)
    E, F, whole = W.E, W.F, W.whole
    order = [1, 2, 3, 4, 5]
    door = Extent.__new__(Extent)  # the doorway: between the door studs, from the bottom plate to the header
    door.x0, door.x1 = min(E["door_stud_end"].x1, E["door_stud_middle"].x1), max(E["door_stud_end"].x0, E["door_stud_middle"].x0)
    door.y0, door.y1 = W.bottom.y1, E["door_header_lower"].y0
    headers = ["header_1", "header_2", "header_3"]
    near, far = E["window_stud_near"], E["window_stud_far"]
    middle, door_mid, door_end = E["middle_stud"], E["door_stud_middle"], E["door_stud_end"]
    sill = E["sill"]

    # Step 3: the next stud beside the window's, clamped and nailed to it below the window.
    step3 = W.through_top(far) + W.through_top(near)
    step3.append(beside(((far.center[0] + near.center[0]) / 2, W.top.y1), "above", Label("x2 both studs"), 0.6 + GAP))
    step3 += W.through_top(middle, "x2")
    step3 += W.through_bottom(far, "x2")
    for k in range(DOUBLING_NAILS):
        y = W.bottom.y1 + (sill.y0 - W.bottom.y1) * (k + 1/2) / DOUBLING_NAILS
        step3 += W.into_side(middle, near, y, size=SMALL_GUN)
    pair_bottom = ((near.x0 + middle.x1) / 2, W.bottom.y1)
    step3 += callout(pair_bottom, "Clamp\nTIGHT", "below right" if near.center[0] < middle.center[0] else "below left", lead=0.7)
    step3.append((pair_bottom[0], pair_bottom[1], Circle(0.3, dy=0.1)))
    # Step 4: the door studs, headers and spacer: the headers clamped to the top plate and nailed from both sides; no nails into the studs' ends.
    header = extent([F.shape["door_header_lower"], F.shape["door_header_upper"], F.shape["door_spacer"]])
    step4 = callout((header.center[0], W.top.y1), "CLAMP", "above", lead=0.7)
    for fx in (1/6, 1/2, 5/6):
        x = header.x0 + fx * header.width
        step4 += [gun((x, W.top.y1), "above", SMALL_GUN), gun((x, header.y0), "below", SMALL_GUN)]
    for stud_ in (door_end, door_mid):
        step4 += crossed_out(W.through_top(stud_, size=SMALL_GUN)[0])
        step4 += crossed_out(W.through_bottom(stud_, size=SMALL_GUN)[0])
    step4 += callout((E["door_header_upper"].x1 - 2, E["door_header_upper"].center[1]), "2x4", "below right", lead=5/8)
    step4 += callout((E["door_spacer"].x1, E["door_spacer"].center[1]), '3/4" plywood', "right", lead=5/8)
    # Step 5: the three studs between the door and the window clamped and nailed together; the spacer blocks.
    trio = extent([F.shape["window_stud_near"], F.shape["middle_stud"], F.shape["door_stud_middle"]])
    step5 = []
    for k in range(DOUBLING_NAILS):
        y = W.bottom.y1 + (sill.y0 - W.bottom.y1) * (k + 1/2) / DOUBLING_NAILS
        step5 += W.into_side(near, middle, y, size=SMALL_GUN)
        y = W.bottom.y1 + (W.top.y0 - W.bottom.y1) * (k + 1/2) / DOUBLING_NAILS
        step5 += W.into_side(door_mid, middle, y, size=SMALL_GUN)
    for fy in (0.2, 0.6):
        step5 += callout((trio.x0 if door_mid.x0 < near.x0 else trio.x1, trio.y0 + fy * trio.height), "CLAMP",
                         "left" if door_mid.x0 < near.x0 else "right", lead=0.6)
    blocks = [E[n] for n in E if n.startswith("spacer_block_")]
    for b in blocks:
        for side, x in (("left", b.x0 - STUD), ("right", b.x1 + STUD)):
            step5.append(gun((x, b.center[1]), side, SMALL_GUN))
    step5 += callout(blocks[-1].top, "Clamp each block,\nnail twice from each side", "above", lead=1/2)
    # Step 6: the stretcher in the doorway; the door studs and the middle studs nailed through the plates.
    stretcher_ext = Extent(stretcher.shape().moved(END_TO_DRAWING * STRETCHER_AT))
    step6 = W.through_top(door_end, "x2") + W.through_top(door_mid, "x2") + W.through_bottom(door_end, "x2")
    trio_gun = gun((trio.center[0], W.bottom.y0), "below")  # (the three studs side by side: one gun for all)
    step6 += [trio_gun, next_to(trio_gun, "right", Label("x2 each stud,\nonly after the\nstretcher fits"))]
    step6 += callout(stretcher_ext.center, "Test with stretcher\nbefore nailing", "above right", lead=3/4)
    # Steps 7-11: the skin.
    wrap_ext = Extent(end_wall_skin(False, False))
    opening = Extent(END_TO_DRAWING * window_opening_flashing.shape())
    flange = Extent(END_TO_DRAWING * window_flange_flashing.shape())
    window = Extent(window_unit())
    plain_left, routed_left = end_panels(siding_panel_plain), end_panels(siding_panel_door)
    seam = max(Extent(plain_left[0]).x0, Extent(plain_left[1]).x0)  # between the panels
    step7 = callout((wrap_ext.center[0], wrap_ext.y1), "Align Tyvek roll to top of wall,\neven on both sides. Roll out Tyvek,\nand staple to frame.", "above left", lead=1/2)
    step8 = (callout(opening.right, "Apply peel-and-stick\nABOVE (not on) jig brackets\nto all 4 sides of window opening.", "right", lead=3/4, bold=("ABOVE",))
             + callout(opening.top_left, "Trim Tyvek flush with inside of window opening", "above left", lead=1/2))
    panel_centers = [Extent(p).center for p in plain_left]
    step9 = (callout((seam, wrap_ext.y1), "Exterior caulk between panels", "above right", lead=1/2)
             + [at((c[0], c[1] - 20), Label(f"PANEL {n}")) for n, c in enumerate(panel_centers, 1)]
             + [beside((door.center[0], W.bottom.y0), "below", Label("NO NAILS"), 1/8)]
             + callout((door.center[0] + 10, W.bottom.center[1]), "Three #8 (yellow)\ntemporary screws", "below right", lead=5/8)
             + [at((panel_centers[1][0], window.y0 - 12), Label("Use Panel Nails", bold=True))])
    step10 = (callout(door.top_right, 'Bore clearance hole 8" below top edge\nand 9 1/2" in from right edge,\nand rout out the door opening', "above right", lead=3/4)
              + callout(window.top_left, "Caulk around opening,\ninstall window unit", "above left", lead=3/4)
              + callout(flange.left, "Peel-and-stick first", "above left", lead=1/2)
              + callout(flange.top, "Peel-and-stick last", "above right", lead=1/2))
    step11 = callout(door.top, 'Nail sides and top of door opening,\nevery 8".  DO NOT nail across\nbottom of door opening.', "above", lead=1/2)

    framing = F.all
    tyv = lambda s: [(s, "bare", TYVEK)]
    window_parts = [(window_unit(), "outline")]
    rows = {}
    for step in order:
        rows[f"step_{step:02d}"] = (jig(framing) + ctx(F.before(step, order)) + new(F.placed(step)), [], [])
    rows["step_01"][2].extend(W.corners("end_stud_door", "end_stud_window"))
    rows["step_02"][2].extend(W.header_notes(headers, "sill", near, far))
    rows["step_03"][2].extend(step3)
    rows["step_04"][2].extend(step4)
    rows["step_05"][2].extend(step5)
    rows.update({
        "step_06": (ctx(framing), [(stretcher, END_TO_DRAWING * STRETCHER_AT)], step6),
        "step_07": (tyv(end_wall_skin(False, False)) + ctx(framing), [], step7),
        "step_08": (tyv(end_wall_skin(True, True)) + ctx(framing) + new([END_TO_DRAWING * window_opening_flashing.shape()]), [], step8),
        "step_09": (ctx(framing) + ctx(plain_left), [], step9),
        "step_10": (ctx(framing) + ctx(routed_left) + new([END_TO_DRAWING * window_flange_flashing.shape()]) + glass() + window_parts, [], step10),
        "step_11": (ctx(framing) + ctx(routed_left) + new([END_TO_DRAWING * window_flange_flashing.shape()]) + glass() + window_parts, [], step11),
    })
    figs = table(FRONT_MD, rows)
    corner_x = whole.x1 - whole.width / 4  # (the labels off to one side, out of the callouts' way)
    for fig in figs:
        fig.notes += [beside((corner_x, whole.y1), "above", Label("Top", TITLE), 1),
                      beside((corner_x, whole.y0), "below", Label("Bottom", TITLE), 1),
                      title(whole.bottom, f"Step {int(fig.name[-2:])}", gap=1.4)]
    return figs


def rear_wall_figures(scale):
    W = EndWall(rear_wall_members(), scale)
    E, F, whole = W.E, W.F, W.whole
    order = ["1", "2", "3", "4", "4b"]
    headers = ["header_1", "header_2", "header_3"]
    near, far, middle, sill = E["window_stud_near"], E["window_stud_far"], E["middle_stud"], E["sill"]
    ac_stud, ac_header, ac_side, ac_sill = E["ac_stud"], E["ac_header"], E["ac_side_block"], E["ac_sill"]
    toward_ac = -1 if ac_stud.center[0] < near.center[0] else 1  # which way along the drawing the A/C end is

    # Step 3: the window studs nailed top and bottom; the next stud clamped and nailed to the window's below the window.
    step3 = []
    for stud_ in (far, near):
        step3 += W.through_top(stud_, size=1) + W.through_bottom(stud_, size=1)
    step3.append(beside(((far.center[0] + near.center[0]) / 2, W.top.y1), "above", Label("x2 into both studs"), 0.6 + GAP))
    step3.append(beside(((far.center[0] + near.center[0]) / 2, W.bottom.y0), "below", Label("x2 into both studs"), 0.6 + GAP))
    step3 += W.through_top(middle, "x2") + W.through_bottom(middle, "x2")
    for k in range(DOUBLING_NAILS):
        y = W.bottom.y1 + (sill.y0 - W.bottom.y1) * (k + 1/2) / DOUBLING_NAILS
        step3 += W.into_side(middle, near, y, "x1", size=SMALL_GUN)
    step3 += callout(((near.x0 + middle.x1) / 2 if near.x0 > middle.x0 else (middle.x0 + near.x1) / 2, (W.bottom.y1 + sill.y0) / 2), "CLAMP",
                     "left" if toward_ac < 0 else "right", lead=0.7)
    # Step 4: the A/C opening's stud and blocks, in order: (1) the straight
    # stud, nailed through the plates; (2) the header block against the top
    # plate, clamped and nailed through it; (3) the side block against the
    # double stud, clamped and nailed to it; (4) the sill block, nailed up
    # into the side block and through the stud.
    edge = (ac_stud.x0 if toward_ac < 0 else ac_stud.x1, ac_stud.center[1] - 10)  # the stud's outer face
    one = (edge[0] + toward_ac * 8, edge[1])
    step4 = circled(one, "1") + [pointer(edge, (one[0] - edge[0]) * scale + toward_ac * -CIRCLED, 0)]
    step4 += W.through_top(ac_stud, "x2", label_side="right" if toward_ac > 0 else "left")
    step4 += W.through_bottom(ac_stud, "x2", label_side="right" if toward_ac > 0 else "left")
    inner = ac_header.x0 if toward_ac < 0 else ac_header.x1  # the opening's side at the A/C stud
    step4 += circled((inner - toward_ac * 4, ac_header.y0 - 4), "2")
    step4 += W.through_top(ac_header, "x2", size=SMALL_GUN, label_side="left" if toward_ac > 0 else "right")
    step4 += circled((inner - toward_ac * 4, ac_side.y0 + 3), "3")
    double = near if abs(ac_side.center[0] - near.center[0]) < abs(ac_side.center[0] - ac_stud.center[0]) else ac_stud
    step4 += W.into_side(ac_side, double, ac_side.center[1], "x2", size=SMALL_GUN)
    step4 += callout((near.x1 if toward_ac < 0 else near.x0, ac_side.center[1]), "CLAMP", "right" if toward_ac < 0 else "left", lead=1/2)
    step4 += circled((ac_sill.center[0], ac_sill.y0 - 8), "4")
    step4 += counted((ac_side.center[0], ac_sill.y0), "below", "x2", SMALL_GUN, "right" if toward_ac < 0 else "left")
    step4 += W.into_side(ac_stud, ac_sill, ac_sill.center[1], "x2", size=SMALL_GUN)
    # Step 4b: the blocks under the A/C sill, each nailed to its neighbor.
    under = [E[f"ac_under_{k}"] for k in (1, 2, 3)]
    step4b = W.into_side(ac_stud, under[0], under[0].center[1], "x2 into\neach block", size=SMALL_GUN)
    step4b += W.into_side(middle, under[2], under[2].center[1], "x2", size=SMALL_GUN)
    step4b += W.into_side(under[1], under[2], under[1].center[1], "x2", size=SMALL_GUN)
    # Steps 5-8: the skin.
    wrap_ext = Extent(end_wall_skin(False, False))
    opening = Extent(END_TO_DRAWING * window_opening_flashing.shape())
    flange = Extent(END_TO_DRAWING * window_flange_flashing.shape())
    window = Extent(window_unit())
    panels = end_panels(siding_panel_plain)
    seam = max(Extent(panels[0]).x0, Extent(panels[1]).x0)
    tyvek_label = at((wrap_ext.center[0], wrap_ext.y0 + 0.4 * wrap_ext.height), Label("TYVEK"))
    step5 = callout((wrap_ext.center[0], wrap_ext.y1), "Align Tyvek roll to top of wall, even on both sides.\nRoll out Tyvek, and staple to frame.", "above left", lead=1/2) + [tyvek_label]
    step6 = (callout(opening.right, "Apply peel-and-stick\nABOVE (not on) jig brackets\nto all 4 sides of window opening.", "right", lead=3/4, bold=("ABOVE",))
             + callout(opening.top_left, "Trim Tyvek flush with inside of window opening", "above left", lead=1/2) + [tyvek_label])
    panel_centers = [Extent(p).center for p in panels]
    step7 = (callout((seam, wrap_ext.y1), "Exterior caulk between panels", "above right", lead=1/2)
             + [at(c, Label(f"PANEL {n}")) for n, c in enumerate(panel_centers, 1)]
             + callout((ac_header.center[0], wrap_ext.y1), "Panel nails, using A/C template", "above left", lead=1/2)
             + [at((panel_centers[0][0], W.bottom.y1 + 15), Label("Use Panel Nails", bold=True))])
    step8 = (callout(window.top_left, "Install window unit", "above left", lead=3/4)
             + callout(flange.left, "Peel-and-stick first", "above left", lead=1/2)
             + callout(flange.top, "Peel-and-stick last,\noverlapping side strips", "above right", lead=1/2))

    framing = F.all
    tyv = lambda s: [(s, "bare", TYVEK)]
    window_parts = [(window_unit(), "outline")]
    rows = {}
    for step in order:
        name = "step_04b" if step == "4b" else f"step_{int(step):02d}"
        rows[name] = (jig(framing) + ctx(F.before(step, order)) + new(F.placed(step)), [], [])
    rows["step_01"][2].extend(W.corners("end_stud_ac", "end_stud_window"))
    rows["step_02"][2].extend(W.header_notes(headers, "sill", near, far))
    rows["step_03"][2].extend(step3)
    rows["step_04"][2].extend(step4)
    rows["step_04b"][2].extend(step4b)
    rows.update({
        "step_05": (tyv(end_wall_skin(False, False)) + ctx(framing), [], step5),
        "step_06": (tyv(end_wall_skin(True, False)) + ctx(framing) + new([END_TO_DRAWING * window_opening_flashing.shape()]), [], step6),
        "step_07": (ctx(framing) + ctx(panels), [], step7),
        "step_08": (ctx(framing) + ctx(panels) + new([END_TO_DRAWING * window_flange_flashing.shape()]) + glass() + window_parts, [], step8),
    })
    figs = table(REAR_MD, rows)
    for fig in figs:
        fig.notes.append(title(whole.bottom, f"Step {fig.name[5:].lstrip('0')}\nRear Wall", gap=1))
    return figs


def figures(scale=1/20, only=None):
    return (side_wall_figures(1, 0, scale) + side_wall_figures(3, 2, scale)
            + front_wall_figures(scale) + rear_wall_figures(scale))
