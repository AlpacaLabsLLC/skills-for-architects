---
name: rhino-axon
description: "The view for an axonometric sheet from a Rhino 9 model: camera and projection, exclusions and cut-away crop, hidden-line occlusion, joint and detail-cut selection, and the building lock, handing linework and cut faces to rhino-thinline. Use when the user asks for an axonometric, axon sheet or exploded axon from a Rhino model; read rhino-thinline too, for the conventions. Not for coloured images or renders, and it never edits the model to get a view."
---

# /as:rhino-axon

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-axon`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Requires Rhino 9 with an open document and its `run_python` tool. **Plugin-only:** the view and its checks use `scripts/as-axon.py` from the installed plugin's folder ([Rhino skill helpers](../../docs/host-harness-contract.md#rhino-skill-helpers)); through hosted MCP instruction delivery this skill is not available. If you cannot find this skill's folder on disk, stop and tell the user to install the plugin. In the Rhino AI panel, there is no Skill tool: read this file and its references by path with `run_python`.

## Outcome

An axonometric on a layout in the open document: the view chosen, projected and drawn as linework, its details cut from the real joints, and the building unchanged. The sheet itself (weights, hatch, annotation, layout, the request record and the PDF) follows [rhino-thinline](../rhino-thinline/SKILL.md); read that skill too, and report under both.

## Invariants

1. **True black and white comes from hidden-line vectors,** not from a line-based display mode. The output is static: after a model change, regenerate it.
2. **A detail bubble is a locator.** Its leader lands on the real joint, and it is cut from that same member.
3. **The sheet never edits the building.** Draw from the model as it is: no deleting, moving, trimming or rebuilding building geometry to make a leader or a view work. `setup_sheet` records the building and `check_sheet` fails if any of it was changed or removed. If a leader cannot reach a joint, pick another joint or move the detail; if the model itself is wrong, say so and stop.
4. **Leave out or cut away in the drawing only.** `exclude` and `crop` act on in-memory copies; the model is never trimmed to show what is behind.
5. **Hand linework, not choices.** This skill decides what is seen and draws it on the page under its own layer roots; rhino-thinline's conventions read it from there and never move the camera ([the handoff](references/views.md#the-linework-handoff)).
6. **Never change a check's threshold, and never delete a failure record or request to pass a check;** report what could not be placed.

## Procedure

Read the [lessons](#lessons) after setup and before asking; write them after the report.

1. **Setup and ask** as in [rhino-thinline](../rhino-thinline/SKILL.md) steps 1 and 2: one `ask_user` batch for drawing, scale, sheet size, details and title text.
2. **Load the library** by file path. It loads rhino-thinline's library into the same namespace first, so one load gives both. Build the path from the folder you read this `SKILL.md` from, which belongs to the installed plugin version; never hard-code it or reuse one from an earlier version:

```python
P = "<absolute path of this skill's folder>/scripts/as-axon.py"
S = {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P}
exec(compile(open(P).read(), P, "exec"), S)
```

3. **Build in this order** with one script per step, following [views](references/views.md) and thinline's [sheets](../rhino-thinline/references/sheets.md): `setup_sheet` for the layout and parallel detail, with its target document active (a headless document need not be); main linework, with every owner's top layer as the source when the model was assembled from several files; annotation and callouts; details, each with `cut_detail`; title block and table. Annotation goes after linework, so it draws on top.
   - **When a detail or label cannot be placed** (`place_locator` or `place_label` refuses every point and `check_sheet` names it), the joint is inside the drawing. Never edit, trim or delete the model to clear a path. Instead:
     1. Draw a cut-away with `main_linework(crop=(x0, y0, z0, x1, y1, z1))`, ending the box at the edge of the window, door or joint you want to show, so that joint sits on the drawing's outline. The cut-away's cut faces are drawn in outline, not hatched; only details hatch their cut faces.
     2. Try the other view side (for example `direction` with x negated), so the cut face of the cut-away turns away from the viewer and the joint becomes the drawing's edge.
     3. Give the placers several points along the part's visible outside edge, nearest the details.
4. **Review** as in rhino-thinline step 5.
5. **Check the sheet** with `S["check_sheet"]`, passing the main linework root, the main detail and its scale, and the drawing field. Loaded from here it is the full check: rhino-thinline's conventions and this view in one list. Then export and run the PDF check as in rhino-thinline step 6.

## Lessons

This skill learns locally. Before planning, read its lessons and the firm rules, and rhino-thinline's; at the end of every run, write what the run learned about the view here and about conventions there. The folder is the one the Arch Studio startup line names; the tags, the privacy rule and promotion are in [lessons](../as-rhino-lessons.md), read once per session.

```python
P = "<absolute path of the skills folder, the parent of this skill's folder>/as-rhino-lessons.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read", "AS_SKILL": "rhino-axon", "AS_LESSONS_DIR": "<lessons folder from the startup line>"})
```

Follow every firm rule, and name each lesson you apply in the report. To write, use `"AS_MODE": "write"` with `AS_LESSONS`, `AS_PRIVATE` and `__rhino_doc__`, then `"offer"`. Each lesson declares its kind: `practice` (modeling practice) or `preference` (the user's own, with what the user said). Never save a design, architectural or engineering rule you inferred; mention it to the user instead ([lessons](../as-rhino-lessons.md)). A firm rule is written only with `"promote"`, after the user said yes in `ask_user`. Never edit the checker, its tests or answer keys to apply a lesson.

## Report

rhino-thinline's report, plus: the scale read back, what was excluded or cut away and why, each detail's joint, and any label or detail that could not be placed. Name the lessons applied and written, or "none". Complete under the [completion contract](../../docs/completion-reporting.md).

## Out of scope

Editing the model to get a view, coloured images ([rhino-display](../rhino-display/SKILL.md)), and the drawing conventions themselves ([rhino-thinline](../rhino-thinline/SKILL.md)). A ghosted envelope for closed buildings is not built yet.
