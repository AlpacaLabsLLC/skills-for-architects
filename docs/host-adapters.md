# Host delivery adapters

Domain requirements live in each skill and its host contract. This reference maps them to the
actual delivery surface; it does not grant access, create an assistant, install preferences or
promise that a named command is registered. Check the available host interfaces before selecting a route.

## Installed plugin

Use the exact installed entry point the host exposes, including any plugin namespace it requires.
Command examples in domain instructions name the intended Arch Studio skill; they do not prove that syntax
is registered in the current surface. Natural-language requests may select a skill;
availability and selection must be observed separately. Do not add a second registration merely
because an existing connection or plugin has not refreshed.

Resolve `<skill-root>` from the loaded `SKILL.md` and `<plugin-root>` from the installed package
containing `skills/`, `corpus/`, `schema/`, `tools/` and `studio/`. Resolve relative references against
their owning resource. The installation cache is not a user studio or a canonical output folder.
Preserve the package revision used by active work; after an update/reload, verify changed dependencies
before resuming. A plugin package revision and hosted source digest have independent distribution receipts.

## Hosted MCP

Discover the available `as_*` workflow tool by its task description and declared capability ID.
Use the returned tool/resource URIs rather than constructing an assumed URI from a local path.
Existing tool names remain valid entry points. A returned workflow delivers instructions; it does
not mean the server ran those instructions or can access the host's files.

Read live status and the declared retrieval contract, then pin the returned source digest for the
active workflow. Use the advertised resource/page bounds, follow `next` until complete and stop on
a digest mismatch or missing required resource. A same-version URI alone is not a digest pin.
Use the service's digest-aware bounded tool when ordinary native `resources/read` cannot express
that pin. Instruction page receipts establish only instruction retrieval. MCP workflow execution uses the native host method described by the owning semantic contract; resource text is never an executable installation path.

The capability's `references` are required; `conditionalReferences` state which extra resources to
load for the chosen mode. Dependency IDs remain discoverable component relationships, not authority
to execute an entire chain. Read the complete non-executable specification at the active digest. Follow the
[harness-native execution contract](host-harness-contract.md#harness-native-execution).
A missing local checkout or cached runner is not a requirement for the hosted workflow.

Use resource URIs already returned by the workflow before searching again. Finish any remaining
instruction pages, read required references, and evaluate conditional references against the source
instructions and current task. Follow applicable semantic references and perform the operation through available native host tooling. A listed historical or maintainer script is neither a required workflow resource nor authority to execute it. Native extraction must still meet the owning validation and preservation requirements.

An empty catalog search means the query matched no indexed entries, not that the release has no
resources. Check the service's matching rules, try a short term or exact returned path, or browse
with an empty query at the same digest and follow pagination. If a URI is already known, read it
directly with the pinned resource tool. Before attributing a blocked step to retrieval, retain the
actual query or resource URI, digest, page arguments and returned status in the existing task
evidence; distinguish no match, unavailable tool, missing resource, denied access and hash mismatch.
Do not record credentials or unrelated source content. Preserve partial work and name any required
validation still unperformed; a failed discovery attempt does not waive that requirement.

## Questions, files and optional delegation

Map a skill's requested question or approval to a real question interface exposed by the current
host; if none exists, ask once in plain text. Show the concrete scope/diff before an approval that
is actually needed, preserve existing authorization, and avoid duplicating the question across chat
and a structured surface. A mentioned tool name is not evidence that the host offers it.

Use granted file, PDF, spreadsheet, browser and process capabilities. A connected MCP server does
not imply a local shell, a writable folder, a spreadsheet provider, shared project storage or
credentials. Inspect the selected destination through the host. For a missing capability, preserve
partial results and give the specific handoff; do not fabricate execution or silently create a
substitute canonical record. Supplied-source fetching, discovery search and interactive browsing
remain distinct routes under the user's request.

For a supplied URL or its content, try the host's page-fetch/retrieval capability first. Use search
for discovery; use interactive browsing when the task needs interaction, a configurator or authorized
authentication. A failed shell request is not proof that host fetching failed, and one failed route
does not prove the origin is dead. Preserve original/final URL, actual attempt time, route and evidence;
distinguish not-attempted, proxy/policy rejection, robots/anti-bot blocking, login-required, fetch error
and an observed origin HTTP 404. An unfinished logged attempt is not a completed URL check. Keep the
supplied-link denominator separate from replacement search and do not widen a frozen task's permissions.

Delegate only when the host exposes that capability and the current request permits it. A specialist
receives the same task boundary, sources, unresolved facts and permissions, and refers to the same
domain skill instead of copying its logic. Without delegation, the host may follow the applicable
skill directly. Neither a specialist name nor a workflow handoff creates an independent runtime,
background work, new credentials or additional write authority.

Use the shared [completion report](completion-reporting.md) for source data, instructions,
host operations, outputs, checks, unresolved work and actual canonical writes. A successful retrieval
is not a completed workflow; an export is not adoption. Verify each supported host path separately
and retain existing machine status fields. Include a relevant Norma next action only when it helps the current task; no mandatory footer.
