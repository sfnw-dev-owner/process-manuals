"""Exterior_Trim/exterior_trim.md figures: the corner boards at the rear-left
corner (in isometric, the new board's back laid flat beside it, and a
section at the top of the corner), the window trim seen from outside, and
the gables (front and rear triangles) step by step."""

from build123d import Box, Plane, Pos, Rot
from build123d import scale as scaled

from model.common import CORNER, key
from model.dimensions import PLATFORM_LENGTH, SIDING_HEIGHT
from model.exterior_trim import (
    FRONT_WALL_IN_HOUSE, REAR_WALL_IN_HOUSE, RO_H, RO_W, TRIM_W, WINDOW_UNIT_INSET,
    alignment_block, alignment_block_at, corner_board_1, corner_board_2, corner_frame, rafters_in_house,
    window_side_trim, window_top_trim, window_trim, window_trim_in_wall, window_trim_nails, window_trim_parts,
)
from model.notes import CIRCLED, SMALL, TITLE, Circle, Label, arc, at, beside, callout, circled, crossed_box, pointer, title
from model.platform import DECK
from model.roof import (
    RAFTER_Y, RIDGE_BOARD_BOTTOM, RIDGE_X, ROOF_Y, SLOPE, TAIL_U, TIP_X, gable_siding_large,
    gable_siding_small, gable_wrap, rafter, ridge_board, structural_triangle, z_flashing,
)
from model.walls import WALL_DEPTH, WALL_HEIGHT, front_wall_skin, rear_wall_skin, side_wall_skin, window_unit_at

from . import GRAY, TYVEK, Extent, Figure, camera, extent, table, xy

MD = "Exterior_Trim/exterior_trim.md"
PAPER_NOTES = True

BACK_CORNER = (0, 0)  # the corner the corner-board figures show: rear, left
FLAT_BOARD_OFF = 40  # the new board's back, laid flat this far left of the building


# ── corner boards: the rear-left corner in isometric ───────────────────────

def corner_figures(scale):
    side_face, ox, end_face, oy = corner_frame(BACK_CORNER)
    # looking from the rear, left and above, the bottom of the siding at the corner at the origin
    iso = camera((-1, -1, 1)) * Pos(-side_face, -end_face, -(DECK + WALL_HEIGHT - SIDING_HEIGHT))
    comp, loc, mods, _ = window_unit_at()
    side = Pos(WALL_DEPTH, 0, DECK) * Rot(Z=90) * side_wall_skin.shape()
    near = Pos(-10, -10, -10) * Box(40, 58, 200, align=CORNER)  # first panel of the side wall
    tails = Pos(-10, -10, -10) * Box(40, 80, 200, align=CORNER)  # rafter tails: run past the drawing's top
    building = [
        REAR_WALL_IN_HOUSE * rear_wall_skin.shape(),
        REAR_WALL_IN_HOUSE * loc * comp.shape(frozenset(), key(mods)),
        REAR_WALL_IN_HOUSE * window_trim_in_wall() * window_trim.shape(),
        side & near,
        *[r & tails for r in rafters_in_house()[:3]],
    ]
    b1, b2 = corner_board_1(BACK_CORNER).shape(), corner_board_2(BACK_CORNER).shape()
    top = b1.bounding_box().max.Z
    block = alignment_block_at(BACK_CORNER)
    on_wall = Extent(iso * b1)
    building_ext = extent([iso * s for s in building] + [iso * b1])
    cutoff = on_wall.y1 + 24  # the drawing's top edge: the rafters run on past it
    clip = (building_ext.x0 - 1e3, building_ext.y0 - 1e3, building_ext.x1 + 1e3, cutoff)

    def flat_board(board, direction, k):
        """A board's back laid flat, seen along `direction`, at k times size,
        placed left of the building."""
        seen = scaled(camera(direction) * board, by=k)
        parts = sorted(seen.solids(), key=lambda s: -s.volume)
        bb = parts[0].bounding_box()
        move = Pos(building_ext.x0 - FLAT_BOARD_OFF - bb.max.X, building_ext.y0 - bb.min.Y + 4, 0)
        return move * seen, Extent(move * parts[0])

    k1 = 3  # Board #1's top, enlarged, so its notch for the rafter shows
    upper = Pos(-50, -50, top - 30) * Box(100, 100, 100, align=CORNER)
    flat1, flat1_ext = flat_board(b1 & upper, (1, 0, 0), k1)
    flat2, flat2_ext = flat_board(b2, (0, 1, 0), 1)

    # The section at the top of the corner, across the side wall through the
    # double rafter, seen from outside, at twice size, right of the building.
    def section():
        k = 2
        cut_x = side_face - 0.375  # through the middle of Board #1
        slab = Pos(cut_x - 0.005, -20, top - 20) * Box(0.01, 40, 40, align=CORNER)
        window = Pos(-20, -20, top - 16) * Box(40, 40, 30, align=CORNER)
        view = camera((-1, 0, 0))  # right = -Y
        pieces = [(view * scaled(b1 & window, k), "outline"), (view * scaled(b2 & window, k), "outline"),
                  (view * scaled(b1 & window, k), "bare", "laid")]
        sections = [view * scaled(r & slab, k) for r in rafters_in_house()[1:3]]
        ext = extent([p[0] for p in pieces] + sections)
        move = Pos(building_ext.x1 + 16 - ext.x0, building_ext.y0 - ext.y0, 0)
        parts = [(move * s, *rest) for s, *rest in pieces] + [(move * s, "outline") for s in sections]
        boards = [Extent(move * p[0]) for p in pieces[:2]]
        rafters_ = [Extent(move * s) for s in sections]
        notes = [(e.x0, e.y0, crossed_box(e.width * scale, e.height * scale)) for e in rafters_]
        notes += callout(rafters_[0].top, "Double Rafter", "above right", lead=3/8)
        notes += callout(boards[0].point(0.5, 0.2), "Board #1", "below left", lead=1/2)
        notes += callout(boards[1].point(1, 0.6), "Board #2", "right", lead=1/2)
        notes += callout(boards[1].point(1, 0.2), "Surface of end wall", "below right", lead=1/2)
        return parts, notes

    section_parts, section_notes = section()
    def flip(ext_):
        """The arrow from the flat board's bottom to the corner, and "Flip" under it."""
        r = (on_wall.x0 - ext_.x1) / 2
        center = ((ext_.x1 + on_wall.x0) / 2, ext_.y0 - 2)
        return arc(center, r, 180, 360, scale) + [beside((center[0], center[1] - r), "below", Label("Flip", TITLE), 1/8)]

    step1 = [
        *callout(flat1_ext.point(0.5, 0.9), "Cutout for rafter", "above left", lead=1/2),
        *callout(flat1_ext.point(0.55, 0.5), "Caulk line", "left", lead=1/2),
        *callout(Extent(iso * alignment_block.shape().moved(block)).right, "Alignment Block", "above right", lead=5/8),
        *callout(flat1_ext.point(0.5, 0.0), "Board #1", "below left", lead=1/2),
        *callout(flat1_ext.point(0.0, 0.3), "Corner Edge", "left", lead=1/2),
        *flip(flat1_ext),
        *section_notes,
    ]
    step2 = [
        *callout(flat2_ext.point(0.7, 0.5), "Caulk", "right", lead=3/8),
        *callout(flat2_ext.point(0.5, 0.0), "Board #2", "below left", lead=1/2),
        *callout(flat2_ext.point(1.0, 0.8), "Corner Edge", "above right", lead=1/2),
        *flip(flat2_ext),
    ]
    rows = {}
    for step, fig_name, new, on, flat, notes in ((1, "corners_1", b1, [b1], flat1, step1), (2, "corners_2", b2, [b1, b2], flat2, step2)):
        parts = [(iso * s, "hlr_thin") for s in building + on] + [(iso * new, "bare", "laid"), (flat, "outline")]
        if step == 1:
            parts += section_parts
        tools = [(alignment_block, iso * block)] if step == 1 else []
        rows[fig_name] = (parts, tools, notes + [title(building_ext.bottom, f"Step {step}", gap=1/2)])
    figs = table(MD, rows, tools_style=("hlr_thin", "laid"))
    for fig in figs:
        fig.clip = clip
    return figs


# ── window trim: the window seen from outside, in the window-trim frame ────

def window_figure(fig_name, view, scale, extra=(), clip=None):
    to_trim = window_trim_in_wall().inverse()
    to_drawing = Pos(-WINDOW_UNIT_INSET, -WINDOW_UNIT_INSET, 0)
    comp, loc, mods, _ = window_unit_at()
    unit = to_trim * loc * comp.shape(frozenset(), key(mods))
    boards = {name: Extent(to_drawing * loc_ * c.shape(frozenset(), key(m))) for name, (c, loc_, m) in window_trim_parts().items()}
    parts = [(to_drawing * s, "hlr") for s in (unit, window_trim.shape())]
    for s in extra:
        parts.append((to_drawing * to_trim * s, "hlr"))
    notes = [at(xy(to_drawing * l), Circle(1/60, fill=(0, 0, 0))) for l in window_trim_nails()]
    top, left, right, bottom = boards["top"], boards["left"], boards["right"], boards["bottom"]
    notes += callout(top.point(0.15, 1), '1/2" overhang', "above left", lead=3/8)
    # the pieces numbered in the order they go on, each number off a corner of its piece
    numbers = {"rear_window": (left, right, top, bottom), "front_window": (top, left, right, bottom)}[view]
    off = 0.4 / scale  # the number this far (drawing inches) off its corner
    corners = {id(left): (left.bottom_left, (-off, -off)), id(right): (right.point(1, 0.85), (off, 0)),
               id(top): (top.top_right, (off, off)), id(bottom): (bottom.point(0.3, 0), (0, -off))}
    for n, board in enumerate(numbers, 1):
        p, (dx, dy) = corners[id(board)]
        c = (p[0] + dx, p[1] + dy)
        notes += circled(c, str(n)) + [pointer(p, (c[0] - p[0]) * scale, (c[1] - p[1]) * scale)]
    notes += callout(bottom.point(0.7, 0), "Measure and cut to fit\nDO NOT CAULK", "below right", lead=1/2)
    if view == "rear_window":  # the precut boards, turned over to show the caulk
        side_, top_ = window_side_trim.shape(), window_top_trim.shape()
        mirrored = window_side_trim.shape(frozenset(), key(['mirror']))
        turned = [Pos(left.x0 - TRIM_W - 10, left.y0, 0) * Rot(Y=180) * Pos(TRIM_W, 0, 0) * side_,
                  Pos(right.x1 + 10, right.y0, 0) * Rot(Y=180) * Pos(TRIM_W, 0, 0) * mirrored,
                  Pos(top.x0, top.y1 + 8 + TRIM_W, 0) * Rot(X=180) * top_]
        parts += [(s, "hlr_thin") for s in turned]
        for b, over in ((left, Extent(turned[0])), (right, Extent(turned[1]))):
            r = abs(b.center[0] - over.center[0]) / 2
            center = ((b.center[0] + over.center[0]) / 2, b.center[1])
            notes += arc(center, r, 180, 360, scale) if b is left else arc(center, r, 0, 180, scale)
            notes.append(at((center[0], center[1] + (-r - 4 if b is left else r + 4)), Label("Flip")))
        over = Extent(turned[2])
        center = (top.x1 + 12, (top.center[1] + over.center[1]) / 2)
        r = (over.center[1] - top.center[1]) / 2
        notes += arc(center, r, 90, -90, scale) + [at((center[0] + r + 6, center[1]), Label("Flip"))]
        notes += callout(top.point(0.6, 1), "30° bevel", "above left", lead=3/8)
        whole = extent([p[0] for p in parts])
        notes.append(beside(whole.bottom, "below", Label('Note: nail 1½" in from each end each board'), 0.8))
    else:
        whole = extent([top, left, right, bottom])
        notes.append(beside((right.x1 + 4, right.y0 - 8), "right", Label("Door Jamb"), 1/4))
    name = {"rear_window": "Rear Window Trim", "front_window": "Front Window Trim"}[view]
    notes.append(title(whole.bottom, name, gap=1.3 if view == "rear_window" else 1))
    return Figure(MD, fig_name, parts, notes, clip=clip)


DOOR_SHOWN = 12  # the front window's figure shows the door's casing this far beyond the window trim


def window_figures(scale):
    around = (-TRIM_W - DOOR_SHOWN, -TRIM_W - DOOR_SHOWN, RO_W + TRIM_W + DOOR_SHOWN, RO_H + TRIM_W + DOOR_SHOWN)
    return [window_figure("rear_window", "rear_window", scale),
            window_figure("front_window", "front_window", scale, front_door(), clip=around)]


def front_door():
    """The door (and its frame) beside the front window, in the front wall's
    frame, as the house puts it."""
    import importlib
    from . import placed
    H = importlib.import_module("model.house")
    comp, loc, mods, _ = placed(H.house, "door_assembly")
    # (just the casing's corner shows: no door panels there)
    return [FRONT_WALL_IN_HOUSE.inverse() * loc * comp.shape(frozenset({"Door Outside"}), key(mods))]


# ── triangles: the front gable, in the roof's frame (Z = 0 at the wall top) ──

FRONT = camera((0, 1, 0))  # the front of the house, seen from outside
SIDING_BAND = 24  # how much of the wall's siding shows under the gable


def plain_board(shape):
    """The shape with any notch along its length filled (a rafter without
    its birdsmouth: the end rafters show as plain boards)."""
    bb = shape.bounding_box()
    hull = Pos(bb.min.X, bb.min.Y, bb.min.Z) * Box(bb.size.X, bb.size.Y, bb.size.Z, align=CORNER)
    axis = max(range(3), key=lambda i: (bb.size.X, bb.size.Y, bb.size.Z)[i])
    lo, hi = (bb.min.X, bb.min.Y, bb.min.Z)[axis], (bb.max.X, bb.max.Y, bb.max.Z)[axis]
    for s in (hull - shape).solids():
        b = s.bounding_box()
        if (b.min.X, b.min.Y, b.min.Z)[axis] > lo + 1 and (b.max.X, b.max.Y, b.max.Z)[axis] < hi - 1:  # not an end cut
            shape = shape + s
    return shape


def front_gable_parts():
    """{name: shape} of what shows at the front gable, in the roof frame."""
    end = RAFTER_Y[-1]
    left_rafter = SLOPE * Pos(TAIL_U, end, 0) * plain_board(rafter.shape())
    left_ridge = Pos(TIP_X, ROOF_Y, RIDGE_BOARD_BOTTOM) * ridge_board.shape()
    mirror_x = lambda s: Pos(2 * RIDGE_X, 0, 0) * s.mirror(Plane.YZ)
    # the top of the existing siding, as a plain slab (the door and window
    # openings would only clutter it), as wide as the gable above it
    gable = Pos(RIDGE_X, PLATFORM_LENGTH, 0)
    wall = (Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, -WALL_HEIGHT) * front_wall_skin.shape()).bounding_box()
    wrap = (gable * gable_wrap.shape()).bounding_box()
    slab = Pos(wrap.min.X, wall.min.Y, -SIDING_BAND) * Box(wrap.size.X, wall.size.Y, SIDING_BAND, align=CORNER)
    return {
        "rafters": [left_rafter, mirror_x(left_rafter)],
        "ridge": [left_ridge, mirror_x(left_ridge)],
        "triangle": [Pos(RIDGE_X, PLATFORM_LENGTH - WALL_DEPTH, 0) * structural_triangle.shape()],
        "wall": [slab],
        "wrap": [gable * gable_wrap.shape()],
        "flashing": [gable * z_flashing.shape()],
        "large": [gable * gable_siding_large.shape()],
        "small": [gable * gable_siding_small.shape()],
    }


def triangle_figures(scale):
    parts = front_gable_parts()
    views = {  # view -> fills
        "tyvek": [("wrap", TYVEK)],
        "z_flashing": [("wrap", TYVEK), ("flashing", GRAY)],
        "siding_large": [("wrap", TYVEK), ("flashing", GRAY), ("large", (0, 0, 0))],
        "siding_small": [("wrap", TYVEK), ("flashing", GRAY), ("large", (0, 0, 0)), ("small", (0, 0, 0))],
    }
    gable_height = (FRONT * Pos(0, 0, RIDGE_BOARD_BOTTOM)).position.Y + 12
    rows = {}
    for fig_name, pair in (("triangles_1_2", ("tyvek", "z_flashing")), ("triangles_3_4", ("siding_large", "siding_small"))):
        fig_parts, notes = [], []
        for k, view in enumerate(pair):
            fills = views[view]
            to_drawing = Pos(0, -k * (gable_height + SIDING_BAND + 10), 0) * FRONT * Pos(-RIDGE_X, 0, 0)  # the second view under the first
            shown = {n for n, _ in fills}
            ext = {}
            for name in ("rafters", "ridge", "triangle", "wall", "wrap", "flashing", "large", "small"):
                if name in ("wrap", "flashing", "large", "small") and name not in shown:
                    continue
                shapes = [to_drawing * s for s in parts[name]]
                ext[name] = extent(shapes)
                for s in shapes:
                    if name == "wall":  # the siding runs on below the drawing: no bottom edge
                        bb = s.bounding_box()
                        # (and once the Z-flashing is on, its lip covers the siding's top edge)
                        top = bb.max.Y - 0.01 if "flashing" in shown else bb.max.Y + 1
                        fig_parts.append((s, "outline", None, (bb.min.X - 1, bb.min.Y + 0.01, bb.max.X + 1, top)))
                    else:
                        fig_parts.append((s, "hlr_thin"))
            for name, color in fills:
                fig_parts += [(to_drawing * s, "bare", color) for s in parts[name]]
            notes.append(at(ext["wall"].center, Label("Existing T1-11 Siding")))
            if view == "tyvek":
                notes.append(at(ext["wrap"].point(0.5, 0.4), Label("Tyvek")))
            elif view == "z_flashing":
                notes += callout(ext["flashing"].point(0.65, 0.5), "Z-flashing", "below right", lead=3/8)
            else:  # the siding pieces, numbered on the band under them
                big = (ext["wall"].point(0.8, 0.5), ext["large"].point(0.7, 0.05))
                notes += circled(big[0], "3.1", height=SMALL) + [pointer(big[1], (big[0][0] - big[1][0]) * scale, (big[0][1] - big[1][1]) * scale + CIRCLED)]
                if view == "siding_small":
                    small = (ext["wall"].point(0.2, 0.5), ext["small"].point(0.5, 0.2))
                    notes += circled(small[0], "3.2", height=SMALL) + [pointer(small[1], (small[0][0] - small[1][0]) * scale, (small[0][1] - small[1][1]) * scale + CIRCLED)]
        whole = extent([p[0] for p in fig_parts])
        notes.append(title(whole.bottom, "Front & Rear Triangles", gap=1/2))
        rows[fig_name] = (fig_parts, [], notes)
    return table(MD, rows)


def figures(scale=1/20, only=None):
    return corner_figures(scale) + window_figures(scale) + triangle_figures(scale)
