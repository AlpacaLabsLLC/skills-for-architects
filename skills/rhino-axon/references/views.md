# Views

The view for an axonometric sheet: camera and projection, exclusions and crop, hidden-line occlusion, joint and detail-cut selection, and the building lock. One working session, no baseline, and no sheet printed. Function names are in `as-axon.py`; the conventions it hands its linework to are [as-rhino-thinline](../../rhino-thinline/SKILL.md).

## The linework handoff

- **The main drawing.** `main_linework` projects the source layers through the main detail's camera and draws the visible curves on the page under its `out_root`, on three layers named for thinline's strokes (`Outline`, `Edge`, `Receding`) at thinline's `WEIGHTS`. It keeps its sources, exclusions and crop on the document (`as-sheet:main-sources`) for `cut_detail` and the occlusion test. Thinline reads that linework back from the page by its layer root (`main_root`): its placers route leaders around it and its checks measure against it. Thinline never projects or moves the camera.
- **Details.** `cut_detail` chooses the members, cuts them and projects them into the ring (`round_detail`), drawing `Bubble linework <tag>` and `Bubble ring <tag>`; each true cut face is hatched with thinline's pattern for its material. Thinline's tags, leaders and request record read these names.
- **Points.** `visible_points` drops label points another part covers in the main view, and `place_locator` picks the joint a detail's leader can reach. Thinline draws the leader to the point it is given.
- **The check.** `check_sheet` here runs thinline's conventions and this view in one list, in one order (`read_sheet`, `check_conventions`, `check_view`, `check_layout`).

## Page setup and camera

`setup_sheet` records the building, then calls thinline's `new_sheet` for the layout, border and title column, and adds the main parallel detail flush with them. It returns the page, the detail, the drawing field and the title box. It runs once: an existing layout name is refused. Set the page size in mm; the detail scale is checked by `SetScale`, and a refusal raises. Then move the drawing into the field with `pan_detail`.

Explosion guides are model-space lines, and `main_linework` draws any curve under its source layers as a guide.

- **Page-space hazard.** While a page view is active, `AddBrep` and `AddLine` with default attributes land in page space, and the detail shows blank. Use `model_add`, which sets `Space=ModelSpace` and `ViewportId=Guid.Empty` after adding.
- **Parallel projection before scale.** `ChangeToParallelProjection`, commit, re-fetch with `FindId`, set camera, then `SetScale`. `parallel_detail` does this. `SetScale` failed in the other order.
- **Reposition a drawing by panning the detail camera** (`pan_detail`), moving camera and target together along `CameraX` and `CameraY` by the page shift over the page scale, then re-project. The scale held exactly.

## Joints and locators

- A bubble must be the real location: project the actual joint's world point through the main detail's transform, and cut the detail from the same member the leader lands on (`locator`).
- Place each locator with `place_locator`, passing every contact of the requested joint. It takes the one nearest the detail ring whose leader crosses no main linework, other detail ring or text, on a simple route or one that jogs around the drawing's outline. When there is none, it draws nothing and `check_sheet` fails the sheet naming the detail: choose another joint or move the detail, never draw through.
- `check_sheet` here adds the view to [thinline's conventions](../../rhino-thinline/references/sheets.md#details-and-leaders), in one list (`check_view`). With `main_root`, it also fails a locator leader that runs along a drawn edge (it would read as part of the member) and a locator ring that sits on no drawn line of the main view. With `main_root`, it also fails a locator leader that meets the main linework away from its own joint (within twice the locator ring's radius is allowed); it does not judge leaders against detail linework, so still review the sheet. With `detail` and `scale` it fails a scale that does not read back, and prints it. It fails when the building recorded by `setup_sheet` was changed or removed. No limit can be passed in: fix the sheet, not the check.
- Rhino details are rectangular, so a circular detail is linework: `round_detail` projects, splits against the circle and keeps pieces whose midpoint is inside.

## Details

Draw a detail with `cut_detail`. Give it a window around the joint, kept to the joint and the start of each member, and `sources=None`: it then takes every solid reaching into the window (`solids_in`), limited to what the main view shows (`main_linework` keeps its sources and exclusions on the document), so the adjoining members show in context and nothing the main view leaves out appears. `skip_roots` leaves out more. Pick a joint the window cuts through, inside the building, not an outer corner where the cut planes miss the members. With `scale=None` it fits the content to the ring at a standard scale. It cuts the members to the window (`cut_pieces`), joins overlapping pieces of one member, hatches each true cut face by material (a face on a window plane of a member that continues past it; a member face that only lies on the plane is not hatched) (`materials`, timber by default: X across the grain, grain lines along it) and draws the cut face edges at outline weight, projects into the ring and draws the tag (`detail_tag`). It warns when nothing is cut. Edges on a piece's own outline are drawn as outline. Hatch is clipped to each cut face's own outline, and its material comes from the piece's layer and name (`material_for`: gypsum is not wood, glass and membranes are not hatched) unless `materials` says otherwise. The cut pieces are deleted after projection, and repeated linework is dropped, so the sheet leaves nothing in model space and no stacked duplicates.

For the head and sill of a window or door, cut one vertical plane through the glass: `section=(axis, at, keep)`, with the axis along the wall, `at` the glass centre, and `keep` the side to show. The detail is then seen square on, and only that plane's faces are hatched. A layer under 2 mm does not boolean reliably, so it is clamped to the window instead.

Choose the cut for what it should reveal. A hidden bolt only showed with a cut through the pier centre, and a window that skimmed a curved rib left a thin accidental strip, which went away by moving the window clear of it.

Overlapping pieces of one member or system, such as pipe runs meeting at an elbow, are joined before the hidden-line pass in both the main drawing and the details (`merge_overlaps`); otherwise their edges show through each other. Pieces that only touch stay apart, so member joints stay drawn; for service runs modelled end to end, pass their layers as `join_touching` (for example `["*::Drain", "*::Supply"]`). Leave void volumes (rough openings, clearances, zones) out with `exclude`: drawn as solids they hide whole bays. For a cut-away piece of the model (a wall cut back beside a window), pass `crop=(x0, y0, z0, x1, y1, z1)` to `main_linework`: copies are cut to the box in memory and the model is not touched. Never trim or delete building geometry to get a view or a leader.

## Team models

A model assembled from several owner files arrives as one top-level layer per owner. Pass them all to `main_linework` as a list. A closed envelope (shell, sheathing, cladding) hides the frame and services; pass its layers in `exclude`, such as `["*::Sheathing"]`, to leave them out of the drawing, and say so on the sheet. Only solids and meshes are projected and curves become guides: text dots and points are skipped, and the counts are printed.

## Order and static linework

Main linework, then annotation, then details, so annotation draws on top. `main_linework` projects only the source layers, then hides every model layer in the main detail, so nothing else in the model shows through and the drawing must be regenerated after a model change. Layers added later, such as the one `cut_pieces` fills, are still visible there, so run `S["hide_in_detail"](d, sheet["detail"])` after the last detail.

## Why hidden-line

Technical kept layer colours, and Pen at 1:40 was too heavy and buried the callouts. `HiddenLineDrawing` gave clean vector linework: 1,526 solids took about 4 seconds, so it is fast enough to be the default. The projection needs an explicit map to page space, solved from three reference points through `WorldToHiddenLine` and the detail's `WorldToPageTransform`; confirm the printed scale matches the sheet's.

The cost is static linework. The live view is hidden with per-viewport layer visibility, and the drawing must be regenerated after a model change. Tell the user.

## Cut faces and hatch

1. Hatch only real cut faces in the view: faces on the cut window's planes with outward normals toward the camera (`cut_faces`). A face that merely coincides with the window extent is not a cut. Take the extents for hatch and label anchors from `face_box`, which reads the trimmed face through `DuplicateFace(False)`; `BrepFace.GetBoundingBox` returns the untrimmed surface.
2. Draw hatch lines in 3D on the face, 1 mm outward, and pass them through the same hidden-line solve (`face_lines`). They foreshorten with the axon and hide behind members. They are lines, so a pattern change means regenerating.

The patterns themselves are thinline's ([hatching](../../rhino-thinline/references/linework.md#hatching)).
