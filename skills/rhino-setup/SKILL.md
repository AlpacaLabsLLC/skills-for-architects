---
name: rhino-setup
description: "Connect and verify Rhino 9 for the rhino cluster, from its AI panel or a connected agent: detect Rhino's tools, confirm an open document and its units, and run a one-object smoke test. Use when the user asks to connect Rhino, or when another rhino skill finds the Rhino tools missing. Guides the user; never installs or registers anything."
---

# /as:rhino-setup

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:rhino-setup`) and the mode profiles it references in the [shared catalog](../../corpus/host-contracts.json). Declarations are requirements, not proof of access or permission.

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation.

## Outcome

A confirmed working connection (tools present, a document open, units known, a script round-trip proven) or the exact user action that is missing.

## Procedure

1. **Tools.** Look for Rhino's tools (`run_python`, `get_context`), from the AI panel or a connected agent. If absent, stop and give the user this action: "Open a document in Rhino 9 and make this request in its AI panel. To use an agent outside Rhino, such as Claude Code in a terminal, run `MCPConnect` once in Rhino 9 and install it for your agent, then run `MCPStart` on the open model and start a new agent session." Arch Studio never installs, registers or configures anything.
   Also note whether the hosted Arch Studio MCP is connected too: its workflow tools are named `as_*` and come from an MCP server other than Rhino's (in Claude Code, `mcp__<server>__as_...`). Only the tool list says this; do not call those tools and do not compare versions.
2. **Document.** `get_context` must answer with the open document. Then one `run_python` script reads `__rhino_doc__`, `Rhino.RhinoApp.Version` and `sys.platform`: Rhino version, operating system (`darwin` is macOS, `win32` is Windows), units, name, path, live object count, top-level layers. If the version is below 9, report that the skills are written for Rhino 9. These values hold for this turn only; a later turn reads them again.
3. **Smoke test** only when the user asked to verify: add one named point on a layer `Rhino Setup Check`, read it back, delete it and the layer, and report both steps. Never touch other objects. Run this script as written in one `run_python` call; it is tested in Rhino 9 and keeps a `Rhino Setup Check` layer that existed before. Layer calls with one string argument (`Layer(name)`, `Layers.Add(name)`, `Layers.FindByFullPath(name)`) fail there with "No overload".

```python
import Rhino
d = __rhino_doc__
NAME = "Rhino Setup Check"
made = d.Layers.FindByFullPath(NAME, -1) < 0
if made:
    layer = Rhino.DocObjects.Layer()
    layer.Name = NAME
    d.Layers.Add(layer)
index = d.Layers.FindByFullPath(NAME, -1)
attr = Rhino.DocObjects.ObjectAttributes()
attr.LayerIndex = index
attr.Name = "rhino-setup check point"
gid = d.Objects.AddPoint(Rhino.Geometry.Point3d(0, 0, 0), attr)
obj = d.Objects.FindId(gid)
print("added:", obj is not None and obj.Attributes.Name == attr.Name and obj.Attributes.LayerIndex == index)
print("point deleted:", d.Objects.Delete(gid, True))
print("layer deleted:" if made else "layer kept, it existed before:", d.Layers.Delete(index, True) if made else NAME)
```

## Report

Tools found or not, Rhino version and operating system, document name or "untitled", units, object count, smoke-test result, and the next user action if anything is missing. On Windows, only when your context has no Arch Studio startup line (the line naming `as-rhino-index.md` and the lessons folder), tell the user to install Git for Windows and start a new panel session: Claude Code runs the plugin's startup hook in Git Bash. When that line is there, the hook ran: say nothing about Git for Windows, the startup line or pointing to the index. Complete under the [completion contract](../../docs/completion-reporting.md). If the hosted Arch Studio MCP is also connected, add this line: "The hosted Arch Studio MCP is also connected; use the Arch Studio plugin or the MCP, not both (README, Two editions)."
