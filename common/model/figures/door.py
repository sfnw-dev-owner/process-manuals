"""floor_door/door_manual.md figures: the door assembly (model/doors.py) as
each figure's View shows it; the wall and floor around it where the figure
needs them."""

from build123d import Align, Box, Compound, Cylinder, Pos, scale

from model.dimensions import PLATFORM_LENGTH
from model.doors import (
    DETAIL, DOOR_HEADER_Z, DOOR_IN_HOUSE, FRAME_BOTTOM, FRAME_GAP, FRAME_WIDTH, FRAMING_Y, INTERIOR_PLYWOOD,
    JAMB_DEPTH, LATCH_Z, STRIKE_FACE_WINDOW, VIEWS, door_assembly,
)
from model.common import key
from model.flooring import floor_rows, flooring
from model.walls import DOOR_OPENING, WALL_DEPTH, front_wall_framing, front_wall_skin

from . import GRAY, Figure, figure_names

MD = "floor_door/door_manual.md"

# The front wall and floor, in the assembly's frame.
HOUSE = DOOR_IN_HOUSE.inverse()  # the house's frame, with the deck at Z = 0
FRONT_WALL = HOUSE * Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, 0)


def assembly(*names):
    """The assembly's parts made from these components, in its frame."""
    # (the drawing had the slab plain: no panels or knob on its outside)
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


def drawn(view, shapes, style="hlr_thin", fill=None):
    v = VIEWS[view]
    out = []
    for s in shapes:
        # (scale() scales a lone solid about its own location; a compound
        # about the origin, which is what's wanted here)
        d = Pos(*v.offset, 0) * scale(Compound([v.camera * s]), by=v.scale)
        out.append((d, style) if fill is None else (d, style, fill))
    return out


def wall_panels(x0, x1):
    """The interior wall panels either side of the doorway, between x0 and x1
    (they're not in the model yet: 1/2" plywood on the framing)."""
    y = (FRAMING_Y - INTERIOR_PLYWOOD, FRAMING_Y)
    return [box(x0, -FRAME_GAP, *y, -FRAME_BOTTOM, 90), box(FRAME_WIDTH + FRAME_GAP, x1, *y, -FRAME_BOTTOM, 90)]


def notes(name, view=None):
    v = VIEWS[view or name]
    shown = {"manual:door", f"manual:door:{name}"}
    return [(*v.xy(tuple(loc.position)), note) for loc, note in door_assembly.notes(shown)]


def figures():
    frame = assembly("jamb_leg", "head_jamb", "brickmold")
    slab, hinges = assembly("door_slab"), assembly("hinge")
    x0, x1 = -FRAME_GAP - 7.5, FRAME_WIDTH + FRAME_GAP + 6

    # 3_Threshold: the doorway in plan at the floor, before the door goes in.
    around = box(x0, x1, -1, JAMB_DEPTH + 3, -FRAME_BOTTOM - 1, -FRAME_BOTTOM + 3)
    walls = [FRONT_WALL * front_wall_framing.shape(), FRONT_WALL * front_wall_skin.shape()]
    floor_at_door = [HOUSE * loc * comp.shape() for comp, loc, _, _ in floor_rows(10)]
    strip = [HOUSE * loc * comp.shape() for comp, loc, _, _ in flooring()[1] if getattr(comp, "__name__", "") == "doorway_strip"]
    threshold_parts = (
        drawn("threshold", clip(walls, around & box(x0, x1, -1, 10, 2, 3)))
        + drawn("threshold", clip(wall_panels(x0, x1), around))
        + drawn("threshold", clip(floor_at_door, box(-FRAME_GAP, FRAME_WIDTH + FRAME_GAP, FRAMING_Y, 5, -5, 5)))
        + drawn("threshold", strip)
        + drawn("threshold", assembly("flashing"), "hlr_thin", "laid")
    )

    # 3.1_ScrewLocs: the legs from the doorway, and a detail at the top hinge.
    detail_circle = Pos(DETAIL[0], DETAIL[1], 0) * Cylinder(DETAIL[2], 2000)
    hinge_leg = assembly("jamb_leg")[:1]
    detail = [s & detail_circle for s, _ in drawn("screws_detail", hinge_leg + hinges[2:])]
    screws_parts = (
        drawn("screws", hinge_leg + hinges)
        + drawn("screws_latch", assembly("jamb_leg")[1:] + assembly("strike_plate"))
        + [(s, "hlr_thin") for s in detail if s.volume > 1e-9]
    )

    # 4_Shimming: the frame in the rough opening, from inside.
    rough = (box(-FRAME_GAP, FRAME_WIDTH + FRAME_GAP, -1, 0, -FRAME_BOTTOM, DOOR_HEADER_Z[0] - FRAME_BOTTOM)
             - box(-FRAME_GAP + 0.01, FRAME_WIDTH + FRAME_GAP - 0.01, -2, 1, -FRAME_BOTTOM + 0.01,
                   DOOR_HEADER_Z[0] - FRAME_BOTTOM - 0.01))
    shims_parts = (drawn("shims", [rough] + frame + slab) + drawn("shims", hinges, "new")
                   + drawn("shims", assembly("shim", "top_shim"), "new"))

    # 5_Strike Plate: the latch jamb in section at the latch, and its face.
    at_latch = box(FRAME_WIDTH - 1, FRAME_WIDTH + FRAME_GAP + 8.5, -1, JAMB_DEPTH + 1, LATCH_Z - 0.1, LATCH_Z + 0.1)
    latch_leg = assembly("jamb_leg")[1:]
    face_window = box(FRAME_WIDTH - 1, FRAME_WIDTH + 1, -1, JAMB_DEPTH + 1, *STRIKE_FACE_WINDOW)
    strike_parts = (
        drawn("strike", clip(latch_leg + walls + wall_panels(x0, x1), at_latch))
        + drawn("strike_face", clip(latch_leg + assembly("strike_plate"), face_window))
    )

    parts = {
        "door": drawn("door", frame + slab) + drawn("door", hinges, "new"),
        "threshold": threshold_parts,
        "screws": screws_parts,
        "shims": shims_parts,
        "strike": strike_parts,
    }
    names = ["door", "threshold", "screws", "shims", "strike"]
    return [Figure(MD, fig_name, parts[name], notes(name))
            for fig_name, name in zip(figure_names(MD), names)]
