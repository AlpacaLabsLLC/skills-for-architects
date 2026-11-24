#!/usr/bin/env bash
# The Rhino startup hook: one short line, the right path for each installed version, never blocks.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

root = Path.cwd()
FILES = ['hooks/as-rhino-context.py', 'hooks/lib/as-run-python.sh', 'skills/as-rhino-index.md',
         'skills/rhino-model/SKILL.md', 'skills/rhino-model/scripts/as-check.py', 'skills/rhino-setup/SKILL.md',
         'skills/rhino-display/SKILL.md', 'skills/rhino-display/scripts/as-display.py',
         'skills/rhino-thinline/SKILL.md', 'skills/rhino-thinline/scripts/as-sheet.py',
         'skills/rhino-thinline/scripts/as-sheet-core.py', 'skills/rhino-thinline/scripts/as-pdf-check.py',
         'skills/rhino-axon/SKILL.md', 'skills/rhino-axon/scripts/as-axon.py', 'skills/rhino-axon/scripts/as-axon-core.py',
         'skills/rhino-bom/SKILL.md', 'skills/rhino-bom/scripts/as-bom.py',
         'skills/as-rhino-lessons.py', 'skills/as-rhino-lessons.md',
         'skills/rhino-agent-team/SKILL.md', 'skills/rhino-agent-team/scripts/as-agent-team.py']


def index_path(line):
    return re.search(r'read (/.+?as-rhino-index\.md) with', line).group(1)


STDIN = '{"hook_event_name":"SessionStart","source":"startup","session_id":"t","cwd":"/tmp"}'

registered = json.loads((root / 'hooks/hooks.json').read_text())['hooks']['SessionStart']
entry = next(e for e in registered if any('as-rhino-context.py' in h['command'] for h in e['hooks']))
assert set(entry['matcher'].split('|')) == {'startup', 'resume', 'clear', 'compact'}
command = entry['hooks'][0]['command']
assert 'hooks/lib/as-run-python.sh' in command and 'node' not in command, command

index_text = (root / 'skills/as-rhino-index.md').read_text()
rows = re.findall(r'^\| `(as-rhino-[a-z-]+)` \| `(/as:[a-z-]+)` \| `([^`]+)` \|', index_text, re.M)
assert {r[0] for r in rows} == {'as-rhino-model', 'as-rhino-setup', 'as-rhino-display', 'as-rhino-thinline', 'as-rhino-axon', 'as-rhino-bom', 'as-rhino-agent-team'}, rows
for name, slash, rel in rows:
    assert (root / 'skills' / rel).is_file(), rel
    assert slash == '/as:' + rel.split('/')[0], (slash, rel)

with tempfile.TemporaryDirectory() as tmp:
    # Rhino's bundled interpreter is stood in for by the interpreter running this test.
    home = Path(tmp) / 'home'
    py = home / '.rhinocode/py313-rh9'
    py.mkdir(parents=True)
    (py / 'python3.13').symlink_to(sys.executable)
    cache = home / '.claude/plugins/cache/skills-for-architects/as'
    for version in ('1.5.2', '1.5.3'):
        for f in FILES:
            dst = cache / version / f
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / f, dst)
    # The panel's environment: minimal PATH, no node, Rhino's PYTHONHOME.
    env = {'HOME': str(home), 'PATH': '/usr/bin:/bin', 'PYTHONHOME': str(py)}
    for version in ('1.5.2', '1.5.3'):
        plugin = cache / version
        cmd = command.replace('${CLAUDE_PLUGIN_ROOT}', str(plugin))
        run = subprocess.run(['/bin/sh', '-c', cmd], input=STDIN, env=env, capture_output=True, text=True, cwd=tmp)
        assert run.returncode == 0 and not run.stderr, run
        out = json.loads(run.stdout)['hookSpecificOutput']
        assert out['hookEventName'] == 'SessionStart'
        line = out['additionalContext']
        assert '\n' not in line and len(line.encode()) < 2048, line
        # The lessons folder is the plugin data folder, the same for every version.
        lessons = re.search(r'Their lessons folder: (/\S+)\.$', line).group(1)
        assert lessons == str(home / '.claude/plugins/data/as-skills-for-architects/rhino-lessons'), lessons
        assert len(line.replace(str(index_path(line)), '').replace(lessons, '').encode()) < 300, line
        assert all(w in line for w in ('as-rhino', 'Arch Studio in Rhino', 'run_python', 'Skill tool', 'compaction')), line
        index = Path(re.search(r'read (/.+?as-rhino-index\.md) with', line).group(1))
        assert index == plugin / 'skills/as-rhino-index.md', index
        # Index to skill to checker stays inside the same version.
        checker = index.parent / 'rhino-model/SKILL.md'
        assert checker.is_file() and (checker.parent / 'scripts/as-check.py').is_file()
        for name, script in (('rhino-agent-team', 'as-agent-team.py'), ('rhino-display', 'as-display.py'), ('rhino-thinline', 'as-sheet.py'), ('rhino-thinline', 'as-pdf-check.py'), ('rhino-axon', 'as-axon.py'), ('rhino-bom', 'as-bom.py')):
            skill = index.parent / name / 'SKILL.md'
            assert skill.is_file() and (skill.parent / 'scripts' / script).is_file(), (name, script)
            assert skill.parent.parent.parent == plugin, skill
    # A broken package gives no output and exit 0.
    (cache / '1.5.2/skills/as-rhino-index.md').unlink()
    cmd = command.replace('${CLAUDE_PLUGIN_ROOT}', str(cache / '1.5.2'))
    run = subprocess.run(['/bin/sh', '-c', cmd], input=STDIN, env=env, capture_output=True, text=True, cwd=tmp)
    assert run.returncode == 0 and run.stdout == '' and run.stderr == '', run
print('PASS: startup hook gives one short line, resolves each installed version, stays silent when incomplete')
PY
