# /product-match

Find visually or functionally similar products from an image, name, or description. for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../../LICENSE)

## Install

```bash
# Via plugin system
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 06-materials-research@skills-for-architects

# Or symlink just this skill
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/06-materials-research/skills/product-match ~/.claude/skills/product-match
```

## Usage

```
/product-match
```

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition and implementation |

## License

MIT
