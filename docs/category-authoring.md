# Component authoring contract

The [four architectural layers](architecture.md) assign responsibility. The existing
five component categories below organize discovery and packaging; they are not five
competing layers or a requirement to move files.

| Category | Canonical owner | Contribution |
|---|---|---|
| Knowledge | `corpus/` | External original-source navigation and geographic metadata |
| Tools | `tools/` | Executable implementation with declared execution route |
| Skills | `skills/<name>/` | Flat public procedure; private assets may remain here |
| Practice Clusters | `clusters/*.json` | Maintained references to components, coverage and evaluations |
| Studio | `studio/` | Distributed workspace contracts/templates; never user records |

`corpus/components.json` maps stable `skill:`, `knowledge:`, `tool:` and `studio:`
IDs to a single canonical file, owner, execution class and dependencies. Directory
names are not public command names. IDs persist through coordinated path moves.
The inventory covers public procedures and extracted shared components; a skill's
private scripts/templates remain owned by that skill rather than duplicated here.

## Capability discovery

Critical skill components may declare optional `capability` metadata in the
existing registry. `description` is task-first and becomes the plugin frontmatter
description. `triggers`, `exclusions`, `inputs` and `outputs` explain selection and
scope; they do not copy the procedure. `references` lists always-required package
files. `conditionalReferences` pairs an additional `path` with the mode in `when`.
Declare the native semantic contracts and schemas a skill needs; workflows perform them with
the host's own tools and never retrieve or reconstruct executable source.
Keep component `dependencies` for component relationships; a file path is not a new
component registration merely because several skills consume it.

`hostContract` points to the existing adjacent declaration cataloged in
`corpus/host-contracts.json`. `executionOwner` is `host` for instruction delivery;
server execution requires an actual server binding. `handoffs` name existing skill
IDs and their conditions. A handoff never grants permission or runs an automatic
chain. All critical skill bodies refer to the shared [host adapters](host-adapters.md)
for invocation, questions, file access and optional delegation.
Every declared critical capability also requires the shared [completion report](completion-reporting.md),
so complete retrieval includes the distinction between delivered instructions and verified work.

Run `python3 tools/validators/capabilities.py --write` after changing definitions,
and `--check` during validation. The generated `corpus/capabilities.json`,
`docs/capabilities.md` and frontmatter descriptions are projections, not parallel
authorities. The generator preserves instruction bodies. Missing, unsafe, duplicate
and stale references or projections fail validation. Native registration, discovery,
selection, complete retrieval, execution and completion need separate host evidence;
an exported package alone does not establish them.

## Practice composition

Nine [practice manifests](practice-clusters.md) assemble these components. New
practice areas add a manifest and any genuinely new components. Geographic coverage
is explicit metadata, independent of practice membership. `jurisdiction:` IDs refer
to the source registry, not parent-folder inference. Coverage booleans distinguish
indexed sources, available procedures, implemented execution and validated workflows.
A contract test cannot establish end-to-end workflow validation. Current cluster
manifests deliberately make no cluster-wide execution/workflow validation claim.

Professional-practice and regulatory interpretation uses external originals reached
through `corpus/sources/catalog.json`; local summaries and forwarding stubs are not
another reference authority. Shared namespace validation has one implementation
under `tools/validators/`; the repository script remains a current engineering caller.
Studio scaffold templates, including hidden `.mcp.json`, have one owner under
`studio/templates/studio/`. Fresh setup uses the shared document/workspace operations.
Arch Studio-owned schemas, templates and procedures stay with their useful owners.

Run `python3 tools/validators/validate-categories.py --write-guide` after manifest
edits and `--check-guide` in validation. Run `bash tests/test-category-contracts.sh`
for negative schema/reference/cycle fixtures and an external package copy.

Package all canonical assets and required imports in both OSS and MCP. Hosted
projection must index the category roots and preserve complete linked bytes; a
successful instruction download does not execute a workflow. Registry execution
classes describe the implementation, not the existence of a hosted binding.
A client still needs supported capabilities and authorization for record mutations.
