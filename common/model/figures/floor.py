"""floor_door/floor_install.md figure: the floor in plan, part way through
(the first five rows), the doorway at the top. The drawing's frame is the
house's plan."""

from build123d import Align, Box, Location, Pos

from model.dimensions import PLATFORM_LENGTH, PLATFORM_WIDTH
from model.flooring import DOORWAY_X, FLOORING, ROOM_X, ROOM_Y, floor_rows, flooring
from model.walls import WALL_DEPTH

from . import Figure, figure_names, placed_notes

MD = "floor_door/floor_install.md"
TO_DRAWING = Location()


def walls_in_plan():
    """The walls as the floor sees them: the outside of the building, the
    inside faces of the wall panels, and the doorway through the front wall."""
    outside = Box(PLATFORM_WIDTH, PLATFORM_LENGTH, FLOORING, align=Align.MIN)
    room = Pos(ROOM_X[0], ROOM_Y[0], 0) * Box(ROOM_X[1] - ROOM_X[0], ROOM_Y[1] - ROOM_Y[0], FLOORING, align=Align.MIN)
    doorway = Pos(DOORWAY_X[0], ROOM_Y[1] - 1, 0) * Box(DOORWAY_X[1] - DOORWAY_X[0], PLATFORM_LENGTH, FLOORING,
                                                        align=Align.MIN)
    return outside - room - doorway


def figures():
    planks = [loc * comp.shape() for comp, loc, _, _ in floor_rows(5)]
    shown = {"manual:floor", "manual:floor:tiles"}
    parts = [(walls_in_plan(), "hlr_thin")] + [(p, "hlr_thin") for p in planks]
    fig_name, = figure_names(MD)
    return [Figure(MD, fig_name, parts, placed_notes(TO_DRAWING, flooring, shown))]
