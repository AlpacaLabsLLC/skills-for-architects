# Socrata API Reference — NYC Due-Diligence Skills

**Single source of truth** for every NYC Open Data (Socrata) dataset ID and field name used by the 7 due-diligence skills (`nyc-property-report`, `nyc-landmarks`, `nyc-dob-permits`, `nyc-dob-violations`, `nyc-acris`, `nyc-hpd`, `nyc-bsa`). If a query in a SKILL.md disagrees with this file, this file wins — fix the SKILL.md. All dataset IDs and field sets below were verified against the live API (`$select` returns 200) on 2026-07-20.

For BBL/BIN address resolution, see `pluto-resolution.md` (same directory).

## Socrata API Basics

- Base URL: `https://data.cityofnewyork.us/resource/{DATASET-ID}.json`
- Returns JSON array of objects
- SoQL query params: `$where`, `$order`, `$limit`, `$offset`, `$select`
- Default limit: 1000 rows. Max: 50,000. Use `$limit` to control.
- String matching: `upper(field) LIKE '%PATTERN%'`
- App token: append `&$$app_token={token}` or pass header `X-App-Token`
- A `$select` naming a nonexistent field returns HTTP 400 — the fastest way to detect field drift.

## Dataset Reference

| Domain | Dataset | ID | Key Fields | Filter Field |
|--------|---------|-----|-----------|-------------|
| PLUTO | Primary Land Use Tax Lot Output | `64uk-42ks` | bbl, address, borough, block, lot, bldgclass, zonedist1, yearbuilt, ownername, numfloors, lotarea, bldgarea, unitstotal, zipcode, cd, histdist, numbldgs, latitude, longitude | bbl, address+borough. **No BIN field.** |
| Building Footprints | BUILDING (footprints) | `5zhs-2jue` | bin, base_bbl, mappluto_bbl, construction_year, height_roof | mappluto_bbl, bin. BBL↔BIN bridge. |
| LPC Landmarks | Individual Landmarks | `buis-pvji` | lpc_name, lpc_lpnumb, desdate, landmarkty, lpc_sitede, lpc_sitest, lpc_altern, address, url_report, bbl, borough, block, lot | bbl (preferred), block+lot+borough. **block/lot NOT zero-padded** (e.g. block `47`, lot `7501`). desdate is M/D/YYYY. |
| DOB Permits (Legacy) | DOB Permit Issuance | `ipu4-2q9a` | permit_si_no, job__, job_type, issuance_date, expiration_date, permittee_s_first_name/last_name, owner_s_first_name/last_name, borough, block, lot | bin__ |
| DOB Filings (Legacy) | DOB Job Application Filings | `ic3t-wcy2` | job__, doc__, job_type, job_status, latest_action_date, applicant_s_first_name/last_name, owner_s_first_name/last_name, borough, block, lot | bin__ |
| DOB Permits (NOW) | DOB NOW Build Approved Permits | `rbx6-tga4` | job_filing_number, work_permit, permit_status, work_type, approved_date, issued_date, expired_date, estimated_job_costs, job_description, owner_name, borough, bin, bbl | bin. **No filing_date or job_type** — use approved_date / work_type. |
| DOB Filings (NOW) | DOB NOW Build Job Application Filings | `w9ak-ipjd` | job_filing_number, filing_status, filing_date, job_type, borough, bin, bbl | bin |
| DOB Violations | DOB Violations | `3h2n-5cm9` | isn_dob_bis_viol, violation_type, issue_date, violation_category, disposition_date, disposition_comments | bin |
| DOB ECB Violations | DOB ECB Violations | `6bgk-3dad` | isn_dob_bis_extract, ecb_violation_number, violation_type, issue_date, penality_imposed, amount_paid, balance_due, hearing_status, ecb_violation_status, severity | bin. Date field is `issue_date` (NOT violation_date). |
| DOB Active Violations | Active DOB Violations | `sjhj-bc8q` | All fields from 3h2n-5cm9 but pre-filtered to open | bin |
| ACRIS Master | ACRIS Real Property Master | `bnx9-e6tj` | document_id, record_type, crfn, doc_type, document_date, document_amt, recorded_datetime, good_through_date | document_id. **NOT doc_date/doc_amount/recorded_filed.** |
| ACRIS Legals | ACRIS Real Property Legals | `8h5j-fqxa` | document_id, borough, block, lot, property_type, street_number, street_name, good_through_date | borough, block, lot |
| ACRIS Parties | ACRIS Real Property Parties | `636b-3b5g` | document_id, party_type, name, address_1, city, state, zip | document_id |
| ACRIS Doc Types | ACRIS Document Control Codes | `7isb-wh4c` | doc__type, doc__type_description | (lookup table) |
| HPD Violations | Housing Maintenance Code Violations | `wvxf-dwi5` | violationid, class, inspectiondate, approveddate, originalcertifybydate, novdescription, currentstatus, novissueddate | boroid, block, lot. Class field is `class` (NOT violationclass). |
| HPD Open Violations | Open HPD Violations | `csn4-vhvf` | Same fields, pre-filtered to open | boroid, block, lot |
| HPD Complaints | Complaints and Problems | `ygpa-z7cr` | complaint_id, received_date, complaint_status, complaint_status_date, major_category, minor_category, problem_status | `borough` as text ("BROOKLYN"), block, lot. NOT boroid; date is `received_date` (NOT receiveddate). |
| HPD Registrations | Multiple Dwelling Registrations | `tesw-yqqr` | registrationid, buildingid, boroid, block, lot, bin, registrationenddate, lastregistrationdate | boroid, block, lot. **No owner-name fields** — join Registration Contacts. |
| HPD Registration Contacts | Registration Contacts | `feu5-w2e2` | registrationcontactid, registrationid, type (CorporateOwner/Agent/HeadOfficer/…), firstname, lastname, corporationname | registrationid |
| BSA Applications | BSA Applications Status | `yvxd-uipr` | application, section, status, date, street_number, street_name, decisions_url, project_description, bbl, borough | bbl. Date field is `date` (NOT calendar_date); street field is `street_name` (NOT premises_address). |

## ACRIS 3-Table Join Logic

ACRIS data is split across three tables linked by `document_id`:

```
1. Query Legals by borough + block + lot → get document_ids
2. Query Master by document_id IN (...) → get doc dates, types, amounts
3. Query Parties by document_id IN (...) → get names (grantor/grantee)
4. Query Doc Type Codes (once) → translate doc_type codes to descriptions
5. For each document: combine Master + Parties, label with doc type description
```

Important: `document_id` is the join key across all 3 tables. The Legals table is the entry point (keyed on BBL).

### Party Types

- `1` = Grantor (seller, borrower, assignor)
- `2` = Grantee (buyer, lender, assignee)

### Common Document Types

| Code | Description |
|------|-------------|
| DEED | Deed |
| MTGE | Mortgage |
| AGMT | Agreement |
| ASST | Assignment of Mortgage |
| SAT  | Satisfaction of Mortgage |
| RPTT | Real Property Transfer Tax |
| ALIS | Assignment of Leases and Rents |
| UCC1 | UCC Financing Statement |
| MCON | Mortgage Consolidation |

## Field Name Differences: Legacy vs DOB NOW

| Concept | Legacy Field | DOB NOW Filings (`w9ak-ipjd`) | DOB NOW Permits (`rbx6-tga4`) |
|---------|-------------|-------------------------------|-------------------------------|
| BIN | `bin__` | `bin` | `bin` |
| Job number | `job__` | `job_filing_number` | `job_filing_number` |
| Permit number | `permit_si_no` | — | `work_permit` |
| Filing date | `latest_action_date` | `filing_date` | — (use `approved_date`) |
| Permit date | `issuance_date` | — | `approved_date` / `issued_date` |
| Job/work type | `job_type` | `job_type` | `work_type` |
| Status | `job_status` | `filing_status` | `permit_status` |
| Borough | `borough` | `borough` | `borough` |
| Block | `block` | (parsed from bbl) | `block` |
| Lot | `lot` | (parsed from bbl) | `lot` |

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200 + empty array `[]` | No results found | Report "none found" for that domain |
| 200 + data | Success | Parse and format |
| 400 | Bad query (SoQL syntax error or nonexistent field) | Report the error, check field names against this file |
| 403 | Forbidden / rate limited (no token) | Suggest setting NYC_SOCRATA_TOKEN |
| 429 | Rate limited | Wait 5 seconds, retry once |

## Rate Limits

- **Without app token:** 1,000 requests per rolling hour per IP
- **With app token:** 10,000+ requests per rolling hour
- Recommendation: always set `NYC_SOCRATA_TOKEN` for production use
