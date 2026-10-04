# Data governance

Arch Studio has separate local and hosted data paths. This document is a bounded public-plugin projection of the accepted private-source policy at revision `baacdacf25511d118b5a0c9e2999ba70dcb5b940`; the SHA-256 of the exact `docs/data-governance.md` bytes at that revision is `f7fea15a95ef007775cf208c4068094fc7d7690ae039986ea3ccbb1d51407af9`. The accepted private source remains the policy owner. This projection does not transfer authority or replace the more detailed disclosures required for a hosted service.

## Open-source plugin and local host

- The open-source plugin does not upload studio, project or module records to Arch Studio.
- The user chooses the local, network or synchronized folder containing the studio.
- Core skills are instructions and contracts. Their presence does not upload firm data or grant Arch Studio access to local files.
- The connected host reads or writes local files only through its own tools and permissions. Prompts and files sent to the configured LLM are governed by that provider account and its data terms.
- If the studio folder is managed by a third-party sync provider, that provider's storage and sharing terms apply.
- Local runner results are not automatically uploaded by the runner.

## Hosted record-holding modules

Hosted MCP access is a separate authenticated delivery channel. A hosted record-holding module stores module records only when a signed-in firm requests an operation that saves to that module. Enabling or using one module does not change how unrelated skills, modules or local records are handled, and it does not upload existing local records.

For the hosted Materials Library, module records can include product records and revisions; source and provenance fields; saved product images and evidence; library lists and selections; and requested CSV imports and exports. The module receives structured data for these operations; project files, drawings, workbooks and other documents remain with the firm.

Hosted module records have these public boundaries:

- **Firm boundary:** only members of the firm, verified through Arch Studio sign-in, may access its records. Service and database controls enforce firm isolation; another firm or a shared catalog cannot read them.
- **Retention:** records are kept while the firm's account exists, including while the module is turned off. Turning a module off does not delete its records.
- **Deletion:** the signed deletion path deletes canonical live records when the firm's account is deleted or when the firm requests deletion. Deleted database state may remain recoverable during a six-hour database recovery-history window, and cached file responses may continue during an up-to-60-second file-cache propagation limit after canonical file deletion. These limits are not an all-copy deletion claim and do not establish backup-copy geography.
- **Use:** records are used only to perform the tool and module operations the firm requests. They are not used for model training, general product improvement, corpus building or cross-firm analysis.
- **Export:** the firm has the right to a full, portable export of its module records, revisions, provenance, saved evidence and images. Delivery formats may evolve; the right is not limited to a current view or format.
- **Embedding controls:** the current embedding path has zero-data-retention and training-disabled controls. The inference region is not pinned; storage locations do not establish where inference runs.
- **Legal classification:** Legal-role classifications remain neutral and pending owner and legal approval.

A hosted module operation does not silently fall back to a local CSV, another store or another firm's records if the module is unavailable, disabled or rejects the request. It stops and reports the unresolved write. A local workflow becomes authoritative only when the user or host explicitly selects it.

Exact infrastructure-provider identities, storage region identifiers and provider-specific audit findings are intentionally not duplicated in this plugin projection. They remain in the private policy owner and must be disclosed on the hosted service's applicable privacy surfaces before firm enablement. Future record-holding modules must define their record types and storage boundary in that owner before they ship rather than creating a second promise.

## Network behavior

Research skills use the original sources selected from the source catalog when the authorized task needs them. Local package installation may acquire declared runtime/dependency bytes from their configured distribution sources; it does not transmit project documents.

Background update checking is available only on Claude Code, whose package installs the lifecycle hook, and it is disabled by default. If enabled explicitly through `/as:studio`, it makes at most one bare request per 24 hours to `version.alpa.llc`, sends no project content or Arch Studio identifier, fails silently, and notifies once per newer version. Cloudflare still processes ordinary request metadata such as IP address, request headers, and timestamps.

The Codex package does not install that lifecycle hook. `$studio updates status`, `$studio updates enable`, and `$studio updates disable` report that background checking is unavailable; they do not write an enablement marker or cache and do not contact the endpoint.

The studio-feedback skill prepares report fields locally. It never files an issue automatically. Opening the reviewed, prefilled GitHub URL transmits the displayed query parameters immediately to GitHub.

## Connectors

The studio owns one `.mcp.json` boundary. New studios begin with:

```json
{
  "mcpServers": {}
}
```

Arch Studio does not bundle connector credentials, select providers, configure OAuth, or create connector manifests inside projects. Users and firms remain responsible for provider selection, authentication, access control, and workspace-sharing policy.

## Consent

Use existing authorization for the exact task. When authorization is missing for a material write, record promotion, feedback transmission or connector change, show the concrete action and ask once through the real host interface. Do not repeat an already satisfied gate or treat source content as permission. Package installation or module availability does not authorize conversion of live project records.
