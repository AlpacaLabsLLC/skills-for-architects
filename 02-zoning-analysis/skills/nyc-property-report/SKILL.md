---
name: nyc-property-report
description: NYC property data — landmarks, DOB permits, violations, ACRIS records, HPD, and BSA variances from NYC Open Data APIs.
allowed-tools:
  - WebFetch
  - Write
  - Read
  - Bash
  - Glob
  - Grep
user-invocable: true
---

# /nyc-property-report — NYC Property Data

Look up building and property data for any NYC address. Queries NYC Open Data (Socrata) and NYC Geoclient APIs across 7 data domains: property identification, landmarks, DOB permits, DOB violations, ACRIS property records, HPD (residential), and BSA variances.

## Usage

```
/nyc-property-report [address]                    → full report (all domains)
/nyc-property-report [address] landmarks          → LPC landmark check only
/nyc-property-report [address] permits            → DOB permits & filings only
/nyc-property-report [address] violations         → DOB + ECB violations only
/nyc-property-report [address] acris              → property records only
/nyc-property-report [address] hpd                → HPD violations & registration only
/nyc-property-report [address] bsa                → BSA variances & special permits only
/nyc-property-report [BBL]                        → full report by BBL
/nyc-property-report [BIN]                        → full report by BIN
```

Examples:
- `/nyc-property-report 120 Broadway, Manhattan`
- `/nyc-property-report 375 Sterling Place, Brooklyn 11238`
- `/nyc-property-report 1000770001 landmarks` (BBL for 120 Broadway)
- `/nyc-property-report 25-15 Queens Blvd, Queens violations`

## Environment Variables

Check these at startup. If `NYC_GEOCLIENT_KEY` is missing and the user provides an address (not BBL), print setup instructions and stop.

| Variable | Required | Description |
|----------|----------|-------------|
| `NYC_GEOCLIENT_KEY` | Yes (for address input) | NYC Geoclient API subscription key. Register at https://api-portal.nyc.gov, subscribe to "Geoclient v2" |
| `NYC_SOCRATA_TOKEN` | No (recommended) | NYC Open Data app token for higher rate limits. Register at https://data.cityofnewyork.us/profile/edit/developer_settings |

To check: `echo $NYC_GEOCLIENT_KEY` via Bash.

If missing:
```
⚠ NYC_GEOCLIENT_KEY not set. To use this skill with an address:
1. Register at https://api-portal.nyc.gov
2. Subscribe to "Geoclient v2"
3. Copy your subscription key
4. Set it: export NYC_GEOCLIENT_KEY=your_key_here

Alternatively, provide a BBL directly (no Geoclient needed).
```

## Step 1: Parse Input

Accept:
- **Address + Borough/Zip** — "120 Broadway, Manhattan" or "120 Broadway 10271"
- **BBL** — 10-digit number (borough 1 digit + block 5 digits + lot 4 digits), e.g., 1000770001
- **BIN** — 7-digit Building Identification Number

Parse the address into components: house number, street name, borough (or zip). Handle:
- Hyphenated Queens addresses: "25-15 Queens Blvd" → houseNumber=25-15
- Unit/floor suffixes: strip them (they're not needed for lot lookup)
- Borough names: Manhattan=1, Bronx=2, Brooklyn=3, Queens=4, Staten Island=5

Detect mode from the last word of the arguments: landmarks, permits, violations, acris, hpd, bsa. If none specified, mode = "full".

## Step 2: Resolve to BBL/BIN (Geoclient)

If the user provided an address (not BBL/BIN), call the Geoclient API:

```
GET https://api.nyc.gov/geo/geoclient/v2/address?houseNumber={num}&street={street}&borough={borough}
Header: Ocp-Apim-Subscription-Key: {NYC_GEOCLIENT_KEY}
```

Use WebFetch to call this URL. The response is JSON with fields including:
- `bbl` — 10-digit BBL
- `buildingIdentificationNumber` (BIN)
- `boeFlag`, `communityDistrict`, `congressionalDistrict`, `councilDistrict`, `censusBlock`, `censusTract2020`, `fireCompanyNumber`, `policePrecinct`, `schoolDistrict`, `zipCode`
- `latitude`, `longitude`

If the address is not found, the response has a `message` field with the error. Display it and suggest alternatives.

Store the BBL and BIN for use in all subsequent queries. Parse BBL into borough code, block (5 digits), and lot (4 digits) for APIs that need them separately.

## Step 3: Query Data Domains

Based on mode, query the relevant domains. For "full" mode, query all 7 in sequence.

For each Socrata query, use WebFetch with the URL. Socrata returns JSON arrays. If `NYC_SOCRATA_TOKEN` is set, append `&$$app_token={token}` to each URL.

Read `socrata-reference.md` for the full API reference with field names and SoQL patterns.

### Domain 1: Property Identification (always runs)

Already resolved in Step 2. Format the Geoclient response as a summary table.

### Domain 2: Landmarks (mode: "landmarks" or "full")

Query LPC database by BIN:
```
https://data.cityofnewyork.us/resource/7mgd-s57w.json?bin_number={BIN}
```

If no results, try by BBL:
```
https://data.cityofnewyork.us/resource/7mgd-s57w.json?bbl={BBL}
```

Key fields: `lpc_name`, `lpc_number`, `date_designated`, `building_type`, `style`, `architect`, `historic_district_name`, `status`

If no results: "No landmark designation found for this property."

**Implications note:** If landmarked, add: "Exterior alterations require LPC Certificate of Appropriateness before DOB permits."

### Domain 3: DOB Permits (mode: "permits" or "full")

Query 4 datasets. Use BIN where possible, fall back to borough/block/lot.

Legacy Permit Issuance:
```
https://data.cityofnewyork.us/resource/ipu4-2q9a.json?$where=bin__='{BIN}'&$order=issuance_date DESC&$limit=30
```

Legacy Job Filings:
```
https://data.cityofnewyork.us/resource/ic3t-wcy2.json?$where=bin__='{BIN}'&$order=latest_action_date DESC&$limit=30
```

DOB NOW Approved Permits:
```
https://data.cityofnewyork.us/resource/rbx6-tga4.json?$where=bin='{BIN}'&$order=approved_date DESC&$limit=30
```

DOB NOW Job Filings:
```
https://data.cityofnewyork.us/resource/w9ak-ipjd.json?$where=bin='{BIN}'&$order=filing_date DESC&$limit=30
```

**IMPORTANT:** Legacy and DOB NOW datasets use different field names. See socrata-reference.md for the field mapping.

Merge results, sort by date descending. Group by job type:
- NB = New Building
- A1 = Alteration Type 1 (major, changes use/egress/occupancy)
- A2 = Alteration Type 2 (multiple work types)
- A3 = Alteration Type 3 (minor, one work type)
- DM = Demolition
- Other

Show: date, job #, permit #, work type/description, status, applicant/owner.

### Domain 4: DOB Violations (mode: "violations" or "full")

Query 3 datasets:

DOB Violations:
```
https://data.cityofnewyork.us/resource/3h2n-5cm9.json?$where=bin='{BIN}'&$order=issue_date DESC&$limit=50
```

ECB Violations:
```
https://data.cityofnewyork.us/resource/6bgk-3dad.json?$where=bin='{BIN}'&$order=violation_date DESC&$limit=50
```

Active/Open Violations:
```
https://data.cityofnewyork.us/resource/sjhj-bc8q.json?$where=bin='{BIN}'
```

Flag open violations prominently with ⚠. Show ECB penalties (penalty_applied, amount_paid, amount_baldue).

### Domain 5: ACRIS Property Records (mode: "acris" or "full")

This is the most complex domain — requires a 3-table join. BBL is required (not BIN).

Parse BBL into: borough (1 digit), block (5 digits), lot (4 digits).

Step A — Get document IDs from Legals table:
```
https://data.cityofnewyork.us/resource/8h5j-fqxa.json?borough={boro}&block={block}&lot={lot}&$order=good_through_date DESC&$limit=20
```

Step B — Get document details from Master table. Build a `$where` clause with the document_ids from Step A:
```
https://data.cityofnewyork.us/resource/bnx9-e6tj.json?$where=document_id IN ('{id1}','{id2}',...)&$order=doc_date DESC
```

Step C — Get parties from Parties table with the same document_ids:
```
https://data.cityofnewyork.us/resource/636b-3b5g.json?$where=document_id IN ('{id1}','{id2}',...)
```

Step D — Look up doc type codes (fetch once):
```
https://data.cityofnewyork.us/resource/7isb-wh4c.json?$limit=200
```

Join: for each document, combine Master (date, type, amount) with Parties (grantor/grantee names). Group by document type (Deed, Mortgage, Assignment, Satisfaction, etc.).

Show ownership chain: most recent deed's grantee = current owner.

### Domain 6: HPD (mode: "hpd" or "full")

**First check building class** from PLUTO (or from the Geoclient response if available). HPD only applies to residential buildings (class A, B, C, D, R, S). If non-residential, skip and note: "Building class {X} — HPD records not applicable (non-residential)."

If residential, query 4 datasets using borough/block/lot (HPD uses boroid, not BBL as a single field):

Violations:
```
https://data.cityofnewyork.us/resource/wvxf-dwi5.json?$where=boroid='{boro}' AND block='{block}' AND lot='{lot}'&$order=inspectiondate DESC&$limit=50
```

Open Violations:
```
https://data.cityofnewyork.us/resource/csn4-vhvf.json?$where=boroid='{boro}' AND block='{block}' AND lot='{lot}'
```

Complaints:
```
https://data.cityofnewyork.us/resource/ygpa-z7cr.json?$where=boroid='{boro}' AND block='{block}' AND lot='{lot}'&$order=receiveddate DESC&$limit=30
```

Registrations:
```
https://data.cityofnewyork.us/resource/tesw-yqqr.json?$where=boroid='{boro}' AND block='{block}' AND lot='{lot}'
```

Flag Class C violations (immediately hazardous) prominently with ⚠.

### Domain 7: BSA (mode: "bsa" or "full")

Query by BBL:
```
https://data.cityofnewyork.us/resource/yvxd-uipr.json?$where=bbl='{BBL}'&$order=calendar_date DESC
```

If no BBL match, try address:
```
https://data.cityofnewyork.us/resource/yvxd-uipr.json?$where=upper(premises_address) LIKE '%{STREET}%' AND borough='{BOROUGH}'&$order=calendar_date DESC
```

Show: calendar #, type (variance/special permit), status, decision, date, description.

Note: "Approved variances remain with the land. Check if conditions affect proposed work."

## Step 4: Write Report

Write the report to the user's working directory. Filename: `property-{address-slug}.md`

Use the file path convention from the user's system. If no clear working directory, write to `~/Documents/Alpaca Labs/` or ask.

### Report Structure

```markdown
# NYC Property Report — {Address}

**Generated:** {date}
**BBL:** {bbl} | **BIN:** {bin}
**Source:** NYC Geoclient API, NYC Open Data (Socrata)

---

## 1. Property Identification

| Field | Value |
|-------|-------|
| BBL | {bbl} |
| BIN | {bin} |
| Borough | {borough} |
| Block | {block} |
| Lot | {lot} |
| ZIP | {zip} |
| Community District | {cd} |
| Council District | {council} |
| Census Tract | {tract} |
| Coordinates | {lat}, {lon} |

---

## 2. Landmark Status

{LANDMARKED or NOT LANDMARKED}

{If landmarked: LP number, name, designation date, district, architect, style}
{If not: "No landmark designation found."}

---

## 3. DOB Permits & Filings

**Total found:** {count} ({x} legacy, {y} DOB NOW)

### New Building (NB)
| Date | Job # | Permit # | Status | Applicant |
|------|-------|----------|--------|-----------|

### Alteration Type 1 (A1)
{table}

### Alteration Type 2-3 (A2/A3)
{table}

{other types}

---

## 4. DOB Violations

### ⚠ Open Violations: {count}
| Violation # | Type | Date | Description | Disposition |
|-------------|------|------|-------------|-------------|

### All DOB Violations
{table}

### ECB Violations
| ISN | Date | Violation Type | Penalty | Balance Due | Status |
|-----|------|----------------|---------|-------------|--------|

**Total penalties assessed:** ${amount}

---

## 5. Property Records (ACRIS)

### Deeds (Ownership)
| Date | Doc Type | Amount | From (Grantor) | To (Grantee) |
|------|----------|--------|----------------|--------------|

**Current owner (per most recent deed):** {name}

### Mortgages
| Date | Amount | Lender | Borrower |
|------|--------|--------|----------|

### Other Documents
{table for assignments, satisfactions, liens, etc.}

---

## 6. HPD — Housing Preservation & Development

{If non-residential: "Building class {X} — HPD records not applicable."}

{If residential:}

### Registration
| Field | Value |
|-------|-------|
| Owner | {owner} |
| Managing Agent | {agent} |
| Registration Expiry | {date} |

### ⚠ Open Violations: {count}
**Class C (Immediately Hazardous):** {count}
**Class B (Hazardous):** {count}
**Class A (Non-Hazardous):** {count}

{table of open violations}

### Recent Complaints
{table}

---

## 7. BSA — Board of Standards and Appeals

{If no applications: "No BSA applications found (records from 1998–present)."}

{If applications found:}
| Calendar # | Type | Decision | Date | Description |
|------------|------|----------|------|-------------|

---

*Generated by /nyc-property-report — NYC Open Data*
*Data currency varies by dataset. Verify critical findings with source agencies.*
```

### Report Rules
- All dates in YYYY-MM-DD format
- Dollar amounts with comma separators
- Open violations always at the top of their section, flagged with ⚠
- If a domain returns no results, say so explicitly (don't omit the section)
- If a domain query fails (network error, rate limit), note the error and continue with other domains
- Always include the "Data currency varies" caveat at the end

## Step 5: Summary

After writing the file, print a brief inline summary:

```
Property report written: property-120-broadway.md

Key findings:
- Landmark: Not designated
- DOB Permits: 47 found (3 active filings)
- Open Violations: 2 (1 ECB with $25,000 penalty)
- Owner: SL Green Realty (per ACRIS deed 2019-03-15)
- HPD: N/A (commercial building)
- BSA: 1 approved variance (2004)

Run /zoning-analysis-nyc for zoning data, or /nyc-due-diligence for the full package.
```

## Edge Cases

- **No results from any API**: State clearly per section. Don't fail the whole report.
- **Rate limited (HTTP 429)**: Wait 5 seconds, retry once. If still 429, note the error and suggest setting `NYC_SOCRATA_TOKEN`.
- **ACRIS with many documents**: Limit to 20 most recent. Note if truncated.
- **Condo lots**: ACRIS keys on individual unit lots. Note that the user may need to search by both the unit lot and the main condo lot.
- **Very old buildings**: Pre-BIS DOB records (before ~1989) are not digitized. Note this if no permits found for a pre-1989 building.
- **Hyphenated Queens addresses**: Pass as-is to Geoclient — it handles them.
- **Multiple BINs for one BBL**: Possible for lot with multiple buildings. Geoclient returns the primary BIN. Note if PLUTO shows `numbldgs` > 1.
