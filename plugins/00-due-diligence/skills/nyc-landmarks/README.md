# /nyc-landmarks

LPC landmark and historic district check for any NYC building as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill. Provide an address, BBL, or BIN and find out if the property is individually landmarked, in a historic district, or not designated — using the LPC Individual Landmark & Historic District Building Database. No API key required.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../../LICENSE)

## Install

```bash
# Via plugin system
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 00-due-diligence@skills-for-architects

# Or symlink just this skill
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/00-due-diligence/skills/nyc-landmarks ~/.claude/skills/nyc-landmarks
```

## Usage

```
/nyc-landmarks 120 Broadway, Manhattan
/nyc-landmarks 1000770001          (BBL)
/nyc-landmarks 1001389             (BIN)
```

The skill:

1. **Resolves the property** via PLUTO — gets BBL, BIN, and building metadata
2. **Queries the LPC database** — checks for individual landmark designation by BIN, with BBL fallback
3. **Cross-checks PLUTO** — the `histdist` field catches historic district membership even when the building isn't individually listed
4. **Presents the result** — designation status, LP number, architect, style, historic district, and implications for permit work

## Data Sources

| Source | Dataset ID | What it provides |
|--------|-----------|-----------------|
| PLUTO | `64uk-42ks` | Address resolution, BBL/BIN, `histdist` field |
| LPC Individual Landmark & Historic District Building Database | `7mgd-s57w` | Landmark name, LP number, designation date, type, style, architect, historic district |

## Output

Inline markdown with landmark status (Landmarked / In Historic District / Not Designated), designation details table, and a note on LPC Certificate of Appropriateness requirements if designated.

## License

MIT
