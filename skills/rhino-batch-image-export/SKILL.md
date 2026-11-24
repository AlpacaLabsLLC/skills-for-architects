---
name: rhino-batch-image-export
description: "Batch-export view images of a Rhino 9 model (options, views, layer sets) in one display mode, each file checked against the mode: a blank image, or colour in a mode that must have none, fails the batch. Sets up the display modes, views and materials the export needs. Use when the user asks for a batch of captures or viewport images of options, views or layer sets, or for images in a display mode. Not for photorealistic rendering, or black and white vector sheets, which rhino-thinline makes."
---

# /as:rhino-batch-image-export

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-batch-image-export`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Requires Rhino 9 with an open document and its `run_python` tool. **Plugin-only:** the image export and its file-by-file check use `scripts/as-batch-image-export.py` from the installed plugin's folder ([Rhino skill helpers](../../docs/host-harness-contract.md#rhino-skill-helpers)); through hosted MCP instruction delivery this skill is not available. If you cannot find this skill's folder on disk, stop and tell the user to install the plugin. In the Rhino AI panel, there is no Skill tool: read this file and its reference by path with `run_python`.

## Outcome

A folder of PNGs the user named, in which every file was read back and matched the requested mode, and a reply opening with the script's `Export:` line.

## Invariants

1. **Verify the exported file, not the viewport.** A batch came out in colour while the viewport showed the requested mode. The batch fails when any file does not match, and the failed files are moved aside with a `FAILED-` prefix.
2. **Name the mode in the capture.** Set it on the viewport and pass it to `CaptureToBitmap`; never rely on the mode already showing.
3. **Capture only by script.** Never use the capture tool's `cameraLocation`, `target` or `view` arguments, which blank or rewrite views. Set the camera in `run_python` and let the view settle ([display](references/display.md)).
4. **Leave the document as found.** Layer visibility, camera and display mode are restored after every batch, and the batch fails if layers, materials or the object count changed.
5. **No temporary colours or materials.** A temporary red reached delivered images. If one is unavoidable, restore and verify it before capturing.

## Procedure

Read the [lessons](#lessons) after setup and before asking; write them after the report.

1. **Setup.** If the Rhino tools are absent, follow [rhino-setup](../rhino-setup/SKILL.md) for the user action. List modes with `"AS_MODE": "modes"`.
2. **Ask** in one `ask_user` batch only what is open: mode, views, layouts, image size, output folder. Each question carries what it asks about, with your proposal as the first option ("Keep 1/4\" = 1'-0\""), since the question pane covers the chat; never refer to text shown behind it. Layouts are layer paths. If an interior view is wanted, say in that batch that it cannot be exported (below). Where `ask_user` is not available (an agent connected to Rhino from outside it), ask the same questions in chat, with the same options, and end the turn.
3. **Export** by file path. Build the path from the folder you read this `SKILL.md` from, which belongs to the installed plugin version; never hard-code it or reuse one from an earlier version:

```python
P = "<absolute path of this skill's folder>/scripts/as-batch-image-export.py"
SPEC = {"out": "<folder>", "mode": "Arctic", "size": [3840, 2160], "shots": [{"name": "option-a-birdseye", "direction": "birdseye", "layers": ["Building::Option A"]}]}
exec(compile(open(P).read(), P, "exec"), {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_MODE": "export", "AS_EXPORT": SPEC})
```

4. **Read the result.** A failed batch is not delivered. Fix the cause and run the whole batch again. To check files already on disk, use `"AS_MODE": "verify"` with `{"mode": "Arctic", "files": [...]}`.
5. **Inspect layouts** with `boxMin` and `boxMax` in page units, not `zoom`, which broke the page view, and not `view:`, which can switch the active viewport.

## What the check can and cannot prove

Colour is judged only for modes that must have none (Arctic and Monochrome): a file with colour fails. Any other mode is confirmed by naming it in the capture, reading the viewport's mode back, and the file not being blank; nothing in a PNG proves it was Shaded. The report says which applies.

## Interior views are not supported

`as-batch-image-export.py` frames every shot from outside: it places the camera beyond the bounding box of the shot's layers, looking in along `direction`. No shot can put the camera inside a room. Hiding layers only opens a cutaway seen from outside, which is not an interior view. Leave interiors out of the batch and name them in the report as not exported.

## Lessons

This skill learns locally. Before planning, read its lessons and the firm rules; at the end of every run, write what the run learned. The folder is the one the Arch Studio startup line names; the tags, the privacy rule and promotion are in [lessons](../as-rhino-lessons.md), read once per session.

```python
P = "<absolute path of the skills folder, the parent of this skill's folder>/as-rhino-lessons.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read", "AS_SKILL": "rhino-batch-image-export", "AS_LESSONS_DIR": "<lessons folder from the startup line>"})
```

Follow every firm rule, and name each lesson you apply in the report. To write, use `"AS_MODE": "write"` with `AS_LESSONS`, `AS_PRIVATE` and `__rhino_doc__`, then `"offer"`. Each lesson declares its kind: `practice` (modeling practice) or `preference` (the user's own, with what the user said). Never save a design, architectural or engineering rule you inferred; mention it to the user instead ([lessons](../as-rhino-lessons.md)). A firm rule is written only with `"promote"`, after the user said yes in `ask_user`. Never edit the checker, its tests or answer keys to apply a lesson.

## Report

Open with the `Export:` line exactly as printed. Then each file, the mode, anything moved aside, any requested view not exported, and the lessons applied and written, or "none". Complete under the [completion contract](../../docs/completion-reporting.md).

## Out of scope

Photorealistic rendering, installing display modes, and interior views. For black and white vector sheets use [rhino-thinline](../rhino-thinline/SKILL.md).
