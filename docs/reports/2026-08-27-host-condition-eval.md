# Host-condition evaluation, 1.4.4 against a host-requirements patch

Run 2026-08-27. 27 runs, $29.28. Harness and method in
[`evals/host-conditions/`](../../evals/host-conditions/README.md).

## What was tested

A candidate patch added a one-line **host requirements** note to nine skills and
a shell-less guard to `csv-to-sif` and `sif-to-csv`. Its stated claim was that on
a host without shell execution, failures would arrive early and named instead of
late and opaque.

Two conditions, both driven through `claude -p --plugin-dir` against two
worktrees of this repository:

- **shell** — `Bash`, `Write` and `Edit` available.
- **noshell** — those three withheld, reproducing Claude Desktop.

## Result: the patch was inert, and was not adopted

**Eight paired cases in the no-shell condition. Mode agreement: 8 of 8.**

| Case | 1.4.4 turns | patched turns | Δ | Mode, both |
|---|---:|---:|---:|---|
| csv-to-sif | 13 | 8 | −5 | D |
| nyc-landmarks | 17 | 19 | +2 | D |
| nyc-hpd | 11 | 11 | 0 | D |
| nyc-dob-violations | 27 | 33 | +6 | D |
| nyc-bsa | 23 | 20 | −3 | D |
| nyc-acris | 34 | 41 | +7 | D |
| nyc-dob-permits | 24 | 22 | −2 | D |
| occupancy-calculator | 25 | 24 | −1 | D |
| | | | **net +4** | |

Every run in both versions landed in mode `D`: nothing written, the missing
capability named explicitly, useful content delivered anyway. Turn deltas ran in
both directions and netted +0.5 per pair, which is noise.

The premise did not hold. The opaque failure the patch was designed to convert
never occurred. Unpatched 1.4.4 on `nyc-bsa` reported: *"The report could not be
saved — `Write`, `Edit`, and `Bash` are all disabled in this session."* That is
the note's content, produced without the note.

**No silent-wrong runs occurred in either version.**

## The regression arm passed

All nine candidate skills ran normally with the shell available — no
over-triggering, no spurious refusal. `csv-to-sif` wrote valid SIF and
`sif-to-csv` parsed it back to three validating rows, so the round trip is
intact. The patch was safe. It simply had no measurable effect.

## What the evaluation found that does matter

**`csv-to-sif` can emit non-ASCII into a SIF file.** One of three runs wrote a
UTF-8 em dash (`\xe2\x80\x94`) into the `ST` header. The other two were pure
ASCII; CRLF endings were correct throughout. Dealer importers commonly reject
non-ASCII, which makes this the silent-wrong mode reaching a third party. It is
pre-existing, unrelated to the patch, and roughly one run in three.

**Same-version output is not stable.** Two runs of one version differed from each
other as much as two runs of different versions did.

## Limits of this result

- One trial per cell on eight cases; a small effect would not be detected.
- Run entirely on one model. Weaker models may well need scaffolding this one did
  not, and Claude Desktop users run whatever their plan provides.
- The real Claude Desktop application was never driven; the condition was
  reproduced by withholding tools, which tests the mechanism rather than the app.
- The notes may still carry value for a person reading a skill, which no run
  measures.
