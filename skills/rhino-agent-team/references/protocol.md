# Protocol: files, layers and notes

Read when writing the set-out or when a helper refuses. Every name below is what `scripts/as-agent-team.py` reads and writes; the team check depends on them.

## Folder

One folder every agent can reach, holding:

- `setout.3dm`, written only by the coordinator.
- One `.3dm` per owner, named in the set-out.
- `reports/round-<n>.json`, the coordinator's team check for each round.

## Set-out file

- **`Setout::Data`:** exactly one object (a point at the origin is enough) with a user string `data` holding JSON, written with `write_setout(...)` and reissued with `issue(...)`:

```json
{"revision": 1,
 "change": null,
 "owners": [{"name": "Mechanical", "file": "mechanical.3dm"}, {"name": "Plumbing", "file": "plumbing.3dm"}],
 "host": "Shell",
 "shared_spaces": [{"name": "Shaft", "box": [100, 250, 0, 124, 290, 520], "owners": ["Mechanical", "Plumbing"]}],
 "datum": {"origin": [0, 0, 0], "x": "across the house, party wall to party wall", "units": "Inches"},
 "levels": [{"name": "Cellar", "z": 0}, {"name": "F1", "z": 108}],
 "priority": ["Plumbing drains", "Mechanical ducts", "Plumbing supply", "Electrical"],
 "min_sizes": {"Mechanical::Supply": 6, "Plumbing::Drain": 3},
 "numbers": {"joist_depth_in": 10}}
```

  - `revision` goes up by one on every change, and `change` says in plain words what changed and why ("a post now takes 8 in off the shaft's east side; mechanical's share moves west"). `issue()` keeps earlier ones in `history`.
  - `levels` is a list of `{"name", "z"}`, one per floor of the host, at the floor's top; `levels_from()` reads them off the host and `write_setout()` refuses anything else (a dict is converted). Ceilings go in `numbers`.
  - `shared_spaces` lists every space more than one owner needs: `{"name", "box", "owners"}`, the owners being every one whose runs pass through it. `check_setout()` refuses the set-out while any listed owner has no share inside its space.
  - `owner_digests` and `revision_rounds` are written by `issue()`: what each owner built to in each revision (its shares, points, levels and datum) and the round each revision was issued. The team check uses them so a reissue makes stale only the owners it touched, and so it can tell when a stale item has waited a round.
  - `host_file` (optional): the host's file in the shared folder when the host is not an owner. The set-out checks read it as last saved; without it, they use the one `.3dm` in the folder that is neither the set-out nor an owner file, if there is exactly one.
  - `host` is optional: the owner whose elements others pass through, and who answers opening requests. Its file may be one no agent writes (a given shell): mark that owner `"given": true` in `owners`. The team check then still measures its geometry (clashes, crossings, openings) but does not expect a revision stamp, an own check or a version stamp from it.
  - `min_sizes` gives the smallest cross-section per system layer. The team check does not measure sizes; each owner writes them into its own requirements (rhino-model).
  - The priority order is the user's preference, not a rule this skill supplies. It decides only what the shares do not.

- **`Setout::Points`:** one point per required point, with user strings `owner`, `system` and `role` (`source` where a system starts, `point` where it must reach) and the object name as its label.
- **`Share::<Owner>`:** closed boxes, one per share, with user strings `owner`, `zone` (a unique name), `by` and `round`, written with `share(...)`. A shaft or opening that several owners use is divided into one share per owner. Shares of two owners must not overlap.

## Owner file

- Every object of an owner sits under the owner's parent layer, which is also its rhino-model parent layer: `Plumbing::Drain`, `Plumbing::Supply`. A system's runs go on `<Owner>::<System>`, which is how the team check follows a run back to its source.
- The document string `setout_revision` records the set-out revision the file is built to (`stamp()`), and rhino-model's own check stores its result in `as:requirements-check`; the team check reads both.
- **Opening requests:** boxes on `Interface::Penetrations` just around a run where it crosses the host's elements, with user strings `from`, `through` and `setout_revision`.
- **Openings (host only):** boxes on `<Host>::Openings`, each covering a current request, stamped with `setout_revision`.

## Notes

A text dot on the `Notes` layer, placed where the issue is, with user strings:

| Key | Values |
|---|---|
| `note_id` | short unique id |
| `from`, `to` | owner names, `coordinator` or `everyone` |
| `kind` | `issue` (a problem with someone's objects, to the owner of the object that must change), `request` (an open design value, to the coordinator), `change` (a change order, to the coordinator), `reply`, or `ruling` (coordinator only) |
| `status` | `open`, `answered` (a reply) or `closed` |
| `round` | the round it was written in |
| `reply_to` | on a reply, the id it answers |
| `issue_kind`, `object` | on an issue note: which of the team check's lists it is about (`clash`, `through_shell`, `unserved`, `undersize`, `reservation`, `note`) and the object, point or note id |

A note lives in the file of the agent who wrote it, so only its author closes it. The team check lists every open issue, request, change and ruling by addressee, and flags to the coordinator any note other than one addressed to it that has had no reply for a round or more after the round it was written in. An owner's open design values go to `coordinator`, never to the user.

## Reading others

`others(owner)` reads the other files with `Rhino.FileIO.File3dm`, as last saved, without opening them as documents. The measured runs read them as linked blocks instead; both give the file as last saved, but this way has not itself been run in a test.
