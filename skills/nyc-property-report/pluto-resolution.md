# Shared Reference — Resolving NYC Input to BBL / BIN (PLUTO)

Shared by all 7 NYC due-diligence skills (`nyc-property-report`, `nyc-landmarks`, `nyc-dob-permits`, `nyc-dob-violations`, `nyc-acris`, `nyc-hpd`, `nyc-bsa`). Each skill's "Parse Input" and "Resolve via PLUTO" steps follow this file; only skill-specific deltas live in the individual SKILL.md. Dataset IDs and field names are canonical in `socrata-reference.md` (same directory).

All queries are NYC Open Data (Socrata) — no API key required.

## Step 1: Parse Input

Accept one of:
- **Address + Borough/Zip** — "120 Broadway, Manhattan" or "120 Broadway 10271"
- **BBL** — 10-digit number (boro 1 + block 5 + lot 4)
- **BIN** — 7-digit Building Identification Number

Borough codes: Manhattan=1/MN, Bronx=2/BX, Brooklyn=3/BK, Queens=4/QN, Staten Island=5/SI

Strip apartment/unit/floor suffixes. Handle hyphenated Queens addresses.

## Step 2: Resolve via PLUTO

Query PLUTO (`64uk-42ks`) to get BBL and building metadata.

By BBL:
```
https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl={BBL}
```

By address:
```
https://data.cityofnewyork.us/resource/64uk-42ks.json?$where=upper(address) LIKE '%{STREET}%'&borough='{BORO_CODE}'&$limit=5
```

**Address normalization:** Uppercase, strip unit/apt suffixes. Borough names to codes: Manhattan=MN, Bronx=BX, Brooklyn=BK, Queens=QN, Staten Island=SI. If multiple results, ask the user to pick. If zero, try variations (ST vs STREET, AVE vs AVENUE) or suggest providing a BBL.

**BBL format gotcha:** PLUTO returns `bbl` as a decimal-formatted number (e.g. `"3012120065.00000000"`). Strip everything from the decimal point onward before using it as a 10-digit BBL string in other datasets.

Store from PLUTO (base set, all skills): `bbl`, `address`, `borough`, `bldgclass`, `zonedist1`, `yearbuilt`, `ownername`, `numfloors`, `lotarea`, `latitude`, `longitude`.

Skill-specific extras (store only if your SKILL.md asks for them):
- `nyc-landmarks`: also `histdist`
- `nyc-property-report`: also `zipcode`, `cd`, `bldgarea`, `unitstotal`, `histdist`, `numbldgs`

Parse BBL into: boro (1 digit), block (5 digits zero-padded), lot (4 digits zero-padded). Note: some datasets store block/lot WITHOUT zero-padding (e.g. LPC landmarks) — check `socrata-reference.md` per dataset.

## Step 3: Resolve BIN via Building Footprints

**PLUTO has no BIN field** (`bin`/`bldgbin` do not exist on `64uk-42ks` — selecting them returns HTTP 400). Skills that query by BIN (DOB permits, DOB/ECB violations) resolve it from the Building Footprints dataset (`5zhs-2jue`):

BBL → BIN:
```
https://data.cityofnewyork.us/resource/5zhs-2jue.json?$where=mappluto_bbl='{BBL}'&$select=bin,base_bbl,mappluto_bbl
```

BIN → BBL (when the user's input was a BIN):
```
https://data.cityofnewyork.us/resource/5zhs-2jue.json?$where=bin='{BIN}'&$select=bin,base_bbl,mappluto_bbl
```
Then feed `mappluto_bbl` into the PLUTO by-BBL query above.

Multiple footprints on one lot means multiple buildings (cross-check PLUTO `numbldgs`) — ask the user to pick or note that results cover one BIN of several.
