# Host failure-mode evaluation, 1.4.4 against 1.4.5

**Status:** executed · **Target:** measurement, no release · **Author:** ALPA · **Revised:** 2026-08-27

Results: [`docs/reports/2026-08-27-host-condition-eval.md`](../../reports/2026-08-27-host-condition-eval.md). The patch under test was found inert and was not adopted; the harness was kept.

Version 1.4.5 adds host-requirements notes to nine skills and a shell-less guard to the two SIF converters. It changes no functionality. Its claim is not that fewer tasks fail, but that failures on a host without shell execution arrive early, named, and before any file is written, instead of late, opaque, and part-way through a conversion.

This evaluation tests that claim. It is a measurement exercise; it gates no release.

## What this evaluation must not do

A raw success-rate comparison would report that 1.4.5 did nothing, and could report it as a regression. On Claude Code the expected delta is exactly zero. On Claude Desktop the same tasks still cannot complete, and a skill that stops cleanly at step one scores as a non-success next to a 1.4.4 run that consumed six turns before dying. Success rate is reported here, but never on its own.

The measured quantity is the **distribution of failure modes** and the **work wasted before failure**.

## Surfaces

| Arm | Harness | Role |
|---|---|---|
| Claude Code, macOS | `claude plugin eval` | Regression control; any movement blocks release |
| Codex, macOS | scripted | Cross-harness regression control |
| Claude Desktop, macOS | manual | The surface the patch is for |

Windows is excluded by decision. ChatGPT is excluded because it cannot install the plugin in either version: Arch Studio is a Claude Code plugin, and ChatGPT accepts MCP connectors only. There is no error rate to compare there until an MCP server exists. Pasting a `SKILL.md` into ChatGPT measures something else and is recorded separately as a portability probe, never as an arm.

## Primary design: within-version contrast

The strongest comparison does not compare versions.

On Claude Desktop running 1.4.5, the nine patched skills and the five deliberately unpatched script-driven skills — `studio`, `project`, `master-schedule`, `skill-maker`, `resize-images` — sit in the same version, on the same surface, in the same session. The only difference between them is whether the skill declares what it needs. That isolates the patch effect without a second install.

The version contrast runs only on `csv-to-sif` and `sif-to-csv`, where before-and-after behavior differs visibly, to confirm the within-version result reflects a real change over 1.4.4.

## Harness

`claude plugin eval` accepts a path to a plugin directory rather than an installed version, so the two arms are two Git worktrees: one checked out at `v1.4.4`, one at the 1.4.5 commit. No version pinning is required, and both arms can run in the same window against the same model.

Both worktrees must be clean checkouts. The working repository currently carries sync-client conflict copies that already break `scripts/lint.sh`; they would also corrupt the file-existence checks below.

## Failure modes

Every run is classified into exactly one mode.

| Mode | Meaning |
|---|---|
| **S** | Success; the expected artifact was produced and is correct |
| **D** | Degraded; the answer was given in conversation, the file was not saved |
| **N** | Named stop; refused early with a stated cause, nothing written |
| **O** | Opaque failure; a tool error with no explanation of cause |
| **W** | Silent wrong; produced something plausible that is partial or incorrect |

The claim under test: on Claude Desktop, patched skills place their mass in **N** and **D** where unpatched skills place theirs in **O** and **W**. On Claude Code and Codex, the distribution does not move at all.

**W** is the mode that matters most and is easiest to miss. A partially written `.sif` file that a dealer system rejects next week is worse than any error message.

## Secondary measures

- Turns before the user learns the task cannot complete.
- Tool calls consumed before that point.
- Whether any file was written before failure. The SIF guard claims zero; this is directly checkable.
- Whether a partial artifact was left on disk.

## Task set

- **Treatment.** The nine patched skills, three prompts each: one clean case, one ambiguous input, one that requires a file to be written.
- **Unpatched control.** The five script-driven skills, the same three prompt shapes.
- **Null control.** Three pure-directive skills untouched by both versions — `spec-writer`, `epd-compare`, `site-history`. Movement here means the evaluation is measuring noise rather than the patch.

## Grading

Deterministic checks run first and settle roughly half the classifications: did the expected file exist, does the SIF output parse, does the occupancy figure match a hand-computed reference, was a partial file left behind.

The remainder is graded by an LLM judge against a written rubric of the five modes. Twenty percent of runs are double-graded and agreement is reported. Disagreement between **O** and **N** invalidates the headline result, because that boundary is the patch.

## Sample size

- Claude Code and Codex: 17 skills × 3 prompts × 5 trials × 2 versions. Automated, so run the full matrix.
- Claude Desktop: approximately 60 runs — the within-version contrast across all fourteen patched and unpatched skills at one to two trials per prompt, plus the SIF version contrast. Sufficient to detect a large shift in mode distribution, not a small one. That is the honest ceiling of a manual arm and is stated in the result.

## Confounds

- **Model drift.** Both arms run in the same window against the same pinned model, or the comparison is void.
- **Session state.** Fresh session per run. The studio and project skills write state that changes later runs.
- **Checkout contamination.** Clean worktrees only.
- **Judge leakage.** The grader must not be told which version or arm produced a transcript.

## Falsification

The patch's claim fails if any of the following hold.

- Mode distribution on Claude Desktop does not differ between patched and unpatched skills.
- Turns-to-failure does not fall for patched skills.
- Any movement appears on the Claude Code or Codex arms, which would mean 1.4.5 caused a regression.

## Delivery sequence

1. Create clean worktrees at `v1.4.4` and at the 1.4.5 commit.
2. Author the eval suite: task files, prompts, deterministic checks, and the mode rubric.
3. Run the Claude Code arm on both worktrees; confirm the null controls do not move.
4. Run the Codex arm.
5. Run the Claude Desktop arm manually, blind-graded.
6. Report mode distributions, wasted-work measures, and raw success rate together, never separately.

## Success criteria

- Every run carries exactly one mode, with inter-grader agreement reported.
- The null-control skills show no movement on any arm.
- The Claude Desktop result states its sample-size ceiling alongside its conclusion.
- The report states plainly whether the patch's claim survived, including if it did not.

## Explicitly excluded

- Windows, by decision.
- ChatGPT as an arm; it cannot install the plugin. Recorded only as a portability probe.
- Any release gate. This measures a shipped change; it does not block one.
- Latency, token cost, and output quality benchmarks. Different question.
