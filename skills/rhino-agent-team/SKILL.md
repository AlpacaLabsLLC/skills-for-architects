---
name: rhino-agent-team
description: "Run several agents on one Rhino 9 model split into one file per owner: a coordinator writes the set-out first (datum, levels, required points, minimum sizes and each owner's share of shared space), then reviews the combined model every round and sends each owner issue notes at the objects that must change, and reissues the set-out when something changes; each owner builds its part with rhino-model. Use when the user has decided to split a Rhino model across agents (separate owners, or more than one session can hold). Not for a model one agent can build alone."
---

# /as:rhino-agent-team

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-agent-team`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Requires Rhino 9 with the agent's own file open and a `run_python` tool. **Plugin-only:** the helpers and the team check run from the installed Arch Studio plugin's folder ([Rhino skill helpers](../../docs/host-harness-contract.md#rhino-skill-helpers)); through hosted MCP instruction delivery this skill is not available. If you cannot find this skill's folder on disk, stop and tell the user to install the plugin. The file conventions are in [protocol](references/protocol.md); what was measured, and what was not, is in [evidence](references/evidence.md).

## Outcome

Each owner's part built in its own file and passing its own [rhino-model](../rhino-model/SKILL.md) requirements check, every file stamped with the current set-out revision, and a team check that prints `Team: settled`; or the team check's exact list of what is still open.

## First: should this be several agents?

Say this to the user before setting anything up, in plain words:

- **One agent was as good where it was tried.** On a row house with full services, one agent reached the same clean model as four owners with a coordinator, for less money and in less time, on Haiku (3 runs) and Sonnet (1 run). The tests that forced owners into the same tight space did not include a one-agent run.
- **If the model is split, set out space first and review every round.** With three owners forced to share one shaft and one wall opening and a change in round 5, a coordinator that set out space up front and then reviewed the combined model every round ended with a coordinated model in 2 of 2 runs, soonest (rounds 3 and 4) and cheapest. Review alone did it in 2 of 3, owners alone in 1 of 3, and a set-out with no review in 0 of 3: faults nobody pointed out stayed, and models were called settled with notes still open. Writing the set-out first also cut first-round clashes from 28 to 88 down to 0 to 35. A coordinator that only handed out space when asked did no better than none.
- **A change takes rounds.** No setup recovered from the change in the round it arrived; it took 2 to 4 rounds.
- **How strong this is:** 2 or 3 runs per setup, one building, one change, bare agents with no Arch Studio skill loaded, in a test harness. A direction, not a measurement. Agents run by people in their own sessions and owners belonging to different people were never tried.

The honest reasons to split are outside what was tested: parts owned by different people, or a model too large for one session. If one agent will do, use [rhino-model](../rhino-model/SKILL.md) alone.

## Who does what

| | Coordinator (this skill) | Each owner ([rhino-model](../rhino-model/SKILL.md), plus [working in a team](#working-in-a-team)) |
|---|---|---|
| Writes | `setout.3dm` only | its own file only |
| Owns | who owns which file; the set-out; the review of the combined model each round; deciding who moves when owners disagree; the team check | its questions, requirements, build scripts and own requirements check |
| Asks the user | yes, once, for every open value the owners send up | never; open values go to the coordinator |
| Never | models, or writes an owner's file | writes another owner's file or the set-out |

## Invariants

1. **The set-out comes first.** No owner builds before the set-out exists at revision 1. It holds the datum (origin, axes, units), named levels, the required points, minimum sizes, the host owner whose elements others pass through, the priority order, and each owner's share of every space more than one owner needs (shafts, chases, ceiling zones, openings in walls). Shares of two owners never overlap.
2. **A change goes to the coordinator first.** A change order enters as a note of kind `change` at the place it is about, addressed to the coordinator, whoever receives it first. The coordinator reissues the set-out with `issue("<plain description>")`, redraws the shares the change moves, and directs the owners it affects by notes; only then do the owners take their turn. Owners read the description, not a diff. Expect the next rounds to create new faults as owners re-route: review every round after a change until the team check is clean again. In the measured runs a set-out with no review lost the coordinated model after the change every time.
3. **One file per owner, and only that owner writes it.** Others' work is read from their files as last saved. An object on another owner's layers is a fault.
4. **Two checks, one deliberate overlap.** Inside one file, the owner's rhino-model requirements check, which measures the owner's shares, minimum sizes and required points (`within`, `network`). Across files, the team check: clashes, runs through the host without an opening, unanswered opening requests, objects in another owner's share, stale revision stamps, open notes, whether each owner's own check passed on its current requirements and on the file as saved, and whether every file was written by the same plugin and helper version as the set-out (a version mismatch). The one overlap is **required points served**: the team check counts them too, because an owner that leaves a set-out point out of its own requirements would otherwise be caught by nobody, and unserved points were the most common failure in the measured runs without a coordinator. The model is settled only when both checks pass.
5. **Whoever finds an issue writes it, at the place.** Any agent, owner or coordinator, that finds a problem in or with someone's objects leaves a note of kind `issue` at that spot, addressed to the owner of the object that has to change, with from, to, kind and status. It never fixes another owner's objects and does not wait for the coordinator's turn. The owner replies when the fix is in its file; the author closes the note. Notes are open to all: the team check lists open notes by addressee, and the coordinator reads every one each turn.
6. **Rebuild only what moved, and look before you save.** One script per assembly; after a new revision, rerun only the assemblies the change or a note touches. Before saving a re-routed run, check it against the other owners' files as last saved (`others()`) and against your own requirements check. In the measured runs, owners re-routing after a change caused nearly all the faults that followed, often breaking something new each round.
7. **Nothing is settled while a note is open.** Every owner answers each note addressed to it in the turn it reads it (a fix and a reply, or a reply saying why not) and closes its own notes once answered. The coordinator never reports the model settled while any note is open, its own rulings included; the team check enforces this. Four of the six measured runs that did not end coordinated were models with no faults left and notes still open, and in two of them the coordinator had declared the model settled anyway.
8. **Reissue the set-out at most once a round, and only when shares change.** Every reissue raises the revision, and every owner file, stamp, opening request and opening built to the old one goes stale until its owner rebuilds. Collect all of a round's share changes and rulings, then reissue once; a ruling that moves no share is a note, not a reissue. Save the reissued set-out before running the team check, or the check reads the old revision. (A measured coordinator reissued five times in five rounds and left 16 to 22 stale references in every check.)

## Procedure

1. **Preflight, every agent, before anything else.** Follow [rhino-setup](../rhino-setup/SKILL.md): the Rhino tools are present, a document is open, its units are known. Then load the helpers (step 4) and run `print(ns["preflight"]())`: it names the shared folder, whether the set-out exists, any owner file that is missing, and whether the open document is your own file. Stop and give the user the exact missing action while `problems` is not empty; do not build, review or rule until every agent's preflight is clear. **The coordinator's preflight does not wait for the set-out:** before one exists it is clear, and its `next` says to save the open document as `setout.3dm` in the shared folder and write the set-out (step 3). An owner's preflight stays blocked until the set-out exists; an owner whose own file is not saved yet is told where to save it.
2. **Set up, with the user, once.** Agree the shared folder, the owners and their files, and the host owner. Collect every value the owners will need in one round of questions, so no owner has to ask the user.
3. **Write the set-out** in `setout.3dm` (coordinator's document): `write_setout(...)`, one point per required point on `Setout::Points`, and `share(...)` for each owner's share of every space more than one owner needs. Leave no shared space unallocated where two owners' routes could meet.
   - **Levels come from the host's floors:** `levels_from(<host objects>)` gives one level per floor or slab, at its top, named as the floor is (`Cellar`, `F1`, ... `Roof`). Pass that list as `levels`. Ceilings and joist undersides are not levels: put them in `numbers`. (Every measured set-out written by hand gave levels the grader could not match.)
   - **Size each share to the runs it holds,** not to the whole zone: its count of runs times the owner's minimum size plus working clearance. A share is room for runs, not the ceiling.
   - **Declare every shared space and who passes through it:** `"shared_spaces": [{"name": "Shaft", "box": [...], "owners": [...]}]` in the set-out data, for every opening the host leaves for runs to pass a wall or floor (a shaft, a slot or gap in a wall). An owner passes through it when its source and some of its points lie on different sides of that wall or floor and this is the way through; list every such owner, and give each a share inside the space. (In a measured run the coordinator gave the one gap in a cellar wall to one owner, though all three owners' mains had to pass it.)
   - **Keep shares clear of the host's solids** (walls, slabs, joists), except through the host's openings such as the shaft.
   - **Where an owner's run must cross the host** (a line set through a wall, a pipe through a floor), draw that piece as its own short share with `share(..., crossing=True)`, just around the run. A crossing share may sit in host solids only inside a host opening or the owner's own opening request; `check_setout()` and the team check refuse it anywhere else. The owner keeps the crossing piece in that share, so its own check passes at the crossing, and requests the opening as usual.
   - **Run `check_setout()` and fix every problem before the owners' first turn,** and again after every `issue()`. The same check also runs by itself: `issue()` returns it with the new revision, and every team check includes it (`setout_gaps`) and refuses `Team: settled` while any problem remains, so shares redrawn mid-run cannot leave an overlap behind. It refuses levels off the host's floors, host floors with no level, a share running into a host solid, and overlapping shares, and warns about a share far larger than its owner's runs. When the host is not an owner (a given shell nobody writes), name its file in the set-out data as `"host_file": "<file>.3dm"`: the re-check in `issue()`, `check_setout()` and the team check then always read the host as last saved, including geometry a change adds. Without `host_file`, they use the one other `.3dm` in the shared folder if there is exactly one.
4. **Rounds are driven by the user.** Nobody else starts a round. In a round, every owner takes a turn on the others' files as last saved, then saves; then the coordinator takes its turn. When a change has been issued, the coordinator's turn comes first in that round. Each turn, load the helpers by path from the folder you read this `SKILL.md` from, which belongs to the installed plugin version:

```python
P = "<absolute path of this skill's folder>/scripts/as-agent-team.py"
ns = {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_TEAM": {"folder": "<shared folder>", "me": "<owner name or coordinator>", "round": 3}}
exec(compile(open(P).read(), P, "exec"), ns)
print(ns["summary"]())
```

5. **Coordinator turn: read everything.** Run the team check with `"AS_MODE": "check"` and `"write": True` in `AS_TEAM`, and read every open note, not only those addressed to you (`summary()` lists them as `all_open_notes`).
6. **The team check writes the fault notes; you keep the judgment.** Every round, run `ns["post_fault_notes"]()`, then `save()`, then the team check with `"write": True`. The helper turns every fault on the check's list into one `issue` note at the object, addressed to the one owner who must move, marked as written by the check (`by: "team-check"`, with a `fault_key`): clashes (the share decides who moves, then the priority order), share breaks, runs through the host without an opening, requests the host has not answered, unserved points, failed `within` checks, and notes left unanswered for a round. It writes no second note for a fault whose note is still open, and closes its own notes once the check no longer lists the fault. **Do not retype faults as notes yourself:** whoever detects a problem most reliably documents it. In the measured barn run the coordinator's own review covered 10 of 27 faults and raised 15 wrong issues; a scripted reviewer raising exactly the check's list missed none. Your review keeps only what needs judgment:
   - **disputes:** an owner replies that the other owner should move instead; decide under step 7 with a `ruling`;
   - **set-out changes:** a share that does not work, or a fault no move within the shares can clear;
   - **the architect's change order** (a `change` note), under invariant 2;
   - stale items the check marks `for_coordinator` in `stale_by_owner` (left stale for a round after their reissue).

   You never model.
7. **Decide what owners cannot settle:** who moves when two owners each say the other should, and anything that changes the set-out (a `change` note, a share that does not work). Rule with one `ruling` note to the owner who moves. A `request` for an open design value that only the user can answer goes to the user once, in one question with the others.
8. **Finish** only when the team check prints `Team: settled`: no fault, every point served, every owner's own check current, no note open, and no version mismatch. A version mismatch means an owner's machine runs a different Arch Studio release or helper than the coordinator's: ask that person to update to the coordinator's release (see [Installing for a team](#installing-for-a-team)), then have them run their check, `stamp()` and `save()` again. If it does not settle within the rounds the user allowed, stop and report the check's list.

## Installing for a team

Every person's machine runs the helpers from its own installed plugin, so every machine needs the Arch Studio plugin (`as`), and everyone must be on **the same release** before a team session. `stamp()` and `write_setout()` record in each file the plugin version and a fingerprint of the helpers (this skill's script and rhino-model's check scripts, so a locally edited copy shows too), and the team check refuses `Team: settled` until every owner's file matches the coordinator's set-out.

- **Install on every machine:** `claude plugin marketplace add AlpacaLabsLLC/skills-for-architects`, then `claude plugin install as@skills-for-architects`. For the Rhino AI panel, install at user scope (the default), since the panel reads the user's settings.
- **Claude Code, shared project:** the firm can commit the marketplace and the enabled plugin in the project's `.claude/settings.json`, under `extraKnownMarketplaces` (`"skills-for-architects": {"source": {"source": "github", "repo": "AlpacaLabsLLC/skills-for-architects"}}`) and `enabledPlugins` (`"as@skills-for-architects": true`). Claude Code registers the marketplace once each teammate trusts the folder; enabling the plugin there does not install it, so each teammate still runs the install command above.
- **Before a team session:** everyone updates to the same release (`claude plugin marketplace update skills-for-architects`, then `claude plugin update as@skills-for-architects`), and each agent's `summary()` shows its `plugin` and `helper` so they can be compared.

## Working in a team

Read this part if you are an owner. Build your part with [rhino-model](../rhino-model/SKILL.md), as its section *When a set-out exists* describes. Each turn: `summary()` first; read notes addressed to you; if the set-out revision is newer than your stamp, read its `change` and handle it as a brief change; build only in your shares or in space the set-out leaves to you; `request_opening(...)` where a run of yours crosses the host's elements; answer every note addressed to you this turn and close your own notes once answered; **clear your own stale items this turn without waiting for a note:** run the team check read only (`team_check = ns["check"]` on the shared folder, without `write`) and act on your entries in `stale_by_owner`. `re-stamp` means the item still holds: `restamp_requests()` re-stamps your requests that still sit in your shares or a host opening. `rebuild` means what it was built to moved: rebuild it, check, and stamp. A reissue that did not touch your shares, points, levels or datum leaves your work current; nothing of yours is listed then; when you see a problem with another owner's objects, `note(<that owner>, ..., kind="issue")` at the place, and leave their objects alone; answer issue notes addressed to you with `kind="reply"` once fixed, or reply saying why not if you disagree; `note("coordinator", ..., kind="request")` only for open design values and for candidate lessons; run your own requirements check after the last geometry change; then `stamp()` and `save()`. `stamp()` returns its status against the set-out as it is now: report it as given, and if it says **stale**, your file is not current, whatever you stamped; read the set-out's `change`, rebuild what moved, check and stamp again. The helpers refuse to write when the open document is not your file.

## Report

Open with the team check's `Team:` line exactly as printed. Then: the set-out revision and its last change, the rounds run, the issue notes you wrote and closed this round, per owner its own check status and what changed this round, open notes, and what is not checked (below). Complete under the [completion contract](../../docs/completion-reporting.md).

## What the team check can and cannot prove

It reads the saved files only. It accepts an owner's own check only when the stored result passed, was run on the file's current requirements revision, and carries a geometry fingerprint (object ids, layers and bounding boxes) equal to the saved file's; an owner whose file changed after its check fails. Notes are left out of the fingerprint. Clashes are shared volume between two owners' solids (touching is not a clash); share and connection checks use bounding boxes, so runs should be straight along x, y or z. A required point is served when a run of its system touches it and connects, piece touching piece, back to that system's source. It checks coordination and modelling practice, never codes, sizes, slopes, clearances or engineering.

## Not tested yet

- **Owners using rhino-model.** No measured run loaded any Arch Studio skill.
- **Real sessions.** Every measured run used headless documents and a script that ran the rounds, saved, reopened and measured. Several agent sessions on window documents, a person driving rounds, and `save()` have not been run.
- **Recovering from a change in one round.** With the change delivered as a note to the coordinator, who went first that round, no setup recovered in the change round; 2 to 4 rounds where it recovered at all.
- **Agents belonging to different people,** more than four owners, and larger models.

## Out of scope

Agents editing the same file, live sync between sessions, rendering, structural or MEP design, and code compliance.
