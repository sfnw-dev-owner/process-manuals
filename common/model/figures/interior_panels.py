"""Interior_Panels/interior_panels.md figures: each wall seen from inside
(framing and the installed panels), with its panels laid out loose above it
showing their preset screws; the ceiling panels flattened out of the slope."""

from build123d import Pos

from model.common import key
from model.interior import (
    PANEL_BOTTOM, SEAM_Z, END_GAP, panel_a, panel_b, panel_c, panel_d, panel_e, panel_g, panel_h,
    front_wall_interior, rear_wall_interior, side_wall_interior_door_side,
)
from model.interior_notes import (
    FLAT_VIEW, FRONT_PANELS_VIEW, INSIDE_VIEW, LOOSE, REAR_PANELS_VIEW, SIDE_PANELS_VIEW, TRIANGLE_PANELS_VIEW,
)
from model.interior_roof import (
    CEILING_VIEW, END_INTERIOR_AT, ceiling_half, end_wall_interior, half_triangle_left, half_triangle_right,
)
from model.walls import front_wall_framing, rear_wall_framing, side_wall_framing

from . import TYVEK, Figure, figure_names, placed_notes

MD = "Interior_Panels/interior_panels.md"
PANEL_FILL = TYVEK  # the drawings' light gray (ACI 9)


def placed(view, component, hidden=frozenset(), mods=()):
    return view * component.shape(frozenset(hidden), key(mods))


def loose(name, component, view=INSIDE_VIEW):
    x, y = LOOSE[name]
    return (Pos(x, y, 0) * view * component.shape(), "outline")


def installed(view, parts):
    """(component, location in the wall's frame) -> filled panel parts."""
    return [(view * loc * c.shape(), "outline", PANEL_FILL) for c, loc in parts]


def framing(view, component):
    return [(view * component.shape(), "outline")]


def notes(view, component, figure):
    return placed_notes(view, component, {"manual:interior_panels", f"manual:interior_panels:{figure}"})


def figures():
    ceiling_rest = {'', 'ceiling_trim'}
    r1_only = ceiling_rest | {'ceiling_r2'}
    ceiling = [
        loose("R1", _ceiling_panel("r1"), FLAT_VIEW), loose("R2", _ceiling_panel("r2"), FLAT_VIEW),
        # R1, then both, then both with the rafter screws: each view down from the last
        (Pos(0.42, 164.49, 0) * placed(CEILING_VIEW, ceiling_half, r1_only), "outline", PANEL_FILL),
        (Pos(-0.52, 87.79, 0) * placed(CEILING_VIEW, ceiling_half, ceiling_rest), "outline", PANEL_FILL),
        (placed(CEILING_VIEW, ceiling_half, ceiling_rest), "outline", PANEL_FILL),
    ]
    side = (
        [loose("A", panel_a), loose("B", panel_b), loose("C", panel_c)]
        + framing(SIDE_PANELS_VIEW, side_wall_framing)
        + [(placed(SIDE_PANELS_VIEW, side_wall_interior_door_side, TRIM_TAGS), "outline", PANEL_FILL)]
    )
    rear = (
        [loose("G", panel_g), loose("H", panel_h)] + framing(REAR_PANELS_VIEW, rear_wall_framing)
        + installed(REAR_PANELS_VIEW, [(panel_h, Pos(END_GAP, 0, PANEL_BOTTOM)), (panel_g, Pos(END_GAP, 0, SEAM_Z))])
    )
    front = (
        [loose("D", panel_d), loose("E", panel_e)] + framing(FRONT_PANELS_VIEW, front_wall_framing)
        + installed(FRONT_PANELS_VIEW, [(panel_d, Pos(END_GAP, 0, SEAM_Z))])
        + [(placed(FRONT_PANELS_VIEW, front_wall_interior, TRIM_TAGS | {'panel_d', 'panel_e2'}), "outline", PANEL_FILL)]
    )
    triangle_at = TRIANGLE_PANELS_VIEW * END_INTERIOR_AT
    triangle = (
        [(Pos(38.5 + 44.5, 12, 0) * INSIDE_VIEW * half_triangle_left.shape(), "outline"),
         (Pos(112.6, 12.38, 0) * INSIDE_VIEW * half_triangle_right.shape(), "outline")]
        + [(s, "outline") for s in (TRIANGLE_PANELS_VIEW * front_wall_framing.shape(),)]
        + [(placed(triangle_at, end_wall_interior, {'triangle_trim'}, ['mirror']), "new")]
    )
    steps = [
        ("ceiling", ceiling, CEILING_VIEW, ceiling_half),
        ("side", side, SIDE_PANELS_VIEW, side_wall_interior_door_side),
        ("rear", rear, REAR_PANELS_VIEW, rear_wall_interior),
        ("front", front, FRONT_PANELS_VIEW, front_wall_interior),
        ("triangle", triangle, triangle_at, end_wall_interior),
    ]
    return [Figure(MD, fig_name, parts, notes(view, component, name))
            for fig_name, (name, parts, view, component) in zip(figure_names(MD), steps)]


TRIM_TAGS = frozenset({
    "baseboards", "rear_shelf", "rear_window_trim", "top_trim", "vertical_trim", "horizontal_trim",
    "front_baseboard", "front_shelf", "front_window_trim", "front_trim_a", "front_trim_b", "final_trim",
})


def _ceiling_panel(which):
    from model.interior_roof import ceiling_panel_r1, ceiling_panel_r2
    return ceiling_panel_r1 if which == "r1" else ceiling_panel_r2
