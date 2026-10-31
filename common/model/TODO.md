# Model TODO

## Looks copied from the old drawings, to reconsider

- `render/model2svg.py` `DRAWING_FONT`: the drawings' labels are in DejaVu
  Sans (QCAD's default, shipped in `render/DejaVu`); the manuals' text is
  Carlito. Switch the labels to Carlito (and drop `render/DejaVu` and its
  entry in `render/go`'s `TYPST_FONT_PATHS`) for one typeface.
- `render/model2svg.py` `PAPER_LINE`: lines are hairlines on paper, as
  QCAD printed them; `PAPER_HEAVY` is the thick outline the platform's
  insulation step had. `EDGE` (`figures/__init__.py`) is the faint outline
  of gray "context" parts, which the drawings didn't outline at all.
- The "foam" and "plywood" hatches mimic the drawings' patterns.
- `figures/extract_instructions.py` hides the roofing (SketchUp's houses had
  plain roofs); `figures/interior_trim.py` leaves the baseboards out of the
  rear window figures and `figures/walls.py` hatches the window's lower pane
  (`glass()`), as the drawings did.
- `figures/exterior_trim.py` cuts the siding's bottom edge off in the
  triangles figure (`"wall"` parts' clip), as the drawing ran off the page.
