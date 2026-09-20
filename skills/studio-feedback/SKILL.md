---
name: studio-feedback
description: "Prepare a user-reviewed Arch Studio bug report or feature request for GitHub. Use when the user runs /as:studio-feedback, says \"report a bug\", \"this skill broke\", \"send feedback\", or requests a feature. Do not use for Claude Code's native /feedback command."
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
---

# /as:studio-feedback — Prepare a GitHub report

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:studio-feedback`). Load only its referenced mode profiles from the [shared catalog](../../corpus/host-contracts.json). Compose modes required by the actual task; declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
> Host adapter: read [delivery-specific guidance](../../docs/host-adapters.md) for invocation, metadata access, questions and browser opening.

This native report-preparation procedure has no registered operation IDs. Its steps below are
the complete owner; no Arch Studio runner, installer, executable download or reconstructed helper
is required. An ordinary native encoding or metadata tool may be used where available. Follow the
[completion contract](../../docs/completion-reporting.md) and distinguish a prepared draft, an opened URL and a submitted issue.

Prepare a report locally, show exactly what would leave the machine, and open GitHub only after one informed confirmation. Never submit the issue, post a comment, call the GitHub API, or transmit diagnostics in the background.

## 1. Choose the report type

Infer `bug` or `feature` when the request is clear. Otherwise use one `AskUserQuestion` gate to choose the type; do not first ask the same question in prose.

Use these issue forms and labels:

- Bug: `bug-report.yml`, label `bug`; fields `version`, `os`, `skill`, `what-happened`, `expected`.
- Feature: `feature-request.yml`, label `enhancement`; fields `version`, `skill`, `problem`, `proposal`.

## 2. Prepare minimal fields locally

For MCP, use the actual delivered release version and digest when present; a connection does not imply a local plugin path. For an installed plugin, read its actual `.codex-plugin/plugin.json` on Codex or `.claude-plugin/plugin.json` on Claude Code through the host's known package location. Gather only the operating-system name/version through available native host metadata or a bounded local command. Process access is optional and depends on that method. If metadata is unavailable, say unknown rather than searching unrelated files, installing tools or inventing it. Infer the affected skill from the conversation when reliable; otherwise leave it blank or ask during editing.

Draft the report from the user's words, but do not automatically include raw conversation history, files, stack traces, environment variables, or command output. Before showing the draft, remove or visibly flag:

- client and project names;
- street and project addresses;
- home-directory paths and usernames;
- email addresses and phone numbers;
- likely secrets, tokens, keys, cookies, and credentials; and
- proprietary document contents.

When uncertain, omit the value and mark where the user can add a safe description. Never invent reproduction details.

## 3. Show the exact outbound values

Present every proposed query field verbatim in one fenced text block. Explain immediately before the gate:

> Opening GitHub sends the displayed fields immediately as URL query parameters, and the URL may remain in browser history. GitHub receives them before issue submission; closing the tab does not undo that transmission. Arch Studio will not submit the issue.

Use a **single confirmation gate** with these outcomes:

1. Open the prefilled GitHub issue.
2. Edit the fields first.
3. Cancel without opening GitHub.

Do not ask for confirmation in prose and then repeat it with `AskUserQuestion`. Editing returns to the same preview and gate. Cancel ends with no browser action or network request.

## 4. Encode and open only after confirmation

Build the URL from `https://github.com/AlpacaLabsLLC/skills-for-architects/issues/new`, the selected `template`, title, label, and the form field IDs above. Encode each query value independently as UTF-8 percent encoding: retain only ASCII letters/digits and `-._~`, encode every other byte as `%HH`, then join key/value pairs with `&`. A native URL API or ordinary task-specific code may do this. Decode each encoded value locally and compare it with the exact approved text before opening; do not double-encode or interpolate report text into shell code. No particular encoding executable is required.

Keep the final URL at or below **6,000 characters**. Reduce only the narrative fields, state visibly that they were shortened for the URL, and retain the complete draft locally in the conversation for optional manual pasting. Never shorten version, operating system, or affected skill.

If shortening or any other edit changes a displayed value after confirmation, return the exact
revised outbound values to the same preview and informed gate before opening. Earlier approval
does not cover a changed payload. Prefer doing encoding and length checks locally before the gate
so the user reviews the final values once.

After the confirmed URL is built:

- Use an actually available native browser-opening capability for the exact approved URL; safely pass it as data. On macOS an available `open` command is one possible method.
- If no browser-opening capability is available, print the exact URL and label it not opened; do not install a browser helper or claim transmission occurred.

Only after observing the browser action, say: "GitHub is open with the displayed fields. Review and edit the issue before choosing Submit on GitHub."

## Hard boundaries

- Never submit the issue or use `gh issue create`.
- Never open GitHub before the exact-value preview and informed gate.
- Never claim that closing an opened tab means nothing was transmitted.
- Never treat feedback as telemetry or send it to ALPA infrastructure.
- Never add project files, conversation transcripts, or attachments automatically.
