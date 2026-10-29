"""The manuals' figures, drawn from the model.

A manual embeds a figure as `model:<manual>/<figure>@1:<N>`, e.g.
`#fullpage("model:platform/step_03@1:20")`{=typst}, for the drawing printed
at 1:N (so the manual chooses each figure's scale: an overview at 1:20, a
detail at 1:10); a page of 3D views (Figure.page) has its own size and takes
no scale. render/model2svg.py renders it to SVG (and caches it). <manual> is
the manual's file name, lowercased.

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

MODULES and FIGURES are plain literals: render/model2svg.py reads them
without importing anything.
"""

import importlib
import inspect
from dataclasses import dataclass, field

from build123d import Location, Plane, Pos, Vector

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
    eye: tuple = None
    target: tuple = None
    up: tuple = (0, 0, 1)
    parts: list = field(default_factory=list)  # (shape, "hlr" | "hlr_thin" | "hlr_light" (gray)), in the model's frame
    height: float = None
    fov: float = None
    notes: list = field(default_factory=list)  # (x, y, z, note) at points of the model, sized in page inches
    offset: tuple = (0, 0)  # the view's center, moved this far (page inches, y down)
    # A parallel view given logically instead: looking along `direction`
    # (toward the model), framed on `fit` (shapes; or the parts, by default)
    # with `margin` of the rect's size around them, whereupon the renderer
    # sets eye, target and height.
    direction: tuple = None
    fit: list = None
    margin: float = 0.05
    # Boxes drawn around the projections of some shapes: (shapes, color,
    # weight relative to notes.LINE, padding in page inches).
    highlights: list = field(default_factory=list)


@dataclass
class Figure:
    md: str  # the manual, relative to the repo
    name: str  # see FIGURES
    parts: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    paper_notes: bool = False  # its notes are in paper inches (model/notes.py); else (not yet converted) drawing inches
    # Only the parts' edges inside this box (x0, y0, x1, y1, in the drawing's
    # frame) are drawn, as if the drawing were cut off there; notes aren't cut.
    clip: tuple = None
    # A page of viewports (like a LayOut page): its (width, height) in
    # inches, and its notes as (x, y, note) in page inches from the top-left
    # corner, y down.
    page: tuple = None
    viewports: list = field(default_factory=list)

    @property
    def manual(self):
        return manual_of(self.md)


def manual_of(md):
    """A manual's name: its file name, lowercased, without .md."""
    return md.rsplit("/", 1)[-1].removesuffix(".md").lower()


def figure_names(md):
    """The names of a manual's figures, in order."""
    return FIGURES[manual_of(md)]


def manual_figures(manual, only=None, scale=1):
    """{name: Figure} for a manual, printed at `scale` (inches on paper per
    inch of drawing): just those named by `only`, if given (a module whose
    figures() takes `only` builds only those)."""
    module = importlib.import_module(f"model.figures.{MODULES[manual]}")
    params = inspect.signature(module.figures).parameters
    kw = {}
    if only is not None and "only" in params:
        kw["only"] = set(only)
    if "scale" in params:
        kw["scale"] = scale
    figures = module.figures(**kw)
    for f in figures:
        f.paper_notes = getattr(module, "PAPER_NOTES", False)
    return {f.name: f for f in figures if f.manual == manual and (only is None or f.name in only)}


def table(md, rows, tools_style=("outline", "laid")):
    """A manual's figures from its table: {name: (parts, tools, notes)},
    where tools are jig tools and the like as (component, Location) in the
    drawing's frame, drawn outlined and hatched."""
    out = []
    for name, (parts, tools, notes) in rows.items():
        parts = list(parts) + [(loc * tool.shape(), *tools_style) for tool, loc in tools]
        out.append(Figure(md, name, parts, list(notes)))
    return out


class Extent:
    """The axis-aligned box of some shapes (or other Extents) in the drawing,
    and points on it."""

    def __init__(self, *shapes):
        boxes = [(s.x0, s.y0, s.x1, s.y1) if isinstance(s, Extent) else
                 (s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().max.X, s.bounding_box().max.Y)
                 for s in shapes]
        self.x0, self.y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
        self.x1, self.y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)

    @classmethod
    def box(cls, x0, y0, x1, y1):
        e = cls.__new__(cls)
        e.x0, e.y0, e.x1, e.y1 = x0, y0, x1, y1
        return e

    @property
    def center(self):
        return (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.y1 - self.y0

    # the middle of each side, and the corners
    @property
    def left(self):
        return self.x0, (self.y0 + self.y1) / 2

    @property
    def right(self):
        return self.x1, (self.y0 + self.y1) / 2

    @property
    def top(self):
        return (self.x0 + self.x1) / 2, self.y1

    @property
    def bottom(self):
        return (self.x0 + self.x1) / 2, self.y0

    @property
    def top_left(self):
        return self.x0, self.y1

    @property
    def top_right(self):
        return self.x1, self.y1

    @property
    def bottom_left(self):
        return self.x0, self.y0

    @property
    def bottom_right(self):
        return self.x1, self.y0

    def point(self, fx, fy):
        """The point fx across and fy up the box (fractions from the lower-left)."""
        return self.x0 + fx * self.width, self.y0 + fy * self.height

    def meets(self, other):
        """The box where this and another overlap (a joint between two parts)."""
        out = Extent.__new__(Extent)
        out.x0, out.y0 = max(self.x0, other.x0), max(self.y0, other.y0)
        out.x1, out.y1 = min(self.x1, other.x1), min(self.y1, other.y1)
        return out


def extent(parts):
    """The Extent of figure parts ((shape, style, ...) entries) or shapes."""
    return Extent(*[p[0] if isinstance(p, tuple) else p for p in parts])


def xy(location):
    """A Location's (or Vector's) point as (x, y) of the drawing."""
    p = location.position if hasattr(location, "position") else location
    return p.X, p.Y


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


def break_box(width, height, broken=(), tooth=1/2):
    """A width x height rectangle (minimum corner at the origin) whose sides
    named in `broken` ("left", "right", "top", "bottom") zigzag: a detail
    cuts a part to it, and the ragged edge shows the part running on."""
    import math
    from build123d import Polygon

    def zigzag(p0, p1):
        (x0, y0), (x1, y1) = p0, p1
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(length / (2 * tooth)))
        nx, ny = -(y1 - y0) / length * tooth, (x1 - x0) / length * tooth
        return [(x0 + (x1 - x0) * i / n + (nx if i % 2 else -nx), y0 + (y1 - y0) * i / n + (ny if i % 2 else -ny))
                for i in range(1, n)]
    corners = [(0, 0), (width, 0), (width, height), (0, height)]
    sides = ["bottom", "right", "top", "left"]
    pts = []
    for i, side in enumerate(sides):
        a, b = corners[i], corners[(i + 1) % 4]
        pts.append(a)
        if side in broken:
            pts += zigzag(a, b)
    return Polygon(*pts, align=None)


def enlarged(shape, view, factor, at):
    """A detail: `shape` seen through `view` (a camera Location), scaled by
    `factor`, centered at `at` in the drawing; and the Location taking a
    point of the shape to the drawing."""
    from build123d import scale
    seen = scale(view * shape, by=factor)
    bb = seen.bounding_box()
    move = Pos(at[0] - bb.center().X, at[1] - bb.center().Y, 0)

    def to_drawing(point):
        p = (view * Pos(*point)).position
        return at[0] + factor * p.X - bb.center().X + 0, at[1] + factor * p.Y - bb.center().Y
    return move * seen, to_drawing


def camera(direction, up=(0, 0, 1)):
    """The Location taking the model to a drawing looking from `direction`
    (toward the model), `up` pointing up the page: e.g. camera((1, -1, 1))
    for an isometric view from the front right."""
    z = Vector(*direction).normalized()
    x = Vector(*up).cross(z).normalized()
    return Location(Plane((0, 0, 0), x_dir=x, z_dir=z)).inverse()
