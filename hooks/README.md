# Hooks

Hooks are event-driven automations that run automatically during Codex or Claude Code sessions. Unlike skills (invoked manually) and rules (reference documents), hooks fire on lifecycle events — at session start or after a file is written or edited.

## Available Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| [session-start-ambient](./session-start-ambient.sh) | Codex `SessionStart` (runs once you trust it) | Adds compact Arch Studio routing context to root sessions without reading or writing state |
| [session-start-welcome](./session-start-welcome.sh) | Every session start | Shows a short message pointing to `/as:start`, and the session line; writes nothing |
| [as-rhino-context](./as-rhino-context.sh) | Claude Code `SessionStart` (startup, resume, clear, compact) | Adds one line pointing to the Rhino skill index with this installed version's path |
| [post-write-disclaimer-check](./post-write-disclaimer-check.sh) | After Write or Edit | Flags a regulatory output (zoning, occupancy, code analysis) that is missing the professional disclaimer |
| [version-check](./version-check.sh) | Enabled session startup, at most daily | Checks for a newer release and notifies once per version |

## Installation

None. Claude Code hooks ship via [`hooks.json`](./hooks.json); the Codex-only ambient hook ships via [`codex-hooks.json`](./codex-hooks.json). Both register with their respective plugin package when enabled.

```bash
claude plugin install as@skills-for-architects
```

Run `/hooks` in Claude Code to confirm they're loaded. Disable them by disabling the plugin, or per-session via `/hooks`.

> Versions ≤ 1.1.3 distributed these hooks as a `settings-snippet.json` requiring a manual merge into `~/.claude/settings.json`. If you did that merge, remove those entries — the plugin now registers the same hooks itself, and the old entries point at a path that no longer exists.

## Behavior

The Claude Code hooks surface their output so Claude actually receives it (stderr with exit 0 is shown to no one in Claude Code):

- **session-start-welcome** (SessionStart, every new session) checks the required plugin files, then emits a short visible message, "Arch Studio: run /as:start to see what it can do, or describe your architecture or firm work.", and the session line from `rules/moments.md`. It writes nothing and does not rewrite the user's first response. With a plugin file missing, the message says discovery is incomplete instead.
- **as-rhino-context** (SessionStart) is plain `sh` with `tr` and `sed`, because the Rhino AI panel has no `node`, passes a broken Python environment on macOS, and a Windows PC may have no Python at all. It emits one short `additionalContext` line naming `skills/as-rhino-index.md`, which the model reads by path with `run_python` only when the user names an as-rhino skill or Arch Studio in Rhino. It never blocks; any problem means no output and exit 0.
- **post-write-disclaimer-check** (PostToolUse) emits JSON `{"decision": "block", "reason": …}` on stdout on findings, which surfaces the reason to Claude so it restores the disclaimer block.
- **version-check** (SessionStart) is on by default. The first session seeds a private local cache silently. Later sessions make at most one two-second request per 24 hours, fail silently, and notify once for each newer version. The same request carries the anonymous usage ping (a random local install ID and the plugin version). Disable the update notice with `AS_UPDATE_CHECK_DISABLED=1` or `/as:studio updates disable`; disable the ping with `AS_TELEMETRY_DISABLED=1`. With both off the hook does no filesystem or network work.

The deterministic preference helper lives with the owning `/as:studio` skill; it is not a hook.

To downgrade the disclaimer hook to advisory-only, replace its JSON emission with a plain `exit 0` at the finding point in the script (the finding then goes unseen).

### post-write-disclaimer-check

Checks written or edited `.md` files for the `<!-- architecture-studio:requires-disclaimer -->` marker that regulatory skills emit. If the marker is present but the canonical disclaimer block is missing (or the marker appears more than once), it emits a `block` decision telling Claude to restore the block from `rules/professional-disclaimer.md`. Marker-driven — silent on files without the marker. Edit provides no full content in its tool input, so the hook always reads the file from disk.


## Customization

Each `.sh` script is a standalone sh or bash file, portable across macOS (BSD sed/grep), Linux and Git Bash on Windows, with no Python, node or jq required. `hooks.json` runs each one through `sh` or `bash` on its quoted path. Claude Code runs hook commands with `sh -c` on macOS and Linux and with Git Bash on Windows, or with PowerShell when Git Bash isn't installed ([hooks reference](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form)); without Git for Windows these hooks don't run, and Claude Code reports them as non-blocking errors. Edit to fit your workflow:

- Downgrade enforcement to advisory: replace the JSON `block` output with `exit 0`
