#!/usr/bin/env python3
"""Seal/export a complete Arch Studio package. Never read executable resource pages."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

EXCLUDED = {'.git', '.venv', '__pycache__', '.DS_Store', 'node_modules'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts) or relative.as_posix() == 'as-package.json':
            continue
        if path.is_symlink():
            raise ValueError('Package contains a symlink: ' + relative.as_posix())
        if path.is_file():
            result[relative.as_posix()] = digest(path.read_bytes())
    return result


def seal(root, source_commit, source_digest=None):
    if len(source_commit) != 40 or any(c not in '0123456789abcdef' for c in source_commit):
        raise ValueError('Full immutable source commit required')
    body = {'schema_version': 1, 'source_commit': source_commit,
            'source_digest': source_digest, 'files': inventory(root)}
    body['release_digest'] = digest(canonical(body))
    return body


def verify(root, manifest, expected):
    if manifest.get('schema_version') != 1 or manifest.get('release_digest') != expected:
        raise ValueError('Package identity does not match requested release')
    body = {k: v for k, v in manifest.items() if k != 'release_digest'}
    if digest(canonical(body)) != expected:
        raise ValueError('Package manifest digest does not match its contents')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Package has no declared files')
    for name, expected_hash in files.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name:
            raise ValueError('Unsafe package file path')
        path = root / relative
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            # Resolve OS aliases before passing the package root.
            raise ValueError('Package file symlink: ' + name)
        if not path.is_file() or digest(path.read_bytes()) != expected_hash:
            raise ValueError('Missing or altered package file: ' + name)
    actual = inventory(root)
    if actual != files:
        raise ValueError('Package contains undeclared or changed files')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--source-digest')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / '.git').exists():
        parser.error('Package a clean git archive/export, not an active checkout with untracked working files')
    if args.output.resolve().is_relative_to(root):
        parser.error('Export destination must be outside source package')
    manifest = seal(root, args.source_commit, args.source_digest)
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in manifest['files']:
            archive.write(root / name, name)
        archive.writestr('as-package.json', json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'package': str(args.output), 'sha256': digest(args.output.read_bytes()),
                      'release_digest': manifest['release_digest'], 'source_commit': args.source_commit,
                      'source_digest': args.source_digest}))


if __name__ == '__main__':
    main()
