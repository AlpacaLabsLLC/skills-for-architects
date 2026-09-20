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

## Steps

1. Resolve the owning project and current document vocabulary/path template. Confirm only missing coordinates and source evidence; preserve authorization already covering the record.
2. Extract recipient, actual sent date, files, purpose and method from the request/evidence. Refer to registered document IDs where available. Mark unverified paths and unknown facts explicitly.
3. Prepare the transmittal text below. Follow the shared document contract to resolve placement and register the authored file as `kind: transmittal`, retaining provenance and the allocated permanent document ID. Use available host tools for the write; no Arch Studio runner or package is required. Do not create a second numbering authority or fixed folder.
4. Reopen the registered file and report its actual path/ID and recorded delivery evidence. A registered report does not prove an email was sent.

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
