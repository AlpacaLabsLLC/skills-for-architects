# /as:rhino-model

Plan, build and check architectural models in a live Rhino 9 session from a plain-language brief: fixtures and rooms, structural centerline and stud-framing models, envelope massing with openings, stairs, doors, ruled and double-curved surfaces, SubD, and live Grasshopper definitions with named sliders. Before building, the skill writes the model's requirements into the document (dimensions, clearances and code values, each with its source). It builds each assembly as one parametric script, runs the requirements check against them, and reports what was met.

## Requirements

- Rhino 9 on macOS or Windows with a document open, used from the Rhino AI panel or an agent connected through Rhino's MCP, and the Arch Studio plugin installed in Claude Code (the requirements check runs the plugin's helper scripts).

## Usage

```
/as:rhino-model a two-story 3-bay barn, 12 ft bays, stud walls at 16 in with a sliding door on the south gable
/as:rhino-model a Dieste brick wall 30 ft long with a sine crown; Grasshopper sliders for amplitude, wavelength and brick size
```

When the brief leaves open values that drive the design, the skill recommends a value for each and asks one question whose text lists them ("Build with these recommendations? Footprint: 12 × 16 ft; wall height: 8 ft; …"): "Use all recommended" or "Go through each one by one". The second opens one question per value, with the recommendation as the first option ("Keep 6 in") and Other for your own. Every question names its values, because Rhino's question pane covers the chat. Your answers end the questions about design values. Only blocking questions (a units mismatch, a conflict with the document, a contradiction, a destructive action, an unknown code jurisdiction) are asked separately, before them. From a terminal agent without Rhino's question tool, it lists the recommendations in chat and asks there. When nothing is open, or you say "use recommended", it goes straight on. It shows the requirements it wrote. When you change the brief or correct the model, it revises the requirements first; earlier revisions stay in the document. Every reply opens with the requirements check status line, which also says what was not checked, for example `Requirements: 17/17 met · 4 not measured · not checked: clashes, structure, code compliance · untitled`. A full score means only that the checks listed passed. Ask for the requirements check or the list of requirements at any time. The document stays unsaved unless you ask it to save.

## Output

- Objects under one parent layer named for the model, child layers by function, every object named.
- A report: dimensions, layers with counts and checks, Grasshopper slider tests when built, assumptions, capture, save state.

## Not included

Rendering, structural analysis, construction documents, Revit or IFC export, and editing objects the skill did not create.

## References

- [RhinoCommon patterns](references/rhinocommon.md)
- [Grasshopper definitions](references/grasshopper.md)
- [Element recipes](references/elements.md)
- [Clash, connectivity and connection checks](references/checks.md)
- [Report template](references/report-template.md)
- [Requirement templates](references/requirements/): [toilet](references/requirements/toilet.json) (standard and ADA)
