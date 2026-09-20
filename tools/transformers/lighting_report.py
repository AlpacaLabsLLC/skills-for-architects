#!/usr/bin/env python3
"""Normalize explicit lighting-report observations; no PDF parsing or inventory inference."""
import argparse
import copy
import json
import math
from pathlib import Path
import re


def fields(value, required, label):
    if not isinstance(value, dict):
        raise ValueError(f'{label}: expected object')
    missing, extra = set(required) - value.keys(), value.keys() - set(required)
    if missing or extra:
        raise ValueError(f'{label}: missing {sorted(missing)}; unknown {sorted(extra)}')


def text(value, label, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label}: expected nonblank string' + (' or null' if nullable else ''))


def number(value, label, nonnegative=False):
    if value is None:
        return
    try:
        valid = type(value) in (int, float) and math.isfinite(value) and (not nonnegative or value >= 0)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f'{label}: expected finite ' + ('nonnegative ' if nonnegative else '') + 'number or null')


def source(value, label):
    fields(value, ('document_sha256', 'physical_page', 'printed_page', 'locator'), label)
    if not isinstance(value['document_sha256'], str) or not re.fullmatch('[a-f0-9]{64}', value['document_sha256']):
        raise ValueError(f'{label}.document_sha256: expected 64 lowercase hexadecimal characters')
    if type(value['physical_page']) is not int or value['physical_page'] < 1:
        raise ValueError(f'{label}.physical_page: expected one-based positive integer')
    text(value['printed_page'], f'{label}.printed_page', nullable=True)
    text(value['locator'], f'{label}.locator')


def context(row, label):
    fields(row['scope'], ('kind', 'id'), f'{label}.scope')
    if row['scope']['kind'] not in ('room', 'scene', 'report', 'custom'):
        raise ValueError(f'{label}.scope.kind: expected room, scene, report or custom')
    text(row['scope']['id'], f'{label}.scope.id')
    text(row['room'], f'{label}.room', nullable=True)
    text(row['surface'], f'{label}.surface', nullable=True)
    fields(row['scene'], ('status', 'name'), f'{label}.scene')
    status = row['scene']['status']
    if status not in ('reported', 'not-reported', 'not-applicable'):
        raise ValueError(f'{label}.scene.status: expected reported, not-reported or not-applicable')
    if status == 'reported':
        text(row['scene']['name'], f'{label}.scene.name')
    elif row['scene']['name'] is not None:
        raise ValueError(f'{label}.scene.name: must be null unless scene is reported')
    source(row['source'], f'{label}.source')


def normalize(request):
    """Keep results and observations; consolidate only asserted identical inventory context.

    The host establishes inventory identity from source inspection. Equal quantities, matching
    labels or calculation surfaces never establish it here. There is deliberately no grand total
    or automatic projection to a downstream schedule key.
    """
    fields(request, ('schema_version', 'inventory_observations', 'calculation_results'), 'request')
    if type(request['schema_version']) is not int or request['schema_version'] != 1:
        raise ValueError('schema_version: expected 1; legacy rows require an explicit reviewed conversion')
    for name in ('inventory_observations', 'calculation_results'):
        if not isinstance(request[name], list):
            raise ValueError(f'{name}: expected array')
    if not request['inventory_observations'] and not request['calculation_results']:
        raise ValueError('request: at least one observation or calculation result required')
    common = ('scope', 'room', 'scene', 'surface', 'source')
    groups, ids = {}, set()
    for index, row in enumerate(request['inventory_observations']):
        label = f'inventory_observations[{index}]'
        fields(row, common + ('observation_id', 'inventory_id', 'identity_evidence', 'tag',
                              'variant', 'quantity', 'raw_quantity', 'unit'), label)
        context(row, label)
        for name in ('observation_id', 'tag', 'unit'):
            text(row[name], f'{label}.{name}')
        for name in ('inventory_id', 'variant', 'raw_quantity'):
            text(row[name], f'{label}.{name}', nullable=True)
        number(row['quantity'], f'{label}.quantity', nonnegative=True)
        if row['observation_id'] in ids:
            raise ValueError(f'{label}.observation_id: duplicate observation ID')
        ids.add(row['observation_id'])
        identity = row['inventory_id']
        evidence = row['identity_evidence']
        if identity is None:
            if evidence is not None:
                raise ValueError(f'{label}.identity_evidence: must be null for unresolved inventory_id')
            # Even identical unidentified rows remain separate; unknown identity is not a key.
            key = ('unresolved', index)
        else:
            fields(evidence, ('source', 'basis'), f'{label}.identity_evidence')
            source(evidence['source'], f'{label}.identity_evidence.source')
            text(evidence['basis'], f'{label}.identity_evidence.basis')
            if evidence['source']['document_sha256'] != row['source']['document_sha256']:
                raise ValueError(f'{label}.identity_evidence.source.document_sha256: must match this report version')
            if row['scope']['kind'] == 'room' and row['room'] is None:
                raise ValueError(f'{label}.room: resolved room inventory requires a reported room')
            if row['scope']['kind'] == 'scene' and row['scene']['status'] != 'reported':
                raise ValueError(f'{label}.scene: resolved scene inventory requires a reported scene')
            # Surface and observation page are evidence locations, never additive inventory axes.
            key = ('resolved', row['source']['document_sha256'], row['scope']['kind'], row['scope']['id'],
                   row['room'], row['scene']['status'], row['scene']['name'], row['variant'],
                   row['tag'], row['unit'], identity)
        if key not in groups:
            groups[key] = {name: copy.deepcopy(row[name]) for name in
                           ('inventory_id', 'scope', 'room', 'scene', 'tag', 'variant', 'unit')}
            groups[key]['document_sha256'] = row['source']['document_sha256']
            groups[key]['observations'] = []
        groups[key]['observations'].append(copy.deepcopy(row))
    for group in groups.values():
        values = [row['quantity'] for row in group['observations']]
        known = set(value for value in values if value is not None)
        status = ('unresolved-identity' if group['inventory_id'] is None else
                  'conflict' if len(known) > 1 else
                  'unknown' if None in values else 'resolved')
        group.update(status=status, quantity=values[0] if status == 'resolved' else None)

    ids = set()
    for index, row in enumerate(request['calculation_results']):
        label = f'calculation_results[{index}]'
        fields(row, common + ('result_id', 'metric', 'value', 'raw_value', 'unit', 'condition'), label)
        context(row, label)
        for name in ('result_id', 'metric'):
            text(row[name], f'{label}.{name}')
        for name in ('raw_value', 'unit', 'condition'):
            text(row[name], f'{label}.{name}', nullable=True)
        number(row['value'], f'{label}.value')
        if row['result_id'] in ids:
            raise ValueError(f'{label}.result_id: duplicate result ID')
        ids.add(row['result_id'])
    return dict(schema_version=1, inventory=list(groups.values()),
                calculation_results=copy.deepcopy(request['calculation_results']),
                source_verified=False, coverage_verified=False,
                verification='Validated supplied observations and asserted inventory identities only; host source review required')


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.input.read_text(encoding='utf-8'), object_pairs_hook=unique_keys)
        print(json.dumps(normalize(request), ensure_ascii=False, allow_nan=False, indent=2))
    except (ValueError, TypeError, OSError) as error:
        parser.exit(2, f'lighting report rejected: {error}\n')


if __name__ == '__main__':
    main()
