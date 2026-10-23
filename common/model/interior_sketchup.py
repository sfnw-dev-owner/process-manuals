"""Interior insulation and trim as modeled in SketchUp (converted), kept for
the iron-cart scenes that stage them. The house's interior is interior.py."""

from .common import *


@component
def interior_trim_raw():
    """SketchUp: 'Group#80'"""
    solids = []
    children = [
        (trim_vertical, Pos(88, 94.1061, 4), ['mirror'], ''),
        (trim_vertical, Pos(87.4768, 3 + 3/4, 4) * Rot(Z=90), ['mirror'], ''),
        (trim_vertical, Pos(88, 3.2921, 4), ['mirror'], ''),
        (trim_vertical, Pos(1/2, 94.1046, 4), ['mirror'], ''),
        (trim_vertical, Pos(2 + 1/2, 3 + 3/4, 4) * Rot(Z=90), ['mirror'], ''),
        (trim_vertical, Pos(1/2, 3.2921, 4), ['mirror'], ''),
        (trim_horizontal_short, Pos(0, 96 + 1/8, 34.0411), [], ''),
        (trim_horizontal_back, Pos(2.4768, 3 + 1/4, 83 + 15/16), [], ''),
        (trim_horizontal_short, Pos(87 + 1/2, 96 + 1/8, 34.0411), [], ''),
        (trim_horizontal_back, Pos(2.4768, 3 + 1/4, 34 + 3/16), [], ''),
        (trim_horizontal_short, Pos(0, 96 + 1/8, 83 + 15/16), [], ''),
        (trim_horizontal_short, Pos(87 + 1/2, 96 + 1/8, 83.9161), [], ''),
        (trim_horizontal_door_top, Pos(0.4768, 138 + 13/16, 83 + 15/16), [], ''),
        (trim_vertical, Pos(88, 137 + 5/16, 3.9786), ['mirror'], ''),
        (trim_vertical, Pos(87.4768, 139 + 5/16, 4) * Rot(Z=90), ['mirror'], ''),
        (trim_vertical, Pos(1/2, 137 + 5/16, 3.9786), ['mirror'], ''),
        (trim_vertical_door_side, Pos(5, 139 + 5/16, 0) * Rot(Z=90), ['mirror'], ''),
        (trim_long_baseboard, Pos(0, 3.2921, 0), [], ''),
        (trim_long_baseboard, Pos(87 + 1/2, 3.2921, 0), [], ''),
        (trim_vertical_door_side_1, Pos(46.7314, 139 + 5/16, 0) * Rot(Z=90), ['mirror'], ''),
        (trim_horizontal_door_top_1, Pos(4.9814, 138 + 13/16, 81 + 5/16), [], ''),
        (trim_horizontal_long, Pos(87 + 1/2, 5.2936, 34.0411), [], ''),
        (trim_horizontal_long, Pos(87 + 1/2, 5.2936, 83.9161), [], ''),
        (trim_horizontal_long, Pos(0, 5.2936, 83.9161), [], ''),
        (trim_horizontal_long, Pos(0, 5.2936, 34.0411), [], ''),
        (trim_baseboard_front, Pos(46 + 3/4, 138 + 13/16, -0.0214), [], ''),
        (trim_baseboard_back, Pos(0.4768, 3 + 1/4, 0.0356), [], ''),
        (interior_trim_horizontal_under_shelf_front, Pos(46.7268, 138 + 13/16, 34.0169), [], ''),  # Interior Trim - Horizontal under shelf front
        (trim_back_window, Pos(10 + 3/4, 0, 41), [], ''),
        (trim_front_window, Pos(46 + 1/4, 134 + 9/16, 41), [], ''),
    ]
    return solids, children


@component
def trim_vertical():
    """SketchUp: 'Trim - Vertical'"""
    solids = [
        board("1/2x2", 81 + 15/16, along="Z", wide="Y"),
    ]
    children = []
    return solids, children


@component
def trim_horizontal_short():
    """SketchUp: 'Trim - Horizontal Short'"""
    solids = [
        Pos(0, -0.0301, 0) * board("1/2x2", 41.2176, along="Y", wide="Z"),
    ]
    children = []
    return solids, children


@component
def trim_horizontal_back():
    """SketchUp: 'Trim - Horizontal Back'"""
    solids = [
        Pos(0, 1/2, 0) * Rot(X=90) * board("1/2x2", 83, along="X", wide="Y"),
    ]
    children = []
    return solids, children


@component
def trim_horizontal_door_top():
    """SketchUp: 'Trim - Horizontal Door Top'"""
    solids = [
        Pos(0, 1/2, 0) * Rot(X=90) * board("1/2x2", 85, along="X", wide="Y"),
    ]
    children = []
    return solids, children


@component
def trim_vertical_door_side():
    """SketchUp: 'Trim - Vertical Door Side'"""
    solids = [
        Pos(0, 0, 0) * Box(1/2, 4 + 1/2, 83 + 15/16, align=CORNER),
    ]
    children = []
    return solids, children


@component
def trim_long_baseboard():
    """SketchUp: 'Trim - Long Baseboard'"""
    solids = [
        Pos(0, 0, 0) * Box(1/2, 136.0205, 4, align=CORNER),
    ]
    children = []
    return solids, children


@component
def trim_vertical_door_side_1():
    """SketchUp: 'Trim - Vertical Door Side#1'"""
    solids = [
        Pos(0, 0, -0.0214) * Sheet(1/2, 6, 83.9589, facing="X"),
    ]
    children = []
    return solids, children


@component
def trim_horizontal_door_top_1():
    """SketchUp: 'Trim - Horizontal Door Top#1'"""
    solids = [
        Pos(0, 1/2, 0) * Rot(X=90) * board("1/2x2", 35 + 3/4, along="X", wide="Y"),
    ]
    children = []
    return solids, children


@component
def trim_horizontal_long():
    """SketchUp: 'Trim - Horizontal Long'"""
    solids = [
        Pos(0, 0, 0) * board("1/2x2", 88 + 13/16, along="Y", wide="Z"),
    ]
    children = []
    return solids, children


@component
def trim_baseboard_front():
    """SketchUp: 'Group#35'"""
    solids = [
        Pos(0, 0, 0) * Box(40 + 3/4, 1/2, 4, align=CORNER),
    ]
    children = []
    return solids, children


@component
def interior_trim_horizontal_under_shelf_front():
    """SketchUp: 'Group#86', 'Group#31'"""
    solids = [
        Pos(0.0186, 0, 0) * board("1/2x2", 38.7314, along="X", wide="Z"),
    ]
    children = []
    return solids, children


@component
def trim_perpendicular_window_interior_horizontal():
    """SketchUp: 'Trim - Perpendicular Window Interior Horizontal'"""
    solids = [
        Box(23, 3.275, 1/2, align=CORNER),
    ]
    children = []
    return solids, children


@component
def trim_perpendicular_window_interior_vertical():
    """SketchUp: 'Trim - Perpendicular Window Interior Vertical '"""
    solids = [
        Box(1/2, 3.275, 35 + 1/2, align=CORNER),
    ]
    children = []
    return solids, children


@component
def shelf_back():
    """SketchUp: 'Shelf - Back'"""
    solids = [
        (Pos(1, 3 + 1/4, 0) * TwoByFour(36, along="X", wide="Z")
            + extrude(Plane.XY.offset(3 + 1/2) * (Polygon((7, 3 + 1/4), (7, -0.025), (31, -0.025), (31, 3 + 1/4), (38, 3 + 1/4), (38, 8 + 1/16), (36 + 13/16, 9 + 1/4), (1 + 3/16, 9 + 1/4), (0, 8 + 1/16), (0, 3 + 1/4), align=None)), 1/2)),
    ]
    children = []
    return solids, children


@component
def trim_window_interior_horizontal_back():
    """SketchUp: 'Trim - Window Interior Horizontal Back'"""
    solids = [
        Pos(0.0299, 1/2, 0) * Rot(X=90) * board("1/2x2", 28.0326, along="X", wide="Y"),
    ]
    children = []
    return solids, children


@component
def trim_window_interior_vertical():
    """SketchUp: 'Trim - Window Interior Vertical'"""
    solids = [
        Pos(-0.0163, 0, 0) * Box(2.0163, 1/2, 35, align=CORNER),
    ]
    children = []
    return solids, children


@component
def shelf_front():
    """SketchUp: 'Shelf - Front'"""
    solids = [
        (Pos(0, 3 + 1/4, 0) * TwoByFour(37 + 1/2, along="X", wide="Z")
            + extrude(Plane.XY.offset(3 + 1/2) * (Polygon((38 + 5/16, 0.025), (38 + 5/16, 4 + 3/4), (23 + 15/16, 4 + 3/4), (24, 8.025), (0, 8.025), (0, 2.5846), (2 + 9/16, 0.025), align=None)), 1/2)),
    ]
    children = []
    return solids, children


@component
def trim_window_interior_horizontal_front():
    """SketchUp: 'Trim - Window Interior Horizontal Front'"""
    solids = [
        Pos(-0.0163, 1/2, 0) * Rot(X=90) * board("1/2x2", 25.5163, along="X", wide="Y"),
    ]
    children = []
    return solids, children


@component
def insulation():
    """SketchUp: 'Group#23'"""
    solids = []
    children = [
        (lhs_wall, Pos(95 + 5/8, 6 + 1/8, 0), ['mirror'], ''),  # LHS Wall
        (front_wall, Pos(50 + 7/16, 141 + 1/16, 3/8), [], ''),  # Front Wall
        (lhs_wall, Pos(3, 6 + 1/8, 0), ['mirror'], ''),  # RHS Wall
        (back_wall, Pos(90.5843, 3, 0) * Rot(Z=180), [], ''),  # Back Wall
    ]
    return solids, children


@component
def lhs_wall():
    """SketchUp: 'Group#22', 'Group#9'"""
    solids = []
    children = [
        *[(insulation_24, Pos(0, y, 0), [], '')
          for y in spaced(19 + 3/4, 23 + 3/4, 4)],  # 4 at 23 + 3/4" on center
        (insulation_16_side_wall, Location(), [], ''),
        (insulation_16_side_wall, Pos(0, 114 + 7/8, 0), [], ''),
    ]
    return solids, children


@component
def insulation_24():
    """SketchUp: 'Insulation - 24"'"""
    solids = [
        Box(3, 21 + 1/4, 83, align=CORNER),
    ]
    children = []
    return solids, children


@component
def insulation_16_side_wall():
    """SketchUp: 'Insulation - 16" Side Wall'"""
    solids = [
        Box(3, 17 + 1/4, 83, align=CORNER),
    ]
    children = []
    return solids, children


@component
def front_wall():
    """SketchUp: 'Group#12'"""
    solids = []
    children = [
        (insulation_15_skinny, Pos(25 + 3/8, 3, 0) * Rot(Z=-90), [], ''),
        (insulation_24_under_window, Pos(0, 3, 0) * Rot(Z=-90), [], ''),
    ]
    return solids, children


@component
def insulation_15_skinny():
    """SketchUp: 'Insulation - 15" Skinny'"""
    solids = [
        Box(3, 14 + 11/16, 83, align=CORNER),
    ]
    children = []
    return solids, children


@component
def insulation_24_under_window():
    """SketchUp: 'Insulation - 24" - Under Window'"""
    solids = [
        Box(3, 23 + 3/16, 40 + 13/16, align=CORNER),
    ]
    children = []
    return solids, children


@component
def back_wall():
    """SketchUp: 'Group#17'"""
    solids = []
    children = [
        (insulation_20_ac, Pos(21 + 15/16, 3, 0) * Rot(Z=-90), [], ''),
        (insulation_24_under_window, Pos(45 + 7/16, 3, 0) * Rot(Z=-90), [], ''),
        (insulation_20, Pos(0, 3, 0) * Rot(Z=-90), [], ''),
        (insulation_15_skinny, Pos(70 + 13/16, 3, 0) * Rot(Z=-90), [], ''),
    ]
    return solids, children


@component
def insulation_20_ac():
    """SketchUp: 'Insulation - 20" - AC'"""
    solids = [
        Box(3, 19 + 11/16, 65 + 13/16, align=CORNER),
    ]
    children = []
    return solids, children


@component
def insulation_20():
    """SketchUp: 'Insulation - 20"'"""
    solids = [
        Box(3, 19 + 11/16, 83, align=CORNER),
    ]
    children = []
    return solids, children


@component
def interior_panel_raw():
    """SketchUp: 'Group#107', 'Group#92', 'Group#21'"""
    solids = []
    children = [
        (interior_panel_front_wall, Pos(1, 136 + 9/16, 1/8), [], ''),  # Interior Panel - Front Wall
        (interior_panel_left_wall, Pos(89, 0.3399, 0), ['mirror'], ''),  # Interior Panel - Left Wall
        (interior_panel_left_wall, Pos(0, 0.3399, 0), [], ''),  # Interior Panel - Right Wall
        (interior_panel_back_wall, Pos(87.9814, 1/2, 0) * Rot(Z=180), [], ''),  # Interior Panel - Back Wall
    ]
    return solids, children


@component
def interior_panel_front_wall():
    """SketchUp: 'Group#96', 'Group#20'"""
    solids = []
    children = [
        (interior_panel_front_upper, Pos(0, 0, 35 + 3/16), [], ''),
        (interior_panel_front_lower, Pos(0, 0, -1/16), [], ''),
    ]
    return solids, children


@component
def interior_panel_front_upper():
    """SketchUp: 'Interior Panel - Front Upper'"""
    solids = [
        extrude(Plane.XZ.offset(-1/2) * (Polygon((87 + 3/16, 0), (87 + 3/16, 50.4003), (0, 50.4003), (0, 0), (3 + 1/2, 0), (3 + 1/2, 46 + 7/16), (41 + 1/4, 46 + 7/16), (41 + 1/4, 0), align=None) - Pos(45 + 3/4, 8 + 15/16) * Rectangle(24, 36, align=CORNER)), 1/2),
    ]
    children = []
    return solids, children


@component
def interior_panel_front_lower():
    """SketchUp: 'Interior Panel - Front Lower'"""
    solids = [
        Pos(41 + 1/4, 1/2, 0.0257) * Rot(X=90) * Sheet(1/2, 45 + 15/16, 35.2243, facing="Z"),
        Pos(0, 0, 0.0257) * Box(3 + 1/2, 1/2, 35.2243, align=CORNER),
    ]
    children = []
    return solids, children


@component
def interior_panel_left_wall():
    """SketchUp: 'Group#98', 'Group#18', 'Group#97'"""
    solids = []
    children = [
        (interior_panel_side_wall_upper_large, Pos(0, 0, 35 + 1/4), [], ''),
        (interior_panel_side_wall_lower_small, Pos(0, 92 + 5/16, 0), [], ''),
        (interior_panel_side_wall_lower_large, Location(), [], ''),
        (interior_panel_side_wall_upper_small, Pos(0, 92 + 5/16, 35 + 1/4), [], ''),
    ]
    return solids, children


@component
def interior_panel_side_wall_upper_large():
    """SketchUp: 'Interior Panel - Side Wall Upper Large'"""
    solids = [
        Sheet(1/2, 92, 50.4628, facing="X"),
    ]
    children = []
    return solids, children


@component
def interior_panel_side_wall_lower_small():
    """SketchUp: 'Interior Panel - Side Wall Lower Small'"""
    solids = [
        Sheet(1/2, 44 + 1/8, 35 + 1/4, facing="X"),
    ]
    children = []
    return solids, children


@component
def interior_panel_side_wall_lower_large():
    """SketchUp: 'Interior Panel - Side Wall Lower Large'"""
    solids = [
        Sheet(1/2, 92, 35 + 1/4, facing="X"),
    ]
    children = []
    return solids, children


@component
def interior_panel_side_wall_upper_small():
    """SketchUp: 'Interior Panel - Side Wall Upper Small'"""
    solids = [
        Sheet(1/2, 44 + 1/8, 50.4628, facing="X"),
    ]
    children = []
    return solids, children


@component
def interior_panel_back_wall():
    """SketchUp: 'Group#94', 'Group#19'"""
    solids = []
    children = [
        (interior_panel_back_upper, Pos(0, 0, 35 + 1/4), [], ''),
        (interior_panel_back_lower, Location(), [], ''),
    ]
    return solids, children


@component
def interior_panel_back_upper():
    """SketchUp: 'Interior Panel - Back Upper'"""
    solids = [
        extrude(Plane.XZ.offset(-1/2) * (Rectangle(87 + 3/16, 50.4628, align=CORNER) - Pos(45.7314, 9) * Rectangle(24, 36, align=CORNER)), 1/2),
    ]
    children = []
    return solids, children


@component
def interior_panel_back_lower():
    """SketchUp: 'Interior Panel - Back Lower'"""
    solids = [
        Pos(0, 0, 0.0257) * Sheet(1/2, 87 + 3/16, 35.2243, facing="Y"),
    ]
    children = []
    return solids, children


@component
def interior_trim_painted():
    """SketchUp: 'Group#34'"""
    solids = []
    children = [
        (trim_vertical, Pos(88 + 1/2, 94.1061, 29 + 15/16), ['mirror'], ''),
        (trim_vertical, Pos(87.9768, 3 + 3/4, 29 + 15/16) * Rot(Z=90), ['mirror'], ''),
        (trim_vertical, Pos(88 + 1/2, 3.2921, 29 + 15/16), ['mirror'], ''),
        (trim_vertical, Pos(1, 94.1046, 29 + 15/16), ['mirror'], ''),
        (trim_vertical, Pos(3, 3 + 3/4, 29 + 15/16) * Rot(Z=90), ['mirror'], ''),
        (trim_vertical, Pos(1, 3.2921, 29 + 15/16), ['mirror'], ''),
        (trim_horizontal_short, Pos(1/2, 96 + 1/8, 59.9786), [], ''),
        (trim_horizontal_back, Pos(2.9768, 3 + 1/4, 109 + 7/8), [], ''),
        (trim_horizontal_short, Pos(88, 96 + 1/8, 59.9786), [], ''),
        (trim_horizontal_back, Pos(2.9768, 3 + 1/4, 60 + 1/8), [], ''),
        (trim_horizontal_short, Pos(1/2, 96 + 1/8, 109 + 7/8), [], ''),
        (trim_horizontal_short, Pos(88, 96 + 1/8, 109.8536), [], ''),
        (trim_horizontal_door_top, Pos(0.9768, 138 + 13/16, 109 + 7/8), [], ''),
        (trim_vertical, Pos(88 + 1/2, 137 + 5/16, 29.9161), ['mirror'], ''),
        (trim_vertical, Pos(87.9768, 139 + 5/16, 29 + 15/16) * Rot(Z=90), ['mirror'], ''),
        (trim_vertical, Pos(1, 137 + 5/16, 29.9161), ['mirror'], ''),
        (trim_vertical_door_side, Pos(5 + 1/2, 139 + 5/16, 25 + 15/16) * Rot(Z=90), ['mirror'], ''),
        (trim_long_baseboard, Pos(1/2, 3.2921, 25 + 15/16), [], ''),
        (trim_long_baseboard, Pos(88, 3.2921, 25 + 15/16), [], ''),
        (trim_vertical_door_side_1, Pos(47.2314, 139 + 5/16, 25 + 15/16) * Rot(Z=90), ['mirror'], ''),
        (trim_horizontal_door_top_1, Pos(5.4814, 138 + 13/16, 107 + 1/4), [], ''),
        (trim_horizontal_long, Pos(1/2, 5.2936, 59.9786), [], ''),
        (trim_horizontal_long, Pos(88, 5.2936, 109.8536), [], ''),
        (trim_horizontal_long, Pos(1/2, 5.2936, 109.8536), [], ''),
        (trim_horizontal_long, Pos(88, 5.2936, 59.9786), [], ''),
        (trim_baseboard_front, Pos(47 + 1/4, 138 + 13/16, 25.9161), [], ''),  # Trim - Baseboard Front
        (trim_baseboard_back, Pos(0.9768, 3 + 1/4, 25.9731), [], ''),  # Trim - Baseboard Back
        (interior_trim_horizontal_under_shelf_front, Pos(47.2268, 138 + 13/16, 59.9544), [], ''),  # Interior Trim - Horizontal under shelf front
        (trim_back_window, Pos(11 + 1/4, 0, 66 + 15/16), [], ''),  # Trim - Back Window
        (trim_front_window, Pos(46 + 3/4, 134 + 9/16, 66 + 15/16), [], ''),  # Trim - Front Window
    ]
    return solids, children


@component
def trim_baseboard_back():
    """SketchUp: 'Group#30', 'Group#87'"""
    solids = [
        Pos(0, 0, 0) * Box(87, 1/2, 3.9644, align=CORNER),
    ]
    children = []
    return solids, children


@component
def trim_back_window():
    """SketchUp: 'Group#37', 'Group#85'"""
    solids = []
    children = [
        (trim_perpendicular_window_interior_horizontal, Pos(7 + 1/2, -0.025, 39), [], ''),
        (trim_perpendicular_window_interior_vertical, Pos(30 + 1/2, -0.025, 4), [], ''),
        (trim_perpendicular_window_interior_vertical, Pos(7, -0.025, 4), [], ''),
        (shelf_back, Location(), [], ''),
        (trim_window_interior_horizontal_back, Pos(4.9538, 3 + 1/4, 39), [], ''),
        (trim_window_interior_vertical, Pos(5 + 1/2, 3 + 1/4, 4), [], ''),
        (trim_window_interior_vertical, Pos(30.5163, 3 + 1/4, 4), [], ''),
    ]
    return solids, children


@component
def trim_front_window():
    """SketchUp: 'Group#38', 'Group#84'"""
    solids = []
    children = [
        (trim_perpendicular_window_interior_horizontal, Pos(1/2, 4 + 3/4, 39), [], ''),
        (trim_perpendicular_window_interior_vertical, Pos(23 + 1/2, 4 + 3/4, 4), [], ''),
        (trim_perpendicular_window_interior_vertical, Pos(0, 4 + 3/4, 4), [], ''),
        (shelf_front, Location(), [], ''),
        (trim_window_interior_horizontal_front, Pos(0.5163, 4 + 1/4, 39), [], ''),
        (trim_window_interior_vertical, Pos(23.5163, 4 + 1/4, 4), [], ''),
    ]
    return solids, children


