# Dispatcher

The entry point for the skills-for-architects plugin system. Two skills:

| Skill | What it does |
|-------|-------------|
| [/architect](skills/architect/) | Smart router — describe your task, get routed to the right agent or skill |
| [/skills](skills/skills-menu/) | Help menu — shows all available skills and agents organized by task |

## Why

The repo has 34 skills and 7 agents. New users shouldn't need to memorize them. `/architect` accepts natural language and figures out the right path. Power users can still call any skill directly by name.

## Install

**Claude Desktop:**

1. Open the **+** menu → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the **Dispatcher** plugin

**Claude Code (terminal):**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 08-dispatcher@skills-for-architects
```

## License

MIT
