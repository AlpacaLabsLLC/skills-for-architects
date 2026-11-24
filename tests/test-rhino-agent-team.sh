#!/usr/bin/env bash
# as-rhino-agent-team: the team check's logic on synthetic models, without Rhino, and what the skill may claim.
# The File3dm reader, the solid-intersection test and the document helpers need a live Rhino and are not run here.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python3 - <<'PY'
import copy, hashlib, re, sys, types
from pathlib import Path

repo = Path.cwd()
skill = repo / 'skills/rhino-agent-team'
failures, passed = [], [0]


def ok(condition, label, detail=''):
    if condition:
        passed[0] += 1
    else:
        failures.append('%s %s' % (label, str(detail)[:400]))


script = skill / 'scripts/as-agent-team.py'
ns = {'AS_SCRIPT_FILE': str(script)}
exec(compile(script.read_text(encoding='utf-8'), str(script), 'exec'), ns)
ok('Rhino' not in sys.modules, 'team: loading the helpers does not import Rhino')

# Records are added in model space: a layout that happens to be active is switched to a model view first.
class _View:
    def __init__(self, page):
        self.PageName = 'Sheet' if page else None
class _Views:
    def __init__(self):
        self.model, self.ActiveView = _View(False), _View(True)
    def GetViewList(self, model, page):
        assert model and not page
        return [self.model]
_doc = types.SimpleNamespace(Views=_Views())
ns['_model_view'](_doc)
ok(_doc.Views.ActiveView is _doc.Views.model, 'team: a layout view is replaced by a model view before records are added')
ns['_model_view'](_doc)
ok(_doc.Views.ActiveView is _doc.Views.model, 'team: a model view is left as it is')
analyse, status_line = ns['analyse'], ns['status_line']

# A small two-owner model: a shell with one floor slab, plumbing with a riser from its source through the slab
# to one fixture, a reservation for the riser, one opening request and its opening.
SETOUT = {'revision': 2, 'host': 'Shell',
           'owners': [{'name': 'Shell', 'file': 'shell.3dm'}, {'name': 'Plumbing', 'file': 'plumbing.3dm'}, {'name': 'Mechanical', 'file': 'mechanical.3dm'}],
           'points': [{'owner': 'Plumbing', 'system': 'Drain', 'role': 'source', 'name': 'exit', 'at': [10, 10, 0]},
                      {'owner': 'Plumbing', 'system': 'Drain', 'role': 'point', 'name': 'WC', 'at': [10, 10, 120]}],
           'shares': [{'owner': 'Plumbing', 'zone': 'chase', 'box': [5, 5, 0, 15, 15, 99]},
                            {'owner': 'Shell', 'zone': 'closet', 'box': [40, 40, 0, 60, 60, 100]}],
           'levels': [{'name': 'F1', 'z': 101}],
           'shared_spaces': [{'name': 'chase', 'box': [5, 5, 0, 15, 15, 99], 'owners': ['Plumbing']},
                             {'name': 'closet', 'box': [40, 40, 0, 60, 60, 100], 'owners': ['Shell']}]}


def rec(file, layer, bb, name='x', kind='solid', **user):
    return {'file': file, 'layer': layer, 'root': layer.split('::')[0], 'name': name, 'id': name + str(bb), 'user': user,
            'bb': tuple(bb), 'kind': kind, 'text': user.pop('text', '') if 'text' in user else ''}


def good():
    return [rec('shell.3dm', 'Shell::Floors', (0, 0, 100, 100, 100, 101), 'slab F1'),
            rec('shell.3dm', 'Shell::Openings', (8, 8, 99, 12, 12, 102), 'opening', setout_revision='2'),
            rec('plumbing.3dm', 'Plumbing::Drain', (9, 9, 0, 11, 11, 120), 'riser'),
            rec('plumbing.3dm', 'Interface::Penetrations', (8.5, 8.5, 99.5, 11.5, 11.5, 101.5), 'request', setout_revision='2', **{'from': 'Plumbing'}),
            rec('plumbing.3dm', 'Notes', (10, 10, 50, 10, 10, 50), 'note', kind='dot', note_id='n1', to='Shell', kind_='x')]


def fix_note(records, **user):
    for r in records:
        if r['layer'] == 'Notes':
            r['user'] = dict({'note_id': 'n1', 'from': 'Plumbing', 'to': 'Shell', 'kind': 'request', 'status': 'closed', 'round': '3'}, **user)
    return records


PASS_CHECK = '{"status": "pass", "rev": 1, "geom_fp": "g1-same"}'


VERSION = {'as:team-plugin': '1.5.4', 'as:team-helper': 'h1-aaaaaaaaaaaa'}


def owner_strings(stamp='2', check=PASS_CHECK, req='{"revision": 1}', now='g1-same', version=VERSION):
    out = dict({'setout_revision': stamp, 'as:requirements': req, '__geom_fp_now__': now}, **version)
    if check is not None:
        out['as:requirements-check'] = check
    return out


def strings(**revs):
    out = dict((f, owner_strings(revs.get(f.split('.')[0], '2'))) for f in ('shell.3dm', 'plumbing.3dm', 'mechanical.3dm'))
    out['setout.3dm'] = dict(VERSION)
    return out


STAMPS = strings()
base = analyse(SETOUT, fix_note(good()), STAMPS)
ok(base['settled'], 'team: a clean model settles', base['counts'])
ok(status_line(base).startswith('Team: settled at set-out revision 2\nASTEAM settled=true faults=0'), 'team: settled status line', status_line(base))

empty = analyse(SETOUT, [], {})
ok(not empty['settled'] and empty['counts']['points_served'] == 0 and empty['counts']['points_required'] == 1, 'team: an empty model does not settle', empty['counts'])

KEYS = ('clashes', 'share_breaks', 'unopened_crossings', 'requests_without_opening', 'points_served', 'ownership_breaks',
        'stale_files', 'stale_references', 'open_notes', 'notes_for_coordinator', 'malformed_notes', 'own_checks_not_passing',
        'version_mismatches', 'setout_gaps')


def seeded(label, change, expect, stamps=STAMPS):
    records = fix_note(good())
    change(records)
    out = analyse(SETOUT, records, stamps)
    moved = dict((k, out['counts'][k] - base['counts'][k]) for k in KEYS if out['counts'][k] != base['counts'][k])
    ok(moved == expect and not out['settled'], 'team: %s is caught and nothing else moves' % label, moved)
    return out


add = lambda r: (lambda records: records.append(r))
seeded('a clash between two owners',
       lambda rs: (rs.append(rec('mechanical.3dm', 'Mechanical::Supply', (70, 70, 10, 90, 90, 30), 'duct')),
                   rs.append(rec('plumbing.3dm', 'Plumbing::Gas', (80, 80, 10, 95, 82, 12), 'gas'))),
       {'clashes': 1})
seeded('an object in another owner\'s share', add(rec('plumbing.3dm', 'Plumbing::Gas', (45, 45, 10, 47, 47, 12), 'gas in the closet')), {'share_breaks': 1})
seeded('a crossing without an opening', add(rec('plumbing.3dm', 'Plumbing::Vent', (30, 30, 95, 32, 32, 105), 'vent')), {'unopened_crossings': 1})
seeded('a request the host has not answered',
       lambda rs: rs.__setitem__(1, rec('shell.3dm', 'Shell::Openings', (70, 70, 99, 72, 72, 102), 'opening elsewhere', setout_revision='2')),
       {'requests_without_opening': 1, 'unopened_crossings': 1, 'stale_references': 1})
seeded('an unserved point', lambda rs: rs.__setitem__(2, rec('plumbing.3dm', 'Plumbing::Drain', (9, 9, 0, 11, 11, 60), 'short riser')), {'points_served': -1})
seeded('an object on another owner\'s layers', add(rec('plumbing.3dm', 'Shell::Walls', (200, 0, 0, 210, 10, 10), 'wall')), {'ownership_breaks': 1})
seeded('a stale file stamp', lambda rs: None, {'stale_files': 1}, strings(plumbing='1'))
seeded('a stale request stamp', lambda rs: rs[3]['user'].update(setout_revision='1'),
       {'stale_references': 2})
seeded('an open request', lambda rs: fix_note(rs, status='open'), {'open_notes': 1})
seeded('a malformed note', lambda rs: fix_note(rs, kind='chat'), {'malformed_notes': 1})
seeded('an owner whose own requirements check failed', lambda rs: None, {'own_checks_not_passing': 1},
       dict(STAMPS, **{'plumbing.3dm': owner_strings(check='{"status": "fail", "rev": 1, "geom_fp": "g1-same"}')}))
seeded('an owner that never ran its own check', lambda rs: None, {'own_checks_not_passing': 1},
       dict(STAMPS, **{'mechanical.3dm': owner_strings(check=None)}))
seeded('an owner whose file changed after its check ran', lambda rs: None, {'own_checks_not_passing': 1},
       dict(STAMPS, **{'plumbing.3dm': owner_strings(now='g1-moved')}))
seeded('an owner whose check ran on an older requirements revision', lambda rs: None, {'own_checks_not_passing': 1},
       dict(STAMPS, **{'shell.3dm': owner_strings(req='{"revision": 2}')}))
seeded('an owner whose stored check has no fingerprint', lambda rs: None, {'own_checks_not_passing': 1},
       dict(STAMPS, **{'shell.3dm': owner_strings(check='{"status": "pass", "rev": 1}')}))
out = analyse(SETOUT, fix_note(good()), dict(STAMPS, **{'plumbing.3dm': owner_strings(now='g1-moved')}))
ok(out['own_checks']['plumbing.3dm'] == 'file changed after its check ran', 'team: the reason a changed file fails is named', out['own_checks'])
# In-file hygiene is rhino-model's: the team check does not repeat it.
for label, change in (('an open solid', lambda rs: rs[2].update(kind='open')), ('an unnamed solid', lambda rs: rs[2].update(name=' ')),
                      ('a duplicate', lambda rs: rs.append(dict(rs[2], name='copy')))):
    records = fix_note(good()); change(records)
    ok(analyse(SETOUT, records, STAMPS)['settled'], 'team: %s is left to rhino-model' % label)

# ---- Whoever finds an issue writes it: owner-to-owner notes and escalation after a round
def issue_note(note_id, frm, to, written, kind='issue', status='open', **extra):
    user = dict({'note_id': note_id, 'from': frm, 'to': to, 'kind': kind, 'status': status, 'round': str(written)}, **extra)
    return {'file': frm.lower() + '.3dm', 'layer': 'Notes', 'root': 'Notes', 'name': kind + ' note', 'id': note_id + '-dot',
            'user': user, 'bb': (60, 60, 60, 60, 60, 60), 'kind': 'dot', 'text': 'your duct runs through my vent at this point'}


owner_issue = fix_note(good()) + [issue_note('i1', 'Mechanical', 'Plumbing', 3)]
out = analyse(SETOUT, owner_issue, STAMPS, round_no=3)
ok(out['open_notes_by_addressee'].get('Plumbing') == ['i1'] and out['counts']['open_notes'] == 1 and not out['settled'],
   'team: an owner-to-owner issue note is listed by the team check, under its addressee', out['open_notes_by_addressee'])
ok(out['counts']['notes_for_coordinator'] == 0, 'team: an issue note written this round is not yet flagged', out['notes_for_coordinator'])
out = analyse(SETOUT, owner_issue, STAMPS, round_no=4)
ok(out['counts']['notes_for_coordinator'] == 1 and out['notes_for_coordinator'][0]['id'] == 'i1',
   'team: a note open more than one round is flagged to the coordinator', out['notes_for_coordinator'])
answered = owner_issue + [issue_note('r1', 'Plumbing', 'Mechanical', 4, kind='reply', status='answered', reply_to='i1')]
ok(analyse(SETOUT, answered, STAMPS, round_no=5)['counts']['notes_for_coordinator'] == 0, 'team: a replied note is not flagged')
to_coord = fix_note(good()) + [issue_note('c1', 'Plumbing', 'coordinator', 2, kind='change')]
out = analyse(SETOUT, to_coord, STAMPS, round_no=6)
ok(out['counts']['open_notes'] == 1 and out['counts']['notes_for_coordinator'] == 0 and out['open_notes_by_addressee'].get('coordinator') == ['c1'],
   'team: a change note is listed for the coordinator and not flagged again', out['open_notes_by_addressee'])
ok(analyse(SETOUT, owner_issue, STAMPS)['counts']['notes_for_coordinator'] == 0, 'team: without a round number nothing is flagged')
ok(status_line(analyse(SETOUT, owner_issue, STAMPS, round_no=4)).find('1 notes for coordinator') > 0, 'team: the status line names flagged notes')

# ---- What the review reads: each owner's own failed checks, and missing owner files
failing = analyse(SETOUT, fix_note(good()), dict(STAMPS, **{'plumbing.3dm': owner_strings(
    check='{"status": "fail", "rev": 1, "geom_fp": "g1-same", "failed": ["within Drain"]}')}))
ok(failing['own_check_failures'] == {'plumbing.3dm': ['within Drain']}, 'team: an owner\'s failed checks are listed for the review', failing['own_check_failures'])
ok(analyse(SETOUT, fix_note(good()), STAMPS)['own_check_failures'] == {}, 'team: nothing listed when every own check passes')
ok(ns['missing_files'](SETOUT, ['shell.3dm', 'plumbing.3dm', 'setout.3dm']) == ['mechanical.3dm'], 'preflight: a missing owner file is named')
ok(ns['missing_files'](SETOUT, ['shell.3dm', 'plumbing.3dm', 'mechanical.3dm']) == [], 'preflight: nothing missing')

# ---- Team installs: every file carries the plugin and helper version that wrote it
seeded('an owner on a different plugin version', lambda rs: None, {'version_mismatches': 1},
       dict(STAMPS, **{'plumbing.3dm': owner_strings(version={'as:team-plugin': '1.5.3', 'as:team-helper': 'h1-aaaaaaaaaaaa'})}))
seeded('an owner with a different helper', lambda rs: None, {'version_mismatches': 1},
       dict(STAMPS, **{'shell.3dm': owner_strings(version={'as:team-plugin': '1.5.4', 'as:team-helper': 'h1-bbbbbbbbbbbb'})}))
seeded('an owner file with no version stamp', lambda rs: None, {'version_mismatches': 1},
       dict(STAMPS, **{'mechanical.3dm': owner_strings(version={})}))
out = analyse(SETOUT, fix_note(good()), dict(STAMPS, **{'plumbing.3dm': owner_strings(version={'as:team-plugin': '1.5.3', 'as:team-helper': 'h1-aaaaaaaaaaaa'})}))
vm = out.get('version_mismatches') or []
ok(len(vm) == 1 and vm[0].get('file') == 'plumbing.3dm' and vm[0].get('plugin') == '1.5.3'
   and vm[0].get('coordinator_plugin') == '1.5.4' and (out.get('coordinator_version') or {}).get('plugin') == '1.5.4',
   'versions: the mismatch names the file, its version and the coordinator\'s', out['version_mismatches'])
ok('1 version mismatches' in status_line(out) and 'settled=false' in status_line(out), 'versions: the status line refuses settled on a mismatch', status_line(out))
out = analyse(SETOUT, fix_note(good()), dict(STAMPS, **{'setout.3dm': {}}))
vm = out.get('version_mismatches') or []
ok(not out['settled'] and len(vm) == 1 and vm[0].get('reason') == 'the set-out has no version stamp', 'versions: an unstamped set-out is refused', vm)
ok(ns['plugin_version'](str(script)) == __import__('json').loads((repo / '.claude-plugin/plugin.json').read_text())['version'],
   'versions: the plugin version is read from the installed plugin.json')
hv = ns['helper_version'](str(script))
ok(hv.startswith('h2-') and hv == ns['helper_version'](str(script)), 'versions: the helper fingerprint is stable', hv)
import shutil as _sh, tempfile as _tf
with _tf.TemporaryDirectory() as _d:
    # A copy of the plugin's helper layout: the team helper and rhino-model's check scripts.
    _team = Path(_d) / 'skills/rhino-agent-team/scripts'; _team.mkdir(parents=True)
    _model = Path(_d) / 'skills/rhino-model/scripts'; _model.mkdir(parents=True)
    _sh.copy(script, _team / 'as-agent-team.py')
    for _n in ('as-check.py', 'as-check-model.py'):
        _sh.copy(repo / 'skills/rhino-model/scripts' / _n, _model / _n)
    _copy = _team / 'as-agent-team.py'
    ok(ns['helper_version'](str(_copy)) == hv, 'versions: an identical copy of the helpers has the same fingerprint')
    (_model / 'as-check.py').write_text((_model / 'as-check.py').read_text() + '\n# local edit\n')
    ok(ns['helper_version'](str(_copy)) != hv, 'versions: a locally edited rhino-model check script changes the fingerprint')
    _sh.copy(repo / 'skills/rhino-model/scripts/as-check.py', _model / 'as-check.py')
    (_model / 'as-check-model.py').unlink()
    ok(ns['helper_version'](str(_copy)) != hv, 'versions: a missing rhino-model check script changes the fingerprint')
    _sh.copy(repo / 'skills/rhino-model/scripts/as-check-model.py', _model / 'as-check-model.py')
    _copy.write_text(script.read_text() + '\n# local edit\n')
    ok(ns['helper_version'](str(_copy)) != hv, 'versions: an edited team helper changes the fingerprint')
    ok(ns['plugin_version'](str(_copy)) == 'unknown', 'versions: no plugin.json above the helper reads as unknown')

# ---- Fixes from the Sonnet skill-on series
# 1. Served test: the same as the measured runs' grader, through the owner's own equipment.
via_equipment = copy.deepcopy(SETOUT)
via_equipment['points'] = [{'owner': 'Plumbing', 'system': 'Drain', 'role': 'source', 'name': 'exit', 'at': [10, 10, 0]},
                           {'owner': 'Plumbing', 'system': 'Drain', 'role': 'point', 'name': 'WC', 'at': [10, 10, 120]}]
recs = fix_note(good())
recs[2] = rec('plumbing.3dm', 'Plumbing::Drain', (9, 9, 20, 11, 11, 120), 'riser above the tank')
recs.append(rec('plumbing.3dm', 'Plumbing::Equipment', (5, 5, 0, 15, 15, 20), 'tank at the source'))
out = analyse(via_equipment, recs, STAMPS)
ok(out['counts']['points_served'] == 1 and out['unserved_points'] == [], 'served: a run reaching its source through the owner\'s equipment counts as served', out['unserved_points'])
recs2 = [r for r in recs if r['layer'] != 'Plumbing::Drain']
ok(analyse(via_equipment, recs2, STAMPS)['counts']['points_served'] == 0, 'served: equipment alone does not serve a point')
other = [r for r in recs if r['layer'] != 'Plumbing::Equipment'] + [rec('mechanical.3dm', 'Mechanical::Equipment', (5, 5, 0, 15, 15, 20), 'another owner\'s unit')]
ok(analyse(via_equipment, other, STAMPS)['counts']['points_served'] == 0, 'served: another owner\'s equipment is no path')

# 2. Set-out: levels from the host's floors, shares clear of the host's solids.
host = [{'layer': 'Shell::Floors', 'name': 'Cellar slab', 'box': [0, 0, -6, 240, 540, 0]},
        {'layer': 'Shell::Floors', 'name': 'F1 subfloor', 'box': [0, 0, 107, 240, 540, 108]},
        {'layer': 'Shell::Floors', 'name': 'Roof subfloor', 'box': [0, 0, 587, 240, 540, 588]},
        {'layer': 'Shell::Walls', 'name': 'Front wall', 'box': [0, -12, -12, 240, 0, 600]},
        {'layer': 'Shell::Openings', 'name': 'Shaft at F1', 'box': [100, 250, 96.5, 122, 274, 108.5]},
        {'layer': 'Shell::Openings', 'name': 'Shaft at Roof', 'box': [100, 250, 576.5, 122, 274, 588.5]}]
lv = ns['levels_from'](host)
ok(lv == [{'name': 'Cellar', 'z': 0}, {'name': 'F1', 'z': 108}, {'name': 'Roof', 'z': 588}], 'set-out: levels_from reads one level per floor, at its top', lv)
ok(ns['normalize_levels']({'F1': 108, 'Cellar': 0}) == [{'name': 'Cellar', 'z': 0.0}, {'name': 'F1', 'z': 108.0}], 'set-out: levels given as a dict are written as a list')
good_so = {'levels': lv, 'owners': SETOUT['owners'], 'min_sizes': {'Plumbing::Drain': [4, 4]},
           'shares': [{'owner': 'Plumbing', 'zone': 'shaft plumbing', 'box': [100, 250, 0, 110, 274, 600]}],
           'shared_spaces': [{'name': 'Shaft', 'box': [100, 250, 0, 122, 274, 600], 'owners': ['Plumbing']}]}
res = ns['setout_check'](good_so, host)
ok(res['problems'] == [], 'set-out: levels on the floors and a shaft share through the openings pass', res)
bad_levels = dict(good_so, levels=lv + [{'name': 'F1 ceiling', 'z': 97}])
ok(any('F1 ceiling' in x for x in ns['setout_check'](bad_levels, host)['problems']), 'set-out: a ceiling given as a level is refused')
ok(any('host floor Roof' in x for x in ns['setout_check'](dict(good_so, levels=lv[:2]), host)['problems']), 'set-out: a host floor with no level is refused')
ok(any('no levels' in x for x in ns['setout_check'](dict(good_so, levels=[]), host)['problems']), 'set-out: no levels is refused')
in_wall = dict(good_so, shares=good_so['shares'] + [{'owner': 'Plumbing', 'zone': 'front lane', 'box': [50, -5, 10, 60, 20, 20]}])
ok(any('front lane' in x and 'Front wall' in x for x in ns['setout_check'](in_wall, host)['problems']), 'set-out: a share running into a host solid is refused')
big = dict(good_so, shares=good_so['shares'] + [{'owner': 'Plumbing', 'zone': 'whole cellar', 'box': [0, 0, 1, 240, 240, 90]}])
chk = ns['setout_check'](big, host)
ok(any('whole cellar' in w for w in chk['warnings']), 'set-out: a share far larger than its owner\'s runs is warned', chk)
slot = dict(good_so, shared_spaces=good_so['shared_spaces'] + [{'name': 'Slot', 'box': [150, 148, 83, 180, 156, 97], 'owners': ['Plumbing', 'Mechanical']}],
            shares=good_so['shares'] + [{'owner': 'Plumbing', 'zone': 'slot plumbing', 'box': [150, 148, 83, 160, 156, 97]}])
res = ns['setout_check'](slot, host)['problems']
ok(len(res) == 1 and 'Slot: no share for Mechanical' in res[0], 'set-out: a shared space with no share for one of the owners passing through it is refused', res)
ok(any('declares no shared_spaces' in x for x in ns['setout_check'](dict(good_so, shared_spaces=[]), host)['problems']), 'set-out: shares with no declared shared spaces are refused')
ok(callable(ns.get('check_setout')) and callable(ns.get('host_records')), 'set-out: check_setout() and host_records() exist for the coordinator')

# 3. Review notes carry only the team check's fault kinds.
ok(ns['FAULT_KINDS'] == ('clash', 'through_shell', 'unserved', 'undersize', 'reservation', 'note'), 'review: issue kinds are the team check\'s lists')
note_src = script.read_text().split('def note(', 1)[1].split('\ndef ', 1)[0]
ok('issue_kind not in FAULT_KINDS' in note_src and 'ruling, not an issue' in note_src, 'review: note() refuses an issue kind the team check does not list')
_skill = (skill / 'SKILL.md').read_text(encoding='utf-8')
ok('post_fault_notes' in _skill and 'Do not retype faults' in _skill, 'review: fault notes come from the team check, not the coordinator\'s reading')
ok('levels_from(' in _skill and 'check_setout()' in _skill and 'Size each share to the runs it holds' in _skill, 'skill: set-out levels, share size and check_setout are in the procedure')

# ---- Fixes from the skill-on smoke run
import os as _os, tempfile as _tf2

def fresh(me, folder, doc=None):
    """A new namespace for the helpers, as one agent's session would load them."""
    env = {'AS_SCRIPT_FILE': str(script), 'AS_TEAM': {'folder': folder, 'me': me, 'round': 1}}
    if doc is not None:
        env['__rhino_doc__'] = doc
    exec(compile(script.read_text(encoding='utf-8'), str(script), 'exec'), env)
    return env


class _Doc:
    def __init__(self, path):
        self.Path = path


# 1. The coordinator's round-0 preflight does not require the set-out it has not written yet.
with _tf2.TemporaryDirectory() as _f:
    target = _os.path.join(_f, 'setout.3dm')
    pf = fresh('coordinator', _f, _Doc(target))['preflight']()
    ok(pf['clear'] and pf['problems'] == [] and any('write the set-out' in s for s in pf['next']),
       'fix 1: the coordinator\'s preflight is clear before the set-out exists, with writing it as the next step', pf)
    pf = fresh('coordinator', _f, _Doc(None))['preflight']()
    ok(pf['clear'] and any('save your open document as' in s for s in pf['next']), 'fix 1: an untitled coordinator document is told where to save', pf)
    pf = fresh('Plumbing', _f, _Doc(_os.path.join(_f, 'plumbing.3dm')))['preflight']()
    ok(not pf['clear'] and any('coordinator writes the set-out' in s for s in pf['problems']), 'fix 1: an owner still waits for the set-out', pf)
    pf = fresh('coordinator', _f)['preflight']()
    ok(not pf['clear'] and any('no open Rhino document' in s for s in pf['problems']), 'fix 1: no open document still stops the coordinator', pf)

# 2. Every owner that needs a shared space gets a share in it before the set-out is issued.
gaps = ns['setout_problems'](SETOUT)
ok(gaps == [], 'fix 2: a set-out that gives every listed owner a share has no gaps', gaps)
shaft = dict(SETOUT, shared_spaces=[{'name': 'Shaft', 'box': [0, 0, 0, 30, 30, 99], 'owners': ['Plumbing', 'Mechanical']}],
             shares=[{'owner': 'Plumbing', 'zone': 'shaft plumbing', 'box': [0, 0, 0, 30, 30, 99]}])
gaps = ns['setout_problems'](shaft)
ok(len(gaps) == 1 and 'no share for Mechanical' in gaps[0], 'fix 2: a shared space with no share for one of its owners is refused', gaps)
both = dict(shaft, shares=shaft['shares'] + [{'owner': 'Mechanical', 'zone': 'shaft mechanical', 'box': [20, 0, 0, 30, 30, 99]}])
gaps = ns['setout_problems'](both)
ok(any('shares overlap' in g for g in gaps) and not any('no share' in g for g in gaps), 'fix 2: overlapping shares are refused', gaps)
split = dict(shaft, shares=[{'owner': 'Plumbing', 'zone': 'p', 'box': [0, 0, 0, 15, 30, 99]}, {'owner': 'Mechanical', 'zone': 'm', 'box': [15, 0, 0, 30, 30, 99]}])
ok(ns['setout_problems'](split) == [], 'fix 2: a shaft split between its owners passes')
undeclared = dict(SETOUT); undeclared.pop('shared_spaces')
ok(any('declares no shared_spaces' in g for g in ns['setout_problems'](undeclared)), 'fix 2: shares with no declared shared spaces cannot be checked')
out = analyse(shaft, fix_note(good()), STAMPS)
ok(not out['settled'] and out['counts']['setout_gaps'] == 1 and '1 setout gaps' in status_line(out), 'fix 2: the team check refuses settled on a set-out gap', out['setout_gaps'])
ok(callable(ns.get('check_setout')), 'fix 2: check_setout() exists for the coordinator')

# 3. Stamping an old revision is reported as stale, not current.
ok(ns['stamp_status']('2', 2) == 'current', 'fix 3: a stamp on the current revision reads current')
st = ns['stamp_status']('1', 2)
ok(st.startswith('stale') and 'revision 1' in st and 'revision 2' in st, 'fix 3: a stamp on an older revision reads stale with both revisions', st)
ok(ns['stamp_status'](None, 2).startswith('not stamped'), 'fix 3: no stamp reads not stamped')
stamp_src = script.read_text().split('def stamp(', 1)[1].split('\ndef ', 1)[0]
ok('"status": stamp_status(revision, current)' in stamp_src and 'current = setout()["revision"]' in stamp_src,
   'fix 3: stamp() reports its status against the set-out as it is now')

# 4. A host file no agent writes can reach settled.
given = copy.deepcopy(SETOUT)
given['owners'][0]['given'] = True                                   # Shell: a given shell nobody writes
bare_shell = dict(STAMPS, **{'shell.3dm': {'__geom_fp_now__': 'g1-x'}})  # no stamp, no own check, no version
out = analyse(given, fix_note(good()), bare_shell)
ok(out['settled'] and out['given_files'] == ['shell.3dm'], 'fix 4: a given host file with no stamps does not block settled', out['counts'])
out = analyse(SETOUT, fix_note(good()), bare_shell)
ok(not out['settled'] and out['counts']['stale_files'] == 1 and out['counts']['version_mismatches'] == 1,
   'fix 4: the same file not marked given is still checked', out['counts'])
moved = fix_note(good()) + [rec('shell.3dm', 'Shell::Floors', (5, 5, 50, 15, 15, 51), 'slab')]
ok(analyse(given, moved, bare_shell)['counts']['unopened_crossings'] >= 1, 'fix 4: a given host\'s geometry is still measured for crossings')

# ---- The set-out check runs inside the team check and on every reissue (TS3: a mid-run redraw left two shares overlapping)
redrawn = copy.deepcopy(SETOUT)
redrawn['shares'] = redrawn['shares'] + [{'owner': 'Shell', 'zone': 'redrawn closet', 'box': [10, 10, 0, 20, 20, 50]}]   # overlaps Plumbing's chase
out = analyse(redrawn, fix_note(good()), STAMPS)
ok(not out['settled'] and any('shares overlap' in g and 'redrawn closet' in g for g in out['setout_gaps']),
   'auto check: a redrawn share overlapping another owner\'s is caught by the team check', out['setout_gaps'])
into_host = copy.deepcopy(SETOUT)
into_host['shares'] = into_host['shares'] + [{'owner': 'Plumbing', 'zone': 'through the slab', 'box': [70, 70, 95, 80, 80, 105]}]
into_host['shared_spaces'] = into_host['shared_spaces']
out = analyse(into_host, fix_note(good()), STAMPS)
ok(any('through the slab' in g and 'slab F1' in g for g in out['setout_gaps']), 'auto check: the team check measures shares against the host\'s saved geometry', out['setout_gaps'])
issue_src = script.read_text().split('def issue(', 1)[1].split('\ndef ', 1)[0]
ok('"setout_check": setout_check(setout(), host_records(), requests=owner_requests())' in issue_src, 'auto check: issue() runs the set-out check on every reissue')

# ---- A host that is not an owner (a given shell named by host_file): the set-out checks still read it
with _tf2.TemporaryDirectory() as _f:
    for _n in ('setout.3dm', 'house-mechanical.3dm', 'house-shell.3dm'):
        open(_os.path.join(_f, _n), 'w').close()
    so_ = {'owners': [{'name': 'Mechanical', 'file': 'house-mechanical.3dm'}]}
    ok(ns['host_path'](dict(so_, host_file='house-shell.3dm'), _f) == _os.path.join(_f, 'house-shell.3dm'), 'host_file: the set-out names a host that is not an owner')
    ok(ns['host_path'](so_, _f) == _os.path.join(_f, 'house-shell.3dm'), 'host_file: without it, the one other .3dm in the folder is the host')
    open(_os.path.join(_f, 'scratch.3dm'), 'w').close()
    ok(ns['host_path'](so_, _f) is None, 'host_file: two candidates and no host_file: no guess')
    ok(ns['host_path'](dict(SETOUT), _f) == _os.path.join(_f, 'shell.3dm'), 'host_file: a host owner\'s own file comes first')
post = [{'file': 'house-shell.3dm', 'layer': 'Shell::Structure', 'root': 'Shell', 'name': 'Post in the shaft', 'id': 'post', 'user': {},
         'bb': (100, 266, 0, 122, 274, 600), 'kind': 'solid'}]
nohost = copy.deepcopy(SETOUT); nohost['host'] = None
nohost['shares'] = nohost['shares'] + [{'owner': 'Plumbing', 'zone': 'Cellar rear A', 'box': [110, 260, 10, 120, 280, 90]}]
nohost['shared_spaces'] = nohost['shared_spaces']
recs = [r for r in fix_note(good()) if 'Openings' not in r['layer'] and 'Penetrations' not in r['layer']]
out = analyse(nohost, recs, STAMPS, host_geometry=post)
ok(any('Cellar rear A' in g and 'Post in the shaft' in g for g in out['setout_gaps']) and not out['settled'],
   'host_file: the team check catches a share running into a post in a host that is not an owner', out['setout_gaps'])
ok(not any('Post in the shaft' in g for g in analyse(nohost, recs, STAMPS)['setout_gaps']), 'host_file: without host geometry the post cannot be seen (the gap this closes)')
check_src = script.read_text().split('def check(folder', 1)[1].split('\ndef ', 1)[0]
hr_src = script.read_text().split('def host_records(', 1)[1].split('\ndef ', 1)[0]
ok('host_geometry=host_geometry' in check_src and 'host_path(' in check_src and 'host_path(' in hr_src,
   'host_file: the team check and host_records() (used by issue() and check_setout()) both resolve the host file')

# ---- Barn eval fixes
# 1. The coordinator's own open notes in setout.3dm count in the team check.
ruling = {'file': 'house-x', 'layer': 'Notes', 'root': 'Notes', 'name': 'ruling note', 'id': 'r9-dot', 'kind': 'dot', 'bb': (1, 1, 1, 1, 1, 1),
          'user': {'note_id': 'r9', 'from': 'coordinator', 'to': 'Plumbing', 'kind': 'ruling', 'status': 'open', 'round': '5'}, 'text': 'move it'}
other = {'file': 'setout', 'layer': 'Share::Plumbing', 'root': 'Share', 'name': 'chase', 'id': 's1', 'kind': 'solid', 'bb': (5, 5, 0, 15, 15, 99), 'user': {}}
sn = ns['setout_notes']([ruling, other])
ok(len(sn) == 1 and sn[0]['file'] == 'setout.3dm', 'notes: setout_notes() takes the set-out\'s notes only, labelled with its file', sn)
out = analyse(SETOUT, fix_note(good()) + sn, STAMPS)
ok(not out['settled'] and out['counts']['open_notes'] == 1 and out['open_notes_by_addressee'].get('Plumbing') == ['r9'],
   'notes: an open ruling in setout.3dm blocks settled', out['counts'])
closed = dict(ruling, user=dict(ruling['user'], status='closed'))
ok(analyse(SETOUT, fix_note(good()) + ns['setout_notes']([closed]), STAMPS)['settled'], 'notes: a closed ruling in setout.3dm does not')
chk = script.read_text().split('def check(folder', 1)[1].split('\ndef ', 1)[0]
ok('records, strings = list(setout_notes(crecs))' in chk, 'notes: the team check reads the set-out\'s notes')

# 2. A crossing share: an owner's run through the host, covered where an opening exists or is requested.
wall = [{'layer': 'Structure::Sheathing', 'name': 'East wall sheathing', 'box': [358, 0, 0, 360, 480, 120]},
        {'layer': 'Structure::Floors', 'name': 'Slab', 'box': [0, 0, -4, 360, 480, 0]}]
xso = {'levels': [{'name': 'Ground', 'z': 0}], 'owners': [{'name': 'HVAC', 'file': 'barn-hvac.3dm'}, {'name': 'Structure', 'file': 'barn-structure.3dm'}],
       'shares': [{'owner': 'HVAC', 'zone': 'line set inside', 'box': [340, 300, 90, 358, 306, 96]}],
       'shared_spaces': [{'name': 'East wall', 'box': [340, 300, 90, 362, 306, 96], 'owners': ['HVAC']}]}
cross = {'owner': 'HVAC', 'zone': 'line set through east wall', 'box': [357, 300, 90, 361, 306, 96], 'crossing': True}
req = [{'layer': 'Interface::Penetrations', 'box': [357, 299.5, 89.5, 361, 306.5, 96.5], 'user': {'from': 'HVAC'}}]
res = ns['setout_check'](dict(xso, shares=xso['shares'] + [cross]), wall, requests=req)['problems']
ok(res == [], 'crossing: a crossing share through the wall inside the owner\'s opening request passes', res)
res = ns['setout_check'](dict(xso, shares=xso['shares'] + [cross]), wall, requests=[])['problems']
ok(any('crossing share line set through east wall' in x and 'no opening exists or is requested' in x for x in res), 'crossing: with no request or opening it is refused', res)
other_req = [dict(req[0], user={'from': 'Plumbing'})]
ok(ns['setout_check'](dict(xso, shares=xso['shares'] + [cross]), wall, requests=other_req)['problems'], 'crossing: another owner\'s request does not cover it')
opening = wall + [{'layer': 'Structure::Openings', 'name': 'HVAC east opening', 'box': [356, 299, 89, 362, 307, 97]}]
ok(ns['setout_check'](dict(xso, shares=xso['shares'] + [cross]), opening, requests=[])['problems'] == [], 'crossing: an existing host opening covers it')
plain = dict(cross, crossing=False)
res = ns['setout_check'](dict(xso, shares=xso['shares'] + [plain]), wall, requests=req)['problems']
ok(any('crossing=True' in x for x in res), 'crossing: an ordinary share in the wall is still refused, and told how to cover a crossing', res)
ok('crossing=False' in script.read_text().split('def share(', 1)[1].split('\n', 1)[0], 'crossing: share() takes crossing')
_sk = (skill / 'SKILL.md').read_text(encoding='utf-8')
ok('crossing=True' in _sk and "the owner's own opening request" in _sk, 'skill: step 3 says how a share meets a host crossing')
ok('**Reissue the set-out at most once a round, and only when shares change.**' in _sk and 'Save the reissued set-out before running the team check' in _sk,
   'skill: the set-out churn rule is stated')

# ---- A reissue makes stale only what it touched (a reissue once left 20 requests stale)
od = ns['owner_digest']; cs = ns['current_since']
rev2 = copy.deepcopy(SETOUT)                       # revision 2: the fixture
rev1 = copy.deepcopy(SETOUT); rev1['revision'] = 1
rev1['shares'] = [dict(s, box=[40, 40, 0, 60, 60, 90]) if s['owner'] == 'Shell' else s for s in rev1['shares']]   # rev 2 moved only Shell's share
rev2['owner_digests'] = {'1': dict((o['name'], od(rev1, o['name'])) for o in rev1['owners'])}
rev2['revision_rounds'] = {'1': 0, '2': 4}
ok(cs(rev2, 'Plumbing') == 1 and cs(rev2, 'Shell') == 2, 'carry: an owner the reissue did not touch is current since the older revision', (cs(rev2, 'Plumbing'), cs(rev2, 'Shell')))
ok(cs(SETOUT, 'Plumbing') == 2, 'carry: without recorded digests every owner is current only at the new revision')
old_stamp = strings(plumbing='1')
for r in fix_note(good()):
    pass
recs = fix_note(good()); recs[3]['user'].update(setout_revision='1')        # Plumbing's request stamped at revision 1
out = analyse(rev2, recs, old_stamp, round_no=4)
ok(out['counts']['stale_files'] == 0 and out['counts']['stale_references'] == 0 and 'Plumbing' not in out['stale_by_owner'],
   'carry: Plumbing\'s file and request at revision 1 are carried forward', (out['counts'], out['stale_by_owner']))
out = analyse(dict(rev2, owner_digests={}), recs, old_stamp, round_no=4)
ok(out['counts']['stale_files'] == 1 and out['counts']['stale_references'] >= 1, 'carry: the same stamps are stale when the reissue touched Plumbing', out['counts'])

# Real staleness, named per owner with its action, and handed to the coordinator only after a round.
touched = dict(rev2, owner_digests={'1': dict(rev2['owner_digests']['1'], Plumbing='changed')})
out = analyse(touched, recs, old_stamp, round_no=4)
items = out['stale_by_owner'].get('Plumbing', [])
kinds = sorted((i['kind'], i['action']) for i in items)
ok(('file', 'rebuild') in kinds and ('request', 're-stamp') in kinds, 'stale: Plumbing\'s file to rebuild and its still-valid request to re-stamp', items)
ok(all(not i['for_coordinator'] for i in items), 'stale: not for the coordinator in the round of the reissue', items)
moved = copy.deepcopy(recs); moved[3]['bb'] = (60, 60, 99.5, 63, 63, 101.5)   # a request outside every share and opening
out = analyse(touched, moved, old_stamp, round_no=5)
items = out['stale_by_owner'].get('Plumbing', [])
ok(any(i['kind'] == 'request' and i['action'] == 'rebuild' for i in items), 'stale: a request that no longer holds is to rebuild', items)
ok(all(i['for_coordinator'] for i in items), 'stale: left a round after the reissue, it goes to the coordinator', items)
ok(callable(ns.get('restamp_requests')), 'stale: restamp_requests() exists for owners')
_sk2 = (skill / 'SKILL.md').read_text(encoding='utf-8')
ok('clear your own stale items this turn without waiting for a note' in _sk2 and '`for_coordinator`' in _sk2, 'skill: owners clear their own stale items; the coordinator directs only what waited a round')

# ---- The team check writes the fault notes
fn, sp = ns['fault_notes'], ns['sync_plan']
FSO = {'owners': [{'name': 'Structure', 'file': 's.3dm'}, {'name': 'Plumbing', 'file': 'p.3dm'}, {'name': 'HVAC', 'file': 'h.3dm'}],
       'host': 'Structure', 'priority': ['Plumbing drains', 'HVAC ducts'],
       'shares': [{'owner': 'HVAC', 'zone': 'hv lane', 'box': [0, 0, 0, 10, 10, 10]}],
       'points': [{'owner': 'Plumbing', 'system': 'Drain', 'role': 'point', 'name': 'WC', 'at': [5, 5, 5]}]}
b_ = lambda f, layer, name, box: {'file': f, 'layer': layer, 'name': name, 'id': name + '-id', 'box': box}
res = {'clashes': [{'a': b_('p.3dm', 'Plumbing::Drain', 'drain', [2, 2, 2, 4, 4, 4]), 'b': b_('h.3dm', 'HVAC::Supply', 'duct', [3, 3, 3, 5, 5, 5]), 'region': [3, 3, 3, 4, 4, 4]},
                   {'a': b_('p.3dm', 'Plumbing::Drain', 'drain2', [20, 2, 2, 24, 4, 4]), 'b': b_('h.3dm', 'HVAC::Supply', 'duct2', [21, 3, 3, 25, 5, 5]), 'region': [21, 3, 3, 24, 4, 4]}],
       'unopened_crossings': [{'a': b_('s.3dm', 'Structure::Walls', 'east wall', [30, 0, 0, 31, 50, 20]), 'b': b_('h.3dm', 'HVAC::Lineset', 'line set', [29, 5, 5, 32, 6, 6]), 'region': [30, 5, 5, 31, 6, 6]}],
       'share_breaks': [{'object': b_('p.3dm', 'Plumbing::Vent', 'vent', [1, 1, 1, 2, 2, 2]), 'zone': 'hv lane', 'shared_to': 'HVAC'}],
       'unserved_points': ['Plumbing Drain: WC'], 'own_check_failures': {'h.3dm': ['within Supply', 'named']},
       'notes_for_coordinator': [{'id': 'n1', 'to': 'HVAC', 'from': 'Plumbing', 'by': None, 'at': [1, 1, 1]},
                                 {'id': 'n2', 'to': 'Plumbing', 'from': 'coordinator', 'by': 'team-check', 'at': [1, 1, 1]}]}
w = fn(res, FSO)
by = dict((x['key'], x) for x in w)
ok(by['clash|HVAC:duct|Plumbing:drain']['to'] == 'Plumbing', 'fault notes: a clash inside one owner\'s share goes to the other owner', w)
ok(by['clash|HVAC:duct2|Plumbing:drain2']['to'] == 'HVAC', 'fault notes: otherwise the lower one in the priority order moves')
ok(by['through_shell|HVAC:line set']['to'] == 'HVAC' and by['through_shell|HVAC:line set']['issue_kind'] == 'through_shell', 'fault notes: a run through the host goes to the run\'s owner')
ok(by['reservation|Plumbing:vent|hv lane']['to'] == 'Plumbing', 'fault notes: a share break goes to the owner out of its share')
ok(by['unserved|Plumbing Drain: WC']['to'] == 'Plumbing' and by['unserved|Plumbing Drain: WC']['at'] == [5, 5, 5], 'fault notes: an unserved point goes to its owner, at the point')
ok('undersize|HVAC|within Supply' in by and not any('named' in k for k in by), 'fault notes: a failed within check is an undersize note; other own-check items are not')
ok('note|n1' in by and 'note|n2' not in by, 'fault notes: an unanswered owner note is escalated; the check\'s own notes are not')
ok(len(w) == len(set((x['key'], x['to']) for x in w)) and all(x['issue_kind'] in ns['FAULT_KINDS'] for x in w), 'fault notes: one note per fault, kinds the grader knows')
plan = sp(w, [])
ok(len(plan['write']) == len(w) and plan['close'] == [], 'sync: first round writes one note per fault')
opened = [{'id': 'id%d' % i, 'fault_key': x['key'], 'to': x['to']} for i, x in enumerate(w)]
plan = sp(w, opened)
ok(plan['write'] == [] and plan['close'] == [] and plan['kept'] == len(w), 'sync: no duplicate for a fault whose note is still open')
fixed = [x for x in w if not x['key'].startswith('clash|HVAC:duct|')]
plan = sp(fixed, opened)
ok(plan['write'] == [] and len(plan['close']) == 1, 'sync: the note for a fixed fault is closed')
ok(callable(ns.get('post_fault_notes')) and ns.get('CHECK_BY') == 'team-check', 'sync: post_fault_notes() writes notes marked by the team check')

# Touching is not a clash.
touch = fix_note(good()) + [rec('mechanical.3dm', 'Mechanical::Supply', (70, 70, 0, 90, 90, 50), 'duct'), rec('plumbing.3dm', 'Plumbing::Gas', (90, 70, 10, 95, 72, 12), 'gas')]
ok(analyse(SETOUT, touch, STAMPS)['counts']['clashes'] == 0, 'team: touching solids do not clash')
# The Rhino solid test can clear a box overlap.
over = fix_note(good()) + [rec('mechanical.3dm', 'Mechanical::Supply', (70, 70, 0, 90, 90, 50), 'duct'), rec('plumbing.3dm', 'Plumbing::Gas', (80, 80, 10, 95, 82, 12), 'gas')]
ok(analyse(SETOUT, over, STAMPS, penetrates=lambda a, b: False)['counts']['clashes'] == 0, 'team: the solid test decides after a box overlap')
# One agent, one file holding every owner: no ownership break, and its own trades can still clash.
single = copy.deepcopy(SETOUT)
single['owners'] = [{'name': n, 'file': 'all.3dm'} for n in ('Shell', 'Plumbing', 'Mechanical')]
one = [dict(r, file='all.3dm') for r in fix_note(good())]
out = analyse(single, one, {'all.3dm': owner_strings(), 'setout.3dm': dict(VERSION)})
ok(out['settled'] and out['counts']['ownership_breaks'] == 0, 'team: the single role settles in one file', out['counts'])
one.append(rec('all.3dm', 'Plumbing::Gas', (45, 45, 10, 47, 47, 12), 'gas'))
ok(analyse(single, one, {'all.3dm': owner_strings(), 'setout.3dm': dict(VERSION)})['counts']['share_breaks'] == 1, 'team: the single file still keeps shares')
# No host: crossings are ordinary clashes and requests are not expected.
nohost = dict(SETOUT, host=None)
out = analyse(nohost, [r for r in fix_note(good()) if 'Openings' not in r['layer'] and 'Penetrations' not in r['layer']], STAMPS)
ok(out['counts']['clashes'] == 1 and out['counts']['requests_without_opening'] == 0, 'team: without a host a crossing is a clash', out['counts'])

# ---- What the skill may claim
text = (skill / 'SKILL.md').read_text(encoding='utf-8')
evidence = (skill / 'references/evidence.md').read_text(encoding='utf-8')
ok('one agent was as good where it was tried' in text.lower(), 'claims: the skill says one agent did as well')
ok('set out space first and review every round' in text and '2 of 2' in text and '0 of 3' in text and '1 of 3' in text and 'A direction, not a measurement' in text,
   'claims: the up-front-plus-review evidence is stated with its figures and its strength')
ok('2 to 4 rounds' in text, 'claims: no setup recovered from the change in its round')
ok('did no better than none' in text, 'claims: space on request is not presented as a gain')
step6 = text.split('6. **The team check writes the fault notes; you keep the judgment.**', 1)[1].split('\n7. ', 1)[0] if '6. **The team check writes the fault notes; you keep the judgment.**' in text else ''
ok('Placeholder' not in text, 'skill: the review-and-direct placeholder is replaced')
ok(step6 and 'post_fault_notes' in step6 and 'Do not retype faults as notes yourself' in step6 and 'You never model' in step6
   and 'no second note' in step6 and 'closes its own notes' in step6, 'skill: step 6 runs the helper every round and keeps judgment only')
for fault in ('clashes', 'share breaks', 'without an opening', 'unserved points', '`within`', 'unanswered'):
    ok(fault in step6, 'skill: step 6 says the helper covers %s' % fault)
for judgment in ('disputes', 'set-out changes', "architect's change order"):
    ok(judgment in step6, 'skill: step 6 keeps judgment: %s' % judgment)
ok('ask for space' not in text.lower() and 'reserve(' not in text, 'skill: asking for space is not the main mode')
ok(re.search(r'A change goes to the coordinator first.*issue\(', text), 'skill: a change goes to the coordinator first, through issue()')
ok('No measured run loaded any Arch Studio skill' in text and 'No measured run used rhino-model' in evidence, 'claims: no run used skills')
ok('delivered to the owners before the coordinator' in evidence, 'claims: the change-order correction is stated')
ok('direction only' in evidence and '$0.28' in evidence and '18 runs' in evidence, 'claims: evidence keeps its limits and the single-agent cost')
ok('## Test 3' in evidence and '**2 of 2**' in evidence and 'including all of test 3' in evidence and 'not comparable' in evidence,
   'claims: test 3 is in the evidence with its caveats')
for word in ('outperform', 'beats a single', 'better than one agent', 'proven', 'validated'):
    ok(word not in (text + evidence).lower(), 'claims: no "%s"' % word)
for link in re.findall(r'\]\(([^)#]+)\)', text):
    ok((skill / link).resolve().exists(), 'skill: link resolves: %s' % link)
for helper in ('summary', 'note', 'close', 'stamp', 'request_opening', 'share', 'release', 'write_setout', 'issue', 'save', 'others', 'setout', 'preflight'):
    ok(callable(ns.get(helper)), 'skill: helper %s exists' % helper)
for gone in ('reserve', 'control'):
    ok(gone not in ns, 'skill: no %s helper' % gone)
ok('"AS_MODE": "check"' in text and 'Team: settled' in text, 'skill: the check call and its status line are named')
contract = (repo / 'docs/host-harness-contract.md').read_text(encoding='utf-8')
exception = contract.split('### Named exception: Rhino skill helpers', 1)[1].split('\n## ', 1)[0] if '### Named exception: Rhino skill helpers' in contract else ''
ok(exception and all('`%s`' % s in exception for s in ('rhino-model', 'rhino-batch-image-export', 'rhino-thinline', 'rhino-bom', 'rhino-agent-team'))
   and 'only exception' in exception and 'hosted MCP' in exception and '**Plugin-only**' in exception,
   'contract: the Rhino helper exception names its skills, its limit and the plugin-only decision')
import json as _json
for name in ('rhino-agent-team', 'rhino-model', 'rhino-batch-image-export', 'rhino-thinline', 'rhino-bom'):
    hc = _json.loads((repo / 'skills' / name / 'host-contract.json').read_text())
    ok(hc['execution'].get('delivery') == 'plugin-only', 'plugin-only: %s declares it in its host contract' % name)
    ok('**Plugin-only' in (repo / 'skills' / name / 'SKILL.md').read_text(), 'plugin-only: %s says so in its requirements' % name)
changelog = (repo / 'CHANGELOG.md').read_text().split('## [1.5.3]')[0]
ok('### Known limits' in changelog and 'plugin-only' in changelog, 'plugin-only: the changelog states it as a known limit')
scripted = sorted(p.parent.parent.name for p in repo.glob('skills/*/scripts/*.py') if p.parent.parent.name.startswith('rhino-'))
ok(all(_json.loads((repo / 'skills' / n / 'host-contract.json').read_text())['execution'].get('delivery') == 'plugin-only' for n in set(scripted)),
   'plugin-only: every script-backed Rhino skill declares it', sorted(set(scripted)))
for name in ('rhino-model', 'rhino-batch-image-export', 'rhino-thinline', 'rhino-bom', 'rhino-agent-team'):
    ok(any((repo / 'skills' / name / 'scripts').glob('*.py')), 'contract: %s ships the helpers the exception covers' % name)
model = (repo / 'skills/rhino-model/SKILL.md').read_text(encoding='utf-8')
section = model.split('## When a set-out exists', 1)[1].split('\n## ', 1)[0] if '## When a set-out exists' in model else ''
ok(section and 'set-out rev N' in section and 'invariant 9' in section and 'coordinator' in section and 'Rebuild only what moved' in section,
   'rhino-model: the set-out section carries rules 1, 2, 4, 5 and 6')
ok('skip this section' in section, 'rhino-model: single-agent use skips the section')
ok('`within`' in section and 'set-out rev N' in section, 'rhino-model: rule 1 uses the within check')
ok('candidate lessons to the coordinator as a note' in section, 'rhino-model: lessons go to the coordinator in a team')
ok('one deliberate overlap' in text and 'Required points served'.lower() in text.lower() and 'caught by nobody' in text, 'skill: the points overlap is stated with its reason')
ok('file changed after its check' in text, 'skill: the stale-check rule is stated')
ok('Whoever finds an issue writes it, at the place' in text and 'addressed to the owner of the object that has to change' in text
   and 'never fixes another owner' in text, 'skill: whoever finds an issue writes the note to the owner of the object')
ok('read every open note, not only those addressed to you' in text and 'who moves when two owners each say the other should' in text,
   'skill: the coordinator reads all notes and decides only what owners cannot settle')
ok('kind `change`' in text and 'addressed to the coordinator' in text, 'skill: a change order enters as a note to the coordinator')
ok('review every round after a change until the team check is clean again' in text, 'skill: review continues after a change (set-out alone lost the model)')
ok('**Nothing is settled while a note is open.**' in text and 'never reports the model settled while any note is open' in text, 'skill: no settled with open notes')
ok('look before you save' in text and '`others()`' in text, 'skill: re-routed runs are checked against the others before saving')
ok('## Installing for a team' in text and '`extraKnownMarketplaces`' in text and '`enabledPlugins`' in text
   and 'does not install' in text and 'same release' in text, 'skill: installing for a team names the settings keys and the same-release rule')
ok('version mismatch' in text.lower(), 'skill: the version rule is stated')
ok('**Preflight, every agent, before anything else.**' in text and '../rhino-setup/SKILL.md' in text and 'preflight' in text, 'skill: preflight routes to rhino-setup')
ok('**Open design values go up, not out.**' in section and 'not issues found in the model' in section and 'Questions go up' not in section,
   'rhino-model: rule 4 covers open design values only')
ok('**An issue note is a correction.**' in section and 'do not change their objects' in section, 'rhino-model: issue notes from any agent are corrections')

# ---- No project terms or home paths in what ships (terms held as hashes, as in the other Rhino tests)
BANNED = {'b7d177840ebb2217', '297839fea58cd1e3', 'd1eeefe5edcb004c', 'dbe1dcf6a112e8b4', 'a569f8dbe4c6ad9d', '91287388e8e9e4db', '3bc7f74b69c3cb77', '6358bacbe7eb49e2'}
home = re.compile(r'/Users/|~/Documents')
for path in sorted(p for p in list(skill.rglob('*')) + [repo / 'clusters/modeling.json'] if p.is_file()):
    body = path.read_text(encoding='utf-8')
    words = re.findall(r'[a-z0-9-]+', body.lower())
    grams = words + [' '.join(pair) for pair in zip(words, words[1:])]
    hits = [g for g in grams if hashlib.sha256(g.encode()).hexdigest()[:16] in BANNED]
    ok(not hits and not home.search(body), 'ships: no project terms or home paths in %s' % path.relative_to(repo))

# ---- An owner's own stamp() re-stamps its requests that still hold (the Orca Sonnet run)
# In that run Windows called stamp() every round but never restamp_requests(): its 4 requests, stamped at revision 1,
# sat inside Structure's openings and stayed stale after the revision-3 reissue, so the team never settled.
# Replay with that run's request ids and boxes, on a stub of the owner's document.
class _P:
    def __init__(self, x, y, z): self.X, self.Y, self.Z = x, y, z
class _Geo:
    def __init__(self, bb): self.bb = bb
    def GetBoundingBox(self, _accurate): return types.SimpleNamespace(Min=_P(*self.bb[:3]), Max=_P(*self.bb[3:]))
class _Attr:
    def __init__(self, layer, name, user): self.LayerIndex, self.Name, self.user = layer, name, dict(user)
    def GetUserString(self, k): return self.user.get(k)
    def SetUserString(self, k, v): self.user[k] = v
    def Duplicate(self): return _Attr(self.LayerIndex, self.Name, self.user)
class _Obj:
    def __init__(self, oid, layer, name, bb, **user): self.Id, self.Attributes, self.Geometry = oid, _Attr(layer, name, user), _Geo(bb)
class _Objects(list):
    def ModifyAttributes(self, o, a, _quiet): o.Attributes = a; return True
class _Strings(dict):
    def SetString(self, k, v): self[k] = v
    def GetValue(self, k): return self.get(k)
ORCA_REQUESTS = [('1f126c52-980d-4557-938f-eb8065421b2f', (-0.5, 168.0, 36.0, 5.5, 204.0, 84.0)),
                 ('8287a926-f13b-4dd4-9acb-c29d63f3af00', (354.5, 168.0, 36.0, 360.5, 204.0, 84.0)),
                 ('73360738-f60b-4d19-9ff5-2edb55a240dd', (162.0, 474.5, 36.0, 198.0, 480.5, 84.0)),
                 ('8633f0eb-62bc-416a-911e-e42b8280edc3', (120.0, -0.5, 0.0, 240.0, 5.5, 96.0))]
layers = [types.SimpleNamespace(FullPath='Windows::Units'), types.SimpleNamespace(FullPath='Interface::Penetrations')]
wdoc = types.SimpleNamespace(Layers=layers, Strings=_Strings(setout_revision='1'),
                             Objects=_Objects([_Obj(i, 1, 'Opening request through Windows', bb, setout_revision='1', **{'from': 'Windows'}) for i, bb in ORCA_REQUESTS]
                                              + [_Obj('gone', 1, 'Opening request through Windows', (500, 500, 0, 506, 506, 10), setout_revision='1'),
                                                 _Obj('unit', 0, 'window W1', (0, 170, 38, 5, 202, 82))]))
openings = [{'layer': 'Structure::Openings', 'bb': (b[0] - 0.25, b[1] - 0.25, b[2] - 0.25, b[3] + 0.25, b[4] + 0.25, b[5] + 0.25)} for _, b in ORCA_REQUESTS]
saved = {k: ns[k] for k in ('_doc', 'setout', 'host_records')}
saved_cfg = dict(ns['CFG'])
ns['CFG'].update(me='Windows', round=5)
ns['_doc'] = lambda: wdoc
ns['setout'] = lambda: {'revision': 3, 'owners': [{'name': 'Windows', 'file': 'barn-windows.3dm'}], 'shares': [], 'host': 'Structure'}
ns['host_records'] = lambda: openings
try:
    before = ns['summary']() if False else None
    out = ns['stamp']()
    stamps = {o.Id: o.Attributes.GetUserString('setout_revision') for o in wdoc.Objects}
    ok(out['requests_restamped'] == 4 and all(stamps[i] == '3' for i, _ in ORCA_REQUESTS),
       'restamp: stamp() re-stamps the 4 Orca requests that still sit in Structure\'s openings', (out, stamps))
    ok(out['requests_to_rebuild'] == [('gone', 'Opening request through Windows')] and stamps['gone'] == '1',
       'restamp: a request that no longer holds is left stale and listed to rebuild', out)
    ok(wdoc.Strings['setout_revision'] == 3 or wdoc.Strings['setout_revision'] == '3', 'restamp: the file is stamped too', wdoc.Strings)
    wdoc.Objects[:] = [o for o in wdoc.Objects if o.Id != 'gone']
    again = ns['stamp']()
    ok(again['requests_restamped'] == 0 and again['requests_to_rebuild'] == [], 'restamp: a second stamp() has nothing left to do', again)
    ns['CFG']['me'] = 'coordinator'
    ok('requests_restamped' not in ns['stamp'](), 'restamp: the coordinator\'s stamp() touches no requests')
finally:
    ns.update(saved)
    ns['CFG'].clear(); ns['CFG'].update(saved_cfg)

# The same rule end to end on the fixture: after a reissue, the owner's ordinary turn (rebuild, check, stamp())
# leaves nothing stale, and the team settles without a note from the coordinator.
before = analyse(touched, recs, old_stamp, round_no=5)
ok(not before['settled'] and any(i['action'] == 're-stamp' for i in before['stale_by_owner'].get('Plumbing', [])),
   'restamp: before the owner\'s turn, Plumbing has a request to re-stamp', before['counts'])
pdoc = types.SimpleNamespace(Layers=[types.SimpleNamespace(FullPath='Interface::Penetrations')], Strings=_Strings(setout_revision='1'),
                             Objects=_Objects([_Obj('req', 0, 'request', recs[3]['bb'], setout_revision='1')]))
saved = {k: ns[k] for k in ('_doc', 'setout', 'host_records')}
saved_cfg = dict(ns['CFG'])
ns['CFG'].update(me='Plumbing', round=5)
ns['_doc'] = lambda: pdoc
ns['setout'] = lambda: touched
ns['host_records'] = lambda: [r for r in recs if r['layer'] == 'Shell::Openings']
try:
    turned = ns['stamp']()
finally:
    ns.update(saved)
    ns['CFG'].clear(); ns['CFG'].update(saved_cfg)
after_recs = copy.deepcopy(recs); after_recs[3]['user']['setout_revision'] = pdoc.Objects[0].Attributes.GetUserString('setout_revision')
after = analyse(touched, after_recs, strings(), round_no=5)
ok(turned['requests_restamped'] == 1 and after['settled'] and after['counts']['stale_references'] == 0,
   'restamp: after the owner\'s stamp() the team settles with no stale reference', (turned, after['counts']))

if failures:
    print('FAIL', len(failures))
    for line in failures:
        print(' -', line)
    sys.exit(1)
print('PASS: %d assertions on the rhino-agent-team check and claims' % passed[0])
PY
