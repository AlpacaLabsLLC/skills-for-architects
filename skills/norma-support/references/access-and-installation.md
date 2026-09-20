# Access, installation and memory

## Connection questions

Use the actual host name, observed entry points and current Arch Studio release status. Follow [host delivery](../../../docs/host-adapters.md) and [release delivery](../../../docs/release-delivery.md) for the applicable route. Public plugin, hosted MCP, local helper package and managed support environment have distinct installation/verification receipts. The same visible version does not establish identical source bytes.

If Arch Studio is absent from the callable inventory, explain how that differs from an authentication error. Discover the installed connection before recommending remount/restart; do not repeatedly uninstall a working connection. Use the current maintained installation instructions or the authenticated release artifact offered by the active service. Do not invent a public ZIP, package-manager command, OAuth client ID or credential. Never request a secret key or bearer token in chat/email.

For `invalid_scope`, capture the named scope, actual issuer/environment and registered client through safe metadata. A missing allowed scope is a client/provider configuration issue; making organization membership optional is not the fix. Scope configuration is handled by the account administrator through the applicable provider UI, not by inventing a custom scope or silently dropping the requested firm scope. Do not expose authorization codes, state values or credential-bearing callback URLs in persisted evidence.

## Known connection issues — checked September 15, 2026 (UTC)

The maintained public issue record is [Known issues](https://architecturestudio.ai/docs/known-issues). This bundled snapshot lets conversational email support explain the verified workaround without web access. Cite the issue ID and checked date; do not claim to have fetched a newer status or that publication, a provider fix, or a user's recovery has occurred without evidence. Review this snapshot whenever the public issue changes.

### KI-001: invalid_scope for user:org:read

Status: provider scope fix verified September 15, 2026 at 01:32 UTC. The automatic Codex client previously rejected `user:org:read`; its missing allowed scope has now been corrected in production. Fresh authorization, two rotating refresh-token exchanges and three authenticated Arch Studio status calls passed with organization context preserved. No MCP redeploy was required. Native recovery after natural expiry/restart remains under investigation in KI-002. The affected path is hosted MCP through local Codex configuration, including desktop sessions that use it. A standalone local plugin does not use this OAuth connection. This failure has not been reproduced on Claude. Hosted ChatGPT web uses a different registration/callback; the local workaround below is not a hosted web configuration.

Before giving commands, establish the user's host/surface, MCP versus plugin, sanitized error, production endpoint, and existing local server name. An enabled connection with unavailable tools can be consistent with failed authorization, but is not enough by itself to diagnose this issue. Website sign-in, repeated restarts or reinstalling do not fix the provider's missing scope permission.

First recommend retrying normal authorization once, selecting the intended firm, and asking the assistant to call `as_status`. Do not require a new manual client override for every user. A working explicit-client connection can stay configured. If the exact local scope failure persists, offer the fallback below and collect sanitized details for support.

For this exact local production fallback, the reviewed public OAuth client is `KwcbrbiJQb5xQEyw`; it requires no client secret. Explain how to back up and merge the following into the existing Codex configuration, normally `~/.codex/config.toml`. Do not replace the whole file, create duplicate TOML sections, or invent an alternate callback. If the server has another name, substitute that same existing name in both table headers and in the login command.

```toml
[mcp_servers.arch_studio]
enabled = true
url = "https://mcp.architecturestudio.ai"

[mcp_servers.arch_studio.oauth]
client_id = "KwcbrbiJQb5xQEyw"
callback_url = "http://127.0.0.1:58687/callback"
callback_port = 58687
```

Port 58687 must be available. If occupied or unsupported by the user's host, stop and escalate rather than selecting an unregistered callback. Have the user run:

```sh
codex mcp login arch_studio --scopes openid,profile,email,offline_access,user:org:read
```

The user completes sign-in and selects the intended firm, reopens the affected app/session, and asks it to call `as_status`. Recovery requires an actual status result, not merely an enabled setting or website sign-in. Email Norma cannot edit files, complete sign-in, inspect credentials, or verify a live connection on the user's behalf.

Evidence: this configuration recovered an affected native connection, and its Arch Studio status call passed. A separate test-account grant passed sign-in, two consecutive renewals and three authenticated status calls with organization context. The automatic client now passes the same protocol checks after the provider correction. Clean native installation, renewal after natural expiry/restart, and hosted ChatGPT web remain unverified. Do not promise that existing expired credentials repair themselves; one new authorization may still be required.

### KI-002: invalid_grant on renewal

Status: investigating. An observed desktop credential failed renewal after access-token expiry with `invalid_grant` / refresh token malformed or not valid, then omitted Arch Studio tools. The cause of the old refresh token's invalidation is unknown. Fresh registered-client and corrected automatic-client grants each renewed twice, which does not prove native storage/rotation or future expiry recovery.

Recommend one normal host reconnect/authorization attempt. For local Codex, `codex mcp login` uses the existing server name. If this returns the exact scope rejection above, route to KI-001. Hosted ChatGPT uses its own reconnect controls. If the failure returns, collect only host/version, approximate failure time and sanitized error for escalation. Do not repeatedly reinstall, delete credential stores, drop the firm scope, loosen organization requirements, or ask for tokens, secrets, codes, state values or full callback URLs.

### KI-003: missing Norma welcome after signup

Status: personal-email pilot verified September 15, 2026 (UTC). The repaired runtime delivered a personal account's welcome and answered its authenticated reply in the same Gmail thread. Durable records show one completed welcome job and one completed reply job, with one accepted message for each. This verifies the personal pilot, not delivery to every customer. This release enables accounts with a verified email and current membership in their intended firm. The runtime rollout policy is separate: use current authorized account context rather than inferring live eligibility from this snapshot.

The former email runtime restricted recipients to an internal owner pilot. Separately, a malformed SQL alias interrupted internal signup notification receipts before provider sending; operator notices and Norma welcomes are different paths. Do not give users private operator addresses or suggest changing their own environment variables.

Hosted email eligibility requires a verified account email and current firm membership. Personal email domains are eligible under the same membership rule; they are not an exclusion by themselves. A signup candidate can wait for delayed membership. For multiple memberships, the user must choose the intended firm; do not choose arbitrarily or create a firm for them. Follow the existing account create/join flow, and never claim every signup automatically creates a firm.

The accompanying web release provides **Start with Norma** at `/profile/firm`. Have the user select the intended firm and use this action once when it is available. It releases only an existing waiting welcome candidate after a fresh account and membership check. It does not enroll an old account, create a second welcome, or authorize an email conversation. A queued result means scheduled, not delivered. If the result says no new welcome was scheduled, continue an existing Norma thread or contact support; do not promise a resend.

If sign-in is pending on required firm selection and the card is blank or stuck, the accompanying web recovery offers **Restart sign-in**. When visible, this action ends only that pending session and returns to sign-in with the intended destination preserved, so the user can choose their firm again. It does not remove the account or membership, and is not a claim that the underlying blank-card cause has been fixed. If the recovery control is unavailable or the problem returns, collect the approximate time and sanitized screen/error for support. Do not advise deleting the account or weakening the firm requirement.

Ask the user to check spam for norma@architecturestudio.ai and finish email verification and firm selection. If no welcome arrives, contact support with approximate signup time and KI-003. Do not recommend duplicate accounts, repeat signups or repeated resends. Missing welcome alone does not diagnose MCP OAuth failure; installation and host authorization can continue independently.

A reply authenticated by the application through aligned sending-service signatures can continue without a separate sign-in confirmation. The verified personal Gmail pilot used this path and created no separate conversation grant. When additional account verification is needed, the application issues the appropriate sign-in challenge; use that actual handoff rather than inventing one. Receiving a welcome alone never grants ongoing conversation authority. Sender, current verified account and firm, thread routing and suppression checks remain required for each reply.

Only an operator with appropriate access can distinguish ineligible, waiting for membership, suppressed, queued, provider-accepted, delivered and rejected states. Do not assert inbox delivery from an HTTP success or provider acceptance. Recovery must preserve original event/job identities and deduplication, suppression and account-deletion protections. The broader rollout does not bulk-resend historical welcomes or reset the original activation cutoff. Any missed-welcome recovery must be a reviewed bounded set of existing candidates. Update the rollout status only from publication and delivery evidence.

## Runner questions

Inspect the actual workflow's delivered execution model and release identity. A harness-native MCP workflow supplies complete semantic instructions for the user's authorized host tools; operation identifiers describe scope and do not require dispatch through an Arch Studio executable. Assess the concrete required capability (for example, preserving workbook formulas or publishing a complete file safely), then verify actual results. Do not infer access or completion from status or instruction retrieval, or propose an Arch Studio runner, bridge, script download or reconstructed helper when a capability is missing. Keep unsupported work incomplete and explain the precise requirement.

An older delivered release may still prescribe a packaged operation whose local runner is unavailable. That is a release dependency issue; preserve successful work and report the missing step without certifying it. Do not claim a private harness-native candidate has repaired production or the public OSS release. Hosted MCP and OSS selection have separate release evidence; no signup-flow change or executable installation is implied by the native architecture.

The September 13 R4 publication included a private local archive used in bounded Mac tests; it did not establish a public hosted installer download, desktop/Windows execution or every failure-recovery route. Treat these as historical release limitations until a newer installation receipt proves the relevant path. Do not recommend an evidence-only archive as a public acquisition URL.

## Memory questions

Native Norma uses context supplied by the current host and explicitly accessible records. Managed email Norma uses authorized case messages and confirmed support facts. Arch Studio does not automatically synchronize all ChatGPT/Claude conversations or local files. Membership in the same firm does not automatically grant access to another user's support case.

The conversational CSM service retains messages and confirmed context for the active account's lifetime, subject to authorized deletion. Active means account lifecycle, not recent use or an open case. Email support does not ingest or process attachments. It can recall confirmed text facts, but cannot reconstruct file bytes. Do not claim instantaneous deletion from provider backups. These are service obligations, not retention settings this skill can enforce on the user's host.

## Maintained installation routes

The Arch Studio-owned installation guide is [architecturestudio.ai/docs/install](https://architecturestudio.ai/docs/install). Select the user's actual host, app or CLI surface, and MCP or local-plugin method. Direct routes: [Claude app MCP](https://architecturestudio.ai/docs/install?host=claude&surface=app&method=mcp), [ChatGPT app MCP](https://architecturestudio.ai/docs/install?host=chatgpt&surface=app&method=mcp), and [distribution comparison](https://architecturestudio.ai/docs/compare).

The production hosted MCP endpoint is `https://mcp.architecturestudio.ai/`. Use the current guide's normal OAuth connection flow and required firm selection; do not reuse historical staging client IDs. Account sign-in alone is not assistant authorization. Custom connections depend on the user's host version, plan and administrator settings. The local plugin uses the [maintained public repository instructions](https://github.com/AlpacaLabsLLC/skills-for-architects#readme); an Arch Studio account is not required to use that local plugin. This does not waive firm membership for protected email cases or hosted access.

These Arch Studio-owned routes are release guidance, not a promise that the support service can install anything. When the user cannot follow a step, ask for its label or sanitized error and the host/surface. The email service cannot browse a new UI to verify changed controls. Do not invent a menu path or claim a new release is installed without the corresponding status receipt.
