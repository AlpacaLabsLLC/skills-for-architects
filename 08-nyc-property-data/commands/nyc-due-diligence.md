---
description: Full NYC site due diligence — zoning analysis + property report + 3D envelope viewer.
argument-hint: "[NYC address, e.g. '120 Broadway, Manhattan']"
---

# /nyc-due-diligence — Full NYC Site Package

Run three skills in sequence to produce a complete site due diligence package:

1. **Zoning Analysis** (`/zoning-analysis-nyc`) — Zoning district, FAR, height limits, setbacks, permitted uses, parking, bonuses
2. **Property Report** (`/nyc-property-report`) — Landmarks, DOB permits, violations, ACRIS records, HPD, BSA
3. **Zoning Envelope** (`/zoning-envelope`) — Interactive 3D viewer of the buildable envelope

## Usage

```
/nyc-due-diligence [address]
```

## Workflow

1. Parse the address from $ARGUMENTS
2. Run `/zoning-analysis-nyc {address}` — produces `zoning-{slug}.md`
3. Run `/nyc-property-report {address}` — produces `property-{slug}.md`
4. Run `/zoning-envelope zoning-{slug}.md` — produces `zoning-{slug}.html`
5. Print summary of all 3 outputs with key findings

## Output

Three files in the working directory:
- `zoning-{address-slug}.md` — Zoning analysis
- `property-{address-slug}.md` — Property report
- `zoning-{address-slug}.html` — 3D envelope viewer (open in browser)
