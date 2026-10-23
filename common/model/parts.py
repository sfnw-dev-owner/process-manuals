"""Components shared by more than one assembly."""

from .common import *


@component
def cross_bar():
    """SketchUp: 'Cross Bar', 'Front/Back Wall - 2x4 Window Header'"""
    solids = [
        TwoByFour(24, along="X", wide="Y"),
    ]
    children = []
    return solids, children
