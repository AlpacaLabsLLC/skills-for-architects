#!/usr/bin/env python3
"""Compare supplied FF&E observations with a pinned selection; never fetch or mutate."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be an ISO string')
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp must include timezone')
    return parsed


def audit(document):
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document.get('schema_version') != 1:
        raise ValueError('expected audit input schema_version 1')
    if set(document) != {'schema_version', 'mode', 'started_at', 'items', 'observations'}:
        raise ValueError('unexpected or missing audit input field')
    mode = document['mode']
    if mode not in ('live', 'snapshot'):
        raise ValueError('mode must be live or snapshot')
    start = timestamp(document['started_at'])
    if start > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise ValueError('audit start timestamp is in the future')
    items = document['items']
    observations = document['observations']
    if not isinstance(items, list) or not items or len(items) > 10000:
        raise ValueError('expected 1–10000 selected items')
    if not isinstance(observations, list) or len(observations) > 100000:
        raise ValueError('invalid observation list')
    ids, tags = set(), set()
    findings = []
    selected = {}
    def finding(item, field, code, **extra):
        findings.append({'item_id': item['item_id'], 'revision': item['revision'],
                         'tag': item['tag'], 'field': field, 'code': code, **extra})
    for item in items:
        if not isinstance(item, dict) or not {'item_id', 'revision', 'tag', 'fields'} <= item.keys():
            raise ValueError('item identity, revision, tag and fields required')
        if any(not isinstance(item[key], str) or not item[key].strip() for key in ('item_id', 'tag')):
            raise ValueError('item identity/tag must be nonempty strings')
        if type(item['revision']) is not int or item['revision'] < 1 or not isinstance(item['fields'], dict):
            raise ValueError('invalid item revision/fields')
        if item['item_id'] in ids or item['tag'].strip() in tags:
            raise ValueError('duplicate item identity or tag in selected scope')
        ids.add(item['item_id']); tags.add(item['tag'].strip())
        selected[item['item_id']] = item
        for field in ('manufacturer', 'model'):
            if item['fields'].get(field) in (None, ''):
                finding(item, field, 'missing-identity-field')
    by_field = {}
    for observation in observations:
        if not isinstance(observation, dict) or set(observation) != {'item_id', 'field', 'value', 'status', 'source', 'observed_at'}:
            raise ValueError('malformed observation')
        item_id, field = observation['item_id'], observation['field']
        if item_id not in selected or not isinstance(field, str) or not field:
            raise ValueError('observation refers to unknown item or invalid field')
        if observation['status'] not in ('observed', 'unavailable'):
            raise ValueError('invalid observation status')
        source = observation['source']
        if not isinstance(source, dict) or set(source) != {'reference', 'locator'} or any(not isinstance(x, str) or not x.strip() for x in source.values()):
            raise ValueError('source reference and page/field locator required')
        observed_at = timestamp(observation['observed_at'])
        if observed_at > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
            raise ValueError('observation timestamp is in the future')
        by_field.setdefault((item_id, field), []).append((observation, observed_at))
    comparisons = 0
    for item in items:
        fields = set(item['fields']) | {field for item_id, field in by_field if item_id == item['item_id']}
        for field in sorted(fields):
            observed = by_field.get((item['item_id'], field), [])
            usable = []
            for obs, when in observed:
                if obs['status'] == 'unavailable':
                    finding(item, field, 'source-unavailable', source=obs['source'])
                elif mode == 'live' and when < start:
                    finding(item, field, 'stale-observation', source=obs['source'])
                else:
                    usable.append(obs)
            if not usable:
                if item['fields'].get(field) not in (None, ''):
                    finding(item, field, 'not-demonstrated')
                continue
            values = {json.dumps(obs['value'], sort_keys=True, allow_nan=False) for obs in usable}
            if len(values) > 1:
                finding(item, field, 'conflicting-sources', sources=[o['source'] for o in usable])
                continue
            value = usable[0]['value']
            comparisons += 1
            if value is None or value == '':
                finding(item, field, 'source-value-unknown', source=usable[0]['source'])
            elif json.dumps(item['fields'].get(field), sort_keys=True, allow_nan=False) != json.dumps(value, sort_keys=True, allow_nan=False):
                finding(item, field, 'discrepancy', recorded=item['fields'].get(field), observed=value,
                        source=usable[0]['source'], action='review; preserve current record until explicit reconciliation')
    raw = json.dumps(document, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return {'schema_version': 1, 'mode': mode, 'input_sha256': hashlib.sha256(raw).hexdigest(),
            'item_count': len(items), 'compared_fields': comparisons, 'findings': findings,
            'status': 'findings' if findings else 'matches-supplied-observations',
            'retrieval_performed': False, 'specification_mutated': False,
            'legal_compliance': 'not-assessed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 20 * 1024 * 1024:
            raise ValueError('audit input exceeds 20 MiB')
        result = audit(json.loads(args.input.read_text(encoding='utf-8')))
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, f'audit input rejected: {exc}\n')


if __name__ == '__main__':
    main()
