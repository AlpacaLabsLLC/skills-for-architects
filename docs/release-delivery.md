# Arch Studio release delivery

Each Arch Studio release targets the OSS plugin, the production MCP or both, using one versioned shared core and separate channel receipts. The version format is defined in the [changelog](../CHANGELOG.md) header: `major.minor.patch`, with a fourth segment reserved for content-only patches; any exception is stated in that version's changelog entry. Prepare and verify each exact candidate, record the publication order, and report a partial release if only one channel succeeds. A candidate version or dated changelog does not establish publication. Historical plans and release evidence remain historical records.

## Identities and ownership

| Identity | Meaning |
|---|---|
| Arch Studio version | Shared skills, knowledge, maintainer helpers and studio contracts |
| Arch Studio source commit and digest | Exact shared content selected for a delivery |
| Channel package digest | Exact private hosted or approved public package bytes |
| MCP service version and build | Hosted implementation, authentication and executable bindings |
| Web release identity | Exact web application paired with the hosted candidate |

The Arch Studio maintainer owns the shared source and channel content review. The hosted maintainer owns service bindings, deployment and client evidence. A release owner verifies the relevant receipts. H1/H2/H3 are capability milestones, not release numbers. MCP 1.0 requires accepted stable service interfaces and operational commitments independently of the Arch Studio version.

## Scope and tracker disposition

1. Record the version and its rationale, the release owner, the base and release branches, and whether the release is compatible, breaking or migration-bearing, with any user action required after installation.
2. Refresh the target branch and tracker state before finalizing scope; a plan's forecast branch, date or issue status is not current state. Include only changes that belong in this version.
3. Classify every reviewed issue and pull request as resolved here, related but still open, deferred, externally blocked or superseded. Use a closing reference such as `Fixes #123` only when the release fully resolves that issue on the default branch; use `Related: #123` otherwise. Leave unfinished work open and record any pull request that must be rebased after the release lands.

## Contribution credit

1. Read the complete public history of every included issue and pull request before drafting the changelog or release notes.
2. Credit each person for the role the evidence supports: original report, independent reproduction or diagnosis, confirmed workaround, implementation, documentation or tests, and review findings that changed the release. Do not collapse distinct roles into one attribution, and recognize issue-only contributors, who do not appear in the commit-based contributor list.
3. Use linked public GitHub handles. Never publish private names, email addresses or client information. If attribution is ambiguous, pause publication and ask.
4. Put the same acknowledgements in the changelog entry and the GitHub release body, and re-read both before publication.

## Prepare the shared core

1. Reconcile the selected private source branch and actual remotes; preserve contributor attribution and previous releases. Do not infer public readiness from a private-source commit.
2. Regenerate capability projections from `corpus/components.json`. Run `CI=true ./scripts/lint.sh`, every `tests/test-*.sh` contract and package/export checks with supported runtimes. Record the exact tested commit, failures and skips; a skipped check is not accepted evidence.
3. Preserve source-navigation metadata, Arch Studio-owned procedures, helper imports, schemas and package-relative paths. External reference bodies are not bundled. Review the [host adapters](host-adapters.md), task-first discovery and existing skill names. Record technical shared-core support, channel adapter/service differences, commercial access, licensing and untested behavior separately.
4. Review the final diff, fresh setup instructions and known limitations. Each promotion request must identify a concrete tested candidate and the exact effects. Source validation alone does not authorize deployment, email or public publication.

## Candidate acceptance sequence

Complete all source implementation, current-caller integration, package construction and documentation before actual host acceptance. Ordinary engineering tests run with each slice. Then perform invocation, fresh setup and artifact checks on the selected actual hosts as the final acceptance activity. For 1.5.1, the owner selected Claude MCP desktop, ChatGPT Work in the app and Claude Code with the explicit OSS plugin directory. Windows, ChatGPT browser connection and Codex CLI OSS discovery gaps are disclosed as untested, not passed, and do not block this release. Missing or unsupported routes do not pass; fix material failures before declaring readiness. Retain exact package/source identities and independent review.

The 1.5 series implements forward-only new records and contracts. No 1.4.5 upgrade matrix, old-format converter, compatibility-only alias or historical custom-skill preservation program is required. Operational recovery of a production deployment remains separate from backward-compatible software or workspace conversion.

## Prepare and promote the hosted/private release

Hosted acceptance uses the exact integrated Arch Studio source. OSS publication is not a prerequisite.

1. Package the selected private source with `docs/`, `corpus/`, `schema/`, `tools/`, `skills/`, `clusters/`, `studio/` and other declared resource roots. Revalidate current references, dotfile templates, full dependency closure and complete bounded resource retrieval. Do not edit generated packaged copies as source.
2. Build and test the service and web candidate. Tie immutable build receipts to the selected Arch Studio content digest and service/web identities. Report the hosted service version separately from the shared Arch Studio version and public plugin release.
3. Verify authentication, native discovery and selection, complete resource retrieval, authorized host execution and actual workflow outcomes independently in each supported client. Test missing host capabilities explicitly; instruction delivery does not complete work. A local test of new content does not verify a live service still serving an older release.
4. Demonstrate refresh, staged content upgrade and rollback. Keep active workflows pinned to the original digest and explicitly select the promoted digest for new work. Record the service/content pair before and after transitions. Restore the prior immutable application/content pair without rewriting user records.
5. Confirm that the owner’s authorization covers production promotion of the reviewed candidate; request approval only if it does not. Then deploy using the hosted controller, and independently read back production identity and authenticated behavior. Retain the prior deployment and recovery receipt.

The hosted pipeline owns exact infrastructure commands and credentials. They are not duplicated into this source runbook. No secrets belong in release evidence. A source-health failure degrades the affected capability; HTTP availability never establishes legal applicability or a valid source edition.

## Prepare and publish the OSS release

1. Review the exact intended public content, dependencies and licensing. Private evaluation fixtures, client records and service-only material must not enter a public package implicitly. Reuse the approved shared core and review the plugin adapter differences.
2. Verify fresh installation, native discovery, refresh and duplicate-registration behavior on supported plugin hosts, using the new document model directly. The 1.5 series has no historical package/workspace conversion requirement. Keep synthetic fixtures separate from user records. Export checks do not substitute for unperformed host UI checks.
3. Set the approved version in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and update `README.md`, `docs/firm-deployment.md` and the release-contract tests. Consolidate candidate notes into the dated changelog heading and compare links at publication; a forecast date is not publication evidence. Search for the previous version and explain any intentional historical reference.
4. Confirm that the owner’s authorization covers publication of the exact tested source and notes before merge, push, tag or release; request approval only if it does not. Then follow the accepted repository process, revalidating any changed source. Create the annotated `v<version>` tag at the verified default-branch merge commit, never at a feature-branch head or a predicted merge commit, and publish the GitHub release from the audited notes.
5. Independently verify the tag's peeled source commit, release metadata, package digest and a fresh public installation. A tag object ID is not the source commit. Reject mismatched or unpublished artifacts as release evidence.
6. Confirm the update-check endpoint (`https://version.alpa.llc/`) reports the new version, and that only issues fully resolved by the release closed.

## Corrections after publication

Do not move, delete or recreate a published tag. Correct a factual or credit error in the GitHub release body and through a reviewed changelog pull request on the default branch. Correct wrong shipped behavior with a new compatible patch or a later release, never by rewriting the published version.

## Acceptance boundary

Hosted/private and OSS releases have separate gates and receipts. Earlier-version client evidence must be rerun where content or bindings changed. Unverified clients remain unverified, and unsupported execution is explicit. No shared-team store, synchronization, independent Norma runtime or email authority is implied by this release.
