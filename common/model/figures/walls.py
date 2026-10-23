"""Wall figures: Side_Walls/sidewall_1.md and sidewall_3.md,
Front_Wall/front_wall_ada.md, Rear_Wall/rear_wall.md. Each wall is drawn as
it lies in its jig, outside face up.

  side walls:  drawing X = down from the top of the wall (top plate at 0), Y = along the wall
  end walls:   drawing X = along the wall as seen from outside, Y = height
"""

from build123d import Align, Box, Location, Plane, Pos, Rot

from model.dimensions import END_WALL_PLATE_LENGTH, SIDE_WALL_PLATE_LENGTH, SIDING_HEIGHT, SIDING_PANEL_WIDTH
from model.walls import (
    DOOR_HEADER_Z, DOOR_OPENING, DOOR_X, END_SIDING_WIDTH, END_SIDING_X, SIDING, SIDING_BOTTOM, SIDING_Y,
    WALL_DEPTH, WALL_HEIGHT, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_X, WINDOW_Z, WRAP, front_wall_steps, panel,
    front_wall, rear_wall, rear_wall_steps, side_wall, side_wall_steps, window_flange_flashing,
    window_opening_flashing, siding_panel_door, siding_panel_plain, siding_panel_window,
    window_unit_at,
)
from model.common import key

from . import TYVEK, Figure, figure_names, optional_parts, placed_notes, title

SIDE_TO_DRAWING = Location(Plane((WALL_HEIGHT, SIDE_WALL_PLATE_LENGTH, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0)))
END_TO_DRAWING = Location(Plane((END_WALL_PLATE_LENGTH, 0, 0), x_dir=(-1, 0, 0), z_dir=(0, 1, 0)))


def shapes(members, to_drawing):
    return [to_drawing * (loc * comp.shape(frozenset(), key(mods))) for comp, loc, mods, _ in members]


def ctx(xs):
    return [(s, "context") for s in xs]


def new(xs):
    return [(s, "new") for s in xs]


def wrap(to_drawing, x0, width, holes=()):
    return to_drawing * Pos(x0, WALL_DEPTH, SIDING_BOTTOM) * panel(width, SIDING_HEIGHT, WRAP, holes=holes)


def figs(md, steps):
    return [Figure(md, fig_name, parts) for fig_name, parts in zip(figure_names(md), steps)]


def side_wall_figures(md, first_panel, wall):
    """first_panel: which end the first siding panel goes on (0 or 2); wall:
    which side wall, for the titles and the step-6/7 layer names (1 or 3)."""
    f = side_wall_steps()
    s1, s3 = shapes(f[1], SIDE_TO_DRAWING), shapes(f[3], SIDE_TO_DRAWING)
    flat, s1 = s1[-2:], s1[:-2]  # the flat studs, laid in at step 1 and screwed at step 2
    tyvek = [wrap(SIDE_TO_DRAWING, 0, SIDE_WALL_PLATE_LENGTH)]
    panels = shapes([(siding_panel_plain, Pos(x, SIDING_Y, SIDING_BOTTOM), [], '')
                     for x in (0, SIDING_PANEL_WIDTH, 2 * SIDING_PANEL_WIDTH)], SIDE_TO_DRAWING)
    p1 = [panels[first_panel]]
    framing = s1 + flat + s3
    jig = [(s, "jig") for s in framing]
    tyv = [(s, "bare", TYVEK) for s in tyvek]
    ab = "a" if wall == 1 else "b"
    steps = [
        ("1", jig + new(s1) + [(s, "outline", "laid") for s in flat]),
        ("2", jig + ctx(s1) + new(flat)),
        ("3", jig + ctx(s1 + flat) + new(s3)),
        ("4", ctx(framing)),
        ("5", tyv + ctx(framing)),
        ("6" + ab, tyv + ctx(framing) + ctx(p1)),
        ("7" + ab, ctx(framing) + ctx(panels)),
    ]
    out = []
    for (fig_name, (step, parts)) in zip(figure_names(md), steps):
        shown = {"manual:side_wall", f"manual:side_wall:{step}"}
        parts = parts + optional_parts(SIDE_TO_DRAWING, side_wall, shown, "outline", "laid")
        notes = placed_notes(SIDE_TO_DRAWING, side_wall, shown) + [
            title(f"Step {step[0]}", 40, -20), title("Side Wall", 34.45, -26.25, 4)]
        if step[0] in "67":
            notes.append(title(f" Wall #{wall}", 38, -32, 4))
        out.append(Figure(md, fig_name, parts, notes))
    return out


def end_wall_skin(window_hole, door_hole):
    """Wrap and the two panels of an end wall's skin, in its frame."""
    door = (DOOR_X - END_SIDING_X, -SIDING_BOTTOM, DOOR_OPENING, DOOR_HEADER_Z[0])
    window = (WINDOW_X - END_SIDING_X, WINDOW_Z - SIDING_BOTTOM, WINDOW_WIDTH, WINDOW_HEIGHT)
    holes = ([window] if window_hole else []) + ([door] if door_hole else [])
    return wrap(END_TO_DRAWING, END_SIDING_X, END_SIDING_WIDTH, holes)


def end_panels(left):
    return shapes([(left, Pos(END_SIDING_X, SIDING_Y, SIDING_BOTTOM), [], ''),
                   (siding_panel_window, Pos(END_SIDING_X + SIDING_PANEL_WIDTH, SIDING_Y, SIDING_BOTTOM), [], '')],
                  END_TO_DRAWING)


def end_wall_figures(md, manual, component, f, keys, titles, skin_steps):
    """An end wall's figures. f: framing shapes by step key; keys: the
    framing steps in order; skin_steps: [(step, figure parts)] after framing."""
    framing = [s for k in keys for s in f[k]]
    jig = [(s, "jig") for s in framing]
    steps = []
    for i, k in enumerate(keys):
        done = [s for kk in keys[:i] for s in f[kk]]
        steps.append((k, jig + ctx(done) + new(f[k])))
    steps += skin_steps(framing)
    out = []
    for fig_name, (step, parts) in zip(figure_names(md), steps):
        shown = {f"manual:{manual}", f"manual:{manual}:{step}"}
        parts = parts + optional_parts(END_TO_DRAWING, component, shown, "outline", "laid")
        notes = placed_notes(END_TO_DRAWING, component, shown) + [title(f"Step {step}", *titles)]
        out.append(Figure(md, fig_name, parts, notes))
    return out


def flashing(which):
    return shapes([(which, Location(), [], '')], END_TO_DRAWING)


def glass():
    """The window's lower pane, hatched as the drawings had it (where the
    unit's lower sash has it; window_unit_at keeps the unit's X)."""
    from model.walls import lower_pane
    x, z, w, h = lower_pane()
    pane = Pos(WINDOW_X - 1/40 + x, 0, WINDOW_Z + z) * Box(w, WALL_DEPTH, h, align=Align.MIN)
    return [(END_TO_DRAWING * pane, "bare", "glass")]


def front_wall_figures():
    f = {str(k): shapes(v, END_TO_DRAWING) for k, v in front_wall_steps().items()}
    window = shapes([window_unit_at()], END_TO_DRAWING)
    plain_left, routed_left = end_panels(siding_panel_plain), end_panels(siding_panel_door)
    opening, flange = flashing(window_opening_flashing), flashing(window_flange_flashing)

    def skin(framing):
        tyvek, cut = end_wall_skin(False, False), end_wall_skin(True, True)  # the drawing trims the doorway too
        tyv = lambda s: [(s, "bare", TYVEK)]
        return [
            ("6", ctx(framing)),                                       # nail, testing with the stretcher
            ("7", tyv(tyvek) + ctx(framing)),                          # Tyvek
            ("8", tyv(cut) + ctx(framing) + new(opening)),             # cut out the window; peel-and-stick
            ("9", ctx(framing) + ctx(plain_left)),  # panels
            ("10", ctx(framing) + ctx(routed_left) + new(flange) + glass() + [(s, "outline") for s in window]),
            ("11", ctx(framing) + ctx(routed_left) + new(flange) + glass() + [(s, "outline") for s in window]),
        ]
    return end_wall_figures("Front_Wall/front_wall_ada.md", "front_wall", front_wall, f, ["1", "2", "3", "4", "5"],
                            (38.17, -23.75), skin)


def rear_wall_figures():
    f = rear_wall_steps()
    f = {k: shapes(v, END_TO_DRAWING) for k, v in f.items()}
    window = shapes([window_unit_at()], END_TO_DRAWING)
    panels = end_panels(siding_panel_plain)
    opening, flange = flashing(window_opening_flashing), flashing(window_flange_flashing)

    def skin(framing):
        tyvek, cut = end_wall_skin(False, False), end_wall_skin(True, False)
        tyv = lambda s: [(s, "bare", TYVEK)]
        return [
            ("5", tyv(tyvek) + ctx(framing)),
            ("6", tyv(cut) + ctx(framing) + new(opening)),
            ("7", ctx(framing) + ctx(panels)),
            ("8", ctx(framing) + ctx(panels) + new(flange) + glass() + [(s, "outline") for s in window]),
        ]
    return end_wall_figures("Rear_Wall/rear_wall.md", "rear_wall", rear_wall, f, ["1", "2", "3", "4", "4b"],
                            (37.01, -18.32, 2.5), skin)


def figures():
    return (side_wall_figures("Side_Walls/sidewall_1.md", 0, 1)
            + side_wall_figures("Side_Walls/sidewall_3.md", 2, 3)
            + front_wall_figures() + rear_wall_figures())
