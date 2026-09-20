# Plugin eval suite

Behaviour tests for the Arch Studio plugin, run with `claude plugin eval` ([docs](https://code.claude.com/docs/en/plugin-evals)). Each case runs with the plugin and again without it, so the score difference shows what the plugin contributes.

```sh
claude plugin eval . --trust-plugin --scaffold --model claude-sonnet-5 --judge-model claude-sonnet-5 \
  --allow-tools Read Write Edit Glob Grep WebSearch WebFetch --max-cost-usd 25 --no-publish
```

`--scaffold` is required. The two fixture cases stage their input file with a `scaffold.sh` the runner executes in the empty workspace; without the flag the script does not run and the case asks the agent for a file that is not there.

Six cases: four answerable from knowledge (`occupant-load`, `outline-spec`, `unrelated-coding-request`, `unverifiable-citation`) and two that read a supplied fixture and write a file (`csv-cleanup`, `spec-pdf-parse`). Run the fixture cases with `--tag fixtures`.

Conventions that matter here:

- **Fixtures are staged by `scaffold_script`, not `add_dirs`.** `context.add_dirs` only grants read access inside the case directory; it puts nothing in the working directory, and an agent starting in an empty workspace cannot resolve the path. Measured on 2026-09-20: `add_dirs` 0 of 10 runs found the file, `scaffold_script` 3 of 3.
- **Grade what the run produced, not only what it said.** An `llm` grader defaults to `focus: last_message`, so a skill that writes its answer to a file scores zero on a correct answer. Use `focus: trace`, or `{source: file, path: ...}` for one known file.
- Run limits belong in `prompt.md`, not `case.yaml`; graders use JavaScript regex, so flags go in the `flags` field; `--case` keeps only its last value, so group with `--tag`; turn caps are 30 because these skills verify sources before answering, which takes 9 to 15 turns where an unaided model takes 1 to 5.

These cases were first measured against the public 1.4.5 plugin, where they showed no positive contribution on any case. The fixture-case and `outline-spec` figures in that baseline were produced before the two defects above were found and do not stand; the knowledge cases are unaffected. That baseline, its cost figures and its limits are recorded in the ARCHITECTURE-STUDIO project record under `docs/evaluations/`. The `skill-fired` graders name skills by their 1.4.5 names; check them when a skill is renamed or its ownership moves.

`results/` is written by each run and is not committed.
