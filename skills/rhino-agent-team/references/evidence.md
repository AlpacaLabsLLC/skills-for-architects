# Evidence

Read when the user asks whether this works, or whether several agents are worth it. Quote these figures with their limits; do not round them into a claim.

**No measured run used rhino-model or any Arch Studio skill**, including all of test 3. Every agent was a bare model with the test harness's Python helpers, working in headless documents, with a script that started each round, saved, reopened and measured the files. Unserved points and undersized runs, the most common failures below, are what rhino-model's own requirements check is meant to catch, so part of what a coordinator seemed to add may overlap with it.

## Where each part comes from

| Part | Measured in | Result |
|---|---|---|
| One file per agent, fixed layer ownership | two-agent stair (12 runs), two-agent drawing sheet (11 runs), both tests below | No ownership break in any run |
| A revisioned shared file as the single source of numbers | the same | Every run redid its work after a mid-run change and ended on the new revision, except one no-coordinator run (row house, Haiku) |
| Notes in the model | two-agent stair | Notes alone: 24 of 24 checks in 4 of 4 runs; with a chat channel added, 24, 23, 22 and 23 |
| Notes for agreeing a fact (numbering) | two-agent drawing sheet | Notes alone 8 of 12 communication checks, with a channel 12 of 12. Putting the allocation in the set-out, as this skill does, is untested |
| The coordinator writing the set-out first | tests 2 and 3, below | Fewer first-round clashes in every run; not enough on its own after a change |
| Space handed out on request | test 2, below | No gain over no coordinator |
| The coordinator reviewing the combined model every round and sending issue notes | test 3, below | With a set-out first, the only setup that ended coordinated every time (2 of 2) |
| Issue notes between owners | test 3, below | Written in every setup (0 to 12 per run); 45 of 64 acted on by the next round |

## Test 1: row house, set-out written by the test, not by an agent

A Brooklyn row house with services (routes and equipment, no sizing): shell, mechanical, plumbing and electrical owners, 42 required points, a change at round 5. The test itself wrote the levels, chases and 25 reserved boxes before the run, so the space was already divided.

| | Four owners + coordinator | Four owners, no coordinator | One agent |
|---|---|---|---|
| Haiku, runs ending clean with 42 of 42 | 3 of 3 | 2 of 3 | 3 of 3 |
| Haiku, mean cost and time | $0.35, 35 min | $0.34, 34 min | $0.28, 23 min |
| Sonnet, one run each: clean, cost, time | yes, $2.76, 23 min | yes, $2.46, 20 min | yes, $1.14, 12 min |

No two owners clashed in any round of any run, so the coordinator had nothing to settle. The one agent's weak spot was housekeeping: openings and requests left on the old revision stamp (71 and 132 in two Haiku runs, 35 on Sonnet).

## Test 2: three owners forced to share, the coordinator writes the set-out

Same house; mechanical, plumbing and electrical owners; the shell given and fixed. All risers must pass one 22 by 24 in shaft and all mains one 30 by 14 in opening in a cellar wall, sized so they fit only if packed on purpose (a scripted check showed shortest routes clash at both). Each owner had minimum run sizes. A post took part of the shaft at round 5. 8 rounds, 3 runs per arm on Haiku and 3 on Sonnet: 18 runs. No one-agent arm.

| | No coordinator | Set-out written up front | Space on request |
|---|---|---|---|
| Runs that passed (clean, 42 of 42, nothing through the shell, no note open) | 2 of 6 | **5 of 6** | 2 of 6 |
| Runs ending with a clash | 1 of 6 | 0 of 6 | 0 of 6 |
| Clashes in round 1, each run | 28 66 39 51 71 53 | **0 19 0 15 2 0** | 36 56 57 79 33 36 |
| Runs with any clash at the shaft before the change | 6 of 6 | **0 of 6** | 6 of 6 |
| Cost per run, Haiku / Sonnet | $0.48 / $3.31 | $0.52 / $3.33 | $0.69 / $3.31 |

What three runs per arm support:

- **The round-1 gap holds in every run on both models:** every up-front run (highest 19) had fewer first-round clashes than every run of the other two arms (lowest 28).
- **As direction only:** space on request did no better than no coordinator, and up front finished more models.
- **Not as rates:** 5 of 6 against 2 of 6 is suggestive; several failures were one open note.
- **Without a coordinator, trades did sort out their clashes themselves,** in 3 to 7 rounds; 5 of 6 such runs ended with no clash. The failures were mostly things nobody was checking: points left unserved, and in one Sonnet run four clashes that appeared in the last round because two owners each moved against the other's file as saved a round earlier.

## Test 3: who the coordinator should be (revision 2)

Same house, same three owners, same tight shaft and wall opening, same post in the shaft at round 5. Rules this time: notes in the model are the only channel; any agent that finds an issue leaves a note to the owner of the object that must change; the change enters once as a note at the post, addressed to the coordinator (who takes its turn first that round) or, with no coordinator, to all owners. "Coordinated" means no clash, nothing through the shell, every point served, no run under its minimum size and **no open note**. Sonnet, 8 rounds; 3 runs per setup, 2 for up front plus review (the third was not run).

| | Owners alone | Set-out up front | Review every round | Set-out up front + review |
|---|---|---|---|---|
| Ended coordinated | 1 of 3 | **0 of 3** | 2 of 3 | **2 of 2** |
| First coordinated model, round | 7, never, never | 4, 3, never | 4, never, 8 | 3, 4 |
| Rounds to recover after the change (1 = same round) | 3, never, never | never, never, never | 3, never, 4 | 3, 2 |
| Clashes in round 1 | 43 88 45 | 21 18 15 | 70 42 73 | 17 35 |
| Cost per run, mean | $3.05 | $3.88 | $4.04 | $2.83 |

Why the six runs that did not end coordinated failed (from the per-round fault causes):

- **Faults nobody pointed out stayed** where nobody reviewed: undersized runs and a run through a wall stayed from round 2 to the end with no note (both owners-alone failures), and 40 of 51 faults in the round after the change in one set-out-only run.
- **Notes left open:** four runs ended with no fault left but notes still open, in two of them after the coordinator had declared the model settled; owners also left their own requests unanswered.
- **Re-routing after the change created new faults each round**, in every setup; in a set-out-only run, one owner re-routed every round and broke something new each time.

What the reviewing coordinator did: each round it read the script's report and the open notes and wrote one note per fault to the owner who had to move. What it raised was fixed by the next round 92 to 100% of the time. With a set-out it missed 41 of 109 faults the script listed, 37 of them share breaks; without one it missed 20 of 325.

Limits: 2 or 3 runs per setup show direction only. No setup recovered from the change in the round it arrived.

## Corrections that limit these results

- **In test 2 the change was delivered to the owners before the coordinator,** so every coordinator run carried a one-round delay after the change; its after-change figures are not used. Test 3 fixed this: the change arrived as a note to the coordinator, who went first.
- **A set-out written at round 0 cannot anticipate a change made at round 5,** so recovery after the change measures the coordinator's reaction, not the set-out.
- **In test 2 the coordinator's rulings were mostly space instructions** ("move your risers into this box"); test 3 measured a coordinator that reviews and writes issue notes.
- **"Coordinated" got stricter in test 3** (an open note fails a run, and the change arrives as a note), so test 2's pass counts and test 3's are not comparable: set-out up front passed 5 of 6 in test 2 and ended coordinated 0 of 3 in test 3.

## Not tested

Owners using rhino-model (the next step is test 3 with both skills loaded); window documents; a person driving the rounds; saving from the agent's own session; agents of different people; more than four owners; larger models; Opus.
