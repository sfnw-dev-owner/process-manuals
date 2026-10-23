"""The manuals' figures, drawn from the model.

A manual embeds a figure as `model:<manual>/<figure>`, e.g.
`#fullpage("model:platform/step_03")`{=typst}; render/model2svg.py renders
it to SVG (and caches it). <manual> is the manual's file name, lowercased.

MODULES says which module here describes each manual's figures; its
figures() returns them, in the manual's order, named by FIGURES. A figure has:

  parts   model parts already placed in the drawing's frame (inches, looking
          down -Z, X right, Y up), as (shape, style), (shape, style, fill) or
          (shape, style, fill, clip):
            "jig"      the whole assembly's outline, faint (every step)
            "context"  parts already in place: filled gray, faintly outlined
            "covered"  parts under sheathing, showing through it: dark gray
                       lines, no fill
            "heavy"    a thick black outline (a new part that can't be filled
                       black, e.g. insulation)
            "new"      the parts this step adds: outlined, filled black
            "outline"  outlined only
            "bare"     not outlined (give it a fill)
            "hlr"      3D views: all of a figure's "hlr" parts drawn together,
                       only their visible edges (hidden-line removal), no fill
            "hlr_thin" the same, thinner lines (projected separately from "hlr")
          fill overrides the style's fill: a color, "foam" (insulation hatch),
          "glass", "plywood", or "laid" (laid in place, not yet fastened, or a
          jig tool)
          clip (not for "hlr" styles) cuts the part's own edges to a box (x0,
          y0, x1, y1) in the drawing, as Figure.clip does for every part
  notes   annotations (model/notes.py) as (x, y, note) in the drawing's frame

MODULES, FIGURES, SIZES and FRAMES are plain literals: render/model2svg.py
reads them without importing anything.
"""

import importlib
import inspect
from dataclasses import dataclass, field

from build123d import Location, Plane, Vector

from model.notes import Label

# manual -> module (in this package) describing its figures
MODULES = {
    'platform': 'platform',
    'sidewall_1': 'walls',
    'sidewall_3': 'walls',
    'front_wall_ada': 'walls',
    'rear_wall': 'walls',
    'half_roof': 'half_roof',
    'exterior_trim': 'exterior_trim',
    'roof_manual': 'roof_manual',
    'structural_triangle_parts': 'triangle_parts',
    'interior_panels': 'interior_panels',
    'interior_trim': 'interior_trim',
    'vent_cap_install': 'vent_cap',
    'door_manual': 'door',
    'floor_install': 'floor',
    'extract_instructions': 'extract_instructions',
    'tilt-up': 'tilt_up',
    'frame-completion': 'post_tilt_up',
    'roof-blocking': 'post_tilt_up',
    'triangle': 'structural_triangle',
}

# manual -> its figures' names, in the manual's order
FIGURES = {
    'platform': ['step_01', 'step_02', 'step_03', 'step_04', 'step_05', 'step_06', 'step_07', 'step_08', 'step_09', 'step_10', 'step_11', 'step_12'],
    'sidewall_1': ['step_01', 'step_02', 'step_03', 'step_04', 'step_05', 'step_06', 'step_07'],
    'sidewall_3': ['step_01', 'step_02', 'step_03', 'step_04', 'step_05', 'step_06', 'step_07'],
    'front_wall_ada': ['step_01', 'step_02', 'step_03', 'step_04', 'step_05', 'step_06', 'step_07', 'step_08', 'step_09', 'step_10', 'step_11'],
    'rear_wall': ['step_01', 'step_02', 'step_03', 'step_04', 'step_04b', 'step_05', 'step_06', 'step_07', 'step_08'],
    'half_roof': ['step_01', 'step_02', 'step_03', 'step_04', 'step_05', 'step_06', 'step_07'],
    'exterior_trim': ['corners_1', 'corners_2', 'rear_window', 'front_window', 'triangles_1_2', 'triangles_3_4'],
    'roof_manual': ['start_end_shingles', 'panel_options'],
    'structural_triangle_parts': ['parts'],
    'interior_panels': ['ceiling_panels', 'side_panels', 'rear_panels', 'front_panels', 'triangle_panels'],
    'interior_trim': ['baseboards', 'rear_shelf', 'rear_window_trim', 'top_trim', 'vertical_trim', 'horizontal_trim', 'triangle_trim', 'front_window', 'front_trim_a', 'front_trim_b', 'final_trim'],
    'vent_cap_install': ['vent_cap'],
    'door_manual': ['door', 'threshold', 'screw_locations', 'shimming', 'strike_plate'],
    'floor_install': ['tiles'],
    'extract_instructions': ['01_prepare', '02_rear_raised', '03_rear_dropped_onto_posts', '04_front_raised', '05_carts_removed', '07_lowered_onto_front_triple_blocks', '08_rear_remove_posts', '09_rear_lowered_onto_triple_blocks', '10_remove_front_triple_blocks', '11_front_dollies_in_place', '12_remove_rear_triple_blocks', '13_home_in_final_position'],
    'tilt-up': ['rhs_jig', 'rhs_tilting', 'rhs_upright', 'rhs_brace', 'rhs_mississippis', 'back_jig', 'back_off_jig', 'back_to_platform', 'back_raise', 'back_clear_hands', 'back_slide', 'back_clamp', 'back_mississippis', 'back_nail', 'lhs_jig', 'lhs_tilted', 'lhs_clear_hands', 'lhs_slide', 'lhs_clamp', 'lhs_mississippis', 'lhs_side_nails', 'front_jig', 'front_off_jig', 'front_to_platform', 'front_align', 'front_tilted', 'front_upright', 'front_clamp', 'front_mississippis', 'front_nail'],
    'frame-completion': ['secure_walls', 'corner_screws_front', 'corner_screws_rear', 'triangles', 'triangle_centered', 'triangle_clamped', 'triangle_screws', 'half_roof_setup', 'raise_half_roof', 'raise_half_roof_up', 'align_half_roof', 'second_half_roof_setup', 'raise_second_half_roof', 'second_half_roof_on', 'join_half_roofs', 'ridge_screws'],
    'roof-blocking': ['ridge_beam_bay', 'ridge_beam', 'align_magic_rafters', 'magic_lag_bolts', 'bracket_screws', 'all_lag_bolts', 'insert_bird_block', 'tap_bird_block', 'bird_block_screws', 'all_bird_blocks', 'vent_guide_board', 'align_vent_block', 'vent_block_screws', 'all_vent_blocks'],
    'triangle': ['step_1', 'step_2', 'step_3', 'step_4', 'step_5'],
}

# manual -> its figures' printed size: inches on paper per inch of drawing,
# or {figure: that} (the scale QCAD printed the drawings they replaced at,
# measured from those PDFs, so the manuals' layouts stay put)
SIZES = {
    'platform': 0.054,
    'sidewall_1': 0.045,
    'sidewall_3': 0.045,
    'front_wall_ada': 0.0491,
    'rear_wall': 0.06,
    'half_roof': 0.05,
    'exterior_trim': {'corners_1': 0.02, 'corners_2': 0.02, 'rear_window': 0.1, 'front_window': 0.1,
                      'triangles_1_2': 0.05, 'triangles_3_4': 0.05},
    'roof_manual': {'start_end_shingles': 0.0785, 'panel_options': 0.04},
    'structural_triangle_parts': 0.07,
    'interior_panels': {'ceiling_panels': 0.0255, 'side_panels': 0.0329, 'rear_panels': 0.0329,
                        'front_panels': 0.0329, 'triangle_panels': 0.0329},
    'interior_trim': {'baseboards': 0.023, 'rear_shelf': 0.032, 'rear_window_trim': 0.032, 'top_trim': 0.023,
                      'vertical_trim': 0.023, 'horizontal_trim': 0.023, 'triangle_trim': 0.023,
                      'front_window': 0.023, 'front_trim_a': 0.023, 'front_trim_b': 0.023, 'final_trim': 0.023},
    'vent_cap_install': 0.0406,
    'door_manual': 0.06,
    'floor_install': 0.0459,
    'triangle': 0.07,
}

# figure -> white around its drawing (left, top, right, bottom), in inches of
# drawing, as QCAD's print-to-PDF left it around the drawing the figure replaced
# (measured from those PDFs), so each manual's pages don't move. Where a figure
# isn't listed, render/model2svg.py's MARGIN applies all around. These are to
# be dropped once the new figures are blessed: see ../TODO.md.
FRAMES = {
    'structural_triangle_parts/parts': (2.9, 1.6, 1.6, 3.2),
    'exterior_trim/corners_1': (4.0, 0.0, 0.4, 4.9),
    'exterior_trim/corners_2': (3.5, 0.0, 0.7, 4.6),
    'exterior_trim/rear_window': (2.5, 2.1, 2.2, 2.4),
    'exterior_trim/front_window': (2.5, 2.3, 2.3, 2.4),
    'exterior_trim/triangles_1_2': (3.0, 1.4, 1.4, 3.5),
    'exterior_trim/triangles_3_4': (3.0, 1.4, 1.4, 3.5),
    'front_wall_ada/step_01': (3.1, 1.0, 1.4, 3.3),
    'front_wall_ada/step_02': (3.1, 0.8, 1.4, 3.3),
    'front_wall_ada/step_03': (3.1, 0.8, 1.4, 3.3),
    'front_wall_ada/step_04': (3.1, 1.4, 1.1, 3.2),
    'front_wall_ada/step_05': (3.1, 0.8, 1.2, 2.5),
    'front_wall_ada/step_06': (3.1, 0.8, 2.6, 2.5),
    'front_wall_ada/step_07': (3.1, 0.8, 1.0, 2.5),
    'front_wall_ada/step_08': (3.3, 0.8, 1.3, 3.3),
    'front_wall_ada/step_09': (3.1, 0.8, 1.7, 3.3),
    'front_wall_ada/step_10': (3.1, 0.8, 1.1, 3.3),
    'front_wall_ada/step_11': (3.1, 0.8, 1.3, 3.3),
    'half_roof/step_01': (3.0, 1.0, 1.1, 3.4),
    'half_roof/step_02': (3.0, 0.8, 1.4, 3.7),
    'half_roof/step_03': (3.0, 1.6, 1.1, 4.0),
    'half_roof/step_04': (3.0, 1.0, 1.4, 3.4),
    'half_roof/step_05': (3.0, 1.4, 1.1, 3.7),
    'half_roof/step_06': (3.0, 1.6, 1.1, 3.7),
    'half_roof/step_07': (3.0, 1.0, 1.1, 3.4),
    'interior_panels/ceiling_panels': (2.7, 1.2, 1.9, 2.6),
    'interior_panels/side_panels': (3.0, 1.2, 2.0, 2.3),
    'interior_panels/rear_panels': (2.7, 2.7, 1.9, 2.2),
    'interior_panels/front_panels': (2.4, 2.7, 1.9, 2.2),
    'interior_panels/triangle_panels': (2.4, 1.8, 1.7, 2.3),
    'interior_trim/baseboards': (2.2, 0.9, 1.4, 2.3),
    'interior_trim/rear_shelf': (2.2, 1.9, 2.0, 2.2),
    'interior_trim/rear_window_trim': (2.2, 1.9, 1.7, 2.2),
    'interior_trim/top_trim': (2.2, 0.9, 1.1, 2.3),
    'interior_trim/vertical_trim': (2.2, 0.9, 2.0, 2.1),
    'interior_trim/horizontal_trim': (2.2, 0.9, 2.0, 2.2),
    'interior_trim/triangle_trim': (2.2, 1.7, 1.7, 2.1),
    'interior_trim/front_window': (2.2, 0.9, 0.7, 2.1),
    'interior_trim/front_trim_a': (2.6, 1.7, 0.9, 2.4),
    'interior_trim/front_trim_b': (2.2, 2.2, 1.8, 2.2),
    'interior_trim/final_trim': (2.2, 1.3, 1.9, 2.2),
    'vent_cap_install/vent_cap': (3.2, 0.7, 1.5, 3.7),
    'platform/step_01': (2.4, 2.8, 2.3, 2.5),
    'platform/step_02': (2.4, 2.6, 2.3, 2.5),
    'platform/step_03': (2.4, 2.6, 2.3, 2.4),
    'platform/step_04': (2.4, 2.2, 2.0, 2.4),
    'platform/step_05': (2.4, 2.2, 2.0, 2.4),
    'platform/step_06': (3.9, 2.63, 3.5, 3.07),  # rebalanced: the ink sat 1.3 right and 0.9 high of the drawing's
    'platform/step_07': (2.4, 2.2, 2.0, 2.4),
    'platform/step_08': (2.4, 2.0, 1.8, 2.4),
    'platform/step_09': (2.4, 2.0, 2.0, 2.4),
    'platform/step_10': (2.4, 2.0, 2.0, 2.4),
    'platform/step_11': (2.4, 2.2, 2.0, 2.4),
    'platform/step_12': (2.4, 2.0, 2.5, 2.4),
    'rear_wall/step_01': (2.5, 2.3, 2.2, 2.3),
    'rear_wall/step_02': (2.3, 2.3, 2.2, 2.5),
    'rear_wall/step_03': (2.3, 2.3, 2.2, 2.4),
    'rear_wall/step_04': (2.3, 2.5, 2.2, 2.4),
    'rear_wall/step_04b': (2.3, 2.0, 2.2, 2.4),
    'rear_wall/step_05': (2.3, 2.2, 1.8, 2.4),
    'rear_wall/step_06': (2.5, 2.2, 2.4, 2.4),
    'rear_wall/step_07': (2.3, 2.2, 2.5, 2.3),
    'rear_wall/step_08': (2.3, 2.3, 1.8, 2.4),
    'roof_manual/start_end_shingles': (2.3, 2.2, 2.1, 2.4),
    'roof_manual/panel_options': (2.2, 2.0, 2.2, 2.4),
    'sidewall_1/step_01': (3.1, 2.0, 1.3, 3.4),
    'sidewall_1/step_02': (3.3, 0.7, 1.6, 3.4),
    'sidewall_1/step_03': (3.1, 1.1, 0.9, 3.5),
    'sidewall_1/step_04': (3.1, 1.1, 2.0, 3.5),
    'sidewall_1/step_05': (3.1, 1.1, 1.1, 3.5),
    'sidewall_1/step_06': (3.1, 0.7, 1.4, 3.5),
    'sidewall_1/step_07': (3.1, 0.9, 1.7, 3.6),
    'sidewall_3/step_01': (3.1, 2.0, 1.3, 3.4),
    'sidewall_3/step_02': (3.3, 0.7, 1.6, 3.4),
    'sidewall_3/step_03': (3.1, 1.1, 0.9, 3.5),
    'sidewall_3/step_04': (3.1, 1.1, 2.0, 3.5),
    'sidewall_3/step_05': (3.1, 1.1, 1.1, 3.5),
    'sidewall_3/step_06': (3.1, 0.7, 1.6, 3.5),
    'sidewall_3/step_07': (3.1, 0.9, 1.7, 3.6),
    'triangle/step_1': (2.9, 1.1, 2.0, 3.2),
    'triangle/step_2': (2.9, 1.3, 2.0, 3.3),
    'triangle/step_3': (2.9, 1.1, 2.0, 3.2),
    'triangle/step_4': (2.9, 1.6, 2.0, 3.2),
    'triangle/step_5': (2.9, 1.7, 2.0, 3.3),
    'door_manual/door': (2.5, 1.8, 2.1, 2.5),
    'door_manual/threshold': (2.5, 2.3, 1.9, 2.5),
    'door_manual/screw_locations': (2.3, 2.2, 2.3, 2.4),
    'door_manual/shimming': (2.5, 2.0, 2.0, 2.4),
    'door_manual/strike_plate': (2.5, 2.2, 2.0, 2.4),
    'floor_install/tiles': (2.4, 1.7, 2.1, 13.9),
}

BLACK, DARK, EDGE, GRAY, LIGHT = (0, 0, 0), (96, 96, 96), (140, 140, 140), (160, 160, 160), (170, 170, 170)
TYVEK = (192, 192, 192)


@dataclass
class Viewport:
    """One camera view on a page (as LayOut places SketchUp scenes): the parts
    seen from `eye` toward `target` (`up` up the page), drawn in `rect`
    (x, y, width, height: page inches from the top-left corner, y down) and
    clipped to it, the target at its center. A parallel view shows `height`
    inches of the model top to bottom; a perspective one (`fov` degrees,
    vertical) as much as that angle takes in at the target."""
    rect: tuple
    eye: tuple
    target: tuple
    up: tuple
    parts: list = field(default_factory=list)  # (shape, "hlr" | "hlr_thin" | "hlr_light" (gray)), in the model's frame
    height: float = None
    fov: float = None
    notes: list = field(default_factory=list)  # (x, y, z, note) at points of the model, sized in page inches
    offset: tuple = (0, 0)  # the view's center, moved this far (page inches, y down)


@dataclass
class Figure:
    md: str  # the manual, relative to the repo
    name: str  # see FIGURES
    parts: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    # Only the parts' edges inside this box (x0, y0, x1, y1, in the drawing's
    # frame) are drawn, as if the drawing were cut off there; notes aren't cut.
    clip: tuple = None
    # A page of viewports (like a LayOut page): its (width, height) in
    # inches, and its notes as (x, y, note) in page inches from the top-left
    # corner, y down.
    page: tuple = None
    viewports: list = field(default_factory=list)
    size: object = None  # printed size, from SIZES
    frame: tuple = None  # white around the drawing (left, top, right, bottom), from FRAMES
    border: float = None  # a page's hairline border, inches (as LayOut's exports had)
    light: str = None  # a page's "hlr_light" gray (CSS color), if not render/model2svg.py's default

    @property
    def manual(self):
        return manual_of(self.md)


def manual_of(md):
    """A manual's name: its file name, lowercased, without .md."""
    return md.rsplit("/", 1)[-1].removesuffix(".md").lower()


def figure_names(md):
    """The names of a manual's figures, in order."""
    return FIGURES[manual_of(md)]


def manual_figures(manual, only=None):
    """{name: Figure} for a manual: just those named by `only`, if given
    (a module whose figures() takes `only` builds only those)."""
    module = importlib.import_module(f"model.figures.{MODULES[manual]}")
    if only is not None and "only" in inspect.signature(module.figures).parameters:
        figures = module.figures(only=set(only))
    else:
        figures = module.figures()
    out = {f.name: f for f in figures if f.manual == manual and (only is None or f.name in only)}
    size = SIZES.get(manual)
    for name, f in out.items():
        f.size = size.get(name) if isinstance(size, dict) and "width" not in size else size
        f.frame = FRAMES.get(f"{manual}/{name}")
    return out


def placed(component, name):
    """The child of `component`'s placement whose function is called `name`,
    as (child, Location, mods, tag). Fails, naming the children there are,
    rather than silently finding nothing."""
    children = component()[1]
    found = [c for c in children if c[0].__name__ == name]
    if len(found) != 1:
        raise LookupError(f"{component.__name__} has {len(found)} children named {name!r}; "
                          f"its children are {sorted({c[0].__name__ for c in children})}")
    return found[0]


def placed_notes(to_drawing, component, shown, loc=Location()):
    """A component's annotations that `shown` asks for, as (x, y, note) in
    the drawing's frame."""
    out = []
    for l, note in component.notes(shown):
        p = (to_drawing * loc * l).position
        out.append((p.X, p.Y, note))
    return out


def optional_parts(to_drawing, component, shown, style, fill=None):
    """The optional (tagged) parts of a component that `shown` asks for,
    placed in the drawing, as figure parts."""
    from model.common import OPTIONAL, key, shown_by
    from model.notes import Note
    out = []
    for child, loc, mods, tag in component()[1]:
        if tag.startswith(OPTIONAL) and shown_by(tag, shown) and not isinstance(child, Note):
            shape = to_drawing * (loc * child.shape(frozenset(), key(mods), shown))
            out.append((shape, style) if fill is None else (shape, style, fill))
    return out


def vertical_fov(fov, rect):
    """A Viewport's (vertical) fov for a SketchUp camera's in a LayOut view,
    whose angle spans the view's shorter side: rect is (x, y, width, height)."""
    import math
    w, h = rect[2], rect[3]
    return fov if w >= h else math.degrees(2 * math.atan(math.tan(math.radians(fov) / 2) * h / w))


def title(text, x, y, height=3, rotation=0, runs=None):
    """A figure's caption, e.g. "Step 3", at (x, y) in the drawing (its
    top-left corner); `runs` for pieces of different heights."""
    return (x, y, Label(text, height, attach=1, rotation=rotation, runs=runs))


def camera(direction, up=(0, 0, 1)):
    """The Location taking the model to a drawing looking from `direction`
    (toward the model), `up` pointing up the page: e.g. camera((1, -1, 1))
    for an isometric view from the front right."""
    z = Vector(*direction).normalized()
    x = Vector(*up).cross(z).normalized()
    return Location(Plane((0, 0, 0), x_dir=x, z_dir=z)).inverse()
