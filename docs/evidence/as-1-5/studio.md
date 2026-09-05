# AS 1.5 studio and commercial validation

Date: 2026-09-05. Workstream: implementation plan W2–W3 and deterministic OSS recovery checks in W8. Baseline: `4d4b067b9d57dfb5f50108d915ddf9aad5ed3a71`. Branch: `feat/as-1-5-studio-validation`.

## Result

The existing studio, project, commercial and migration implementations passed all 39 baseline shell contracts. Review found two retry defects: recording the same SOW allocated another amendment row, and appending the same invoice number allocated another ledger row. Both now reject the duplicate before creating a temporary output or mutating canonical records.

Invoice uniqueness includes void and corrected history. A correction uses a distinct revision number and cites the original permanent row ID. Amendment identity is the document already referenced in the Amendments table; a new amendment needs a distinct document. These are sequential, single-writer protections, not concurrency guarantees. Adversarial follow-up checks also reject AWK escape/control injection in amendment fields and compare invoice identities after trimming table-cell padding, preventing a whitespace-only duplicate bypass. The four affected executable/contract tests passed again after this hardening.

## Fresh verification

| Check | Result | Evidence scope |
|---|---|---|
| All 39 baseline `tests/test-*.sh` | Passed | Repository contracts and executable synthetic fixtures; includes existing FF&E regressions |
| Agreement contract and workspace tests after changes | Passed | Source checksum, explicit acceptance, direct engagement, path confinement and amendment handling |
| Invoice contract and ledger tests after changes | Passed | Arithmetic, correction lineage, lifecycle, failure atomicity and ledger boundaries |
| New commercial lifecycle integration test | Passed | Combined project → proposal → agreement/amendment → invoice path, duplicate rejection and byte preservation |
| `CI=true bash scripts/lint.sh` after changes | Passed | 50 skill frontmatter entries, paths, public namespace and shellcheck, including new test |
| `git diff --check` | Passed | Whitespace integrity |

The baseline loop expanded its test file list before the new test was added; the new integration test and all four affected existing tests were then run separately against the changed source. Integration must rerun the complete suite after merging the architecture extraction work.

## Coverage map

| Requirement | Existing or added proof |
|---|---|
| Studio setup, universal projects, readable naming and lifecycle | [Studio workspace tests](../../../tests/test-studio-workspace.sh), [project workspace tests](../../../tests/test-project-workspace.sh) |
| Context boundaries, stale/moved identities and ambiguous records | [Context resolution](../../../tests/test-project-context-resolution.sh), [studio/project boundaries](../../../tests/test-studio-project-boundaries.sh), project workspace tests |
| Typed-record authority, routing and optional portfolio register | [Record integration](../../../tests/test-project-records-integration.sh), studio workspace, tasklist, meeting, site report and timetracker contracts |
| Proposal creation/issue/acceptance and revision history | [Proposal register](../../../tests/test-proposal-register.sh), [commercial lifecycle](../../../tests/test-commercial-lifecycle-integration.sh) |
| Agreement source citation, amendments and issued-term tampering | [Agreement workspace](../../../tests/test-agreement-workspace.sh), commercial lifecycle |
| Invoice lifecycle, totals, corrections and retry identity | [Invoice ledger](../../../tests/test-invoice-ledger.sh), commercial lifecycle |
| Original professional-practice knowledge and typed handoffs | [Knowledge contract](../../../tests/test-architecture-knowledge-contract.sh), [knowledge integration](../../../tests/test-architecture-knowledge-integration.sh) |
| Format-2 preview, format-3 adoption, commercial migration and preserved instructions/history | [Migration](../../../tests/test-project-migration.sh) |
| Failure rollback, exact bytes/topology, failed restore and retained recovery snapshots | Migration tests and [rollback failure](../../../tests/test-project-rollback-failure.sh) |

The combined fixture uses synthetic issue/acceptance receipts and explicit lifecycle commands. It verifies that commercial activity leaves `PROJECT.md`, `.as-folder.json` and issued proposal bytes unchanged. It does not claim a model independently evaluated approval evidence correctly. Internal project creation also proves that commercial records are not required or inferred.

## Remaining integration and release gates

- Rerun all tests from the final integrated source after shared templates, knowledge and tooling move.
- Validate fresh installed Codex/Claude Code plugin behavior outside the checkout. Repository compatibility tests are not actual installed-host acceptance.
- Real rendered artifacts, MCP-only client checks, desktop access, actual hosted operations, CI-to-staging linkage and deployment rollback remain with the integration/MCP workstreams.
- These disposable migration fixtures establish deterministic recovery behavior; they are not a customer-data migration or permission to migrate a studio automatically.
- No customer records, release tags, marketplace publication or production deployment were changed. No independent Norma functionality was added.
