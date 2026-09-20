#!/usr/bin/env python3
"""Validate declarations and supplied evidence. Never probe, grant, execute or certify a host."""
import argparse
import json
import re
from pathlib import Path, PureWindowsPath
from urllib.parse import urlsplit


def load(root):
    root = Path(root).resolve()
    document = json.loads((root / 'corpus/host-contracts.json').read_text(encoding='utf-8'))
    for key, reference in document['components'].items():
        if not isinstance(reference, str) or Path(reference).is_absolute() or '..' in Path(reference).parts:
            raise ValueError('Unsafe declaration path')
        path = root / reference
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise ValueError('Declaration escapes package')
        document['components'][key] = json.loads(path.read_text(encoding='utf-8'))
    return document


def schema_check(value, rule, schema, path='$'):
    if 'anyOf' in rule:
        for candidate in rule['anyOf']:
            try:
                schema_check(value, candidate, schema, path)
                return
            except ValueError:
                pass
        raise ValueError(path + ': no valid schema alternative')
    if '$ref' in rule:
        node = schema
        for part in rule['$ref'][2:].split('/'):
            node = node[part]
        return schema_check(value, node, schema, path)
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    if rule.get('type') in types and not isinstance(value, types[rule['type']]):
        raise ValueError(path + ': wrong type')
    if rule.get('type') == 'integer' and type(value) is not int:
        raise ValueError(path + ': not an integer')
    if 'const' in rule and (type(value) is not type(rule['const']) or value != rule['const']):
        raise ValueError(path + ': wrong constant')
    if 'enum' in rule and value not in rule['enum']:
        raise ValueError(path + ': unknown value')
    if isinstance(value, str) and len(value.strip()) < rule.get('minLength', 0):
        raise ValueError(path + ': empty string')
    if isinstance(value, str) and 'pattern' in rule and re.search(rule['pattern'], value) is None:
        raise ValueError(path + ': invalid string pattern')
    if isinstance(value, dict):
        if len(value) < rule.get('minProperties', 0) or set(rule.get('required', [])) - value.keys():
            raise ValueError(path + ': missing properties')
        props = rule.get('properties', {})
        extra = rule.get('additionalProperties', True)
        for key, child in value.items():
            if key not in props and extra is False:
                raise ValueError(path + ': unknown property ' + key)
            child_rule = props.get(key, extra if isinstance(extra, dict) else {})
            schema_check(child, child_rule, schema, path + '.' + key)
    if isinstance(value, list):
        if len(value) < rule.get('minItems', 0):
            raise ValueError(path + ': empty array')
        if rule.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise ValueError(path + ': duplicate entries')
        for child in value:
            schema_check(child, rule.get('items', {}), schema, path + '[]')


def validate(document, root):
    root = Path(root)
    schema = json.loads((root / 'schema/host-contracts.schema.json').read_text(encoding='utf-8'))
    schema_check(document, schema, schema)
    for name, profile in document['profiles'].items():
        if profile['mode'] != name:
            raise ValueError('Mode profile identity mismatch: ' + name)
    expected = {'skill:' + p.parent.name: p for p in root.glob('skills/*/SKILL.md')}
    expected.update({'agent:' + p.stem: p for p in root.glob('agents/*.md')})
    if set(document['components']) != set(expected):
        raise ValueError('Missing or stale component declarations: ' + ', '.join(sorted(set(document['components']) ^ set(expected))))
    if not (root / document['policy']).is_file():
        raise ValueError('Shared host policy is missing')
    for key, component in document['components'].items():
        path = expected[key]
        if component['path'] != path.relative_to(root).as_posix():
            raise ValueError(key + ': wrong instruction path')
        execution = component.get('execution')
        if execution is not None:
            # A native declaration identifies a specification, never a local binding.
            if not execution['operations'] and any(mode['mode'] in ('record-read', 'record-write') for mode in component['modes']):
                raise ValueError(key + ': native record modes require their semantic operation scope')
            contract = root / execution['contract']
            if (not contract.resolve().is_relative_to(root.resolve())
                    or contract.is_symlink() or not contract.is_file()):
                raise ValueError(key + ': native semantic contract is missing or escapes package')
        text = path.read_text(encoding='utf-8')
        prefix = '../../' if key.startswith('skill:') else '../'
        own_link = 'host-contract.json' if key.startswith('skill:') else path.stem + '.host-contract.json'
        for link in (prefix + 'docs/host-harness-contract.md', own_link, prefix + 'corpus/host-contracts.json'):
            if '](' + link + ')' not in text:
                raise ValueError(key + ': instruction does not consume shared contract')
        if '`' + key + '`' not in text:
            raise ValueError(key + ': missing declaration selector')
        delegates = key.startswith('agent:') or any(m['mode'] == 'delegate' for m in component['modes'])
        if delegates and component['delegation'] != 'inherit-scope-target-permissions-and-evidence':
            raise ValueError(key + ': delegation must preserve contract')
        seen = set()
        for selection in component['modes']:
            mode = select(document, key, selection['mode'])
            schema_check(mode, schema['$defs']['mode'], schema)
            if mode['mode'] in seen or set(mode['required']) & set(mode['optional']):
                raise ValueError(key + ': duplicate mode or capability')
            seen.add(mode['mode'])
            required = set(mode['required'])
            if (execution is not None and mode['mode'] == 'file-output'
                    and not {'file.read', 'file.write'} <= required):
                raise ValueError(key + ': native file output requires actual readback capabilities')
            if mode['mode'] == 'workbook-edit':
                if not {'spreadsheet.read', 'spreadsheet.edit', 'spreadsheet.features', 'spreadsheet.backup'} <= required or mode['completion'] != 'provider-or-native-readback':
                    raise ValueError(key + ': unsafe workbook edit declaration')
            if mode['mode'] == 'workbook-read' and not {'spreadsheet.read', 'spreadsheet.features'} <= required:
                raise ValueError(key + ': incomplete workbook read declaration')
            if 'canonical-write' in mode['effects'] and not component['owned_records']:
                raise ValueError(key + ': nonowner cannot write canonical records')
            if any(e != 'none' for e in mode['effects']) and mode['permission'] == 'read-within-scope':
                raise ValueError(key + ': write effect requires write authority')
    return {'skills': sum(k.startswith('skill:') for k in expected), 'agents': sum(k.startswith('agent:') for k in expected)}


def select(document, component, mode):
    for entry in document['components'][component]['modes']:
        if entry['mode'] == mode:
            if mode not in document['profiles']:
                raise ValueError('Unknown mode profile: ' + mode)
            selected = dict(document['profiles'][mode], **entry)
            validate_mode(selected)
            return selected
    raise ValueError('Undeclared mode: ' + mode)


def validate_mode(mode):
    """Operation identity fixes its minimum mutation contract, including on direct assessment."""
    writes = {
        'workbook-edit': ('document-edit', 'write-within-scope', 'provider-or-native-readback',
                          {'spreadsheet.read', 'spreadsheet.edit', 'spreadsheet.features', 'spreadsheet.backup'}),
        'record-write': ('canonical-write', 'write-within-scope', 'file-readback', {'file.read', 'file.write'}),
        'file-output': ('artifact-write', 'write-within-scope', 'file-readback', {'file.write'}),
        'render': ('artifact-write', 'write-within-scope', 'artifact-inspection', {'file.write', 'document.render', 'document.inspect'}),
        'image-transform': ('artifact-write', 'write-within-scope', 'artifact-inspection', {'file.read', 'file.write', 'image.read', 'image.transform'}),
        'external-open': ('external-open', 'explicit-outbound', 'source-evidence', {'browser.open'}),
    }
    if mode['mode'] in writes:
        effect, permission, completion, capabilities = writes[mode['mode']]
        if (mode['effects'] != [effect] or mode['permission'] != permission
                or mode['completion'] != completion or not capabilities <= set(mode['required'])):
            raise ValueError('Unsafe mutation declaration: ' + mode['mode'])


def assess(document, component, mode, evidence):
    """Check caller-supplied claims only; the caller must obtain and verify actual tool evidence."""
    contract = select(document, component, mode)
    reasons = []
    capabilities = evidence.get('capabilities', [])
    if not isinstance(capabilities, list) or any(not isinstance(c, str) for c in capabilities):
        raise ValueError('capabilities must be a string list')
    missing = set(contract['required']) - set(capabilities)
    if missing:
        reasons.append('missing capabilities: ' + ', '.join(sorted(missing)))
    target = evidence.get('target')
    if contract['required'] and (not isinstance(target, str) or not target or evidence.get('access_checked') is not True or evidence.get('access_target') != target):
        reasons.append('exact target access is not evidenced')
    writes = any(effect != 'none' for effect in contract['effects'])
    if mode == 'workbook-edit' and evidence.get('destination_kind') not in ('provider', 'local'):
        reasons.append('explicit provider/local destination_kind is required')
    if mode == 'workbook-edit' and evidence.get('destination_kind') == 'local' and isinstance(target, str):
        # URI destinations (including Sheets IDs and HTTPS URLs) cannot be relabeled native files.
        # Windows drive letters are local paths, not provider schemes.
        if urlsplit(target).scheme and not PureWindowsPath(target).is_absolute():
            reasons.append('provider/URI target cannot be declared a local workbook path')
    if writes:
        for name in ('authorized', 'preserved', 'conflicts_resolved'):
            if evidence.get(name) is not True:
                reasons.append(name + ' is not evidenced')
    status = 'blocked' if reasons else 'evidence-conforms'
    if not reasons and writes:
        readback = evidence.get('readback', {})
        if not isinstance(readback, dict):
            raise ValueError('readback must be an object')
        expected_kind = 'provider' if evidence.get('destination_kind') == 'provider' else 'native'
        if readback.get('target') != target or readback.get('fresh') is not True or (mode == 'workbook-edit' and readback.get('kind') != expected_kind):
            status = 'unverified'
            reasons.append('fresh actual destination readback is missing; local export is not provider evidence')
    return {'status': status, 'reasons': reasons, 'execution_verified': False,
            'limitation': 'Declarative checks of supplied evidence only; no actual host tools, permission grant or readback authenticated.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--component')
    parser.add_argument('--mode')
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    try:
        document = load(args.root)
        result = validate(document, args.root)
        if any((args.component, args.mode, args.evidence)):
            if not all((args.component, args.mode, args.evidence)):
                raise ValueError('component, mode and evidence are required together')
            result = assess(document, args.component, args.mode, json.loads(args.evidence.read_text(encoding='utf-8')))
        print(json.dumps(result))
        return 2 if result.get('status') in ('blocked', 'unverified') else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, 'host contract rejected: ' + str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
