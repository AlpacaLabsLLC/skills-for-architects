# Firm deployment guide

Arch Studio v1.5.1 supplies governed workflows through plugin and hosted instruction delivery. Project records remain local. Assign a technology owner before firm distribution and keep the studio workspace in firm-controlled storage. The [release guide](release-delivery.md) separates candidate, host acceptance and publication.

## Pilot ownership

- Name an owner who approves private studio skills, plugin updates, shared rules, and rollback decisions.
- Test updates in a non-production studio before changing the firm-wide installation.
- Keep firm skills in private source control when they encode confidential procedures. Contribute upstream only after removing client, project, credential, and proprietary content.
- Document the supported host, Codex or Claude Code version, operating systems, and local dependencies used by the pilot. Repository tests do not establish parity for every host surface or operating system.

## Records and collaboration

- Treat `STUDIO.md`, each `PROJECT.md`, and canonical task or time registers as one-writer records. Do not have two agent sessions edit the same canonical record concurrently.
- Document operations check expected local revisions and preserve recoverable write state for cooperating writers. Network and synchronized folders retain their provider's conflict, sharing, retention and recovery behavior; these checks are not distributed locking or automatic conflict resolution.
- Back up the studio before structural changes. Recovery means restoring user-owned files through the firm's backup or source-control process; plugin reinstall does not restore records.
- Restrict filesystem access to the people and systems authorized for the underlying projects.

## Data, secrets, and incidents

- Apply the firm's active OpenAI or Anthropic account, retention, and administrator controls to prompts and files. See [data governance](./data-governance.md).
- Keep credentials out of Markdown, CSV, skill bodies, and source control. Connector authentication is administered separately; the empty studio `.mcp.json` does not configure a provider.
- Define retention and deletion rules for studio records, generated outputs, logs, and backups before the pilot.
- For accidental disclosure, compromised credentials, or incorrect regulated output, stop the affected workflow, preserve relevant local evidence, rotate credentials where applicable, and follow the firm's incident and professional-review procedures. ALPA does not receive or administer the firm's project records.

## Distribution, rollback, and support

Distribute approved plugin releases through the documented marketplace. Hosted MCP workflows are harness-native: the connected host performs them with its own tools and needs no local Arch Studio package, runner or installer. The [managed package installer](../tools/runner/README.md) applies only to the OSS plugin's retained local operations; a pilot that uses it records the package digest and tested host route. Distribute private firm skills through firm-controlled tooling into the relevant host skill root. The 1.5 series uses fresh new-model setup; there is no historical register converter. Retain user-file backups independently of package versions; selecting another package never restores or downgrades records.

Arch Studio issues belong in `$studio-feedback` on Codex or `/as:studio-feedback` on Claude Code after the outbound fields are reviewed. Account, billing, model, and retention questions belong with OpenAI or Anthropic and the firm's host administrator. Storage, sync, access, and backup incidents belong with the firm's provider and internal owners.
