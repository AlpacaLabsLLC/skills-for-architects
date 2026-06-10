# /decision

Captures project decisions as ADR-style records — `decisions/NNNN-slug.md` at the project root. Context, options considered, the call, consequences, and a status (`proposed` / `decided` / `superseded`). Every record is indexed in `PROJECT.md`.

## Usage

```
/decision                          → interview, then record
/decision we're going with X       → record, asking only for gaps
/decision supersede 0003           → replace an earlier decision, keep the trail
/decision list                     → index with statuses
```

Numbers are permanent; wrong decisions get superseded, never deleted. One decision per record. Facts live in [`/project-dossier`](../project-dossier); this skill records the reasoning.
