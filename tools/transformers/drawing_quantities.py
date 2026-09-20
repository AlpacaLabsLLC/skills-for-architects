#!/usr/bin/env python3
"""Count explicitly classified drawing instances; not an automatic takeoff or visual verifier."""
import argparse
import json
import math
from pathlib import Path
import re


def summarize(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Nonempty instance ledger required')
    identities, positions, counts, excluded, unresolved = set(), set(), {}, [], []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Instance record must be an object')
        identity = row.get('instance_id')
        if not isinstance(identity, str) or not identity or identity in identities:
            raise ValueError('Unique instance ID required')
        identities.add(identity)
        digest, page, box = row.get('document_sha256'), row.get('physical_page'), row.get('bbox')
        if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest) or type(page) is not int or page < 1:
            raise ValueError('Document hash and physical page required')
        try:
            valid_box = isinstance(box, list) and len(box) == 4 and all(type(n) in (int, float) and math.isfinite(n) for n in box) and box[0] < box[2] and box[1] < box[3]
        except OverflowError:
            valid_box = False
        if not valid_box:
            raise ValueError('Valid source bounding box required')
        position = (digest, page, *box)
        if position in positions:
            raise ValueError('Duplicate source position; resolve overlapping extraction layers first')
        positions.add(position)
        if row.get('classification') not in ('instance', 'legend', 'note', 'unresolved') or type(row.get('reviewed')) is not bool:
            raise ValueError('Explicit classification and review state required')
        if not row['reviewed'] or row['classification'] == 'unresolved':
            unresolved.append(identity)
        elif row['classification'] != 'instance':
            excluded.append(identity)
        else:
            if not all(isinstance(row.get(k), str) and row[k].strip() for k in ('tag', 'scope')):
                raise ValueError('Instances require exact tag and drawing scope')
            key = (row['tag'], row['scope'])
            counts[key] = counts.get(key, 0) + 1
    return dict(counts=[dict(tag=k[0], scope=k[1], quantity=v, unit='each') for k, v in sorted(counts.items())],
                excluded=excluded, unresolved=unresolved, complete=not unresolved,
                coverage='supplied ledger only; page completeness and visual review are host evidence',
                source_completeness_verified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(json.loads(args.input.read_text(encoding='utf-8'))), allow_nan=False))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
        parser.exit(2, str(error) + '\n')
