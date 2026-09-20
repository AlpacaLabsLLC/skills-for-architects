#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 - <<'PY'
import json
import re
import subprocess
from pathlib import Path

claude = json.loads(Path('.claude-plugin/plugin.json').read_text(encoding='utf-8'))
claude_marketplace = json.loads(Path('.claude-plugin/marketplace.json').read_text(encoding='utf-8'))
codex = json.loads(Path('.codex-plugin/plugin.json').read_text(encoding='utf-8'))
codex_marketplace = json.loads(Path('.agents/plugins/marketplace.json').read_text(encoding='utf-8'))

assert codex['name'] == claude['name'] == 'as'
assert codex['version'] == claude['version'] == claude_marketplace['metadata']['version']
assert codex['skills'] == './skills/'
assert codex['hooks'] == './hooks/codex-hooks.json'
assert codex['repository'] == 'https://github.com/AlpacaLabsLLC/skills-for-architects'

codex_hooks = json.loads(Path('hooks/codex-hooks.json').read_text(encoding='utf-8'))['hooks']
assert set(codex_hooks) == {'SessionStart'}
session_start = codex_hooks['SessionStart']
assert len(session_start) == 1
assert set(session_start[0]['matcher'].split('|')) == {'startup', 'resume', 'clear', 'compact'}
handlers = session_start[0]['hooks']
assert handlers == [{
    'type': 'command',
    'command': '/bin/sh "${PLUGIN_ROOT}/hooks/session-start-ambient.sh"',
    'timeout': 2,
}]

expected_ambient_context = re.search(r'<!-- AS_SESSION_LINE: (.+) -->', Path('rules/moments.md').read_text()).group(1)
ambient = subprocess.run(
    ['/bin/sh', 'hooks/session-start-ambient.sh'],
    input='{"hook_event_name":"SessionStart","source":"startup"}',
    text=True,
    capture_output=True,
    check=True,
)
ambient_output = json.loads(ambient.stdout)
assert ambient_output == {
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': expected_ambient_context,
    },
}
assert ambient.stderr == ''

interface = codex['interface']
for field in ('displayName', 'shortDescription', 'longDescription', 'developerName', 'category', 'capabilities', 'websiteURL', 'defaultPrompt'):
    assert interface.get(field), field

assert codex_marketplace['name'] == 'skills-for-architects'
assert len(codex_marketplace['plugins']) == 1
entry = codex_marketplace['plugins'][0]
assert entry['name'] == 'as'
assert entry['source'] == {'source': 'local', 'path': './'}
assert entry['policy'] == {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}
assert entry['category'] == interface['category']

# Delivery policy is owned once; components may link it using their own concise prose.
subprocess.run(['python3', 'tools/validators/host_contracts.py'], check=True)

forbidden_roots = ('${CLAUDE_PLUGIN_ROOT}', '${CLAUDE_SKILL_DIR}')
violations = []
for asset in sorted(Path('skills').rglob('*')):
    if not asset.is_file():
        continue
    asset_bytes = asset.read_bytes()
    if b'\0' in asset_bytes:
        continue
    try:
        asset_text = asset_bytes.decode('utf-8')
    except UnicodeDecodeError:
        continue
    for line_number, line in enumerate(asset_text.splitlines(), start=1):
        for forbidden_root in forbidden_roots:
            if forbidden_root in line:
                violations.append(f'{asset}:{line_number}: {forbidden_root}')

assert not violations, (
    'Claude-only bundled path variables remain in portable skill assets:\n'
    + '\n'.join(violations)
)
PY

# Fresh workspace scaffolds and instruction files are exercised by current document-model tests.
# Retired Bash setup helpers are not a supported local-runtime requirement.

grep -q 'codex plugin marketplace add AlpacaLabsLLC/skills-for-architects' README.md
grep -q 'codex plugin add as@skills-for-architects' README.md

echo "✓ Codex manifest, marketplace, skills, workspace scaffolds, and install docs stay compatible"
