# Linework, weights and hatch

Black and white methods. Everything here comes from one working session with no baseline. No sheet was printed. Weights were accepted on screen; hatch patterns were not checked against the National CAD Standard or Architectural Graphic Standards.

## Line hierarchy

Three ideas, adapted to Rhino: filled forms hide what is behind them, so hidden curves are dropped by the projection; silhouette, edge and receding lines are separate strokes; every stroke is thin. Style reference: the [hairline](https://github.com/lucasmarkes/hairline) figures, for this hierarchy only.

| Stroke | From `HiddenLineDrawing` | Layer |
|---|---|---|
| Outline | `Boundary`, `Projecting`, `Tangent`, `TangentProjects` silhouettes | `Outline` |
| Edge | `Crease`, `NonSilhouetteCrease`, on objects toward the front | `Edge` |
| Receding | The same edges, on objects toward the back | `Receding` |

The Receding stroke is new here and was not used in the source session. By default it is 0.09, a step thinner than Edge. `receding_from` sets where the back begins (default 0.6 of the depth range).

Join curves by source object to keep curve counts down. as-rhino-axon's `main_linework` does this and sorts each projected curve into these strokes; the hierarchy applies to any linework: an axon, a plan, a section or an elevation.

## Weights

The first values (outline 0.18 against edge 0.09) did not read as a hierarchy at sheet scale in the maintainers' sheet grading, so the main view now has three clear steps: only the assembly's outline against the paper is heavy, member edges are medium, and members toward the back are light. In details, an edge on its own piece's outline and every cut edge are heavy.

Provisional, in mm, set as layer `PlotWeight`. Accepted on screen, not proven in print. One printed sheet settles them.

| Element | Weight |
|---|---|
| Main drawing guides and receding edges | 0.09 |
| Main drawing member edges | 0.18 |
| Main drawing outline (the assembly against the paper) | 0.35 |
| Detail hatch | 0.09 |
| Detail edges | 0.18 |
| Detail outlines and cut edges | 0.50 |
| Annotation and label leaders | 0.18 |
| Locator leader | 0.25 |
| Detail ring and tag | 0.50 |

## Black and white hygiene

- Mask callouts over dense linework: a solid white hatch behind each balloon, added before the ring, with object and plot colour both white (`white_mask`, which adds the Solid pattern if the document has none).
- Remove colour language from notes ("shown in red"). `check_sheet` flags it.

## Hatching

Working conventions by material and cut direction. Not checked against a standard.

| Material and cut | Pattern | Function in `as-sheet-core.py` |
|---|---|---|
| Sawn lumber, across the grain | X corner to corner | `hatch_x` |
| Plywood | Lengthwise ply lines | `hatch_plies` |
| Boards, along the grain | Broken lengthwise grain lines | `hatch_grain` |
| Timber with no boards modeled | General diagonal; do not invent board joints | `hatch_diagonal` |
| Gypsum board | Fine stipple | `hatch_pattern("gypsum", ...)` |
| Concrete | Stipple and aggregate triangles; sizes in metres, pass `unit` (one metre in model units) | `hatch_concrete` |
| Steel in section, small scale | Near-solid dense lines | `hatch_dense` |
| Glulam, across the laminations | Concentric lamination lines, one set per assumed lamination thickness | draw with arcs for the member |
| Membrane too thin to hatch | Leave as a line, and say so | none |

Method. Which faces are cut, and drawing hatch through the hidden-line solve, belong to the view: as-rhino-axon's `cut_detail` does both ([views](../../rhino-axon/references/views.md#cut-faces-and-hatch)) and hands the hatch to these patterns.

1. Clip hatch around members inside the cut (`clip_out`), such as a bolt through wood and concrete.
2. Scatter concrete on a stratified grid with a fixed seed. Plain random clumps visibly, and the seed keeps reruns identical.
