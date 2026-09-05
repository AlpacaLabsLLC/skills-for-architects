#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
root = Path.cwd()
spec = importlib.util.spec_from_file_location('categories', root/'tools/validators/validate-categories.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
components, clusters = m.validate(root)
assert len(clusters) == 9
assert len([x for x in components if x.startswith('skill:')]) == 50
assert m.render(components, clusters) == (root/'docs/practice-clusters.md').read_text()
with tempfile.TemporaryDirectory(prefix='as-package-') as directory:
    dest = Path(directory)/'package'
    shutil.copytree(root, dest, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    # Actual canonical assets remain readable in a package without repository metadata.
    assert (dest/'studio/templates/studio/.mcp.json').is_file()
    assert (dest/'corpus/practice-methods/us-professional-practice/sources.md').is_file()
    subprocess.run(['python3',str(dest/'tools/validators/validate-categories.py'),'--check-guide'],cwd=directory,check=True)
    subprocess.run(['bash',str(dest/'skills/studio/scripts/studio-workspace.sh'),'init',str(Path(directory)/'Example Studio'),'Example Studio','metric','US','NY','NYC'],cwd=directory,check=True)
    assert (Path(directory)/'Example Studio/.mcp.json').is_file()
    # Negative mutations must fail rather than silently degrade coverage.
    registry=dest/'corpus/components.json'; original=registry.read_text()
    def rejects():
        try: m.validate(dest)
        except ValueError: return
        raise AssertionError('invalid mutation accepted')
    for mutate in [lambda d:d['components'].append(d['components'][0]),
                   lambda d:d['components'][0].update(path='../../outside'),
                   lambda d:d['components'][0].update(dependencies=['unknown:id']),
                   lambda d:d['components'][0].update(dependencies=[d['components'][0]['id']])]:
        d=json.loads(original); mutate(d); registry.write_text(json.dumps(d)); rejects()
    registry.write_text(original)
    cluster=dest/'clusters/programming.json'; saved=cluster.read_text()
    for mutate in [lambda d:d['members'].append('skill:nonexistent'),
                   lambda d:d['dependencies'].append(d['id']),
                   lambda d:d['coverage'].update(workflow_validated=True),
                   lambda d:d.update(project_records=['private/PROJECT.md']),
                   lambda d:d['coverage'].update(jurisdictions=['jurisdiction:missing'])]:
        d=json.loads(saved);mutate(d);cluster.write_text(json.dumps(d));rejects()
    cluster.write_text(saved)
    # A new practice/geography fixture composes existing definitions with no skill duplication.
    d=json.loads(saved); d.update(id='cluster:fixture-practice',name='Fixture practice')
    jurisdictions=dest/'corpus/jurisdictions/catalog.json'
    catalog=json.loads(jurisdictions.read_text())
    fixture=dict(catalog['jurisdictions'][-1]);fixture['id']='jurisdiction:fixture-city'
    catalog['jurisdictions'].append(fixture);jurisdictions.write_text(json.dumps(catalog))
    d['coverage']['jurisdictions']=['jurisdiction:fixture-city']
    (dest/'clusters/fixture-practice.json').write_text(json.dumps(d))
    _, updated=m.validate(dest); assert len(updated)==10
    # Existing skill reference paths forward to a canonical file, with no duplicated concepts.
    for file in (dest/'skills/architecture-knowledge/references').glob('*.md'):
        text=file.read_text(); assert '../../../corpus/practice-methods/' in text
        assert '## AK-' not in text
print('category ownership, discovery, malformed fixtures and portable package checks passed')
PY
