---
name: rhino-setup
description: "Connect and verify Rhino 9 and its AI panel for the rhino cluster: detect the panel's Rhino tools, confirm an open document and its units, and run a one-object smoke test. Use when the user asks to connect Rhino, or when another rhino skill finds the Rhino tools missing. Guides the user; never installs or registers anything."
---

# /as:rhino-setup

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-setup`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation.

## Outcome

A confirmed working connection (tools present, a document open, units known, a script round-trip proven) or the exact user action that is missing.

## Procedure

1. **Tools.** Look for the Rhino AI panel's tools (`run_python`, `get_context`). If absent, stop and give the user this action: "Open a document in Rhino 9, open its AI panel, and make this request there." Arch Studio never installs, registers or configures anything.
2. **Document.** `get_context` must answer with the open document. Then one `run_python` script reads `__rhino_doc__` and `Rhino.RhinoApp.Version`: Rhino version, units, name, path, live object count, top-level layers. If the version is below 9, report that the skills are written for Rhino 9.
3. **Smoke test** only when the user asked to verify: add one named point on a layer `Rhino Setup Check`, read it back, delete it and the layer, and report both steps. Never touch other objects.

## Report

Tools found or not, Rhino version, document name or "untitled", units, object count, smoke-test result, and the next user action if anything is missing. Complete under the [completion contract](../../docs/completion-reporting.md).
