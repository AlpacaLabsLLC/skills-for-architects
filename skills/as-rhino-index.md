# Arch Studio for Rhino: skill index

Load a skill from this index only when the user names it or asks for Arch Studio in Rhino. A plain modeling request that does neither gets no skill.

Each path below is relative to the folder this file is in, which belongs to the installed plugin version. Join it to the folder you read this file from; never reuse a remembered path or one from another version.

To load a skill, read its whole `SKILL.md` with `run_python` (`for line in open(path): print(line.rstrip())`; one very long `print` can be dropped) and follow it. Resolve the links and script paths inside it against that file's own folder. If a Skill tool is available, call the slash name instead. Read the skill again after compaction.

| Skill | Slash name | Path | Use |
|---|---|---|---|
| `as-rhino-model` | `/as:rhino-model` | `rhino-model/SKILL.md` | Plan, build and check architectural models in the open Rhino document |
| `as-rhino-setup` | `/as:rhino-setup` | `rhino-setup/SKILL.md` | Connect and verify Rhino, and name the action needed when something is missing |
| `as-rhino-display` | `/as:rhino-display` | `rhino-display/SKILL.md` | Display modes, views, materials and image exports checked against the requested mode |
| `as-rhino-thinline` | `/as:rhino-thinline` | `rhino-thinline/SKILL.md` | Drawing conventions for black and white vector sheets, with a checked PDF |
| `as-rhino-axon` | `/as:rhino-axon` | `rhino-axon/SKILL.md` | The view for axonometric sheets: camera, cut-away, occlusion, details; loads thinline too |
| `as-rhino-bom` | `/as:rhino-bom` | `rhino-bom/SKILL.md` | Quantities from the model, reconciled to the object count |
| `as-rhino-agent-team` | `/as:rhino-agent-team` | `rhino-agent-team/SKILL.md` | Several agents on one Rhino model: a set-out written first, one file per owner, notes in the model and a check across the files |
