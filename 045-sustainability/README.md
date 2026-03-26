# Sustainability

A Claude Code plugin for embodied carbon and environmental product declarations. Parses EPD PDFs, searches registries for published EPDs, compares products on GWP and other impact metrics, and generates CSI specification language with maximum GWP thresholds.

## The Problem

Embodied carbon is increasingly regulated and incentivized — LEED v4.1 MRc2, Buy Clean policies, and net-zero commitments all require Environmental Product Declarations. But EPDs are dense PDFs with inconsistent formats, scattered across dozens of registries, and the data needs to flow into specifications and whole-building LCA.

## The Solution

Four skills form a pipeline: parse EPD PDFs into structured data, search registries for published EPDs, compare products on environmental impact metrics, and generate CSI specification sections with GWP thresholds.

```
EPD PDFs ──→ /epd-parser ──→ structured data ←── /epd-research ←── registries
                                    │
                             /epd-comparator
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
| [epd-comparator](skills/epd-comparator/) | Side-by-side impact comparison with LEED MRc2 eligibility check |
| [epd-to-spec](skills/epd-to-spec/) | CSI specification sections requiring EPDs and setting GWP limits |

## Output

All skills share a **42-column EPD schema** covering product identity, EPD metadata, impact indicators (GWP-fossil, GWP-biogenic, ODP, AP, EP, POCP), resource use, and LEED eligibility. Data saves to CSV or Google Sheets. Comparison reports and specifications save as markdown.

## Install

```bash
claude install github:AlpacaLabsLLC/skills-for-architects/045-sustainability
```

## License

MIT
