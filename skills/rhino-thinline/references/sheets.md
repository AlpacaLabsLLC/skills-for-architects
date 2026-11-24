# Sheets

Layout, annotation, leaders, the request record and the PDF: conventions for linework from any view. The view (camera, exclusions and crop, occlusion, joint and detail-cut selection, the building lock) is [as-rhino-axon](../../rhino-axon/references/views.md). One working session, no baseline, and no sheet printed. Function names are in `as-sheet.py`.

## Page setup

`new_sheet` makes the layout, the border and the title column, and returns the page, the drawing field and the title box; it also starts the request record (below). It runs once: an existing layout name is refused. Set the page size in mm. It chooses no view: for an axonometric, [as-rhino-axon](../../rhino-axon/SKILL.md)'s `setup_sheet` calls it and puts the main detail in the field.

**A document can have empty tables.** A script-built document may have no hatch patterns and no linetypes.

- Hatch patterns: `white_mask` adds the Solid pattern when it is missing, so nothing is needed.
- Linetypes: look for `Dashed` with `d.Linetypes.Find("Dashed")` before planning dashed guides. If the table is empty or has no `Dashed`, draw the guides as plain solid lines on the source layer. They come out on the `Guides` layer at the thinnest weight. Say in the report that the guides are solid. Do not stop to add a linetype, and do not imitate dashes.

**Unconfirmed hazard: page creation and the active document.** Creating or activating a page appeared to write an internal string to Rhino's active document rather than the targeted one. The cause has not been isolated, and it is not known which call does it. As a precaution, `new_page` refuses a window document that is not the active one, so make the target active first and keep other documents closed while building a sheet. If several documents are open, compare each one's `Strings` before and after. A headless document is never active and is accepted; `new_page` compares the active document's strings around the page and prints a warning if they changed.

## Sheet layout

- Ask for the title and the scale when the request does not give them; if nobody answers, set them yourself and say so in the report. Take the scale from the document's unit system: imperial architectural scales (1/8", 1/4", 1/2" = 1'-0", that is 1:96, 1:48, 1:24) for feet or inches, metric (1:20, 1:50, 1:100) otherwise. Do not take a title from a file or folder name.

- Size details to the space left, not the reverse. Small axons in corners worked where 1:1 sections did not.
- Build the title block on an explicit grid: fixed rows, a shared baseline per row, one padding constant, frame flush with the view (`title_block`).
- Centre the composite on the drawing area, not the sheet. Measure the extents of linework, callouts and details, leave out the title column, centre that box in the field, and report the margins (`composite_shift`).
- `text` with no justification takes x as the left of the text and y as its top, so the text hangs below y. A label meant to sit above a leader goes at the leader's y, plus the gap, plus the height measured with `text_box`. Pass a justification, such as `G.TextJustification.MiddleCenter`, for another anchor.
- Measure text with `text_box` and check it against its frame. An estimate of 1.9 mm per character for 3.5 mm bold was really about 2.8 mm, and two labels overran.
- Review the whole sheet, then zoom each new element. The layout view hides collisions at full-sheet scale.

## Details and leaders

- Detail leaders are orthogonal only: one horizontal per label row with a short vertical stub at the anchor (`label_rows`). `check_sheet` fails a diagonal one.
- Give each anchor its own x and sit it on a visible face of its member (`shared_x`). Two anchors with one x make collinear stubs that read as one leader.
- A locator leaves the ring cleanly: from its side or top with an elbow, not almost tangent at its bottom (`locator_route`). Prefer empty paper to the member's own shaft.
- A locator must not cross text. `check_sheet` fails a leader named `Locator leader ...` that passes through the measured box of any text under the sheet's root. Move the caption or use the other route. It fails a locator leader through another detail's ring, any line through a detail tag or a label, any label touching a detail ring, a locator leader that enters its own detail, and two locator leaders that share a segment. With `field` it fails a composite closer than the fixed 10 mm (`MIN_MARGIN_MM`) to the field's edge, and prints the margins. It fails text drawn more than 10% off the height `text()` was asked for (`text_height_failure`, on the drawn height: text height times its dimension scale). No limit can be passed in: fix the sheet, not the check.
- `check_sheet` recomputes every request from the page. `new_sheet` (called by axon's `setup_sheet`) starts a request ledger (document strings `as-sheet:requests` and `as-sheet:requests-seal`, a hash chain that also covers the building record), and `place_label` here, and axon's `place_locator` and `round_detail`, append each attempt to it. A label counts as placed only while a `Label text` with its words is on the page, a locator only while its `Locator leader` and `Locator ring` are, and a detail only while its `Bubble ring` and `Bubble linework` are; anything else fails with the last attempt's reason. An edited, cut-short or deleted ledger, seal or building record fails too, and so does a sheet not started by `new_sheet`. There is no way to withdraw a request: report what could not be placed.
- A tag on a ring needs a real gap, because a white mask does not hide the ring in the layout view. Pass the tags to axon's `round_detail` as `ring_tags=[((x_mm, y_mm), radius_mm)]`, and it stops the ring under each one.

Label a component with `place_label(doc, page, index, text, world_points, main_detail, main_root)`. It first drops every point another part covers in the main view (`visible_points`, which as-rhino-axon supplies; loaded alone, this library keeps every point), so a label never lands on a part hidden behind another; when none is left it draws nothing and `check_sheet` names the label. It tries the remaining points nearest the drawing's outline first and puts the text in the clear paper beside the drawing, with a straight leader ending in a dot on the part. The leader crosses no main linework, other leader, ring or text; when no route is clear it draws nothing and `check_sheet` names the label. `check_sheet` also fails a label leader that runs along another leader, and axon's `check_sheet` one that crosses the main drawing. `label()` places text where you say, for a sheet laid out by hand. Numbered `callout`s end in a dot too.

## Tables from the BOM

Read the [rhino-bom](../../rhino-bom/SKILL.md) CSV with `bom_rows` and find each row with `table_lookup`: a lookup that does not match exactly one row fails, so the table cannot quietly drift or show a blank.

## Rhino layout mechanics

- **Inspect layouts** with `boxMin` and `boxMax` in page units. `zoom` broke the page view, and passing `view:` can switch the active viewport.
- **PDF export.** `FilePdf.Create()`, `ViewCaptureSettings(page, 300)`, `AddPage`, `Write` (`export_pdf`). For dashed lines, see the empty-tables note in Page setup.

## Verifying the PDF

Rhino writes colours as `SC` and `sc` after `/DeviceRGB CS`, not `rg`. A first check that looked for `rg` found nothing and would have passed. `as-pdf-check.py` handles all colour forms, treats finding no colour operators as a failure, and reports page count, MediaBox, image count, colours and line widths in mm.

## Unconfirmed defaults

Seen once with no test. Not rules; use them until a person decides.

- Number details in a series separate from callouts (D1, D2 against 1 to 16), and renumber when a detail is removed.
- Keep export colour on `PrintColor` rather than `BlackAndWhite`, on the unconfirmed worry that `BlackAndWhite` could turn white masks black.
