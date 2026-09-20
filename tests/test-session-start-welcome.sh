#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json,os,re,subprocess,tempfile
from pathlib import Path
root=Path.cwd()
line=re.search(r'<!-- AS_SESSION_LINE: (.+) -->',(root/'rules/moments.md').read_text()).group(1)
with tempfile.TemporaryDirectory() as tmp:
    work=Path(tmp); plugin=work/'plugin'; state=work/'state'
    for f in ['.claude-plugin/plugin.json','skills/norma/SKILL.md','skills/tool-catalog/SKILL.md']:
        p=plugin/f;p.parent.mkdir(parents=True,exist_ok=True);p.touch()
    env={**os.environ,'CLAUDE_PLUGIN_ROOT':str(plugin),'ARCHITECTURE_STUDIO_STATE_DIR':str(state)}
    def run(name):
        p=subprocess.run(['sh',str(root/'hooks'/name)],cwd=work,env=env,capture_output=True,text=True,check=True)
        return json.loads(p.stdout)
    first=run('session-start-welcome.sh');second=run('session-start-welcome.sh');ambient=run('session-start-ambient.sh')
    assert first==second, 'Session context must survive subsequent sessions'
    assert all(v['hookSpecificOutput']['additionalContext']==line for v in [first,second,ambient])
    assert not state.exists(),'Discovery must not persist onboarding state'
    (plugin/'skills/norma/SKILL.md').unlink()
    missing=run('session-start-welcome.sh')
    assert missing['systemMessage'] != first['systemMessage'], 'Incomplete package must not claim available workflows'
    assert missing['hookSpecificOutput']['additionalContext']==line
print('PASS: both hooks emit canonical context, repeat without state writes, and incomplete package differs')
PY
