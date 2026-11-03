#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json,re
from pathlib import Path
names=['product-research','product-data-import','product-data-cleanup','product-enrich','product-match','product-pair','product-image-processor','product-spec-bulk-fetch','product-spec-pdf-parser','sif-to-csv','csv-to-sif']
for name in names:
    root=Path('skills')/name
    text=(root/'SKILL.md').read_text()
    assert 'product-library.csv' in text,name
    assert 'csv-conventions.md' in text,name
    assert not re.search(r'mcp__google-sheets|sheet-conventions\.md|spreadsheet ID|sheet ID',text,re.I),name
    declaration=json.loads((root/'host-contract.json').read_text())
    assert 'product-library.csv' not in declaration['owned_records'],name
    assert 'product-library.csv' in declaration['non_owned_records'],name
owner=json.loads(Path('skills/product-library/host-contract.json').read_text())
assert 'product-library.csv' in owner['owned_records']
image=Path('skills/product-image-processor/SKILL.md').read_text()
assert 'Image URL' in image and 'Product Name' in image
assert not re.search(r'column\s+(AC|E)\b',image,re.I)
print('PASS: current CSV ownership, schema links and named image fields')
PY
