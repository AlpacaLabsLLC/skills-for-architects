# /as:rhino-agent-team

Several agents on one Rhino 9 model: one file per owner, a set-out the coordinator writes before anyone builds and reissues on every change, notes in the model, and a check across the files each round. Each owner builds with [rhino-model](../rhino-model/SKILL.md). It starts by asking whether one agent would do. See [SKILL.md](SKILL.md), the [protocol](references/protocol.md) and the [evidence](references/evidence.md).

## Running the team in Orca (or any IDE terminal host)

The agents are ordinary Claude Code sessions, one per owner plus the coordinator, each in its own terminal. Orca, or any IDE that runs terminals, only hosts those terminals; it adds no agent features, and nothing in the skill depends on it.

**Per-project MCP config.** Start each session in its own folder, with the Arch Studio plugin installed and the Rhino connection in that folder's `.mcp.json`:

```json
{"mcpServers": {"rhino": {"type": "stdio", "command": "<router>", "args": [], "env": {"RHINO_MCP_DEFAULT_VERSION": "9"}}}}
```

`<router>` is Rhino 9's MCP router: `~/Library/Application Support/McNeel/Rhinoceros/ai/bin/rhino-mcp-router` on macOS (write the full path), `%APPDATA%\McNeel\Rhinoceros\ai\bin\rhino-mcp-router.exe` on Windows (see the [README](../../README.md#rhino-9)). Each session works only in its own owner file (`summary()`, then the team check on the shared folder).

**Setup notes (macOS, from two Orca runs; an Orca update stopped the first after one round):**

- **Launch Rhino 9 with the user temp folder and without window restoration:** `open --env TMPDIR=$(getconf DARWIN_USER_TEMP_DIR) -a "/Applications/Rhino 9.app" --args -ApplePersistenceIgnoreState YES`. Rhino opens its script pipe in `$TMPDIR`; from a shell whose `TMPDIR` points elsewhere, the pipe is not where the tools look. Restored or autosaved windows change what is open.
- **Update prompt:** if Rhino shows "Software Update", click **Remind Me Later** before the run, so the installed build stays the same through the team session.
- **Orca stall after `orca open`:** Orca's runtime can stop answering for 1–2 minutes before it is ready. Wait until `orca status --json` shows `runtime.state: ready` before starting the sessions. Orca also has no switch to stop app updates; set its update delay to the longest before a long session, since an update restarts it mid-round.

**What is tested.** One complete run in Orca, five Sonnet owners and a coordinator over five rounds with a change in round 3, was stable but did not settle ([evidence](references/evidence.md), test 4). It was free of clashes and every point was served from round 4, but one note stayed open: an owner never re-stamped its four opening requests after the change. `stamp()` now re-stamps them. Those sessions used the evaluation harness's own tool server and headless documents, not the Rhino connection above, which has not been run in Orca.
