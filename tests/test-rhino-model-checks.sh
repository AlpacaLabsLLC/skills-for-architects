#!/usr/bin/env bash
# Seeded cases for the as-rhino-model requirements check: clash, network, hardware, flags and report.
# Rhino is not available here, so a small stub stands in for RhinoCommon: axis-aligned box breps,
# straight line curves and points. It proves the checkers' logic, not RhinoCommon's behaviour on
# real geometry. See the stub's calls in the Rhino section of this file.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
python3 - <<'PY'
import contextlib, io, json, sys, types
from pathlib import Path

ROOT = Path.cwd() / "skills/rhino-model/scripts"
CHECK, MODEL = ROOT / "as-check.py", ROOT / "as-check-model.py"

# ---- stub RhinoCommon ----
class Point3d:
    def __init__(self, x, y=None, z=None):
        self.X, self.Y, self.Z = (x.X, x.Y, x.Z) if y is None else (x, y, z)
    def DistanceTo(self, o):
        return ((self.X - o.X) ** 2 + (self.Y - o.Y) ** 2 + (self.Z - o.Z) ** 2) ** 0.5

class BoundingBox:
    def __init__(self, lo=None, hi=None):
        self.Min, self.Max = lo, hi
    @classmethod
    def _empty(cls):
        return cls()
    def Union(self, b):
        if self.Min is None:
            self.Min, self.Max = b.Min, b.Max
        else:
            self.Min = Point3d(min(self.Min.X, b.Min.X), min(self.Min.Y, b.Min.Y), min(self.Min.Z, b.Min.Z))
            self.Max = Point3d(max(self.Max.X, b.Max.X), max(self.Max.Y, b.Max.Y), max(self.Max.Z, b.Max.Z))

class GeometryBase:
    IsValid = True
    def GetBoundingBox(self, _accurate):
        return self.bb

class Vertex:
    def __init__(self, p):
        self.Location = p

class Domain:
    def __init__(self, a, b):
        self.T0, self.T1, self.Mid = a, b, (a + b) / 2

class Edge:
    Domain = Domain(0.0, 1.0)
    def __init__(self, a, b):
        self.a, self.b = a, b
    def PointAt(self, t):
        return Point3d(*[u + (v - u) * t for u, v in zip((self.a.X, self.a.Y, self.a.Z), (self.b.X, self.b.Y, self.b.Z))])

class Brep(GeometryBase):
    def __init__(self, lo, hi, solid=True):
        self.lo, self.hi = tuple(lo), tuple(hi)
        self.bb = BoundingBox(Point3d(*lo), Point3d(*hi))
        self.IsSolid = solid
        corners = [Point3d(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        self.Vertices = [Vertex(c) for c in corners]
        self.Edges = [Edge(a, b) for i, a in enumerate(corners) for b in corners[i + 1:]
                      if sum(1 for u, v in zip((a.X, a.Y, a.Z), (b.X, b.Y, b.Z)) if u != v) == 1]
    def IsPointInside(self, p, tol, strict):
        if strict:  # inside by at least tol
            return all(l + tol < v < h - tol for l, h, v in zip(self.lo, self.hi, (p.X, p.Y, p.Z)))
        return all(l - tol <= v <= h + tol for l, h, v in zip(self.lo, self.hi, (p.X, p.Y, p.Z)))
    def ClosestPoint(self, p):
        return Point3d(*[min(max(v, l), h) for l, h, v in zip(self.lo, self.hi, (p.X, p.Y, p.Z))])
    @staticmethod
    def CreateBooleanIntersection(a, b, tol):
        lo = [max(u, v) for u, v in zip(a.lo, b.lo)]
        hi = [min(u, v) for u, v in zip(a.hi, b.hi)]
        return [Brep(lo, hi)] if all(h - l > 0 for l, h in zip(lo, hi)) else []

class Curve(GeometryBase):
    pass

class LineCurve(Curve):
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.Domain = Domain(0.0, 1.0)
        self.bb = BoundingBox(Point3d(min(a.X, b.X), min(a.Y, b.Y), min(a.Z, b.Z)),
                              Point3d(max(a.X, b.X), max(a.Y, b.Y), max(a.Z, b.Z)))
    PointAtStart = property(lambda s: s.a)
    PointAtEnd = property(lambda s: s.b)
    def PointAt(self, t):
        return Edge(self.a, self.b).PointAt(t)
    def ClosestPoint(self, p):
        v = [self.b.X - self.a.X, self.b.Y - self.a.Y, self.b.Z - self.a.Z]
        w = [p.X - self.a.X, p.Y - self.a.Y, p.Z - self.a.Z]
        n = sum(x * x for x in v) or 1.0
        return True, max(0.0, min(1.0, sum(x * y for x, y in zip(v, w)) / n))

class Point(GeometryBase):
    def __init__(self, p):
        self.Location = p
        self.bb = BoundingBox(p, p)

class Surface(GeometryBase):
    pass

class SubD(GeometryBase):
    pass

class Mesh(GeometryBase):
    def __init__(self, lo, hi):
        self.bb = BoundingBox(Point3d(*lo), Point3d(*hi))

def curve_brep(c, b, tol):
    ts = []
    for axis in range(3):
        a0, a1 = [(c.a.X, c.a.Y, c.a.Z)[axis], (c.b.X, c.b.Y, c.b.Z)[axis]]
        if a0 == a1:
            continue
        for plane in (b.lo[axis], b.hi[axis]):
            t = (plane - a0) / (a1 - a0)
            if 0 <= t <= 1:
                p = c.PointAt(t)
                if all(l - 1e-9 <= v <= h + 1e-9 for l, h, v in zip(b.lo, b.hi, (p.X, p.Y, p.Z))):
                    ts.append(p)
    return bool(ts), [], ts

Geometry = types.SimpleNamespace(Point3d=Point3d, BoundingBox=types.SimpleNamespace(Empty=None), Brep=Brep, Curve=Curve,
                                 LineCurve=LineCurve, Point=Point, Surface=Surface, SubD=SubD, Mesh=Mesh,
                                 Intersect=types.SimpleNamespace(Intersection=types.SimpleNamespace(CurveBrep=curve_brep)))

class EmptyBox:  # BoundingBox.Empty is read fresh by the existing checks
    def __get__(self, *_):
        return BoundingBox()

Geometry = type("GeometryNS", (), dict(vars(Geometry)))
Geometry.BoundingBox = type("BB", (), {"Empty": EmptyBox()})

class Settings:
    HiddenObjects = LockedObjects = DeletedObjects = False

Rhino = types.ModuleType("Rhino")
Rhino.Geometry = Geometry
Rhino.DocObjects = types.SimpleNamespace(ObjectEnumeratorSettings=Settings)
Rhino.RhinoDoc = types.SimpleNamespace(ActiveDoc=None)
sys.modules["Rhino"] = Rhino
sys.modules["System"] = types.ModuleType("System")

class Obj:
    def __init__(self, n, layer, name, g, hidden=False):
        self.Id, self.Geometry, self.hidden = "id-%04d" % n, g, hidden
        self.Attributes = types.SimpleNamespace(LayerIndex=layer, Name=name)
        self.RuntimeSerialNumber = n
        self.ObjectType = type(g).__name__

class Objects(list):
    def __iter__(self):  # like a plain enumeration: hidden objects are left out
        return iter([o for o in list.__iter__(self) if not o.hidden])
    def GetObjectList(self, s):
        return [o for o in list.__iter__(self) if s.HiddenObjects or not o.hidden]

class Strings(dict):
    def GetValue(self, k):
        return self.get(k)
    def SetString(self, k, v):
        self[k] = v

class Layer:
    def __init__(self, path):
        self.FullPath, self.IsDeleted = path, False

class Layers(list):
    def FindByFullPath(self, p, _d):
        return next((i for i, l in enumerate(self) if l.FullPath == p), -1)

class Doc:
    Name = ""; Path = None; Modified = True; ModelUnitSystem = "Meters"; ModelAbsoluteTolerance = 0.001
    def __init__(self):
        self.Objects, self.Layers, self.Strings, self.n = Objects(), Layers(), Strings(), 0
    def layer(self, path):
        i = self.Layers.FindByFullPath(path, -1)
        if i < 0:
            self.Layers.append(Layer(path)); i = len(self.Layers) - 1
        return i
    def add(self, path, name, g, hidden=False):
        self.n += 1
        self.Objects.append(Obj(self.n, self.layer(path), name, g, hidden))

def box(lo, hi, solid=True):
    return Brep(lo, hi, solid)

def building():
    """A clean case: pier and girder, a toilet and a basin on a drain to a sump, a cold riser into a tank."""
    d = Doc()
    d.layer("B")
    d.add("B::Piers", "pier 1", box((0, 0, 0), (0.4, 0.4, 1.0)))
    d.add("B::Girders", "girder 1", box((0, 0, 1.0), (3, 0.4, 1.3)))
    d.add("B::Fixtures", "toilet 1", box((1.0, 1.0, 0.5), (1.4, 1.5, 0.9)))
    d.add("B::Fixtures", "basin 1", box((2.0, 1.0, 0.8), (2.4, 1.3, 0.9)))
    d.add("B::Drain", "drain 1", box((1.15, 1.2, 0.2), (1.25, 1.3, 0.5)))   # toilet down to the run
    d.add("B::Drain", "drain run", box((1.15, 1.2, 0.1), (3.0, 1.3, 0.2)))
    d.add("B::Drain", "drain 2", box((2.15, 1.1, 0.2), (2.25, 1.2, 0.8)))   # basin down to the run
    d.add("B::Drain", "drain 3", box((2.15, 1.1, 0.1), (2.25, 1.3, 0.2)))
    d.add("B::Sump", "sump", box((3.0, 1.0, 0.0), (4.0, 2.0, 1.0)))
    d.add("B::Cold", "cold riser 1", box((5.0, 0, 0), (5.05, 0.05, 2.1)))   # top 0.1 inside the tank
    d.add("B::Tank", "tank", box((4.8, -0.2, 2.0), (5.3, 0.3, 2.5)))
    return d

BASE = {"parent": "B", "brief": "seeded case", "units": "Meters",
        "clash": {"Cold": {"against": ["Piers", "Girders", "Tank"]}},
        "network": {"Drain": {"pipes": ["Drain"], "fixtures": {"name": ["toilet*", "basin*"]}, "to": {"name": ["sump*"]}}},
        "intended": [{"a": "cold riser*", "b": "tank*", "why": "the riser feeds the tank"}]}

def run(doc, req=None, mode="check", g=None):
    out = io.StringIO()
    env = {"__rhino_doc__": doc, "AS_SCRIPT_FILE": str(CHECK), "AS_MODE": mode, "AS_REQUIREMENTS": req}
    env.update(g or {})
    with contextlib.redirect_stdout(out):
        exec(compile(CHECK.read_text(), str(CHECK), "exec"), env)
    return out.getvalue()

def check(doc, req):
    run(doc, dict(req), "write")
    return run(doc)

def run_doc_result(doc):
    return doc.Strings.GetValue("as:requirements-check")

def status(text):
    return next(l for l in text.splitlines() if l.startswith("ASCHECK")).split()[1]

def line(text, start):
    return next(l for l in text.splitlines() if l.strip().startswith(start))

passed = 0
def ok(cond, name, text=""):
    global passed
    assert cond, "%s\n%s" % (name, text)
    passed += 1

# ---- clean case must pass ----
t = check(building(), BASE)
ok(status(t) == "status=pass", "clean case passes", t)
ok("clashes\": 0" in line(t, "PASS  clash Cold") and "declared\": 1" in line(t, "PASS  clash Cold"), "declared connection is listed, not a clash", t)
ok("declared: cold riser 1 x tank" in t, "excused pair is printed", t)

# ---- a riser through a pier must fail ----
d = building()
d.add("B::Cold", "cold riser 2", box((0.15, 0.15, -0.2), (0.25, 0.25, 0.9)))
t = check(d, BASE)
ok(status(t) == "status=fail", "riser through pier fails", t)
ok("clash: cold riser 2 x pier 1" in t, "the clash names both objects", t)

# ---- the same riser as a centreline curve ----
d = building()
d.add("B::Cold", "cold riser c", LineCurve(Point3d(0.2, 0.2, -0.5), Point3d(0.2, 0.2, 2.0)))
t = check(d, BASE)
ok("clash: cold riser c x pier 1" in t, "centreline through a pier fails", t)

# ---- a centreline that stops on the face does not clash ----
d = building()
d.add("B::Cold", "cold riser d", LineCurve(Point3d(0.2, 0.2, -0.5), Point3d(0.2, 0.2, 0.0)))
t = check(d, BASE)
ok("cold riser d" not in t or "clash: cold riser d" not in t, "a curve ending on a face is not a clash", t)

# ---- the declaration is what excuses the overlap ----
t = check(building(), dict(BASE, intended=[]))
ok(status(t) == "status=fail" and "clash: cold riser 1 x tank" in t, "undeclared riser into tank is a clash", t)

# ---- declarations cannot be blanket or unexplained ----
t = check(building(), dict(BASE, intended=[{"a": "*", "b": "tank*", "why": "x"}]))
ok(status(t) == "status=fail" and "refused intended" in t, "bare wildcard refused", t)
t = check(building(), dict(BASE, intended=[{"a": "cold riser*", "b": "tank*"}]))
ok(status(t) == "status=fail" and "refused intended" in t, "declaration without why refused", t)

# ---- touching faces are not a clash ----
t = check(building(), dict(BASE, clash={"Piers": {"against": ["Girders"]}}))
ok("PASS  clash Piers" in t, "pier under girder only touches", t)

# ---- a broken drain must fail ----
d = Doc(); d.layer("B")
d.add("B::Fixtures", "toilet 1", box((1.0, 1.0, 0.5), (1.4, 1.5, 0.9)))
d.add("B::Fixtures", "basin 1", box((2.0, 1.0, 0.8), (2.4, 1.3, 0.9)))
d.add("B::Drain", "drain 1", box((1.15, 1.2, 0.2), (1.25, 1.3, 0.5)))
d.add("B::Drain", "drain run", box((1.15, 1.2, 0.1), (3.0, 1.3, 0.2)))
d.add("B::Drain", "drain 2 short", box((2.15, 1.1, 0.25), (2.25, 1.2, 0.8)))  # stops 0.05 above the run
d.add("B::Sump", "sump", box((3.0, 1.0, 0.0), (4.0, 2.0, 1.0)))
drain_only = {k: v for k, v in BASE.items() if k != "clash"}
t = check(d, drain_only)
ok(status(t) == "status=fail", "broken drain fails", t)
ok("not connected: basin 1" in t and "0.05 away" in t, "names the fixture and the gap", t)
ok("not connected: toilet 1" not in t, "the connected fixture is not reported", t)

# ---- a fixture with nothing to reach ----
d = building()
d.add("B::Fixtures", "basin 2", box((7, 7, 0.8), (7.4, 7.3, 0.9)))
t = check(d, BASE)
ok("not connected: basin 2" in t, "isolated fixture fails", t)

# ---- empty selections must not pass ----
t = check(building(), dict(BASE, clash={"Colt": {"against": ["Piers"]}}))
ok("FAIL  clash Colt" in t, "a mistyped clash layer fails", t)
t = check(building(), dict(BASE, clash={}, network={"Drain": {"pipes": ["Drin"], "fixtures": {"name": ["toilet*"]}, "to": {"name": ["sump*"]}}}))
ok("FAIL  network Drain" in t and "nothing matched: pipes" in t, "a mistyped pipe layer fails", t)

# ---- members and pairs: a zero only passes with members on both sides ----
def apart():
    """Pipe and pier far from each other, so no bounding boxes overlap."""
    d = Doc(); d.layer("B")
    d.add("B::Cold", "cold 1", box((0, 0, 0), (0.1, 0.1, 1)))
    d.add("B::Cold", "cold 2", box((1, 0, 0), (1.1, 0.1, 1)))
    d.add("B::Piers", "pier 1", box((5, 5, 0), (5.4, 5.4, 1)))
    return d
t = check(apart(), {"parent": "B", "brief": "seeded", "clash": {"Cold": {"against": ["Piers"]}}})
ok(status(t) == "status=pass" and "PASS  clash Cold" in t, "members on both sides and nothing near is a pass", t)
ok('"group": 2, "against": 1, "pairs_tested": 0' in line(t, "PASS  clash Cold"), "the result gives members on each side and pairs tested", t)
ok("members: 2 in Cold, 1 against; 0 of 2 pairs tested" in t and "clear: members on both sides" in t, "the output says a zero-pair pass is clear", t)

t = check(building(), {"parent": "B", "brief": "seeded", "clash": {"Cold": {"against": [{"name": ["gas main*"]}]}}})
ok(status(t) == "status=fail" and "FAIL  clash Cold" in t and "NOT MEASURED" not in t, "an empty side the requirement names fails", t)
ok("members: 1 in Cold, 0 against" in t and "clear:" not in t, "an empty side is counted and not called clear", t)
t = check(apart(), {"parent": "B", "brief": "seeded", "clash": {"Vent": {"against": ["Piers"]}}})
ok(status(t) == "status=fail" and "FAIL  clash Vent" in t and "members: 0 in Vent, 1 against" in t, "an empty named group fails", t)

d = Doc(); d.layer("B")
d.add("B::Cold", "cold 1", box((0, 0, 0), (0.1, 0.1, 1)))
t = check(d, {"parent": "B", "brief": "seeded", "clash": {"Cold": {}}})
ok(status(t) == "status=fail" and "NOT MEASURED  clash Cold" in t and "PASS  clash Cold" not in t, "nothing else under the parent is not measured and not a pass", t)
ok("1 with nothing to measure" in line(t, "Requirements:") and "not measured: nothing to test against" in t, "the status line and detail say so", t)
ok("clashes" not in line(t, "Checked:"), "a check with nothing to measure is not listed as checked", t)
ok(json.loads(run_doc_result(d))["not_measured"] == ["clash Cold"], "the stored result names it", t)
t = check(apart(), {"parent": "B", "brief": "seeded", "layers": {"Vent": {"min": 0, "max": 4}},
                    "clash": {"Cold": {"against": ["Vent"]}}})
ok("NOT MEASURED  clash Cold" in t and status(t) == "status=fail", "a side whose layer allows zero is not measured", t)
t = check(apart(), {"parent": "B", "brief": "seeded", "clash": {"Cold": {"against": ["Cold"]}}})
ok("clear:" in t and "0 of 1 pairs tested" in t, "a group against itself pairs its own members", t)
d = Doc(); d.layer("B")
d.add("B::Cold", "cold 1", box((0, 0, 0), (0.1, 0.1, 1)))
t = check(d, {"parent": "B", "brief": "seeded", "clash": {"Cold": {"against": ["Cold"]}}})
ok("NOT MEASURED  clash Cold" in t and "both sides are the same objects" in t, "one object against itself is not measured", t)

# ---- zero tested because pairs were skipped is not clear ----
d = Doc(); d.layer("B")
d.add("B::Cold", "cold c", LineCurve(Point3d(0, 0, 0), Point3d(1, 1, 1)))
d.add("B::Hot", "hot c", LineCurve(Point3d(0, 1, 0), Point3d(1, 0, 1)))
t = check(d, {"parent": "B", "brief": "seeded", "clash": {"Cold": {"against": ["Hot"]}}})
ok("skipped 1 pair" in t and "clear:" not in t, "skipped pairs are not reported as clear", t)

# ---- hidden objects still count ----
d = building()
d.add("B::Cold", "cold riser h", box((0.15, 0.15, 0.1), (0.25, 0.25, 0.9)), hidden=True)
t = check(d, BASE)
ok("clash: cold riser h x pier 1" in t, "a hidden riser is still tested", t)

# ---- an open surface is skipped and counted ----
d = building()
d.add("B::Cold", "cold shell", box((0.1, 0.1, 0.1), (0.3, 0.3, 0.9), solid=False))
t = check(d, BASE)
ok("skipped 1 pair" in t, "an open surface is reported as not tested", t)

# ---- hardware plausibility ----
HW = {"parent": "B", "brief": "seeded", "hardware": {"Anchor": {"items": {"name": ["anchor*"]}, "joins": ["Piers", "Girders"],
      "past": {"of": "Girders", "by": 0.05, "axis": "z"}}}}
def bolted(top):
    d = building()
    d.add("B::Hardware", "anchor 1", box((0.15, 0.15, 0.5), (0.2, 0.2, top)))
    return d
t = check(bolted(1.29), HW)
ok(status(t) == "status=fail" and "extends" in t, "a bolt that stops short of the top fails", t)
t = check(bolted(1.4), HW)
ok(status(t) == "status=pass", "a bolt past the top passes", t)
ok("plausibility only" in line(t, "PASS  hardware Anchor"), "the report says plausibility only", t)
d = building()
d.add("B::Hardware", "anchor 2", box((6, 6, 0), (6.05, 6.05, 1)))
t = check(d, dict(HW, hardware={"Anchor": dict(HW["hardware"]["Anchor"], past=None)}))
ok("does not reach" in t, "a connector touching nothing fails", t)
d = building()
d.add("B::Hardware", "anchor placeholder 1", box((0.15, 0.15, 0.5), (0.2, 0.2, 1.0)))
PH = {"parent": "B", "brief": "seeded", "hardware": {"Anchor": {"items": {"name": ["anchor*"]}, "placeholder": True}}}
t = check(d, PH)
ok(status(t) == "status=pass" and "no connection was checked" in t, "a named placeholder passes and says nothing was checked", t)
d = building()
d.add("B::Hardware", "anchor 1", box((0.15, 0.15, 0.5), (0.2, 0.2, 1.0)))
t = check(d, PH)
ok(status(t) == "status=fail", "an unmarked placeholder fails", t)

# ---- the report states what was and was not checked ----
t = check(building(), {"parent": "B", "brief": "seeded", "layers": {"Piers": {"min": 1, "max": 1}}})
s = line(t, "Requirements:")
ok("not checked: clashes, connectivity, connections, structure, code compliance" in s, "absent checks are named", s)
ok(s.startswith("Requirements: ") and "/" in s and " met \u00b7 " in s and "checks met" not in s, "the line reads plainly: score met, then dot-separated parts", s)
ok("A passing score means only" in t, "a full score is not assurance", t)
t = check(building(), BASE)
ok("not checked: connections, structure" in line(t, "Requirements:"), "only the checks not asked for are named", t)
ok(line(t, "Checked:").count("clashes") == 1 and "connectivity" in line(t, "Checked:"), "checked kinds listed", t)

# ---- the misleading unsaved label ----
d = building()
t = check(d, BASE)
ok("unsaved" not in line(t, "Requirements:") and "untitled" in line(t, "Requirements:"), "untitled is not called unsaved", t)
d = building(); d.Path = "/x/a.3dm"; d.Modified = False
ok("saved to a.3dm" in line(check(d, BASE), "Requirements:"), "a saved file is named")
d = building(); d.Path = "/x/a.3dm"; d.Modified = True
ok("unsaved changes to a.3dm" in line(check(d, BASE), "Requirements:"), "an edited file says so")

# ---- requirements changed after the model exists ----
req = {"parent": "B", "brief": "seeded", "extent": {"Piers": {"size_z": [0.9, 1.1]}}}
d2 = Doc(); d2.layer("B")
run(d2, req, "write")
d2.add("B::Piers", "pier 1", box((0, 0, 0), (0.4, 0.4, 1.0)))
txt = run(d2)
ok("written after geometry existed" not in txt, "requirements first, no flag", txt)
loose = dict(req, change="relaxed to fit", extent={"Piers": {"size_z": [0.1, 5.0]}})
w = run(d2, dict(loose), "write")
ok("written after geometry existed" in w, "write mode flags the change", w)
txt = run(d2)
ok("rev 2 written after geometry existed" in txt and "relaxed to fit" in txt, "check lists it with its reason", txt)
ok("1 revision written after geometry" in line(txt, "Check notes") and "after geometry" not in line(txt, "Requirements:"), "a self-made change goes to the check notes, not the reader's line", txt)

d3 = Doc(); d3.layer("B")
run(d3, {"parent": "B", "brief": "seeded", "extent": {"Piers": {"size_z": [0.9, 1.1]}}}, "write")
d3.add("B::Piers", "pier 1", box((0, 0, 0), (0.4, 0.4, 1.0)))
run(d3)
w = run(d3, {"parent": "B", "brief": "seeded", "change": "user correction: taller", "extent": {"Piers": {"size_z": [1.9, 2.1]}}}, "write")
txt = run(d3)
ok("rev 2 written after geometry" in txt and "after geometry existed" not in line(txt, "Requirements:") and "Check notes" not in txt, "a user correction is listed but not raised in the notes", txt)

d4 = Doc(); d4.layer("B")
d4.add("B::Piers", "pier 1", box((0, 0, 0), (0.4, 0.4, 3.0)))
txt = check(d4, {"parent": "B", "brief": "seeded", "extent": {"Piers": {"size_z": [0.9, 1.1]}}})
ok("FAIL  extent Piers" in txt and "rev 1 written after geometry" in txt, "requirements written after geometry are flagged", txt)
w = run(d4, {"parent": "B", "brief": "seeded", "change": "user correction: taller piers", "extent": {"Piers": {"size_z": [0.1, 5.0]}}}, "write")
txt = run(d4)
ok("was failing: extent Piers" in txt and "2 revisions written" in line(txt, "Check notes"), "changing a failing check is raised even when called a correction", txt)

# ---- count ranges ----
t = check(building(), {"parent": "B", "brief": "seeded", "layers": {"Piers": {"min": 1, "max": 400}}})
ok("count range too wide" in t and "1 count range too wide" in line(t, "Check notes") and "too wide" not in line(t, "Requirements:"), "a wide range is flagged in the notes", t)
t = check(building(), {"parent": "B", "brief": "seeded", "layers": {"Piers": {"min": 1, "max": 1, "derived": "one pier in this layout"}}})
ok("too wide" not in t and "one pier in this layout" in t, "a derived count is tight and shown", t)

# ---- a count derived from a form that later moved ----
DERIVED = {"parent": "B", "brief": "seeded", "layers": {"Ribs": {"min": 2, "max": 2, "derived": "2 ribs at 2 m"}}}
def ribbed(last, name="rib 2"):
    d = Doc(); d.layer("B")
    d.add("B::Ribs", "rib 1", box((0, 0, 0), (0.1, 0.1, 3)))
    d.add("B::Ribs", name, box((last, 0, 0), (last + 0.1, 0.1, 3)))
    return d
def reform(d, last):
    """Rebuild rib 2 at a new position in the same document, as a generator rerun does."""
    d.Objects[1:] = []
    d.add("B::Ribs", "rib 2", box((last, 0, 0), (last + 0.1, 0.1, 3)))
d = ribbed(2.0)
t = check(d, DERIVED)
ok(status(t) == "status=pass" and "may be stale" not in t, "the first check of a revision records the size and does not flag", t)
ok(json.loads(run_doc_result(d))["derived_sizes"]["Ribs"] == [2.1, 0.1, 3], "the layer's size is stored with the result", run_doc_result(d))
t = run(d)
ok("may be stale" not in t, "an unchanged form is not flagged", t)
reform(d, 1.5)
t = run(d)
ok(status(t) == "status=pass", "a pinned count still passes, so the flag is the only sign of it", t)
ok("flag: layer Ribs changed size since rev 1 was first measured (2.1 x 0.1 x 3 to 1.6 x 0.1 x 3)" in t and "2 ribs at 2 m" in t, "a derived count whose layer moved is flagged, with its note", t)
ok("1 derived count may be stale" in line(t, "Check notes") and "stale" not in line(t, "Requirements:"), "the flag reaches the check notes, not the reader's line", t)
ok("never set a constant to keep the old count" in t, "the flag states the rule", t)
t = run(d)
ok("(2.1 x 0.1 x 3 to 1.6 x 0.1 x 3)" in t, "the comparison stays against the first measurement of the revision", t)
w = run(d, dict(DERIVED, change="form change: last rib moved", layers={"Ribs": {"min": 2, "max": 2, "derived": "2 ribs at 1.5 m"}}), "write")
ok("written after geometry existed" in w, "the new revision is itself reported as written after geometry", w)
ok("if the design changed, keep it and report it" in w, "the write flag does not tell the agent to undo a revision for a design change", w)
t = run(d)
ok("may be stale" not in t and "rev 2 written after geometry" in t, "a new revision clears the flag and stays listed", t)
ok("2 revisions written after geometry" in line(t, "Check notes"), "a form change the agent made reaches the check notes (rev 1 too: this seeded case writes it after building)", t)
d = ribbed(2.0)
check(d, DERIVED)
reform(d, 2.005)
ok("may be stale" not in run(d), "a small adjustment under 1% is not flagged")
d = ribbed(2.0)
check(d, {"parent": "B", "brief": "seeded", "layers": {"Ribs": {"min": 2, "max": 2}}})
reform(d, 1.5)
ok("may be stale" not in run(d), "a count with no derived note is out of the flag's reach")
d = Doc(); d.layer("B"); d.layer("B::Ribs")
d.add("B::Piers", "pier 1", box((0, 0, 0), (0.4, 0.4, 1.0)))
check(d, dict(DERIVED, layers={"Ribs": {"min": 0, "max": 0, "derived": "none yet", "match": ["Ribs"]}, "Piers": {"min": 1, "max": 1}}))
ok("Ribs" not in json.loads(run_doc_result(d))["derived_sizes"], "a layer with nothing on it has no size to compare", run_doc_result(d))

# ---- inside, and a point exactly on a joint ----
def panels():
    """Four solids meeting at x=1, y=1, all touching, plus a lone block with a 0.01 gap to a neighbour."""
    d = Doc(); d.layer("B")
    d.add("B::Panels", "panel a", box((0, 0, 0), (1, 1, 1)))
    d.add("B::Panels", "panel b", box((1, 0, 0), (2, 1, 1)))
    d.add("B::Panels", "panel c", box((0, 1, 0), (1, 2, 1)))
    d.add("B::Panels", "panel d", box((1, 1, 0), (2, 2, 1)))
    d.add("B::Panels", "block e", box((5, 0, 0), (6, 1, 1)))
    d.add("B::Panels", "block f", box((6.01, 0, 0), (7, 1, 1)))
    return d
def inside(points):
    d = panels()
    t = check(d, {"parent": "B", "brief": "seeded", "inside": {"Panels": {"points": points}}})
    return line(t, "PASS  inside Panels" if "PASS  inside Panels" in t else "FAIL  inside Panels").strip()
l = inside([[0.5, 0.5, 0.5]])
ok(l.startswith("PASS") and "on_joint" not in l, "a point inside a solid passes and is not called a joint", l)
l = inside([[1, 0.5, 0.5]])
ok(l.startswith("PASS") and '"on_joint": [[1, 0.5, 0.5]]' in l, "a point on a joint between two solids passes and is named", l)
l = inside([[1, 1, 0.5]])
ok(l.startswith("PASS") and "on_joint" in l, "a point where four solids meet passes", l)
l = inside([[0, 0.5, 0.5]])
ok(l.startswith("FAIL") and "[0, 0.5, 0.5]" in l, "a point on the outer skin of one solid still fails", l)
l = inside([[1, 0.5, 1]])
ok(l.startswith("FAIL"), "a point on the outer edge of a joint still fails: a step outward leaves the solids", l)
l = inside([[6.005, 0.5, 0.5]])
ok(l.startswith("FAIL"), "a point in a real gap between solids fails", l)
l = inside([[9, 9, 9]])
ok(l.startswith("FAIL"), "a point far outside fails", l)

# ---- local code ----
t = check(building(), {"parent": "B", "brief": "seeded", "code": {"jurisdiction": "Example County", "used": "2010 ADA Standards", "status": "stand-in"}})
ok("2010 ADA Standards is a stand-in: no local code for Example County" in line(t, "Requirements:"), "a stand-in is on the status line", t)
w = run(building(), {"parent": "B", "brief": "seeded", "sources": {"x": "ADA 604.4"}}, "write")
ok("sources cite a code" in w, "a cited code without 'code' is flagged", w)

# ---- machine line and list mode are unchanged ----
t = check(building(), BASE)
ok(line(t, "ASCHECK").startswith("ASCHECK status=pass checks="), "ASCHECK line keeps its format", t)
d = building(); run(d, dict(BASE), "write"); l = run(d, None, "list")
ok("clash Cold" in l and "declared connection: cold riser* to tank*" in l, "list mode shows clash and declarations", l)

# ---- the status line counts what was not measured; the report keeps the items ----
import importlib.util
items = ["item %02d: not modeled" % i for i in range(26)]
d = building()
w = run(d, dict(BASE, stated=items), "write")
t = run(d)
s = line(t, "Requirements:")
ok("26 not measured" in s and "see report" not in s and "item 00" not in s, "the status line gives a count, not the items", s)
ok(sum("not measured: item" in l for l in t.splitlines()) == 26, "every item stays in the full report", t)
HARVEST = Path.cwd() / "maintainers/rhino-lessons/as-harvest-lessons.py"
if HARVEST.exists():  # maintainer tooling; not part of the public package
    spec = importlib.util.spec_from_file_location("harvest", HARVEST)
    harvest = importlib.util.module_from_spec(spec); spec.loader.exec_module(harvest)
    m = harvest.ASCHECK.search(t)
    ok(m is not None and m.group(1) == "pass" and m.group(4) == "26", "the harvester still reads ASCHECK", t)
    m = harvest.SAVED.search(w)
    ok(m is not None and m.group(3) == "26", "the harvester still reads ASREQUIREMENTS saved", w)
s = line(check(building(), BASE), "Requirements:")
ok("not measured" not in s, "nothing not measured, nothing on the status line", s)

# ---- within: a run against inline set-out boxes (rhino-agent-team) ----
def team_doc():
    d = building()
    d.add("B::Supply", "supply riser", box((10, 0, 0), (10.3, 0.3, 3)))        # in the shaft share
    d.add("B::Supply", "supply main", box((10.3, 0, 2.6), (14, 0.3, 2.9)))     # in the ceiling lane share
    return d

SHARES = [[9.9, -0.1, -0.1, 10.4, 0.4, 3.1], [10.2, -0.1, 2.5, 14.1, 0.4, 3.0]]   # two boxes: shaft and lane
OTHER = [[11, 0.5, 0, 12, 1.5, 3]]                                                 # another owner's share
WITHIN = dict(BASE, within={"Supply": {"boxes": SHARES, "avoid": OTHER, "min_section": 0.25}},
              sources={"within Supply": "set-out rev 3"})
t = check(team_doc(), WITHIN)
ok(status(t) == "status=pass" and "PASS  within Supply" in t, "within: runs inside a share of two boxes pass", t)
d = team_doc(); d.add("B::Supply", "supply branch", box((10.3, 0.3, 2.6), (10.6, 2.0, 2.9)))
t = check(d, WITHIN)
ok(status(t) == "status=fail" and "outside every share: supply branch" in t, "within: a run outside a multi-box share fails", t)
d = team_doc(); d.add("B::Supply", "supply stub", box((11.2, 0.3, 1.0), (11.5, 0.8, 1.3)))
t = check(d, dict(WITHIN, within={"Supply": {"avoid": OTHER}}))
ok(status(t) == "status=fail" and "in another owner's share [0]: supply stub" in t, "within: a run in another owner's share fails", t)
d = team_doc(); d.add("B::Supply", "supply touching", box((10.7, 0.3, 1.0), (11.0, 0.8, 1.3)))
t = check(d, dict(WITHIN, within={"Supply": {"avoid": OTHER}}))
ok("PASS  within Supply" in t, "within: touching another owner's share is not entering it", t)
d = team_doc(); d.add("B::Supply", "supply thin", box((10.0, 0.0, 0.5), (10.1, 0.3, 1.0)))
t = check(d, WITHIN)
ok(status(t) == "status=fail" and "undersized: supply thin" in t, "within: an undersized run fails", t)
d = building()
t = check(d, WITHIN)
ok("within Supply" in t and status(t) == "status=fail", "within: a layer with nothing on it is not a pass", t)
# No set-out: nothing changes for a single agent.
plain = check(building(), BASE)
ok("within" not in plain and status(plain) == "status=pass", "within: absent for a single agent with no set-out", plain)
ok("set-out shares and sizes" not in line(plain, "Requirements:"), "within: the status line is unchanged without a set-out", line(plain, "Requirements:"))

# ---- the stored result: requirements revision and a geometry fingerprint that survives saving ----
d = building()
check(d, BASE)
stored = json.loads(run_doc_result(d))
ok(stored.get("rev") == 1 and str(stored.get("geom_fp", "")).startswith("g1-"), "fingerprint: stored with the result and the revision", stored)
team_ns = {"AS_SCRIPT_FILE": "as-agent-team.py"}
exec(compile((Path.cwd() / "skills/rhino-agent-team/scripts/as-agent-team.py").read_text(), "as-agent-team.py", "exec"), team_ns)
rows = [(str(o.Id), d.Layers[o.Attributes.LayerIndex].FullPath,
         (o.Geometry.bb.Min.X, o.Geometry.bb.Min.Y, o.Geometry.bb.Min.Z, o.Geometry.bb.Max.X, o.Geometry.bb.Max.Y, o.Geometry.bb.Max.Z)) for o in d.Objects]
ok(team_ns["geometry_fp"](rows) == stored["geom_fp"], "fingerprint: the team check computes the same value from the same objects", rows[:2])
before = stored["geom_fp"]
d.add("Notes", "reply", Point(Point3d(1, 1, 1)))
fp_after_note = team_ns["geometry_fp"](rows + [("id-note", "Notes", (1, 1, 1, 1, 1, 1))])
ok(fp_after_note == before, "fingerprint: a note added after the check leaves it unchanged")
moved = [r if r[1] != "B::Tank" else (r[0], r[1], tuple(v + 0.01 for v in r[2])) for r in rows]
ok(team_ns["geometry_fp"](moved) != before, "fingerprint: moving one object changes it")
ok(team_ns["geometry_fp"](rows + [("id-new", "B::Cold", (0, 0, 0, 1, 1, 1))]) != before, "fingerprint: adding an object changes it")

# ---- envelope and hardware: proportion, cover, bears ----
def wall():
    """A wall face across y with siding courses around an opening, a sill and two casing legs, and sealant."""
    d = Doc()
    d.layer("W")
    for z in range(0, 10):                                   # siding courses 1 high from x 0 to 10
        if 3 <= z < 7:                                       # beside the opening: left and right pieces
            d.add("W::Siding", "board %d left" % z, box((0, -1, z), (3, 0, z + 1)))
            d.add("W::Siding", "board %d right" % z, box((7, -1, z), (10, 0, z + 1)))
        else:
            d.add("W::Siding", "board %d" % z, box((0, -1, z), (10, 0, z + 1)))
    d.add("W::Frame", "sill", box((2.5, -1.5, 2.5), (7.5, 3, 3)))   # its nose runs under both casing legs
    d.add("W::Trim", "casing left", box((2.5, -1.5, 3), (3, -1, 7)))
    d.add("W::Trim", "casing right", box((7, -1.5, 3), (7.5, -1, 7)))
    d.add("W::Sealant", "sealant bead 1", box((3, -0.5, 3), (3.5, -0.25, 7)))   # 0.5 wide, 0.25 deep
    return d

ENV = {"parent": "W", "brief": "seeded envelope", "units": "Meters",
       "proportion": {"Sealant": {"items": {"layer": "Sealant", "name": ["*bead*"]}, "axis": "y", "ratio": [0.4, 0.75]}},
       "cover": {"Siding": {"items": "Siding", "axis": "y", "region": [[0, 0], [10, 10]], "holes": [[[3, 3], [7, 7]]], "step": 0.5}},
       "bears": {"Casing legs": {"items": {"layer": "Trim", "name": ["casing*"]}, "on": [{"name": ["sill"]}, "Siding"]}}}
t = check(wall(), ENV)
ok(status(t) == "status=pass", "a clean envelope passes proportion, cover and bears", t)
d = wall()
d.Objects[:] = [o for o in list.__iter__(d.Objects) if o.Attributes.Name not in ("board 7", "board 8")]   # siding missing above the head
t = check(d, ENV)
ok(status(t) == "status=fail" and "FAIL  cover Siding" in t, "missing courses above an opening fail cover", t)
ok("uncovered" in line(t, "FAIL  cover Siding"), "the cover failure says where", t)
d = wall()
d.add("W::Sealant", "sealant bead 2", box((6.5, -0.8, 3), (6.8, 0, 7)))   # 0.3 wide, 0.8 deep: deeper than wide
t = check(d, ENV)
ok("FAIL  proportion Sealant" in t and "sealant bead 2" in t, "a joint deeper than wide fails proportion", t)
d = wall()
for o in list.__iter__(d.Objects):
    if o.Attributes.Name == "casing left":
        o.Geometry = box((2.5, -1.5, 3.2), (3, -1, 7))         # stops short of the sill: a gap under its foot
t = check(d, ENV)
ok("FAIL  bears Casing legs" in t and "casing left" in t, "a leg stopping short of its sill fails bears", t)
flat = dict(ENV, bears={"Sill": {"items": {"name": ["sill"]}}})
t = check(wall(), flat)
ok("NOT MEASURED" in t or "FAIL  bears Sill" in t, "a member that is not taller than wide is skipped, so nothing is tested", t)

# ---- a measured run: a head flashing through the barrier and a siding course ----
def head():
    """Barrier and sheathing across y, a siding course, and a head flashing over the opening that laps the barrier."""
    d = Doc()
    d.layer("H")
    d.add("H::Sheathing", "sheathing", box((0, 0, 0), (10, 0.5, 10)))
    d.add("H::Barrier", "weather-resistive barrier", box((0, -0.1, 0), (10, 0, 10)))
    d.add("H::Siding", "lap siding course 15 mid", box((0, -1, 7.2), (10, -0.1, 8.2)))
    d.add("H::Flashing", "head flashing", box((2.5, -1.2, 7), (7.5, -0.1, 7.2)))   # on the barrier face, under the course
    return d

HEAD = {"parent": "H", "brief": "seeded head", "units": "Meters", "closed": ["Flashing", "Barrier"],
        "clash": {"Flashing": {"against": ["Barrier", "Sheathing", "Siding"]}}}
t = check(head(), HEAD)
ok(status(t) == "status=pass", "a head flashing that only touches the layers it laps passes", t)
d = head()
for o in list.__iter__(d.Objects):
    if o.Attributes.Name == "head flashing":
        o.Geometry = box((2.5, -1.2, 7), (7.5, 0.3, 7.4))   # through the barrier into the sheathing, and up into the course
t = check(d, HEAD)
ok(status(t) == "status=fail" and "FAIL  clash Flashing" in t, "a head flashing through the barrier and the siding fails clash", t)
ok('"clashes": 3' in line(t, "FAIL  clash Flashing"), "each layer it passes through is a clash", line(t, "FAIL  clash Flashing"))
d = head()
for o in list.__iter__(d.Objects):
    if o.Attributes.Name == "head flashing":
        o.Geometry = box((2.5, -1.2, 7), (7.5, 0.3, 7.4), solid=False)   # the same, left as an open polysurface
t = check(d, HEAD)
ok("FAIL  closed Flashing" in t, "an open flashing fails closed, so the clash it hides is not passed silently", t)
ok("skipped" in t, "the clash check says the open flashing was not tested", t)
c = next(l for l in t.splitlines() if "clash Flashing" in l)
ok(c.strip().startswith("NOT MEASURED") and "every overlapping pair was skipped" in t and status(t) == "status=fail", "a clash entry whose every overlapping pair was skipped is not measured, and fails", t)
def open_head():
    d = head()
    for o in list.__iter__(d.Objects):
        if o.Attributes.Name == "head flashing":
            o.Geometry = box((2.5, -1.2, 7), (7.5, 0.3, 7.4), solid=False)
    return d
t = check(open_head(), dict(HEAD, closed=["Barrier"]))
c = next(l for l in t.splitlines() if "clash Flashing" in l)
ok(c.strip().startswith("NOT MEASURED") and status(t) == "status=fail", "with flashing left out of closed, the all-skipped clash still fails the run", t)
d = head()
d.add("H::Flashing", "drip edge", box((2.5, -1.5, 6.8), (7.5, -1.2, 7.0)))    # a closed flashing that touches nothing overlapping
for o in list.__iter__(d.Objects):
    if o.Attributes.Name == "head flashing":
        o.Geometry = box((2.5, -1.2, 7), (7.5, 0.3, 7.4), solid=False)
d.add("H::Flashing", "sill pan", box((2.5, -0.5, 2.9), (7.5, 0.2, 3.0)))    # closed, through the barrier: decided
t = check(d, dict(HEAD, closed=["Barrier"]))
c = next(l for l in t.splitlines() if "clash Flashing" in l)
ok(c.strip().startswith("FAIL") and "skipped" in t, "when some pairs are decided, the clash is measured and the skipped ones are still listed", t)

# ---- an undecided pair passes and is reported as undecided ----
class Thin(Brep):
    """Overlapping boxes, no sample point inside both, and a boolean that gives nothing: Rhino on touching faces."""
    def IsPointInside(self, p, tol, strict):
        return False
d = head()
d.add("H::Flashing", "drip edge", Thin((2.5, -1.2, 6.9), (7.5, -0.05, 7.1)))
real_boolean = Brep.CreateBooleanIntersection
Brep.CreateBooleanIntersection = staticmethod(lambda a, b, tol: None if isinstance(a, Thin) or isinstance(b, Thin) else real_boolean(a, b, tol))
t = check(d, HEAD)
Brep.CreateBooleanIntersection = staticmethod(real_boolean)
c = next(l for l in t.splitlines() if "clash Flashing" in l)
ok(c.strip().startswith("PASS") and '"undecided": 1' in c, "an undecided pair passes and is counted as undecided", t)
ok("undecided: drip edge x lap siding course 15 mid" in t or "undecided: drip edge x weather-resistive barrier" in t, "the undecided pair is named in the output", t)

# ---- objects added while a layout was the active view are on its page, not in the model ----
d = building()
t = check(d, BASE)
ok(status(t) == "status=pass" and "baseline model space" in t, "model-space baseline runs and passes on a model built in model space", t)
for o in list.__iter__(d.Objects):
    o.Attributes.Space = "PageSpace"   # str() of Rhino's ActiveSpace.PageSpace
t = run(d)
ok(status(t) == "status=fail" and line(t, "FAIL  baseline model space"), "every part on a layout's page fails the check", t)
d = building()
list.__getitem__(d.Objects, 0).Attributes.Space = "PageSpace"
t = check(d, BASE)
ok(status(t) == "status=fail" and "pier 1" in line(t, "FAIL  baseline model space"), "one part in page space fails and is named", t)

print("rhino-model checks: %d seeded assertions passed (stub geometry, not Rhino)" % passed)
PY
