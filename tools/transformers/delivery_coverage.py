#!/usr/bin/env python3
"""Check a supplied item-to-artifact ledger; actual artifact verification stays with ffe_outputs."""
import argparse
import json
from pathlib import Path
import re
import hashlib


def assess(expected, entries):
    if not isinstance(expected, list) or not expected or not all(isinstance(x, str) and x.strip() for x in expected) or len(set(expected)) != len(expected):
        raise ValueError('Nonempty unique expected item list required')
    seen, unresolved = set(), []
    for entry in entries:
        item = entry.get('item')
        if item not in expected or item in seen:
            raise ValueError('Unexpected or duplicate coverage item')
        seen.add(item)
        if entry.get('status') == 'verified':
            if not isinstance(entry.get('artifact'), str) or not entry['artifact'].strip() or not re.fullmatch('[a-f0-9]{64}', str(entry.get('sha256', ''))):
                raise ValueError('Verified entry requires artifact reference and SHA-256')
        elif entry.get('status') == 'unresolved' and isinstance(entry.get('reason'), str) and entry['reason'].strip():
            unresolved.append(item)
        else:
            raise ValueError('Explicit verified or unresolved entry with evidence required')
    missing = [item for item in expected if item not in seen]
    return dict(missing=missing, unresolved=unresolved, accounted_for=not missing,
                complete=not missing and not unresolved, evidence_verified=False,
                claim='Ledger completeness only; run output checks and inspect actual artifacts')


def verify_links(expected):
    """Compare current accepted item identities to actual linked files and their receipts."""
    if not isinstance(expected, list) or not expected:
        raise ValueError('Explicit current item/link scope required')
    seen, verified, failures = set(), [], []
    for row in expected:
        item = row.get('item')
        if not isinstance(item, str) or not item or item in seen or type(row.get('revision')) is not int or row['revision'] < 1:
            raise ValueError('Unique current item and positive revision required')
        seen.add(item)
        try:
            artifact = Path(row['artifact'])
            receipt_path = Path(row['receipt'])
            if artifact.is_symlink() or receipt_path.is_symlink():
                raise ValueError('Symlink artifact/receipt not supported')
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            if receipt.get('mechanical_status') != 'passed':
                raise ValueError('Linked receipt has no mechanical pass')
            groups = [group for group in receipt['outputs'] if any(i['item_id'] == item and i['revision'] == row['revision'] for i in group['items'])]
            if len(groups) != 1:
                raise ValueError('Linked artifact receipt belongs to a different item revision')
            filename = groups[0].get('filename', groups[0]['tag'] + '.pdf')
            if artifact.name != filename:
                raise ValueError('Artifact link differs from intended output')
            for field in ('source_sha256', 'template_sha256'):
                if not re.fullmatch('[a-f0-9]{64}', str(row.get(field, ''))) or receipt.get(field) != row[field]:
                    raise ValueError('Linked receipt differs from current ' + field)
            matches = [entry for entry in receipt['verified_artifacts'] if entry['file'] == filename]
            if len(matches) != 1 or hashlib.sha256(artifact.read_bytes()).hexdigest() != matches[0]['sha256']:
                raise ValueError('Artifact bytes differ from linked verified receipt')
            verified.append(item)
        except (ValueError, KeyError, OSError, TypeError) as error:
            failures.append({'item': item, 'reason': str(error)})
    return {'complete': not failures, 'verified_items': verified, 'failures': failures,
            'evidence_verified': 'current revision/link/file hashes only; receipt observations remain supplied claims',
            'workflow_completed': False}


def dispatch(operation, request):
    if operation == 'delivery_coverage.verify-links':
        return verify_links(request['expected'])
    raise ValueError('Unknown delivery coverage operation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.input.read_text(encoding='utf-8'))
        print(json.dumps(assess(request['expected'], request['entries']), allow_nan=False))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
        parser.exit(2, str(error) + '\n')
