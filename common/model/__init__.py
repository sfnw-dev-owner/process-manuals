"""build123d model of the tiny home, the jigs and tools used to build it,
and the equipment used to move it: the source of truth for the manuals'
figures (see figures/ and render/model2svg.py).

Units are inches. Values no manual states came from the SketchUp model and
the QCAD drawings this package was bootstrapped from (removed in commit
1492ff3), not to be trusted where the manuals differed.

Each component is a function returning its own solids and its children as
(component, placement, modifiers, tag). A child is only shown
when its tag isn't hidden; untagged ("") children follow their parent.
Modifiers ("mirror", ("scale", (sx, sy, sz))) cover
transforms that a Location can't express. Boxes and sheets are placed by their
minimum corner.

Modules:
  dimensions     named dimensions from the construction manuals
  lumber         standard lumber sizes and sheet goods
  hardware       hardware stand-ins
  common         helpers shared by every module
  notes          annotations for the manuals' figures
  platform_assembly  the platform (floor framing, subfloor, foam insulation)
  walls          the four walls
  roof           roof framing, deck, fascia and soffits, bird and vent blocks
  roofing        tar paper, shingles, ridge vent, cap shingles
  gables         structural triangles and gable siding
  interior*      interior panels, trim, insulation and ceiling
  doors          the door
  flooring       the floor
  exterior_trim  exterior trim
  equipment      iron carts, jacks, triple blocks, 4x4 stands, dollies and arrows
  house          the assembled house
  iron_carts     the iron-cart removal scenes' instances
  figures/       the manuals' figures
"""
