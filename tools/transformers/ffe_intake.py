#!/usr/bin/env python3
"""Write a create-only FF&E input manifest from explicitly selected project sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit, parse_qsl


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


def manifest(project, document):
    if Path(project).is_symlink():
        raise ValueError('symlink project root is not supported')
    root = Path(project).resolve()
    if not (root / 'PROJECT.md').is_file() or (root / 'PROJECT.md').is_symlink():
        raise ValueError('resolve a project before FF&E intake')
    required = {'schema_version', 'mode', 'job_id', 'sources', 'selected_tags', 'template', 'record_basis', 'supersedes', 'actor', 'reason'}
    if not isinstance(document, dict) or set(document) != required or type(document['schema_version']) is not int or document['schema_version'] != 1:
        raise ValueError('invalid intake schema')
    if document['mode'] not in ('one-off', 'adopted'):
        raise ValueError('explicit one-off or adopted mode required')
    for field in ('actor', 'reason'):
        if not isinstance(document[field], str) or not document[field].strip():
            raise ValueError('actor and reason are required')
    job = document['job_id']
    if not isinstance(job, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', job):
        raise ValueError('invalid job ID')
    tags = document['selected_tags']
    if not isinstance(tags, list) or not tags or any(not isinstance(t, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', t) for t in tags) or len(set(tags)) != len(tags):
        raise ValueError('selected tags must be unique safe strings')
    if document['mode'] == 'one-off' and document['record_basis'] is not None:
        raise ValueError('one-off inputs cannot imply adopted record authority')
    if document['mode'] == 'adopted':
        basis = document['record_basis']
        if not isinstance(basis, dict) or set(basis) != {'schedule_id', 'revision', 'hash'} or type(basis['revision']) is not int or basis['revision'] < 1:
            raise ValueError('adopted input requires a pinned record basis')
        import importlib.util
        spec = importlib.util.spec_from_file_location('ffe_records', Path(__file__).resolve().parents[1] / 'workspace/ffe_records.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        schedule = module.read_schedule(root, basis['schedule_id'], basis['revision'])
        if schedule['hash'] != basis['hash'] or not set(tags) <= {x['tag'] for x in schedule['items']}:
            raise ValueError('record basis or selection mismatch')
    sources = document['sources']
    if not isinstance(sources, list) or not sources:
        raise ValueError('source bundle required')
    ids = set()
    verified = []
    for source in sources:
        if not isinstance(source, dict) or set(source) != {'id', 'kind', 'reference', 'sha256', 'status'}:
            raise ValueError('invalid source entry')
        if not isinstance(source['id'], str) or not source['id'] or source['id'] in ids:
            raise ValueError('duplicate/invalid source ID')
        ids.add(source['id'])
        if source['status'] not in ('available', 'unavailable'):
            raise ValueError('invalid source status')
        digest = source['sha256']
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest)):
            raise ValueError('invalid source SHA256')
        if source['kind'] == 'file':
            path = package_path(root, source['reference'], required=source['status'] == 'available')
            if source['status'] == 'available':
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest is not None and digest != actual:
                    raise ValueError('source hash mismatch')
                source = dict(source, sha256=actual)
        elif source['kind'] == 'url':
            url = urlsplit(source['reference'])
            if url.scheme != 'https' or not url.netloc or url.username or url.password or any(re.search('token|secret|password|authorization|api.?key', key, re.I) for key, _ in parse_qsl(url.query)):
                raise ValueError('source URL must be HTTPS without credentials')
            if source['status'] == 'available' and digest is None:
                raise ValueError('available URL source requires a host-captured content hash')
        else:
            raise ValueError('source kind must be file or url')
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
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 20 * 1024 * 1024:
            raise ValueError('input exceeds 20 MiB')
        print(json.dumps(manifest(args.project, json.loads(args.input.read_text())), indent=2))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, f'intake rejected: {exc}\n')


if __name__ == '__main__':
    main()
