#! python3
"""View logic with no Rhino in it (Arch Studio, as-rhino-axon): layer selection, projection mapping, overlap groups,
true cuts, the building lock's comparison, ray clipping, detail scale and joint picking.

as-axon.py loads this file after as-rhino-thinline's as-sheet-core.py. It is separate so that it can be tested without Rhino.
"""
import math
PROJECTED = ("Brep", "Extrusion", "Mesh", "SubD")  # geometry main_linework projects; curves become guides


def layer_selected(path, roots):
    """Whether a layer path is one of the roots, under one, or matches one as a glob. roots is a path or a list."""
    for root in [roots] if isinstance(roots, str) else roots:
        if path == root or path.startswith(root + "::") or fnmatch.fnmatchcase(path, root):
            return True
    return False


def solve_affine(source, target):
    """2D affine from three reference pairs: returns ((a, b, c), (d, e, f)) with x' = ax + by + c."""
    (a, b), (c, e), (f, g) = source
    det = (c - a) * (g - b) - (f - a) * (e - b)
    if abs(det) < 1e-12:
        raise ValueError("the three reference points are collinear in the drawing")

    def row(v0, v1, v2):
        p = ((v1 - v0) * (g - b) - (v2 - v0) * (e - b)) / det
        q = ((c - a) * (v2 - v0) - (f - a) * (v1 - v0)) / det
        return p, q, v0 - p * a - q * b

    return row(target[0][0], target[1][0], target[2][0]), row(target[0][1], target[1][1], target[2][1])


def true_cut(low, high, at, tol):
    """Whether a member spanning low..high along an axis is really cut by a section plane at `at`: it
    continues past the plane. A member face that only lies on the plane is not a cut."""
    return low < at - tol and high > at + tol


def pick_locator(targets, centre, radius, stop, polylines, outline, gap):
    """The joint and route for a detail's locator: targets are page points of the requested joint, tried
    nearest the detail ring first (the building's edge facing the details), each on every route of
    locator_routes. Returns (index into targets, route) for the first leader that crosses no linework away
    from its own joint, or None when there is no clean one."""
    order = sorted(range(len(targets)), key=lambda i: math.hypot(targets[i][0] - centre[0], targets[i][1] - centre[1]))
    for i in order:
        tx, ty = targets[i]
        for legs in locator_routes(centre, radius, (tx, ty), stop, outline, gap):
            if any(point_segment_distance(centre, a, b) < 0.98 * radius for a, b in legs):
                continue    # a leader never runs through its own detail
            if not leader_crossings(legs, polylines, [(tx, ty, stop)]):
                return i, legs
    return None


def overlap_groups(boxes, names, min_depth, touching=()):
    """Clusters of indices whose boxes (x0, y0, z0, x1, y1, z1) share a name and overlap by more than
    min_depth in all three directions: interpenetrating pieces of one system, such as pipe runs meeting
    at an elbow. Members that only touch are left apart, so the seam between them stays drawn, except
    names matching a glob in touching (runs of one service drawn end to end), which join when they touch."""
    parent = list(range(len(boxes)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            depth = -min_depth if any(fnmatch.fnmatchcase(names[i], g) for g in touching) else min_depth
            if names[i] == names[j] and all(min(a[k + 3], b[k + 3]) - max(a[k], b[k]) > depth for k in range(3)):
                parent[root(i)] = root(j)
    groups = {}
    for i in range(len(boxes)):
        groups.setdefault(root(i), []).append(i)
    return [g for g in groups.values() if len(g) > 1]


def building_changes(before, after):
    """(removed, changed) object ids between two {id: fingerprint} maps of the building's objects."""
    removed = sorted(k for k in before if k not in after)
    changed = sorted(k for k in before if k in after and before[k] != after[k])
    return removed, changed


def clip_segment_to_box(a, b, box):
    """The part of segment a-b inside box (x0, y0, z0, x1, y1, z1), as parameters (t0, t1) along it, or None."""
    t0, t1 = 0.0, 1.0
    for axis in range(3):
        lo, hi = min(box[axis], box[axis + 3]), max(box[axis], box[axis + 3])
        d = b[axis] - a[axis]
        if abs(d) < 1e-12:
            if a[axis] < lo or a[axis] > hi:
                return None
            continue
        u, v = (lo - a[axis]) / d, (hi - a[axis]) / d
        t0, t1 = max(t0, min(u, v)), min(t1, max(u, v))
        if t0 > t1:
            return None
    return t0, t1


def dedupe_curves(keys, tol):
    """Indices to keep from curve keys [(x0, y0, x1, y1, length)]: a curve repeating one already kept (same ends,
    either way round, and length, within tol) is dropped, so a sheet carries no stacked duplicate linework."""
    kept, out = [], []
    for i, (x0, y0, x1, y1, n) in enumerate(keys):
        dup = any(abs(n - m) <= tol and ((abs(x0 - a) <= tol and abs(y0 - b) <= tol and abs(x1 - c) <= tol and abs(y1 - e) <= tol) or
                                          (abs(x0 - c) <= tol and abs(y0 - e) <= tol and abs(x1 - a) <= tol and abs(y1 - b) <= tol))
                  for a, b, c, e, m in kept)
        if not dup:
            kept.append((x0, y0, x1, y1, n))
            out.append(i)
    return out


STANDARD_SCALES = (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 16, 20, 24, 25, 30, 40, 48, 50, 60, 75, 96, 100, 125, 150, 200, 250, 300, 400, 500)


def fit_scale_denominator(content, space, fill=0.8):
    """The smallest standard scale 1:n at which content (model length) fills at most fill of space (page length, same unit)."""
    for n in STANDARD_SCALES:
        if content / n <= fill * space:
            return n
    return STANDARD_SCALES[-1]
