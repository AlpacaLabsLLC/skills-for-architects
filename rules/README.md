# Rules

Rules are always-on conventions that shape every skill output. Unlike skills (invoked with a slash command), rules are loaded automatically and apply across all plugins.

| Rule | What it governs |
|------|-----------------|
| [units-and-measurements](./units-and-measurements.md) | Imperial/metric defaults, area types (GSF/USF/RSF), dimension formatting |
| [code-citations](./code-citations.md) | Building code references — edition years, section symbols, jurisdiction awareness |
| [professional-disclaimer](./professional-disclaimer.md) | Disclaimer language, what AI outputs can and cannot claim |
| [csi-formatting](./csi-formatting.md) | MasterFormat 2018 section numbers, three-part structure, cross-references |
| [terminology](./terminology.md) | AEC standard terms, abbreviation conventions, material names |
| [output-formatting](./output-formatting.md) | Tables, headings, source attribution, file naming, list structure |
| [transparency](./transparency.md) | Show your work — link sources, expose inputs, make outputs verifiable |

## How Rules Work

When you install a plugin from this repository, its skills follow these rules automatically. The rules are reference documents — Claude reads them to maintain consistency across all outputs.

Rules are not invoked directly. They inform how skills produce their outputs.
