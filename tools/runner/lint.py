#!/usr/bin/env python3
"""Validate operation declarations and their executable fixture references."""
import importlib.util
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import registry


def check(root):
    root = Path(root).resolve()
    operations = registry(root)
    for name, row in operations.items():
        if not row['input_schema'].get('additionalProperties') is False:
            raise ValueError(name + ': closed operation input required')
        if not row.get('effects') or not row.get('fixtures'):
            raise ValueError(name + ': effects and executable fixture evidence required')
        for field in ('module', 'script'):
            if field in row and not (root / row[field]).is_file():
                raise ValueError(name + ': missing ' + field)
        for fixture in row['fixtures']:
            if not (root / fixture).is_file():
                raise ValueError(name + ': missing fixture ' + fixture)
    fixture = json.loads((root / 'tools/runner/fixtures/operations.json').read_text())
    if set(fixture['operations']) != set(operations):
        raise ValueError('Operation fixture index does not cover the current registry')
    return {'operations': len(operations), 'fixture_index': 'tools/runner/fixtures/operations.json',
            'claim': 'Declaration and fixture-reference coverage, not execution acceptance'}


if __name__ == '__main__':
    print(json.dumps(check(Path(__file__).resolve().parents[2])))
