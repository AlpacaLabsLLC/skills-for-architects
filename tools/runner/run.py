#!/usr/bin/env python3
"""Execute one declared local operation from an integrity-checked package."""
import argparse
import contextlib
import importlib.metadata
import importlib.util
import io
import json
from pathlib import Path
import sys
import subprocess
import re

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package import verify

MAX_REQUEST = 4 * 1024 * 1024
MAX_RESULT = 4 * 1024 * 1024


class OperationError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON value')))


def validate(value, schema, label='input'):
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        raise ValueError(label + ': wrong constant')
    if 'anyOf' in schema:
        for option in schema['anyOf']:
            try:
                validate(value, option, label)
                return
            except ValueError:
                pass
        raise ValueError(label + ': invalid alternative')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'number': (int, float), 'boolean': bool, 'null': type(None)}
    expected = schema.get('type')
    if expected and (not isinstance(value, types[expected]) or expected in ('number', 'integer') and isinstance(value, bool)):
        raise ValueError(label + ': expected ' + expected)
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(label + ': unsupported value')
    if isinstance(value, dict):
        properties = schema.get('properties', {})
        if set(schema.get('required', [])) - value.keys():
            raise ValueError(label + ': missing required fields')
        if schema.get('additionalProperties') is False and value.keys() - properties.keys():
            raise ValueError(label + ': unknown fields')
        extra = schema.get('additionalProperties')
        for key, child in value.items():
            validate(child, properties.get(key, extra if isinstance(extra, dict) else {}), label + '.' + key)
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise ValueError(label + ': too few items')
        for child in value:
            validate(child, schema.get('items', {}), label + '[]')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or ('pattern' in schema and not re.search(schema['pattern'], value)):
            raise ValueError(label + ': invalid text')


def registry(root):
    document = read_json(root / 'tools/runner/operations.json')
    rows = list(document['operations'])
    for include in document.get('includes', []):
        if Path(include).is_absolute() or '..' in Path(include).parts:
            raise ValueError('Invalid registry include')
        rows += read_json(root / include)['operations']
    result = {}
    for row in rows:
        if row['id'] in result:
            raise ValueError('Duplicate operation: ' + row['id'])
        result[row['id']] = row
    return result


def runtime(root, spec):
    lock = read_json(root / 'tools/runner/runtime-lock.json')
    if spec.get('platforms') and sys.platform not in spec['platforms']:
        raise OperationError('unsupported_operation', spec.get('unsupported_handoff', 'Operation unavailable on this platform'))
    if '.'.join(map(str, sys.version_info[:3])) != lock['python']:
        raise OperationError('installation_required', 'Use the installed Arch Studio managed Python ' + lock['python'])
    for dependency in spec.get('dependencies', []):
        expected = lock['python_dependencies'][dependency]
        try:
            actual = importlib.metadata.version(dependency)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        if actual != expected:
            raise OperationError('installation_required', 'Missing or different managed dependency: ' + dependency + '==' + expected)


def execute(request, package_manifest):
    operation = request.get('operation') if isinstance(request, dict) else None
    pin = request.get('release_digest') if isinstance(request, dict) else None
    envelope = {'schema_version': 1, 'operation': operation, 'release_digest': pin,
                'workflow_completed': False}
    try:
        if len(json.dumps(request, ensure_ascii=False, allow_nan=False).encode()) > MAX_REQUEST:
            raise OperationError('invalid_request', 'Request exceeds shared CLI/desktop bound')
        if not isinstance(request, dict) or set(request) != {'schema_version', 'operation', 'release_digest', 'input'} or type(request['schema_version']) is not int or request['schema_version'] != 1:
            raise OperationError('invalid_request', 'Expected schema_version, operation, release_digest and input only')
        root = Path(package_manifest).resolve().parent
        try:
            verify(root, read_json(package_manifest), pin)
        except (ValueError, OSError) as error:
            raise OperationError('package_mismatch', str(error)) from error
        operations = registry(root)
        if not isinstance(operation, str) or operation not in operations:
            raise OperationError('unknown_operation', 'Operation is not declared by this package')
        spec = operations[operation]
        validate(request['input'], spec['input_schema'])
        runtime(root, spec)
        module_path = root / spec['module']
        if not module_path.is_relative_to(root) or '..' in module_path.parts:
            raise OperationError('package_mismatch', 'Invalid operation module')
        module_spec = importlib.util.spec_from_file_location('as_operation_' + operation.replace('.', '_'), module_path)
        module = importlib.util.module_from_spec(module_spec)
        with contextlib.redirect_stdout(io.StringIO()):
            module_spec.loader.exec_module(module)
            result = getattr(module, spec['handler'])(operation, request['input'])
        value = {**envelope, 'status': 'ok', 'result': result}
        if len(json.dumps(value, allow_nan=False).encode()) > MAX_RESULT:
            raise OperationError('result_too_large', 'Operation result exceeds bound; inspect the named output files')
        return value
    except (ValueError, TypeError, KeyError, OSError, ImportError, AttributeError, subprocess.TimeoutExpired) as error:
        failure = {**envelope, 'status': 'error', 'error': {'code': getattr(error, 'code', 'operation_failed'), 'message': str(error)[:2000]}}
        if hasattr(error, 'result'):
            failure['result'] = error.result
        return failure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--package-manifest', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.request.stat().st_size > MAX_REQUEST:
            raise ValueError('Request exceeds bound')
        request = read_json(args.request)
        result = execute(request, args.package_manifest)
    except (ValueError, OSError) as error:
        result = {'schema_version': 1, 'status': 'error', 'workflow_completed': False,
                  'error': {'code': 'invalid_request', 'message': str(error)}}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result['status'] == 'ok' else 2


if __name__ == '__main__':
    raise SystemExit(main())
