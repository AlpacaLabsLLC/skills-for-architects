#!/usr/bin/env bash
# Local lessons for the as-rhino skills: write, read, repeats, promotion only after a yes,
# private details stripped, measuring instruments out of reach, and the startup line naming the folder.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python3 - <<'PY'
import contextlib, io, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

root = Path.cwd()
SCRIPT = root / 'skills/as-rhino-lessons.py'
SKILLS = ('rhino-model', 'rhino-bom', 'rhino-display', 'rhino-thinline', 'rhino-axon')


def load():
    g = {'__name__': 'as_rhino_lessons'}
    exec(compile(SCRIPT.read_text(), str(SCRIPT), 'exec'), g)
    return g


L = load()
LessonError = L['LessonError']


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
    except LessonError as e:
        return str(e)
    raise AssertionError('not refused: %r %r' % (a, k))


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    d = str(tmp / 'data' / 'rhino-lessons')

    # Read before anything was written.
    out = L['run']('read', 'rhino-model', d)
    assert 'No lessons yet' in out and not os.path.exists(d), out

    # Write: one line per lesson, plain text, tagged, in the skill's own file.
    t0 = 1_800_000_000
    out = L['run']('write', 'rhino-model', d, [
        {'tag': 'F', 'kind': 'practice', 'text': 'CreateBooleanDifference with a Python list hit the single-Brep overload; a List[G.Brep] worked'},
        {'tag': 'J', 'kind': 'practice', 'text': 'Show the requirements table before the first build script, even for one element'},
        {'tag': '[M]', 'kind': 'practice', 'text': 'Sheathing of 13 mm per side ate the knee clearance; recheck tight widths after an added layer'},
    ], now=t0)
    assert 'wrote 3' in out, out
    text = (Path(d) / 'rhino-model.txt').read_text()
    rows = [ln for ln in text.splitlines() if not ln.startswith('#')]
    assert len(rows) == 3 and all(re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ \[[UFMJ]\] ', r) for r in rows), rows
    assert set(os.listdir(d)) == {'rhino-model.txt'}, os.listdir(d)
    assert 'none to offer' in out, out
    assert refused(L['run'], 'write', 'rhino-model', d, [{'tag': 'X', 'kind': 'practice', 'text': 'an unknown tag is refused here'}])

    # Read: the next run, a fresh chat, sees them; a lone [J] is marked unconfirmed.
    out = L['run']('read', 'rhino-model', d)
    assert 'List[G.Brep] worked' in out and '13 mm per side' in out, out
    assert re.search(r'\[J\] practice: Show the requirements table.*\(unconfirmed\)', out), out
    assert 'name any you apply in the report' in out, out
    assert 'No lessons yet' in L['run']('read', 'rhino-bom', d)

    # Promotion: a lone [J], [F] or [M] is not offered.
    assert 'OFFER rhino-model: none' in L['run']('offer', 'rhino-model', d)

    # Repeat detection: the same lesson in other words, in a later run, counts twice.
    out = L['run']('write', 'rhino-model', d, [
        {'tag': 'J', 'kind': 'practice', 'text': 'show the requirements table before the first build script, even for a single element.'},
        {'tag': 'J', 'kind': 'practice', 'text': 'Show the requirements table before the first build script even for one element'},  # same run: once
    ], now=t0 + 3600)
    assert 'wrote 1' in out and 'now 2 runs' in out and 'none to offer' in out, out
    out = L['run']('read', 'rhino-model', d)
    assert 'seen in 2 runs' in out and 'unconfirmed' not in out, out
    # The same run written twice by mistake (one timestamp) is still one run.
    L['run']('write', 'rhino-model', d, [{'tag': 'M', 'kind': 'practice', 'text': 'Sheathing of 13 mm per side ate the knee clearance; recheck tight widths after an added layer'}], now=t0)
    assert not any('13 mm' in g['text'] and g['count'] > 1 for g in L['clusters'](L['load_lessons'](d, 'rhino-model')))
    # A different lesson is not a repeat.
    assert not L['similar']('Name every object by element type', 'Restore layer visibility after every batch')

    # Repeats of tool, script or check lessons are never offered, however often they recur.
    assert 'OFFER rhino-model: none' in L['run']('offer', 'rhino-model', d)

    # A [U] lesson (the user's own preference) is offered at once, without id tags or run counts.
    out = L['run']('write', 'rhino-model', d, [{'tag': 'U', 'kind': 'preference', 'text': 'The user wants wall, floor and roof thickness asked as three questions', 'user_said': 'ask me wall, floor and roof separately'}], now=t0 + 7200)
    offer = L['run']('offer', 'rhino-model', d)
    ids = re.findall(r'^- ([0-9a-f]{6}) ', offer, re.M)
    assert len(ids) == 1 and 'ask_user' in offer and 'None, keep them as lessons' in offer and 'plain words' in offer, offer
    assert '[U]' not in offer and 'seen in' not in offer, offer

    # Promote asks first: no firm rule without confirmed and the user's answer.
    for bad in (None, {}, {'ids': ids}, {'ids': ids, 'confirmed': True}, {'ids': ids, 'answer': 'yes'},
                {'ids': ids, 'confirmed': 'yes', 'answer': 'yes'}, {'ids': ids, 'confirmed': True, 'answer': '  '}):
        assert 'ask the user' in refused(L['run'], 'promote', 'rhino-model', d, promote=bad), bad
        assert not (Path(d) / 'firm-rules.txt').exists()
    assert 'not offered' in refused(L['run'], 'promote', 'rhino-model', d, promote={'ids': ['ffffff'], 'confirmed': True, 'answer': 'yes'})
    assert 'not offered' in refused(L['run'], 'promote', 'rhino-bom', d, promote={'ids': ids[:1], 'confirmed': True, 'answer': 'yes'})
    assert not (Path(d) / 'firm-rules.txt').exists()
    u_id = re.search(r'^- ([0-9a-f]{6}) The user wants', offer, re.M).group(1)
    out = L['run']('promote', 'rhino-model', d, promote={'ids': [u_id], 'confirmed': True, 'answer': 'Yes, the first one only'}, now=t0 + 7300)
    assert '1 firm rule' in out, out
    rules = (Path(d) / 'firm-rules.txt').read_text()
    assert re.search(r'^\d{4}-\d\d-\d\d rhino-model: The user wants wall.* \(from %s\)$' % u_id, rules, re.M), rules
    # Promoted once: not offered again, read as a firm rule; other skills do not see a skill rule.
    offer2 = L['run']('offer', 'rhino-model', d)
    assert u_id not in offer2 and 'OFFER rhino-model: none' in offer2, offer2
    out = L['run']('read', 'rhino-model', d)
    assert out.index('Firm rules') < out.index('Lessons from earlier runs') and '1 firm rules' in out, out
    assert 'Firm rules' not in L['run']('read', 'rhino-display', d)
    # scope all reaches every skill; the firm rule keeps the plain wording the user saw.
    L['run']('write', 'rhino-model', d, [{'tag': 'U', 'kind': 'preference', 'text': 'user wants the requirements table shown before the first build script', 'user_said': 'show me the table before you build'}], now=t0 + 7400)
    j_id = re.search(r'^- ([0-9a-f]{6}) ', L['run']('offer', 'rhino-model', d), re.M).group(1)
    assert 'wording maps' in refused(L['run'], 'promote', 'rhino-model', d, promote={'ids': [j_id], 'confirmed': True, 'answer': 'yes', 'wording': {'ffffff': 'x y z'}})
    L['run']('promote', 'rhino-model', d, promote={'ids': [j_id], 'confirmed': True, 'answer': 'yes, for every skill', 'scope': 'all',
                                                   'wording': {j_id: 'Show the requirements table before building'}})
    for s in SKILLS:
        assert 'Show the requirements table before building' in L['run']('read', s, d), s
    # A declined preference ("None") is recorded and not offered again, so the next run asks nothing.
    L['run']('write', 'rhino-model', d, [{'tag': 'U', 'kind': 'preference', 'text': 'user wants 300 mm roof overhangs on sheds', 'user_said': 'I always use 300 mm overhangs on sheds'}], now=t0 + 7500)
    k_id = re.search(r'^- ([0-9a-f]{6}) ', L['run']('offer', 'rhino-model', d), re.M).group(1)
    assert 'either promoted or declined' in refused(L['run'], 'promote', 'rhino-model', d, promote={'ids': [k_id], 'declined': [k_id], 'confirmed': True, 'answer': 'x'})
    out = L['run']('promote', 'rhino-model', d, promote={'declined': [k_id], 'confirmed': True, 'answer': 'None, keep them as lessons'})
    assert '1 declined' in out and k_id in (Path(d) / 'declined.txt').read_text(), out
    assert 'OFFER rhino-model: none' in L['run']('offer', 'rhino-model', d) and 'ask nothing' in L['run']('offer', 'rhino-model', d)
    assert '300 mm roof overhangs' not in (Path(d) / 'firm-rules.txt').read_text()
    assert 'OFFER rhino-model: none' in L['run']('offer', 'rhino-model', d)

    # Stripping: project names, places and personal details go unless the user wrote them in.
    private = ['Sample Ridge Cabin', 'Quillby', 'Exampleton']
    cases = [
        ('Sample Ridge Cabin needs the stair header doubled over the opening', 'Sample Ridge Cabin'),
        ('For Quillby, ask the deck board width before modeling boards', 'Quillby'),
        ('Projects in Exampleton name the code jurisdiction in the first question', 'Exampleton'),
        ('Export to /Users/user0/Desktop/out failed until the folder existed; create the folder first', '/Users/user0'),
        ('Saved a copy to C:\\Users\\user0\\x.3dm and read it back with File3dm.Read', 'user0'),
        ('Send the PDF to user0@example.com after the check passes', 'user0@example.com'),
        ('Call +1 212 555 0100 before exporting layouts', '555'),
        ('Site at 12 Sample Lane gets a north arrow on every sheet', 'Sample Lane'),
        ('Survey from https://example.com/survey sets the datum for every height', 'example.com'),
        ('The cabin-final.3dm document keeps its layers under one parent', 'cabin-final'),
    ]
    for text, gone in cases:
        clean, removed = L['strip_private'](text, private)
        assert gone not in clean and removed, (text, clean)
        L['check_text'](clean)
    clean, _ = L['strip_private']('Stud spacing 16 in, header 2x10, clear width 2400 x 1200 mm, sections 16-18 in', private)
    assert clean == 'Stud spacing 16 in, header 2x10, clear width 2400 x 1200 mm, sections 16-18 in', clean
    out = L['run']('write', 'rhino-bom', d, [{'tag': 'U', 'kind': 'practice', 'text': cases[0][0]}, {'tag': 'F', 'kind': 'practice', 'text': cases[3][0]}], private)
    stored = (Path(d) / 'rhino-bom.txt').read_text()
    assert 'Sample Ridge' not in stored and '/Users' not in stored and 'user0' not in stored and '<project>' in stored and '<path>' in stored, stored
    assert 'stripped' in out, out
    # Too little left after stripping: refused, nothing written.
    before = (Path(d) / 'rhino-bom.txt').read_text()
    assert 'too little left' in refused(L['run'], 'write', 'rhino-bom', d, [{'tag': 'U', 'kind': 'practice', 'text': 'Sample Ridge Cabin, Quillby'}], private)
    assert (Path(d) / 'rhino-bom.txt').read_text() == before
    # The user wrote the name in: kept.
    L['run']('write', 'rhino-bom', d, [{'tag': 'U', 'kind': 'preference', 'text': 'Quillby wants every BOM grouped by layout', 'user_said': 'group every BOM by layout', 'user_wrote': True}], private)
    assert 'Quillby wants every BOM' in (Path(d) / 'rhino-bom.txt').read_text()
    # The document name passed from Rhino is stripped too.
    class Doc:
        Name = 'Samplefield-Shed.3dm'
        Path = '/Users/user0/Projects/Samplefield-Shed.3dm'
    g = {'__rhino_doc__': Doc(), 'AS_SCRIPT_FILE': str(SCRIPT), 'AS_MODE': 'write', 'AS_SKILL': 'rhino-display',
         'AS_LESSONS_DIR': d, 'AS_LESSONS': [{'tag': 'F', 'kind': 'practice', 'text': 'Samplefield-Shed exported in colour until the mode was named in the capture call'}]}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(SCRIPT.read_text(), str(SCRIPT), 'exec'), g)
    assert 'wrote 1' in buf.getvalue(), buf.getvalue()
    assert 'Sample Ridge' not in (Path(d) / 'rhino-display.txt').read_text()

    # Scope: only two kinds are stored. Modeling practice, and the user's own preference with what the user said.
    b = str(tmp / 'kinds' / 'rhino-lessons')
    out = L['run']('write', 'rhino-model', b, [
        {'tag': 'F', 'kind': 'practice', 'text': 'Join the wall faces before offsetting, or the offset leaves open edges'},
        {'tag': 'U', 'kind': 'preference', 'text': 'Put the door on the short end wall of sheds', 'user_said': 'doors go on the short end for my sheds'},
    ], now=t0)
    assert 'wrote 2' in out, out
    stored = (Path(b) / 'rhino-model.txt').read_text()
    assert '[F] practice: Join the wall faces' in stored and '[U] preference: Put the door on the short end wall of sheds (user said: doors go on the short end for my sheds)' in stored, stored
    # No kind, another kind, an inferred design rule, a preference the user did not state: refused, nothing written.
    for bad in ({'tag': 'J', 'text': 'Roof overhangs on sheds are 300 mm'},
                {'tag': 'J', 'kind': 'design', 'text': 'Roof overhangs on sheds are 300 mm'},
                {'tag': 'J', 'kind': 'engineering', 'text': 'Size the ridge beam at span over 20'},
                {'tag': 'J', 'kind': 'preference', 'text': 'Put the door on the gable end', 'user_said': 'agent thought it looked better'},
                {'tag': 'U', 'kind': 'preference', 'text': 'Put the door on the gable end'},
                {'tag': 'U', 'kind': 'preference', 'text': 'Put the door on the gable end', 'user_said': '  '}):
        msg = refused(L['run'], 'write', 'rhino-model', b, [bad])
        assert 'refused' in msg and 'mention it to the user' in msg, (bad, msg)
    assert (Path(b) / 'rhino-model.txt').read_text() == stored
    # A lessons file from before kinds: read, kept, but not offered or promoted until a kind is added.
    legacy = Path(b) / 'rhino-bom.txt'
    legacy.write_text('2026-01-01T00:00:00Z [U] user wants every BOM grouped by layout\n')
    out = L['run']('read', 'rhino-bom', b)
    assert 'user wants every BOM grouped by layout' in out and 'no kind' in out, out
    assert 'OFFER rhino-bom: none' in L['run']('offer', 'rhino-bom', b)
    old_id = L['lesson_id']('user wants every BOM grouped by layout')
    assert 'has no kind' in refused(L['run'], 'promote', 'rhino-bom', b, promote={'ids': [old_id], 'confirmed': True, 'answer': 'yes'})
    assert legacy.read_text().startswith('2026-01-01T00:00:00Z [U] user wants') and not (Path(b) / 'firm-rules.txt').exists()
    legacy.write_text('2026-01-01T00:00:00Z [U] preference: user wants every BOM grouped by layout\n')
    assert old_id in L['run']('offer', 'rhino-bom', b)
    # Promotion stays inside the boundary: practice and preference lessons from the user ([U]) only.
    offer = L['run']('offer', 'rhino-model', b)
    assert 'Put the door on the short end wall' in offer and 'Join the wall faces' not in offer, offer

    # The learner never edits the checker, its tests or answer keys.
    for text in ('Relax the clearance tolerance in as-check-model.py so the seat passes',
                 'Edit the answer key for the stair to accept 7 risers',
                 'Skip the PDF check when the sheet looks right',
                 'Change the grader to ignore unnamed objects'):
        assert 'never changes the checker' in refused(L['check_text'], text), text
    L['check_text']('Never skip the requirements check after a rebuild, even a small one')
    # And never writes inside the installed plugin, where the checker lives.
    plugin = tmp / 'plugins/cache/mkt/as/1.5.3'
    (plugin / 'skills').mkdir(parents=True)
    shutil.copy2(SCRIPT, plugin / 'skills/as-rhino-lessons.py')
    fake = str(plugin / 'skills/as-rhino-lessons.py')
    for inside in (plugin, plugin / 'skills/rhino-model', plugin / 'evals'):
        assert 'inside the installed plugin' in refused(L['resolve_dir'], str(inside), fake, {})
    assert 'not a lessons folder' in refused(L['resolve_dir'], str(root), None, {})
    # Folder resolution: the named folder, else CLAUDE_PLUGIN_DATA, else derived as Claude Code does.
    assert L['resolve_dir'](d, fake, {}) == d
    assert L['resolve_dir'](None, fake, {'CLAUDE_PLUGIN_DATA': '/x/data/as-mkt'}) == os.path.join('/x/data/as-mkt', 'rhino-lessons')
    assert L['resolve_dir'](None, fake, {}) == str(tmp / 'plugins/data/as-mkt/rhino-lessons')
    assert 'no lessons folder' in refused(L['resolve_dir'], None, str(tmp / 'dev/skills/as-rhino-lessons.py'), {})
    assert L['sanitize_id']('as@skills-for-architects') == 'as-skills-for-architects'

    # The command line runs the same logic (the stand-in for run_python in CI).
    spec = tmp / 'spec.json'
    spec.write_text(json.dumps({'lessons': [{'tag': 'M', 'kind': 'practice', 'text': 'Arctic exports read back with zero coloured pixels at 3840 wide'}]}))
    run = subprocess.run([sys.executable, '-I', str(SCRIPT), 'write', '--skill', 'rhino-display', '--dir', d, '--json', str(spec)], capture_output=True, text=True)
    assert run.returncode == 0 and 'wrote 1' in run.stdout, run
    run = subprocess.run([sys.executable, '-I', str(SCRIPT), 'read', '--skill', 'rhino-display', '--dir', d], capture_output=True, text=True)
    assert run.returncode == 0 and 'zero coloured pixels' in run.stdout, run
    run = subprocess.run([sys.executable, '-I', str(SCRIPT), 'read', '--skill', 'rhino-setup', '--dir', d], capture_output=True, text=True)
    assert run.returncode == 1 and 'unknown skill' in run.stdout, run

    # Only plain text files, all in the one folder.
    assert sorted(os.listdir(d)) == ['declined.txt', 'firm-rules.txt', 'rhino-bom.txt', 'rhino-display.txt', 'rhino-model.txt'], os.listdir(d)

# The four skills read before planning, write at the end, promote only after ask_user.
for s in SKILLS:
    text = (root / 'skills' / s / 'SKILL.md').read_text()
    assert text.count('## Lessons') == 1, s
    assert '"AS_SKILL": "%s"' % s in text and 'as-rhino-lessons.py' in text, s
    assert '"AS_MODE": "read"' in text and '"write"' in text and '"promote"' in text and 'ask_user' in text, s
    assert 'Never edit the checker, its tests or answer keys' in text, s
    assert re.search(r'\[lessons\]\(#lessons\)', text), s
    assert '~/.claude' not in text, s
ref = (root / 'skills/as-rhino-lessons.md').read_text()
assert 'temporary path' in ref and 'CLAUDE_PLUGIN_DATA' in ref and 'Host memory (optional)' in ref

# The startup line names the lessons folder, stays short, and the skill script agrees on the folder.
# The hook is POSIX sh, run here through /bin/sh; on Windows tests/windows/run-hooks-no-python.sh runs it under Git Bash.
if os.name != 'nt':
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / 'home'
        plugin = home / '.claude/plugins/cache/skills-for-architects/as/1.5.3'
        for f in ('hooks/as-rhino-context.sh', 'skills/as-rhino-index.md', 'skills/as-rhino-lessons.py'):
            (plugin / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / f, plugin / f)
        registered = json.loads((root / 'hooks/hooks.json').read_text())['hooks']['SessionStart']
        command = next(h['command'] for e in registered for h in e['hooks'] if 'as-rhino-context.sh' in h['command'])
        cmd = command.replace('${CLAUDE_PLUGIN_ROOT}', str(plugin))
        data = home / '.claude/plugins/data/as-skills-for-architects'
        for env_data in (str(data), None):  # Claude Code exports CLAUDE_PLUGIN_DATA to hooks; without it, derived
            env = {'HOME': str(home), 'PATH': '/usr/bin:/bin'}
            if env_data:
                env['CLAUDE_PLUGIN_DATA'] = env_data
            run = subprocess.run(['/bin/sh', '-c', cmd], input='{}', env=env, capture_output=True, text=True, cwd=tmp)
            assert run.returncode == 0 and not run.stderr, run
            line = json.loads(run.stdout)['hookSpecificOutput']['additionalContext']
            folder = re.search(r'Their lessons folder: (/\S+)\.$', line).group(1)
            assert folder == str(data / 'rhino-lessons'), folder
            assert '\n' not in line and len(line.encode()) < 2048, len(line.encode())
            assert not data.exists(), 'the hook writes nothing'
            g = load()
            assert g['resolve_dir'](None, str(plugin / 'skills/as-rhino-lessons.py'), {}) == folder
        print('startup line: %d bytes' % len(line.encode()))
print('PASS: lessons write, read, count repeats, promote only after a yes, strip private details, stay away from the checker; the startup line names the folder')
PY
