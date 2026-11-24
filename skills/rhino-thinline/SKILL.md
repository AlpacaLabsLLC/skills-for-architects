---
name: rhino-thinline
description: "Drawing conventions for black and white vector sheets from a Rhino 9 model: a line hierarchy, line styles, hatch by material on the cut faces of details, labels and leaders, detail tags, a title block, the sheet layout, a tamper-proof request record and a checked PDF. Use when the user asks for a line drawing, drawing sheet or black and white export from a Rhino model; for an axonometric, load rhino-axon, which chooses the view and loads this skill's library. Not for construction documents, coloured images or renders; line weights and hatch patterns are working conventions."
---

# /as:rhino-thinline

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-thinline`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Requires Rhino 9 with an open document and its `run_python` tool. **Plugin-only:** the sheet and its PDF check use `scripts/as-sheet.py`, `as-sheet-core.py` and `as-pdf-check.py` from the installed plugin's folder ([Rhino skill helpers](../../docs/host-harness-contract.md#rhino-skill-helpers)); through hosted MCP instruction delivery this skill is not available. If you cannot find this skill's folder on disk, stop and tell the user to install the plugin. In the Rhino AI panel, there is no Skill tool: read this file and its references by path with `run_python`.

## Outcome

A layout in the open document and a one-page vector PDF, read back and passed by the PDF check, in pure black and white, with the sheet's limits said plainly in the reply.

This skill owns how the sheet looks: weights, styles, hatch, annotation, layout, the request record and the PDF. It never chooses a view. The view for an axonometric (camera and projection, exclusions and crop, occlusion, joint and detail-cut selection, the building lock) is [rhino-axon](../rhino-axon/SKILL.md), which draws the linework and hands it here ([the handoff](../rhino-axon/references/views.md#the-linework-handoff)).

## Invariants

1. **The main drawing is the focus.** Details serve it and are sized to the space left.
2. **The line hierarchy is the drawing.** Filled forms hide what is behind them, and silhouette, edge and receding lines are separate thin strokes on separate layers ([linework](references/linework.md)).
3. **Black and white only.** Strokes and hatch are black on white; colour language in notes fails the check. The linework is static: after a model change, the view regenerates it.
4. **Detail leaders are orthogonal only,** and a label's leader ends in a dot on its part.
5. **Hatch only real cut faces, by material.** Cut faces are hatched in the round details only; a cut-away in the main drawing is drawn in outline, not hatched. The patterns are working conventions, not checked against a standard; say so on request.
6. **Measure, do not estimate.** Text boxes, margins and scale are read from the document.
7. **Verify the PDF by parsing it, and an empty parse is a failure.** A sheet is not done until `as-pdf-check.py` passes.
8. **Line weights are provisional.** They were accepted on screen and have not been proven on paper. Say so in every report until a printed sheet accepts them.
9. **Never change a check's threshold; fix the sheet.** The checks' limits are fixed in the library, not arguments. When a check fails, move or resize what it names.
10. **Never delete a failure record or request to pass a check; report what could not be placed.** Every label, locator and detail you ask for is recorded, and `check_sheet` fails each one the sheet does not show, and fails an edited or deleted record. A label that finds no clear leader stays a failure until it is drawn; if you stop there, name each unplaced item in the report.

## Procedure

Read the [lessons](#lessons) after setup and before asking; write them after the report.

1. **Setup.** If the Rhino tools are absent, follow [rhino-setup](../rhino-setup/SKILL.md) for the user action.
2. **Ask** in one `ask_user` batch only what is open: drawing, scale, sheet size, details, title text. Scale and title are open unless the request gives them: ask for both; when nobody can answer, choose them and say in the report that you chose them. Propose a scale in the document's unit system: an imperial architectural scale (such as 1/4" = 1'-0", 1:48) for a document in feet or inches, a metric one (such as 1:50) for a metric document, and write it that way in the title block. Details follow from the drawing, not the reverse.
3. **Load the library** by file path. For an axonometric, load [rhino-axon](../rhino-axon/SKILL.md)'s `as-axon.py` instead: it loads this library first, and the sheet script then has both. For linework from another view, load this one alone. Build the path from the folder you read this `SKILL.md` from, which belongs to the installed plugin version; never hard-code it or reuse one from an earlier version:

```python
P = "<absolute path of this skill's folder>/scripts/as-sheet.py"
S = {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P}
exec(compile(open(P).read(), P, "exec"), S)
```

4. **Build in this order** with one script per step, following [sheets](references/sheets.md): `new_sheet` for the layout, border and title column (axon's `setup_sheet` calls it); the view's linework (axon's `main_linework`); annotation and callouts; details (axon's `cut_detail`); title block and table. Annotation goes after linework, so it draws on top.
   - Label components with `place_label`: it puts each label in the clear paper nearest its part, with a straight leader ending in a dot on the part, and refuses a leader that would cross the drawing. When a label or detail cannot be placed and `check_sheet` names it, the fix is in the view: follow [rhino-axon](../rhino-axon/SKILL.md)'s steps, never edit the model.
5. **Review** the whole sheet, then zoom each new element. Each round of review in the source session found something new. With no viewport, run `S["preview_sheet"](d, page, "<absolute path>.png")`: look at the PNG if you can open images, cropping it to zoom. It also prints and returns a text summary (the closest rings, leaders and text with their distances in mm, what sits nearest the field's edge, and any detail ring that is mostly empty); act on that when you cannot see the image.
6. **Check the sheet** with `S["check_sheet"]`, passing the drawing field (margins are checked against a fixed 10 mm); loaded through rhino-axon, it is the full check and also takes the main linework root, the main detail and its scale. Then export with `S["export_pdf"]` and run the PDF check:

```python
P = "<absolute path of this skill's folder>/scripts/as-pdf-check.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_PDF": "<absolute path>.pdf", "AS_PDF_SIZE": [914.4, 609.6]})
```

## Lessons

This skill learns locally. Before planning, read its lessons and the firm rules; at the end of every run, write what the run learned. The folder is the one the Arch Studio startup line names; the tags, the privacy rule and promotion are in [lessons](../as-rhino-lessons.md), read once per session.

```python
P = "<absolute path of the skills folder, the parent of this skill's folder>/as-rhino-lessons.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read", "AS_SKILL": "rhino-thinline", "AS_LESSONS_DIR": "<lessons folder from the startup line>"})
```

Follow every firm rule, and name each lesson you apply in the report. To write, use `"AS_MODE": "write"` with `AS_LESSONS`, `AS_PRIVATE` and `__rhino_doc__`, then `"offer"`. A firm rule is written only with `"promote"`, after the user said yes in `ask_user`. Never edit the checker, its tests or answer keys to apply a lesson.

## Report

The `ASPDF` result and the measurements it printed, the path of the PDF and the margins measured (the view reports the scale read back). State that the linework is static and how to regenerate it. State that weights are provisional and that hatch patterns are working conventions. These caveats go in the reply, not on the sheet: the sheet carries only drawing content, notes about the drawing and the title block. Name the lessons applied and written, or "none". Complete under the [completion contract](../../docs/completion-reporting.md).

## Out of scope

Choosing the view, cutting details and occlusion: [rhino-axon](../rhino-axon/SKILL.md). Construction documents, code review and engineering. For coloured images use [rhino-display](../rhino-display/SKILL.md). Quantity tables are drawn from a [rhino-bom](../rhino-bom/SKILL.md) CSV, and a lookup that does not match exactly one row fails.
