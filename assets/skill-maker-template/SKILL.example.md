---
name: transmittal
description: Log an outgoing transmittal — turn a list of files and a recipient into a numbered record of what was sent, to whom, when, and why. Use when the user asks to record a transmittal, log an issuance, or says "we sent the drawings to the contractor".
allowed-tools:
  - Read
  - Write
  - Glob
---

# Transmittal Records

<!-- architecture-studio:harness-compatibility -->
> Invoke as $transmittal on Codex or /transmittal on Claude Code. Use equivalent native tools when host tool names differ.

Record what the user confirms was sent, with its actual delivery evidence. This custom skill writes a transmittal document through the current Arch Studio document model; it sends no messages. Before a durable write, retrieve the applicable Arch Studio workspace contract and the receive workflow's document-registration contract, then perform the registration with the tools available in this host.

## Usage

```
$transmittal sent the 50% CD set to the structural engineer for review
/transmittal sent the 50% CD set to the structural engineer for review
/transmittal issued A-101 through A-110 to the GC via file share
```

## Outcome and evidence

Produce a transmittal in the owning project from the user's confirmed delivery evidence. Record recipient, actual sent date, files, purpose and method; refer to registered document IDs where available. Mark missing facts unknown, and do not infer that a registered report proves a message was sent.

Follow the shared document contract to allocate the permanent ID, register the file as `kind: transmittal` and verify the actual destination. Preserve existing authorization, provenance and unrelated records. Report the registered path/ID and the delivery evidence. Use the host's available tools; no Arch Studio runner is required.

## Output format

```markdown
# Transmittal — {recipient role or firm}

- **Date:** {YYYY-MM-DD}
- **To:** {recipient role or firm}
- **Via:** {email | file share | courier | not recorded}
- **Purpose:** {for review | for record | for construction | not recorded}

| # | File | Description |
|---|------|-------------|
| 1 | {filename} | {one line} |

Notes: {anything else worth keeping, or omit the line}
```
