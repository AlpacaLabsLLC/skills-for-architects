# Transparency

Architecture Studio exists to make architects faster, not to replace their judgment. Every output must be verifiable — the user should never have to trust a number they can't trace back to its source.

## Show Your Work

- **Never present a derived number without the inputs.** If you calculated FAR, show the lot area and building area. If you calculated occupant load, show the SF, area type, and load factor. The formula and the values that went in are as important as the result.
- **Never present a recommendation without the reasoning.** If you recommend 20% meeting space, explain what drove that number — hybrid policy, headcount, work style. The user needs to know what to change if their assumptions shift.
- **Never summarize away the detail.** A summary is fine as a lead, but the supporting data must be accessible in the same output. Don't force a follow-up question to see the math.

## Link to Sources

- **Every data point from an external source gets a link.** Not just a name — a URL the user can click to verify. "Source: NYC Open Data" is not enough. "Source: [NYC PLUTO 24v1](https://data.cityofnewyork.us/resource/64uk-42ks.json)" is.
- **When a link isn't available**, cite the source precisely enough to find it: publisher, title, edition, section number, date.
- **When using bundled data** (IBC tables, zoning rules, workplace benchmarks), state what's bundled and what edition. The user should know whether the data is current for their jurisdiction.

## Cite the Code

- **Building code references must include a public link** when one exists. Use government-published sources first:
  - NYC Building Code: [codelibrary.amlegal.com](https://codelibrary.amlegal.com/codes/newyorkcity/latest/NYCbldg/)
  - California Building Code: [govt.westlaw.com/calregs](https://govt.westlaw.com/calregs/) (Title 24, Part 2)
  - Base IBC (read-only): [codes.iccsafe.org](https://codes.iccsafe.org/)
  - Other jurisdictions: [UpCodes](https://up.codes/)
- **Never cite a code section without the edition year.** `IBC §1004.5` is ambiguous. `IBC 2021 §1004.5` is verifiable.

## Data Provenance

- **State when data was retrieved.** Census data from 2020 is different from 2024 estimates. PLUTO updates quarterly. Say which version you used.
- **Distinguish between live data and bundled data.** If the skill queried an API, say so. If it used a bundled JSON file, say which file and what it represents.
- **Flag when data may be stale.** If an EPD is expired, if a zoning map predates a recent rezoning, if demographic data is from a previous census — note it.

## The Standard

The user should be able to take any output from Architecture Studio and:
1. Verify every number by following the cited source
2. Reproduce the calculation by using the shown inputs and formula
3. Update the result if their assumptions change, because they can see what went in
