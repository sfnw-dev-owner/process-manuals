"""Extract_Iron_Carts/Extract_instructions.md figures: perspective views of
the iron-cart removal, one per step (model/iron_carts.py places the house
and the equipment at each).

Each row of SCENES:
  name       the figure's name
  camera     a name in CAMERAS: (eye, target, up) in the house's frame
  house      the heights the house's rear and front ends stand at
  parts      the equipment in the scene: (component, placement, mods)
  numbers    [(arrow, n, along, across)]: a circled n beside an arrow
             entry, that far along the arrow from its tail and across it
             (inches; across is the arrow's width direction)
"""

import math

from build123d import Location

from model import iron_carts as IC
from model.common import key
from model.notes import Circle, Label

from . import Figure, Viewport

MD = "Extract_Iron_Carts/Extract_instructions.md"

WINDOW = (6, 4.8)  # each figure's size, inches, with the camera's fov across its width (as SketchUp's is)
FOV = 35  # degrees, across the figure's width
NUMBER = (0.15, 0.14)  # a circled number: its circle's radius and its digit's height, page inches
NUMBER_BESIDE = 14  # the circled number, this far beside the arrow's middle (across its width)

# The views, in the house's frame: from high over a rear corner (rear) or a
# front corner (front) of the house, as the manual's pictures were taken.
UP_REAR, UP_FRONT = (0.0948, 0.1769, 0.9797), (0.0446, -0.1235, 0.9913)  # the cameras' up, a little off plumb
CAMERAS = {
    "rear_wide": ((-166, -340, 139), (79, 117, 33), UP_REAR),
    "rear_jack": ((-145, -331, 124), (100, 127, 18), UP_REAR),
    "rear_posts": ((-176, -342, 132), (-60, -127, 82), UP_REAR),
    "rear_low": ((-151, -358, 134), (191, 281, -14), UP_REAR),
    "front_jack": ((-89, 465, 87), (-5, 233, 54), UP_FRONT),
    "front_wide": ((-110, 523, 101), (10, 190, 54), UP_FRONT),
    "front_blocks": ((-85, 471, 86), (37, 134, 38), UP_FRONT),
}


def numbered(arrows, n, along=None, across=NUMBER_BESIDE):
    """[(arrow entry, n, along, across)] for the arrows, numbered n."""
    return [(a, n, along, across) for a in arrows]


def scene(name, camera, rear, front, parts, numbers=()):
    return {"name": name, "camera": camera, "house": (rear, front), "parts": parts, "numbers": list(numbers)}


SCENES = [
    scene("01_prepare", "rear_wide", IC.ON_CARTS, IC.ON_CARTS,
          IC.carts() + [IC.jack("rear", out=IC.JACK_STAGED), IC.jack("front", out=IC.JACK_STAGED)] + IC.posts("staged")
          + IC.blocks("rear", False) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", False)),
    scene("02_rear_raised", "rear_jack", IC.ON_JACK, IC.ON_CARTS,
          IC.carts() + [IC.jack("rear", raised=True), IC.jack("front", out=IC.JACK_STAGED)] + IC.posts("staged")
          + IC.blocks("rear", False) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", False),
          numbered([IC.jack_arrow("rear", up=True)], 1) + numbered(IC.post_arrows(going_in=True), 2)),
    scene("03_rear_dropped_onto_posts", "rear_posts", IC.ON_POSTS, IC.ON_CARTS,
          IC.carts() + [IC.jack("rear"), IC.jack("front", out=IC.JACK_STAGED)] + IC.posts("under")
          + IC.blocks("rear", False) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", False)
          + [IC.jack_arrow("rear", up=False)]),
    scene("04_front_raised", "front_jack", IC.ON_POSTS, IC.ON_JACK,
          IC.carts() + [IC.jack("rear"), IC.jack("front", raised=True)] + IC.posts("under")
          + IC.blocks("rear", False) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", False),
          numbered([IC.jack_arrow("front", up=True)], 1) + numbered(IC.cart_arrows(), 2)),
    scene("05_carts_removed", "front_wide", IC.ON_POSTS, IC.ON_JACK,
          [IC.jack("rear"), IC.jack("front", raised=True)] + IC.posts("under")
          + IC.blocks("rear", False) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", False),
          numbered(IC.block_arrows("front", going_in=True), 1)),
    scene("07_lowered_onto_front_triple_blocks", "front_blocks", IC.ON_POSTS, IC.ON_BLOCKS,
          [IC.jack("rear"), IC.jack("front")] + IC.posts("under")
          + IC.blocks("rear", False) + IC.blocks("front", True) + IC.dollies("rear", False) + IC.dollies("front", False)
          + [IC.jack_arrow("front", up=False)]),
    scene("08_rear_remove_posts", "rear_low", IC.ON_JACK, IC.ON_BLOCKS,
          [IC.jack("rear", raised=True), IC.jack("front")] + IC.posts("under")
          + IC.blocks("rear", False) + IC.blocks("front", True) + IC.dollies("rear", False) + IC.dollies("front", False),
          numbered([IC.jack_arrow("rear", up=True)], 1) + numbered(IC.block_arrows("rear", going_in=True), 2)
          + numbered(IC.post_arrows(going_in=False), 3)),
    scene("09_rear_lowered_onto_triple_blocks", "rear_low", IC.ON_BLOCKS, IC.ON_BLOCKS,
          [IC.jack("rear"), IC.jack("front")] + IC.posts("out")
          + IC.blocks("rear", True) + IC.blocks("front", True) + IC.dollies("rear", False) + IC.dollies("front", False)
          + [IC.jack_arrow("rear", up=False)]),
    scene("10_remove_front_triple_blocks", "front_blocks", IC.ON_BLOCKS, IC.ON_JACK,
          [IC.jack("rear"), IC.jack("front", raised=True)] + IC.posts("out")
          + IC.blocks("rear", True) + IC.blocks("front", True) + IC.dollies("rear", False) + IC.dollies("front", False),
          numbered([IC.jack_arrow("front", up=True)], 1) + numbered(IC.block_arrows("front", going_in=False), 2)
          + numbered(IC.dolly_arrows("front"), 3)),
    scene("11_front_dollies_in_place", "front_blocks", IC.ON_BLOCKS, IC.ON_DOLLIES,
          [IC.jack("rear"), IC.jack("front")] + IC.posts("out")
          + IC.blocks("rear", True) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", True)
          + [IC.jack_arrow("front", up=False)]),
    scene("12_remove_rear_triple_blocks", "rear_low", IC.ON_JACK, IC.ON_DOLLIES,
          [IC.jack("rear", raised=True), IC.jack("front")] + IC.posts("out")
          + IC.blocks("rear", True) + IC.blocks("front", False) + IC.dollies("rear", False) + IC.dollies("front", True),
          numbered([IC.jack_arrow("rear", up=True)], 1) + numbered(IC.block_arrows("rear", going_in=False), 2)
          + numbered(IC.dolly_arrows("rear"), 3)),
    scene("13_home_in_final_position", "rear_low", IC.ON_DOLLIES, IC.ON_DOLLIES,
          [IC.jack("rear"), IC.jack("front")] + IC.posts("out")
          + IC.blocks("rear", False) + IC.blocks("front", False) + IC.dollies("rear", True) + IC.dollies("front", True)
          + [IC.jack_arrow("rear", up=False)]),
]


def circled(n):
    radius, height = NUMBER
    return [Circle(radius, fill=(255, 255, 255), weight=2), Label(str(n), height)]


def number(arrow, n, along, across):
    """(x, y, z, note)s: a circled n beside an arrow entry, `along` it from
    its tail (default its middle) and `across` it."""
    comp, loc, mods = arrow
    along = IC.ARROW[0] / 2 if along is None else along
    p = (loc * Location((0, along, IC.ARROW[1] / 2 + across))).position  # in the arrow's frame: +Y tail to tip, +Z across its width
    return [(p.X, p.Y, p.Z, note) for note in circled(n)]


def figures(only=None):
    """The figures (just those named by `only`, if given)."""
    out = []
    for row in SCENES:
        if only is not None and row["name"] not in only:
            continue
        parts = [IC.house_at(*row["house"])] + row["parts"] + [a for a, *_ in row["numbers"]]
        shapes = [loc * comp.shape(IC.HOUSE_HIDDEN if comp is IC.house else frozenset(), key(mods)) for comp, loc, mods in parts]
        notes = [x for arrow, n, along, across in row["numbers"] for x in number(arrow, n, along, across)]
        eye, target, up = CAMERAS[row["camera"]]
        w, h = WINDOW
        # the fov spans the window's width; a Viewport's its height.
        fov = math.degrees(2 * math.atan(math.tan(math.radians(FOV) / 2) * h / w))
        view = Viewport((0, 0, w, h), eye, target, up, [(s, "hlr") for s in shapes], fov=fov, notes=notes)
        out.append(Figure(MD, row["name"], page=(w, h), viewports=[view]))
    return out
