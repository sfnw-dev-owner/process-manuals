# Model TODO

## Once the model-drawn figures are blessed: drop the old drawings' quirks

To keep the visual diff against the QCAD/SketchUp/LayOut figures minimal, the
figures currently reproduce how those were cropped and printed, including
things that were just artifacts of the old tools. Once the new figures are
accepted as the reference, undo these:

- `figures/__init__.py` `FRAMES`: per-figure white space around each DXF-drawn
  figure, measured from the old PDFs. Delete the table; every drawing then gets
  `render/model2svg.py`'s `MARGIN` (QCAD's 2.5" print margin) all around, or
  pick a tighter one. Most entries just reproduce QCAD's lopsided cropping
  (about 3" left, 1" top, 1.3" right, 3.4" bottom on the wall drawings); a
  few reproduce stray extents of the old drawings that the new figures are
  better without: `floor_install/tiles` (14" of nothing below the tiles),
  `platform/step_06`, and `exterior_trim/corners_*` (whose roof lines ran off
  the top edge).
- `figures/exterior_trim.py` `DOOR_SHOWN`: the front window's drawing cuts the
  door casing off where the old drawing stopped drawing it. Keep, or show the
  whole door.
- `figures/__init__.py` `SIZES`: the scales QCAD printed each drawing at,
  measured from the old PDFs (several differed from the DXFs' nominal print
  scale). Keep, or re-choose sizes per manual for consistency (e.g. all wall
  manuals at one scale).
- `figures/tilt_up.py` and `figures/post_tilt_up.py` `BORDER`: the one-pixel
  black border LayOut's PNG export put around every page. Drop it (set to
  `None`), or keep as a deliberate frame.
- `figures/extract_instructions.py` `WINDOWS`, and each scene's `zoom` and
  `shift`: each iron-cart view is drawn in a window the size of SketchUp's
  export of it, zoomed and shifted to line up with that export (the scenes'
  transcribed cameras don't quite reproduce it), so parts are cut off at the
  edges exactly as they were. Drop `zoom` and `shift`, and replace `WINDOWS`
  with one window size (or a crop to the parts in view) for a consistent look.

- Looks copied from the old drawings, to reconsider:
  - `render/model2svg.py` `DRAWING_FONT`: the drawings' labels are in DejaVu
    Sans (QCAD's default, shipped in `render/DejaVu`); the manuals' text is
    Carlito. Switch the labels to Carlito (and drop `render/DejaVu` and its
    entry in `render/go`'s `TYPST_FONT_PATHS`) for one typeface.
  - `render/model2svg.py` `PAPER_LINE`: lines are hairlines on paper, as
    QCAD printed them; `PAPER_HEAVY` is the thick outline the platform's
    insulation step had. `EDGE` (`figures/__init__.py`) is the faint outline
    of gray "context" parts, which the drawings didn't outline at all.
  - The "foam" and "plywood" hatches mimic the drawings' patterns.
  - `figures/post_tilt_up.py` `LIGHT_GRAY` and `render/model2svg.py`
    `PAGE_COLORS`: the grays LayOut's exports used, per page.
  - `figures/extract_instructions.py` hides the roofing (SketchUp's houses had
    plain roofs); `figures/interior_trim.py` leaves the baseboards out of the
    rear window figures and `figures/walls.py` hatches the window's lower pane
    (`glass()`), as the drawings did.
  - `figures/exterior_trim.py` cuts the siding's bottom edge off in the
    triangles figure (`"wall"` parts' clip), as the drawing ran off the page.

## Known differences from the old figures (the model is right, or the old
## drawing was a sketch)

- Half_Roof: the step 7 lag bolt bores are at the model's position (the
  manual's text), not 4" up the rafter where the DXF put them. (The ridge
  board is drawn as its top edge's footprint: the view is square to the
  rafters, as the DXF's true rafter lengths are, in which a plumb board
  would also show its face.)

- The window unit is drawn from its SketchUp geometry (sash and sill), where
  the DXFs sketched a two-pane window; the door is SketchUp's flat slab with a
  knob, where the DXFs sketched a six-panel door.
- Interior views show the A/C opening in the rear wall's panel; the old
  drawings predate it.
- The front wall's door jamb shows its hinge and strike mortises.
- `roof-blocking/align_vent_block`: from that page's camera the model's vent
  block sits behind the members it should be in front of, so their lines
  cross it; LayOut's export had the block in front.
- The roof's start/end shingle sets and the door strike-plate detail follow
  the model's dimensions, not the DXFs' sketches.

## Open items from the rewrite

- See the `<!-- TODO: ... -->` comments in `Roof/roof_manual.md` and
  `Interior_Trim/interior_trim.md`.

## To resolve

- `interior.py` `REAR_SHELF_DEPTH`: the rear shelf's template reads 6-1/4"
  into the room (pencil, over a scaled ~6"), which with its 3-1/8" tab makes
  it 9-3/8" wide; but the shelves are ripped from a roof panel's 18-1/4"
  offcut, about 9-1/8" each. Re-measure the real shelf: if it's 6", set the
  depth to 6 and its chamfers to 1-3/4" (the template's straight ends are
  4-1/4").

- Interior_Trim front window figure, first view: the "LONG Screws" label
  overlaps the "Mount support block ... of shelf" label above it (as the
  drawing had them); move one, or shorten the note.
- post-tilt-up/frame-completion.md "triangle_screws": the two screws at each
  of the structural triangle's narrowest sections are too close together;
  space them farther apart.
- tilt-up/tilt-up.md "front_to_platform" (and the pages after it): the wall
  brace (the 2x4 from the platform's end up to the first wall) is no longer
  used; drop it from the model and the figures.
- tilt-up/tilt-up.md "lhs_jig": note in the manual that the first wall's
  brace comes off before this step, or the LHS wall runs into it before it
  can be tilted up.
