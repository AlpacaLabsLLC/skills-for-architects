#!/usr/bin/env python3
"""Compare explicit tag/scope/unit quantity snapshots without choosing authoritative values."""
import argparse
import json
import math
from pathlib import Path


def index(rows):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('Quantity snapshot must be an array of row objects')
    result = {}
    for row in rows:
        if not all(isinstance(row.get(k), str) and row[k].strip() for k in ('tag', 'scope', 'unit', 'source')):
            raise ValueError('Exact tag, scope, unit and source required')
        if 'quantity' not in row:
            raise ValueError('Explicit quantity required; use null for unknown')
        value = row['quantity']
        try:
            valid = value is None or (type(value) in (int, float) and math.isfinite(value) and value >= 0)
        except OverflowError:
            valid = False
        if not valid:
            raise ValueError('Quantity must be finite nonnegative number or null')
        key = row['tag'], row['scope'], row['unit']
        if key in result:
            raise ValueError('Duplicate comparison key; explicitly aggregate or resolve first')
        result[key] = row
    return result


def reconcile(left, right):
    a, b = index(left), index(right)
    output = []
    for key in sorted(a.keys() | b.keys()):
        x, y = a.get(key), b.get(key)
        status = ('missing-left' if x is None else 'missing-right' if y is None else
                  'unknown' if x['quantity'] is None or y['quantity'] is None else
                  'match' if x['quantity'] == y['quantity'] else 'conflict')
        output.append(dict(tag=key[0], scope=key[1], unit=key[2], left=x, right=y, status=status))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.input.read_text(encoding='utf-8'))
        print(json.dumps(reconcile(request['left'], request['right']), allow_nan=False))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
        parser.exit(2, str(error) + '\n')
