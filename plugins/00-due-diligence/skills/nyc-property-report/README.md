# /nyc-property-report

Combined NYC property report as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill. Runs all 6 NYC property data lookups in sequence and writes a comprehensive markdown report covering landmarks, DOB permits, violations, ACRIS records, HPD data, and BSA variances. No API key required.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../../LICENSE)

## Install

```bash
# Via plugin system
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 00-due-diligence@skills-for-architects

# Or symlink just this skill
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/00-due-diligence/skills/nyc-property-report ~/.claude/skills/nyc-property-report
```

## Usage

```
/nyc-property-report 120 Broadway, Manhattan
/nyc-property-report 1000770001          (BBL)
/nyc-property-report 1001389             (BIN)
```

## What it covers

This skill orchestrates all 6 standalone NYC property skills into a single report. Each skill can also be run independently:

| Skill | What it covers |
|-------|---------------|
| [`/nyc-landmarks`](../nyc-landmarks) | LPC landmark & historic district check |
| [`/nyc-dob-permits`](../nyc-dob-permits) | DOB permit & filing history (Legacy BIS + DOB NOW) |
| [`/nyc-dob-violations`](../nyc-dob-violations) | DOB & ECB violations with open violation flags |
| [`/nyc-acris`](../nyc-acris) | ACRIS property transaction records (deeds, mortgages, liens) |
| [`/nyc-hpd`](../nyc-hpd) | HPD violations, complaints & registration (residential only) |
| [`/nyc-bsa`](../nyc-bsa) | BSA variances & special permits |

## Data Sources

| Source | Dataset ID | What it provides |
|--------|-----------|-----------------|
| PLUTO | `64uk-42ks` | Address resolution, property metadata |
| LPC Building Database | `7mgd-s57w` | Landmark and historic district status |
| DOB Permit Issuance (Legacy) | `ipu4-2q9a` | Legacy permits |
| DOB Job Filings (Legacy) | `ic3t-wcy2` | Legacy job applications |
| DOB NOW Approved Permits | `rbx6-tga4` | DOB NOW permits |
| DOB NOW Job Filings | `w9ak-ipjd` | DOB NOW applications |
| DOB Violations | `3h2n-5cm9` | DOB violations |
| DOB ECB Violations | `6bgk-3dad` | ECB violations and penalties |
| DOB Active Violations | `sjhj-bc8q` | Currently open violations |
| ACRIS Legals | `8h5j-fqxa` | Document-to-lot mapping |
| ACRIS Master | `bnx9-e6tj` | Document details |
| ACRIS Parties | `636b-3b5g` | Grantor/grantee names |
| ACRIS Document Codes | `7isb-wh4c` | Document type translations |
| HPD Violations | `wvxf-dwi5` | Housing violations |
| HPD Open Violations | `csn4-vhvf` | Open housing violations |
| HPD Complaints | `ygpa-z7cr` | Housing complaints |
| HPD Registrations | `tesw-yqqr` | Building registrations |
| BSA Applications | `yvxd-uipr` | Variances and special permits |

## Output

A markdown file (`property-{address-slug}.md`) with 7 sections: property identification, landmark status, DOB permits, DOB violations, ACRIS records, HPD data, and BSA variances. After writing the file, prints a brief inline summary with key findings.

Pair with `/zoning-analysis-nyc` for a complete property and zoning picture.

## License

MIT
