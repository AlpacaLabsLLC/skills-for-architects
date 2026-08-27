#!/usr/bin/env bash
# Build the deterministic fixture project the host-condition cases run against.
# Usage: make-fixture.sh <target-dir> <plugin-root>
set -euo pipefail

target=${1:?usage: make-fixture.sh <target-dir> <plugin-root>}
plugin_root=${2:?usage: make-fixture.sh <target-dir> <plugin-root>}

rm -rf "$target"
mkdir -p "$target"

cat > "$target/PROJECT.md" <<'PROJECT'
# Eval Fixture Project

**Format version:** 3
**Project ID:** 2026-08-EVL-EVAL-FIXTURE
**Type:** internal
**Status:** active
**Client:** —
PROJECT

python3 "$plugin_root/skills/master-schedule/scripts/csv-library.py" init product --project "$target" >/dev/null

python3 - "$target" <<'PY'
import csv, sys, pathlib

path = pathlib.Path(sys.argv[1]) / "product-library.csv"
header = list(csv.reader(path.open(newline=""))) [0]
index = {name: header.index(name) for name in header}

products = [
    ("Seating",  "Herman Miller", "Aeron Chair",           "Bill Stumpf",            "Task chair, size B, graphite frame",   "AER1B23DW",   "Qty 12", "1395.00"),
    ("Tables",   "Vitra",         "Eames Segmented Table", "Charles and Ray Eames",  "Conference table, 240cm, oak veneer",  "EST-240-OAK", "Qty 2",  "4850.00"),
    ("Lighting", "Flos",          "Arco Floor Lamp",       "Achille Castiglioni",    "Floor lamp, marble base, steel arc",   "ARC-F-MARB",  "Qty 4",  "3120.00"),
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

python3 "$plugin_root/skills/master-schedule/scripts/csv-library.py" validate product --project "$target"
