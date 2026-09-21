# Tooling catalog

Architecture Studio skills install together in one flat catalog so every workflow can be invoked directly. The links below use Claude Code's `/as:<skill>` namespace; Codex invokes the same installed skills as `$<skill>`. These groups describe what the tools do; they are not separate plugins or installation packages.

## Firm operations

| Skill | Description |
|-------|-------------|
| [`/as:studio`](./studio) | Set up and inspect the studio, route work, and create projects |
| [`/as:tool-catalog`](./tool-catalog) | Show the available skills and agents |
| [`/as:learn`](./learn) | Guided, resumable introduction to Codex and Claude Code for architects (use `$learn` on Codex) |
| [`/as:skill-maker`](./skill-maker) | Create studio-wide or project-specific procedures outside the plugin cache |
| [`/as:studio-feedback`](./studio-feedback) | Prepare a reviewed bug report or feature request without automatic submission |

## Project management

### Project Records

Project records form a linked graph of plain files. `/as:project` is the setup and memory interface: `PROJECT.md` owns sourced facts and `decisions/` owns durable reasoning. Meetings and site reports preserve source context, the canonically resolved project or studio `TASKS.md` owns action history, work plans read those records, and `TIMELOG.md` records only user-confirmed durations.

| Skill | Description |
|-------|-------------|
| [`/as:project`](./project) | Initialize a project, maintain sourced facts, and manage durable decisions |
| [`/as:workplan`](./workplan) | Plan repository, operational, or AEC delivery work before acting |
| [`/as:meeting-minutes`](./meeting-minutes) | Create source-linked meeting records with explicit promotion handoffs |
| [`/as:site-visit-report`](./site-visit-report) | Record field observations, reported information, limitations, and follow-up candidates |
| [`/as:tasklist`](./tasklist) | Maintain project tasks or an opted-in studio portfolio register |
| [`/as:timetracker`](./timetracker) | Reconstruct activity and append only user-confirmed time |
| [`/as:proposal`](./proposal) | Maintain project-local proposals with protected issued terms and flexible lifecycle records |
| [`/as:agreement`](./agreement) | Maintain sourced agreement context and check work against its scope |
| [`/as:invoice`](./invoice) | Record user-directed invoices with cap warnings and gap detection |

### Professional practice knowledge

| Skill | Description |
|-------|-------------|
| [`/as:architecture-knowledge`](./architecture-knowledge) | Source-backed US practice terminology: “What is a CD set?”, AIA relationships, and CSI/NCS context |

## Practice and design

### Due diligence

| Skill | Description |
|-------|-------------|
| [`/as:nyc-landmarks`](./nyc-landmarks) | LPC landmark and historic district check |
| [`/as:nyc-dob-permits`](./nyc-dob-permits) | DOB permit and filing history |
| [`/as:nyc-dob-violations`](./nyc-dob-violations) | DOB and ECB violations |
| [`/as:nyc-acris`](./nyc-acris) | ACRIS property transaction records |
| [`/as:nyc-hpd`](./nyc-hpd) | HPD violations, complaints, and registration |
| [`/as:nyc-bsa`](./nyc-bsa) | BSA variances and special permits |
| [`/as:nyc-property-report`](./nyc-property-report) | Combined NYC property report |

### Site and zoning

| Skill | Description |
|-------|-------------|
| [`/as:environmental-analysis`](./environmental-analysis) | Climate, wind, sun, flood, seismic, and soil research |
| [`/as:mobility-analysis`](./mobility-analysis) | Transit, walkability, cycling, and pedestrian infrastructure |
| [`/as:demographics-analysis`](./demographics-analysis) | Population, income, age, housing, and employment |
| [`/as:site-history`](./site-history) | Neighborhood context, landmarks, activity, and planned development |
| [`/as:zoning-analysis-nyc`](./zoning-analysis-nyc) | NYC FAR, height, setback, and use analysis |
| [`/as:zoning-envelope`](./zoning-envelope) | Self-contained interactive 3D zoning envelope |

### Programming and specifications

| Skill | Description |
|-------|-------------|
| [`/as:workplace-programmer`](./workplace-programmer) | Workplace programs from headcount and work style |
| [`/as:occupancy-calculator`](./occupancy-calculator) | IBC occupancy loads, egress, exits, and plumbing fixtures |
| [`/as:spec-writer`](./spec-writer) | CSI outline specifications with review markers |

### Sustainability

| Skill | Description |
|-------|-------------|
| [`/as:epd-parser`](./epd-parser) | Extract environmental data from EPD PDFs |
| [`/as:epd-research`](./epd-research) | Research EPD registries by material or category |
| [`/as:epd-compare`](./epd-compare) | Compare environmental impacts and LEED eligibility |
| [`/as:epd-to-spec`](./epd-to-spec) | Generate CSI language with EPD requirements and GWP thresholds |

### FF&E and materials

Explicitly adopted FF&E schedules use immutable item/schedule records; workbooks are pinned views. The optional reusable library remains `product-library.csv`; optional EPD persistence uses `epd-library.csv`. See [record ownership](../studio/ffe/README.md) and [`schema/`](../schema).

| Skill | Description |
|-------|-------------|
| [`/as:master-schedule`](./master-schedule) | Adopt/revise/reconcile schedules or manage the optional product library |
| [`/as:product-research`](./product-research) | Find products from a design brief |
| [`/as:product-spec-bulk-fetch`](./product-spec-bulk-fetch) | Extract specifications from product URLs at scale |
| [`/as:product-spec-pdf-parser`](./product-spec-pdf-parser) | Extract specifications from catalogs, price books, and sheets |
| [`/as:product-data-cleanup`](./product-data-cleanup) | Normalize product categories, dimensions, materials, and language |
| [`/as:product-data-import`](./product-data-import) | Turn product lists into formatted FF&E schedules |
| [`/as:product-enrich`](./product-enrich) | Tag products with categories, colors, materials, and styles |
| [`/as:product-match`](./product-match) | Find similar products from an image, name, or description |
| [`/as:product-pair`](./product-pair) | Suggest complementary products |
| [`/as:product-image-processor`](./product-image-processor) | Download, resize, and remove product-image backgrounds |
| [`/as:product-audit`](./product-audit) | Review fresh or saved product evidence, discrepancies and unknowns |
| [`/as:product-cut-sheet`](./product-cut-sheet) | Prepare one revision-pinned cut sheet using shared templates and host production |
| [`/as:spec-book`](./spec-book) | Assemble a complete ordered specification package with itemized receipts |
| [`/as:csv-to-sif`](./csv-to-sif) | Convert canonical product CSV to SIF |
| [`/as:sif-to-csv`](./sif-to-csv) | Convert SIF into the canonical product CSV schema |

### Presentations

| Skill | Description |
|-------|-------------|
| [`/as:slide-deck-generator`](./slide-deck-generator) | Create self-contained HTML slide decks |
| [`/as:color-palette-generator`](./color-palette-generator) | Create palettes with WCAG contrast checks |
| [`/as:resize-images`](./resize-images) | Resize images for web, social, slides, and print |

## Individual skill documentation

### Code & Regulatory

Bounded reference lookup; source-specific rights, edition and retrieval limits apply.

| Skill | Primary output |
|---|---|
| [`/as:nyc-building-code`](./nyc-building-code) | Building-code provision evidence |
| [`/as:nyc-existing-building-code`](./nyc-existing-building-code) | Existing-building provision evidence |
| [`/as:nyc-plumbing-code`](./nyc-plumbing-code) | Plumbing provision evidence |
| [`/as:nyc-mechanical-code`](./nyc-mechanical-code) | Mechanical provision evidence |
| [`/as:nyc-fuel-gas-code`](./nyc-fuel-gas-code) | Fuel-gas provision evidence |
| [`/as:nyc-construction-administration`](./nyc-construction-administration) | Administrative provision evidence |
| [`/as:nyc-electrical-code`](./nyc-electrical-code) | Electrical provision evidence |
| [`/as:nyc-fire-code`](./nyc-fire-code) | Fire Code provision evidence |
| [`/as:nyc-fdny-rule`](./nyc-fdny-rule) | FDNY rule evidence |
| [`/as:nyc-energy-code`](./nyc-energy-code) | Energy Code provision evidence |
| [`/as:nyc-ll97-applicability`](./nyc-ll97-applicability) | LL97 applicability evidence with unresolved conditions |
| [`/as:nyc-emissions-limit`](./nyc-emissions-limit) | Emissions-limit citation, unit and period |
| [`/as:nyc-zoning-provision`](./nyc-zoning-provision) | Zoning provision evidence |
| [`/as:nyc-housing-maintenance`](./nyc-housing-maintenance) | Housing Maintenance Code provision evidence |
| [`/as:nyc-multiple-dwelling-law`](./nyc-multiple-dwelling-law) | State-owned MDL provision evidence |
| [`/as:nyc-noise-requirement`](./nyc-noise-requirement) | Noise requirement evidence |
| [`/as:nyc-asbestos-requirement`](./nyc-asbestos-requirement) | Asbestos procedural requirement evidence |
| [`/as:nyc-air-emissions-requirement`](./nyc-air-emissions-requirement) | Air-emissions requirement evidence |
| [`/as:nyc-stormwater-requirement`](./nyc-stormwater-requirement) | Stormwater requirement evidence |
| [`/as:nyc-sewer-requirement`](./nyc-sewer-requirement) | Sewer requirement evidence |
| [`/as:nyc-hazardous-material-requirement`](./nyc-hazardous-material-requirement) | Authority-qualified hazardous-material requirement evidence |
| [`/as:nyc-accessibility-requirement`](./nyc-accessibility-requirement) | NYC accessibility provision evidence with separate federal pointer |
| [`/as:ada-requirement`](./ada-requirement) | Federal ADA provision evidence |
| [`/as:nyc-lpc-requirement`](./nyc-lpc-requirement) | LPC requirement evidence |
| [`/as:nyc-sidewalk-requirement`](./nyc-sidewalk-requirement) | Sidewalk requirement evidence |
| [`/as:nyc-curb-cut-requirement`](./nyc-curb-cut-requirement) | Curb-cut requirement evidence |
| [`/as:nyc-plaza-requirement`](./nyc-plaza-requirement) | Program-qualified plaza requirement evidence |
| [`/as:nyc-street-tree-requirement`](./nyc-street-tree-requirement) | Street-tree requirement evidence |
| [`/as:nyc-utility-connection-requirement`](./nyc-utility-connection-requirement) | Water-connection requirement evidence |
| [`/as:nyc-material-requirement`](./nyc-material-requirement) | Application-qualified material requirement evidence |
| [`/as:nyc-interior-finish-requirement`](./nyc-interior-finish-requirement) | Interior wall/ceiling finish requirement evidence |
| [`/as:nyc-floor-finish-requirement`](./nyc-floor-finish-requirement) | Floor-finish requirement evidence |
| [`/as:nyc-furnishing-requirement`](./nyc-furnishing-requirement) | Furnishing requirement evidence |
| [`/as:nyc-drapery-requirement`](./nyc-drapery-requirement) | Drapery requirement evidence |
| [`/as:nyc-local-law`](./nyc-local-law) | Identified Local Law evidence |
| [`/as:nyc-agency-rule`](./nyc-agency-rule) | Identified agency-rule evidence |
| [`/as:nyc-buildings-bulletin`](./nyc-buildings-bulletin) | Buildings Bulletin evidence and document classification |
| [`/as:nyc-code-note`](./nyc-code-note) | Code Note guidance evidence |
| [`/as:nyc-executive-order`](./nyc-executive-order) | Executive-order evidence and scope unknowns |
| [`/as:nyc-certificate-of-occupancy`](./nyc-certificate-of-occupancy) | Property-specific occupancy-record evidence |
| [`/as:nyc-authority-resolver`](./nyc-authority-resolver) | Candidate-authority map with triggers and unknowns |
| [`/as:nyc-code-edition`](./nyc-code-edition) | Edition-candidate evidence with unresolved applicability |
| [`/as:nyc-code-section`](./nyc-code-section) | Identified provision evidence |
| [`/as:nyc-amendment-check`](./nyc-amendment-check) | Bounded amendment evidence and search limitations |
| [`/as:nyc-referenced-standard`](./nyc-referenced-standard) | Referenced-standard metadata and authorized access route |

Each directory contains an authoritative `SKILL.md`, a human-facing `README.md`, and any scripts, references, templates, or data owned by that skill. Create studio or project procedures with `/as:skill-maker`; to contribute a built-in skill, read [CONTRIBUTING.md](../CONTRIBUTING.md).

Practice discovery is generated from the [maintained cluster manifests](../docs/practice-clusters.md).
See the [category authoring contract](../docs/category-authoring.md) for shared ownership;
public skill names and invocation syntax remain unchanged.
