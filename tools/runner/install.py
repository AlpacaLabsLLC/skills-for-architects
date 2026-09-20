#!/usr/bin/env python3
"""Install immutable package bytes and locked local dependencies, outside model context."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package import verify


def download(url, target, sha256):
    if not url.startswith('https://'):
        raise ValueError('HTTPS package acquisition required')
    with urllib.request.urlopen(url, timeout=60) as response, target.open('xb') as output:
        shutil.copyfileobj(response, output)
    if hashlib.sha256(target.read_bytes()).hexdigest() != sha256.removeprefix('sha256:'):
        raise ValueError('Downloaded archive digest mismatch')


def unpack(archive, destination):
    destination.mkdir()
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as source:
            for entry in source.infolist():
                path = Path(entry.filename)
                if path.is_absolute() or '..' in path.parts or '\\' in entry.filename or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Unsafe archive member')
            source.extractall(destination)
    else:
        with tarfile.open(archive) as source:
            source.extractall(destination, filter='data')


def platform_key():
    arch = platform.machine().lower()
    return sys.platform + '-' + ('arm64' if arch in ('arm64', 'aarch64') else 'x64' if arch in ('x86_64', 'amd64') else arch)


def launchers(target, python, package):
    manifest = package / 'as-package.json'
    if os.name == 'nt':
        command = subprocess.list2cmdline([str(python), str(package / 'tools/runner/run.py'), '--package-manifest', str(manifest)])
        (target / 'as-run.cmd').write_text('@echo off\r\nset "AS_LOCAL_INSTALLATION=' + str(target) + '"\r\n' + command + ' %*\r\n')
    else:
        command = ' '.join(shlex.quote(str(value)) for value in (python, package / 'tools/runner/run.py', '--package-manifest', manifest))
        launcher = target / 'as-run'
        launcher.write_text('#!/bin/sh\nexport AS_LOCAL_INSTALLATION=' + shlex.quote(str(target)) + '\nexec ' + command + ' "$@"\n')
        launcher.chmod(0o755)
    (target / 'desktop-mcp.json').write_text(json.dumps({'mcpServers': {'as-local': {
        'command': str(python), 'args': [str(package / 'tools/runner/desktop.py'), '--package-manifest', str(manifest)],
        'env': {'AS_LOCAL_INSTALLATION': str(target)}}}}, indent=2) + '\n')


def install(package_archive, archive_hash, destination, uv):
    destination = Path(destination).expanduser().resolve()
    archive = Path(package_archive).resolve()
    if hashlib.sha256(archive.read_bytes()).hexdigest() != archive_hash.removeprefix('sha256:'):
        raise ValueError('Package archive does not match supplied SHA-256')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.as-install-', dir=destination) as scratch:
        package = Path(scratch) / 'package'
        unpack(archive, package)
        manifest = json.loads((package / 'as-package.json').read_text())
        verify(package, manifest, manifest['release_digest'])
        lock = json.loads((package / 'tools/runner/runtime-lock.json').read_text())
        if subprocess.check_output([str(uv), '--version'], text=True).strip().split()[:2] != ['uv', lock['uv']]:
            raise ValueError('Pinned uv bootstrap required')
        target = destination / manifest['release_digest'].split(':')[1]
        if target.exists():
            receipt = json.loads((target / 'installation.json').read_text())
            verify(target / 'package', json.loads((target / 'package/as-package.json').read_text()), manifest['release_digest'])
            return {**receipt, 'reused': True}
        # Final location is selected once; venv launchers cannot survive a later directory move.
        target.mkdir()
        try:
            shutil.copytree(package, target / 'package')
            package = target / 'package'
            shutil.copytree(package / 'tools/runner', target / 'runtime-project', ignore=shutil.ignore_patterns('.venv', '__pycache__'))
            env = {**os.environ, 'UV_PYTHON_INSTALL_DIR': str(target / 'python'),
                   'UV_PROJECT_ENVIRONMENT': str(target / 'venv'), 'UV_PYTHON_DOWNLOADS': 'automatic'}
            subprocess.run([str(uv), 'sync', '--project', str(target / 'runtime-project'), '--frozen',
                            '--managed-python', '--python', lock['python']], env=env, check=True)
            python = target / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            node = lock['node_downloads'].get(platform_key())
            if node is None:
                raise ValueError('No managed Node build declared for this platform')
            downloaded = Path(scratch) / 'node-archive'
            download(node['url'], downloaded, node['sha256'])
            node_temp = Path(scratch) / 'node-unpacked'
            unpack(downloaded, node_temp)
            entries = list(node_temp.iterdir())
            if len(entries) != 1 or not entries[0].is_dir():
                raise ValueError('Unexpected Node archive shape')
            shutil.move(str(entries[0]), target / 'node')
            launchers(target, python, package)
            receipt = {'schema_version': 1, 'release_digest': manifest['release_digest'],
                       'source_commit': manifest['source_commit'], 'source_digest': manifest['source_digest'],
                       'python': lock['python'], 'node': lock['node'], 'installation': str(target),
                       'manifest': str(package / 'as-package.json'), 'reused': False}
            (target / 'installation.json').write_text(json.dumps(receipt, indent=2) + '\n')
            return receipt
        except BaseException:
            # Only the new, private incomplete installation is removed; earlier releases stay usable.
            shutil.rmtree(target)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--destination', required=True)
    parser.add_argument('--uv', required=True)
    args = parser.parse_args()
    print(json.dumps(install(args.package, args.sha256, args.destination, args.uv)))
