"""Standard lumber and sheet goods.

Every piece is built with its minimum corner at the origin, so it can be
placed with Pos(corner). Lengths are in inches.

A board's orientation is given by two axes: `along`, the axis its length runs
along, and `wide`, the axis its wide face spans. Its thickness is on the
remaining axis. For example, a platform joist lying on edge and running
along X is TwoBySix(93, along="X", wide="Z").
"""

from build123d import Align, Box

# Nominal size -> (actual thickness, actual width), inches.
ACTUAL = {
    "1x2": (3 / 4, 1 + 1 / 2),
    "1x3": (3 / 4, 2 + 1 / 2),
    "1x4": (3 / 4, 3 + 1 / 2),
    "1x6": (3 / 4, 5 + 1 / 2),
    "1x8": (3 / 4, 7 + 1 / 4),
    "1x10": (3 / 4, 9 + 1 / 4),
    "1x12": (3 / 4, 11 + 1 / 4),
    "2x2": (1 + 1 / 2, 1 + 1 / 2),
    "2x3": (1 + 1 / 2, 2 + 1 / 2),
    "2x4": (1 + 1 / 2, 3 + 1 / 2),
    "2x6": (1 + 1 / 2, 5 + 1 / 2),
    "2x8": (1 + 1 / 2, 7 + 1 / 4),
    "2x10": (1 + 1 / 2, 9 + 1 / 4),
    "2x12": (1 + 1 / 2, 11 + 1 / 4),
    "4x4": (3 + 1 / 2, 3 + 1 / 2),
    "4x6": (3 + 1 / 2, 5 + 1 / 2),
    # Trim stock, named by actual size (Cut_Lists/Interior_Trim_Items.md).
    "1/2x2": (1 / 2, 2),
    "1/2x3-1/8": (1 / 2, 3 + 1 / 8),
    "1/2x9-1/2": (1 / 2, 9 + 1 / 2),
    "3/4x4": (3 / 4, 4),
    "3/4x8": (3 / 4, 8),
}

AXES = "XYZ"


def _box(sizes):
    """Box from {axis: size}, minimum corner at the origin."""
    return Box(sizes["X"], sizes["Y"], sizes["Z"], align=Align.MIN)


def board(nominal, length, along="X", wide="Z"):
    """A board of the given nominal size (e.g. "2x6")."""
    if along == wide:
        raise ValueError("along and wide must be different axes")
    thickness, width = ACTUAL[nominal]
    (thin,) = set(AXES) - {along, wide}
    return _box({along: length, wide: width, thin: thickness})


def OneByTwo(length, along="X", wide="Z"):
    return board("1x2", length, along, wide)


def OneByThree(length, along="X", wide="Z"):
    return board("1x3", length, along, wide)


def OneByFour(length, along="X", wide="Z"):
    return board("1x4", length, along, wide)


def OneBySix(length, along="X", wide="Z"):
    return board("1x6", length, along, wide)


def OneByEight(length, along="X", wide="Z"):
    return board("1x8", length, along, wide)


def OneByTen(length, along="X", wide="Z"):
    return board("1x10", length, along, wide)


def OneByTwelve(length, along="X", wide="Z"):
    return board("1x12", length, along, wide)


def TwoByTwo(length, along="X", wide="Z"):
    return board("2x2", length, along, wide)


def TwoByThree(length, along="X", wide="Z"):
    return board("2x3", length, along, wide)


def TwoByFour(length, along="X", wide="Z"):
    return board("2x4", length, along, wide)


def TwoBySix(length, along="X", wide="Z"):
    return board("2x6", length, along, wide)


def TwoByEight(length, along="X", wide="Z"):
    return board("2x8", length, along, wide)


def TwoByTen(length, along="X", wide="Z"):
    return board("2x10", length, along, wide)


def TwoByTwelve(length, along="X", wide="Z"):
    return board("2x12", length, along, wide)


def FourByFour(length, along="Z"):
    """A 4x4 post; standing upright by default."""
    return board("4x4", length, along, "X" if along != "X" else "Y")


def FourBySix(length, along="X", wide="Z"):
    return board("4x6", length, along, wide)


def Sheet(thickness, width, height, facing="X"):
    """A sheet (plywood, siding, foam) of the given thickness, lying in the
    plane perpendicular to `facing`. `width` and `height` go along the other
    two axes in X, Y, Z order."""
    a, b = [ax for ax in AXES if ax != facing]
    return _box({facing: thickness, a: width, b: height})


def thickness(nominal):
    """Actual thickness of a nominal size, e.g. thickness("2x6") == 1 + 1/2."""
    return ACTUAL[nominal][0]


def width(nominal):
    """Actual width of a nominal size, e.g. width("2x6") == 5 + 1/2."""
    return ACTUAL[nominal][1]
