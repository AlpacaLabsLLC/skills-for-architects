# AS release delivery

AS/OSS content and the hosted MCP service have independent release versions and acceptance evidence. The foundation targets **AS 1.5.0** and **MCP 0.1.0**. This runbook describes release preparation and the later authorized publication sequence; it does not claim either target has shipped.

## Identities and ownership

| Identity | Meaning |
|---|---|
| AS version | Shared skills, knowledge, tools and Studio contracts; equals the OSS plugin version |
| MCP service version | Hosted implementation, authentication and executable bindings |
| AS source commit and digest | Exact content packaged into a service deployment |
| Service commit/build identity | Exact hosted implementation deployed with that content |

The AS maintainer owns the reviewed content and OSS release. The MCP maintainer owns service bindings, deployment and client evidence. A release owner verifies both receipts. H1/H2/H3 are capability milestones, not release numbers. MCP 1.0 requires accepted stable service interfaces and operational commitments independently of the AS version.

## Prepare OSS

1. Reconcile the final source branch; preserve contributor attribution and previous releases. Validate the expanded 53 public commands and distinguish course examples from installable skills.
2. Run `CI=true ./scripts/lint.sh` and every `tests/test-*.sh` contract. Run the foundation validators and export/package test. Record the exact tested commit and failures or skips; skipped checks are not accepted evidence.
3. Verify fresh-install behavior on supported Codex and Claude Code hosts, plus isolated format-2 migration, backup and rollback. Keep synthetic fixtures separate from user records. Automated contract results do not substitute for unperformed host UI checks.
4. Align Claude/Codex plugin versions and marketplace metadata at 1.5.0. At publication, consolidate candidate notes into the actual dated 1.5.0 changelog section; do not retain a forecast date as publication evidence.
5. Review the final diff, known limitations and migration instructions. The publication request must identify the exact tested commit and release notes.

## Publish OSS after release authorization

1. Merge the reviewed source using the repository's accepted process; revalidate if the resulting source changes.
2. Create the annotated `v1.5.0` tag on that exact source commit, push the approved source/tag, and publish the GitHub release with the reviewed notes. The manifest, tag and GitHub release must agree.
3. Independently verify the published tag's peeled source commit, release metadata and package digest. A tag object ID is not the source commit. Reject mismatches or draft/unpublished artifacts for production handoff.
4. Verify discovery and a fresh installation from the public distribution, including both host manifests and marketplace identity. Users update/reload through their host; existing workspace migration remains explicit.

## Stage and promote MCP

MCP implementation and baseline client work can proceed while AS foundation changes are in progress. Final acceptance uses the exact integrated AS source; publication of OSS alone does not establish MCP readiness.

1. Rebuild the MCP package from the selected AS source. Include `corpus/`, `tools/`, `clusters/` and `studio/` alongside existing resources. Revalidate forwarding references, dotfile templates, complete paginated content and script bindings. Do not edit generated packaged copies as source.
2. Build and test the service; tie the immutable build receipt to CI output and the staging deployment. Report service version separately from AS content version and digest.
3. Test authentication, actual resource retrieval, at least one executable operation and governed workflow behavior in each supported client. Test missing host capabilities as explicit blocked paths; do not report instruction delivery as completed work.
4. Demonstrate client refresh, staged AS-content upgrade and rollback. Record the service/content pair before and after each transition. Restore the previous known-good pair without changing user records.
5. After the OSS publication is independently verified and production release is authorized, promote the verified immutable staging candidate using the hosted controller. Verify production source/build identity and authenticated behavior. Retain the prior deployment and recovery receipt.

The hosted pipeline owns exact infrastructure commands and credentials. They are not duplicated into this public repository. No secrets belong in release evidence. A source-health failure degrades the affected capability; HTTP availability never establishes legal applicability or a valid source edition.

## Acceptance boundary

OSS can ship when its own gates pass; MCP can follow later. Current MCP client evidence for an earlier AS version must be rerun where final content or bindings changed. Unverified clients remain unverified, and unsupported execution is explicitly declared. No shared-team store, synchronization or independent Norma agent is implied by this release.
