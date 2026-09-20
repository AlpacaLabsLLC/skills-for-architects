"""Closed JSON-to-existing-operation adapters; no caller-controlled executable."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def dispatch(operation, request):
    root = Path(__file__).resolve().parents[2]
    specification = next(row for row in json.loads((root / 'tools/runner/operations.json').read_text())['operations'] if row['id'] == operation)
    script = root / specification['script']
    runtime = sys.executable
    if script.suffix == '.mjs':
        installation = os.environ.get('AS_LOCAL_INSTALLATION')
        if not installation:
            raise ValueError('Managed Arch Studio Node runtime missing; use installed as-run entry point')
        runtime = str(Path(installation) / 'node' / ('node.exe' if os.name == 'nt' else 'bin/node'))
        expected = json.loads((root / 'tools/runner/runtime-lock.json').read_text())['node']
        probe = subprocess.run([runtime, '--version'], capture_output=True, text=True, timeout=10)
        if probe.returncode or probe.stdout.strip() != 'v' + expected:
            raise ValueError('Managed Node runtime version mismatch')
    with tempfile.TemporaryDirectory(prefix='as-operation-') as temp:
        args = []
        for binding in specification['argv']:
            if isinstance(binding, str):
                args.append(binding)
                continue
            field = binding['field']
            if field not in request:
                continue
            value = request[field]
            if binding.get('boolean'):
                if value:
                    args.append(binding['flag'])
                continue
            if 'flag' in binding:
                args.append(binding['flag'])
            if binding.get('json_file'):
                path = Path(temp) / (field + '.json')
                path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False), encoding='utf-8')
                args.append(str(path))
            elif binding.get('json_string'):
                args.append(json.dumps(value, ensure_ascii=False, allow_nan=False))
            elif isinstance(value, list):
                args.extend(str(item) for item in value)
            else:
                args.append(str(value))
        # File-backed capture keeps child output out of unbounded RAM allocation.
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            stdin = json.dumps(request[specification['stdin_field']], allow_nan=False).encode() if specification.get('stdin_field') else None
            process = subprocess.run([runtime, str(script), *args], input=stdin, stdout=stdout, stderr=stderr,
                                     cwd=root, timeout=120)
            stdout.seek(0); stderr.seek(0)
            raw = stdout.read(4 * 1024 * 1024 + 1)
            diagnostic = stderr.read(2000).decode('utf-8', errors='replace')
        if len(raw) > 4 * 1024 * 1024:
            raise ValueError('Operation output exceeds result bound')
        text = raw.decode('utf-8', errors='strict').strip()
        try:
            result = json.loads(text)
        except ValueError:
            try:
                result = json.loads(text.splitlines()[-1])
            except (ValueError, IndexError):
                result = {'message': text}
        if process.returncode:
            from run import OperationError
            error = OperationError('operation_failed', diagnostic.strip() or 'Operation returned failure')
            error.result = result
            raise error
        return result
