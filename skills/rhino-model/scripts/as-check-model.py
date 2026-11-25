"""Deterministic model checker: measures the open document against a requirements file.

Used by the requirements check (as-check.py, requirements stored in the .3dm) and by the rhino-modeling
evals (expected/*.json). Same format for both.

Runs inside Rhino, not on the grader's machine: paste it into Rhino's
`run_python` tool with CASE set to an expected/*.json path, or run
    CASE = "<abs path>/expected/<case>.json"; exec(open("<abs path>/as-check-model.py").read(), globals())
It reads the live
document through the injected `__rhino_doc__` handle and prints one JSON verdict.
No installs; RhinoCommon and the standard library only.

Checks (each optional in the expected file):
  units         document unit system name
  parent        parent layer exists
  layers        per child layer: object type and count range. A child is found by
                keyword, not exact name: any layer under the parent whose path
                contains one of its `match` words (default: the key) and none of
                its `exclude` words, any case. If no child layer matches, objects
                of the child's `type` anywhere under the parent are used instead,
                since briefs name the parent layer but not its children
  bbox          parent-layer bounding-box size within tol
  named         every object under the parent has a non-empty name
  valid         every object's geometry IsValid
  closed        breps on these child layers are closed solids
  objects       objects on a child layer and/or matching name globs (any case)
                -> bbox size within tol (standards dimensions); `oriented`
                measures a rotated box by its own sorted edge lengths instead
  extent        per child layer, the combined bounding box of its objects against
                [lo, hi] ranges (inclusive; null for an open end) on any of min_x,
                max_x, min_y, max_y, min_z, max_z, size_x, size_y, size_z, mid_x,
                mid_y, mid_z (centre lines, e.g. "to the centerline of the dispenser"). Code
                ranges and one-sided limits ("16-18 in", "54 in min") read directly
  bond          points on a layer grouped into courses of height `course`;
                consecutive courses must start at different stations
  spacing       vertical lines on a layer, grouped by wall and start height,
                gap between neighbours <= max; `openings` gaps may exceed it
  points        expected coordinates; each needs a point on the child layer within tol
  grid          points on a child layer form an nx by ny grid at dx, dy spacing
  props         per object on a child layer: closed, planar, area, length,
                length_in (allowed lengths), volume, inner_loops, arc_radius;
                area and volume use relative tolerance rtol (default 0.001);
                ruled (one isocurve family is straight lines), gaussian_min and
                gaussian_max (Gaussian curvature sampled on a 12 by 12 grid),
                gaussian_mixed (both signs present)
  centroids     each expected [x, y, z] is the volume (or area) centroid of one
                object on the child layer within tol, and the counts match
  on_surface    every curve on the child layer lies within tol of the breps on
                the `surface` child layer (11 samples per curve)
  heights       at each expected [x, y, z], a vertical line through (x, y) meets
                the child layer's surfaces with its highest hit at z within tol
  clear         each [[x0,y0,z0],[x1,y1,z1]] segment misses every brep on the child
                layer (openings really go through)
  inside        each [x, y, z] lies inside a closed brep on the child layer. A point exactly
                on a joint between solids that touch counts as inside when every
                direction from it stays in one of them; a point on the outer skin, or
                on a joint with a real gap, does not. Joint points are listed as on_joint
  subd          objects on the child layer are SubD with the given faces and
                vertices; closed means the limit surface converts to a solid
  slider_response  in the graded GH document, set a slider (nickname contains
                `slider`, any case) to `set`, re-solve, and require some output
                parameter to hold `points` points or a brep matching `brep`
                (area, inner_loops); the slider is restored afterwards
  within        per child layer, every object's bounding box against inline boxes from a set-out
                (rhino-agent-team): {"Supply": {"boxes": [[x0,y0,z0,x1,y1,z1], ...], "avoid": [[...]],
                "min_section": 6}}. Each object must lie inside one of `boxes` (its owner's shares and
                the space the set-out leaves free), share no volume with any `avoid` box (another
                owner's share; touching is not entering), and have no bounding-box side shorter than
                `min_section`. `tol` (default 10x the document tolerance) is allowed on every side.
                Each key is optional; objects that are not runs belong on another child layer
  clash         overlaps between a group and others: {"Plumbing": {"against": ["Piers",
                "Girders"]}} (`against` omitted: everything else under the parent).
                Solids and centreline curves are tested; an open surface or mesh is
                skipped and counted (an entry whose overlapping pairs were all
                skipped is not measured, and fails), and a pair that cannot be
                decided passes and is listed as `undecided: a x b`.
                Touching faces are not a clash. `tol` is the overlap depth ignored
                (default the document tolerance). The top-level `intended` list
                excuses declared pairs: [{"a": "cold riser*", "b": "tank*", "why":
                "riser feeds the tank"}]; a and b are object-name globs, `why` is
                required and a bare wildcard is refused. Each excused pair is printed.
                Each result gives the members matched on each side and the pairs tested.
                A side that matches nothing is never a pass: it fails when the requirement
                names objects expected to exist (a name glob, or a layer word whose `layers`
                entry does not allow zero) and is otherwise not measured (`not_measured`,
                still `pass: false`). Members on both sides with no boxes overlapping is a
                valid pass with 0 pairs tested, and the output says so
  network       every fixture reaches a sink through connected pipes:
                {"Drain": {"pipes": ["Drain"], "fixtures": {"name": ["basin*"]},
                "to": {"name": ["sump*"]}}}. Pieces connect when they touch or
                overlap within `tol` (default 10x the document tolerance). Fails on a
                fixture that does not reach the sink and on a pipe not connected to it
  hardware      connection plausibility for bolts, hangers and ties:
                {"Anchor": {"items": {"name": ["anchor*"]}, "joins": ["Pier", "Girder"],
                "past": {"of": "Girder", "by": 0.05, "axis": "z"}}}: each item must touch
                every `joins` group and extend `by` beyond the `of` members it touches.
                {"placeholder": true} instead only requires "placeholder" in the name.
                A pass is plausibility, not engineering: strength, nuts and washers,
                and a bolt lying in a seam between plies are not detected
                For clash, network and hardware, a selector is a layer word (a string,
                using `layers` match words when defined) or {"layer": ..., "name":
                [globs]}. They see hidden and locked objects, and a selector that
                matches nothing never passes with nothing to test
  proportion    each item's size along `axis` over the smaller of its other two sizes lies in
                `ratio` [lo, hi]: {"Sealant": {"items": {"layer": "Sealant", "name": ["*bead*"]},
                "axis": "y", "ratio": [0.4, 0.75]}} (a sealant joint about half as deep as wide)
  cover         the items cover a face region with no gap: {"Siding": {"items": "Siding", "axis": "y",
                "region": [[u0, v0], [u1, v1]], "holes": [[[u0, v0], [u1, v1]]], "step": 1.0}}. The face
                is the plane across `axis`, u and v are the other two axes in order (x, y, z); points on
                a `step` grid inside the region and outside the holes must fall within some item's
                extent. Catches cladding or flashing that stops short of an opening, or a missing course
  bears         vertical members (taller than wide) sit on material across their whole footprint:
                {"Casing legs": {"items": {"layer": "Trim", "name": ["*casing*"]}, "on": ["Frame"]}}.
                A 3 x 3 grid just under each member's bottom must be inside a solid (`on`, else
                anything under the parent). Catches a leg or jamb cut flat over a sloped sill. Members
                not taller than wide are skipped and counted
  gh            open Grasshopper documents: the one holding the most required
                components is graded for slider count, missing components and
                components at error level
"""
import fnmatch
import json

import Rhino
import System

CASE = globals().get("CASE", "/path/to/expected/case.json")  # set before exec, or edit here

d = __rhino_doc__  # noqa: F821  (injected by Rhino's run_python script runner)
exp = json.load(open(CASE))
res = []
derived_sizes = {}  # layer -> overall size, for counts with a `derived` note; as-check.py compares revisions of it


def check(name, ok, actual, expected=None, not_measured=False):
    res.append({"check": name, "pass": bool(ok), "actual": actual, "expected": expected})
    if not_measured:
        res[-1]["not_measured"] = True


def objs_under(path):
    out = []
    for o in d.Objects:  # live objects only; deleted objects are not enumerated
        lp = d.Layers[o.Attributes.LayerIndex].FullPath
        if lp == path or lp.startswith(path + "::"):
            out.append((lp, o))
    return out


def on(child):
    """Objects on every child layer whose path below the parent contains a match word."""
    spec = exp.get("layers", {}).get(child, {})
    words = [w.lower() for w in spec.get("match", [child])]
    skip = [w.lower() for w in spec.get("exclude", [])]
    hit = lambda sub: any(w in sub for w in words) and not any(w in sub for w in skip)
    found = [o for lp, o in allobjs if lp != parent and hit(lp[len(parent) + 2:].lower())]
    if found or any(lp != parent and hit(lp[len(parent) + 2:].lower()) for lp in layer_paths):
        return found
    return [o for _, o in allobjs if "type" not in spec or str(o.ObjectType) == spec["type"]]


def size(bb):
    return [round(bb.Max.X - bb.Min.X, 3), round(bb.Max.Y - bb.Min.Y, 3), round(bb.Max.Z - bb.Min.Z, 3)]


def within(a, e, tol):
    return all(abs(x - y) <= tol for x, y in zip(a, e))


parent = exp["parent"]
if "units" in exp:
    check("units", str(d.ModelUnitSystem) == exp["units"], str(d.ModelUnitSystem), exp["units"])
check("parent", d.Layers.FindByFullPath(parent, -1) >= 0, parent)
allobjs = objs_under(parent)
layer_paths = [l.FullPath for l in d.Layers if not l.IsDeleted and l.FullPath.startswith(parent + "::")]

for child, spec in exp.get("layers", {}).items():
    items = on(child)
    kinds = sorted({str(o.ObjectType) for o in items})
    n = len(items)
    ok = spec["min"] <= n <= spec["max"] and (not spec.get("type") or kinds == [spec["type"]])
    check("layer " + child, ok, {"count": n, "types": kinds}, spec)
    if spec.get("derived") and items:
        layer_box = Rhino.Geometry.BoundingBox.Empty
        for o in items:
            layer_box.Union(o.Geometry.GetBoundingBox(True))
        derived_sizes[child] = size(layer_box)

if "bbox" in exp:
    bb = Rhino.Geometry.BoundingBox.Empty
    for _, o in allobjs:
        bb.Union(o.Geometry.GetBoundingBox(True))
    s = size(bb)
    check("bbox", within(s, exp["bbox"]["size"], exp["bbox"]["tol"]), s, exp["bbox"])

if exp.get("named"):
    unnamed = sum(1 for _, o in allobjs if not (o.Attributes.Name or "").strip())
    check("named", unnamed == 0, {"unnamed": unnamed, "total": len(allobjs)})

if exp.get("valid", True):
    bad = sum(1 for _, o in allobjs if not o.Geometry.IsValid)
    check("valid", bad == 0, {"invalid": bad})

for child in exp.get("closed", []):
    open_ = [o.Attributes.Name for o in on(child)
             if hasattr(o.Geometry, "IsSolid") and not o.Geometry.IsSolid]
    check("closed " + child, not open_, open_)

for key, spec in exp.get("objects", {}).items():
    pool = on(spec["layer"]) if "layer" in spec else [o for _, o in allobjs]
    globs = [g.lower() for g in spec.get("name", ["*"])]
    hits = [o for o in pool if any(fnmatch.fnmatch((o.Attributes.Name or "").lower(), g) for g in globs)]
    if spec.get("oriented"):
        sizes = [sorted({round(e.GetLength(), 3) for e in o.Geometry.Edges}) if hasattr(o.Geometry, "Edges") else [] for o in hits]
        want = sorted(spec["size"])
        ok = len(hits) >= spec.get("count", 1) and all(len(s) == 3 and within(s, want, spec["tol"]) for s in sizes)
        shown = sorted({tuple(s) for s in sizes})[:5]
    else:
        sizes = [size(o.Geometry.GetBoundingBox(True)) for o in hits]
        ok = len(hits) >= spec.get("count", 1) and all(within(s, spec["size"], spec["tol"]) for s in sizes)
        shown = sizes[:20]
    check("object " + key, ok, {"count": len(hits), "sizes": shown}, spec)

AXES = {"min_x": lambda b: b.Min.X, "max_x": lambda b: b.Max.X, "min_y": lambda b: b.Min.Y,
        "max_y": lambda b: b.Max.Y, "min_z": lambda b: b.Min.Z, "max_z": lambda b: b.Max.Z,
        "size_x": lambda b: b.Max.X - b.Min.X, "size_y": lambda b: b.Max.Y - b.Min.Y,
        "size_z": lambda b: b.Max.Z - b.Min.Z, "mid_x": lambda b: (b.Min.X + b.Max.X) / 2,
        "mid_y": lambda b: (b.Min.Y + b.Max.Y) / 2, "mid_z": lambda b: (b.Min.Z + b.Max.Z) / 2}
for child, spec in exp.get("extent", {}).items():
    items = on(child)
    bb = Rhino.Geometry.BoundingBox.Empty
    for o in items:
        bb.Union(o.Geometry.GetBoundingBox(True))
    got, bad = {}, []
    for k, rng in spec.items():
        if k not in AXES:
            continue
        v = round(AXES[k](bb), 3) if items else None
        got[k] = v
        lo, hi = (list(rng) + [None, None])[:2]
        if v is None or (lo is not None and v < lo - 1e-6) or (hi is not None and v > hi + 1e-6):
            bad.append(k)
    check("extent " + child, not bad, {"measured": got, "count": len(items), "out_of_range": bad}, spec)


def box_of(o):
    b = o.Geometry.GetBoundingBox(True)
    return (b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z)


def box_inside(a, z, tol):
    return all(a[i] >= z[i] - tol for i in range(3)) and all(a[i] <= z[i] + tol for i in range(3, 6))


def box_enters(a, z, tol):
    return all(min(a[i + 3], z[i + 3]) - max(a[i], z[i]) > tol for i in range(3))


for child, spec in exp.get("within", {}).items():
    items = on(child)
    tol = spec.get("tol", d.ModelAbsoluteTolerance * 10)
    boxes, avoid, least = spec.get("boxes"), spec.get("avoid", []), spec.get("min_section")
    outside, entered, small, detail = [], [], [], []
    for o in items:
        name, bb = (o.Attributes.Name or "") or str(o.Id)[:8], box_of(o)
        if boxes and not any(box_inside(bb, z, tol) for z in boxes):
            outside.append(name)
            detail.append("outside every share: %s %s" % (name, [round(v, 3) for v in bb]))
        hit = [i for i, z in enumerate(avoid) if box_enters(bb, z, tol)]
        if hit:
            entered.append(name)
            detail.append("in another owner's share %s: %s" % (hit, name))
        if least is not None:
            side = min(bb[i + 3] - bb[i] for i in range(3))
            if side < least - tol:
                small.append(name)
                detail.append("undersized: %s, smallest side %.3f, minimum %s" % (name, side, least))
    if len(detail) > 20:
        detail = detail[:20] + ["... and %d more" % (len(detail) - 20)]
    check("within " + child, bool(items) and not (outside or entered or small),
          {"count": len(items), "outside": len(outside), "in_other_share": len(entered), "undersized": len(small), "detail": detail},
          spec, not_measured=not items)

if "bond" in exp:
    spec = exp["bond"]
    rows = {}
    for o in on(spec["layer"]):
        if hasattr(o.Geometry, "Location"):
            p = o.Geometry.Location
            rows.setdefault(int(round(p.Z / spec["course"] - 0.5)), []).append(p.X)
    ks = sorted(rows)
    starts = [round(min(rows[k]), 3) for k in ks]
    stacked = sum(1 for a, b in zip(starts, starts[1:]) if abs(a - b) < spec.get("min_offset", 0.5))
    check("bond", len(ks) > 1 and stacked == 0, {"courses": len(ks), "stacked_joints": stacked}, spec)

for child, spec in exp.get("spacing", {}).items():
    groups = {}
    for o in on(child):
        if not hasattr(o.Geometry, "PointAtStart"):
            continue
        a, b = o.Geometry.PointAtStart, o.Geometry.PointAtEnd
        if abs(a.X - b.X) > 0.01 or abs(a.Y - b.Y) > 0.01:
            continue  # not vertical
        z0 = round(min(a.Z, b.Z), 1)
        groups.setdefault(("x", round(a.X, 1), z0), []).append(a.Y)
        groups.setdefault(("y", round(a.Y, 1), z0), []).append(a.X)
    over = []
    for key, vals in groups.items():
        if len(vals) < 3:
            continue  # a single stud pair is not a wall run
        vals.sort()
        over += [round(q - p, 2) for p, q in zip(vals, vals[1:]) if q - p > spec["max"] + 0.01]
    check("spacing " + child, len(over) <= spec.get("openings", 0), {"gaps_over_max": over}, spec)

def pt_of(o):
    return o.Geometry.Location if hasattr(o.Geometry, "Location") else None


for child, spec in exp.get("points", {}).items():
    pts = [p for p in (pt_of(o) for o in on(child)) if p is not None]
    missing = [a for a in spec["at"] if not any(p.DistanceTo(Rhino.Geometry.Point3d(*a)) <= spec.get("tol", 0.01) for p in pts)]
    check("points " + child, not missing, {"points": len(pts), "missing": missing}, spec)

for child, spec in exp.get("grid", {}).items():
    pts = [p for p in (pt_of(o) for o in on(child)) if p is not None]
    t = spec.get("tol", 0.01)
    xs = sorted({round(p.X / t) * t for p in pts}); ys = sorted({round(p.Y / t) * t for p in pts})
    gaps = lambda v: [round(b - a, 3) for a, b in zip(v, v[1:])]
    ok = (len(pts) == spec["nx"] * spec["ny"] and len(xs) == spec["nx"] and len(ys) == spec["ny"]
          and all(abs(g - spec["dx"]) <= t for g in gaps(xs)) and all(abs(g - spec["dy"]) <= t for g in gaps(ys)))
    check("grid " + child, ok, {"points": len(pts), "nx": len(xs), "ny": len(ys), "dx": sorted(set(gaps(xs))), "dy": sorted(set(gaps(ys)))}, spec)


def to_brep(g):
    G = Rhino.Geometry
    if isinstance(g, G.Brep):
        return g
    if isinstance(g, G.SubD):
        return g.ToBrep(G.SubDToBrepOptions.Default)
    if isinstance(g, G.Surface):
        return g.ToBrep()
    return g.ToBrep() if hasattr(g, "ToBrep") else None


def is_ruled(b, tol):
    for f in b.Faces:
        srf = f.UnderlyingSurface()
        ok = False
        for dirn in (0, 1):
            other = srf.Domain(1 - dirn)
            if all(srf.IsoCurve(dirn, other.ParameterAt(k / 6.0)).IsLinear(tol) for k in range(7)):
                ok = True
                break
        if not ok:
            return False
    return True


def gaussian_range(b):
    ks = []
    for f in b.Faces:
        du, dv = f.Domain(0), f.Domain(1)
        for i in range(12):
            for j in range(12):
                c = f.CurvatureAt(du.ParameterAt((i + 0.5) / 12), dv.ParameterAt((j + 0.5) / 12))
                if c is not None:
                    ks.append(c.Gaussian)
    return (min(ks), max(ks)) if ks else (None, None)


def props(g):
    G = Rhino.Geometry
    out = {}
    if isinstance(g, G.Curve):
        out["closed"] = g.IsClosed
        out["planar"] = g.IsPlanar()
        out["length"] = g.GetLength()
        if g.IsClosed and g.IsPlanar():
            amp = G.AreaMassProperties.Compute(g)
            out["area"] = amp.Area if amp else None
        radii = []
        for seg in (g.DuplicateSegments() or [g]):
            ok_, arc = seg.TryGetArc()
            if ok_:
                radii.append(round(arc.Radius, 3))
        out["arc_radius"] = radii
    else:
        b = g.ToBrep() if hasattr(g, "ToBrep") and not isinstance(g, G.Brep) else g
        if isinstance(b, G.Brep):
            out["closed"] = b.IsSolid
            out["planar"] = all(f.IsPlanar() for f in b.Faces)
            amp = G.AreaMassProperties.Compute(b)
            out["area"] = amp.Area if amp else None
            if b.IsSolid:
                vmp = G.VolumeMassProperties.Compute(b)
                out["volume"] = vmp.Volume if vmp else None
            out["inner_loops"] = sum(f.Loops.Count - 1 for f in b.Faces)
            out["ruled"] = is_ruled(b, 0.01)
            out["gaussian"] = gaussian_range(b)
    return out


for child, spec in exp.get("props", {}).items():
    items = on(child)
    t, rt = spec.get("tol", 0.01), spec.get("rtol", 0.001)
    bad, seen = [], []
    for o in items:
        pr = props(o.Geometry)
        seen.append({k: (round(v, 3) if isinstance(v, float) else v) for k, v in pr.items()})
        errs = []
        for k in ("closed", "planar", "inner_loops", "ruled"):
            if k in spec and pr.get(k) != spec[k]:
                errs.append(k)
        for k in ("area", "volume"):
            if k in spec and (pr.get(k) is None or abs(pr[k] - spec[k]) > rt * abs(spec[k])):
                errs.append(k)
        if "length" in spec and abs(pr.get("length", -1) - spec["length"]) > t:
            errs.append("length")
        if "length_in" in spec and not any(abs(pr.get("length", -1) - L) <= t for L in spec["length_in"]):
            errs.append("length_in")
        gmin, gmax = pr.get("gaussian", (None, None))
        if "gaussian_min" in spec and (gmin is None or gmin < spec["gaussian_min"]):
            errs.append("gaussian_min")
        if "gaussian_max" in spec and (gmax is None or gmax > spec["gaussian_max"]):
            errs.append("gaussian_max")
        if spec.get("gaussian_mixed") and not (gmin is not None and gmin < -1e-7 and gmax > 1e-7):
            errs.append("gaussian_mixed")
        if "arc_radius" in spec and not any(abs(r - spec["arc_radius"]) <= t for r in pr.get("arc_radius", [])):
            errs.append("arc_radius")
        if errs:
            bad.append({"name": o.Attributes.Name, "failed": errs})
    ok = bool(items) and not bad and ("count" not in spec or len(items) == spec["count"])
    check("props " + child, ok, {"objects": len(items), "bad": bad[:5], "sample": seen[:2]}, spec)

for child, spec in exp.get("centroids", {}).items():
    G = Rhino.Geometry
    cs = []
    for o in on(child):
        b = to_brep(o.Geometry)
        if b is None:
            continue
        mp = G.VolumeMassProperties.Compute(b) if b.IsSolid else G.AreaMassProperties.Compute(b)
        if mp:
            cs.append(mp.Centroid)
    t = spec.get("tol", 0.05)
    missing = [a for a in spec["at"] if not any(c.DistanceTo(G.Point3d(*a)) <= t for c in cs)]
    check("centroids " + child, not missing and len(cs) == len(spec["at"]),
          {"objects": len(cs), "missing": missing[:5]}, {"count": len(spec["at"]), "tol": t})

for child, spec in exp.get("on_surface", {}).items():
    srfs = [to_brep(o.Geometry) for o in on(spec["surface"])]
    srfs = [b for b in srfs if b is not None]
    worst = 0.0
    n = 0
    for o in on(child):
        c = o.Geometry
        if not hasattr(c, "PointAt"):
            continue
        n += 1
        for k in range(11):
            p = c.PointAt(c.Domain.ParameterAt(k / 10.0))
            dmin = min(p.DistanceTo(b.ClosestPoint(p)) for b in srfs) if srfs else float("inf")
            worst = max(worst, dmin)
    check("on_surface " + child, n > 0 and worst <= spec.get("tol", 0.01),
          {"curves": n, "max_distance": round(worst, 4)}, spec)

for child, spec in exp.get("heights", {}).items():
    G = Rhino.Geometry
    breps = [to_brep(o.Geometry) for o in on(child)]
    breps = [b for b in breps if b is not None]
    got, bad = [], []
    for x, y, z in spec["at"]:
        line = G.LineCurve(G.Point3d(x, y, -1e5), G.Point3d(x, y, 1e5))
        zs = []
        for b in breps:
            ok_, _, pts = G.Intersect.Intersection.CurveBrep(line, b, 0.001)
            if ok_:
                zs += [p.Z for p in pts]
        top = max(zs) if zs else None
        got.append(None if top is None else round(top, 3))
        if top is None or abs(top - z) > spec.get("tol", 0.05):
            bad.append([x, y, z])
    check("heights " + child, not bad, {"measured": got, "off": bad}, spec)

for child, spec in exp.get("clear", {}).items():
    G = Rhino.Geometry
    breps = [b for b in (to_brep(o.Geometry) for o in on(child)) if b is not None]
    hit = []
    for a, b in spec["segments"]:
        seg = G.LineCurve(G.Point3d(*a), G.Point3d(*b))
        if any(G.Intersect.Intersection.CurveBrep(seg, br, 0.001)[2] for br in breps):
            hit.append([a, b])
    check("clear " + child, bool(breps) and not hit, {"breps": len(breps), "blocked": hit}, spec)

def on_joint(x, y, z, breps, tol=0.001, step=0.005):
    """A point on a joint is strictly inside no solid. It is inside the assembly when at least two
    solids touch it and a short step in every diagonal direction lands strictly inside one of them.
    Diagonals, because an axis step from a point where joints cross runs along another joint."""
    G = Rhino.Geometry
    touching = [b for b in breps if b.IsPointInside(G.Point3d(x, y, z), tol, False)]
    if len(touching) < 2:
        return False
    steps = [(sx * step, sy * step, sz * step) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    return all(any(b.IsPointInside(G.Point3d(x + a, y + c, z + e), tol, True) for b in touching) for a, c, e in steps)


for child, spec in exp.get("inside", {}).items():
    G = Rhino.Geometry
    breps = [b for b in (to_brep(o.Geometry) for o in on(child)) if b is not None and b.IsSolid]
    missed = [pt for pt in spec["points"] if not any(br.IsPointInside(G.Point3d(*pt), 0.001, True) for br in breps)]
    joints = [pt for pt in missed if on_joint(pt[0], pt[1], pt[2], breps)]
    out = [pt for pt in missed if pt not in joints]
    found = {"solids": len(breps), "outside": out}
    if joints:
        found["on_joint"] = joints
    check("inside " + child, bool(breps) and not out, found, spec)

for child, spec in exp.get("subd", {}).items():
    G = Rhino.Geometry
    items = on(child)
    bad = []
    for o in items:
        g = o.Geometry
        if not isinstance(g, G.SubD):
            bad.append({"name": o.Attributes.Name, "type": str(o.ObjectType)}); continue
        info = {"faces": g.Faces.Count, "vertices": g.Vertices.Count}
        b = to_brep(g)
        info["closed"] = bool(b and b.IsSolid)
        if any(k in spec and info[k] != spec[k] for k in ("faces", "vertices", "closed")):
            bad.append(dict(info, name=o.Attributes.Name))
    check("subd " + child, bool(items) and not bad and ("count" not in spec or len(items) == spec["count"]),
          {"objects": len(items), "bad": bad[:3]}, spec)

def is_slider(o):
    # agents asked to name sliders may set Name as well as NickName (2026-09-29), so match by type
    return hasattr(o, "Slider") and o.GetType().Name == "GH_NumberSlider"


def gh_graded(need, slider_words=()):
    """The open GH document holding the most required components, then the most named sliders."""
    import Grasshopper
    docs = list(Grasshopper.Instances.DocumentServer)
    def score(g):
        names = [o.Name for o in g.Objects]
        nicks = [((o.NickName or "") + " " + (o.Name or "")).lower() for o in g.Objects if is_slider(o)]
        return (sum(1 for c in need if c in names), sum(1 for w in slider_words if any(w.lower() in n for n in nicks)))
    return max(docs, key=score) if docs else None


SLIDER_WORDS = [r["slider"] for r in exp.get("slider_response", [])]

def gh_outputs(gdoc):
    import Grasshopper
    outs = []
    for o in gdoc.Objects:
        if isinstance(o, Grasshopper.Kernel.IGH_Component):
            for prm in o.Params.Output:
                outs.append([g.ScriptVariable() for g in prm.VolatileData.AllData(True) if g is not None])
    return outs

for spec in exp.get("slider_response", []):
    import Grasshopper
    G = Rhino.Geometry
    gdoc = gh_graded(exp.get("gh", {}).get("components", []), SLIDER_WORDS)
    sl = [o for o in (gdoc.Objects if gdoc else []) if is_slider(o) and spec["slider"].lower() in (o.NickName or "").lower()]
    if len(sl) != 1:
        check("slider_response " + spec["slider"], False, {"sliders_matched": len(sl)}, spec); continue
    s0 = sl[0]; old = s0.Slider.Value
    try:
        s0.Slider.Value = System.Decimal(spec["set"]); gdoc.NewSolution(True)
        found = None
        for vals in gh_outputs(gdoc):
            if "points" in spec and sum(1 for v in vals if isinstance(v, G.Point3d)) == spec["points"]:
                found = {"points": spec["points"]}; break
            if "brep" in spec:
                for v in vals:
                    b = to_brep(v) if not isinstance(v, (G.Point3d, G.Curve)) and hasattr(v, "ToBrep") or isinstance(v, G.Brep) else None
                    if b is None:
                        continue
                    pr = props(b)
                    e = spec["brep"]
                    ok_ = ("inner_loops" not in e or pr.get("inner_loops") == e["inner_loops"]) and \
                          ("area" not in e or (pr.get("area") is not None and abs(pr["area"] - e["area"]) <= 0.001 * e["area"]))
                    if ok_:
                        found = {"area": round(pr.get("area") or 0, 2), "inner_loops": pr.get("inner_loops")}; break
                if found:
                    break
        check("slider_response " + spec["slider"], found is not None, {"set": spec["set"], "found": found}, spec)
    finally:
        s0.Slider.Value = old; gdoc.NewSolution(True)

if "gh" in exp:
    spec = exp["gh"]
    import Grasshopper
    need = spec.get("components", [])
    gdoc = gh_graded(need, SLIDER_WORDS)
    if gdoc is None:
        check("gh canvas", False, "no Grasshopper document", spec)
    else:
        from Grasshopper.Kernel import GH_RuntimeMessageLevel, IGH_ActiveObject
        objs = list(gdoc.Objects)
        names = [o.Name for o in objs]
        sliders = sum(1 for o in objs if is_slider(o))
        missing = [c for c in spec.get("components", []) if c not in names]
        errors = [o.Name for o in objs if isinstance(o, IGH_ActiveObject)
                  and o.RuntimeMessageLevel == GH_RuntimeMessageLevel.Error]
        check("gh sliders", sliders >= spec.get("sliders_min", 1), sliders, spec.get("sliders_min", 1))
        check("gh components", not missing, {"missing": missing}, spec.get("components"))
        check("gh errors", len(errors) <= spec.get("errors", 0), errors, spec.get("errors", 0))

# ---- clash, network, hardware ----
# New check types only; nothing above changes. Unlike on(), a selector never falls back
# to "everything under the parent": a check with nothing to test must not pass.
def _system_objects():
    s = Rhino.DocObjects.ObjectEnumeratorSettings()
    s.HiddenObjects = True  # one layout's thatch was hidden in a real file and would have dropped out
    s.LockedObjects = True
    s.DeletedObjects = False
    out = []
    for o in d.Objects.GetObjectList(s):
        lp = d.Layers[o.Attributes.LayerIndex].FullPath
        if lp and (lp == parent or lp.startswith(parent + "::")):
            out.append((lp, o))
    return out


SYSTEM = _system_objects() if any(k in exp for k in ("clash", "network", "hardware", "proportion", "cover", "bears")) else []
PARTS = {}


def part(o):
    """A measured object: name, bounding box and the geometry the tests can use."""
    key = str(o.Id)
    if key not in PARTS:
        G = Rhino.Geometry
        g = o.Geometry
        curve = g if isinstance(g, G.Curve) else None
        point = g.Location if isinstance(g, G.Point) else None
        brep = None if curve is not None or point is not None else to_brep(g)
        PARTS[key] = {"name": (o.Attributes.Name or "").strip() or key[:8], "id": key, "bb": g.GetBoundingBox(True),
                      "curve": curve, "point": point, "brep": brep}
    return PARTS[key]


def select(sel):
    """Parts matching a selector: a layer word, or {"layer": word, "name": [globs]}."""
    if isinstance(sel, str):
        sel = {"layer": sel}
    pool = SYSTEM
    if sel.get("layer"):
        spec = exp.get("layers", {}).get(sel["layer"], {})
        words = [w.lower() for w in spec.get("match", [sel["layer"]])]
        skip = [w.lower() for w in spec.get("exclude", [])]
        hit = lambda sub: any(w in sub for w in words) and not any(w in sub for w in skip)
        pool = [(lp, o) for lp, o in pool if lp != parent and hit(lp[len(parent) + 2:].lower())]
    if sel.get("name"):
        globs = sel["name"] if isinstance(sel["name"], list) else [sel["name"]]
        globs = [g.lower() for g in globs]
        pool = [(lp, o) for lp, o in pool if any(fnmatch.fnmatch((o.Attributes.Name or "").lower(), g) for g in globs)]
    return [part(o) for _, o in pool]


def names_objects(sel):
    """Whether a selector says its objects should exist: a name glob does, and so does a
    layer word unless its `layers` entry allows zero."""
    if isinstance(sel, dict) and sel.get("name"):
        return True
    word = sel if isinstance(sel, str) else sel.get("layer")
    return exp.get("layers", {}).get(word, {}).get("min", 1) > 0


def select_all(sels):
    out, seen = [], set()
    for sel in (sels if isinstance(sels, list) else [sels]):
        for p in select(sel):
            if p["id"] not in seen:
                seen.add(p["id"]); out.append(p)
    return out


def box_gap(a, b):
    """Largest separation along any axis; negative when the boxes overlap on every axis."""
    return max(a.Min.X - b.Max.X, b.Min.X - a.Max.X, a.Min.Y - b.Max.Y, b.Min.Y - a.Max.Y, a.Min.Z - b.Max.Z, b.Min.Z - a.Max.Z)


def curve_inside(c, b, tol):
    """A curve enters a closed brep: test the midpoint of each piece between its hits."""
    G = Rhino.Geometry
    _ok, _overlaps, hits = G.Intersect.Intersection.CurveBrep(c, b, tol)
    ts = [c.Domain.T0, c.Domain.T1]
    for h in hits or []:
        found, t = c.ClosestPoint(h)
        if found:
            ts.append(t)
    ts.sort()
    for t0, t1 in zip(ts, ts[1:]):
        if c.PointAt(t0).DistanceTo(c.PointAt(t1)) > tol and b.IsPointInside(c.PointAt((t0 + t1) / 2), tol, True):
            return True
    return False


def overlaps(a, b, tol, grid=7):
    """True, False, or None when the pair cannot be decided."""
    G = Rhino.Geometry
    ab, bb = a["bb"], b["bb"]
    lo = [max(ab.Min.X, bb.Min.X), max(ab.Min.Y, bb.Min.Y), max(ab.Min.Z, bb.Min.Z)]
    hi = [min(ab.Max.X, bb.Max.X), min(ab.Max.Y, bb.Max.Y), min(ab.Max.Z, bb.Max.Z)]
    if any(h - l <= tol for l, h in zip(lo, hi)) and a["curve"] is None and b["curve"] is None:
        return False  # faces that only touch; a straight curve's box may be flat, so curves go on
    if a["curve"] is not None or b["curve"] is not None:
        c, s = (a, b) if a["curve"] is not None else (b, a)
        if s["brep"] is None or not s["brep"].IsSolid:
            return None
        return curve_inside(c["curve"], s["brep"], tol)
    if a["brep"] is None or b["brep"] is None or not a["brep"].IsSolid or not b["brep"].IsSolid:
        return None
    # Points in the shared box: exact where booleans fail on coincident faces
    for i in range(grid):
        for j in range(grid):
            for k in range(grid):
                p = G.Point3d(*[l + (h - l) * (n + 0.5) / grid for l, h, n in zip(lo, hi, (i, j, k))])
                if a["brep"].IsPointInside(p, tol, True) and b["brep"].IsPointInside(p, tol, True):
                    return True
    # Thin diagonal members can pass between the points
    res = G.Brep.CreateBooleanIntersection(a["brep"], b["brep"], tol)
    if res is None:
        return None
    for r in res:
        rb = r.GetBoundingBox(True)
        if min(rb.Max.X - rb.Min.X, rb.Max.Y - rb.Min.Y, rb.Max.Z - rb.Min.Z) > tol:
            return True
    return False


def samples(p):
    if p["point"] is not None:
        return [p["point"]]
    if p["curve"] is not None:
        c = p["curve"]
        return [c.PointAtStart, c.PointAtEnd, c.PointAt(c.Domain.Mid)]
    if p["brep"] is None:
        return []
    return [v.Location for v in p["brep"].Vertices] + [e.PointAt(e.Domain.Mid) for e in p["brep"].Edges]


def distance_to(q, p):
    if p["point"] is not None:
        return q.DistanceTo(p["point"])
    if p["curve"] is not None:
        found, t = p["curve"].ClosestPoint(q)
        return q.DistanceTo(p["curve"].PointAt(t)) if found else float("inf")
    return q.DistanceTo(p["brep"].ClosestPoint(q)) if p["brep"] is not None else float("inf")


def gap_between(a, b):
    """Smallest distance found between the sampled points of one part and the other part."""
    pairs = [distance_to(q, b) for q in samples(a)] + [distance_to(q, a) for q in samples(b)]
    return min(pairs) if pairs else float("inf")


def touching(a, b, tol):
    if box_gap(a["bb"], b["bb"]) > tol:
        return False
    if gap_between(a, b) <= tol:
        return True
    return overlaps(a, b, tol) is True


def intended_pairs():
    """Declared connections, and the ones refused as too broad or unexplained."""
    good, bad = [], []
    for item in exp.get("intended", []):
        a, b = item.get("a"), item.get("b")
        globs = lambda v: [g.lower() for g in (v if isinstance(v, list) else [v] if v else [])]
        ga, gb = globs(a), globs(b)
        broad = any(not g.strip("*?[]! ") for g in ga + gb)
        if not ga or not gb or broad or not str(item.get("why", "")).strip():
            bad.append(item)
        else:
            good.append({"a": ga, "b": gb, "why": item["why"], "used": 0})
    return good, bad


def excused(pa, pb, declared):
    na, nb = pa["name"].lower(), pb["name"].lower()
    for dec in declared:
        forward = any(fnmatch.fnmatch(na, g) for g in dec["a"]) and any(fnmatch.fnmatch(nb, g) for g in dec["b"])
        back = any(fnmatch.fnmatch(nb, g) for g in dec["a"]) and any(fnmatch.fnmatch(na, g) for g in dec["b"])
        if forward or back:
            dec["used"] += 1
            return dec
    return None


DECLARED, REFUSED = intended_pairs()
for child, spec in exp.get("clash", {}).items():
    group = select_all(child)
    tol = spec.get("tol", d.ModelAbsoluteTolerance)
    if "against" in spec:
        others = select_all(spec["against"])
        unmatched = [w for w in spec["against"] if not select(w)]
    else:
        ids = {p["id"] for p in group}
        others = [part(o) for _, o in SYSTEM if str(o.Id) not in ids]
        unmatched = []
    tested, clashes, kept, unsure, skipped, seen, decided = 0, [], [], [], 0, set(), 0
    for pa in group:
        for pb in others:
            if pa["id"] == pb["id"] or frozenset((pa["id"], pb["id"])) in seen:
                continue
            seen.add(frozenset((pa["id"], pb["id"])))
            if box_gap(pa["bb"], pb["bb"]) >= 0:
                continue  # at best touching
            if (pa["curve"] is not None) and (pb["curve"] is not None):
                skipped += 1
                continue
            tested += 1
            hit = overlaps(pa, pb, tol)
            decided += hit is not None
            if hit is None:
                if (pa["brep"] is not None and pa["brep"].IsSolid) and (pb["brep"] is not None and pb["brep"].IsSolid):
                    unsure.append("%s x %s" % (pa["name"], pb["name"]))
                else:
                    skipped += 1
            elif hit:
                dec = excused(pa, pb, DECLARED)
                if dec:
                    kept.append("declared: %s x %s (%s)" % (pa["name"], pb["name"], dec["why"]))
                else:
                    clashes.append("%s x %s" % (pa["name"], pb["name"]))
    problems, unmeasured = list(clashes), []
    if not group:
        (problems if names_objects(child) else unmeasured).append("nothing matched %s" % child)
    for w in unmatched:
        (problems if names_objects(w) else unmeasured).append("no objects matched against word: %s" % w)
    if not others and not unmatched:
        unmeasured.append("nothing to test against")
    elif group and others and not seen:
        unmeasured.append("no pair to test: both sides are the same objects")
    if skipped and not decided and not unsure:
        unmeasured.append("every overlapping pair was skipped (open surface, mesh or two curves), so nothing was tested")
    problems += ["refused intended (bare wildcard or no why): %s" % json.dumps(x) for x in REFUSED]
    detail = ["members: %d in %s, %d against; %d of %d pairs tested" % (len(group), child, len(others), tested, len(seen))]
    if group and others and seen and not tested and not skipped:
        detail.append("clear: members on both sides and no bounding boxes overlap, so no pair needed a geometry test")
    detail += ["clash: " + x for x in clashes[:40]] + kept[:40] + ["undecided: " + x for x in unsure[:20]]
    detail += [x for x in problems if x not in clashes] + ["not measured: " + x for x in unmeasured]
    if skipped:
        detail.append("skipped %d pair(s) with an open surface, mesh or two curves: not tested" % skipped)
    if len(clashes) > 40:
        detail.append("... and %d more clashes" % (len(clashes) - 40))
    check("clash " + child, not problems and not unmeasured, {"group": len(group), "against": len(others), "pairs_tested": tested,
          "clashes": len(clashes), "declared": len(kept), "undecided": len(unsure), "skipped": skipped, "detail": detail}, spec,
          not_measured=bool(unmeasured) and not problems)

for key, spec in exp.get("network", {}).items():
    tol = spec.get("tol", d.ModelAbsoluteTolerance * 10)
    pipes, fixtures, sinks = select_all(spec.get("pipes", key)), select_all(spec.get("fixtures", [])), select_all(spec.get("to", []))
    reached, frontier, stray = [], list(sinks), list(pipes)
    while frontier:
        cur = frontier.pop()
        keep = []
        for r in stray:
            if touching(cur, r, tol):
                reached.append(r); frontier.append(r)
            else:
                keep.append(r)
        stray = keep
    connected = reached + sinks
    missing, detail = [], []
    for f in fixtures:
        if not any(touching(f, c, tol) for c in connected):
            near = min((gap_between(f, c) for c in connected), default=float("inf"))
            missing.append(f["name"])
            detail.append("not connected: %s (nearest connected piece %s away)" % (f["name"], "none" if near == float("inf") else round(near, 3)))
    for s in stray[:20]:
        near = min((gap_between(s, c) for c in connected), default=float("inf"))
        detail.append("stray pipe: %s (nearest connected piece %s away)" % (s["name"], "none" if near == float("inf") else round(near, 3)))
    empty = [n for n, v in (("pipes", pipes), ("fixtures", fixtures), ("to", sinks)) if not v]
    detail += ["nothing matched: %s" % n for n in empty]
    check("network " + key, not (missing or stray or empty), {"fixtures": len(fixtures), "pipes": len(pipes), "sinks": len(sinks),
          "not_connected": len(missing), "stray_pipes": len(stray), "detail": detail}, spec)

for key, spec in exp.get("hardware", {}).items():
    items = select_all(spec.get("items", key))
    tol = spec.get("tol", d.ModelAbsoluteTolerance * 10)
    detail = []
    if spec.get("placeholder"):
        bad = [p["name"] for p in items if "placeholder" not in p["name"].lower()]
        detail = ["not named as a placeholder: " + n for n in bad[:20]]
        check("hardware " + key, bool(items) and not bad, {"items": len(items), "placeholders": len(items) - len(bad), "detail": detail or ["placeholder only: no connection was checked"]}, spec)
        continue
    groups = [(g, select_all(g)) for g in spec.get("joins", [])]
    bad = []
    empty = [json.dumps(g) for g, members in groups if not members]
    past = spec.get("past")
    axis = (past or {}).get("axis", "z").upper()
    top = lambda bb: getattr(bb.Max, axis)
    of_group = select_all(past["of"]) if past else []
    for p in items:
        faults = []
        for g, members in groups:
            if not any(touching(p, m, tol) for m in members):
                faults.append("does not reach %s" % json.dumps(g))
        if past:
            held = [m for m in of_group if touching(p, m, tol)]
            if held:
                reach = top(p["bb"]) - max(top(m["bb"]) for m in held)
                if reach < past["by"] - 1e-9:
                    faults.append("extends %.3f past %s, needs %s" % (reach, past["of"], past["by"]))
        if faults:
            bad.append(p["name"])
            detail.append("%s: %s" % (p["name"], "; ".join(faults)))
    if len(detail) > 20:
        detail = detail[:20] + ["... and %d more" % (len(detail) - 20)]
    if not spec.get("joins"):
        empty.append("joins")
    detail += ["nothing matched: %s" % e for e in empty]
    check("hardware " + key, bool(items) and not bad and not empty, {"items": len(items), "implausible": len(bad), "detail": detail}, spec)

AXES = "XYZ"


def extent(p, k):
    return getattr(p["bb"].Max, AXES[k]) - getattr(p["bb"].Min, AXES[k])


for key, spec in exp.get("proportion", {}).items():
    items = select_all(spec.get("items", key))
    k = AXES.index(spec.get("axis", "z").upper())
    lo, hi = spec["ratio"]
    bad = []
    for p in items:
        across = min(extent(p, i) for i in range(3) if i != k)
        r = extent(p, k) / across if across > 1e-12 else float("inf")
        if not lo - 1e-9 <= r <= hi + 1e-9:
            bad.append("%s: %.2f" % (p["name"], r))
    check("proportion " + key, bool(items) and not bad, {"items": len(items), "outside_ratio": len(bad), "detail": bad[:20] or ["none matched"] * (not items)}, spec)

for key, spec in exp.get("cover", {}).items():
    items = select_all(spec.get("items", key))
    k = AXES.index(spec.get("axis", "y").upper())
    ua, va = [i for i in range(3) if i != k]
    (u0, v0), (u1, v1) = spec["region"]
    holes = spec.get("holes", [])
    step = spec.get("step", 1.0)
    tol = spec.get("tol", d.ModelAbsoluteTolerance * 10)
    spans = [(getattr(p["bb"].Min, AXES[ua]), getattr(p["bb"].Max, AXES[ua]), getattr(p["bb"].Min, AXES[va]), getattr(p["bb"].Max, AXES[va])) for p in items]
    gaps, total = [], 0
    u = u0 + step / 2.0
    while u < u1:
        v = v0 + step / 2.0
        while v < v1:
            if not any(h[0][0] <= u <= h[1][0] and h[0][1] <= v <= h[1][1] for h in holes):
                total += 1
                if not any(a - tol <= u <= b + tol and c - tol <= v <= e + tol for a, b, c, e in spans):
                    gaps.append((u, v))
            v += step
        u += step
    detail = []
    if gaps:
        us, vs = [g[0] for g in gaps], [g[1] for g in gaps]
        detail.append("%d of %d points uncovered, within %s %.2f to %.2f, %s %.2f to %.2f" % (len(gaps), total, AXES[ua].lower(), min(us), max(us), AXES[va].lower(), min(vs), max(vs)))
        detail += ["uncovered at %s %.2f, %s %.2f" % (AXES[ua].lower(), g[0], AXES[va].lower(), g[1]) for g in gaps[:10]]
    check("cover " + key, bool(items) and total > 0 and not gaps, {"items": len(items), "points": total, "uncovered": len(gaps), "detail": detail or ["none matched"] * (not items)}, spec)

for key, spec in exp.get("bears", {}).items():
    items = select_all(spec.get("items", key))
    supports = select_all(spec["on"]) if spec.get("on") else [part(o) for _, o in SYSTEM]
    tol = spec.get("tol", d.ModelAbsoluteTolerance * 10)
    G = Rhino.Geometry
    bad, skipped, tested = [], 0, 0
    for p in items:
        if extent(p, 2) <= max(extent(p, 0), extent(p, 1)):
            skipped += 1
            continue
        tested += 1
        b = p["bb"]
        z = b.Min.Z - tol / 2.0
        free = 0
        for fx in (0.1, 0.5, 0.9):
            for fy in (0.1, 0.5, 0.9):
                q = G.Point3d(b.Min.X + fx * (b.Max.X - b.Min.X), b.Min.Y + fy * (b.Max.Y - b.Min.Y), z)
                held = any(s["id"] != p["id"] and s["brep"] is not None and s["bb"].Min.Z - tol <= z <= s["bb"].Max.Z + tol
                           and s["bb"].Min.X - tol <= q.X <= s["bb"].Max.X + tol and s["bb"].Min.Y - tol <= q.Y <= s["bb"].Max.Y + tol
                           and s["brep"].IsPointInside(q, d.ModelAbsoluteTolerance, False) for s in supports)
                free += 0 if held else 1
        if free:
            bad.append("%s: %d of 9 points under its foot rest on nothing" % (p["name"], free))
    detail = bad[:20] + (["skipped %d not taller than wide" % skipped] if skipped else [])
    check("bears " + key, tested > 0 and not bad, {"items": len(items), "tested": tested, "unsupported": len(bad), "detail": detail or ["none matched"] * (not items)}, spec)

# One JSON line per check: the MCP runner has dropped a single multi-kilobyte print
# while returning the same text split across prints (2026-09-28).
print(json.dumps({"case": exp.get("case"), "pass": all(r["pass"] for r in res), "checks": len(res)}))
for r in res:
    print(json.dumps(r))
