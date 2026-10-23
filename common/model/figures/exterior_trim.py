"""Exterior_Trim/exterior_trim.md figures."""

from build123d import Box, Plane, Pos, Rot

from model.dimensions import PLATFORM_LENGTH
from model.roof import (
    GABLE_VIEWS, RAFTER_Y, RIDGE_BOARD_BOTTOM, RIDGE_X, ROOF_Y, SLOPE, TAIL_U, TIP_X, gable_siding_large,
    gable_siding_small, gable_skin, gable_wrap, rafter, ridge_board, structural_triangle, z_flashing,
)
from model.walls import DOOR_HEADER_Z, WALL_DEPTH, WALL_HEIGHT, front_wall_skin
from model.dimensions import SIDING_HEIGHT
from model.common import CORNER

from . import GRAY, TYVEK, Figure, camera, figure_names, placed, placed_notes, title

MD = "Exterior_Trim/exterior_trim.md"
FRONT = camera((0, 1, 0))  # the front of the house, seen from outside


# ── triangles: the front gable, in the roof's frame (Z = 0 at the wall top) ──

def plain_board(shape):
    """The shape with any notch along its length filled (a rafter without
    its birdsmouth: the drawing showed the end rafters as plain boards)."""
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
    # openings would only clutter it), as wide as the gable above it (the
    # drawing's siding ended at the flashing's ends, not at the wall's)
    band = 24
    gable = Pos(RIDGE_X, PLATFORM_LENGTH, 0)
    wall = (Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, -WALL_HEIGHT) * front_wall_skin.shape()).bounding_box()
    wrap = (gable * gable_wrap.shape()).bounding_box()
    slab = Pos(wrap.min.X, wall.min.Y, -band) * Box(wrap.size.X, wall.size.Y, band, align=CORNER)
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


def triangle_figures():
    parts = front_gable_parts()
    views = {  # view -> (drawing position of the gable's center at the wall top, fills)
        "tyvek": ((0, 18), [("wrap", TYVEK)]),
        "z_flashing": ((0.15, -59.53), [("wrap", TYVEK), ("flashing", GRAY)]),
        "siding_large": ((0, 18), [("wrap", TYVEK), ("flashing", GRAY), ("large", (0, 0, 0))]),
        "siding_small": ((0.15, -59.53), [("wrap", TYVEK), ("flashing", GRAY), ("large", (0, 0, 0)), ("small", (0, 0, 0))]),
    }
    out = []
    for fig_name, pair in zip(figure_names(MD)[4:6], (("tyvek", "z_flashing"), ("siding_large", "siding_small"))):
        fig_parts, notes = [], []
        for view in pair:
            (x, y), fills = views[view]
            to_drawing = Pos(x, y, 0) * FRONT * Pos(-RIDGE_X, 0, 0)
            shown = {n for n, _ in fills}
            for name in ("rafters", "ridge", "triangle", "wall", "wrap", "flashing", "large", "small"):
                if name in ("wrap", "flashing", "large", "small") and name not in shown:
                    continue
                for s in parts[name]:
                    if name == "wall":  # the siding runs on below the drawing: no bottom edge
                        bb = (to_drawing * s).bounding_box()
                        # (and once the Z-flashing is on, its lip covers the siding's top edge)
                        top = bb.max.Y - 0.01 if "flashing" in shown else bb.max.Y + 1
                        fig_parts.append((to_drawing * s, "outline", None, (bb.min.X - 1, bb.min.Y + 0.01, bb.max.X + 1, top)))
                    else:
                        fig_parts.append((to_drawing * s, "hlr_thin"))
            for name, color in fills:
                fig_parts += [(to_drawing * s, "bare", color) for s in parts[name]]
            notes += placed_notes(to_drawing * Pos(RIDGE_X, PLATFORM_LENGTH, 0), gable_skin,
                                  {f"manual:exterior_trim:{view}"})
        notes.append(title("Front & Rear Triangles", -25.69, -110.9, 4))
        out.append(Figure(MD, fig_name, fig_parts, notes))
    return out




# ── window trim: the window seen from outside, in the window-trim frame ──

def window_figure(fig_name, view, extra=(), clip=None):
    from model.exterior_trim import (
        WINDOW_TOP_TRIM, WINDOW_UNIT_INSET, window_side_trim, window_top_trim, window_trim,
        window_trim_in_wall,
    )
    from model.common import key
    from model.walls import window_unit_at
    to_trim = window_trim_in_wall().inverse()
    to_drawing = Pos(-WINDOW_UNIT_INSET, -WINDOW_UNIT_INSET, 0)
    comp, loc, mods, _ = window_unit_at()
    unit = to_trim * loc * comp.shape(frozenset(), key(mods))
    parts = [(to_drawing * s, "hlr") for s in (unit, window_trim.shape())]
    for s in extra:
        parts.append((to_drawing * to_trim * s, "hlr"))
    if view == "rear_window":  # the precut boards, turned over to show the caulk
        side, top = window_side_trim.shape(), window_top_trim.shape()
        mirrored = window_side_trim.shape(frozenset(), key(['mirror']))
        parts += [
            (Pos(-14.892, -11.136, 0) * Rot(Y=180) * side, "hlr_thin"),
            (Pos(37.805, -11.136, 0) * Rot(Y=180) * mirrored, "hlr_thin"),
            (Pos(-4.25, 48.75, 0) * Rot(X=180) * top, "hlr_thin"),
        ]
    notes = placed_notes(to_drawing, window_trim, {f"manual:exterior_trim:{view}"})
    name = {"rear_window": "Rear Window Trim", "front_window": "Front Window Trim"}[view]
    notes.append(title(name, -5.07 if view == "rear_window" else -5, -26.13 if view == "rear_window" else -30, 3))
    return Figure(MD, fig_name, parts, notes, clip=clip)


# The front window's drawing shows only the corner of the door's casing
# beside it: its lines stop this far below the window's opening and this far
# right of it (where the drawing it replaces had them end).
DOOR_SHOWN = (-1e3, -18, 44.5, 1e3)


def window_figures():
    figs = figure_names(MD)
    return [window_figure(figs[2], "rear_window"),
            window_figure(figs[3], "front_window", front_door(), clip=DOOR_SHOWN)]


def figures():
    return corner_figures() + window_figures() + triangle_figures()


def front_door():
    """The door (and its frame) beside the front window, in the front wall's
    frame, as the house puts it."""
    import importlib
    from model.common import key
    from model.exterior_trim import FRONT_WALL_IN_HOUSE
    H = importlib.import_module("model.house")
    comp, loc, mods, _ = placed(H.house, "door_assembly")
    # (just the casing's corner shows: the drawing had no door panels there)
    return [FRONT_WALL_IN_HOUSE.inverse() * loc * comp.shape(frozenset({"Door Outside"}), key(mods))]


# ── corner boards: the rear-left corner in isometric ──

def fit(shape, x0, y0, sx, sy):
    """The shape scaled (sx, sy) in the drawing, its lower-left at (x0, y0)."""
    from build123d import scale
    s = scale(shape, by=(sx, sy, 1))
    bb = s.bounding_box()
    return Pos(x0 - bb.min.X, y0 - bb.min.Y, 0) * s


def corner_figures():
    from build123d import Box, Location
    from model.common import key
    from model.exterior_trim import (
        BACK_CORNER, BACK_CORNER_DRAWING, REAR_WALL_IN_HOUSE, corner_board_1, corner_board_2,
        external_trim, rafters_in_house, window_trim, window_trim_in_wall,
    )
    from model.platform import DECK
    from model.walls import rear_wall_skin, side_wall_skin, window_unit_at
    from model.notes import Leader
    from . import optional_parts
    iso = BACK_CORNER_DRAWING
    comp, loc, mods, _ = window_unit_at()
    side = Pos(WALL_DEPTH, 0, DECK) * Rot(Z=90) * side_wall_skin.shape()
    near = Pos(-10, -10, -10) * Box(40, 58, 200, align=CORNER)  # first panel of the side wall
    tails = Pos(-10, -10, -10) * Box(40, 80, 200, align=CORNER)  # rafter tails: run past the drawing's top
    TOP = 119.13  # the drawing's top edge, where the rafters are cut off (back_corner.dxf)
    building = [
        REAR_WALL_IN_HOUSE * rear_wall_skin.shape(),
        REAR_WALL_IN_HOUSE * loc * comp.shape(frozenset(), key(mods)),
        REAR_WALL_IN_HOUSE * window_trim_in_wall() * window_trim.shape(),
        side & near,
        *[r & tails for r in rafters_in_house()[:3]],
    ]
    b1, b2 = corner_board_1(BACK_CORNER).shape(), corner_board_2(BACK_CORNER).shape()
    figs = figure_names(MD)
    out = []
    for step, fig_name in ((1, figs[0]), (2, figs[1])):
        shown = {f"manual:exterior_trim:corners_{step}"}
        new = b1 if step == 1 else b2
        on = [b1] if step == 1 else [b1, b2]
        parts = [(iso * s, "hlr_thin") for s in building + on]
        parts += [(iso * new, "bare", "laid")]
        parts += optional_parts(iso, external_trim, shown, "hlr_thin")
        # the board's back, laid flat beside the corner (drawn wide, as in the DXF)
        if step == 1:  # just the top of Board #1, enlarged, so its notch for the rafter shows
            k = 13 / 3.5
            top = b1.bounding_box().max.Z
            upper = Pos(-50, -50, top - 69.88 / k) * Box(100, 100, 100, align=CORNER)
            flat = fit(camera((1, 0, 0)) * (b1 & upper), -92.65, 4.92, k, k)
        else:
            # (the board is drawn squashed, as the DXF drew it, so the bead
            # is redrawn with its insets alike on the page)
            sx, sy = 13 / 3.5, 60 / SIDING_HEIGHT
            flat = flat_bead(fit(camera((0, 1, 0)) * b2, -90, -10, sx, sy), sx)
        parts.append((flat, "outline"))
        notes = placed_notes(iso, external_trim, shown)
        if step == 1:
            parts_d, notes_d = corner_detail()
            parts += parts_d
            notes += notes_d
        notes.append(title(f"Step {step}", 23.76 if step == 1 else 30, -15.91 if step == 1 else -20, 5))
        out.append(Figure(MD, fig_name, parts, notes, clip=(-1e3, -1e3, 1e3, TOP)))
    return out


def flat_bead(flat, k):
    """A flat-laid board (the largest solid) with its caulk bead redrawn
    along the same edges, inset CAULK_INSET * k from them on the page."""
    from build123d import Compound
    from model.exterior_trim import CAULK_BEAD, CAULK_INSET
    board, *bead = sorted(flat.solids(), key=lambda s: -s.volume)
    bb = board.bounding_box()
    # which edge the bead runs up: where it is in the board's lower half
    lower = Pos(bb.min.X - 1, bb.min.Y - 1, bb.min.Z - 1) * Box(bb.size.X + 2, bb.size.Y / 2, bb.size.Z + 2, align=CORNER)
    cx = sum((s & lower).bounding_box().center().X for s in bead) / len(bead)
    i, w = CAULK_INSET * k, CAULK_BEAD[0] * k
    x = bb.min.X + i if cx < bb.center().X else bb.max.X - i - w
    z = bb.max.Z - 0.01  # just proud of the board's face, where the bead was
    return Compound([board, Pos(x, bb.min.Y + i, z) * Box(w, bb.size.Y - 2 * i, 0.08, align=CORNER),
                     Pos(bb.min.X + i, bb.max.Y - i - w, z) * Box(bb.size.X - 2 * i, w, 0.08, align=CORNER)])


def corner_detail():
    """A section at the top of the corner, across the side wall through the
    double rafter, seen from outside, at twice size."""
    from build123d import Box
    from model.exterior_trim import BACK_CORNER, corner_board_1, corner_board_2, corner_frame, rafters_in_house
    from model.notes import crossed_box
    k = 2
    side_face, _, end_face, _ = corner_frame(BACK_CORNER)
    b1, b2 = corner_board_1(BACK_CORNER).shape(), corner_board_2(BACK_CORNER).shape()
    top = b1.bounding_box().max.Z
    view = camera((-1, 0, 0))  # right = -Y
    cut_x = side_face - 0.375  # through the middle of Board #1
    slab = Pos(cut_x - 0.005, -20, top - 20) * Box(0.01, 40, 40, align=CORNER)
    window = Pos(-20, -20, top - 16) * Box(40, 40, 30, align=CORNER)
    sections = [r & slab for r in rafters_in_house()[1:3]]
    # (boolean results carry no placement of their own, so scale() treats
    # them alike: scale about the origin, turn to the view, then move Board
    # #1's corner edge to x = 109.62 and the siding's top to y = 40)
    from build123d import scale
    shift = Pos(109.62 + k * end_face, 40 - k * top, 0)  # view: (X, Y, Z) -> (-Y, Z, -X)

    def place(s):
        return shift * view * scale(s, k)
    parts = [(place(b1 & window), "outline"), (place(b2 & window), "outline"), (place(b1 & window), "bare", "laid")]
    notes = []
    for s in sections:
        bb = place(s).bounding_box()
        parts.append((place(s), "outline"))
        notes += [(bb.min.X, bb.min.Y, n) for n in crossed_box(bb.size.X, bb.size.Y)]
    return parts, notes
