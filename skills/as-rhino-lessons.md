# Arch Studio for Rhino: local lessons

The as-rhino skills (`rhino-model`, `rhino-bom`, `rhino-batch-image-export`, `rhino-thinline`, `rhino-axon`) learn on purpose, on this machine: each run writes what it learned, and the next run reads it before planning. Nothing leaves the machine.

`rhino-batch-image-export` was called `rhino-display` in earlier test builds. Lessons, firm rules and declined lines saved under the old name still count for it, and the script accepts the old name; new lines are written under the new name.

**What a lesson may hold: two kinds only.**

| Kind | What | Examples |
|---|---|---|
| `practice` | Modeling practice: how to build reliably in Rhino | geometric construction, normals, joined edges, duplicates, construction tolerances, a call or overload that failed and what worked |
| `preference` | The user's own preference, stated by the user | tolerances, layers, naming; a design preference only when the user said it themselves |

Never save a design, architectural or engineering rule you inferred, such as a roof overhang, a door placement, a member size or a code value: mention the observation to the user in the reply and save nothing. A preference records that the user said it (`user_said`). The same boundary holds for firm rules, which are promoted only from these two kinds.

The script cannot judge a lesson's meaning. You declare the kind under these rules; the script refuses a lesson with no kind or another kind, and a `preference` without tag `U` and `user_said`.

## Where

The plugin's data folder, which Claude Code keeps across plugin updates (`CLAUDE_PLUGIN_DATA`), in a `rhino-lessons` subfolder. The Arch Studio startup line names it ("Their lessons folder: ..."); pass that path as `AS_LESSONS_DIR`. Without a startup line, leave `AS_LESSONS_DIR` out and the script finds the folder from its own install path, or says it cannot. Never use the panel's own memory folder: it is keyed to a temporary path.

Plain text, one file per skill (`rhino-model.txt`, ...) and one `firm-rules.txt`. The user may read, edit or delete them. Uninstalling the plugin deletes the data folder unless the user keeps it.

## The script

[as-rhino-lessons.py](as-rhino-lessons.py), in this folder, used by all four skills. Build its path from the folder this file is in; never reuse one from another version.

```python
P = "<absolute path of the skills folder>/as-rhino-lessons.py"
exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read", "AS_SKILL": "rhino-model", "AS_LESSONS_DIR": "<lessons folder from the startup line>"})
```

| `AS_MODE` | Also pass | Does |
|---|---|---|
| `read` | | Prints the firm rules for the skill, then its lessons, newest first, with repeats counted |
| `write` | `AS_LESSONS`, `AS_PRIVATE`, `__rhino_doc__` | Appends this run's lessons, each with its kind, stripped of private details; refuses a lesson without an allowed kind |
| `offer` | | Lists the user's own corrections that may become firm rules, each with an id |
| `promote` | `AS_PROMOTE` | Writes the chosen lessons to `firm-rules.txt`, only after the user agreed |

## Read, before planning

Run `read` once, before the questions or the first script. Follow every firm rule. Apply a lesson where it fits this brief. Name the firm rules and user preferences you applied in the reply, as plain rules (at most three); record every other lesson you applied in the run notes the skill keeps. A lesson marked unconfirmed is a judgment from one run: weigh it, do not treat it as a rule.

## Write, at the end of every run

After the report's checks, write what this run learned, one short general line per lesson, each with one kind (above) and one tag:

| Tag | When |
|---|---|
| `U` | The user corrected something: a value, a name, an element, the scope |
| `F` | Something failed, and a change fixed it: the signature as it appeared and the call or value that worked |
| `M` | A value was measured from the model or a file and settled a question |
| `J` | You changed your mind on your own judgment, including a derived value adjusted: unconfirmed |

```python
AS_LESSONS = [{"tag": "F", "kind": "practice", "text": "CreateBooleanDifference with a Python list hit the single-Brep overload; a List[G.Brep] worked"},
              {"tag": "U", "kind": "preference", "text": "Name layers in capitals", "user_said": "I always want layer names in capitals"}]
AS_PRIVATE = ["<every project name, client, person and place named in this session>"]
```

Write a lesson that is true of the element, the tool or the user's way of working, not of this one model. A `J` lesson is always `practice`: a judgment of yours is never the user's preference. Write nothing when the run taught nothing. Never write a lesson that changes the requirements check, the PDF check, their tests or answer keys: the script refuses one, and a lesson that only passes a check measures nothing.

**Private details.** Lessons never hold project names, places or personal details unless the user wrote them in. List them in `AS_PRIVATE`; the script also strips the document's name, paths, emails, phone numbers, URLs and street addresses, and refuses a lesson with too little left. Set `"user_wrote": true` on a lesson only when the user dictated its wording.

## Promote, with the user's yes

Then run `offer`. Only the user's own preferences and practice can become firm rules: `offer` lists the `U` lessons with a kind that no firm rule covers yet. A lesson about our tools, scripts or checks (clash or contact behaviour, a script overload, a checker format) is never offered, however often it repeats: it stays a lesson. From what `offer` lists, drop any candidate that is really about a tool or check, or that a firm rule already says.

If nothing is left, ask nothing. Otherwise end the reply with one `ask_user` question, for example "Make any of these a standing rule for your future models?", multi-select, with:

- one option per candidate, written as one plain rule an architect would recognise ("On sheds, put the door centred on a short end wall unless I say otherwise", where the user said so). The option label is the rule itself: no id, no tag, no run count, no tool names;
- a last option "None, keep them as lessons".

None is proposed by default. Ids stay in the file and in your call to `promote`, never in the question. Run `promote` only on the answer, with the ids the user chose, `"confirmed": True`, the answer in the user's words and, for each id, the wording the user saw, which is what the firm rule keeps:

```python
AS_PROMOTE = {"ids": ["a1b2c3"], "confirmed": True, "answer": "<the user's answer>", "scope": "skill",
              "wording": {"a1b2c3": "On sheds, put the door centred on a short end wall unless I say otherwise"}}
```

Pass every candidate the user did not choose in `"declined"` (all of them when the answer is "None"): they go to `declined.txt` and are not offered again, so the next run asks nothing about them. The user can delete a line there to have it offered again.

`"scope": "all"` makes the rule apply to all four skills. The script refuses `promote` without a confirmation and an answer, and refuses an id `offer` did not list.

**Lessons written before kinds existed** are read and kept, never deleted, but are not offered or promoted. The user can add `practice: ` or `preference: ` after the tag in the file to make one eligible.

## Host memory (optional)

The startup line names the folder on every start and after compaction, so no memory entry is needed. Where the host has a memory location that is stable and known, one line there may point to the lessons folder; the panel's memory folder is not, so the skills do not write one.
