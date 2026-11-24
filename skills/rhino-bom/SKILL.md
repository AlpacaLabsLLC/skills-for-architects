---
name: rhino-bom
description: "Take quantities from a Rhino model built under one parent layer with every object named by element type: a bill of quantities per layout in which every object lands in exactly one line, every line states its source, and what the model does not contain is listed with the reason. Use when the user asks for a BOM, takeoff or quantities from a Rhino model. Not for pricing, procurement or structural sizing, and a count does not validate the thing counted."
---

# /as:rhino-bom

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-bom`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Requires Rhino 9 with an open document and its `run_python` tool. **Plugin-only:** the quantities and their reconciliation use `scripts/as-bom.py` from the installed plugin's folder ([Rhino skill helpers](../../docs/host-harness-contract.md#rhino-skill-helpers)); through hosted MCP instruction delivery this skill is not available. If you cannot find this skill's folder on disk, stop and tell the user to install the plugin. In the Rhino AI panel, there is no Skill tool: read this file and its references by path with `run_python`.

## Outcome

One CSV per layout under a folder the user chose, and a reply opening with the script's `BOM:` line, in which the object total reconciles and nothing was silently left out.

## Invariants

1. **Everything in the model, by default.** Offer the full scope first. A shorter scope is the user's choice, stated in `covers`.
2. **Reconcile to the object count.** Every object lands in one line or in `excluded` with a reason. One object with no line fails the run, and no CSV is written.
3. **Quantities depend on names.** The script reads the object names and layers that [as-rhino-model](../rhino-model/SKILL.md) gives every object. A generic or missing name loses the item, so fix the model's names rather than adding a catch-all rule.
4. **Every line states its source:** measured from the model, calculated, or assumed, with the reason in the same column.
5. **List what is not counted, with the reason.** Fittings, traps, valves, fasteners, footings and rebar are usual cases. An unmentioned omission reads as zero. `not_counted` is required.
6. **Cut lengths are firm; purchase counts depend on assumed stock.** Keep them in separate lines. Identical and near-identical members share one line with a count and a cut-length range; the CSV's cut schedule keeps every exact length, and nesting uses them.
7. **A count does not validate the thing counted.** Mark hardware `to_engineer`.

## Procedure

Read the [lessons](#lessons) after setup and before asking; write them after the report.

1. **Read the document** with one script: units, layers, and whether the model's parent layer exists. If the Rhino tools are absent, follow [rhino-setup](../rhino-setup/SKILL.md) for the user action.
2. **Ask** only what the model cannot answer, in one `ask_user` batch: scope (default everything), layouts, stock lengths, sheet sizes, waste, output folder.
3. **List the names**: run with `"AS_MODE": "names"`. Every name it prints needs a rule or an exclusion.
4. **Write the specification** from [quantities](references/quantities.md), which lists the measures and the choice of measure by geometry.
5. **Run** by file path. Build the path from the folder you read this `SKILL.md` from, which belongs to the installed plugin version; never hard-code it or reuse one from an earlier version:

```python
P = "<absolute path of this skill's folder>/scripts/as-bom.py"
exec(compile(open(P).read(), P, "exec"), {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_MODE": "check", "AS_BOM": SPEC})
```

   `"check"` reconciles and writes nothing. Fix every unclassified name and every object it could not measure, then run with `"AS_MODE": "run"`. Never add a rule that catches everything to make it pass.
6. **Read one CSV back** and compare its object total with the `BOM:` line.
7. **Rerun after any model change.** A BOM is one state of the model; say which layouts have none.

## Lessons

This skill learns locally. Before planning, read its lessons and the firm rules; at the end of every run, write what the run learned. The folder is the one the Arch Studio startup line names; the tags, the privacy rule and promotion are in [lessons](../as-rhino-lessons.md), read once per session.

```python
P = "<absolute path of the skills folder, the parent of this skill's folder>/as-rhino-lessons.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read", "AS_SKILL": "rhino-bom", "AS_LESSONS_DIR": "<lessons folder from the startup line>"})
```

Follow every firm rule, and name each lesson you apply in the report. To write, use `"AS_MODE": "write"` with `AS_LESSONS`, `AS_PRIVATE` and `__rhino_doc__`, then `"offer"`. A firm rule is written only with `"promote"`, after the user said yes in `ask_user`. Never edit the checker, its tests or answer keys to apply a lesson.

## Report

Open with each `BOM:` line exactly as printed. Then: the file paths; when layouts share most lines, "same in every layout" and a short table of differences; every assumed line; the not-counted list; the stock lengths and waste used, as working values; the lessons applied and written, or "none". Complete under the [completion contract](../../docs/completion-reporting.md).

## Out of scope

Pricing, procurement, supplier selection, and whether a modeled connection works. For a quantity table on a sheet, hand the CSV to [rhino-thinline](../rhino-thinline/SKILL.md).
