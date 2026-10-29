"""floor_door/floor_install.md figure: the floor in plan, part way through
(the first five rows), the doorway at the top. The drawing's frame is the
house's plan."""

from build123d import Align, Box, Pos

from model.dimensions import PLATFORM_LENGTH, PLATFORM_WIDTH
from model.flooring import DOORWAY_X, FLOORING, FLOOR_X, FLOOR_Y, ROOM_X, ROOM_Y, floor_rows
from model.notes import Label, around, at, callout

from . import Extent, extent, table

MD = "floor_door/floor_install.md"
ROWS_SHOWN = 5


def walls_in_plan():
    """The walls as the floor sees them: the outside of the building, the
    inside faces of the wall panels, and the doorway through the front wall."""
    outside = Box(PLATFORM_WIDTH, PLATFORM_LENGTH, FLOORING, align=Align.MIN)
    room = Pos(ROOM_X[0], ROOM_Y[0], 0) * Box(ROOM_X[1] - ROOM_X[0], ROOM_Y[1] - ROOM_Y[0], FLOORING, align=Align.MIN)
    doorway = Pos(DOORWAY_X[0], ROOM_Y[1] - 1, 0) * Box(DOORWAY_X[1] - DOORWAY_X[0], PLATFORM_LENGTH, FLOORING,
                                                        align=Align.MIN)
    return outside - room - doorway


def figures(scale=1/20, only=None):
    planks = [loc * comp.shape() for comp, loc, _, _ in floor_rows(ROWS_SHOWN)]
    first = Extent(planks[len(floor_rows(1)) - 1])  # the first row's last plank, notched beside the doorway
    notch = (first.x0, first.y1)  # the corner cut out of it, by the wall
    whole = extent(planks)
    notes = [
        at(((DOORWAY_X[0] + DOORWAY_X[1]) / 2, ROOM_Y[1] + 6), Label("DOORWAY")),
        around(notch, 1/2),
        *callout((notch[0] + 1/2 / scale * 0.7, notch[1] + 1/2 / scale * 0.7), "Note notch cut out for wall clearance.", "above right", lead=1/2),
        *callout((FLOOR_X[0], FLOOR_Y[0]), '1/4" space from walls', "below left", lead=3/4),
    ]
    rows = {"tiles": ([(walls_in_plan(), "hlr_thin")] + [(p, "hlr_thin") for p in planks], [], notes)}
    return table(MD, rows)
