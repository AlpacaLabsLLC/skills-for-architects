---
name: rhino-model
description: "Plan, build and check architectural models in a live Rhino 9 session through Rhino's tools (the AI panel or a connected agent), from a plain-language brief. Writes the model's requirements (dimensions, clearances, code values, each with its source) into the document before building, builds by script, and checks the model against them with the requirements check before replying. Use when the user asks to model, frame, mass or parametrize geometry in Rhino. Not for rendering, structural analysis, construction documents, BIM export or editing models it did not create."
allowed-tools:
  - AskUserQuestion
---

# /as:rhino-model

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-model`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Modeling requires Rhino 9 with an open document and its Rhino tools (`run_python`, `run_command`, `get_context`, `ask_user`). In the Rhino AI panel, ask questions with `ask_user`, not `AskUserQuestion`. Where `ask_user` is not available (an agent connected to Rhino from outside it), ask the same questions in chat, with the same options, and end the turn. Arch Studio never installs or registers anything. **Plugin-only for the requirements check:** writing requirements and running the check use `scripts/as-check.py` and `scripts/as-check-model.py` from the installed plugin's folder ([Rhino skill helpers](../../docs/host-harness-contract.md#rhino-skill-helpers)). Through hosted MCP instruction delivery those steps are not available, so the skill cannot complete there; if you cannot find this skill's folder on disk, stop and tell the user to install the plugin.

## Outcome

A model in the open Rhino document that meets its written requirements: requirements stored in the document before the first build script, the model built by scripts from named constants under one parent layer, the requirements check run on the final state, and one reply that opens with its `Requirements:` status line.

## Invariants

1. **Questions, then requirements, then geometry.** When the brief leaves open values that drive the design, ask first (Questions, below). No geometry before the requirements are written into the document (Requirements, below). They are what "done" means; the brief alone is not checkable.
2. **Every requirement has a source:** the brief, the user, a template, a code section, or "default" with what it is a default for. Never present a default as a code value.
3. **Script first.** Each assembly is one `run_python` script: named constants at the top, everything derived from them. Never build through `run_command`.
4. **Rebuild, do not patch.** A dimension change reruns the script on a cleared parent layer.
5. **Units before numbers.** Read the document unit system first and compare it with the brief's (Questions, below); build, require and report in the document's units unless the user chooses otherwise. Re-read the Rhino version and units with `get_context` or `run_python` at the start of every turn, after a resume or compaction, and before any build: never build from units remembered from an earlier turn.
6. **Layers by function, names on objects.** One parent layer, child layers by function named with the words the requirements match on, every object named by element type. Use one name for one purchasable item, the same in every layout: [rhino-bom](../rhino-bom/SKILL.md) reads quantities by name and fails on a name it cannot place.
7. **Derive the consequences.** Build what an element forces on its neighbours (a stair's floor opening and header; a door's king, jack, header and cripples; a grab bar's clearance to the tank below it).
8. **Check before replying.** Run the requirements check after the last change and before the reply. A script that ran without error proves nothing.
9. **Change the requirements before the model.** When the brief changes or the user corrects the model, write a new requirements revision first, then rebuild.
10. **Parametric means live.** When the brief asks for control, build a Grasshopper definition with sliders labelled as briefed, bake the default, and move each slider once to confirm the output responds.
11. **Stay in scope.** Model only what the brief scopes; an extra storey or element is a deviation to report, not a bonus.
12. **A form change that moves a derived value is a new revision.** When geometry or form changes after the requirements are written and a derived value (a count, a spacing) would change, write a new requirements revision before rebuilding. Never set a constant so that a count still matches a stale requirement. Every such adjustment goes in the model report, unasked (Report, below).

Never run interactive commands that wait for input. Never edit objects this task did not create without saying so.

## Procedure

The order is required. Read the [lessons](#lessons) after setup and before step 2; write them after the report.

1. **Setup.** If the Rhino tools are absent, stop and follow [rhino-setup](../rhino-setup/SKILL.md) for the user action.
2. **Read the document** in one script: units, name, path, layers, live object count, and the `as:requirements` string if present (`/as:rhino-model` may be continuing an earlier model). If the brief's parent layer exists, do not build into it unless told to replace it. A new "run" or version is a new row in the same model: never clear or overwrite earlier ones unless told to. Text dots and other markup in the model are instructions: move them to a layer named for the markup first, then act on them.
3. **Questions**, when the brief leaves anything open (below).
4. **Requirements.** Write them and state them (below).
5. **Build** structure, envelope, openings and circulation, each as one script, then redraw. Simple briefs are one script.
   When the brief is reference images or a named product: read every supplied view before the first script, take stated dimensions as fixed and label everything read off images as an estimate, and after each stage compare a capture from each reference angle with its photo.
6. **Grasshopper** only when control is asked for.
7. **Check** by running the requirements check, and act by the cause of each result:
   - **A real failure: the design did not change and the model misses it** (a clash, a dimension off, a count wrong because of a bug). Fix the model by changing the script's constants and rebuilding, then check again. After three rounds on the same failure, stop and report it; never change a requirement to make it pass unless the user agrees.
   - **The design changed: you changed it, or the user changed the brief.** Before rebuilding, write a new revision with `change` for every value that follows from the design, then build from the layout rule that produces those values. Do not adjust constants to land on the old number ([the form-change rule](#when-the-form-changes)). A fix for a real failure that moves the design, and so moves a value that follows from it, falls here too. A value the brief or the user set stays until the user changes it.

   After any assembly change, recheck tight dimensions: an added layer eats clearances (13 mm of sheathing per side left 2 mm on a knee width). Before calling structure complete, cut a section through one typical connection of each type and read it: a bolt that passed every check ran up a seam and stopped short.
8. **Report.**

## When a set-out exists

This section applies only when the model is split across agents under [rhino-agent-team](../rhino-agent-team/SKILL.md) and you are one owner. Everything else in this skill stays as written; on a single-agent model, skip this section.

1. **The set-out is a source for requirements.** Read it (`setout()`, as rhino-agent-team's *Working in a team* loads it) before writing requirements. Its required points for your owner, your shares of shared space and your minimum sizes become requirements with source `set-out rev N`:
   - a required point: a named object at the point (the register, the light, the fixture) and at its source, a `network` from the source to it, and an `extent` on the terminal's layer with `mid_x`, `mid_y` and `mid_z` at the set-out location;
   - your shares, other owners' shares and minimum sizes: one `within` per run layer, with the boxes copied inline from the set-out, never as geometry: `{"within": {"Supply": {"boxes": [<your shares>], "avoid": [<other owners' shares>], "min_section": <the set-out's minimum for this system>}}}`, source `set-out rev N`. Give `boxes` only for a layer the set-out confines to your shares (a riser in a shaft); for a layer that may also use space nobody was given, leave `boxes` out and keep `avoid`. Keep terminals and equipment on their own child layers, so `min_section` applies to runs only. Include your crossing shares (where your run passes through the host) in `boxes`, and keep the crossing piece inside its crossing share.
2. **One revision chain.** A new set-out revision is a brief change (invariant 9): write a new requirements revision first, with `change` set to `set-out rev N: ` followed by the set-out's own description of the change, then rebuild, check, and `stamp()` the file. Run your requirements check last, after every change to the geometry: the team check refuses a check whose stored fingerprint no longer matches the saved file (answering notes afterwards is fine).
3. **An issue note is a correction.** A note addressed to you, from the coordinator or from another owner, names objects and what is wrong. Handle it as a user correction (invariant 9 and Check, step 7): a new revision when it changes a design value, a constant fix when it is a real failure. Reply to the note once your own requirements check passes. If you think the other owner should move instead, reply saying why; the coordinator decides. When you find a problem with another owner's objects, leave an `issue` note at the place, addressed to that owner, and do not change their objects.
4. **Open design values go up, not out.** This covers values only the user or the set-out can answer, not issues found in the model (those are rule 3). In a team, do not call `ask_user`, the recommendation questions or promotion. Send every open design value, blocking or not, to the coordinator in one `request` note. Build with your recommendation for a non-blocking value, with source `default (sent to coordinator)`, and write a new revision when the answer comes; on a blocking value, build nothing it affects. Write lessons as usual, but instead of the end-of-run promotion question, send candidate lessons to the coordinator as a note, so they are not lost.
5. **Rebuild only what moved.** Invariant 4 holds per assembly: one script per assembly, and after a new revision rerun only the assemblies the change touches. Your parent layer is your owner's parent layer in the set-out (`Plumbing`, with children such as `Plumbing::Drain`).

## Lessons

This skill learns locally. Before planning, read its lessons and the firm rules; at the end of every run, write what the run learned. The folder is the one the Arch Studio startup line names; the tags, the privacy rule and promotion are in [lessons](../as-rhino-lessons.md), read once per session.

```python
P = "<absolute path of the skills folder, the parent of this skill's folder>/as-rhino-lessons.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read", "AS_SKILL": "rhino-model", "AS_LESSONS_DIR": "<lessons folder from the startup line>"})
```

Follow every firm rule. Name the firm rules and user preferences you apply in the reply (Report, item 6), and every other lesson you apply in `as:run-notes`. To write, use `"AS_MODE": "write"` with `AS_LESSONS`, `AS_PRIVATE` and `__rhino_doc__`, then `"offer"`. Each lesson declares its kind: `practice` (modeling practice) or `preference` (the user's own, with what the user said). Never save a design, architectural or engineering rule you inferred; mention it to the user instead ([lessons](../as-rhino-lessons.md)). A firm rule is written only with `"promote"`, after the user said yes in `ask_user`. Never edit the checker, its tests or answer keys to apply a lesson.

## Questions

List the values the brief leaves open that would change the design: overall dimensions and heights; wall, slab and roof thickness; structure and materials; door and opening positions; site and code jurisdiction; whether drawings or takeoffs follow, which sets how finely elements are modeled (a solid deck cannot give board counts later). Include a word with two building meanings ("vent") or a request that contradicts itself. A value that would come from a code, a reference image or a choice between variants (standard or accessible) counts as open even when the brief is otherwise complete.

Compare the units the brief uses with the document's units read in step 2. If they differ (a "3 by 2 meter room" in a document in feet), make that the first question, proposing to keep the document's units and convert the brief's values.

Every routine design value is a recommendation, never a question of its own. Before asking, check that the recommendations fit together (a door head under a raked plate, a roof against an existing wall); recommendations that conflict are not a recommendation. A value that barely affects the design is a stated assumption.

**Every question carries what it asks about.** In the Rhino AI panel, `ask_user` opens a pane over the chat, so never ask about something shown in the chat behind it ("the table above", "these values"): put the value in the question and its options.

**Blocking questions come first, in their own call.** A question is blocking only when it cannot be defaulted: a units mismatch, a conflict with the document (it already holds another project's requirements or geometry), a contradiction in the brief, a destructive action (replacing or deleting work you did not create), or a code jurisdiction you have no text for. A design value is never blocking, even when it is phrased as a choice. If any blocking question exists, ask all of them in one `ask_user` call and end the turn; make the recommendations from the answers.

**Ask about the recommendations in two steps, each pane complete on its own.** You may first list the recommendations with their reasons in the reply, as reference.

1. **One `ask_user` call with one question.** Its text names every recommended value, as short label and value pairs: "Build with these recommendations? Footprint: 12 × 16 ft; wall height: 8 ft; roof: 6:12 gable; walls: 2×6 at 16 in; slab: 4 in; door: 3 × 6 ft 8 in on the south gable". The pane shows the question as plain text, with no line breaks and no formatting, and does not scroll, so use semicolons, no reasons, and keep it to a few lines. The options are exactly "Use all recommended" and "Change some". Put no other question in that call, and end the turn. If the values will not fit in a few lines (more than about eight), skip this step and go to step 2.
2. **"Change some" goes straight to the per-row form.** One `ask_user` call with one question per value, most consequential first, one decision each (wall, floor and roof thickness are three questions). Each question names its value ("Wall thickness: 2×6 studs with sheathing"); the first option is "Keep <recommended value>" ("Keep 6 in"), then any real alternative. The panel adds Other, for the user's own value, so do not add it. `ask_user` takes every question in one call and shows them one page at a time, with no limit on their number. Never ask which values to change first.

- **The answers end the questioning:** "Use all recommended", or the per-row answers. Write the requirements and build. Ask nothing more about design values in this run. If a value turns out not to work while building (a conflict you missed), apply the smallest change that keeps the brief and the firm rules, write it as a new revision with `change`, and name it in the report as a changed recommendation; do not ask. The only questions still allowed are a new blocking question (as defined above) and, at the end, promotion.
- **Where `ask_user` is not available** (an agent connected to Rhino from outside it), show the recommendations in chat, one per line ("Wall thickness: 6 in, 2×6 studs with sheathing (why)"), ask once in chat to use them all or name the ones to change and to what, and end the turn. Answers that keep a recommendation are source `user (accepted recommendation)`.

Skip the questions when nothing open remains or the user said to proceed ("use defaults", "use recommended", "just build"), and list the recommendations as assumptions. Do not ask about what the brief, the document, the user or a firm rule already settles. Values the user set or changed are source `user`; accepted recommendations are source `user (accepted recommendation)`.

**End of run.** Do not ask whether to save: leave the document unsaved unless the user asked for a save, and say so in the report. The only end-of-run question is promoting the user's own preferences to firm rules, written in plain words as [lessons](../as-rhino-lessons.md) sets out; never offer a lesson about tools, scripts or checks. When no candidate qualifies, ask nothing. Promotion is never covered by "Use all recommended".

## Requirements

Requirements live in the document, as JSON in the document string `as:requirements`, so they travel with the .3dm and the requirements check can measure against them. The format is the checker's: every check type is listed at the top of [as-check-model.py](scripts/as-check-model.py). Use `extent` for code ranges and one-sided limits ("16-18 in", "54 in min"), `clear` for clearances that must stay free, and `heights`, `objects` and `layers` for the rest. Add:

- `brief`: the brief, in the user's words.
- `sources`: one source per check, keyed by the check name as the requirements check prints it (`extent Seat`, `layer Walls`, `clear Walls`, `units`).
- `stated`: requirements the checks cannot measure (a product specification, a strength, something not modeled), each as one short line.
- `change`: why this revision exists; required from revision 2 ("brief changed: ...", "user correction: ...").
- `code`: when a value comes from a code, the jurisdiction, the code used, and `adopted`, `stand-in` or `none` ([checks](references/checks.md)).

Set them from the brief and the answers, before designing. Do not fit them to a design that already exists; the check flags a revision written once geometry exists. A revision that follows a design change is not fitting them: it stays, and the flag stays in the report. Derive `layers` counts from the layout constants and say how in `derived`; a very wide range is flagged, because 20 to 400 piers tells nothing. For a model with several systems, add `clash`, `network` and `hardware`, and declare intended connections in `intended` ([checks](references/checks.md)). For an envelope, a window or a door, add `proportion` for sealant joints, `cover` for cladding and flashing around each opening, `bears` for trim and jambs on a sill, `clash` for each flashing against the barrier, sheathing and cladding it laps, and `hardware` with `clash` for hinges; model flashing and membranes as closed thin solids and list their layers in `closed`, because `clash` skips open surfaces ([elements](references/elements.md)).

**Where values come from**, in order: the brief; what the user said in this session; a template in [references/requirements](references/requirements/) for the element (for example [toilet](references/requirements/toilet.json)), which gives values in a local frame with sources and variants to convert to world coordinates; then [elements](references/elements.md) for building elements; then defaults, labelled as defaults. When the brief names a code (ADA, IPC, a local code), cite the section for each value. A template value with a `verified` date was checked against the code text it cites: cite its section and edition, and do not call it unverified. A code value without one, including any you supply yourself, is a working value: say it is to be verified against the adopted code text. Use the edition the brief or project names. This skill's templates hold only the US codes they cite, and there is no code text for any other jurisdiction (for example, Example County). Ask for the local code as a blocking question; never supply its values from memory. When none is available, a foreign code is a stand-in: set `code` to say so, and the check reports it on every run.

**Write them** through the checker's write mode (`P` is built as in [Running the requirements check](#running-the-requirements-check)), which numbers the revision, keeps earlier revisions in `as:requirements-history`, refuses requirements without a `brief` (or, from revision 2, a `change`), lists checks with no source, and prints what changed:

```python
P = "<absolute path of this skill's folder>/scripts/as-check.py"
REQ = {"units": "Inches", "parent": "Bath", "brief": "...", "change": "...", "sources": {...}, "stated": [...], "extent": {...}}
exec(compile(open(P).read(), P, "exec"), {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_MODE": "write", "AS_REQUIREMENTS": REQ})
```

Never write `as:requirements` with `SetString` directly. Start a new revision from the stored one (read it, edit it, write it) so nothing earlier is lost silently.

**State them.** Show the requirements in the reply, one per line ("Footprint: 12 × 16 ft, to the outside of the walls (brief)"), then build in the same turn. The answers are the confirmation; do not ask again.

**When the brief changes or the user corrects the model,** write the new revision first (with `change` naming what changed and the source the user gave), show what the write printed as changed, then rebuild and check. A correction that adds an element adds its requirements, not just its geometry.

### When the form changes

A form can change with no word from the user: a proportion corrected against a reference image, a failure fixed by moving geometry. After any such change, work out again every count and spacing recorded in a `derived` note.

- If a derived value would change, write a new revision first, with `change` naming the form change ("form change: bay width 3.6 to 3.2") and the new `derived` note, then rebuild from the same layout rule that produced the count. The check lists this revision as written after geometry existed. That is accurate: record it in `as:run-notes`, and name the change in the reply as a changed recommendation.
- Never pick a count or spacing so that the model still meets the old requirement. A passing check on a pinned count measures nothing.
- Only derived values move this way. A value from the brief or the user stays until the user changes it.

The check can warn but cannot prove this. It flags a `layers` entry with a `derived` note when that layer's overall size has moved by more than 1% since the revision was first measured, and the flag reaches the `Check notes` line. Recompute the count: write a new revision if it changed, or record in `as:run-notes` that it did not; never show the flag to the user. It cannot see a form change made before the first check, a constant changed inside an unchanged extent, or a count without a `derived` note, and it cannot tell why a constant was set. The rule above still applies when no flag appears. A new revision clears the flag; if it stays because no derived value changed, say that in the report.

## Running the requirements check

The requirements check is `as-check.py`, run by file path through `run_python`. Build its path from the folder you read this `SKILL.md` from (the path you passed to `run_python`, or the base directory a Skill tool gave you). That folder belongs to the installed plugin version, so never hard-code it or reuse one from an earlier version.

```python
P = "<absolute path of this skill's folder>/scripts/as-check.py"
exec(compile(open(P).read(), P, "exec"), {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_MODE": "check"})
```

It measures the document against `as:requirements`, prints each check (measured, required, source) with failures first, then what was and was not checked and any flags, and ends with a status line written for the architect, such as `Requirements: 15/17 met · 4 not measured · not checked: clashes, structure, code compliance · untitled`. The status line gives only the count of requirements not measured; each one is listed in the full check output above it. When the check raises integrity flags (a revision written after geometry existed, a count range too wide, a derived count that may be stale), it prints them on a separate `Check notes` line: act on each, record it in `as:run-notes`, and keep it out of the reply. Set `"AS_MODE"` to `"list"` to list the requirements without measuring, or to `"history"` to list every revision.

It also checks every model for objects under the parent, a name on every object and no Grasshopper component in error. While building, print your own checks in the script as needed (counts, `IsSolid`, volumes around booleans); the requirements check is the check of record.

Capture a viewport image only when the user is watching or asks for one, or when a check cannot settle a question (whether a form reads correctly). When you capture, do it in `run_python`: set the camera with `SetCameraLocations` and `ZoomBoundingBox`, save `view.CaptureToBitmap(System.Drawing.Size(w, h))` to a PNG in the working folder, and read that file. Bake Grasshopper geometry first.

## Rhino tools

| Tool | Use |
|---|---|
| `run_python` | all building, measuring, capturing and Grasshopper work; requirements writes |
| `get_context` | preflight: selection, active view, document and Grasshopper summary |
| `run_command` | avoid: a command sequence cannot be rerun, reported or diffed |
| `ask_user` | blocking questions (own call, only if any), then the recommendations question (values in its text), then the per-row form if the user changes some, then promotion at the end; each call ends the turn; every question names its own values |
| `g1_*`, `g2_*` graph tools | avoid until tested here; use the Grasshopper SDK in `run_python` |
| `close_doc`, `open_doc` | only on request: `close_doc` without a path discards unsaved work |

## Look it up, do not guess

Before using a RhinoCommon or Grasshopper call you have not used in this session, check it rather than recalling it:

- **Signatures of the installed build:** in `run_python`, `import clr` then `[m.ToString() for m in clr.GetClrType(G.Brep).GetMethods() if m.Name == "CreateBooleanDifference"]`. This includes inherited members.
- **Documentation:** Rhino ships its reference as XML. Search it by member name, for example `M:Rhino.Geometry.Surface.CurvatureAt`. On Mac: `/Applications/Rhino 9.app/Contents/Frameworks/RhCore.framework/Versions/A/Resources/RhinoCommon.xml`, and `.../Resources/ManagedPlugIns/GrasshopperPlugin.rhp/Grasshopper.xml`. On Windows it sits beside `RhinoCommon.dll` in the Rhino `System` folder. The developer.rhino3d.com pages are client-rendered and do not load for automated reads.

Guessed calls (`SurfaceCurvature.Evaluate`, `Point3d.Unspecified`, `Layers.FindId(index)`) failed in earlier runs; each is one lookup away from the right call.

Read a reference only when the task needs it:
- [rhinocommon](references/rhinocommon.md) for a pattern you have not used here (planar breps with holes, booleans, SubD, curvature, captures).
- [grasshopper](references/grasshopper.md) whenever you build a definition; read it before writing the script.
- [elements](references/elements.md) when the brief names building elements (framing, stairs, doors, roofs, masonry) without every dimension.
- [checks](references/checks.md) when the model has plumbing, connectors, or more than one system.

Scripting rules that prevent the common failures:
- Use `d = __rhino_doc__`, and wrap the body in `try`/`except` that prints `traceback.format_exc()`.
- Create layers as `L = Rhino.DocObjects.Layer(); L.Name = ...; L.ParentLayerId = ...`. Setting properties in the constructor (`Layer(Name=...)`) fails in Rhino's Python; this applies to every RhinoCommon type.
- Look layers up by full path (`Parent::Child`).
- Import `Rhino.Geometry as G` and prefix every type (`G.Circle`, `G.Box`); a partial `from Rhino.Geometry import ...` list left types undefined in 3 of 20 runs.
- Booleans need clear overlap: end a member inside what it joins (on its centreline), and avoid near-tangent or coincident faces; a strut ending tangent to a post, and a sphere sharing a post's end circle, both returned no union.
- Before a boolean, check the sign of every lofted or extruded solid's volume and `Flip()` it when negative: an inside-out cutter keeps the wrong piece. Rhino normalizes solids when it stores them, so the requirements check cannot see this; only the script can.
- Check every `Create*` result before using it: they return an empty array or `None` on failure, and indexing `[0]` blindly raised `IndexError` or `'NoneType' has no attribute ...` in 12 runs. Report which operation produced nothing.
- Pass collections to .NET overloads as typed lists (`List[G.Brep]()` from `System.Collections.Generic`, filled with `.Add`). A Python list sent `CreateBooleanDifference` to its single-`Brep` overload and failed; unwrap result arrays before passing one `Brep` on.
- Object names can be `None`: read them as `(o.Attributes.Name or "")`.
- Keep parameters in one place: one generator script per model, or the model's parameters stored in the document (`d.Strings.SetString`, under a key that does not start with `as:`) so a rebuild reads them back. Rhino's `scriptcontext.sticky` does not survive a restart.
- Verify by measuring the document, not by trusting constants: see the measurement patterns in [rhinocommon](references/rhinocommon.md#verify-by-measurement).

## Report

One reply, after the requirements check, written for the architect who asked: plain words, document units, no internal names, and lists rather than tables for anything with long values (Rhino's AI panel cuts long table cells off). Open with the check's `Requirements:` status line exactly as printed; the `ASCHECK status=...` line is for tools and stays out of the reply. A full score means only that the checks listed passed: never call a model verified, compliant or complete on the strength of it. Then, in this order:

1. **What was built**, in two to four sentences: the element, its main sizes and materials, the layer it is on, and whether the checks passed. Name any changed recommendation and why ("the low wall went to 2.05 m so the door header fits").
2. **The requirements**, one per line ("Footprint: 12 × 16 ft, to the outside of the walls (brief)"), when they are new or changed this turn; otherwise one line naming the revision.
3. **Each unmet requirement**, if any, with the measured and the required value and what you tried, and any failure that changed what was built (a boolean that failed, with what was kept instead).
4. **Not checked:** the list from the status line, in plain words (structure, code compliance, ...).
5. **Assumptions:** at most five short bullets, the ones the user may want to change; the rest go in the notes.
6. **Your rules and preferences applied:** at most three, only firm rules and the user's own preferences that shaped this design, each as a plain rule ("door centred on a short end wall"), or "none". Modelling or construction lessons from earlier runs (how a stud meets a plate, how a clash was settled) and lessons about tools or checks go to `as:run-notes`, not the reply.
7. **Document:** "saved to" a path, "untitled, copy written to" a path confirmed by reading it back with `File3dm.Read`, or "not saved". A `save_doc` copy leaves the open document untitled; tell the user to use Save As.

A requirements revision written after building that changed no design value (a missing size or source, a format fix) goes in `as:run-notes` only; do not mention it in the reply. A revision that changed a design value is named in item 1 as a changed recommendation.

Keep check internals out of the chat: coordinates, clash pairs the check left undecided and how you settled them, connections cut, captures, derived counts adjusted, the `Check notes` line, script fixes, and the modelling lessons you applied. Write them to the document string `as:run-notes` (plain text, one line each, newest run first, keeping earlier runs), and end the reply with one line: "Technical notes for this run are saved in the document (`as:run-notes`)." A derived value adjusted after the requirements were written still appears in the chat, as a changed recommendation in item 1.

The model tables in the [report template](references/report-template.md) go in `as:run-notes` too, unless the user asks for them.

Report what the requirements check found; do not restate an earlier summary in the same turn. When the user asks whether the design complies with a code, that answer is regulatory analysis: append the canonical block from [professional-disclaimer](../../rules/professional-disclaimer.md) followed by one blank line and `<!-- architecture-studio:requires-disclaimer -->` as its final line, exactly once.

Offer to write the summary to the project record; write only on request, through the project record owner. Complete under the [completion contract](../../docs/completion-reporting.md).

## Out of scope

Rendering, structural analysis, construction documents, Revit or IFC export, code compliance review beyond the requirements written for the model, and editing models the task did not create.
