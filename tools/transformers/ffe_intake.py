#!/usr/bin/env python3
"""Write a create-only FF&E input manifest from explicitly selected project sources."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit, parse_qsl

_identity_spec = importlib.util.spec_from_file_location('as_intake_product_identity', Path(__file__).with_name('product_identity.py'))
identity = importlib.util.module_from_spec(_identity_spec)
_identity_spec.loader.exec_module(identity)


def required_fields(value, expected, field):
    if not isinstance(value, dict):
        raise ValueError(f'{field}: expected object')
    for name in sorted(set(expected) - value.keys()):
        raise ValueError(f'{field}.{name}: required field missing')
    extra = value.keys() - set(expected)
    if extra:
        raise ValueError(f'{field}: unknown fields {sorted(extra)}')


def package_path(root, relative, required=True):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('expected a project-relative path')
    path = root / relative
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlink source/destination is not supported')
    if not path.resolve().is_relative_to(root):
        raise ValueError('path escapes project')
    if required and not path.is_file():
        raise ValueError('source is missing or not a file')
    return path


def manifest(project, document, *, standalone=False):
    if Path(project).is_symlink():
        raise ValueError('symlink project root is not supported')
    root = Path(project).resolve()
    if not root.is_dir():
        raise ValueError('authorized output root must exist')
    if standalone and (not isinstance(document, dict) or document.get('mode') != 'one-off'):
        raise ValueError('standalone workspace permits one-off mode only')
    if not standalone and (not (root / 'PROJECT.md').is_file() or (root / 'PROJECT.md').is_symlink()):
        raise ValueError('resolve a project before FF&E intake')
    required = {'schema_version', 'mode', 'job_id', 'sources', 'selected_tags', 'template', 'record_basis', 'supersedes', 'actor', 'reason'}
    required_fields(document, required, 'intake')
    if type(document['schema_version']) is not int or document['schema_version'] != 1:
        raise ValueError('schema_version: expected intake version 1')
    if document['mode'] not in ('one-off', 'adopted'):
        raise ValueError('mode: explicit one-off or adopted mode required')
    for field in ('actor', 'reason'):
        if not isinstance(document[field], str) or not document[field].strip():
            raise ValueError(f'{field}: nonblank string required')
    job = document['job_id']
    if not isinstance(job, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', job):
        raise ValueError('job_id: expected 1–80 ASCII letters/digits/underscore/hyphen starting with letter or digit; product tags have a separate contract')
    tags = document['selected_tags']
    if not isinstance(tags, list) or not tags:
        raise ValueError('selected_tags: nonempty array of exact product IDs required')
    seen_tags = set()
    for index, tag in enumerate(tags):
        identity.validate_tag(tag, f'selected_tags[{index}]')
        if tag in seen_tags:
            raise ValueError(f'selected_tags[{index}]: duplicate exact product identity')
        seen_tags.add(tag)
    if document['mode'] == 'one-off' and document['record_basis'] is not None:
        raise ValueError('one-off inputs cannot imply adopted record authority')
    if document['mode'] == 'adopted':
        basis = document['record_basis']
        if not isinstance(basis, dict) or set(basis) != {'schedule_id', 'revision', 'hash'} or type(basis['revision']) is not int or basis['revision'] < 1:
            raise ValueError('adopted input requires a pinned record basis')
        spec = importlib.util.spec_from_file_location('ffe_records', Path(__file__).resolve().parents[1] / 'workspace/ffe_records.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        schedule = module.read_schedule(root, basis['schedule_id'], basis['revision'])
        if schedule['hash'] != basis['hash'] or not set(tags) <= {x['tag'] for x in schedule['items']}:
            raise ValueError('record basis or selection mismatch')
    sources = document['sources']
    if not isinstance(sources, list) or not sources:
        raise ValueError('sources: nonempty source bundle required')
    ids = set()
    verified = []
    for index, source in enumerate(sources):
        label = f'sources[{index}]'
        required_fields(source, {'id', 'kind', 'reference', 'sha256', 'status'}, label)
        if not isinstance(source['id'], str) or not source['id'] or source['id'] in ids:
            raise ValueError(f'{label}.id: unique nonempty source ID required')
        ids.add(source['id'])
        if source['status'] not in ('available', 'unavailable'):
            raise ValueError(f'{label}.status: expected available or unavailable')
        digest = source['sha256']
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest)):
            raise ValueError(f'{label}.sha256: expected 64 lowercase hexadecimal characters or explicit null')
        if not isinstance(source['reference'], str) or not source['reference']:
            raise ValueError(f'{label}.reference: nonempty file path or URL required')
        if source['kind'] == 'file':
            try:
                path = package_path(root, source['reference'], required=source['status'] == 'available')
            except ValueError as error:
                raise ValueError(f'{label}.reference: {error}') from error
            if source['status'] == 'available':
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest is not None and digest != actual:
                    raise ValueError(f'{label}.sha256: source hash mismatch; reread the selected file')
                source = dict(source, sha256=actual)
        elif source['kind'] == 'url':
            url = urlsplit(source['reference'])
            if url.scheme != 'https' or not url.netloc or url.username or url.password or any(re.search('token|secret|password|authorization|api.?key', key, re.I) for key, _ in parse_qsl(url.query)):
                raise ValueError(f'{label}.reference: source URL must be HTTPS without credentials')
            if source['status'] == 'available' and digest is None:
                raise ValueError(f'{label}.sha256: available URL source requires a host-captured content hash')
        else:
            raise ValueError(f'{label}.kind: expected file or url')
        verified.append(source)
    template = document['template']
    if template is not None and template not in ids:
        raise ValueError('template must reference an input source ID')
    supersedes = document['supersedes']
    if supersedes is not None:
        if not isinstance(supersedes, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', supersedes) or supersedes == job:
            raise ValueError('invalid superseded job ID')
        previous = json.loads(package_path(root, f'ffe/jobs/{supersedes}/input-manifest.json').read_text())
        if not isinstance(previous, dict) or set(previous) != required | {'input_hash'}:
            raise ValueError('superseded input manifest is malformed')
        previous_hash = previous.pop('input_hash')
        actual_hash = hashlib.sha256(json.dumps(previous, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        if previous.get('job_id') != supersedes or previous.get('schema_version') != 1 or previous_hash != actual_hash:
            raise ValueError('superseded input manifest integrity mismatch')
    output = dict(document, sources=verified)
    output['input_hash'] = hashlib.sha256(json.dumps(output, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    target = package_path(root, f'ffe/jobs/{job}/input-manifest.json', required=False)
    if target.exists():
        raise ValueError('input manifest already exists; corrections create a new job naming supersedes')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive link publishes a complete file without clobbering a concurrent creator.
    fd, temporary = tempfile.mkstemp(prefix='.input-', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as file:
            json.dump(output, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write('\n'); file.flush(); os.fsync(file.fileno())
        os.link(temporary, target)
    finally:
        os.unlink(temporary)
    return {'path': str(target.relative_to(root)), 'input_hash': output['input_hash'], 'mode': output['mode'], 'adoption_performed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--project', type=Path)
    target.add_argument('--workspace', type=Path, help='authorized standalone one-off output root; no project adoption')
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 20 * 1024 * 1024:
            raise ValueError('input exceeds 20 MiB')
        print(json.dumps(manifest(args.project or args.workspace, json.loads(args.input.read_text()), standalone=args.workspace is not None), indent=2))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, f'intake rejected: {exc}\n')


if __name__ == '__main__':
    main()
