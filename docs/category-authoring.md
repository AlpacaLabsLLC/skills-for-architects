# Five-category authoring contract

| Category | Canonical owner | Contribution |
|---|---|---|
| Knowledge | `corpus/` | Original shared concepts/methods or explicit source metadata |
| Tools | `tools/` | Executable implementation with declared execution route |
| Skills | `skills/<name>/` | Flat public procedure; private assets may remain here |
| Practice Clusters | `clusters/*.json` | Maintained references to components, coverage and evaluations |
| Studio | `studio/` | Distributed workspace contracts/templates; never user records |

`corpus/components.json` maps stable `skill:`, `knowledge:`, `tool:` and `studio:`
IDs to a single canonical file, owner, execution class and dependencies. Directory
names are not public command names. IDs persist through coordinated path moves.
The inventory covers public procedures and extracted shared components; a skill's
private scripts/templates remain owned by that skill rather than duplicated here.

Nine [practice manifests](practice-clusters.md) assemble these components. New
practice areas add a manifest and any genuinely new components. Geographic coverage
is explicit metadata, independent of practice membership. `jurisdiction:` IDs refer
to the source registry, not parent-folder inference. Coverage booleans distinguish
indexed sources, available procedures, implemented execution and validated workflows.
A contract test cannot establish end-to-end workflow validation. Current cluster
manifests deliberately make no cluster-wide execution/workflow validation claim.

Shared professional-practice knowledge was extracted intact; old skill references
are Markdown forwarding links which readers must follow. Shared namespace validation
has one implementation under `tools/validators/`; its old script delegates to it.
Studio scaffold templates, including hidden `.mcp.json`, have one owner under
`studio/templates/studio/`. The studio workspace helper reads that canonical path.
Private record templates and shell helpers retain established ownership and paths.

Run `python3 tools/validators/validate-categories.py --write-guide` after manifest
edits and `--check-guide` in validation. Run `bash tests/test-category-contracts.sh`
for negative schema/reference/cycle fixtures and an external package copy.

Package all canonical assets and forwarding targets in both OSS and MCP. Hosted
projection must index the category roots and preserve complete linked bytes; a
successful instruction download does not execute a workflow. Registry execution
classes describe the implementation, not the existence of a hosted binding.
A client still needs supported capabilities and authorization for record mutations.
