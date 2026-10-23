"""The assembled house.

Frame: the platform's frame (see platform.py): origin at the outside corner of
the 2x6 frame, level with the bottom of the skids; X across the house, Y along
it (the front wall, with the door, is at the far end), Z up.

Everything is stacked on what it rests on: the walls stand on the deck, the
roof sits on the walls, so changing a dimension below moves everything above.
"""

from .common import *
from .platform import (
    DECK,
    platform,
)
from .walls import (
    WALL_DEPTH,
    WALL_HEIGHT,
    front_wall,
    rear_wall,
    side_wall,
)
from .roof import (
    roof,
)
from .interior import (
    interior,
)
from .interior_roof import (
    interior_roof,
)
from .doors import (
    DOOR_IN_HOUSE,
    door_assembly,
)
from .flooring import (
    flooring,
)
from .exterior_trim import (
    external_trim,
)

WALL_TOP = DECK + WALL_HEIGHT

@component
def house():
    """The house, from the platform up."""
    solids = []
    children = [
        (platform, Location(), [], ''),
        # Walls, standing on the deck. The side walls run the full length of
        # the platform; the end walls fit between them.
        (side_wall, Pos(WALL_DEPTH, 0, DECK) * Rot(Z=90), [], ''),
        (side_wall, Pos(PLATFORM_WIDTH - WALL_DEPTH, PLATFORM_LENGTH, DECK) * Rot(Z=-90), [], ''),
        (front_wall, Pos(WALL_DEPTH, PLATFORM_LENGTH - WALL_DEPTH, DECK), [], ''),
        (rear_wall, Pos(PLATFORM_WIDTH - WALL_DEPTH, WALL_DEPTH, DECK) * Rot(Z=180), [], ''),
        # Door, in the front wall's doorway (on the doorway strip of flooring).
        (door_assembly, Pos(0, 0, DECK) * DOOR_IN_HOUSE, [], ''),
        # Inside, on the deck: the floating floor, the interior panels and trim.
        (flooring, Pos(0, 0, DECK), [], ''),
        (interior, Location(), [], ''),
        # Roof, on the walls.
        (roof, Pos(0, 0, WALL_TOP), [], ''),
        (interior_roof, Pos(0, 0, WALL_TOP), [], ''),
        # Exterior trim: corner boards and window trim.
        (external_trim, Location(), [], ''),
    ]
    return solids, children
