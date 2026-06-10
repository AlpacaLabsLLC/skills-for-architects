# /project-dossier

Creates and maintains `PROJECT.md` — the project facts file at the project root. Identity, site, zoning, program, and code facts, each entry with a source and date, plus an index of decision records.

## Usage

```
/project-dossier            → status
/project-dossier init       → create, with a short interview
/project-dossier update     → reconcile with new facts from the conversation
```

Facts only. Rationale goes in decision records — see [`/decision`](../decision).

Analysis skills across the marketplace read the dossier before fetching and append findings after completing; this skill owns init, updates, and file hygiene.
