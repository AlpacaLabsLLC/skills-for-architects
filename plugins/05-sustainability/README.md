# Sustainability

A Claude Code plugin for embodied carbon and environmental product declarations. Parses EPD PDFs, searches registries for published EPDs, compares products on GWP and other impact metrics, and generates CSI specification language with maximum GWP thresholds.

## The Problem

Embodied carbon is increasingly regulated and incentivized — LEED v4.1 MRc2, Buy Clean policies, and net-zero commitments all require Environmental Product Declarations. But EPDs are dense PDFs with inconsistent formats, scattered across dozens of registries, and the data needs to flow into specifications and whole-building LCA.

## The Solution

Four skills form a pipeline: parse EPD PDFs into structured data, search registries for published EPDs, compare products on environmental impact metrics, and generate CSI specification sections with GWP thresholds.

```
EPD PDFs ──→ /epd-parser ──→ structured data ←── /epd-research ←── registries
                                    │
                             /epd-compare
                                    │
                          comparison report
                                    │
                              /epd-to-spec
                                    │
                         CSI spec sections
```

Each skill works standalone. Chaining is natural but not required.

## Skills

| Skill | Description |
|-------|-------------|
| [epd-parser](skills/epd-parser/) | Extract structured data from EPD PDFs — GWP, life cycle stages, certifications |
| [epd-research](skills/epd-research/) | Search EC3, UL, Environdec, and manufacturer sites for EPDs by material |
| [epd-compare](skills/epd-compare/) | Side-by-side impact comparison with LEED MRc2 eligibility check |
| [epd-to-spec](skills/epd-to-spec/) | CSI specification sections requiring EPDs and setting GWP limits |

## Output

All skills share a **42-column EPD schema** covering product identity, EPD metadata, impact indicators (GWP-fossil, GWP-biogenic, ODP, AP, EP, POCP), resource use, and LEED eligibility. Data saves to CSV or Google Sheets. Comparison reports and specifications save as markdown.

## Install

**Claude Desktop:**

1. Open the **+** menu → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the **Sustainability** plugin

**Claude Code (terminal):**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 05-sustainability@skills-for-architects
```

**Manual:**

```bash
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/05-sustainability/skills/epd-parser ~/.claude/skills/epd-parser
```

## License

MIT
