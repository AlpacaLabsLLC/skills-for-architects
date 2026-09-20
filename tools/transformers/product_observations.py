#!/usr/bin/env python3
"""Validate unadopted product evidence and propose explicitly bound item changes; no writes/fetches."""
import argparse
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
import uuid

SCHEMA = Path(__file__).resolve().parents[2] / 'schema/product-observation.schema.json'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')


def preflight_schema(rule):
    """Reject unsupported assertions even in branches the instance never visits."""
    supported = {'$schema', '$id', '$defs', 'title', 'description', '$ref', 'oneOf', 'allOf', 'if', 'then',
                 'type', 'const', 'enum', 'minimum', 'minLength', 'pattern', 'format', 'required',
                 'minProperties', 'properties', 'additionalProperties', 'minItems', 'maxItems', 'uniqueItems', 'items'}
    if set(rule) - supported or rule.get('format') not in (None, 'uuid', 'date-time', 'uri'):
        raise ValueError('Unsupported schema assertion; update validator before using this schema')
    if '$ref' in rule and set(rule) - {'$ref', '$schema', '$id', '$defs', 'title', 'description'}:
        raise ValueError('Assertion siblings of $ref are unsupported')
    for keyword in ('$defs', 'properties'):
        for child in rule.get(keyword, {}).values():
            preflight_schema(child)
    for keyword in ('oneOf', 'allOf'):
        for child in rule.get(keyword, []):
            preflight_schema(child)
    for keyword in ('if', 'then', 'items', 'additionalProperties'):
        if isinstance(rule.get(keyword), dict):
            preflight_schema(rule[keyword])


def check(value, rule, schema, path='$'):
    """Preflight the whole schema before evaluating instance-dependent branches."""
    preflight_schema(schema)
    if rule is not schema:
        preflight_schema(rule)
    return _check(value, rule, schema, path)


def _check(value, rule, schema, path):
    if '$ref' in rule:
        node = schema
        if rule['$ref'] != '#':
            for name in rule['$ref'][2:].split('/'):
                node = node[name]
        return _check(value, node, schema, path)
    if 'oneOf' in rule:
        matches = 0
        for option in rule['oneOf']:
            try:
                _check(value, option, schema, path)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError(path + ': field must match exactly one typed evidence variant')
    for extra in rule.get('allOf', []):
        _check(value, extra, schema, path)
    if 'if' in rule:
        try:
            _check(value, rule['if'], schema, path)
        except ValueError:
            pass
        else:
            _check(value, rule.get('then', {}), schema, path)
    tests = {'object': lambda v: type(v) is dict, 'array': lambda v: type(v) is list,
             'string': lambda v: type(v) is str, 'null': lambda v: v is None,
             'integer': lambda v: type(v) is int,
             'number': lambda v: type(v) is int or (type(v) is float and math.isfinite(v)),
             'boolean': lambda v: type(v) is bool}
    if 'type' in rule:
        choices = rule['type'] if isinstance(rule['type'], list) else [rule['type']]
        if not any(tests[name](value) for name in choices):
            raise ValueError(path + ': wrong type')
    if 'const' in rule and (type(value) is not type(rule['const']) or value != rule['const']):
        raise ValueError(path + ': wrong constant')
    if 'enum' in rule and value not in rule['enum']:
        raise ValueError(path + ': unknown value')
    if type(value) in (int, float) and 'minimum' in rule and value < rule['minimum']:
        raise ValueError(path + ': value below minimum')
    if isinstance(value, str):
        if len(value.strip()) < rule.get('minLength', 0) or ('pattern' in rule and not re.fullmatch(rule['pattern'], value)):
            raise ValueError(path + ': malformed string')
        if rule.get('format') == 'uuid':
            try:
                if str(uuid.UUID(value)) != value:
                    raise ValueError('noncanonical UUID')
            except (ValueError, AttributeError) as error:
                raise ValueError(path + ': canonical UUID required') from error
        if rule.get('format') == 'date-time':
            try:
                stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if stamp.tzinfo is None or stamp > datetime.now(timezone.utc) + timedelta(minutes=5):
                    raise ValueError('timestamp requires timezone and cannot be in the future')
            except ValueError as error:
                raise ValueError(path + ': invalid observation time') from error
        if rule.get('format') == 'uri':
            url = urlsplit(value)
            if url.scheme not in ('https', 'http') or not url.netloc or url.username or url.password:
                raise ValueError(path + ': HTTP(S) image reference without credentials required')
    if isinstance(value, dict):
        if set(rule.get('required', [])) - value.keys() or len(value) < rule.get('minProperties', 0):
            raise ValueError(path + ': missing properties')
        properties = rule.get('properties', {})
        additional = rule.get('additionalProperties', True)
        for name, child in value.items():
            if name not in properties and additional is False:
                raise ValueError(path + ': unknown property ' + name)
            _check(child, properties.get(name, additional if isinstance(additional, dict) else {}), schema, path + '.' + name)
    if isinstance(value, list):
        if len(value) < rule.get('minItems', 0) or len(value) > rule.get('maxItems', len(value)):
            raise ValueError(path + ': invalid array length')
        if rule.get('uniqueItems') and len({canonical(v) for v in value}) != len(value):
            raise ValueError(path + ': duplicate values')
        for child in value:
            _check(child, rule.get('items', {}), schema, path + '[]')


def validate(document):
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    canonical(document)
    check(document, schema, schema)
    if document['source']['kind'] == 'url':
        url = urlsplit(document['source']['reference'])
        if url.scheme not in ('http', 'https') or not url.netloc or url.username or url.password:
            raise ValueError('URL source requires an HTTP(S) reference without credentials')
    return {'valid': True, 'observation_id': document['observation_id'], 'sha256': hashlib.sha256(canonical(document)).hexdigest(),
            'adoption_performed': False, 'retrieval_performed': False, 'specification_mutated': False}


def evidence_value(field):
    if field['value'] is None:
        return None
    if field['kind'] == 'price':
        return {'amount': field['value'], 'currency': field['currency'], 'basis': field['price_basis']}
    if field['kind'] == 'quantity':
        return {'value': field['value'], 'unit': field['unit'], 'meaning': field['meaning']}
    if field['kind'] == 'image':
        return {'url': field['value'], 'variant_match': field['variant_match']}
    return field['value']


def validate_batch(documents):
    """Validate every producer envelope; reject the whole batch without writes."""
    if not isinstance(documents, list) or not documents:
        raise ValueError('Nonempty array of producer observations required')
    results, ids = [], set()
    for number, document in enumerate(documents):
        try:
            result = validate(document)
            if result['observation_id'] in ids:
                raise ValueError('Duplicate observation ID')
            ids.add(result['observation_id'])
            results.append(result)
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError('Observation index ' + str(number) + ': ' + str(error)) from error
    return dict(valid=True, count=len(results), observations=results, adoption_performed=False,
                retrieval_performed=False, specification_mutated=False)


def usable(field):
    if field['status'] != 'observed' or field['variant_match'] != 'exact' or field['value'] in (None, ''):
        return False
    if field['kind'] == 'price' and (not field['currency'] or not field['price_basis']):
        return False
    if field['kind'] == 'quantity' and (not field['unit'] or not field['meaning']):
        return False
    return True


def adapt(observations, items, bindings):
    document = dict(schema_version=1, observations=observations, items=items, bindings=bindings)
    canonical(document)
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    check(document, schema['$defs']['adapter'], schema)
    by_observation, by_item = {}, {}
    for observation in observations:
        validate(observation)
        oid = observation['observation_id']
        if oid in by_observation:
            raise ValueError('Duplicate observation ID')
        by_observation[oid] = observation
    tags = set()
    for item in items:
        if any(Path(ref).is_absolute() or '..' in Path(ref).parts for ref in item['decision_refs']):
            raise ValueError('Decision references must be project-relative links')
        if item['item_id'] in by_item or item['tag'] in tags:
            raise ValueError('Duplicate item identity or tag')
        by_item[item['item_id']] = item
        tags.add(item['tag'])
    candidates, projected, notices, used, conflicts = {}, [], [], set(), []
    for binding in bindings:
        oid, iid = binding['observation_id'], binding['item_id']
        if oid not in by_observation or iid not in by_item:
            raise ValueError('Binding refers to an unknown observation or selected item')
        if binding['expected_revision'] != by_item[iid]['revision']:
            raise ValueError('Stale item revision; reread and bind again')
        observation = by_observation[oid]
        identity_conflicts = [name for name, value in observation['product'].items()
                              if value not in (None, '') and by_item[iid]['fields'].get(name) not in (None, '')
                              and canonical(value) != canonical(by_item[iid]['fields'][name])]
        if identity_conflicts:
            conflicts.append({'item_id': iid, 'observation_id': oid, 'code': 'product-identity-conflict',
                              'fields': identity_conflicts})
        available = {f['field'] for f in observation['fields']}
        if set(binding['fields']) - available:
            raise ValueError('Binding selects an absent observation field')
        for source_field, target_field in binding['fields'].items():
            token = (oid, iid, source_field, target_field)
            if token in used:
                raise ValueError('Duplicate field binding')
            used.add(token)
            for field in (f for f in observation['fields'] if f['field'] == source_field):
                value = evidence_value(field)
                status = 'unavailable' if identity_conflicts or field['status'] in ('unavailable', 'inferred') or field['variant_match'] != 'exact' else 'observed'
                source = {'reference': observation['source']['reference'], 'locator': field['locator']}
                projected.append(dict(item_id=iid, field=target_field, value=value, status=status, source=source,
                                      observed_at=observation['observed_at']))
                if usable(field) and not identity_conflicts:
                    candidates.setdefault((iid, target_field), []).append((value, observation, field))
                else:
                    notices.append({'item_id': iid, 'field': target_field, 'observation_id': oid,
                                    'code': 'not-eligible-for-record-proposal', 'status': field['status'],
                                    'variant_match': field['variant_match']})
    proposed = copy.deepcopy(items)
    output_items = {i['item_id']: i for i in proposed}
    for (iid, field_name), values in candidates.items():
        distinct = {canonical(value) for value, _, _ in values}
        if len(distinct) != 1:
            conflicts.append({'item_id': iid, 'field': field_name, 'code': 'conflicting-observations',
                              'observed': [value for value, _, _ in values]})
            continue
        value, observation, field = values[0]
        item = output_items[iid]
        if field_name in item['fields']:
            if canonical(item['fields'][field_name]) != canonical(value):
                conflicts.append({'item_id': iid, 'field': field_name, 'code': 'existing-value-requires-resolution',
                                  'recorded': item['fields'][field_name], 'observed': value})
            continue
        item['fields'][field_name] = copy.deepcopy(value)
        item['provenance'][field_name] = {'status': 'supplied', 'source': observation['source']['reference'],
                                        'retrieved_at': observation['observed_at'],
                                        'note': 'Observation ' + observation['observation_id'] + ' at ' + field['locator'] + '; host evidence, not independently verified'}
    return {'schema_version': 1, 'input_sha256': hashlib.sha256(canonical(document)).hexdigest(),
            'audit_observations': projected, 'record_proposal': {'items': proposed},
            'expected_item_revisions': {i['item_id']: i['revision'] for i in items},
            'conflicts': conflicts, 'notices': notices, 'requires_review': True,
            'adoption_performed': False, 'retrieval_performed': False, 'specification_mutated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'validate-batch', 'adapt'))
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 20 * 1024 * 1024:
            raise ValueError('Input exceeds 20 MiB')
        document = json.loads(args.input.read_text(encoding='utf-8'))
        if args.command == 'validate':
            result = validate(document)
        elif args.command == 'validate-batch':
            result = validate_batch(document)
        else:
            if not isinstance(document, dict) or set(document) != {'schema_version', 'observations', 'items', 'bindings'} or type(document['schema_version']) is not int or document['schema_version'] != 1:
                raise ValueError('Invalid adapter envelope')
            result = adapt(document['observations'], document['items'], document['bindings'])
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, 'observation rejected: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
