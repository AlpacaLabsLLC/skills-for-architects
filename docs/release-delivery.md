# Arch Studio release delivery

Arch Studio 1.5.1 targets both the OSS plugin and production MCP, using one versioned shared core and separate channel receipts. Both channels previously published 1.5.0. Prepare and verify each exact candidate, record the publication order, and report a partial release if only one channel succeeds. A candidate version or dated changelog does not establish publication. Historical plans and release evidence remain historical records.

## Identities and ownership

| Identity | Meaning |
|---|---|
| Arch Studio version | Shared skills, knowledge, maintainer helpers and studio contracts |
| Arch Studio source commit and digest | Exact shared content selected for a delivery |
| Channel package digest | Exact private hosted or approved public package bytes |
| MCP service version and build | Hosted implementation, authentication and executable bindings |
| Web release identity | Exact web application paired with the hosted candidate |

The Arch Studio maintainer owns the shared source and channel content review. The hosted maintainer owns service bindings, deployment and client evidence. A release owner verifies the relevant receipts. H1/H2/H3 are capability milestones, not release numbers. MCP 1.0 requires accepted stable service interfaces and operational commitments independently of the Arch Studio version.

## Prepare the shared core

1. Reconcile the selected private source branch and actual remotes; preserve contributor attribution and previous releases. Do not infer public readiness from a private-source commit.
2. Regenerate capability projections from `corpus/components.json`. Run `CI=true ./scripts/lint.sh`, every `tests/test-*.sh` contract and package/export checks with supported runtimes. Record the exact tested commit, failures and skips; a skipped check is not accepted evidence.
3. Preserve source-navigation metadata, Arch Studio-owned procedures, helper imports, schemas and package-relative paths. External reference bodies are not bundled. Review the [host adapters](host-adapters.md), task-first discovery and existing skill names. Record technical shared-core support, channel adapter/service differences, commercial access, licensing and untested behavior separately.
4. Review the final diff, fresh setup instructions and known limitations. Each promotion request must identify a concrete tested candidate and the exact effects. Source validation alone does not authorize deployment, email or public publication.

## Candidate acceptance sequence

Complete all source implementation, current-caller integration, package construction and documentation before actual host acceptance. Ordinary engineering tests run with each slice. Then perform invocation, fresh setup and artifact checks on the selected actual hosts as the final acceptance activity. For 1.5.1, the owner selected Claude MCP desktop, ChatGPT Work in the app and Claude Code with the explicit OSS plugin directory. Windows, ChatGPT browser connection and Codex CLI OSS discovery gaps are disclosed as untested, not passed, and do not block this release. Missing or unsupported routes do not pass; fix material failures before declaring readiness. Retain exact package/source identities and independent review.

The 1.5 series implements forward-only new records and contracts. No 1.4.5 upgrade matrix, old-format converter, compatibility-only alias or historical custom-skill preservation program is required. Operational recovery of a production deployment remains separate from backward-compatible software or workspace conversion.

## Prepare and promote hosted/private 1.5.1

Hosted acceptance uses the exact integrated Arch Studio source. OSS publication is not a prerequisite.

1. Package the selected private source with `docs/`, `corpus/`, `schema/`, `tools/`, `skills/`, `clusters/`, `studio/` and other declared resource roots. Revalidate current references, dotfile templates, full dependency closure and complete bounded resource retrieval. Do not edit generated packaged copies as source.
2. Build and test the service and web candidate. Tie immutable build receipts to the selected Arch Studio content digest and service/web identities. Report the hosted service version separately from the shared Arch Studio version and public plugin release.
3. Verify authentication, native discovery and selection, complete resource retrieval, authorized host execution and actual workflow outcomes independently in each supported client. Test missing host capabilities explicitly; instruction delivery does not complete work. A local test of new content does not verify a live service still serving an older release.
4. Demonstrate refresh, staged content upgrade and rollback. Keep active workflows pinned to the original digest and explicitly select the promoted digest for new work. Record the service/content pair before and after transitions. Restore the prior immutable application/content pair without rewriting user records.
5. Confirm that the owner’s authorization covers production promotion of the reviewed candidate; request approval only if it does not. Then deploy using the hosted controller, and independently read back production identity and authenticated behavior. Retain the prior deployment and recovery receipt.

The hosted pipeline owns exact infrastructure commands and credentials. They are not duplicated into this source runbook. No secrets belong in release evidence. A source-health failure degrades the affected capability; HTTP availability never establishes legal applicability or a valid source edition.

## Prepare and publish OSS 1.5.1

1. Review the exact intended public content, dependencies and licensing. Private evaluation fixtures, client records and service-only material must not enter a public package implicitly. Reuse the approved shared core and review the plugin adapter differences.
2. Verify fresh installation, native discovery, refresh and duplicate-registration behavior on supported plugin hosts, using the new document model directly. The 1.5 series has no historical package/workspace conversion requirement. Keep synthetic fixtures separate from user records. Export checks do not substitute for unperformed host UI checks.
3. Align Claude/Codex plugin manifests, marketplace metadata and release ledger with the approved public version. Consolidate candidate notes into the actual dated changelog at publication; a forecast date is not publication evidence.
4. Confirm that the owner’s authorization covers publication of the exact tested source and notes before merge, push, tag or release; request approval only if it does not. Then follow the accepted repository process, revalidating any changed source. Create the annotated release tag and publish the approved package.
5. Independently verify the tag's peeled source commit, release metadata, package digest and a fresh public installation. A tag object ID is not the source commit. Reject mismatched or unpublished artifacts as release evidence.

## Acceptance boundary

Hosted/private 1.5.1 and OSS 1.5.1 have separate gates and receipts. Earlier-version client evidence must be rerun where content or bindings changed. Unverified clients remain unverified, and unsupported execution is explicit. No shared-team store, synchronization, independent Norma runtime or email authority is implied by this release.
