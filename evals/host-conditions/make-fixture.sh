#!/usr/bin/env bash
# Build the deterministic fixture project the host-condition cases run against.
# Usage: make-fixture.sh <target-dir> <plugin-root>
set -euo pipefail

target=${1:?usage: make-fixture.sh <target-dir> <plugin-root>}
plugin_root=${2:?usage: make-fixture.sh <target-dir> <plugin-root>}

# Repeated trials need a new output path; never erase an existing run.
[ ! -e "$target" ] || { echo 'Fixture target already exists' >&2; exit 2; }
python3 - "$target" "$plugin_root" <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, str(Path(sys.argv[2]).resolve()/'skills/receive/scripts'))
import workspaces
workspaces.dispatch('project.init', {'target':str(Path(sys.argv[1]).resolve()),
    'name':'Synthetic evaluation fixture','project_id':'EVL-FIXTURE','kind':'building',
    'type':'internal','status':'active','client_code':'EVL','client':'Synthetic fixture',
    'vocabularies':{'phases':['design'],'scopes':['main'],'originators':['fixture']},
    'dry_run':False})
PY

python3 "$plugin_root/skills/product-library/scripts/csv-library.py" init product --project "$target" >/dev/null

python3 - "$target" <<'PY'
import csv, sys, pathlib

path = pathlib.Path(sys.argv[1]) / "product-library.csv"
header = list(csv.reader(path.open(newline=""))) [0]
index = {name: header.index(name) for name in header}

# Deliberately fictional products and prices, not manufacturer reference data.
products = [
    ("Seating", "Fixture Works", "Sample Chair", "Fixture Designer", "Synthetic chair", "FIX-C1", "Qty 3", "100.00"),
    ("Tables", "Fixture Works", "Sample Table", "Fixture Designer", "Synthetic table", "FIX-T1", "Qty 2", "200.00"),
    ("Lighting", "Fixture Works", "Sample Light", "Fixture Designer", "Synthetic light", "FIX-L1", "Qty 4", "300.00"),
]

rows = []
for category, brand, name, designer, description, sku, note, price in products:
    row = [""] * len(header)
    row[index["Category"]] = category
    row[index["Brand"]] = brand
    row[index["Vendor"]] = brand
    row[index["Product Name"]] = name
    row[index["Designer"]] = designer
    row[index["Indoor/Outdoor"]] = "Indoor"
    row[index["Description"]] = description
    row[index["SKU"]] = sku
    row[index["Notes"]] = note
    row[index["List Price"]] = price
    row[index["Currency"]] = "USD"
    row[index["Unit"]] = "EA"
    rows.append(row)

with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
PY

python3 "$plugin_root/skills/product-library/scripts/csv-library.py" validate product --project "$target"
