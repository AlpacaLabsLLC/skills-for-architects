# Project context resolution

`context.resolve` is semantic work performed with native host reads; no installed package or
process is required. Follow the [workspace model](../../../docs/workspace-model.md) for identities,
registry columns and task ownership, and the [host contract](../../../docs/host-harness-contract.md)
for target access and source authority. This procedure reads only; it never creates or repairs context.

## Resolve the boundary

1. Start at the explicitly selected path, otherwise the actual current directory. For a file, use
   its containing directory. Resolve native system path aliases to the physical location, but reject
   symlinked project/studio roots, identity files and owned targets. Keep all selected paths within
   their authorized physical boundary.
2. Walk ancestors to the nearest PROJECT.md and separately the nearest STUDIO.md. PROJECT.md is the
   only implicit project marker; git roots, task files and folder names establish no project identity.
   An encountered malformed manifest is invalid, not absent; do not skip it to choose another project.
3. For a project, read identity fields from PROJECT.md and .as-folder.json. Require Format version 3,
   Document model 1, nonempty Project ID/Project/Kind/Type/Status, Type internal or client, and folder
   identity containing exactly format 1, kind project and a canonical `asf_` UUID. Never synthesize a
   missing identity. A valid standalone project has no studio and owns its local TASKS.csv.
4. For an owning studio, read STUDIO.md, its identity and the one bounded projects table between
   projects:start/end markers. Require the declared format/model, exact registry columns, unique
   project IDs and folder IDs, and Task register equal to project or portfolio. Resolve each
   registration by immutable Folder ID to exactly one safe physical descendant project; the cached
   Folder path is a convenience, not authority to replace the identity. Search only within the
   authorized studio boundary without following symlinks. Compare Project ID/Folder ID and the
   registered Project, Client, Type, Kind and Status with the project manifest. A readable-path drift
   with the same unique identity is a diagnostic; missing/duplicate identity or metadata mismatch is
   invalid. Invalid registrations remain visible as diagnostics, never valid selectable projects.
5. A selected project inside a studio must match exactly one valid registration. In project mode
   return its local TASKS.csv; in portfolio mode return the studio TASKS.csv and exact project filter.
   These writers are mutually exclusive. Type, Kind and Status are advisory; they do not hide a valid
   registration. Missing/malformed task registers are separate explicit errors, not empty lists.

## Result and continuation

- **project:** retain project_root, project_id, advisory kind/project_type/status, studio_root
  (null for standalone), task_mode and canonical task_register. Use that exact owner.
- **studio-picker:** no selected project; show valid registered choices and invalid diagnostics.
  Ask only for the missing project selection. All-invalid rows are not an empty studio.
- **no-projects:** the bounded registry is actually empty; creation can be offered, never inferred.
- **no-context:** no project/studio marker. For durable work, consult a canonical studio registry
  already specified by the user's host instructions and bind only on a reliable match; otherwise
  ask one project/studio selection question. One-off tasks need no manufactured context.
- **invalid / unavailable:** report the specific manifest, identity, boundary or access failure and
  preserve input. Permission denial is not evidence that a project does not exist.

Read the selected owning AGENTS.md/PROJECT.md and applicable studio settings before durable work.
Use available native reads and retained file paths/hashes or revisions as evidence; a typed result
is an observation summary, not a self-certified access grant. Recheck relevant identity and current
register state before a mutation. This supports the current record model only; no old-format
conversion or implicit project registration is performed.

A locally stored user reference is not proof of currency or applicability and cannot become copied
reference content in the plugin package. Keep project outputs in the owning project; use the
receive-owned semantic document rules for placement and ID-based lookup.
