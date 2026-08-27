# Host-condition evaluation

Measures how bundled skills behave when the host lacks shell execution and local
file writing — the condition on Claude Desktop, and on any surface that loads
skills without giving them a terminal.

## What it measures, and what it deliberately does not

Success rate is the wrong headline here and is never reported alone. A skill that
stops cleanly because it cannot write a file scores as a non-success while being
the better outcome; a skill that thrashes for twenty turns and then emits an
unvalidated artifact scores no worse. The measured quantities are the **failure
mode** each run lands in and the **work spent** reaching it.

| Mode | Meaning |
|---|---|
| `S` | The artifact was written |
| `D` | Nothing written, the missing capability was named, content delivered anyway |
| `N` | The missing capability was named and nothing was produced |
| `W` | A write was claimed but no file changed |
| `?` | Unclassified; review by hand |

`W` is the mode that matters most and the one that is easiest to miss: a
plausible file that is wrong, or a claimed save that never happened.

## Running it

```bash
evals/host-conditions/run-case.sh <plugin-root> <shell|noshell> <case-id> <trial> "<prompt>" <out-dir>
evals/host-conditions/grade.py <out-dir>
```

`<plugin-root>` is a checkout of this repository, so two versions are compared by
pointing at two worktrees. `claude -p --plugin-dir` loads a plugin straight from
a directory: no install, no marketplace entry, and nothing pushed.

Cases live in `cases.tsv`. The fixture is a deterministic three-product project
built by `make-fixture.sh` and validated by the real `csv-library.py`.

## Two traps worth knowing before trusting a number

**`--allowedTools` does not restrict anything.** It is an auto-approve list. A
run given only `--allowedTools Skill Read Glob Grep` still reached `Write` and
produced a real file, which made the first "no shell" arm measure nothing at all.
`--disallowedTools` is what actually withholds a tool.

**Deterministic graders produce confident false findings.** Three separate regex
defects each yielded a plausible result that survived until it was checked by
hand: an offer to save (`"Want this saved to a file?"`) read as a claim, a
negation (`"Nothing was written to PROJECT.md"`) read as a claim, and a file
modified in place read as no output because its name was not new. All three are
guarded in `grade.py`; treat any new grader as wrong until a run is verified
against it manually.

## Same-version controls are mandatory

Two runs of the same version differ from each other about as much as two runs of
different versions do — header wording, field grouping, and ordering all move.
Any comparison without a same-version control will report that variance as a
finding.
