---
name: tool-catalog
description: "Show Arch Studio help, available skills, agents and host-specific commands. Use for help, how do I use Arch Studio, what is Norma, or a capability directory."
allowed-tools:
  - Read
---

# tool-catalog

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component’s [declaration](host-contract.json) (`skill:tool-catalog`). Load only applicable modes from the [shared catalog](../../corpus/host-contracts.json); declarations do not grant access or permission. Use the actual host’s [delivery route](../../docs/host-adapters.md).

Provide read-only help for “help”, “how do I use Arch Studio”, “what is Norma”, available skills, agents and commands. Start with the actual delivery channel and known workspace state when relevant; do not run setup just to answer help.

Read the current [component registry](../../corpus/components.json) and [generated practice discovery](../../docs/practice-clusters.md). Select the requested scope and show names, short purposes and actual host-discovered entry points. A directory is generated from maintained metadata, not a second static skill list. For a broad help request give two or three useful next actions; a focused capability question gets a focused answer.

For Arch Studio onboarding or troubleshooting beyond a directory answer, the [Norma support procedure](../norma-support/SKILL.md) owns that support outcome; its presence does not imply an active email service or shared chat history.

Norma coordinates work; direct skill invocation remains valid. A substantial task may benefit from a workplan and approved team; a quick task needs no extra gate. Records require accessible selected workspace files. For workflows explicitly declared harness-native, the host follows the owner's complete procedure using its actual capabilities; no Arch Studio runner or executable installation is required. Report the selected workflow's actual declaration and any unresolved capability gap; do not infer catalog-wide execution support. A hosted connection or a displayed skill alone proves neither file access nor completed work. Optional agent profiles are available only when actual host registration/delegation is observed, including the Norma worker after context and approval are resolved.

This directory procedure has no registered operation IDs or record effects. Read its maintained
metadata through the actual delivery channel and use the [completion contract](../../docs/completion-reporting.md).
Do not invent dispatch operations, run an installer, activate another workflow or perform setup
merely to answer a help question. Report unknown host capabilities as unknown.

For external-source directories use the [source catalog](../../corpus/sources/catalog.json) with geography/topic filtering. Return matching original links, distinguish code sources from related datasets, and state available-manifest coverage. No content retrieval, studio setup or permission is required for listing. Missing LA routes do not substitute NYC. See [moments](../../rules/moments.md) for state facts and the [source contract](../../docs/source-integration-contracts.md) for interpretation boundaries.
