#!/usr/bin/env python3
"""Validate Arch Studio declarations and assess supplied geographic context; never fetch, geocode or grant execution."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
NYC = 'jurisdiction:us-ny-nyc'
LIMITATIONS = {
    'portable': 'The method has no built-in geographic selection. Its sources, market facts, standards and regulatory assertions still need task-specific checks; this is not worldwide substantive coverage.',
    'site-research': 'Location-specific source research only. No complete geographic dataset, hazard coverage or validated site conclusion is established.',
    'nyc-records': 'Existing NYC procedure only. Verify exact property, issuing agency, dataset coverage and observation period; absence of records is not clearance.',
    'nyc-zoning': 'Existing NYC zoning procedure only. Every controlling provision, edition, amendment, date and site condition remains to be verified.',
    'jurisdiction-calculation': 'Jurisdiction-dependent occupant-load method. Bundled IBC factors are comparison data, never proof of adoption or a substitute for local rules.',
    'input-report': 'Render supplied report evidence and limitations without recalculating or certifying zoning applicability.',
    'us-explanation': 'US professional-practice orientation only. No workspace is required; no local legal or worldwide practice claim is established.',
    'source-health': 'Registered source reachability and identity only. Reachable or indexed sources do not establish geographic, legal or execution applicability.',
}


def check(value, rule, schema, label='$'):
    """Closed subset used by this schema; reject unsupported validation keywords."""
    allowed = {'$schema', 'title', '$defs', '$ref', 'type', 'const', 'enum', 'required', 'properties',
               'additionalProperties', 'minProperties', 'items', 'minItems', 'maxItems', 'uniqueItems',
               'minLength', 'maxLength', 'pattern'}
    if set(rule) - allowed:
        raise ValueError('Unsupported schema keyword')
    if '$ref' in rule:
        node = schema
        for part in rule['$ref'].removeprefix('#/').split('/'):
            node = node[part]
        return check(value, node, schema, label)
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}
    declared = rule.get('type', [])
    declared = declared if isinstance(declared, list) else [declared]
    if declared and not any(type(value) is types[t] for t in declared):
        raise ValueError(label + ': wrong type')
    if 'const' in rule and (type(value) is not type(rule['const']) or value != rule['const']):
        raise ValueError(label + ': wrong constant')
    if 'enum' in rule and value not in rule['enum']:
        raise ValueError(label + ': unsupported value')
    if isinstance(value, str):
        if len(value.strip()) < rule.get('minLength', 0) or len(value) > rule.get('maxLength', 4096):
            raise ValueError(label + ': invalid length')
        if 'pattern' in rule and not re.fullmatch(rule['pattern'], value):
            raise ValueError(label + ': invalid format')
    if isinstance(value, dict):
        if len(value) < rule.get('minProperties', 0) or set(rule.get('required', [])) - value.keys():
            raise ValueError(label + ': missing properties')
        properties, extra = rule.get('properties', {}), rule.get('additionalProperties', True)
        for key, child in value.items():
            if key not in properties and extra is False:
                raise ValueError(label + ': unknown property ' + key)
            check(child, properties.get(key, extra if isinstance(extra, dict) else {}), schema, label + '.' + key)
    if isinstance(value, list):
        if len(value) < rule.get('minItems', 0) or len(value) > rule.get('maxItems', 128):
            raise ValueError(label + ': invalid array length')
        if rule.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise ValueError(label + ': duplicate entries')
        for child in value:
            check(child, rule.get('items', {}), schema, label + '[]')


def load(root=ROOT):
    return json.loads((Path(root) / 'corpus/geographic-applicability.json').read_text(encoding='utf-8'))


def validate(document, root=ROOT):
    root = Path(root).resolve()
    schema = json.loads((root / 'schema/geographic-applicability.schema.json').read_text(encoding='utf-8'))
    check(document, schema, schema)
    inventory = json.loads((root / 'corpus/components.json').read_text(encoding='utf-8'))
    expected = {row['id'] for row in inventory['components'] if row['category'] in ('skills', 'tools')}
    if set(document['components']) != expected:
        raise ValueError('Missing or stale skill/tool geographic declaration')
    seen = set()
    for reference in [{'path': document['policy']}, *document['references']]:
        relative = Path(reference['path'])
        target = root / relative
        if relative.is_absolute() or '..' in relative.parts or not target.resolve().is_relative_to(root) or target.is_symlink() or not target.exists():
            raise ValueError('Unsafe or missing applicability reference')
        if relative.as_posix() in seen:
            raise ValueError('Duplicate applicability reference')
        seen.add(relative.as_posix())
        if reference.get('effective_date') is not None:
            date.fromisoformat(reference['effective_date'])
    return {'valid': True, 'components': len(expected), 'legal_applicability': 'unverified'}


def assess(document, request, root=ROOT):
    validate(document, root)
    schema = json.loads((Path(root) / 'schema/geographic-applicability.schema.json').read_text(encoding='utf-8'))
    check(request, schema['$defs']['request'], schema)
    component = request['component']
    if component not in document['components']:
        raise ValueError('Unknown skill/tool component')
    for value in [request.get('as_of'), request.get('input_report', {}).get('as_of')]:
        if value is not None:
            date.fromisoformat(value)
    profile = document['components'][component]
    result = {'schema_version': 1, 'component': component, 'profile': profile,
              'status': 'procedure-supported', 'reasons': [], 'legal_applicability': 'unverified',
              'source_verification': 'not-assessed' if profile in ('portable', 'us-explanation') else 'required',
              'execution_verified': False, 'evidence_authenticated': False, 'limitation': LIMITATIONS[profile]}

    def missing(reason):
        result['status'] = 'context-required'
        result['reasons'].append(reason)

    required = set(request.get('material_fields', []))
    if profile in ('nyc-zoning', 'jurisdiction-calculation'):
        required.update(('as_of', 'use', 'work_scope'))
    for field in sorted(required):
        if not request.get(field):
            missing('Material context missing: ' + field)

    if profile in ('portable', 'us-explanation', 'source-health'):
        return result
    # Studio defaults never resolve a site. The caller must supply normalized,
    # sourced context; this checker does not interpret place names or geocode IDs.
    locations = [item for item in request['locations'] if item['origin'] != 'studio-default']
    if not locations or any(item['status'] != 'resolved' for item in locations):
        missing('Resolve the site location from request, project or input-report evidence; studio defaults and ambiguous locations are insufficient.')
        return result
    if len({(item['jurisdiction'], item['target']) for item in locations}) != 1:
        missing('Supplied locations conflict; resolve the intended site and jurisdiction without silently overriding another source.')
        return result
    result['location'] = locations[0]
    jurisdiction = locations[0]['jurisdiction']
    if profile in ('nyc-records', 'nyc-zoning') and jurisdiction != NYC:
        if jurisdiction in ('jurisdiction:us', 'jurisdiction:us-ny'):
            missing('Resolve whether the site is in New York City; country/state alone does not establish NYC applicability.')
        else:
            result['status'] = 'unsupported'
            result['reasons'].append('This procedure is NYC-only; do not substitute NYC datasets or rules for another location.')
        return result
    if profile == 'jurisdiction-calculation' and jurisdiction != 'jurisdiction:us' and not jurisdiction.startswith('jurisdiction:us-'):
        if not request.get('local_rule_reference'):
            missing('Outside the US, obtain the local occupancy table/reference; do not load or use bundled IBC factors.')
    if profile == 'input-report':
        if 'input_report' not in request:
            missing('Provide the selected input report, its date or explicit unknown, and its limitations; rendering does not establish applicability.')
        else:
            result['input_report'] = request['input_report']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--assess', action='store_true', help='Read bounded request JSON from stdin; otherwise validate declarations only')
    args = parser.parse_args()
    try:
        document = load(args.root)
        if args.assess:
            raw = sys.stdin.buffer.read(65537)
            if len(raw) > 65536:
                raise ValueError('Supplied context exceeds limit')
            result = assess(document, json.loads(raw), args.root)
        else:
            result = validate(document, args.root)
        print(json.dumps(result))
        return 2 if result.get('status') in ('context-required', 'unsupported') else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        # Do not echo supplied targets, source contents or parser exception text.
        print('geographic applicability rejected: invalid declaration or supplied context', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
