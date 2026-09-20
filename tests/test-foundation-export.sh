#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Export the working candidate, including reviewed new files, without .git or
# ignored machine-local data. Validation must work outside the author's tree.
python3 - <<'PY'
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path.cwd()
files = subprocess.check_output([
    'git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'
]).decode().split('\0')
with tempfile.TemporaryDirectory(prefix='as-foundation-export-') as temporary:
    exported = Path(temporary) / 'plugin with spaces'
    exported.mkdir()
    for name in sorted(set(files)):
        if not name:
            continue
        source = root / name
        if not source.exists():
            continue  # Working-tree deletions are not package files.
        if source.is_symlink() or not source.is_file():
            raise AssertionError(f'Unexpected non-regular package file: {name}')
        destination = exported / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    assert not (exported / '.git').exists()
    skills = sorted(p.parent.name for p in (exported / 'skills').glob('*/SKILL.md'))
    assert skills == sorted(p.parent.name for p in (root / 'skills').glob('*/SKILL.md'))
    assert len(list(exported.rglob('SKILL.md'))) == len(skills)
    versions = [json.loads((exported / path).read_text())['version'] for path in (
        '.claude-plugin/plugin.json', '.codex-plugin/plugin.json')]
    assert versions == ['1.5.0', '1.5.0']
    subprocess.run([sys.executable, 'tools/validators/validate-categories.py',
                    '--root', '.', '--check-guide'], cwd=exported, check=True)
    subprocess.run([sys.executable, 'tools/validators/capabilities.py',
                    '--root', '.', '--check'], cwd=exported, check=True)
    subprocess.run([sys.executable, 'tests/test-completion-reporting.py'], cwd=exported, check=True)
    subprocess.run(['node', 'tools/integrations/source-health.mjs', '--validate'],
                   cwd=exported, check=True)
    subprocess.run([sys.executable, 'scripts/check-plugin-namespace.py', '.'],
                   cwd=exported, check=True)
    # Studio connector template remains complete in the detached package.
    assert (exported / 'studio/templates/studio/.mcp.json').is_file()
    subprocess.run([sys.executable, 'tools/validators/host_contracts.py'], cwd=exported, check=True)
    # Current shared operations must work from the exported package.
    subprocess.run([sys.executable, 'tests/test-product-library.py'], cwd=exported, check=True)
    subprocess.run([sys.executable, 'tests/test-product-observations.py'], cwd=exported, check=True)
    subprocess.run([sys.executable, 'tests/test-evidence-reliability.py'], cwd=exported, check=True)
    subprocess.run([sys.executable, 'tests/test-product-url-clip.py'], cwd=exported, check=True)
    subprocess.run([sys.executable, 'tests/test-geographic-applicability.py'], cwd=exported, check=True)
    private_record = exported / 'PROJECT.md'
    assert not private_record.exists(), 'A real project record entered the plugin'
    print(f'Export verified: {len(skills)} skills, matching versions and canonical resources')
PY
