"""Extract_Iron_Carts/Extract_instructions.md figures: perspective views of
the iron-cart removal, one per scene of the SketchUp model they were first
drawn from (model/iron_carts.py has every step's copy of the house and the
equipment, where the scenes had them).

Each row of SCENES:
  name         the figure's name
  skp_scene    the SketchUp scene the row came from (informational)
  eye, target, up, fov   camera (inches; fov in degrees, across the export)
  zoom, shift  the view zoomed in by this factor and its center moved this
               far (page inches, y down): what lines the figure up with the
               export it replaces (whose camera this transcription doesn't
               quite reproduce); to drop once the figures are blessed, see
               ../TODO.md
  hidden_tags  tags hidden in this scene
  show, hide   top-level instance names (iron_carts.ROOT keys) forced on/off
  numbers      {arrow instance: n}: a circled n behind the arrow's tail, or
               (n, "head"): past its head, or (n, along, across): that far
               along the arrow from its tail, and across it (inches), or
               (n, (x, y)): at that point of the page (inches from the
               top-left corner, y down: where the export it replaces had it)
  far          (optional) drop instances farther than this (inches)
"""

import math

from build123d import Location

from model import iron_carts
from model.notes import Circle, Label

from . import Figure, Viewport

MD = "Extract_Iron_Carts/Extract_instructions.md"

# Horizontal/vertical ratio assumed when deciding what's inside the camera's
# view. SketchUp's fov is vertical; the width depends on the window it was
# exported from, so err on the wide side.
ASPECT = 1.8

# Objects farther than this multiple of the eye-target distance are dropped:
# the model keeps each step's copy of the house at a different spot, and the
# far ones would otherwise be drawn tiny in the background.
FAR = 4

ARROW_TAIL = (0, 0, 6)  # arrow_1_2's tail, in its own frame
NUMBER_BACK = 16  # the circled number, this far behind the tail

# Each figure is drawn in a window the size of the SketchUp export it
# replaces (Extract_Iron_Carts/images/*.pdf, in git history), in inches, with
# the camera's fov across its width as SketchUp had it, so the manual's pages
# don't move. (To revisit once the figures are blessed: see ../TODO.md.)
WINDOWS = {
    '01_prepare': (6.042, 3.847),
    '02_rear_raised': (6.389, 5.069),
    '03_rear_dropped_onto_posts': (5.972, 4.444),
    '04_front_raised': (6.25, 5.278),
    '05_carts_removed': (6.097, 4.611),
    '07_lowered_onto_front_triple_blocks': (6.236, 5.069),
    '08_rear_remove_posts': (6.069, 4.819),
    '09_rear_lowered_onto_triple_blocks': (6.375, 4.375),
    '10_remove_front_triple_blocks': (6.306, 5.347),
    '11_front_dollies_in_place': (5.597, 5.722),
    '12_remove_rear_triple_blocks': (5.958, 4.958),
    '13_home_in_final_position': (6.028, 4.931),
}
NOTE_SCALE = 6.1 / 150  # page inches per unit of the numbers' sizes below (drawn for a 6.1" wide figure)


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(_dot(a, a))
    return tuple(x / n for x in a)


def in_view(row):
    """Top-level instances whose bounding box reaches into the camera frustum,
    up to the far limit (tested at the box's corners and center)."""
    eye = row["eye"]
    fwd = _unit(_sub(row["target"], eye))
    right = _unit(_cross(fwd, row["up"]))
    up = _cross(right, fwd)
    tan_v = math.tan(math.radians(row["fov"]) / 2)
    tan_h = tan_v * ASPECT
    far = row.get("far", FAR * math.dist(eye, row["target"]))
    names = set()
    for name, (lo, hi) in iron_carts.BOUNDS.items():
        pts = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        pts.append(tuple((a + b) / 2 for a, b in zip(lo, hi)))
        for p in pts:
            v = _sub(p, eye)
            z = _dot(v, fwd)
            if 0 < z < far and abs(_dot(v, right)) <= z * tan_h and abs(_dot(v, up)) <= z * tan_v:
                names.add(name)
                break
    return names



ARROW_LENGTH = 39.7148  # arrow_1_2's, tail to head


NUMBER_RADIUS, NUMBER_HEIGHT = 3.8, 3.5  # the circle and its digit (in NOTE_SCALE units), as the exports had them


def circled(n):
    return [Circle(NUMBER_RADIUS * NOTE_SCALE, fill=(255, 255, 255), weight=2.5 * NOTE_SCALE / 0.06),  # 0.06: PAGE_UNIT in render/model2svg.py
            Label(str(n), NUMBER_HEIGHT * NOTE_SCALE)]


def number(arrow, n):
    """(x, y, z, note)s: a circled n behind an arrow's tail (or past its head),
    sized in page inches; or (x, y, note)s on the page, for (n, (x, y))."""
    comp, loc, mods, _ = iron_carts.ROOT[arrow]
    n, *where = n if isinstance(n, tuple) else (n,)
    if where and isinstance(where[0], tuple):
        x, y = where[0]
        return [(x, y, note) for note in circled(n)]
    if not where:
        along, across = -NUMBER_BACK, 0
    elif where == ["head"]:
        along, across = ARROW_LENGTH + NUMBER_BACK, 0
    else:
        along, across = where
    back = loc * Location((ARROW_TAIL[0], ARROW_TAIL[1] + along, ARROW_TAIL[2] + across))
    p = back.position
    return [(p.X, p.Y, p.Z, note) for note in circled(n)]


def figures(only=None):
    """The figures (just those named by `only`, if given)."""
    out = []
    for row in SCENES:
        if only is not None and row["name"] not in only:
            continue
        names = in_view(row) - set(row["hide"])
        # (the SketchUp houses' roofs were plain: no shingles)
        shapes = iron_carts.model(names, list(row["hidden_tags"]) + ["Roofing"], row["show"])
        notes = [x for arrow, n in row.get("numbers", {}).items() for x in number(arrow, n)]
        page_notes = [x for x in notes if len(x) == 3]  # on the page
        notes = [x for x in notes if len(x) == 4]  # at points of the model
        w, h = WINDOWS[row["name"]]
        # SketchUp's fov spans the window's width; a Viewport's its height.
        fov = math.degrees(2 * math.atan(math.tan(math.radians(row["fov"]) / 2) * h / w / row.get("zoom", 1)))
        view = Viewport((0, 0, w, h), row["eye"], row["target"], row["up"], [(s, "hlr") for s in shapes.values()],
                        fov=fov, notes=notes, offset=row.get("shift", (0, 0)))
        out.append(Figure(MD, row["name"], page=(w, h), viewports=[view], notes=page_notes))
    return out


SCENES = [
    # No matching image in Extract_Iron_Carts/images/:
    # {'name': 'iso_iron_cart_2_view_of_jack_from_underside_of_home',
    #  'skp_scene': 'ISO - Iron Cart 2 -  View of Jack from Underside of Home',
    #  'eye': (5.6018, 6.7631, -79.3916),
    #  'target': (107.703, 35.1752, 82.5033),
    #  'up': (-0.806, -0.2243, 0.5477),
    #  'fov': 35.0,
    #  'hidden_tags': [],
    #  'show': [],
    #  'hide': []},
    {'name': '01_prepare',
     'skp_scene': 'ISO - Prepare',
     'eye': (269.8755, 504.2659, 139.4664),
     'target': (24.8433, 46.939, 33.1946),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 1.02, 'shift': (0.131, -0.252),
     'hidden_tags': ['Tools',
                     'Home - Level',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting'],
     'show': [],
     'hide': []},
    {'name': '02_rear_raised',
     'skp_scene': 'ISO - Rear Raised',
     'eye': (-802.3091, 1082.0749, 125.0889),
     'target': (-1047.3412, 624.748, 18.8172),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 0.97, 'shift': (0.404, -0.376),
     'hidden_tags': ['Tools',
                     'Home - Level',
                     'Jack Rear - Down',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation'],
     'show': [],
     'hide': [],
     'numbers': {'arrow_rear_up_1': (1, (4.15, 4.89)), 'arrow_1_2_1': (2, (3.17, 4.19)), 'arrow_1_2_2': (2, (5.51, 3.76))}},
    {'name': '03_rear_dropped_onto_posts',
     'skp_scene': 'ISO - Rear\t dropped onto Posts',
     'eye': (-1822.5656, 1681.1681, 132.3369),
     'target': (-1937.8712, 1465.9622, 82.3282),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 1.03, 'shift': (-0.03, -0.393),
     'hidden_tags': ['Tools',
                     'Home - Level',
                     'Home - Level Raised',
                     'Arrows',
                     'Jack Rear - Down',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Front Up'],
     'show': [],
     'hide': []},
    {'name': '04_front_raised',
     'skp_scene': 'ISO - Front raised',
     'eye': (-1908.8437, 873.5761, 87.2798),
     'target': (-1992.8556, 1105.9145, 54.5589),
     'up': (-0.0446, 0.1235, 0.9913),
     'fov': 35.0,
     'zoom': 0.9, 'shift': (0.138, -0.444),
     'hidden_tags': ['Tools',
                     'Home - Back Raised',
                     'Home - Level',
                     'Jack Front - Down',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Down'],
     'show': [],
     'hide': [],
     'numbers': {'arrow_front_up_1': (1, (2.59, 5.10)), 'arrows_1': (2, (3.16, 4.10)), 'arrows_2': (2, (1.41, 3.89))}},
    {'name': '05_carts_removed',
     'skp_scene': 'ISO - Carts Removed',
     'eye': (-2979.3506, 1436.8306, 101.9201),
     'target': (-3099.6851, 1769.6209, 55.0523),
     'up': (-0.0446, 0.1235, 0.9913),
     'fov': 35.0,
     'zoom': 1.03, 'shift': (0.112, -0.381),
     'hidden_tags': ['Tools',
                     'Home - Level',
                     'Home - Front lowered onto Triple Block',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Under',
                     'Posts - Out',
                     'Triple Blocks Front - Under',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Front - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Arrow',
                     'Dolly Front Under',
                     'Home - Front lowered onto Dolly',
                     'Jack Front - Down & Out',
                     'Dolly Rear Arrow',
                     'Home - Front lowered onto Dolly rear raised',
                     'Home - Level on Dollies',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Up',
                     'Arrow Rear Down',
                     'Arrow Front Down',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': [],
     'numbers': {'triple_block_front_arrow_in_1': (1, (4.00, 3.61)), 'triple_block_front_arrow_in_2': (1, (1.40, 3.36))}},
    # No matching image in Extract_Iron_Carts/images/:
    # {'name': 'iso_front_triple_blocks_in_place',
    #  'skp_scene': 'ISO - Front Triple Blocks in place',
    #  'eye': (-3004.4694, 1488.2756, 86.458),
    #  'target': (-3126.5279, 1825.8335, 38.9187),
    #  'up': (-0.0446, 0.1235, 0.9913),
    #  'fov': 35.0,
    #  'hidden_tags': ['Tools',
    #                  'Home - Back Raised',
    #                  'Home - Level',
    #                  'Home - Front lowered onto Triple Block',
    #                  'Home - Level on Triple Blocks',
    #                  'Triple Blocks Rear - Under',
    #                  'Posts - Out',
    #                  'Triple Blocks Front - Staged',
    #                  'Triple Block Front Arrow - In',
    #                  'Triple Block Rear Arrow - In',
    #                  'Post Arrow - Out',
    #                  'Jack Front - Down',
    #                  'Home - Front raised on Rear Triple Block',
    #                  'Triple Block Front Arrow - Out',
    #                  'Triple Block Rear Arrow - Out',
    #                  'Dolly Front Arrow',
    #                  'Dolly Front Under',
    #                  'Home - Front lowered onto Dolly',
    #                  'Jack Front - Down & Out',
    #                  'Dolly Rear Arrow',
    #                  'Home - Front lowered onto Dolly rear raised',
    #                  'Home - Level on Dollies',
    #                  'Dolly Rear Under',
    #                  'Wall Framing',
    #                  'Floor Framing',
    #                  'Floor Insulation',
    #                  'Floor Sheeting',
    #                  'Arrow Rear Up',
    #                  'Arrow Rear Down',
    #                  'Arrow Front Down',
    #                  'Arrow Rear Down Final'],
    #  'show': [],
    #  'hide': []},
    {'name': '07_lowered_onto_front_triple_blocks',
     'skp_scene': 'ISO - Lowered onto Front Triple Blocks',
     'eye': (-3004.4694, 1488.2756, 86.458),
     'target': (-3126.5279, 1825.8335, 38.9187),
     'up': (-0.0446, 0.1235, 0.9913),
     'fov': 35.0,
     'zoom': 0.91, 'shift': (-0.001, -0.568),
     'hidden_tags': ['Tools',
                     'Home - Back Raised',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Under',
                     'Posts - Out',
                     'Triple Blocks Front - Staged',
                     'Triple Block Front Arrow - In',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Front - Up',
                     'Jack Front - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Arrow',
                     'Dolly Front Under',
                     'Home - Front lowered onto Dolly',
                     'Dolly Rear Arrow',
                     'Home - Front lowered onto Dolly rear raised',
                     'Home - Level on Dollies',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Up',
                     'Arrow Rear Down',
                     'Arrow Front Up',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': []},
    {'name': '08_rear_remove_posts',
     'skp_scene': 'ISO - Rear remove Posts',
     'eye': (-2938.6725, 2317.1551, 134.7265),
     'target': (-3280.5932, 1678.9957, -13.5663),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 1.03, 'shift': (0.551, -0.578),
     'hidden_tags': ['Tools',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Under',
                     'Posts - Out',
                     'Triple Blocks Front - Staged',
                     'Triple Block Front Arrow - In',
                     'Jack Rear - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Arrow',
                     'Dolly Front Under',
                     'Home - Front lowered onto Dolly',
                     'Dolly Rear Arrow',
                     'Home - Front lowered onto Dolly rear raised',
                     'Home - Level on Dollies',
                     'Jack Rear - Down & Out',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Down',
                     'Arrow Front Down',
                     'Arrow Front Up',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': [],
     'numbers': {'arrow_rear_up_2': (1, (3.93, 4.64)), 'triple_block_rear_arrow_in_1': (2, (1.88, 3.01)), 'triple_block_rear_arrow_in_2': (2, (5.22, 3.35)), 'post_arrow_out_1': (3, (2.86, 3.86)), 'post_arrow_out_2': (3, (5.12, 2.40))}},
    {'name': '09_rear_lowered_onto_triple_blocks',
     'skp_scene': 'ISO - Rear lowered onto Triple Blocks',
     'eye': (-2938.6725, 2317.1551, 134.7265),
     'target': (-3280.5932, 1678.9957, -13.5663),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 0.98, 'shift': (0.396, -0.464),
     'hidden_tags': ['Tools',
                     'Home - Back Raised',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Front lowered onto Triple Block',
                     'Triple Blocks Rear - Staged',
                     'Posts - Under',
                     'Triple Blocks Front - Staged',
                     'Triple Block Front Arrow - In',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Rear - Up',
                     'Jack Front - Up',
                     'Jack Front - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Arrow',
                     'Dolly Front Under',
                     'Home - Front lowered onto Dolly',
                     'Dolly Rear Arrow',
                     'Home - Front lowered onto Dolly rear raised',
                     'Home - Level on Dollies',
                     'Jack Rear - Down & Out',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Up',
                     'Arrow Front Down',
                     'Arrow Front Up',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': []},
    {'name': '10_remove_front_triple_blocks',
     'skp_scene': 'ISO - Remove Front Triple Blocks',
     'eye': (-3004.4694, 1488.2756, 86.458),
     'target': (-3126.5279, 1825.8335, 38.9187),
     'up': (-0.0446, 0.1235, 0.9913),
     'fov': 35.0,
     'zoom': 0.9, 'shift': (0.004, -0.398),
     'hidden_tags': ['Tools',
                     'Home - Back Raised',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Front lowered onto Triple Block',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Staged',
                     'Posts - Under',
                     'Posts - Out',
                     'Triple Blocks Front - Staged',
                     'Triple Block Front Arrow - In',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Rear - Up',
                     'Jack Front - Down',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Under',
                     'Home - Front lowered onto Dolly',
                     'Jack Front - Down & Out',
                     'Dolly Rear Arrow',
                     'Home - Front lowered onto Dolly rear raised',
                     'Home - Level on Dollies',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Up',
                     'Arrow Rear Down',
                     'Arrow Front Down',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': [],
     'numbers': {'arrow_front_up_2': (1, (2.62, 5.18)), 'triple_block_front_arrow_out_1': (2, (3.95, 3.81)), 'triple_block_front_arrow_out_2': (2, (1.93, 3.59)), 'dolly_front_arrow_1': (3, (5.65, 3.47)), 'dolly_front_arrow_2': (3, (0.60, 2.96))}},
    {'name': '11_front_dollies_in_place',
     'skp_scene': 'ISO - Front Dollies in place',
     'eye': (-3004.4694, 1488.2756, 86.458),
     'target': (-3126.5279, 1825.8335, 38.9187),
     'up': (-0.0446, 0.1235, 0.9913),
     'fov': 35.0,
     'zoom': 1.15, 'shift': (-0.72, -0.66),
     'hidden_tags': ['Tools',
                     'Home - Back Raised',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Front lowered onto Triple Block',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Staged',
                     'Posts - Under',
                     'Posts - Out',
                     'Triple Blocks Front - Under',
                     'Triple Blocks Front - Staged',
                     'Triple Block Front Arrow - In',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Rear - Up',
                     'Jack Front - Up',
                     'Jack Front - Down',
                     'Jack Rear - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Staged',
                     'Dolly Front Arrow',
                     'Home - Front lowered onto Dolly',
                     'Dolly Rear Arrow',
                     'Home - Level on Dollies',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Up',
                     'Arrow Rear Down',
                     'Arrow Front Up',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': []},
    {'name': '12_remove_rear_triple_blocks',
     'skp_scene': 'ISO - Remove Rear Triple Blocks',
     'eye': (-2938.6725, 2317.1551, 134.7265),
     'target': (-3280.5932, 1678.9957, -13.5663),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 1.08, 'shift': (0.088, -0.552),
     'hidden_tags': ['Tools',
                     'Iron Carts',
                     'Home - Back Raised',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Front lowered onto Triple Block',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Staged',
                     'Posts - Under',
                     'Triple Blocks Front - Under',
                     'Triple Block Front Arrow - In',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Front - Up',
                     'Jack Front - Down',
                     'Jack Rear - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Dolly Front Staged',
                     'Dolly Front Arrow',
                     'Home - Front lowered onto Dolly',
                     'Jack Front - Down & Out',
                     'Home - Level on Dollies',
                     'Jack Rear - Down & Out',
                     'Dolly Rear Under',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Down',
                     'Arrow Front Down',
                     'Arrow Front Up',
                     'Arrow Rear Down Final'],
     'show': [],
     'hide': [],
     'numbers': {'arrow_rear_up_2': (1, (3.43, 4.79)), 'triple_block_rear_arrow_out_1': (2, (2.05, 3.58)), 'triple_block_rear_arrow_out_2': (2, (3.90, 3.24)), 'dolly_rear_arrow_1': (3, (0.65, 4.08)), 'dolly_rear_arrow_2': (3, (5.25, 3.15))}},
    {'name': '13_home_in_final_position',
     'skp_scene': 'ISO - Home in Final Position',
     'eye': (-2938.6725, 2317.1551, 134.7265),
     'target': (-3280.5932, 1678.9957, -13.5663),
     'up': (-0.0948, -0.1769, 0.9797),
     'fov': 35.0,
     'zoom': 1.11, 'shift': (0.042, -0.728),
     'hidden_tags': ['Tools',
                     'Iron Carts',
                     'Home - Back Raised',
                     'Home - Level',
                     'Home - Level Raised',
                     'Home - Front lowered onto Triple Block',
                     'Home - Level on Triple Blocks',
                     'Triple Blocks Rear - Under',
                     'Posts - Under',
                     'Triple Blocks Front - Under',
                     'Triple Block Front Arrow - In',
                     'Triple Block Rear Arrow - In',
                     'Post Arrow - Out',
                     'Jack Rear - Up',
                     'Jack Front - Up',
                     'Jack Front - Down',
                     'Jack Rear - Down',
                     'Home - Front raised on Rear Triple Block',
                     'Triple Block Front Arrow - Out',
                     'Triple Block Rear Arrow - Out',
                     'Dolly Front Staged',
                     'Dolly Front Arrow',
                     'Home - Front lowered onto Dolly',
                     'Jack Front - Down & Out',
                     'Dolly Rear Staged',
                     'Dolly Rear Arrow',
                     'Home - Front lowered onto Dolly rear raised',
                     'Wall Framing',
                     'Floor Framing',
                     'Floor Insulation',
                     'Floor Sheeting',
                     'Arrow Rear Up',
                     'Arrow Rear Down',
                     'Arrow Front Down',
                     'Arrow Front Up'],
     'show': [],
     'hide': []},
]
