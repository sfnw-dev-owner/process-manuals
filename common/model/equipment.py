"""Iron carts, jacks, triple blocks, 4x4 stands, dollies and arrows."""

from .common import *
from .parts import (
    cross_bar,
)


@component
def iron_cart():
    """SketchUp: 'Iron Cart'"""
    solids = []
    children = [
        (tab_4in, Pos(133 + 7/16, 16 + 1/4, 11 + 7/16) * Rot(Z=180), ['mirror'], ''),
        (tab_4in, Pos(6 + 7/16, 16 + 1/4, 11 + 7/16) * Rot(Z=180), [], ''),
        (tab_4in, Pos(6 + 7/16, 19 + 3/4, 11 + 7/16), ['mirror'], ''),
        (iron_cart_caster, Pos(6 + 15/16, 32.0204, 0) * Rot(Z=90), [], ''),
        (iron_cart_caster, Pos(6 + 15/16, 0.0204, 0) * Rot(Z=90), [], ''),
        (tab_4in, Pos(133 + 7/16, 19 + 3/4, 11 + 7/16), [], ''),
        (iron_cart_caster, Pos(137.4567, 0.0204, 0) * Rot(Z=90), [], ''),
        (iron_cart_caster, Pos(137.4567, 32.0204, 0) * Rot(Z=90), [], ''),
        (outershell_2, Pos(2 + 7/16, 0, 7 + 7/16), [], ''),  # OuterShell
    ]
    return solids, children


@component
def tab_4in():
    """SketchUp: 'Tab_4in'"""
    solids = [
        # approximate: 1% of surface area not modeled
        (Pos(0, 1/4, 0) * Box(1/4, 3 + 3/4, 4, align=CORNER)
            + extrude(Plane.XZ.offset(-1/4) * (make_face(Wire([ThreePointArc((4, 3), (3.7071, 3.7071), (3, 4)), Line((3, 4), (0, 4)), Line((0, 4), (0, 0)), Line((0, 0), (4, 0)), Line((4, 0), (4, 3))]))), 1/4)),
    ]
    children = []
    return solids, children


@component
def iron_cart_caster():
    """SketchUp: '01CSTBRKVP#1'"""
    solids = [
        # hand-modeled stand-in (hardware.py)
        cart_caster(lo=(-0.0204, 0.0192, 0), hi=(3.9796, 6.9706, 7 + 7/16)),
    ]
    children = []
    return solids, children


@component
def outershell_2():
    """SketchUp: 'OuterShell#2'"""
    solids = [
        (extrude(Plane.XY * (Rectangle(135, 36, align=CORNER) - Pos(1/4, 1/4) * Rectangle(134 + 1/2, 35 + 1/2, align=CORNER)), 3 + 3/4)
            + extrude(Plane.XY.offset(3 + 3/4) * (Rectangle(135, 36, align=CORNER) - Pos(4, 4) * Rectangle(127, 28, align=CORNER)), 1/4)),
    ]
    children = []
    return solids, children


@component
def _2x8_block():
    """SketchUp: '2x8 Block'"""
    solids = []
    children = [
        *[(block_2x8, Pos(0, 0, z), [], '')
          for z in spaced(0, 1 + 1/2, 4)],  # 4 side by side
    ]
    return solids, children


@component
def block_2x8():
    """SketchUp: '24in 2x8'"""
    solids = [
        TwoByEight(18, along="Y", wide="X"),
    ]
    children = []
    return solids, children


@component
def car_wheel_caster():
    """SketchUp: 'car_wheel_caster'"""
    solids = []
    children = [
        (car_caster, Location(), [], ''),
    ]
    return solids, children


@component
def car_caster():
    """SketchUp: 'car_caster'"""
    solids = []
    children = [
        (half_plate_car_caster, Pos(16, 0.0233, 1.8934), ['mirror'], ''),
        (half_plate_car_caster, Pos(0, 0.0233, 1.8934), [], ''),
        (car_dolly_caster, Pos(1 + 13/16, 3/16, 0) * Rot(Z=90), [], ''),
        (car_dolly_caster, Pos(15 + 13/16, 3/16, 0) * Rot(Z=90), [], ''),
        (car_dolly_caster, Pos(15 + 13/16, 10 + 3/16, 0) * Rot(Z=90), [], ''),
        (car_dolly_caster, Pos(1 + 13/16, 10 + 3/16, 0) * Rot(Z=90), [], ''),
    ]
    return solids, children


@component
def half_plate_car_caster():
    """SketchUp: 'half_plate_car_caster'"""
    solids = [
        extrude(Plane.XZ.offset(-12) * (make_face(Wire([ThreePointArc((2 + 5/16, 1 + 7/8), (2 + 1/16, 1.9669), (1.7778, 2)), Line((1.7778, 2), (0, 2)), Line((0, 2), (0, 1 + 3/4)), Line((0, 1 + 3/4), (1.7778, 1 + 3/4)), ThreePointArc((1.7778, 1 + 3/4), (2, 1.7241), (2 + 3/16, 1.6477)), Line((2 + 3/16, 1.6477), (5 + 3/16, 0.0988)), ThreePointArc((5 + 3/16, 0.0988), (5 + 3/8, 0.0251), (5.5896, 0)), Line((5.5896, 0), (8, 0)), Line((8, 0), (8, 1/4)), Line((8, 1/4), (5.5896, 1/4)), ThreePointArc((5.5896, 1/4), (5 + 7/16, 0.2679), (5 + 5/16, 5/16)), Line((5 + 5/16, 5/16), (2 + 5/16, 1 + 7/8))]))), 12),
    ]
    children = []
    return solids, children


@component
def car_dolly_caster():
    """SketchUp: 'Group#242'"""
    solids = [
        # hand-modeled stand-in (hardware.py)
        dolly_caster(lo=(0.0233, -0.0263, 0), hi=(3 + 7/16, 1 + 13/16, 3.8933)),
    ]
    children = []
    return solids, children


@component
def jack_2_1():
    """SketchUp: 'Jack 2#1', 'Jack Lowered All the way'"""
    solids = []
    children = [
        (pad, Pos(24, 0, 11 + 5/16), [('scale', (1.5, 1.5, 1.0))], ''),
        (pad, Pos(6, 0, 11 + 5/16), ['mirror', ('scale', (1.5, 1.5, 1.0))], ''),
        (cross_bar, Pos(3, 1 + 1/4, 9 + 13/16), [], ''),
        (jack_rear_axle, Pos(1.2796, 0.2896, 0), [], ''),
        (jack_handle, Pos(10.9563, 18.8961, 7.269), [], ''),
    ]
    return solids, children


@component
def pad():
    """SketchUp: 'Pad'"""
    solids = [
        Box(4, 4, 1/2, align=CORNER),
    ]
    children = []
    return solids, children


@component
def jack_rear_axle():
    """SketchUp: 'Group#308'"""
    solids = []
    children = [
        (jack_chassis, Location(), [], ''),
    ]
    return solids, children


WHEEL_WIDTH, AXLE_RADIUS = 1 + 1/2, 1/2


def _wheel_pair(x, y, z, radius, span):
    """Two wheels `span` apart (outside to outside) on an axle along X,
    centered at (x, y, z)."""
    half = span / 2
    wheel = lambda x0: Pos(x0, y, z) * Rot(Y=90) * Cylinder(radius, WHEEL_WIDTH)
    return [wheel(x - half + WHEEL_WIDTH / 2), wheel(x + half - WHEEL_WIDTH / 2),
            Pos(x, y, z) * Rot(Y=90) * Cylinder(AXLE_RADIUS, span - WHEEL_WIDTH)]


@component
def jack_chassis():
    """SketchUp: 'Group#296'"""
    solids = [
        # (the meshes were a pair of wheels each, on an axle)
        *_wheel_pair(23.7909, 16 + 5/16, 3.404, 3.2205, 6 + 1/2),
        *_wheel_pair(4.2125, 16.6053, 3 + 1/2, 3 + 5/16, 6 + 1/2),
        Pos(0, 16 + 5/8, 6.7057) * Box(9, 4 + 1/16, 1.0205, align=CORNER),
        extrude(Plane(origin=(0, 0, 8 + 1/2), x_dir=(-0.000991, -0.999998, 0.001751), z_dir=(-0.000282, 0.001751, 0.999998)) * (Pos(-(17 + 15/16), 9 + 1/2) * Rectangle(17, 8 + 7/16, align=CORNER)), 1 + 1/4),
        Pos(18.6513, 16 + 9/16, 6 + 11/16) * Box(8.3355, 4 + 1/16, 1.0206, align=CORNER),
    ]
    children = [
        (jack_lift_arm, Pos(9, 0, 0.1587), [], ''),
    ]
    return solids, children


@component
def jack_lift_arm():
    """SketchUp: 'Group#284'"""
    solids = [
        extrude(Plane(origin=(9 + 3/16, 0, 0.0836), x_dir=(0.002811, -0.951057, -0.309004), z_dir=(-0.999959, 0, -0.009097)) * (Pos(-2.0798, 0.5412) * Circle(1 + 3/16)), 8 + 5/8),
    ]
    children = [
        (jack_saddle, Location(Plane(origin=(0.0302, 0.1582, 1 + 1/2), x_dir=(1, 0.000581, 0.000153), z_dir=(-0.00007, -0.141113, 0.989993))), [], ''),
    ]
    return solids, children


@component
def jack_saddle():
    """SketchUp: 'Group#260'"""
    solids = [
        extrude(Plane(origin=(0.0163, 0, 0), x_dir=(0, 1, 0), z_dir=(0.999997, 0, 0.002527)) * (make_face(Wire([Line((0.1652, 2), (1/16, 1.6049)), Line((1/16, 1.6049), (1/16, 0)), Line((1/16, 0), (24 + 1/16, 0)), ThreePointArc((24 + 1/16, 0), (21.0897, 5 + 1/8), (15 + 5/16, 6.543)), Line((15 + 5/16, 6.543), (3.0996, 4 + 1/2)), ThreePointArc((3.0996, 4 + 1/2), (1.2844, 3.6604), (0.1652, 2))]))), 1/2),
        Pos(9 + 1/8, 1/16, 6.6423) * Rot(Z=-0.045) * Rot(Y=89.761) * (Sheet(1/2, 6.6423, 24, facing="Z") - extrude((Polygon((5.0374, 0), (4.6424, 0.1027), (4 + 3/16, 0.2952), (3 + 3/4, 9/16), (3.3361, 7/8), (2.9819, 1.2219), (2 + 11/16, 1 + 5/8), (2 + 7/16, 2 + 1/16), (2 + 1/4, 2.5444), (2 + 1/8, 3.0371), (0.0993, 15 + 1/4), (0, 16.2697), (0, 0), align=None) + Polygon((0.0374, 17.2851), (0.2107, 18.2864), (0.5168, 19 + 1/4), (15/16, 20 + 3/16), (1 + 1/2, 21.0272), (2.1653, 21 + 13/16), (2 + 15/16, 22.4728), (3.7684, 23.0396), (4 + 11/16, 23 + 1/2), (5.644, 23 + 13/16), (6.6423, 24), (0, 24), (0, 16.2697), align=None)), 1/2)),
    ]
    children = []
    return solids, children


@component
def jack_handle():
    """SketchUp: 'Group#313'"""
    solids = [
        # approximate: 4% of surface area not modeled
        (extrude(Plane(origin=(0, 35 + 1/8, 45 + 7/16), x_dir=(-1, 0, 0), z_dir=(0, -0.611527, -0.791224)) * (Pos(-4.092, 1/4) * Circle(13/16)), 51.0881)
            + extrude(Plane(origin=(0, 2 + 9/16, 3 + 5/16), x_dir=(-1, 0, 0), z_dir=(0, -0.611527, -0.791224)) * (Pos(-2.5456, -11/16) * Rectangle(2.5247, 1 + 7/8, align=CORNER) + Pos(-(8 + 3/16), -11/16) * Rectangle(2 + 7/16, 1 + 7/8, align=CORNER)), 3.2833)),
    ]
    children = []
    return solids, children


@component
def jack_2():
    """SketchUp: 'Jack 2'"""
    solids = []
    children = [
        (pad, Pos(24, 1 + 3/16, 22 + 13/16), [('scale', (1.5, 1.5, 1.0))], ''),
        (pad, Pos(6, 1 + 3/16, 22 + 13/16), ['mirror', ('scale', (1.5, 1.5, 1.0))], ''),
        (cross_bar, Pos(3, 2 + 7/16, 21 + 5/16), [], ''),
        (jack_connector_block, Pos(10.7751, 4 + 1/8, 18 + 15/16), [], ''),
        (jack_rear_axle_raised, Pos(1 + 5/16, 0, 0), [], ''),
        (jack_handle, Pos(10.9835, 18.591, 7 + 1/4), [], ''),
    ]
    return solids, children


@component
def jack_connector_block():
    """SketchUp: 'Jack Connector block'"""
    solids = [
        Box(8 + 7/16, 1 + 1/4, 3 + 5/8, align=CORNER),
    ]
    children = []
    return solids, children


@component
def jack_rear_axle_raised():
    """SketchUp: 'Group#7'"""
    solids = []
    children = [
        (jack_chassis_raised, Location(), [], ''),
    ]
    return solids, children


@component
def jack_chassis_raised():
    """SketchUp: 'Group#8'"""
    solids = [
        # (the meshes were a pair of wheels each, on an axle)
        *_wheel_pair(23.7909, 16 + 5/16, 3.404, 3.2205, 6 + 1/2),
        *_wheel_pair(4.2125, 16.6053, 3 + 1/2, 3 + 5/16, 6 + 1/2),
        Pos(0, 16 + 5/8, 6.7057) * Box(9, 4 + 1/16, 1.0205, align=CORNER),
        extrude(Plane(origin=(0, 11.4092, 14.9766), x_dir=(0.001597, 0.795469, -0.605992), z_dir=(-0.000441, -0.605992, -0.795471)) * (Pos(-8.1666, 9 + 1/2) * Rectangle(17, 8 + 7/16, align=CORNER)), 1 + 1/4),
        Pos(18.6513, 16 + 9/16, 6 + 11/16) * Box(8.3355, 4 + 1/16, 1.0206, align=CORNER),
    ]
    children = [
        (jack_lift_arm, Pos(9, 0, 0.1587), [], ''),
    ]
    return solids, children


@component
def post():
    """SketchUp: 'Post'"""
    solids = []
    children = [
        (post_base_plate, Location(), [], ''),
        (post_brace, Pos(7 + 1/4, 10 + 1/4, 3/4) * Rot(Z=180), ['mirror'], ''),
        (post_brace, Pos(3 + 3/4, 10 + 1/4, 3/4) * Rot(Z=180), [], ''),
        (post_brace, Pos(7 + 1/4, 6 + 3/4, 3/4) * Rot(Z=90), ['mirror'], ''),
        (post_brace, Pos(7 + 1/4, 10 + 1/4, 3/4) * Rot(Z=90), [], ''),
        (post_4x4, Pos(3 + 3/4, 6 + 3/4, 3/4), [], ''),
    ]
    return solids, children


@component
def post_base_plate():
    """SketchUp: 'Group#44'"""
    solids = [
        Sheet(3/4, 11, 17, facing="Z"),
    ]
    children = []
    return solids, children


@component
def post_brace():
    """SketchUp: 'Group#102', 'Group#103'"""
    solids = [
        Pos(-(1 + 1/16), 3 + 1/2, 2 + 11/16) * Rot(Y=45) * Rot(X=90) * (TwoByFour(5 + 5/16, along="X", wide="Z") - extrude((Polygon((1 + 1/2, 0), (0, 1 + 1/2), (0, 0), align=None) + Polygon((5 + 5/16, 0), (5 + 5/16, 1 + 1/2), (3 + 13/16, 0), align=None)), 3 + 1/2)),
    ]
    children = []
    return solids, children


@component
def post_4x4():
    """SketchUp: 'Group#104'"""
    solids = [
        FourByFour(18 + 1/4, along="Z"),
    ]
    children = []
    return solids, children


@component
def arrow_1_2():
    """SketchUp: 'arrow 1#2'"""
    solids = [
        extrude(Plane.YZ * (Polygon((24, 9), (0, 9), (0, 3), (24, 3), (24, 0), (39.7148, 6), (24, 12), align=None)), 1/2),
    ]
    children = []
    return solids, children
