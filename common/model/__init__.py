"""build123d model of the tiny home, the jigs and tools used to build it,
and the equipment used to move it: the source of truth for the manuals'
figures (see figures/ and render/model2svg.py).

Units are inches. Each component is a function returning its own solids and
its children as (component, placement, modifiers, tag). A child is only shown
when its tag isn't hidden; untagged ("") children follow their parent. Tags
starting "manual:" mark optional children (tools, annotations) that only a
manual's figures ask for. Modifiers ("mirror", ("scale", (sx, sy, sz))) cover
transforms that a Location can't express. Boxes and sheets are placed by their
minimum corner.

Modules:
  dimensions     named dimensions from the construction manuals
  lumber         standard lumber sizes and sheet goods
  hardware       hardware stand-ins
  common         helpers shared by every module
  notes          annotations for the manuals' figures
  parts          components shared by more than one assembly
  platform       the platform (floor framing, subfloor, floor insulation)
  walls          the four walls
  roof           roof framing, sheathing and roofing
  interior*      interior panels, trim, insulation and ceiling
  doors          the door
  flooring       the floor
  exterior_trim  exterior trim
  equipment      iron carts, jacks, triple blocks, 4x4 stands, dollies and arrows
  house          the assembled house
  iron_carts     the iron-cart removal scenes' instances
  figures/       the manuals' figures
"""
