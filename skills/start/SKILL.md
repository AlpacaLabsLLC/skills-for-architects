---
name: start
description: "Show the Arch Studio card: logotype, installed release, a short setup checklist, what Arch Studio is, how to use it, a tour of the practice areas and prompts to try. Use for start, welcome, connect, is Arch Studio installed or working, or how do I begin. Read-only: runs no task and changes nothing."
allowed-tools:
  - Read
  - Glob
---

# /as:start

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:start`). Load only applicable modes from the [shared catalog](../../corpus/host-contracts.json); declarations do not grant access or permission. Use the actual host's [delivery route](../../docs/host-adapters.md). This skill only reads: it never runs setup, connects anything, installs a server or writes a file.

The card is the plugin's version of the hosted Arch Studio MCP's `as_connect` welcome, as text. If you received these instructions through the hosted Arch Studio MCP rather than from the installed plugin's folder, call `as_connect` instead and follow its result: this card describes the plugin. Otherwise print the card in this order, as one reply, then wait for the user.

## 1. Logotype and release

Print this logotype exactly as given, in a fenced code block with no language, every character and space unchanged:

```
   ##+             +##     +++                                                     +#+                   ##+++
  ####             +##     +#+ ##+                  ##                            ### ###                ##+##+
  ####+   ++#  +###+####+  +#++####   +##++   ++##+#####+##  +#  ++#  +###+       ##++####++#+ +#+  +######++#   +###+
 +##+##  ####+#####+######+###+####+#######+ #####+####++##  ##+####+#######      ##++####+### ### ########+##++#######+
 ######+ ##+ ###    ##  ##+### ###  ##+##+  +##     ##  +##  ##+##+ ###+##+       ##+ ###  ##+ ######    ##+##+##+   +##
+####### ##+ +###+++##  ##+### ####+#######+ ###+++ ####+######+##+  #######+    ###  +###+####### ###++### ##++###+###+
##+   ##+##    +###+##  ##++#+  +##+ +####+   +###+  +##  +####+##+   +####+     #+    +##+ +#####  +####+  ##+  +###+
```

Then one line: `Release <version>`, where the version is `version` in the installed plugin's `.claude-plugin/plugin.json` (Claude Code) or `.codex-plugin/plugin.json` (Codex), two folders above this file. If neither can be read, write `Release unknown`; never guess one.

## 2. Checklist

Bold title **Arch Studio check**, then one line per item, ✅ when observed and ⬜ when not. Decide each line only from what you can see in this session: your own tool list and files you can read. Never call a tool or open a connection to find out. When you cannot tell, say "not checked".

- **Plugin:** ✅ Arch Studio plugin installed (you are reading this file from it).
- **Studio:** walk up from the current working folder to the nearest `STUDIO.md` (as in the [context resolution](../project/references/context-resolution.md)). Found: ✅ Studio set up: `<studio name or folder>`. Not found: ⬜ No studio here. Optional; run `/as:studio` to set one up. A missing studio is not a fault: every skill works without one.
- **Rhino 9:** Rhino's tools (`run_python`, `get_context`) in your tool list: ✅ Rhino 9 connected. Absent: ⬜ Rhino not connected. Only for the Rhino skills; see `/as:rhino-setup`.
- **Norma index:** the Norma index MCP's tools (`search_products`, `get_product`, `show_products`, `get_brand`) in your tool list: ✅ Norma index connected, for product search in the FF&E skills. Absent: ⬜ Norma index not connected. Optional, no login: [normaindex.com](https://normaindex.com); in Claude Code, `claude mcp add --transport http norma https://mcp.normaindex.com` (add `--scope user` for every project); in Claude or ChatGPT, add `https://mcp.normaindex.com` as a custom connector.
- **Hosted MCP:** only if the hosted Arch Studio MCP's tools (named `as_*`, from a server other than Rhino's) are in your tool list, add: The hosted Arch Studio MCP is also connected; use the Arch Studio plugin or the MCP, not both.

## 3. Welcome sections

One bold heading per section, the text as given, lists as bullets, and each **Say:** line as written. Do not add claims.

1. **What it is**
   Arch Studio gives Claude Code or Codex an architecture office’s skills, tools and references. Your firm adds its own standards, procedures and project records, and decides what the assistant can access.
   A framework with four connected pillars:
   - Studio — How your firm sets up and assures the work.
   - Knowledge — What the work draws on.
   - Tooling — How operations are performed or coordinated.
   - Memory — What carries forward.
   Say: **"What can Arch Studio do?"**
2. **How to use it**
   - Describe the work in plain words, or name a skill: `/as:<skill>` in Claude Code, `$<skill>` in Codex
   - For a larger job, `workplan` shows the steps, skills and outputs before anything runs
   - Run `/as:start` anytime to see this card again
   Say: **"Help me plan a furniture schedule for a small office"**
3. **Take a tour**
   `<n>` practice areas. Open one to see its skills, sources and handoffs; nothing runs.
   One bullet per practice area, read from the bundled `clusters/*.json` (two folders above this file): its `name`, then in parentheses the number of its `members` that start with `skill:` (only those are skills), and the prompt "Show me the `<name>` practice area". List `Materials & FF&E` first, then the rest in file-name order. `<n>` is the number of cluster files.
4. **Start building**
   Turn something your office always does the same way into your own skill, written together and saved in your studio or project folder.
   Say: **"Build my first skill"** (runs `/as:skill-maker`)
5. **Your data**
   - Arch Studio runs inside your own Claude Code or Codex session; your AI provider's data controls apply
   - The plugin does not upload or store studio, project or module records on Arch Studio servers
   - Research skills contact the public sources named in their documentation when you run them
   - In Claude Code, the update check makes one request a day at most, with an anonymous usage ping; `AS_TELEMETRY_DISABLED=1` turns the ping off ([README](../../README.md#data-privacy-and-telemetry))

## 4. Footer

Last line, small: `Release <version> · © 2026 Alpaca Labs, LLC · https://alpa.llc`

## After the card

When the user picks a prompt, hand it to the skill that owns it: "What can Arch Studio do?" and a practice-area tour to [tool-catalog](../tool-catalog/SKILL.md), "Build my first skill" to [skill-maker](../skill-maker/SKILL.md), setup questions to [support](../support/SKILL.md), studio setup to [studio](../studio/SKILL.md). Don't start a task until the user chooses one.

Report under the [completion contract](../../docs/completion-reporting.md): the card is instructions delivered and facts observed, not a completed workflow.
