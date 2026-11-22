"""The iron-cart removal (Extract_Iron_Carts/Extract_instructions.md): the
finished house jacked up an end at a time off the iron carts it was built
on, onto 4x4 stands and triple blocks, and finally onto auto dollies.

Everything is placed in the house's frame (house.py: X across, Y from the
rear wall to the front, Z up from the skids' bottoms as the house sits on
the carts); the shop floor is FLOOR below that. A step's scene is the house
at the heights its ends stand at (house_at) and the equipment under and
around it (carts, jack, posts, blocks, dollies) with the manual's diagram
arrows (flat_arrow, upright_arrow); figures/extract_instructions.py lists
the scenes.
"""

import math

from build123d import Pos, Rot

from .dimensions import SKID, SKID_INSET
from .equipment import _2x8_block, arrow_1_2, car_wheel_caster, iron_cart, jack_2, jack_2_1, post
from .house import house
from .lumber import thickness
from .platform_assembly import FRAME_BOTTOM, PLATFORM_LENGTH, PLATFORM_WIDTH, SKID_END_CUT

# ── the equipment's working heights (equipment.py) ─────────────────────────
CART_DECK = 7 + 7/16 + 4  # an iron cart's shell top, where the skids ride (iron_cart)
FLOOR = -CART_DECK  # the shop floor, below the skids' bottoms
POST_HEIGHT = 3/4 + 18 + 1/4  # a 4x4 stand: base plate and post (post)
JACK_PADS = {False: 11 + 5/16 + 1/2, True: 22 + 13/16 + 1/2}  # a jack's load pads' tops, lowered and raised (jack_2_1, jack_2)
BLOCK = (7 + 1/4, 18, 6)  # a triple block (three 2x8s): wide, long, high (_2x8_block)
DOLLY = (16, 13 + 5/8, 1.8934 + 1/4)  # an auto dolly: across the skid (its cradle centered), along it, and the skid's seat in the cradle (car_caster)
JACK_WIDTH, JACK_PAD = 30, 6  # a jack across, and its two load pads along it: at its Y = 0 end, the handle beyond (jack_2_1)

# What an end of the house stands on, as the height of the skids' bottoms
# there: the jack and the stands take the platform's rim (FRAME_BOTTOM up),
# the blocks and the dollies the skids.
ON_CARTS = 0
ON_JACK = FLOOR + JACK_PADS[True] - FRAME_BOTTOM
ON_POSTS = FLOOR + POST_HEIGHT - FRAME_BOTTOM
ON_BLOCKS = FLOOR + BLOCK[2]
ON_DOLLIES = FLOOR + DOLLY[2]

SKID_X = (SKID_INSET + thickness(SKID) / 2, PLATFORM_WIDTH - SKID_INSET - thickness(SKID) / 2)  # the skids' centers
HOUSE_HIDDEN = frozenset({"Roofing", "Wall Framing", "Floor Framing", "Floor Insulation", "Floor Sheeting"})  # not drawn in these scenes (the SketchUp houses were plain)


def house_at(rear, front):
    """The house with its skids' bottoms `rear` and `front` up at its ends
    (ON_CARTS, ON_JACK, ...): (component, placement, mods)."""
    tilt = math.degrees(math.asin((front - rear) / PLATFORM_LENGTH))
    return (house, Pos(0, 0, rear) * Rot(X=tilt), [])


# ── the equipment, where each step has it ──────────────────────────────────

CART_FROM_REAR = 1 + 1/2  # a cart's rear end in from the platform's
CART_WIDTH = 36  # across; its flanges' gap, the skid's width, is centered


def carts():
    """The two iron carts, one under each skid: the cart's flanges astride
    the skid, its rear end CART_FROM_REAR in from the platform's. (Its
    frame: X along it from its rear end, Y across it.)"""
    return [(iron_cart, Pos(x + CART_WIDTH / 2, CART_FROM_REAR, FLOOR) * Rot(Z=90), []) for x in SKID_X]


JACK_PADS_IN = 1  # a jack's load pads' outer edge in from the platform's end, under the rim ("just inside the siding")
JACK_STAGED = 36  # a jack waiting beyond the platform's end: its pads this far out


def jack(end, raised=False, out=0):
    """The hydraulic jack at the rear or front end: centered across the house,
    its load pads under the rim JACK_PADS_IN in from the end (or `out`
    beyond it, waiting), lowered or raised."""
    comp = jack_2 if raised else jack_2_1
    reach = -out if out else JACK_PADS_IN + JACK_PAD  # the pads' far edge (its Y = 0 end), in from the platform's end
    if end == "rear":  # turned to face the house, its handle toward -Y
        return (comp, Pos(PLATFORM_WIDTH / 2 + JACK_WIDTH / 2, reach, FLOOR) * Rot(Z=180), [])
    return (comp, Pos(PLATFORM_WIDTH / 2 - JACK_WIDTH / 2, PLATFORM_LENGTH - reach, FLOOR), [])


POST_PLATE = (11, 17)  # a stand's base plate; the 4x4 is centered on it (post)
POST_FROM_SIDE = 1/2  # under a rear corner: the plate's edge in from the platform's side
POST_STAGED = (22, 12)  # waiting beside a rear corner: the plate outside the side and behind the rear end, this far
POST_OUT = (35, 42)  # out of the way, once the rear is on blocks


def posts(where):
    """The two 4x4 stands at the rear corners: "under" (the 4x4 under the
    rim joist, the plate POST_FROM_SIDE in from the side), "staged" or
    "out" (beside the corners, POST_STAGED or POST_OUT away)."""
    wide, deep = POST_PLATE
    rim = thickness("2x6") / 2  # the rim joist's center line
    places = {"under": (POST_FROM_SIDE, rim - deep / 2), "staged": (-POST_STAGED[0] - wide, -POST_STAGED[1] - deep),
              "out": (-POST_OUT[0] - wide, -POST_OUT[1] - deep)}
    x, y = places[where]
    return [(post, Pos(x, y, FLOOR), []), (post, Pos(PLATFORM_WIDTH - x - wide, y, FLOOR), [])]


BLOCK_FROM_END = 18  # under a skid: the block's near face from the platform's end ("about 18 inches from the end of the skids")
BLOCK_STAGED = 33  # waiting beside the house: outside the side, abreast of its place


def blocks(end, under):
    """The two triple blocks for the rear or front: under the skids, across
    them and centered on them, BLOCK_FROM_END from the end; or staged
    beside the house abreast of their places. (The block's frame: X its
    width, Y its length; turned to lie across the skid.)"""
    wide, long, _ = BLOCK
    y = BLOCK_FROM_END if end == "rear" else PLATFORM_LENGTH - BLOCK_FROM_END - wide
    out = []
    for skid, staged in ((SKID_X[0], -BLOCK_STAGED), (SKID_X[1], PLATFORM_WIDTH + BLOCK_STAGED + long)):
        x = skid + long / 2 if under else staged  # the block's +X edge (Rot(Z=90) lays its length toward -X)
        out.append((_2x8_block, Pos(x, y, FLOOR) * Rot(Z=90), []))
    return out


DOLLY_IN = 4  # under a skid's end: the dolly's outer edge in from the end of the skid's flat bottom ("about 4 inches")
DOLLY_STAGED = 66  # waiting beside the house: outside the side, at that end


def dollies(end, under):
    """The two auto dollies for the rear or front ends of the skids: under
    them, centered on the skid, DOLLY_IN in from the flat bottom's end; or
    staged beside the house at that end."""
    across, along, _ = DOLLY
    flat = SKID_END_CUT[0]  # the skids' ends are cut at an angle this far
    y = flat + DOLLY_IN if end == "rear" else PLATFORM_LENGTH - flat - DOLLY_IN - along
    out = []
    for skid, staged in ((SKID_X[0], -DOLLY_STAGED - across), (SKID_X[1], PLATFORM_WIDTH + DOLLY_STAGED)):
        x = skid - across / 2 if under else staged
        out.append((car_wheel_caster, Pos(x, y if under else (-along / 2 if end == "rear" else PLATFORM_LENGTH - along / 2), FLOOR), []))
    return out


# ── the manual's diagram arrows (equipment.arrow_1_2: a flat arrow in its
# YZ plane, pointing +Y, ARROW wide across Z, 1/2" thick) ──────────────────
ARROW = (39.7148, 12)  # tail to tip, wide
ARROW_UP_TIP = FLOOR - 20  # an arrow pointing up stands below the floor, its tip this far under (the jack's step number sits between)
ARROW_DOWN_TAIL = FLOOR - 12  # one pointing down hangs from this far under
ARROW_BEYOND_END = 16  # a jack's arrow, beyond the platform's end
POST_ARROW_IN = (22, 40)  # the arrows for the stands going in: tails this far outside and behind the rear corners, pointing in at 45°
POST_ARROW_OUT = (5, 12)  # for the stands coming out: tails this far outside and behind the corners, pointing out at 45°
SIDE_ARROW_TIP = 22  # an arrow pointing in from beside the house: its tip this far outside the side


def flat_arrow(tail, heading):
    """An arrow lying on the floor, its tail's middle at `tail` (x, y),
    pointing `heading` degrees counterclockwise from +Y (seen from above)."""
    return (arrow_1_2, Pos(tail[0], tail[1], FLOOR) * Rot(Z=heading) * Pos(-ARROW[1] / 2, 0, 1/2) * Rot(Y=90), [])


def upright_arrow(x, y, up):
    """An arrow standing below the floor, centered at (x, y), facing along
    the house (its width across it), pointing up (its tip at ARROW_UP_TIP)
    or down (its tail at ARROW_DOWN_TAIL)."""
    long, wide = ARROW
    if up:  # stood up (Y to Z), then turned so its width lies across X
        return (arrow_1_2, Pos(x - wide / 2, y - 1/4, ARROW_UP_TIP - long) * Rot(Z=90) * Rot(X=90), [])
    return (arrow_1_2, Pos(x + wide / 2, y - 1/4, ARROW_DOWN_TAIL) * Rot(Z=90) * Rot(X=-90), [])


def jack_arrow(end, up):
    """The arrow at the rear or front jack: going up or down, ARROW_BEYOND_END past the end."""
    return upright_arrow(PLATFORM_WIDTH / 2, -ARROW_BEYOND_END if end == "rear" else PLATFORM_LENGTH + ARROW_BEYOND_END, up)


def cart_arrows():
    """Pulling the carts out the front: an arrow from the platform's end, along each skid."""
    return [flat_arrow((x, PLATFORM_LENGTH + 1/2), 0) for x in SKID_X]


def post_arrows(going_in):
    """The stands going in under the rear corners, or coming out."""
    (beside, behind), heading = (POST_ARROW_IN, -45) if going_in else (POST_ARROW_OUT, 135)  # (the left one's; the right mirrors it)
    return [flat_arrow((-beside, -behind), heading), flat_arrow((PLATFORM_WIDTH + beside, -behind), -heading)]


def block_arrows(end, going_in):
    """The rear or front triple blocks going in under the skids (tips at the
    skids' near faces) or coming out (tails at the platform's sides)."""
    wide = BLOCK[0]
    y = (BLOCK_FROM_END if end == "rear" else PLATFORM_LENGTH - BLOCK_FROM_END - wide) + wide / 2
    if going_in:
        return [flat_arrow((SKID_INSET - ARROW[0], y), -90), flat_arrow((PLATFORM_WIDTH - SKID_INSET + ARROW[0], y), 90)]
    return [flat_arrow((0, y), 90), flat_arrow((PLATFORM_WIDTH, y), -90)]


def dolly_arrows(end):
    """The rear or front dollies going in under the skids' ends: from beside the house, tips SIDE_ARROW_TIP outside the sides."""
    y = 7 if end == "rear" else PLATFORM_LENGTH - 7
    return [flat_arrow((-SIDE_ARROW_TIP - ARROW[0], y), -90), flat_arrow((PLATFORM_WIDTH + SIDE_ARROW_TIP + ARROW[0], y), 90)]
