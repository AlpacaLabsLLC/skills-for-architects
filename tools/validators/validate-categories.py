#!/usr/bin/env python3
"""Validate portable category contracts and render discovery without dependencies."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def check(value, schema, label):
    """Validate the closed JSON Schema vocabulary used by the bundled schemas."""
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        raise ValueError(f'{label}: wrong constant')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{label}: unsupported value {value}')
    typ = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool}
    if typ and type(value) is not types[typ]:
        raise ValueError(f'{label}: expected {typ}')
    if typ == 'object':
        missing = set(schema.get('required', [])) - value.keys()
        extra = value.keys() - schema.get('properties', {}).keys()
        if missing or (schema.get('additionalProperties') is False and extra):
            raise ValueError(f'{label}: missing {sorted(missing)}; unknown {sorted(extra)}')
        for key, item in value.items():
            if key in schema.get('properties', {}):
                check(item, schema['properties'][key], f'{label}.{key}')
    if typ == 'array':
        if len(value) < schema.get('minItems', 0):
            raise ValueError(f'{label}: empty list')
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise ValueError(f'{label}: duplicates')
        for i, item in enumerate(value):
            check(item, schema.get('items', {}), f'{label}[{i}]')
    if typ == 'string':
        if len(value.strip()) < schema.get('minLength', 0) or ('pattern' in schema and not re.search(schema['pattern'], value)):
            raise ValueError(f'{label}: malformed or blank string')


def local_file(root, value):
    path = Path(value)
    resolved = (root / path).resolve()
    if path.is_absolute() or '..' in path.parts or not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError(f'unsafe or missing package file: {value}')
    return resolved


def acyclic(nodes):
    visiting, visited = set(), set()
    def visit(key):
        if key in visiting:
            raise ValueError(f'dependency cycle: {key}')
        if key in visited:
            return
        if key not in nodes:
            raise ValueError(f'unknown dependency: {key}')
        visiting.add(key)
        for dep in nodes[key]['dependencies']:
            visit(dep)
        visiting.remove(key)
        visited.add(key)
    for key in nodes:
        visit(key)


def validate(root):
    root = Path(root).resolve()
    data = json.loads((root / 'corpus/components.json').read_text())
    schema = json.loads((root / 'schema/components.schema.json').read_text())
    check(data, schema, 'components')
    components = {}
    paths = set()
    prefixes = {'skills': ('skill:', 'skills/'), 'knowledge': ('knowledge:', 'corpus/'), 'tools': ('tool:', 'tools/'), 'studio': ('studio:', 'studio/')}
    for row in data['components']:
        key, path = row['id'], row['path']
        if key in components or path in paths:
            raise ValueError(f'duplicate component identity or canonical path: {key}')
        prefix, base = prefixes[row['category']]
        if not key.startswith(prefix) or not path.startswith(base):
            raise ValueError(f'category owner mismatch: {key}')
        local_file(root, path)
        if row['category'] == 'tools' and row['execution'] in ('instructions', 'reference'):
            raise ValueError(f'tool lacks execution contract: {key}')
        components[key] = row
        paths.add(path)
    acyclic(components)
    expected = {'skill:' + p.parent.name for p in (root / 'skills').glob('*/SKILL.md')}
    if expected != {k for k in components if k.startswith('skill:')}:
        raise ValueError('public skill inventory does not match registry')
    schema = json.loads((root / 'schema/clusters.schema.json').read_text())
    jurisdiction_catalog = json.loads((root / 'corpus/jurisdictions/catalog.json').read_text())
    jurisdictions = {row['id'] for row in jurisdiction_catalog['jurisdictions']}
    clusters = {}
    membership = set()
    for file in sorted((root / 'clusters').glob('*.json')):
        row = json.loads(file.read_text())
        check(row, schema, file.name)
        key = row['id']
        if key in clusters or file.stem != key.removeprefix('cluster:'):
            raise ValueError(f'duplicate or mismatched cluster ID: {key}')
        for member in row['members']:
            if member not in components:
                raise ValueError(f'dangling member {member} in {key}')
            membership.add(member)
        for jurisdiction in row['coverage']['jurisdictions']:
            if jurisdiction not in jurisdictions:
                raise ValueError(f'unknown jurisdiction {jurisdiction} in {key}')
        for evaluation in row['evaluations']:
            local_file(root, evaluation['path'])
        if row['coverage']['workflow_validated'] and not any(e['kind'] == 'workflow' for e in row['evaluations']):
            raise ValueError(f'workflow claim lacks workflow evidence: {key}')
        clusters[key] = row
    if not clusters or not expected <= membership:
        raise ValueError(f'public skills without cluster membership: {sorted(expected - membership)}')
    acyclic(clusters)
    return components, clusters


def render(components, clusters):
    lines = ['# Practice cluster discovery', '', '<!-- Generated by tools/validators/validate-categories.py --write-guide. Do not edit. -->', '',
             'Clusters assemble shared components; they are not agents or project-record stores.',
             'A listed procedure is not proof of executable tooling, legal coverage or a validated workflow.', '',
             '| Cluster | Public procedures | Geographic declaration |', '|---|---|---|']
    for key, row in sorted(clusters.items()):
        skills = ', '.join('`' + x.removeprefix('skill:') + '`' for x in row['members'] if x.startswith('skill:'))
        geo = ', '.join(row['coverage']['jurisdictions']) or 'No cluster-wide coverage; inspect individual skill'
        lines.append(f"| [{row['name']}](../clusters/{key.removeprefix('cluster:')}.json) | {skills} | {geo} |")
    lines += ['', '## Ownership and capability checks', '',
              'The [component registry](../corpus/components.json) maps stable IDs to canonical package files.',
              'Read each manifest’s limitations, host requirements and evaluations before selecting a workflow.',
              'Only explicit workflow evidence can establish a validated workflow; contract tests establish structure.', '',
              'Run `python3 tools/validators/validate-categories.py --check-guide` to validate this view.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write-guide', action='store_true')
    mode.add_argument('--check-guide', action='store_true')
    args = parser.parse_args()
    try:
        components, clusters = validate(args.root)
        guide = render(components, clusters)
        target = args.root / 'docs/practice-clusters.md'
        if args.write_guide:
            target.write_text(guide, encoding='utf-8')
        if args.check_guide and target.read_text(encoding='utf-8') != guide:
            raise ValueError('generated practice-cluster guide is stale')
        print(json.dumps({'valid': True, 'components': len(components), 'clusters': len(clusters), 'workflowValidated': False}))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f'category validation failed: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
