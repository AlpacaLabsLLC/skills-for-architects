#!/usr/bin/env bash
# Seeded cases for as-rhino-bom, as-rhino-display and as-rhino-thinline.
# Rhino is not available here. A small stub stands in for the part of RhinoCommon the BOM reads
# (layers, object attributes, bounding boxes, mass properties). The display and PDF checks read
# real files written by this test. The Rhino drawing calls in as-sheet.py and the capture calls
# in as-display.py are not run; they need a live Rhino.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python3 - <<'PY'
import contextlib, csv, hashlib, io, json, math, re, struct, sys, tempfile, types, zlib
from pathlib import Path

root = Path.cwd() / 'skills'
failures = []
passed = [0]


def ok(condition, label, detail=''):
    if condition:
        passed[0] += 1
    else:
        failures.append('%s %s' % (label, str(detail)[:400]))


def load(path, **extra):
    ns = {'AS_SCRIPT_FILE': str(path), **extra}
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), ns)
    return ns


def run_print(fn, *args, **kwargs):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        value = fn(*args, **kwargs)
    return value, out.getvalue()


# ---- as-rhino-bom ----
BOM = load(root / 'rhino-bom/scripts/as-bom.py')


def obj(name, layer, dims, volume=None, area=None):
    return {'name': name, 'layer': layer, 'dims': sorted(dims), 'volume': (lambda: volume), 'area': (lambda: area)}


SPEC = {
    'covers': 'seeded layout', 'scopes': [{'layer': 'B::A', 'label': 'a'}],
    'sections': {'2x6': {'w': .038, 'd': .14, 'label': '2x6', 'stock': 3.6}}, 'kerf': .003,
    'rules': [
        {'match': 'Stud', 'category': 'Lumber', 'item': 'Stud', 'measure': 'section_length', 'section': '2x6'},
        {'match': 'Drain', 'category': 'Pipe', 'item': 'Drain', 'size': '110', 'measure': 'volume_over_pipe', 'dia': .11, 'material_assumed': True},
        {'match': 'Membrane', 'category': 'Roof', 'item': 'Membrane', 'measure': 'half_area', 'qty_is_total': True},
        {'match': 'Bolt', 'category': 'Connectors', 'item': 'Bolt', 'measure': 'count', 'to_engineer': True},
    ],
    'excluded': [{'match': 'Markup', 'reason': 'user markup'}],
    'allowances': [{'item': 'Lining', 'source': 'assumed', 'qty': 2, 'unit': 'sheets', 'note': 'not modeled'}],
    'not_counted': [{'item': 'Fasteners', 'reason': 'not modeled'}],
}
good = [obj('Stud', 'Walls', [.038, .14, 2.4]) for _ in range(3)] + [
    obj('Drain', 'Pipe', [.11, .11, 2.0], volume=math.pi * .055 ** 2 * 2.0),
    obj('Membrane', 'Roof', [.001, 4, 5], area=40.0), obj('Bolt', 'Connectors', [.01, .01, .3]), obj('Markup', 'Notes', [1, 1, 1])]
r = BOM['build'](good, SPEC)
ok(not r['failures'] and r['total'] == 7 and r['counted'] == 6 and sum(r['excluded'].values()) == 1, 'bom: clean case reconciles', r['failures'])
rows = [row for row in r['rows'][1:] if len(row) == len(BOM['HEADER'])]
ok(all(row[9] for row in rows), 'bom: every line has a source', rows)
ok(any('Measured from model' in row[9] for row in rows) and any(row[9].startswith('NOT MODELED: Assumed') for row in rows) and any(row[9].startswith('Calculated') for row in r['rows'][1:]), 'bom: measured, calculated and assumed are shown', rows)
ok(any('(material assumed)' in row[1] for row in rows), 'bom: an assumed material is labelled inside the line')
ok(any('to be engineered' in row[9] for row in rows), 'bom: hardware is marked to be engineered')
ok(any(row[1] == 'Membrane' and row[6] == 20.0 for row in rows), 'bom: a membrane is half its surface area', rows)
ok(any(row[1].startswith('Drain') and abs(row[6] - 2.0) < .01 for row in rows), 'bom: pipe length is volume over pipe area', rows)
ok(any(row[0] == 'Purchase' and row[3] == 3 for row in r['rows'][1:]), 'bom: purchase count is separate from cut length', r['rows'])

bad = build_bad = BOM['build'](good + [obj('Toilet seat', 'Fixtures', [.1, .3, .4])], SPEC)
ok(bad['failures'] and sum(bad['unclassified'].values()) == 1, 'bom: an unclassified object fails', bad)
ok(('Toilet seat', 'Fixtures') in bad['unclassified'], 'bom: the unclassified object is named', bad['unclassified'])
noname = BOM['build'](good + [obj('', 'Fixtures', [.1, .3, .4])], SPEC)
ok(noname['failures'], 'bom: an unnamed object fails')
wrong = BOM['build']([obj('Stud', 'Walls', [.5, .6, 2.4])], SPEC)
ok(wrong['failures'] and 'section' in wrong['errors'][0], 'bom: a section that does not fit fails', wrong['errors'])
openb = BOM['build']([obj('Drain', 'Pipe', [.11, .11, 2.0], volume=None)], SPEC)
ok(openb['failures'], 'bom: an open pipe that gives no volume fails, rather than counting zero', openb)

p = BOM['validate'](dict({k: v for k, v in SPEC.items() if k != 'not_counted'}))
ok(any('not_counted' in x for x in p), 'bom: a spec without not_counted is refused', p)
p = BOM['validate'](dict(SPEC, allowances=[{'item': 'X', 'source': 'measured'}]))
ok(any('calculated or assumed' in x for x in p), 'bom: an allowance cannot claim to be measured', p)

n, spliced = BOM['nest']([3.0, 3.0, 0.5, 0.5], 3.6, .003)
ok((n, spliced) == (2, 0), 'bom: nesting first-fit descending', (n, spliced))
ok(BOM['nest']([4.0], 3.6, 0)[1] == 1, 'bom: a cut over stock is a splice')

a = BOM['build'](good, SPEC)
b = BOM['build'](good + [obj('Stud', 'Walls', [.038, .14, 2.4])], SPEC)
v = BOM['varies']({'a': a, 'b': b})
ok(v['different'] and v['same'] > 0, 'bom: what varies between layouts is reported', v)


# Identical and near-identical cuts share a line, and every object stays accounted for.
GROUP = dict(SPEC, sections={'2x6': {'w': .038, 'd': .14, 'label': '2x6', 'stock': 7.2}}, rules=[SPEC['rules'][0]], allowances=[], excluded=[])
def studs(*lengths):
    return [obj('Stud', 'Walls', [.038, .14, x]) for x in lengths]
def cut_lines(result):
    return [row for row in result['rows'][1:] if len(row) == len(BOM['HEADER']) and row[4] == 'pcs']
lengths = [2.4, 2.4, 2.4, 2.41, 2.415, 3.0, 3.0]
g = BOM['build'](studs(*lengths), GROUP)
lines = cut_lines(g)
ok(not g['failures'] and g['total'] == 7 and g['counted'] == 7, 'bom group: grouped members still reconcile', g['failures'])
ok([(row[3], row[5]) for row in lines] == [(5, '2.4 to 2.415'), (2, 3.0)], 'bom group: near-identical cuts share a line with a count and a range', lines)
ok(sum(row[8] for row in lines) == 7 and sum(row[3] for row in lines) == 7, 'bom group: the objects and quantities on the lines add up to every object', lines)
ok(lines[0][6] == round(2.4 * 3 + 2.41 + 2.415, 3), 'bom group: the total is the sum of the real lengths, not count times a mean', lines[0])
ok(all(row[9].startswith('Measured from model') for row in lines), 'bom group: the source column is kept', lines)
ok(g['schedule'] == [['Stud', '2x6', 2.4, 3], ['Stud', '2x6', 2.41, 1], ['Stud', '2x6', 2.415, 1]], 'bom group: the cut schedule keeps each exact length behind a range', g['schedule'])
ok(sum(row[3] for row in g['schedule']) == lines[0][3], 'bom group: the schedule adds up to its line', g['schedule'])
ok(any(row[0] == 'Purchase' and row[3] == BOM['nest'](lengths, 7.2, .003)[0] for row in g['rows'][1:]), 'bom group: nesting uses the exact lengths', g['rows'])
exact = BOM['build'](studs(2.4, 2.4), GROUP)
ok([(row[3], row[5]) for row in cut_lines(exact)] == [(2, 2.4)] and exact['schedule'] == [], 'bom group: identical cuts are one number, with no schedule', exact['rows'])
chain = BOM['build'](studs(*[2.4 + .01 * k for k in range(10)]), GROUP)
chained = cut_lines(chain)
ok(len(chained) == 4 and sum(row[3] for row in chained) == 10, 'bom group: small steps cannot chain into one long line', chained)
zero = BOM['build'](studs(2.4, 2.4, 2.41), dict(GROUP, length_group=0))
ok([(row[3], row[5]) for row in cut_lines(zero)] == [(2, 2.4), (1, 2.41)], 'bom group: 0 groups identical lengths only', cut_lines(zero))
wide = dict(GROUP, rules=[dict(GROUP['rules'][0], length_group=2.0)])
ok([(row[3], row[5]) for row in cut_lines(BOM['build'](studs(1.5, 2.4, 3.2), wide))] == [(3, '1.5 to 3.2')], 'bom group: a rule can set a wider span', wide['rules'])
ok(BOM['length_tolerance']({}, {}, 'mm') == 25.0 and abs(BOM['length_tolerance']({}, {}, 'ft') - 0.08202) < 1e-4 and BOM['length_tolerance']({}, {}, 'Parsecs') == 0.0, 'bom group: the default follows the document units')
two = dict(GROUP, rules=[dict(GROUP['rules'][0], match='Stud', layer='Walls', source='assumed'), dict(GROUP['rules'][0], match='Stud', layer='Roof')])
mixed = BOM['build']([obj('Stud', 'Walls', [.038, .14, 2.4]), obj('Stud', 'Roof', [.038, .14, 2.4])], two)
ok(len(cut_lines(mixed)) == 2 and mixed['sources']['assumed'] == 1, 'bom group: different sources stay on separate lines', cut_lines(mixed))
for value, label in ((-1, 'negative'), ('wide', 'text'), (True, 'boolean')):
    ok(any('length_group' in x for x in BOM['validate'](dict(GROUP, length_group=value))), 'bom group: a %s length_group is refused' % label)
    ok(any('length_group' in x for x in BOM['validate'](dict(GROUP, rules=[dict(GROUP['rules'][0], length_group=value)]))), 'bom group: a %s rule length_group is refused' % label)
v = BOM['varies']({'a': BOM['build'](studs(2.4, 2.41), GROUP), 'b': BOM['build'](studs(2.4, 2.4), GROUP)})
ok(v['different'], 'bom group: a different range between layouts is reported', v)
with tempfile.TemporaryDirectory() as tmp:
    BOM['write_csv'](tmp + '/g.csv', g, GROUP, 'seeded')
    written = list(csv.reader(open(tmp + '/g.csv', encoding='utf-8-sig')))
    at = next(i for i, row in enumerate(written) if row[:1] == ['Cut schedule'])
    ok(written[at + 1] == ['Item', 'Size', 'Cut length', 'Qty'] and written[at + 2:at + 5] == [['Stud', '2x6', '2.4', '3'], ['Stud', '2x6', '2.41', '1'], ['Stud', '2x6', '2.415', '1']], 'bom group: the CSV carries the cut schedule', written[at:])
    ok(['Counted in lines', '7'] in written, 'bom group: the CSV reconciliation is unchanged', written)
    BOM['write_csv'](tmp + '/e.csv', exact, GROUP, 'seeded')
    ok(not any(row[:1] == ['Cut schedule'] for row in csv.reader(open(tmp + '/e.csv', encoding='utf-8-sig'))), 'bom group: no schedule section when no line gives a range')


# BOM through a stub of RhinoCommon, to cover the document reader.
class Layer:
    def __init__(self, path, deleted=False):
        self.FullPath, self.IsDeleted = (None if deleted else path), deleted


class Attr:
    def __init__(self, name, index):
        self.Name, self.LayerIndex = name, index


class P:
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = x, y, z


class Box:
    def __init__(self, d):
        self.Min, self.Max = P(0, 0, 0), P(*d)


class Geo:
    def __init__(self, d, volume=1.0, area=1.0):
        self.d, self.volume, self.area = d, volume, area

    def GetBoundingBox(self, _accurate):
        return Box(self.d)


class Item:
    def __init__(self, name, index, geo):
        self.Attributes, self.Geometry = Attr(name, index), geo


class Settings:
    HiddenObjects = LockedObjects = False


class Objects(list):
    def GetObjectList(self, settings):
        assert settings.HiddenObjects and settings.LockedObjects, 'hidden and locked objects must be read'
        return list(self)


class Doc:
    ModelUnitSystem = 'Meters'


geo_mod = types.ModuleType('Rhino.Geometry')
geo_mod.VolumeMassProperties = types.SimpleNamespace(Compute=lambda g: types.SimpleNamespace(Volume=g.volume))
geo_mod.AreaMassProperties = types.SimpleNamespace(Compute=lambda g: types.SimpleNamespace(Area=g.area))
rhino = types.ModuleType('Rhino')
rhino.Geometry = geo_mod
rhino.DocObjects = types.SimpleNamespace(ObjectEnumeratorSettings=Settings)
sys.modules['Rhino'], sys.modules['Rhino.Geometry'] = rhino, geo_mod

layers = [Layer('B'), Layer('B::A'), Layer('B::A::Walls'), Layer('B::A2'), Layer('', True)]


def doc_with(extra=()):
    d = Doc()
    d.Layers = layers
    d.Objects = Objects([Item('Stud', 2, Geo([.038, .14, 2.4])) for _ in range(2)] + [Item('Bolt', 2, Geo([.01, .01, .3]))] + list(extra))
    return d


with tempfile.TemporaryDirectory() as tmp:
    spec = dict(SPEC, out=tmp + '/bom')
    status, out = run_print(BOM['run'], doc_with(), spec, True)
    ok(status == 0 and 'ASBOM status=pass files=1' in out, 'bom: stub run passes and writes', out)
    ok('BOM: a - 3 objects: 3 counted, 0 excluded, 0 unclassified' in out, 'bom: status line reconciles', out)
    ok('no BOM for: B::A2' in out, 'bom: a layout with no BOM is named', out)
    csv_rows = list(csv.reader(open(tmp + '/bom/bom-a.csv', encoding='utf-8-sig')))
    ok(['Objects in scope', '3'] in csv_rows and ['Fasteners', 'not modeled'] in csv_rows, 'bom: the CSV carries the reconciliation and what is not counted', csv_rows[-12:])
    Path(tmp + '/bom/bom-a.csv').unlink()
    status, out = run_print(BOM['run'], doc_with([Item('Mystery', 2, Geo([1, 1, 1]))]), spec, True)
    ok(status == 1 and 'BOM: FAILED' in out and 'unclassified: 1 x Mystery' in out and 'ASBOM status=fail files=0' in out, 'bom: an unclassified object fails the run', out)
    ok(not Path(tmp + '/bom/bom-a.csv').exists(), 'bom: a failed run writes no CSV')

for mod in ('Rhino', 'Rhino.Geometry'):
    del sys.modules[mod]


# ---- as-rhino-display ----
DISPLAY = load(root / 'rhino-display/scripts/as-display.py')


def png(path, width, height, colour):
    """A PNG from a colour(x, y) function, with the standard library."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(colour(x, y))

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw))) + chunk(b'IEND', b''))


with tempfile.TemporaryDirectory() as tmp:
    shape = lambda x, y: 40 < x < 160 and 40 < y < 80
    grey = tmp + '/grey.png'
    png(grey, 200, 120, lambda x, y: (120, 120, 120) if shape(x, y) else (250, 250, 250))
    colour = tmp + '/colour.png'
    png(colour, 200, 120, lambda x, y: (200, 40, 30) if shape(x, y) else (250, 250, 250))
    blank = tmp + '/blank.png'
    png(blank, 200, 120, lambda x, y: (250, 250, 250))

    ok(DISPLAY['verify_files']([grey], 'Arctic')[0]['failures'] == [], 'display: a grey file passes Arctic')
    result = DISPLAY['verify_files']([colour], 'Arctic')
    ok(any('coloured' in f for f in result[0]['failures']), 'display: a coloured file fails Arctic', result)
    all_ok, out = run_print(DISPLAY['report'], result, 'Arctic')
    ok(not all_ok and 'Export: FAILED' in out and 'ASEXPORT status=fail' in out, 'display: one bad file fails the batch', out)
    mixed, out = run_print(DISPLAY['report'], DISPLAY['verify_files']([grey, colour], 'Arctic'), 'Arctic')
    ok(not mixed and '1 of 2' in out, 'display: a batch with one coloured file fails', out)
    ok(any('blank' in f for f in DISPLAY['verify_files']([blank], 'Arctic')[0]['failures']), 'display: a blank file fails')
    shaded = DISPLAY['verify_files']([colour], 'Shaded')
    ok(shaded[0]['failures'] == [], 'display: colour is not a failure in Shaded', shaded)
    all_ok, out = run_print(DISPLAY['report'], shaded, 'Shaded')
    ok(all_ok and 'Colour was not judged' in out, 'display: the report says colour was not judged for a coloured mode', out)
    all_ok, out = run_print(DISPLAY['report'], [], 'Arctic')
    ok(not all_ok, 'display: an empty batch is not a pass')
    missing = DISPLAY['verify_files']([tmp + '/gone.png'], 'Arctic')
    ok(missing[0]['failures'], 'display: a missing file fails', missing)

    # Every PNG filter type, against a known pixel, since the reader is the standard-library path.
    def filtered(path, width, height, value):
        bpp = 3
        rows = [[value(x, y) for x in range(width)] for y in range(height)]
        raw = bytearray()
        prev = bytearray(width * bpp)
        for y, row in enumerate(rows):
            flat = bytearray(c for px in row for c in px)
            kind = y % 5
            out_row = bytearray(len(flat))
            for i in range(len(flat)):
                a = flat[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pred = {0: 0, 1: a, 2: b, 3: (a + b) // 2, 4: a if abs(p - a) <= abs(p - b) and abs(p - a) <= abs(p - c) else (b if abs(p - b) <= abs(p - c) else c)}[kind]
                out_row[i] = (flat[i] - pred) & 255
            raw.append(kind)
            raw.extend(out_row)
            prev = flat
        def chunk(k, d):
            return struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d) & 0xffffffff)
        Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw))) + chunk(b'IEND', b''))
    p5 = tmp + '/filters.png'
    value = lambda x, y: ((x * 7 + y) % 256, (y * 11) % 256, (x + y * 3) % 256)
    filtered(p5, 30, 20, value)
    w, h, pixel = DISPLAY['read_png'](p5)
    ok((w, h) == (30, 20) and all(pixel(x, y) == value(x, y) for y in range(20) for x in range(30)), 'display: the PNG reader decodes all five filters')

target, camera = DISPLAY['aim']([(0, 0, 0), (10, 0, 0), (0, 6, 0), (10, 6, 3)], DISPLAY['DIRECTIONS']['birdseye'], 0.4, 16 / 9.0)
d = DISPLAY['_unit'](tuple(camera[i] - target[i] for i in range(3)))
ok(all(abs(a - b) < 1e-6 for a, b in zip(d, DISPLAY['_unit'](DISPLAY['DIRECTIONS']['birdseye']))) and camera[2] > target[2], 'display: the camera is on the requested direction', (target, camera))


# ---- as-rhino-thinline ----
PDF = load(root / 'rhino-thinline/scripts/as-pdf-check.py')
THIN_CORE = load(root / 'rhino-thinline/scripts/as-sheet-core.py')
CORE = load(root / 'rhino-axon/scripts/as-axon-core.py', **THIN_CORE)   # as-axon.py loads both into one namespace

# Text height: sheet text sized in mm must be drawn at that size, whatever the document's dimension style scales by.
# The old text() kept the style's scale: Rhino 9's Meters template (1.5) drew 7 mm text at 10.5 mm, Foot-Inch (96) at 672 mm.
thf = THIN_CORE['text_height_failure']
old = [thf('Title', 7.0, 7.0 * s) for s in (1.5, 10.0, 12.0, 96.0, 100.0)]
ok(all(f and f.startswith('text drawn at') for f in old), 'sheet: text drawn at the old style scale (1.5x to 100x) fails', old)
ok(thf('Title', 7.0, 7.0 * 1.0) is None and thf('Note', 2.6, 2.6) is None, 'sheet: text drawn at the asked height passes')
ok(thf('Title', 7.0, 7.6) is None and thf('Title', 7.0, 7.8) is not None and thf('Title', 7.0, 6.2) is not None, 'sheet: the tolerance is 10% either way')
src = (root / 'rhino-thinline/scripts/as-sheet.py').read_text(encoding='utf-8')
ok('attr.SetUserString(TEXT_HEIGHT_KEY' in src and 'text_height_failure(item.Geometry.PlainText' in src and 'entity.DimensionScale = 1.0' in src,
   'sheet: text() records the asked height and resets the style scale, and read_sheet checks it')


def pdf(content, media='0 0 2592 1728', extra=b''):
    body = zlib.compress(content)
    return (b'%PDF-1.5\n1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n'
            b'2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n'
            b'3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [' + media.encode() + b'] /Contents 4 0 R>>\nendobj\n'
            b'4 0 obj\n<</Length ' + str(len(body)).encode() + b' /Filter /FlateDecode>>\nstream\n' + body + b'\nendstream\nendobj\n' + extra + b'trailer\n<</Root 1 0 R>>\n')


BW = b'/DeviceRGB CS 0 0 0 SC /DeviceRGB cs 1 1 1 sc q 0.24 w 10 10 m 100 100 l S Q'
SIZE = (914.4, 609.6)
m, f = PDF['check'](pdf(BW), SIZE)
ok(not f and m['pages'] == 1 and m['colour_ops'] == 2, 'pdf: black and white after DeviceRGB CS passes', (m, f))
ok(0.08 < m['line_widths_mm'][0] < 0.09, 'pdf: line width is reported in mm', m)
m, f = PDF['check'](pdf(b'q 0.24 w 10 10 m 100 100 l S Q'), SIZE)
ok(any('no colour operators' in x for x in f), 'pdf: no colour operators is a failure, not a pass', f)
m, f = PDF['check'](pdf(b''), SIZE)
ok(f, 'pdf: an empty page is a failure', f)
m, f = PDF['check'](b'not a pdf', SIZE)
ok(f, 'pdf: garbage is a failure', f)
m, f = PDF['check'](pdf(b'/DeviceRGB CS 1 0 0 SC q 0.24 w 10 10 m 100 100 l S Q'), SIZE)
ok(any('not black or white' in x for x in f), 'pdf: red SC fails', f)
m, f = PDF['check'](pdf(b'1 0 0 rg q 0.24 w 10 10 m 100 100 l S Q'), SIZE)
ok(any('not black or white' in x for x in f), 'pdf: red rg fails', f)
m, f = PDF['check'](pdf(b'0.5 g 0.24 w 10 10 m 100 100 l S'), SIZE)
ok(any('not black or white' in x for x in f), 'pdf: mid-grey fails', f)
# A deflated stream whose last byte is a CR: the stream pattern drops it before the writer's LF, and it must still be read.
for n in range(256):
    body = BW + b' %' + b'x' * (n % 16) + b'y' * (n // 16)   # a comment; its byte sum sets the checksum's last byte
    if zlib.compress(body)[-1:] == b'\r':
        break
m, f = PDF['check'](pdf(body), SIZE)
ok(zlib.compress(body)[-1:] == b'\r' and not f and m['colour_ops'] == 2, 'pdf: a deflated stream ending in a CR is still read', (m, f))
m, f = PDF['check'](pdf(b'/DeviceRGB CS 1 7 7 SC 3 g q 0.24 w 10 10 m 100 100 l S Q'), SIZE)
ok(any('outside 0 to 1' in x for x in f), 'pdf: colour values outside 0 to 1 fail instead of counting as white', f)
m, f = PDF['check'](pdf(b'0 0 0 1 k 0.24 w 10 10 m 100 100 l S'), SIZE)
ok(not f, 'pdf: CMYK black passes', f)
m, f = PDF['check'](pdf(BW, media='0 0 612 792'), SIZE)
ok(any('expected' in x for x in f), 'pdf: wrong page size fails', f)
m, f = PDF['check'](pdf(BW, extra=b'9 0 obj\n<</Subtype /Image>>\nstream\nx\nendstream\nendobj\n'), SIZE)
ok(any('raster' in x for x in f), 'pdf: an embedded image fails', f)
m, f = PDF['check'](pdf(b'/DeviceRGB CS 0 0 0 SC 0.24 w 0.5 0 0 0.5 0 0 cm 10 10 m 100 100 l S'), SIZE)
ok(abs(m['line_widths_mm'][0] - 0.24 * .5 * 25.4 / 72) < .002, 'pdf: the line width follows the transform', m)
# A real writer, when one is installed.
try:
    import pymupdf
except ImportError:
    pymupdf = None
if pymupdf:
    doc = pymupdf.open()
    page = doc.new_page(width=2592, height=1728)
    page.draw_line((10, 10), (500, 500), color=(0, 0, 0), width=0.24)
    raw = doc.tobytes()
    m, f = PDF['check'](raw, SIZE)
    ok(not [x for x in f if 'no colour' in x or 'pages' in x or 'expected' in x], 'pdf: a file from PyMuPDF is read', (m, f))
    doc = pymupdf.open()
    page = doc.new_page(width=2592, height=1728)
    page.draw_line((10, 10), (500, 500), color=(1, 0, 0), width=0.24)
    m, f = PDF['check'](doc.tobytes(), SIZE)
    ok(any('not black or white' in x for x in f), 'pdf: colour in a file from PyMuPDF fails', (m, f))

fx, fy = CORE['solve_affine']([(0, 0), (1, 0), (0, 1)], [(5, 7), (6, 7), (5, 9)])
ok(fx == (1.0, 0.0, 5.0) and fy == (0.0, 2.0, 7.0), 'sheet: the affine map solves', (fx, fy))
try:
    CORE['solve_affine']([(0, 0), (1, 1), (2, 2)], [(0, 0), (1, 1), (2, 2)])
    ok(False, 'sheet: collinear reference points are refused')
except ValueError:
    ok(True, 'sheet: collinear reference points are refused')
routes = [CORE['locator_route']((0, 0), 10, t, 1.0) for t in ((50, 3), (3, 50), (50, 40), (-50, -40))] + [CORE['locator_route']((0, 0), 10, (30, 40), 1.0, 'vh')]
ok(all(not CORE['axis_aligned'](r) for r in routes), 'sheet: every locator route is orthogonal', routes)
ok(CORE['axis_aligned']([((0, 0), (5, 5))]), 'sheet: a diagonal leader is detected')
ok(CORE['stroke_class']('Boundary') == 'outline' and CORE['stroke_class']('Crease', .1, .6) == 'edge' and CORE['stroke_class']('NonSilhouetteCrease', .9, .6) == 'receding', 'sheet: three stroke classes')
ok(CORE['stroke_class']('NonSilhouetteSeam') is None, 'sheet: other curves are dropped')
ok(CORE['shared_x']([1.0, 1.05, 5.0], .2) == [(1.0, 1.05)], 'sheet: anchors with one x are flagged')
shift, margins = CORE['composite_shift']((0, 0, 10, 6), (10, 10, 30, 30))
ok(shift == (15.0, 17.0) and margins['left'] == margins['right'], 'sheet: the composite centres in the field', (shift, margins))
ok(CORE['colour_language'](['Connectors shown in red', 'Double top plate']) == ['Connectors shown in red'], 'sheet: colour language is found')
ok(CORE['outside']((0, 0, 11, 5), (0, 0, 10, 10)) and not CORE['outside']((1, 1, 9, 9), (0, 0, 10, 10)), 'sheet: text outside its frame is found')
rows = [['Cat', 'Item', 'Size'], ['Lumber', 'Stud', '2x6'], ['Lumber', 'Twice', 'a'], ['Lumber', 'Twice', 'b']]
ok(CORE['table_lookup'](rows, 'Lumber', 'Stud')[2] == '2x6', 'sheet: a table row is found')
for category, item in (('Lumber', 'Gone'), ('Lumber', 'Twice')):
    try:
        CORE['table_lookup'](rows, category, item)
        ok(False, 'sheet: a lookup not matching exactly one row fails', item)
    except ValueError:
        ok(True, 'sheet: a lookup not matching exactly one row fails')
one = CORE['hatch_concrete'](0, 0, .3, .3)
ok(one == CORE['hatch_concrete'](0, 0, .3, .3) and one != CORE['hatch_concrete'](0, 0, .3, .3, seed=2), 'sheet: concrete is reproducible from its seed')
ok(all(.0 <= p[0] <= .31 and .0 <= p[1] <= .31 for s in one for p in s), 'sheet: concrete stays in its face')
ok(not CORE['hatch_concrete'](0, 0, .3, .3, holes=[(.1, .1, .2, .2)]) == one, 'sheet: concrete leaves room for a member')
clipped = CORE['clip_out'](CORE['hatch_x'](0, 0, 10, 10), [(4, 4, 6, 6)])
ok(len(clipped) == 4 and all(not (4 < s[1][0] < 6 and 4 < s[1][1] < 6) or abs(s[1][0] - 4) < 1e-6 or abs(s[1][0] - 6) < 1e-6 for s in clipped), 'sheet: hatch is clipped around a member', clipped)
ok(CORE['label_rows']([10, 9.5, 2, 1], 2, 12, 0)[-1] >= 0, 'sheet: label rows stay in the column')
big = CORE['hatch_concrete'](0, 0, 12, 12, unit=39.37)
dots = [s for s in big if abs(s[1][0] - s[0][0] - 0.0016 * 39.37) < 1e-9]
ok(len(dots) > 20 and len(big) == len(CORE['hatch_concrete'](0, 0, .3048, .3048)), 'sheet: concrete scales to an inch model', len(dots))
ok(all(.012 * 39.37 - 1e-9 <= p[0] for s in dots for p in s), 'sheet: the concrete edge scales with the unit')

# Team models: several owner layers, some left out, and what is projected.
ok(CORE['layer_selected']('Shell::Walls', ['Shell', 'Plumbing']) and CORE['layer_selected']('Plumbing', ['Shell', 'Plumbing']), 'sheet: a layer under any of several roots is selected')
ok(CORE['layer_selected']('Shell', 'Shell') and not CORE['layer_selected']('Shellfish', 'Shell'), 'sheet: one root still works, and a prefix is not a root')
ok(CORE['layer_selected']('Structure::Sheathing', ['*::Sheathing']) and not CORE['layer_selected']('Structure::Studs', ['*::Sheathing']), 'sheet: an exclude glob matches by leaf')
ok(not CORE['layer_selected']('Shell', []), 'sheet: no exclusions select nothing')
ok('TextDot' not in CORE['PROJECTED'] and 'Point' not in CORE['PROJECTED'] and 'Brep' in CORE['PROJECTED'], 'sheet: notes and points are not projected')

# Locator leaders across the main drawing, scale read-back and margins.
ok(CORE['segment_hit']((0, 0), (10, 0), (5, -1), (5, 1)) == (5.0, 0.0), 'sheet: crossing segments meet')
ok(CORE['segment_hit']((0, 0), (10, 0), (5, 1), (5, 3)) is None, 'sheet: separate segments do not meet')
ok(CORE['segment_hit']((0, 0), (10, 0), (4, 0), (20, 0)) == (4.0, 0.0), 'sheet: a leader along a drawn line is found')
ok(CORE['segment_hit']((0, 0), (10, 0), (11, 0), (20, 0)) is None, 'sheet: collinear but apart is clear')
edge = [(50, -100), (50, 100)]
lead = [((0, 0), (100, 0))]
ok(len(CORE['leader_crossings'](lead, [edge], [(100, 0, 5)])) == 1, 'sheet: a leader across the drawing is found')
ok(CORE['leader_crossings'](lead, [[(98, -5), (98, 5)]], [(100, 0, 5)]) == [], 'sheet: lines at the leader\'s own joint are allowed')
ok(CORE['leader_crossings'](lead, [[(0, 50), (100, 50)]], [(100, 0, 5)]) == [], 'sheet: a leader clear of the drawing passes')
# Labels: a straight leader from clear paper beside the drawing to the part, crossing nothing.
box_draw = [[(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)], [(50, 0), (50, 100)], [(0, 50), (100, 50)]]
got = CORE['pick_label']([(100, 80)], (0, 0, 100, 100), 8, box_draw, 1.5)
ok(got is not None and got[1] == 'right' and got[2] == (108, 80), 'sheet: a part on the outline is labelled in the clear paper beside it', got)
dense = box_draw + [[(0, y), (100, y)] for y in range(2, 100, 3)] + [[(x, 0), (x, 100)] for x in range(2, 100, 3)]
ok(CORE['pick_label']([(25, 25)], (0, 0, 100, 100), 8, dense, 1.5, (12, 3)) is None, 'sheet: a part inside dense linework gets no label leader across it')
inside = CORE['pick_label']([(25, 25)], (0, 0, 100, 100), 8, box_draw, 1.5, (12, 3))
ok(inside is not None and abs(inside[2][0] - 25) + abs(inside[2][1] - 25) <= 14, 'sheet: a part beside clear space inside the drawing is labelled there, close by', inside)
crowd = box_draw + [[(104, 95), (140, 95), (140, 105), (104, 105), (104, 95)]]         # a text box already beside the corner on the right
got = CORE['pick_label']([(100, 100)], (0, 0, 100, 100), 8, crowd, 1.5)
ok(got is not None and got[1] != 'right', 'sheet: a label goes round another label already there', got)
ok(not CORE['scale_mismatch'](1 / 40.0, 0.025) and CORE['scale_mismatch'](1 / 50.0, 0.025), 'sheet: the scale read back is compared')
# Detail outlines, overlapping pieces, hatch by material, tags.
ok(abs(CORE['point_segment_distance']((5, 3), (0, 0), (10, 0)) - 3) < 1e-9 and abs(CORE['point_segment_distance']((13, 4), (0, 0), (10, 0)) - 5) < 1e-9, 'sheet: point to segment distance')
square = [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]]
ok(CORE['near_polyline']((5, 0.001), square, 0.01) and not CORE['near_polyline']((5, 5), square, 0.01), 'sheet: an edge on its piece outline is found, an inner edge is not')
ok(CORE['through_circle']([(0, 0), (20, 0)], (10, 1), 3) and not CORE['through_circle']([(0, 0), (20, 0)], (10, 5), 3), 'sheet: a line through a tag is found, one clear of it is not')
ok(not CORE['through_circle']([(0, 3), (20, 3)], (10, 0), 3), 'sheet: a line that only grazes a tag is clear')
pipes = [(0, 0, 0, 10, 1, 1), (9, 0, 0, 10, 10, 1), (20, 0, 0, 30, 1, 1)]
ok(CORE['overlap_groups'](pipes, ['Drain'] * 3, 0.01) == [[0, 1]], 'sheet: pipe runs that overlap at an elbow are grouped', CORE['overlap_groups'](pipes, ['Drain'] * 3, 0.01))
ok(CORE['overlap_groups'](pipes, ['Drain', 'Gas', 'Drain'], 0.01) == [], 'sheet: overlapping pieces of different members stay apart')
studs = [(0, 0, 0, 1.5, 3.5, 90), (1.5, 0, 0, 3, 3.5, 90)]
ok(CORE['overlap_groups'](studs, ['Studs'] * 2, 0.01) == [], 'sheet: members that only touch keep their seam')
ok(CORE['overlap_groups']([(0, 0, 0, 10, 1, 1), (10, 0, 0, 20, 1, 1)], ['Drain'] * 2, 0.01, ['Drain']) == [[0, 1]], 'sheet: service runs that only touch end to end are joined when asked')
ok(CORE['overlap_groups']([(0, 0, 0, 10, 1, 1), (10, 0, 0, 20, 1, 1)], ['Studs'] * 2, 0.01, ['Drain']) == [], 'sheet: framing that only touches is not joined')
ok(CORE['fit_scale_denominator'](800, 164, 0.8) == 8 and CORE['fit_scale_denominator'](100, 164, 0.8) == 1, 'sheet: a detail scale fits its content to the ring', CORE['fit_scale_denominator'](800, 164, 0.8))
ok(CORE['fit_scale_denominator'](10 ** 9, 1) == CORE['STANDARD_SCALES'][-1], 'sheet: an oversize detail takes the smallest scale')
ok(CORE['collinear_runs'](((0, 0), (100, 0)), [[(20, 0.1), (60, 0.1)]], 0.3, 3) == [(40.0, 0.0)], 'sheet: a leader along a drawn edge is found')
ok(CORE['collinear_runs'](((0, 0), (100, 0)), [[(20, 5), (60, 5)], [(30, -9), (30, 9)]], 0.3, 3) == [], 'sheet: parallel lines apart and crossing lines are not runs')
ok(CORE['collinear_runs'](((0, 0), (100, 0)), [[(90, 0), (100, 0)]], 0.3, 3, [(100, 0, 5)]) == [], 'sheet: running along the joint itself is allowed')
ok(CORE['circle_near_box']((0, 0), 10, (9.5, -1, 20, 1), 0.5) and not CORE['circle_near_box']((0, 0), 10, (12, -1, 20, 1), 0.5), 'sheet: a label touching a ring is found, one clear of it is not')
ok(not CORE['circle_near_box']((0, 0), 10, (-2, -1, 2, 1), 0.5), 'sheet: a label well inside a ring does not touch it')
ok(CORE['lines_through_box']([[(0, 5), (20, 5)]], (8, 4, 12, 6)) and not CORE['lines_through_box']([[(0, 9), (20, 9)]], (8, 4, 12, 6)), 'sheet: a line through a label is found')
ok(CORE['main_stroke']('Boundary', True) == 'outline' and CORE['main_stroke']('Boundary', False, 0.1) == 'edge' and CORE['main_stroke']('Crease', False, 0.9) == 'receding', 'sheet: only the assembly outline is heavy in the main view')
ok(CORE['main_stroke']('NonSilhouetteSeam', True) is None, 'sheet: other curves are still dropped')
frame = [[(0, 0), (100, 0), (100, 50), (0, 50), (0, 0)], [(10, 10), (20, 10), (20, 40), (10, 40), (10, 10)], [(200, 0), (210, 0), (210, 5), (200, 0)]]
ok(CORE['outer_loops'](frame) == [frame[0], frame[2]], 'sheet: the holes of a see-through frame are not its outline')
sq = [(0, 0), (10, 0), (10, 10), (0, 10)]
ok(CORE['point_in_polygon']((5, 5), sq) and not CORE['point_in_polygon']((15, 5), sq), 'sheet: point in polygon')
regions = [((0, 0, 10, 10), sq), ((10, 0, 20, 10), [(10, 0), (20, 0), (20, 10), (10, 10)])]
ok(CORE['against_paper']((5, 10), (1, 0), 0.1, regions), 'sheet: an edge with paper on one side is the assembly outline')
ok(not CORE['against_paper']((10, 5), (0, 1), 0.1, regions), 'sheet: an edge between two members is not')
ok(CORE['segment_distance']((0, 0), (10, 0), (0, 3), (10, 3)) == 3 and CORE['segment_distance']((0, 0), (10, 0), (5, -1), (5, 1)) == 0, 'sheet: segment to segment distance')
ok(abs(CORE['shape_distance'](('circle', 0, 0, 5), ('circle', 20, 0, 5)) - 10) < 1e-9 and abs(CORE['shape_distance'](('circle', 0, 0, 5), ('poly', [(8, -1), (8, 1)])) - 3) < 1e-9, 'sheet: distances between rings and lines')
els = [('ring D1', 'D1', ('circle', 100, 100, 20)), ('leader D1', 'D1', ('poly', [(80, 100), (10, 100)])), ("text 'D2 eave'", 'D2', ('poly', [(118, 60), (160, 60), (160, 66), (118, 66), (118, 60)])), ('ring D2', 'D2', ('circle', 150, 30, 20))]
summary = CORE['layout_summary'](els, (0, 0, 300, 200), 1.0, 3, 0.25, {'D1': 0.1, 'D2': 0.5})
ok("18.5  ring D1  <->  text 'D2 eave'" in summary, 'sheet: the preview summary names the closest pair with its distance', summary)
ok('ring D1  <->  leader D1' not in summary and 'leader D1  <->  ring D1' not in summary, 'sheet: a ring and its own leader are not a pair', summary)
ok('10.0  leader D1 (left)' in summary and 'D1  10%' in summary and 'D2  50%' not in summary, 'sheet: the summary names the edge distances and the empty detail', summary)
ok(CORE['MIN_MARGIN_MM'] == 10.0, 'sheet: the margin limit is fixed')
twice = CORE['layout_summary'](els + [('leader D1', 'D1', ('poly', [(10, 100), (10, 150)]))], (0, 0, 300, 200), 1.0)
ok(twice.count('leader D1 (left)') == 1 and twice.count("leader D1  <->  text 'D2 eave'") + twice.count("text 'D2 eave'  <->  leader D1") == 1, 'sheet: a leader of several segments is listed once', twice)
ok([CORE['material_for'](x) for x in ('Wall::Gypsum board', 'Wall::Studs stud 2x6', 'Window::Glazing IGU pane', 'Wall::Sheathing panel', 'Window::Glazing Stops stop', 'Flashing::Head flashing', 'Mystery')] == ['gypsum', 'timber', 'none', 'plywood', 'timber', 'none', 'none'], 'sheet: the hatch material follows the layer and name; gypsum is not wood')
ok(len(CORE['hatch_pattern']('gypsum', True, 0, 0, 1, 1, 1.0)) > 0 and CORE['hatch_pattern']('gypsum', True, 0, 0, 1, 1, 1.0) != CORE['hatch_x'](0, 0, 1, 1), 'sheet: gypsum gets its own stipple, not the timber X')
sloped = [(0, 0), (10, 0), (10, 2), (0, 6)]          # a sloped sill's cut face
spill = CORE['clip_to_polygon']([((0, 0), (10, 6)), ((0, 5), (10, 5))], sloped)
ok(spill and all(CORE['point_in_polygon'](((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), sloped) for a, b in spill), 'sheet: hatch is clipped to a sloped cut face', spill)
ok(abs(max(b[0] for a, b in spill if abs(a[1] - 5) < 1e-9) - 2.5) < 1e-9, 'sheet: a line across the slope stops at the sloped edge', spill)
ok(CORE['building_changes']({'a': '1', 'b': '2', 'c': '3'}, {'a': '1', 'b': '9', 'd': '4'}) == (['c'], ['b']), 'sheet: removed and changed building objects are found; added ones are not')
ok(CORE['dedupe_curves']([(0, 0, 1, 1, 1.41), (1, 1, 0, 0, 1.41), (0, 0, 1, 1, 2.0), (5, 5, 6, 6, 1.41)], 0.01) == [0, 2, 3], 'sheet: a curve repeating another, either way round, is dropped')
ok(CORE['true_cut'](0, 10, 5, 0.01) and not CORE['true_cut'](0, 10, 10, 0.01) and not CORE['true_cut'](0, 10, 0, 0.01), 'sheet: a face on the plane is a cut only when the member continues past it')
ok(len(CORE['hatch_pattern']('timber', True, 0, 0, 4, 4)) == 2, 'sheet: timber cut across the grain gets the X')
ok(CORE['hatch_pattern']('timber', False, 0, 0, 4, 40) == CORE['hatch_grain'](0, 0, 4, 40), 'sheet: timber cut along the grain gets grain lines')
ok(CORE['hatch_pattern']('none', True, 0, 0, 4, 4) == [] and CORE['hatch_pattern']('glass', True, 0, 0, 4, 4) == [], 'sheet: no hatch for none or an unknown material')
ok(CORE['hatch_pattern']('concrete', True, 0, 0, 12, 12, 39.37) == CORE['hatch_concrete'](0, 0, 12, 12, unit=39.37), 'sheet: concrete hatch follows the model unit')

# Picking a joint a locator reaches cleanly: ring on the right, a box drawing on the left.
box_lines = [[(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)], [(50, 0), (50, 100)], [(0, 50), (100, 50)]]
outline = (0, 0, 100, 100)
routes = CORE['locator_routes']((300, 50), 30, (100, 80), 5, outline, 6)
ok(len(routes) == 5 and all(not CORE['axis_aligned'](r) for r in routes), 'sheet: every candidate route is orthogonal', routes)
picked = CORE['pick_locator']([(25, 25), (100, 80)], (300, 50), 30, 5, box_lines, outline, 6)
ok(picked is not None and picked[0] == 1, 'sheet: the joint on the edge facing the details is picked', picked)
ok(picked is not None and not CORE['leader_crossings'](picked[1], box_lines, [(100, 80, 5)]), 'sheet: the picked leader is clean', picked)
wide = box_lines + [[(100, 0), (120, 0), (120, 100), (100, 100)]]
top = CORE['pick_locator']([(50, 100)], (300, 50), 30, 5, wide, (0, 0, 120, 100), 6)
ok(top is not None and len(top[1]) == 3, 'sheet: a leader jogs around the outline to reach the top edge', top)
ok(CORE['pick_locator']([(25, 25)], (300, 50), 30, 5, box_lines, outline, 6) is None, 'sheet: an interior joint with no clean leader is refused')
tall = CORE['locator_routes']((300, 95), 30, (50, 100), 5, (0, 0, 100, 100), 6)
ok(all(CORE['point_segment_distance']((300, 95), a, b) >= 0.98 * 30 - 1e-9 for r in tall[2:] for a, b in r), 'sheet: a jog route never starts back through its own ring', tall)
behind = CORE['pick_locator']([(100, 80)], (60, 50), 30, 5, [], (0, 0, 100, 100), 6)
ok(behind is None or all(CORE['point_segment_distance']((60, 50), a, b) >= 0.98 * 30 for a, b in behind[1]), 'sheet: a picked leader never runs through its own detail', behind)
ok(CORE['margins']((20, 15, 80, 90), (10, 10, 100, 100)) == {'left': 10, 'right': 20, 'bottom': 5, 'top': 10}, 'sheet: margins are measured per side')
ok(CORE['margins']((5, 15, 80, 90), (10, 10, 100, 100))['left'] < 0, 'sheet: a spill out of the field is negative')

# A locator leader across a caption.
ok(CORE['segment_hits_box']((0, 5), (20, 5), (8, 4, 12, 6)), 'sheet: a leader through a box is found')
ok(not CORE['segment_hits_box']((0, 7), (20, 7), (8, 4, 12, 6)), 'sheet: a leader above a box is clear')
ok(not CORE['segment_hits_box']((0, 5), (7, 5), (8, 4, 12, 6)), 'sheet: a leader that stops short of a box is clear')
ok(CORE['segment_hits_box']((10, 0), (10, 20), (8, 4, 12, 6)), 'sheet: a vertical leader through a box is found')
leaders = [((0, 5), (20, 5)), ((0, 30), (20, 30))]
ok(CORE['leaders_through_text'](leaders, [('Caption', (8, 4, 12, 6)), ('Far', (50, 50, 60, 60))]) == [(leaders[0], 'Caption')], 'sheet: the leader and the caption are named', leaders)

# The ring stops under a tag.
full = 2 * math.pi
ok(CORE['ring_arcs']((0, 0), 10, None) == [(0.0, full)], 'sheet: with no tags the ring is whole')
ok(CORE['ring_arcs']((0, 0), 10, [((50, 0), 2)]) == [(0.0, full)], 'sheet: a tag away from the ring leaves it whole')
ok(CORE['ring_arcs']((0, 0), 10, [((0, 0), 2)]) == [(0.0, full)], 'sheet: a tag at the centre leaves the ring whole')
arcs = CORE['ring_arcs']((0, 0), 10, [((0, 10), 2)])
half = math.acos((100 + 100 - 4) / 200.0)
ok(len(arcs) == 1 and abs(arcs[0][1] - arcs[0][0] - (full - 2 * half)) < 1e-9, 'sheet: one tag leaves one arc, short by the gap', arcs)
middle = (arcs[0][0] + arcs[0][1]) / 2
ok(abs((middle % full) - 3 * math.pi / 2) < 1e-9, 'sheet: the arc is opposite the tag', arcs)
def point_at(angle):
    return 10 * math.cos(angle), 10 * math.sin(angle)
x, y = point_at(arcs[0][0])
ok(abs(math.hypot(x, y - 10) - 2) < 1e-9, 'sheet: the arc ends where the ring meets the tag', (x, y))
ok(len(CORE['ring_arcs']((5, 5), 10, [((15, 5), 2), ((5, 15), 2)])) == 2, 'sheet: two tags leave two arcs')
near = CORE['ring_arcs']((0, 0), 10, [((10, 0), 2), ((9.9, 1.4), 2)])
ok(len(near) == 1, 'sheet: overlapping tags make one gap', near)
wrap = CORE['ring_arcs']((0, 0), 10, [((10, -.5), 2), ((10, .5), 2)])
ok(len(wrap) == 1 and wrap[0][1] - wrap[0][0] < full, 'sheet: a gap across angle zero is one gap', wrap)
total = sum(e - s for s, e in CORE['ring_arcs']((0, 0), 10, [((10, 0), 2), ((-10, 0), 2)]))
ok(abs(total - (full - 4 * math.acos(196 / 200.0))) < 1e-9, 'sheet: the arcs add up to the ring less the gaps', total)

# new_page, through a stub: the guard against a document that is not the active one.
class PageDoc:
    PageUnitSystem = 'Millimeters'

    def __init__(self, serial, pages=()):
        self.RuntimeSerialNumber, self.added = serial, []
        pages = list(pages)
        doc = self

        class Views:
            ActiveView = None

            def GetPageViews(self):
                return pages

            def AddPageView(self, name, w, h):
                doc.added.append((name, w, h))
                return types.SimpleNamespace(PageName=name)

        self.Views = Views()


active = PageDoc(1)
fake = types.ModuleType('Rhino')
fake.RhinoDoc = types.SimpleNamespace(ActiveDoc=active)
fake.RhinoMath = types.SimpleNamespace(UnitScale=lambda a, b: 1.0)
fake.UnitSystem = types.SimpleNamespace(Millimeters='Millimeters')
fake_geo = types.ModuleType('Rhino.Geometry')
fake_geo.HiddenLineDrawing = fake_geo.HiddenLineDrawingParameters = object
fake.Geometry = fake_geo
system = types.ModuleType('System')
drawing = types.ModuleType('System.Drawing')
system.Drawing = drawing
stubbed = {'Rhino': fake, 'Rhino.Geometry': fake_geo, 'System': system, 'System.Drawing': drawing}
sys.modules.update(stubbed)
SHEET = load(root / 'rhino-axon/scripts/as-axon.py')   # loads rhino-thinline's as-sheet.py first
page = SHEET['new_page'](active, 'Sheet 1', 914.4, 609.6)
ok(active.added == [('Sheet 1', 914.4, 609.6)] and active.Views.ActiveView is page, 'sheet: a page is created at the size asked for', active.added)
other = PageDoc(2)
try:
    SHEET['new_page'](other, 'Sheet 1', 914.4, 609.6)
    ok(False, 'sheet: a window document that is not active is refused')
except ValueError as exc:
    ok('active' in str(exc) and not other.added, 'sheet: a window document that is not active is refused', other.added)
headless = PageDoc(3)
headless.IsHeadless = True
page, said = run_print(SHEET['new_page'], headless, 'Sheet 1', 914.4, 609.6)
ok(headless.added == [('Sheet 1', 914.4, 609.6)] and 'WARNING' not in said, 'sheet: a headless document gets a page without being active', (headless.added, said))


class Strings:
    def __init__(self):
        self.items = []
    Count = property(lambda self: len(self.items))
    def GetKey(self, i):
        return self.items[i][0]
    def GetValue(self, i):
        return self.items[i][1]
    def SetString(self, key, value):
        self.Delete(key)
        self.items.append((key, value))
    def Delete(self, key):
        self.items = [kv for kv in self.items if kv[0] != key]


active.Strings = Strings()
leaky = PageDoc(4)
leaky.IsHeadless = True
add = leaky.Views.AddPageView
leaky.Views.AddPageView = lambda *a: (active.Strings.items.append(('k', 'v')), add(*a))[1]
page, said = run_print(SHEET['new_page'], leaky, 'Sheet 1', 914.4, 609.6)
ok('WARNING' in said, 'sheet: a page that changes the active document is reported', said)
taken = PageDoc(1, [types.SimpleNamespace(PageName='Sheet 1')])
fake.RhinoDoc.ActiveDoc = taken
try:
    SHEET['new_page'](taken, 'Sheet 1', 914.4, 609.6)
    ok(False, 'sheet: an existing layout name is refused')
except ValueError as exc:
    ok('already exists' in str(exc) and not taken.added, 'sheet: an existing layout name is refused')


# The sheet functions the first test pass corrected, through small stubs.
class PatternTable:
    def __init__(self, solid=None, add=7):
        self.solid, self.add, self.added = solid, add, []

    def FindName(self, name):
        return self.solid

    def Add(self, pattern):
        self.added.append(pattern)
        return self.add


fake.DocObjects = types.SimpleNamespace(HatchPattern=types.SimpleNamespace(Defaults=types.SimpleNamespace(Solid='solid pattern')))
empty = types.SimpleNamespace(HatchPatterns=PatternTable())
ok(SHEET['solid_pattern_index'](empty) == 7 and empty.HatchPatterns.added == ['solid pattern'], 'sheet: the Solid pattern is added when the document has none')
has = types.SimpleNamespace(HatchPatterns=PatternTable(types.SimpleNamespace(Index=2)))
ok(SHEET['solid_pattern_index'](has) == 2 and not has.HatchPatterns.added, 'sheet: an existing Solid pattern is reused')
try:
    SHEET['solid_pattern_index'](types.SimpleNamespace(HatchPatterns=PatternTable(add=-1)))
    ok(False, 'sheet: a refused Solid pattern raises')
except ValueError:
    ok(True, 'sheet: a refused Solid pattern raises')


class PerLayer:
    def __init__(self, path, deleted=False):
        self.FullPath, self.IsDeleted, self.hidden, self.commits = path, deleted, [], 0

    def SetPerViewportVisible(self, viewport, visible):
        self.hidden.append((viewport, visible))

    def CommitChanges(self):
        self.commits += 1


sheet_layers = [PerLayer('Model'), PerLayer('Model::Staged'), PerLayer('Model::Assembled'), PerLayer('', True)]
SHEET['hide_in_detail'](types.SimpleNamespace(Layers=sheet_layers), types.SimpleNamespace(Viewport=types.SimpleNamespace(Id='vp')))
ok(all(l.hidden == [('vp', False)] and l.commits == 1 for l in sheet_layers[:3]), 'sheet: every model layer is hidden in the detail, not only the source', [l.hidden for l in sheet_layers])
ok(sheet_layers[3].hidden == [], 'sheet: a deleted layer is left alone')

trimmed = types.SimpleNamespace(GetBoundingBox=lambda accurate: 'trimmed box')
face = types.SimpleNamespace(GetBoundingBox=lambda accurate: 'untrimmed box', DuplicateFace=lambda meshes: None if meshes else trimmed)
ok(SHEET['face_box'](face) == 'trimmed box', 'sheet: a cut face is measured through its trimmed copy')


class CutBrep:
    IsSolid = True

    def __init__(self, encloses=False):
        self.encloses = encloses

    def IsPointInside(self, point, tolerance, strict):
        return self.encloses

    def DuplicateBrep(self):
        return self


class WindowBox:
    def __init__(self, a, b):
        self.Min, self.Max, self.Center = types.SimpleNamespace(X=a[0], Y=a[1], Z=a[2]), types.SimpleNamespace(X=b[0], Y=b[1], Z=b[2]), 'centre'

    def Contains(self, point):
        return False


contact = {}
fake_geo.BoundingBox = WindowBox
fake_geo.Brep = types.SimpleNamespace(CreateFromBox=lambda box: 'cutter', CreateBooleanIntersection=lambda a, b, tol: [])
fake_geo.Transform = types.SimpleNamespace(Translation=lambda offset: 'move')
fake.Geometry.Intersect = types.SimpleNamespace(Intersection=types.SimpleNamespace(BrepBrep=lambda a, b, tol: contact['result']))
SHEET['layer_index'] = lambda doc, path, weight=None: 0
SHEET['Rhino'] = fake
bounds = WindowBox((0, 0, 0), (1, 1, 1))
unit_doc = types.SimpleNamespace(ModelUnitSystem='Meters')
fake.UnitSystem.Meters = 'Meters'
source = [('Joist 1', CutBrep(), bounds)]
window = ((0, 0, 0), (1, 1, 1))

def cut(result, member=None):
    contact['result'] = result
    return run_print(SHEET['cut_pieces'], unit_doc, member or source, window, (0, 0, 0), 'Cut')[1]

ok('cut failed' not in cut((True, [], [])), 'sheet: a member that never meets the window is not a failed cut')
ok('cut failed' not in cut((True, None, None)), 'sheet: no intersection results at all is not a failed cut')
ok('cut failed: Joist 1' in cut((True, ['curve'], [])), 'sheet: a member that meets the window and gives no piece is a failed cut')
ok('cut failed: Joist 1' in cut((True, [], ['point'])), 'sheet: a point of contact with no piece is a failed cut')
ok('cut failed: Joist 1' in cut((False, None, None)), 'sheet: an intersection that cannot be computed still reports the failure')
ok('cut failed: Joist 1' in cut((True, [], []), [('Joist 1', CutBrep(encloses=True), bounds)]), 'sheet: a member that encloses the window and gives no piece is a failed cut')


class Pt:
    def __init__(self, x, y):
        self.X, self.Y = x, y


class Text:
    def __init__(self, body, box, height=1.0, scale=1.0):
        self.PlainText, self.box = body, box
        self.TextHeight, self.DimensionScale = height, scale

    def GetBoundingBox(self, accurate):
        return types.SimpleNamespace(Min=Pt(*self.box[:2]), Max=Pt(*self.box[2:]))


fake_geo.TextEntity = Text
fake_geo.Curve = type('NoCurve', (), {})  # replaced by the Polyline stub below
sheet_view = types.SimpleNamespace(PageName='A-1', MainViewport=types.SimpleNamespace(Id='main'))

def page_item(name, geometry, user=None):
    user = dict(user or {})
    return types.SimpleNamespace(Attributes=types.SimpleNamespace(Name=name, ViewportId='main', GetUserString=user.get), Geometry=geometry)

def leader(a, b):
    return types.SimpleNamespace(PointAtStart=Pt(*a), PointAtEnd=Pt(*b))

def started(building=None):
    """Document strings as setup_sheet leaves them: the building record, when given, and the request ledger."""
    holder = types.SimpleNamespace(Strings=Strings())
    extra = {}
    if building is not None:
        holder.Strings.SetString(SHEET['BUILDING_KEY'], building)
        extra['building'] = hashlib.sha256(building.encode('utf-8')).hexdigest()
    SHEET['record_request'](holder, 'sheet', 'A-1', **extra)
    return holder.Strings

def sheet_doc(items, main=(), strings=None):
    root = types.SimpleNamespace(FullPath='Sheet', IsDeleted=False)
    linework = types.SimpleNamespace(FullPath='Sheet::Main', IsDeleted=False)
    return types.SimpleNamespace(Layers=[root, linework], PageUnitSystem='Millimeters', Views=types.SimpleNamespace(GetPageViews=lambda: [sheet_view]),
                                 Objects=types.SimpleNamespace(FindByLayer=lambda layer: list(main) if layer is linework else items),
                                 Strings=strings if strings is not None else started())

caption = page_item('Caption', Text('Section at joint', (8, 4, 12, 6)))
result = SHEET['check_sheet'](sheet_doc([caption, page_item('Locator leader D1', leader((0, 5), (20, 5)))]), 'A-1', 'Sheet', [])
ok(result == ['locator leader through text: Section at joint'], 'sheet: check_sheet fails a locator leader through a caption', result)
result = SHEET['check_sheet'](sheet_doc([caption, page_item('Locator leader D1', leader((0, 9), (20, 9)))]), 'A-1', 'Sheet', [])
ok(result == [], 'sheet: check_sheet passes a locator leader clear of the caption', result)
result = SHEET['check_sheet'](sheet_doc([caption, page_item('Label leader 1', leader((0, 5), (20, 5)))]), 'A-1', 'Sheet', [])
ok(result == [], 'sheet: a label leader is not held to the locator rule', result)

# check_sheet reads each text's drawn height (text height x dimension scale) against the height text() recorded
asked = {SHEET['TEXT_HEIGHT_KEY']: '7.0000'}
for scale in (1.5, 96.0):   # the old text(): the document's dimension style scale stayed on the text
    title = page_item('Title', Text('Camera obscura', (10, 10, 60, 17), 7.0, scale), asked)
    result = SHEET['check_sheet'](sheet_doc([title]), 'A-1', 'Sheet', [])
    ok(result == ['text drawn at %.1f mm, asked 7.0 mm: Camera obscura' % (7.0 * scale)], 'sheet: check_sheet fails text drawn at %gx the asked height' % scale, result)
title = page_item('Title', Text('Camera obscura', (10, 10, 60, 17), 7.0, 1.0), asked)
result = SHEET['check_sheet'](sheet_doc([title]), 'A-1', 'Sheet', [])
ok(result == [], 'sheet: check_sheet passes text drawn at the asked height (the fixed text())', result)


class Polyline:
    def __init__(self, *points):
        self.points = [Pt(*p) for p in points]

    def TryGetPolyline(self):
        return True, self.points

    def GetBoundingBox(self, accurate):
        xs, ys = [p.X for p in self.points], [p.Y for p in self.points]
        return types.SimpleNamespace(Min=Pt(min(xs), min(ys)), Max=Pt(max(xs), max(ys)))


fake_geo.Curve = Polyline
ring = page_item('Locator ring D1', types.SimpleNamespace(GetBoundingBox=lambda accurate: types.SimpleNamespace(Min=Pt(95, -5), Max=Pt(105, 5))))
lead = page_item('Locator leader D1', leader((0, 0), (95, 0)))
wall = page_item('Linework edge', Polyline((50, -100), (50, 100)))
result = SHEET['check_sheet'](sheet_doc([lead, ring], [wall]), 'A-1', 'Sheet', [], main_root='Sheet::Main')
ok('across the main drawing' in result[0] and any('not on the main drawing' in r for r in result), 'sheet: check_sheet fails a locator leader across the main drawing, and a ring on no drawn line', result)
near = page_item('Linework edge', Polyline((97, -100), (97, 100)))
result = SHEET['check_sheet'](sheet_doc([lead, ring], [near]), 'A-1', 'Sheet', [], main_root='Sheet::Main')
ok(result == [], 'sheet: lines at the leader\'s own joint pass', result)
result = SHEET['check_sheet'](sheet_doc([lead, ring], [wall]), 'A-1', 'Sheet', [])
ok(result == [], 'sheet: with no main_root the drawing is not read', result)
scaled = types.SimpleNamespace(Id='d', DetailGeometry=types.SimpleNamespace(PageToModelRatio=1 / 50.0))
scale_doc = sheet_doc([])
scale_doc.Objects.FindId = lambda i: scaled
result, said = run_print(SHEET['check_sheet'], scale_doc, 'A-1', 'Sheet', [], detail=scaled, scale=1 / 40.0)
ok(result == ['scale reads back 1:50.000, expected 1:40.000'] and '1:50.000' in said, 'sheet: check_sheet fails a scale that does not read back', result)
result, said = run_print(SHEET['check_sheet'], scale_doc, 'A-1', 'Sheet', [], detail=scaled, scale=1 / 50.0)
try:
    SHEET['check_sheet'](scale_doc, 'A-1', 'Sheet', [], min_margin_mm=5)
    ok(False, 'sheet: check_sheet takes no margin override')
except TypeError:
    ok(True, 'sheet: check_sheet takes no margin override')
ok(result == [], 'sheet: check_sheet passes the scale it reads back', result)
other_ring = page_item('Bubble ring D1', Polyline((40, -10), (60, -10), (60, 10), (40, 10), (40, -10)))
own_ring = page_item('Bubble ring D2', Polyline((-10, -10), (10, -10), (10, 10), (-10, 10)))
d2 = page_item('Locator leader D2', leader((10, 0), (95, 0)))
result = SHEET['check_sheet'](sheet_doc([d2, other_ring, own_ring]), 'A-1', 'Sheet', [])
ok(result == ['locator leader D2 through the ring of detail D1'], 'sheet: check_sheet fails a locator through another detail ring, not its own', result)
tag_ring = page_item('Detail tag ring D1', Polyline((-3, -3), (3, -3), (3, 3), (-3, 3), (-3, -3)))
through = page_item('Bubble linework D1', Polyline((-10, 0), (10, 0)))
clear_line = page_item('Bubble linework D1', Polyline((-10, 8), (10, 8)))
result = SHEET['check_sheet'](sheet_doc([tag_ring, through]), 'A-1', 'Sheet', [])
ok(result == ['a line runs through detail tag D1: Bubble linework D1'], 'sheet: check_sheet fails a line through a detail tag', result)
result = SHEET['check_sheet'](sheet_doc([tag_ring, clear_line]), 'A-1', 'Sheet', [])
ok(result == [], 'sheet: check_sheet passes a tag with no line through it', result)
label = page_item('Detail label D1', Text('D1 Post to beam', (8, 4, 12, 6)))
result = SHEET['check_sheet'](sheet_doc([label, page_item('Linework edge', Polyline((0, 5), (20, 5)))]), 'A-1', 'Sheet', [])
ok(result == ["a line runs through the label 'D1 Post to beam': Linework edge"], 'sheet: check_sheet fails a line through a label', result)
ring_d2 = page_item('Bubble ring D2', Polyline((12.2, -10), (32.2, -10), (32.2, 10), (12.2, 10), (12.2, -10)))
result = SHEET['check_sheet'](sheet_doc([label, ring_d2]), 'A-1', 'Sheet', [])
ok(result == ["the label 'D1 Post to beam' touches the ring of detail D2"], 'sheet: check_sheet fails a label touching a ring', result)
along = page_item('Linework edge', Polyline((20, 0.1), (80, 0.1)))
result = SHEET['check_sheet'](sheet_doc([lead, ring], [along]), 'A-1', 'Sheet', [], main_root='Sheet::Main')
ok(any('runs along a drawn edge' in r for r in result), 'sheet: check_sheet fails a locator leader along a member edge', result)
own_ring_d1 = page_item('Bubble ring D1', Polyline((-30, -20), (10, -20), (10, 20), (-30, 20), (-30, -20)))
inward = page_item('Locator leader D1', leader((10, 0), (-5, 0)))
result = SHEET['check_sheet'](sheet_doc([own_ring_d1, inward]), 'A-1', 'Sheet', [])
ok(result == ['locator leader D1 enters its own detail'], 'sheet: check_sheet fails a leader that enters its own detail', result)
l1, l2 = page_item('Locator leader D1', leader((0, 50), (100, 50))), page_item('Locator leader D2', leader((60, 50), (150, 50)))
result = SHEET['check_sheet'](sheet_doc([l1, l2]), 'A-1', 'Sheet', [])
ok(result == ['locator leaders D1 and D2 share a segment'], 'sheet: check_sheet fails two leaders sharing a segment', result)
edited = sheet_doc([], strings=started(json.dumps({'root': 'Sheet', 'objects': {'a': 'L|Brep|0,0,0,1,1,1', 'b': 'L|Brep|0,0,0,2,2,2'}})))
real = SHEET['building_fingerprints']
SHEET['building_fingerprints'] = lambda doc, root: {'a': 'L|Brep|0,0,0,1,1,1'}
result = SHEET['check_sheet'](edited, 'A-1', 'Sheet', [])
ok(len(result) == 1 and '1 objects removed, 0 changed' in result[0], 'sheet: check_sheet fails when the building was edited after the sheet started', result)
SHEET['building_fingerprints'] = lambda doc, root: {'a': 'L|Brep|0,0,0,1,1,1', 'b': 'L|Brep|0,0,0,2,2,2', 'new': 'x'}
ok(SHEET['check_sheet'](edited, 'A-1', 'Sheet', []) == [], 'sheet: an unchanged building passes')
edited.Strings.Delete(SHEET['BUILDING_KEY'])
result = SHEET['check_sheet'](edited, 'A-1', 'Sheet', [])
ok(result == ['the building record was replaced or removed after the sheet started'], 'sheet: deleting the building record fails rather than skipping the guard', result)
SHEET['building_fingerprints'] = real
wall_line = page_item('Linework edge', Polyline((50, -100), (50, 100)))
crossing = page_item('Label leader', leader((0, 0), (95, 0)))
dot = page_item('Label dot', types.SimpleNamespace(GetBoundingBox=lambda accurate: types.SimpleNamespace(Min=Pt(94, -1), Max=Pt(96, 1))))
result = SHEET['check_sheet'](sheet_doc([crossing, dot], [wall_line]), 'A-1', 'Sheet', [], main_root='Sheet::Main')
ok(any('label leader across the main drawing' in r for r in result), 'sheet: check_sheet fails a label leader across the main drawing', result)
clear_leader = page_item('Label leader', leader((60, 0), (95, 0)))
result = SHEET['check_sheet'](sheet_doc([clear_leader, dot], [wall_line]), 'A-1', 'Sheet', [], main_root='Sheet::Main')
ok(not any('label leader' in r for r in result), 'sheet: a label leader in clear paper passes', result)
two = [page_item('Label leader', leader((0, 30), (60, 30))), page_item('Label leader', leader((40, 30), (100, 30)))]
result = SHEET['check_sheet'](sheet_doc(two), 'A-1', 'Sheet', [])
ok(any('shares a segment' in r for r in result), 'sheet: label leaders that converge on one line fail', result)
unplaced = sheet_doc([])
SHEET['record_request'](unplaced, 'locator', 'D2', 'detail D2: none of its 4 joints can be reached')
result = SHEET['check_sheet'](unplaced, 'A-1', 'Sheet', [])
ok(result == ['detail D2: none of its 4 joints can be reached'], 'sheet: check_sheet fails a detail with no clean joint', result)

# Requests are recomputed from the sheet, and the record of them cannot be deleted to pass.
NOT_PLACED = "label %r: no leader to the part stays clear of the main drawing, the other leaders and text; give other points on the part or move the drawing"
def run_one_sheet():
    """Run 1's sheet: 3 labels placed, 5 that found no clear leader, then 2 more tries that failed too."""
    placed = [page_item('Label text', Text(body, (200 + 30 * i, 10, 220 + 30 * i, 13))) for i, body in enumerate(('Lap siding', 'Head flashing', 'Gypsum'))]
    doc = sheet_doc(placed)
    for body in ('Lap siding', 'Exterior casing', 'Head flashing', 'Casement sash', 'Sloped sill', '2x6 stud', 'Sheathing', 'Gypsum', 'Top plates and studs', 'Sheathing and weather barrier'):
        drawn = any(i.Geometry.PlainText == body for i in placed)
        SHEET['record_request'](doc, 'label', body, None if drawn else NOT_PLACED % body)
    return doc
dropped = ['Exterior casing', 'Casement sash', 'Sloped sill', '2x6 stud', 'Sheathing', 'Top plates and studs', 'Sheathing and weather barrier']
honest = SHEET['check_sheet'](run_one_sheet(), 'A-1', 'Sheet', [])
ok(honest == [NOT_PLACED % b for b in dropped], 'sheet: every label that could not be placed fails check_sheet', honest)
trick = run_one_sheet()
for b in dropped:   # run 1 deleted the failure records it was given; the new records hold no per-request key to delete
    trick.Strings.Delete('as-sheet:unplaced:label ' + b)
ok(SHEET['check_sheet'](trick, 'A-1', 'Sheet', []) == honest, "sheet: run 1's deletion of the unplaced-label records no longer passes", trick.Strings.items)
for key in (SHEET['REQUESTS_KEY'], SHEET['SEAL_KEY']):
    gone = run_one_sheet()
    gone.Strings.Delete(key)
    result = SHEET['check_sheet'](gone, 'A-1', 'Sheet', [])
    ok('request record is missing' in result[0] and 'never delete a request or failure record' in result[0], 'sheet: deleting the %s fails check_sheet' % key.split(':')[-1], result)
gone = run_one_sheet()
gone.Strings.Delete(SHEET['REQUESTS_KEY']); gone.Strings.Delete(SHEET['SEAL_KEY'])
result = SHEET['check_sheet'](gone, 'A-1', 'Sheet', [])
ok(len(result) == 1 and 'request record is missing' in result[0], 'sheet: deleting the whole request record fails check_sheet', result)
pruned = run_one_sheet()
entries = json.loads(SHEET['string_value'](pruned, SHEET['REQUESTS_KEY']))
pruned.Strings.SetString(SHEET['REQUESTS_KEY'], json.dumps([e for e in entries if e.get('message') is None]))
result = SHEET['check_sheet'](pruned, 'A-1', 'Sheet', [])
ok(len(result) == 1 and 'request record was edited' in result[0], 'sheet: removing the failed requests from the record fails check_sheet', result)
truncated = run_one_sheet()
entries = json.loads(SHEET['string_value'](truncated, SHEET['REQUESTS_KEY']))
truncated.Strings.SetString(SHEET['REQUESTS_KEY'], json.dumps(entries[:4]))
result = SHEET['check_sheet'](truncated, 'A-1', 'Sheet', [])
ok('has 4 entries but 11 were recorded' in result[0], 'sheet: cutting the record short fails check_sheet', result)
removed_label = sheet_doc([page_item('Label text', Text('Lap siding', (200, 10, 220, 13)))])
SHEET['record_request'](removed_label, 'label', 'Lap siding'); SHEET['record_request'](removed_label, 'label', 'Gypsum')
result = SHEET['check_sheet'](removed_label, 'A-1', 'Sheet', [])
ok(result == ["label 'Gypsum' was requested and is not on the sheet"], 'sheet: a placed label later deleted from the page fails', result)
retried = sheet_doc([page_item('Label text', Text('Sheathing', (200, 10, 220, 13)))])
SHEET['record_request'](retried, 'label', 'Sheathing', NOT_PLACED % 'Sheathing'); SHEET['record_request'](retried, 'label', 'Sheathing')
ok(SHEET['check_sheet'](retried, 'A-1', 'Sheet', []) == [], 'sheet: a label placed on a later try passes', retried.Strings.items)
details = sheet_doc([page_item('Bubble ring D1', Text('', (0, 0, 1, 1))), page_item('Bubble linework D1', Text('', (0, 0, 1, 1))), page_item('Bubble ring D2', Text('', (0, 0, 1, 1)))])
SHEET['record_request'](details, 'detail', 'D1'); SHEET['record_request'](details, 'detail', 'D2')
result = SHEET['check_sheet'](details, 'A-1', 'Sheet', [])
ok(result == ["detail 'D2' was requested and is not on the sheet"], 'sheet: a detail with a ring and no linework fails', result)
loc = sheet_doc([page_item('Locator leader D1', leader((0, 300), (0, 320))), page_item('Locator ring D1', Text('', (0, 0, 1, 1)))])
SHEET['record_request'](loc, 'locator', 'D1'); SHEET['record_request'](loc, 'locator', 'D3')
result = SHEET['check_sheet'](loc, 'A-1', 'Sheet', [])
ok(result == ["locator 'D3' was requested and is not on the sheet"], 'sheet: a locator with nothing drawn fails, a drawn one passes', result)
ok(any('never delete a request or failure record' in r for r in SHEET['check_sheet'](sheet_doc([], strings=Strings()), 'A-1', 'Sheet', [])), 'sheet: a sheet not started by setup_sheet fails check_sheet')

# place_label keeps only target points no other part covers in the main view (visible_points).
clip = CORE['clip_segment_to_box']
ok(clip((0, 0, 0), (10, 0, 0), (2, -1, -1, 4, 1, 1)) == (0.2, 0.4), 'sheet: a segment is clipped to a box', clip((0, 0, 0), (10, 0, 0), (2, -1, -1, 4, 1, 1)))
ok(clip((0, 5, 0), (10, 5, 0), (2, -1, -1, 4, 1, 1)) is None, 'sheet: a segment beside a box misses it')


class V:
    def __init__(self, x, y=None, z=None):
        self.X, self.Y, self.Z = (x.X, x.Y, x.Z) if y is None else (x, y, z)
    def __add__(self, o): return V(self.X + o.X, self.Y + o.Y, self.Z + o.Z)
    def __sub__(self, o): return V(self.X - o.X, self.Y - o.Y, self.Z - o.Z)
    def __mul__(self, k): return V(self.X * k, self.Y * k, self.Z * k)
    def DistanceTo(self, o): return math.sqrt((self.X - o.X) ** 2 + (self.Y - o.Y) ** 2 + (self.Z - o.Z) ** 2)
    Length = property(lambda self: math.sqrt(self.X ** 2 + self.Y ** 2 + self.Z ** 2))
    def Unitize(self):
        n = self.Length
        self.X, self.Y, self.Z = self.X / n, self.Y / n, self.Z / n


class BoxBrep:
    """A solid box: inside test, and where a line crosses its surface."""
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
    def GetBoundingBox(self, accurate):
        return types.SimpleNamespace(Min=V(*self.lo), Max=V(*self.hi), Diagonal=V(*self.hi) - V(*self.lo))
    def IsPointInside(self, p, tol, strict):
        return all(l + tol < v < h - tol for l, h, v in zip(self.lo, self.hi, (p.X, p.Y, p.Z)))


def curve_brep(line, brep, tol):
    a, b = line
    span = CORE['clip_segment_to_box']((a.X, a.Y, a.Z), (b.X, b.Y, b.Z), brep.lo + brep.hi)
    if span is None:
        return True, [], []
    return True, [], [a + (b - a) * t for t in span if 0 < t < 1]


ray_geo = types.SimpleNamespace(Point3d=V, Vector3d=V, LineCurve=lambda a, b: (a, b),
                                Intersect=types.SimpleNamespace(Intersection=types.SimpleNamespace(CurveBrep=curve_brep)))
saved_geo = SHEET['G']
SHEET['G'] = ray_geo
looking = types.SimpleNamespace(Viewport=types.SimpleNamespace(CameraDirection=V(0, 1, 0)))   # camera at -y, looking along +y
ray_doc = types.SimpleNamespace(ModelAbsoluteTolerance=0.001)
siding = BoxBrep((0, -1, 0), (10, 0, 10))         # outside, toward the camera
stud = BoxBrep((2, 0.5, 0), (3.5, 6, 10))          # behind the siding
pts = lambda found: [(q.X, q.Y, q.Z) for q in found]
see = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 0.5, 5)], [siding, stud]))
ok(see == [], 'sheet: a stud face behind the siding is covered, so place_label drops it', see)
see = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 0.5, 5), V(5, -1, 5)], [siding, stud]))
ok(see == [(5, -1, 5)], 'sheet: a point on the siding face toward the camera is kept', see)
see = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 0.5, 5)], [siding, stud], crop=(1, -2, 0, 9, 7, 10)))
ok(see == [], 'sheet: inside a cut-away that keeps the siding, the stud is still covered', see)
see = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 0.5, 5)], [siding, stud], crop=(1, 0.2, 0, 9, 7, 10)))
ok(see == [(2.5, 0.5, 5)], 'sheet: a cut-away that leaves the siding out shows the stud', see)
see = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 6, 5)], [siding, stud], crop=(1, 0.2, 0, 9, 7, 10)))
ok(see == [], 'sheet: a face turned away from the camera is covered by its own part', see)
cut_face = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 3, 5)], [siding, BoxBrep((0, 0, 0), (10, 2.5, 10))], crop=(1, 1, 0, 9, 7, 10)))
ok(cut_face == [], 'sheet: a solid the crop cuts through still covers what is behind its cut face', cut_face)
inside = pts(SHEET['visible_points'](ray_doc, looking, [V(2.5, 3, 5)], [BoxBrep((0, 0.5, 0), (10, 6, 10))]))
ok(inside == [], 'sheet: a point inside another solid is covered', inside)
ok(pts(SHEET['visible_points'](ray_doc, looking, [V(1, 1, 1)], [])) == [(1, 1, 1)], 'sheet: before main_linework nothing is known to cover a point')
SHEET['G'] = saved_geo
src = (root / 'rhino-thinline/scripts/as-sheet.py').read_text()
start = src.index('def place_label(')
ok('visible_points(doc, main_detail, world_points)' in src[start:src.index('\ndef ', start + 10)], 'sheet: place_label filters its points through visible_points before picking a route')

# ---- the split: rhino-thinline holds conventions and loads alone; rhino-axon adds the view ----
THIN = load(root / 'rhino-thinline/scripts/as-sheet.py')
VIEW = ('setup_sheet', 'parallel_detail', 'main_linework', 'crop_copies', 'cut_detail', 'round_detail', 'place_locator', 'check_view',
        'building_fingerprints', 'main_blockers', 'solids_in', 'MAIN_KEY', 'layer_selected', 'true_cut', 'pick_locator', 'building_changes')
ok(not [n for n in VIEW if n in THIN], 'split: rhino-thinline chooses no view', [n for n in VIEW if n in THIN])
ok(all(n in SHEET for n in VIEW + ('new_sheet', 'place_label', 'title_block', 'export_pdf', 'record_request', 'WEIGHTS', 'hatch_pattern')), 'split: as-axon.py gives one namespace with both halves')
import ast as _ast
def top_names(path):
    return {n.name for n in _ast.parse(path.read_text()).body if isinstance(n, _ast.FunctionDef)} | {t.id for n in _ast.parse(path.read_text()).body if isinstance(n, _ast.Assign) for t in n.targets if isinstance(t, _ast.Name)}
thin_names = top_names(root / 'rhino-thinline/scripts/as-sheet.py') | top_names(root / 'rhino-thinline/scripts/as-sheet-core.py')
axon_names = top_names(root / 'rhino-axon/scripts/as-axon.py') | top_names(root / 'rhino-axon/scripts/as-axon-core.py')
twice = sorted((thin_names & axon_names) - {'HERE', 'check_sheet', 'visible_points'})
ok(not twice, 'split: no function lives in both skills, except the two axon replaces on purpose', twice)
pts_in = [object(), object()]
ok(THIN['visible_points'](None, None, pts_in) == pts_in, 'split: alone, thinline keeps every label point (it knows no view)')
view_case = sheet_doc([crossing, dot], [wall_line])
full = SHEET['check_sheet'](view_case, 'A-1', 'Sheet', [], main_root='Sheet::Main')
conv = THIN['check_sheet'](sheet_doc([crossing, dot], [wall_line]), 'A-1', 'Sheet', [])
ok(any('across the main drawing' in r for r in full) and not any('across the main drawing' in r for r in conv), 'split: the view check (leaders across the drawing) is axon\'s; thinline\'s check is the conventions only', (full, conv))
two = [page_item('Label leader', leader((0, 30), (60, 30))), page_item('Label leader', leader((40, 30), (100, 30)))]
ok(THIN['check_sheet'](sheet_doc(two), 'A-1', 'Sheet', []) == SHEET['check_sheet'](sheet_doc(two), 'A-1', 'Sheet', []), 'split: on conventions alone both checks agree')

for mod in stubbed:
    del sys.modules[mod]

# ---- No project constants or home paths in what ships ----
# Terms that must not ship are held as hashes, so this test does not name them.
BANNED = {'b7d177840ebb2217', '297839fea58cd1e3', 'd1eeefe5edcb004c', 'dbe1dcf6a112e8b4', 'a569f8dbe4c6ad9d', '91287388e8e9e4db', '3bc7f74b69c3cb77', '6358bacbe7eb49e2'}
home = re.compile(r'/Users/|~/Documents')


def banned_terms(text, hashes=BANNED):
    words = re.findall(r'[a-z0-9-]+', text.lower())
    grams = words + [' '.join(pair) for pair in zip(words, words[1:])]
    return [g for g in grams if hashlib.sha256(g.encode()).hexdigest()[:16] in hashes]


seed = hashlib.sha256(b'seeded place').hexdigest()[:16]
ok(banned_terms('a seeded place name', {seed}) == ['seeded place'], 'ships: the term check finds a seeded term')
repo = root.parent


def files_under(*patterns):
    for pattern in patterns:
        for match in sorted(repo.glob(pattern)):
            for path in ([match] if match.is_file() else sorted(match.rglob('*'))):
                if path.is_file() and '__pycache__' not in path.parts:
                    yield path


def text_of(path):
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return None


# Every Rhino file that ships or describes what ships: no terms, no home paths.
shipped = list(files_under('skills/*rhino*', 'hooks/*rhino*', 'agents/rhino-*', 'mcp/*rhino*',
                           'maintainers/rhino-lessons', 'evals/rhino-modeling'))
ok(any(p.parent.name == 'rhino-model' for p in shipped), 'ships: the term scan reaches skills/rhino-model')
for path in shipped:
    text = text_of(path)
    if text is not None:
        ok(not banned_terms(text) and not home.search(text), 'ships: no project terms or home paths in %s' % path.relative_to(repo))
# Tests and fixtures: no terms. They may hold synthetic home paths on purpose,
# for example to check that private details are stripped.
for path in files_under('tests/test-rhino-*', 'tests/fixtures'):
    text = text_of(path)
    if text is not None:
        ok(not banned_terms(text), 'ships: no project terms in %s' % path.relative_to(repo))

if failures:
    print('FAIL', len(failures))
    for line in failures:
        print(' -', line)
    sys.exit(1)
print('PASS: %d assertions on the BOM, display and sheet checks' % passed[0])
PY
