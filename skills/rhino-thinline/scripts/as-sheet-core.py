#! python3
"""Sheet logic with no Rhino in it (Arch Studio, as-rhino-thinline): mapping, routes, hatch, table lookups, sheet checks.

as-sheet.py loads this file. It is separate so that it can be tested without Rhino.
Page coordinates here are in page units; pass mm for the page's millimetre size.
"""
import fnmatch
import hashlib
import json
import math
import random
import re

COLOUR_WORDS = re.compile(r"\b(red|blue|green|yellow|orange|purple|pink|brown|magenta|cyan|colou?red)\b", re.I)
OUTLINE_TYPES = ("Boundary", "Projecting", "Tangent", "TangentProjects")
TEXT_HEIGHT_KEY = "as-sheet:text-mm"   # object user string: the text height text() was asked for, in mm
TEXT_HEIGHT_TOLERANCE = 0.10
EDGE_TYPES = ("Crease", "NonSilhouetteCrease")


def stroke_class(silhouette, depth_t=0.0, receding_from=None):
    """"outline", "edge", "receding" or None to drop.

    outline: the silhouette of an object. edge: an inner crease. receding: an inner crease on an
    object in the rear of the drawing (depth_t: 0 nearest the viewer, 1 farthest)."""
    if silhouette in OUTLINE_TYPES:
        return "outline"
    if silhouette in EDGE_TYPES:
        return "receding" if receding_from is not None and depth_t >= receding_from else "edge"
    return None


def main_stroke(silhouette, on_outline, depth_t=0.0, receding_from=0.6):
    """Stroke for the main drawing: "outline" only on the whole assembly's outline against the paper,
    "edge" for member edges, "receding" for member edges toward the back, None to drop."""
    if silhouette not in OUTLINE_TYPES and silhouette not in EDGE_TYPES:
        return None
    if on_outline:
        return "outline"
    return "receding" if receding_from is not None and depth_t >= receding_from else "edge"


def point_in_polygon(p, points):
    """Even-odd test of a point against a closed polyline of (x, y)."""
    x, y = p
    inside = False
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def against_paper(mid, direction, eps, regions):
    """Whether an edge at mid with the given direction has empty paper on one side: a point eps to either
    side lies in none of the regions [(box, polygon)]. That edge is the assembly's outline."""
    dx, dy = direction
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length * eps, dx / length * eps

    def covered(p):
        return any(b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3] and point_in_polygon(p, poly) for b, poly in regions)

    return not covered((mid[0] + nx, mid[1] + ny)) or not covered((mid[0] - nx, mid[1] - ny))


def outer_loops(polylines):
    """The outer loops of a projected outline: loops whose box is not inside another loop's box. The holes
    of a see-through frame are dropped, so only the assembly's edge against the paper is left."""
    boxes = []
    for points in polylines:
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        boxes.append((min(xs), min(ys), max(xs), max(ys)) if points else None)

    def inside(a, b):
        return a != b and b[0] <= a[0] and b[1] <= a[1] and a[2] <= b[2] and a[3] <= b[3]

    return [p for i, p in enumerate(polylines) if boxes[i] and not any(boxes[j] and inside(boxes[i], boxes[j]) for j in range(len(polylines)) if j != i)]


def composite_shift(extents, field):
    """Page shift that centres the composite (linework, callouts, details) in the drawing field,
    and the margins it leaves. Extents and field are (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = extents
    fx0, fy0, fx1, fy1 = field
    dx = (fx0 + fx1) / 2.0 - (x0 + x1) / 2.0
    dy = (fy0 + fy1) / 2.0 - (y0 + y1) / 2.0
    return (dx, dy), {"left": x0 + dx - fx0, "right": fx1 - x1 - dx, "bottom": y0 + dy - fy0, "top": fy1 - y1 - dy}


def locator_route(centre, radius, target, stop_short=0.0, route=None):
    """Orthogonal leader from a detail ring to a point on the main drawing, as point pairs.

    A leader running near the ring's bottom meets it almost tangent, so one that is not nearly in
    line leaves from the ring's side or top with one elbow."""
    cx, cy = centre
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
    if route == "vh":
        return [((cx, cy + sy * radius), (cx, ty)), ((cx, ty), (tx - sx * stop_short, ty))]
    if abs(dy) < 0.6 * radius:
        return [((cx + sx * math.sqrt(radius * radius - dy * dy), ty), (tx - sx * stop_short, ty))]
    if abs(dx) < 0.6 * radius:
        return [((tx, cy + sy * math.sqrt(radius * radius - dx * dx)), (tx, ty - sy * stop_short))]
    return [((cx + sx * radius, cy), (tx, cy)), ((tx, cy), (tx, ty - sy * stop_short))]


def locator_routes(centre, radius, target, stop, outline, gap):
    """Every orthogonal leader to try from a detail ring to a joint, as lists of point pairs: the two simple
    routes, then routes that jog around the drawing's outline (x0, y0, x1, y1), gap clear of it: in from
    the side, from above and from below."""
    cx, cy = centre
    tx, ty = target
    sx = 1 if tx > cx else -1
    routes = [locator_route(centre, radius, target, stop), locator_route(centre, radius, target, stop, "vh")]
    xj = outline[0] - gap if sx > 0 else outline[2] + gap
    if (xj - cx) * sx > radius:
        side = 1 if xj > tx else -1
        routes.append([((cx + sx * radius, cy), (xj, cy)), ((xj, cy), (xj, ty)), ((xj, ty), (tx + side * stop, ty))])
    for yj in (outline[3] + gap, outline[1] - gap):
        side = 1 if yj > ty else -1
        if abs(yj - cy) < radius:   # the jog height crosses the ring: leave from its side at that height
            start = (cx + sx * math.sqrt(radius * radius - (yj - cy) ** 2), yj)
            routes.append([(start, (tx, yj)), ((tx, yj), (tx, ty + side * stop))])
            continue
        sy = 1 if yj > cy else -1
        routes.append([((cx, cy + sy * radius), (cx, yj)), ((cx, yj), (tx, yj)), ((tx, yj), (tx, ty + side * stop))])
    return routes


def label_routes(target, outline, gap):
    """Straight leaders from clear paper beside the drawing's outline (x0, y0, x1, y1) to a part: one per side, as
    (side, start, end). The label's text sits at `start`, outside the outline; `end` is the dot on the part."""
    tx, ty = target
    return [("left", (outline[0] - gap, ty), (tx, ty)), ("right", (outline[2] + gap, ty), (tx, ty)),
            ("top", (tx, outline[3] + gap), (tx, ty)), ("bottom", (tx, outline[1] - gap), (tx, ty))]


def label_box(side, start, size, pad):
    """The text box (x0, y0, x1, y1) of a label whose leader starts at `start` on `side` of its part."""
    w, h = size
    x, y = start
    if side == "left":
        return (x - pad - w, y - h / 2.0, x - pad, y + h / 2.0)
    if side == "right":
        return (x + pad, y - h / 2.0, x + pad + w, y + h / 2.0)
    if side == "top":
        return (x - w / 2.0, y + pad, x + w / 2.0, y + pad + h)
    return (x - w / 2.0, y - pad - h, x + w / 2.0, y - pad)


def pick_label(targets, outline, gap, polylines, dot, text_size=None, steps=(8, 14, 20, 30, 45), pad=1.0):
    """The clearest label for a part: (target index, side, start, end) for the shortest straight leader, in any
    of four directions, that crosses no linework away from its dot, with its text box (text_size (w, h), when
    given) clear of every line too. Short leaders into clear space inside the drawing (the open glass of a
    window) are tried with the routes from beside the outline. None when nothing is clear."""
    dirs = {"left": (-1, 0), "right": (1, 0), "top": (0, 1), "bottom": (0, -1)}
    cands = []
    for i, t in enumerate(targets):
        for side, start, end in label_routes(t, outline, gap):
            cands.append((math.hypot(start[0] - end[0], start[1] - end[1]), i, side, start, end))
        for side, (dx, dy) in dirs.items():
            for d in steps:
                cands.append((d, i, side, (t[0] + dx * d, t[1] + dy * d), t))
    for _length, i, side, start, end in sorted(cands, key=lambda c: c[0]):
        if leader_crossings([(start, end)], polylines, [(end[0], end[1], dot)], clear=1.0):
            continue
        if text_size is not None:
            x0, y0, x1, y1 = label_box(side, start, text_size, pad)
            if lines_through_box(polylines, (x0 - 2 * pad, y0 - 2 * pad, x1 + 2 * pad, y1 + 2 * pad)):   # a margin round the text
                continue
        return i, side, start, end
    return None


def label_rows(anchor_ys, separation, top, bottom):
    """A y for each label, in anchor order (high to low), no closer than `separation` and inside the column."""
    rows = []
    for i, y in enumerate(anchor_ys):
        rows.append(min(y, top) if i == 0 else min(y, rows[-1] - separation))
    if rows and rows[-1] < bottom:
        rows[-1] = bottom
        for i in range(len(rows) - 2, -1, -1):
            rows[i] = max(rows[i], rows[i + 1] + separation)
    return rows


def axis_aligned(segments, tol=1e-3):
    """The segments that are neither horizontal nor vertical."""
    return [s for s in segments if abs(s[0][0] - s[1][0]) > tol and abs(s[0][1] - s[1][1]) > tol]


def shared_x(anchors, min_gap):
    """Pairs of anchors whose x positions are close enough to read as one leader."""
    xs = sorted(anchors)
    return [(a, b) for a, b in zip(xs, xs[1:]) if b - a < min_gap]


def segment_hits_box(a, b, box):
    """True when the segment a-b passes through or touches the box (x0, y0, x1, y1)."""
    t0, t1 = 0.0, 1.0
    for p, d, lo, hi in ((a[0], b[0] - a[0], box[0], box[2]), (a[1], b[1] - a[1], box[1], box[3])):
        if abs(d) < 1e-12:
            if p < lo or p > hi:
                return False
            continue
        u, v = sorted(((lo - p) / d, (hi - p) / d))
        t0, t1 = max(t0, u), min(t1, v)
        if t0 > t1:
            return False
    return True


def segment_hit(a, b, c, d, tol=1e-9):
    """Where segments a-b and c-d meet, or None. Collinear overlap returns the start of the overlap."""
    r, s = (b[0] - a[0], b[1] - a[1]), (d[0] - c[0], d[1] - c[1])
    den = r[0] * s[1] - r[1] * s[0]
    q = (c[0] - a[0], c[1] - a[1])
    if abs(den) < tol:
        if abs(q[0] * r[1] - q[1] * r[0]) > tol * max(1.0, math.hypot(*r)):
            return None
        rr = r[0] * r[0] + r[1] * r[1]
        if rr < tol:
            return None
        t0, t1 = sorted(((q[0] * r[0] + q[1] * r[1]) / rr, ((d[0] - a[0]) * r[0] + (d[1] - a[1]) * r[1]) / rr))
        if t1 < 0 or t0 > 1:
            return None
        t = max(t0, 0.0)
        return a[0] + r[0] * t, a[1] + r[1] * t
    t = (q[0] * s[1] - q[1] * s[0]) / den
    u = (q[0] * r[1] - q[1] * r[0]) / den
    if -tol <= t <= 1 + tol and -tol <= u <= 1 + tol:
        return a[0] + r[0] * t, a[1] + r[1] * t
    return None


def leader_crossings(leaders, polylines, targets, clear=2.0):
    """(leader, point) where a locator leader meets the main drawing, ignoring points within clear times the
    locator ring's radius of any ring: a leader has to reach its own joint. targets is [(x, y, radius)]."""
    found = []
    for leader in leaders:
        for points in polylines:
            for c, d in zip(points, points[1:]):
                at = segment_hit(leader[0], leader[1], c, d)
                if at is not None and not any(math.hypot(at[0] - x, at[1] - y) < clear * r for x, y, r in targets):
                    found.append((leader, at))
                    break
            else:
                continue
            break
    return found


def scale_mismatch(read_back, expected, rel=1e-4):
    """True when a detail's page-to-model ratio is not the scale asked for."""
    return abs(read_back - expected) > rel * expected


def margins(extents, field):
    """Distance from the composite's extents to each side of the field; negative when it spills out."""
    x0, y0, x1, y1 = extents
    fx0, fy0, fx1, fy1 = field
    return {"left": x0 - fx0, "right": fx1 - x1, "bottom": y0 - fy0, "top": fy1 - y1}


MIN_MARGIN_MM = 10.0   # check_sheet's margin limit; fixed, never passed in: fix the sheet, not the check


def segment_distance(a, b, c, d):
    """Shortest distance between segments a-b and c-d, in 2D; 0 when they meet."""
    if segment_hit(a, b, c, d) is not None:
        return 0.0
    return min(point_segment_distance(a, c, d), point_segment_distance(b, c, d), point_segment_distance(c, a, b), point_segment_distance(d, a, b))


def shape_distance(s, t):
    """Distance between two shapes: ("circle", cx, cy, r) or ("poly", [(x, y), ...]). A circle is its ring."""
    if s[0] == "circle" and t[0] == "circle":
        return max(0.0, math.hypot(s[1] - t[1], s[2] - t[2]) - s[3] - t[3])
    if t[0] == "circle":
        s, t = t, s
    if s[0] == "circle":
        pts = t[1]
        nearest = min(point_segment_distance((s[1], s[2]), a, b) for a, b in zip(pts, pts[1:])) if len(pts) > 1 else math.hypot(pts[0][0] - s[1], pts[0][1] - s[2])
        return max(0.0, nearest - s[3])
    p, q = s[1], t[1]
    return min(segment_distance(a, b, c, d) for a, b in zip(p, p[1:]) for c, d in zip(q, q[1:]))


def shape_box(s):
    if s[0] == "circle":
        return s[1] - s[3], s[2] - s[3], s[1] + s[3], s[2] + s[3]
    xs, ys = [p[0] for p in s[1]], [p[1] for p in s[1]]
    return min(xs), min(ys), max(xs), max(ys)


def layout_summary(elements, field, one_mm=1.0, count=6, empty_below=0.25, fills=None):
    """A text summary of a sheet for a host that cannot show images: the closest pairs of elements, the
    elements closest to the field's edges, and any detail ring mostly empty.

    elements is [(label, tag, shape)]; pairs with the same tag (a ring and its own leader) are skipped. field is
    (x0, y0, x1, y1). fills is {tag: share of the ring's area the detail content covers}. Distances in mm."""
    lines = []
    pairs = []
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            (la, ta, sa), (lb, tb, sb) = elements[i], elements[j]
            if ta and ta == tb:
                continue
            pairs.append((shape_distance(sa, sb) / one_mm, la, lb))
    pairs.sort()
    seen = set()
    pairs = [p for p in pairs if frozenset(p[1:]) not in seen and not seen.add(frozenset(p[1:]))]   # a leader's segments count once
    lines.append("closest pairs (mm):")
    lines += ["  %.1f  %s  <->  %s" % p for p in pairs[:count]] or ["  none"]
    edges = []
    for label, _tag, shape in elements:
        x0, y0, x1, y1 = shape_box(shape)
        gaps = {"left": x0 - field[0], "right": field[2] - x1, "bottom": y0 - field[1], "top": field[3] - y1}
        side = min(gaps, key=gaps.get)
        edges.append((gaps[side] / one_mm, label, side))
    edges.sort()
    seen = set()
    edges = [e for e in edges if e[1] not in seen and not seen.add(e[1])]
    lines.append("closest to the field edge (mm, under %g fails check_sheet):" % MIN_MARGIN_MM)
    lines += ["  %.1f  %s (%s)" % e for e in edges[:count]] or ["  none"]
    empty = sorted((share, tag) for tag, share in (fills or {}).items() if share < empty_below)
    lines.append("detail rings mostly empty (content covers under %d%% of the ring):" % round(100 * empty_below))
    lines += ["  %s  %d%%" % (tag, round(100 * share)) for share, tag in empty] or ["  none"]
    return "\n".join(lines)


def point_segment_distance(p, a, b):
    """Distance from point p to segment a-b, in 2D."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = dx * dx + dy * dy
    t = 0.0 if length < 1e-24 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def near_polyline(p, polylines, tol):
    """Whether p lies within tol of any of the polylines (lists of (x, y))."""
    return any(point_segment_distance(p, a, b) <= tol for points in polylines for a, b in zip(points, points[1:]))


def through_circle(points, centre, radius, inside=0.9):
    """Whether a polyline passes inside a circle (closer than inside * radius to its centre): a line through a tag."""
    return any(point_segment_distance(centre, a, b) < inside * radius for a, b in zip(points, points[1:]))


MATERIAL_WORDS = [   # first match wins, on "<layer path> <object name>"; anything unmatched gets no hatch
    ("timber", r"glazing[\s_-]*stops?\b|glazing[\s_-]*bead"),
    ("none", r"glass|glazing|igu|\bpanes?\b|\blites?\b|membrane|wrb|weather|wrap|paper|felt|flashing|tape|sealant|caulk|backer|gasket|weatherstrip|film"),
    ("gypsum", r"gypsum|drywall|plasterboard|gwb|plaster"),
    ("plywood", r"plywood|osb|sheathing|subfloor|panel"),
    ("concrete", r"concrete|slab|footing|foundation|masonry|cmu|block|screed"),
    ("steel", r"steel|metal|alumin|hinge|bolt|plate[\s_-]*steel|bracket|hardware|spacer"),
    ("timber", r"wood|timber|lumber|stud|plate|header|joist|rafter|beam|post|girt|sill|jamb|stile|rail|frame|trim|casing|stool|apron|shim|siding|clapboard|cripple|king|jack|stop|sash|blocking|ledger"),
]


def material_for(label):
    """The hatch material a layer path or object name implies (MATERIAL_WORDS); "none" when nothing matches."""
    text = (label or "").lower()
    for material, pattern in MATERIAL_WORDS:
        if re.search(pattern, text):
            return material
    return "none"


def clip_to_polygon(segments, polygon):
    """The parts of 2D segments inside a closed polygon [(u, v), ...]: hatch clipped to the real outline of a cut
    face (a sloped sill is not its bounding box)."""
    pts = list(polygon) + [polygon[0]]
    out = []
    for a, b in segments:
        ts = [0.0, 1.0]
        for c, d in zip(pts, pts[1:]):
            hit = segment_hit(a, b, c, d)
            if hit is not None:
                length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
                ts.append(math.hypot(hit[0] - a[0], hit[1] - a[1]) / length)
        ts = sorted(set(min(1.0, max(0.0, t)) for t in ts))
        for t0, t1 in zip(ts, ts[1:]):
            if t1 - t0 < 1e-9:
                continue
            p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            if point_in_polygon(((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0), polygon):
                out.append((p0, p1))
    return out


def ledger_hash(prev, entry):
    """The chain hash of one request entry after the hash before it."""
    return hashlib.sha256((prev + json.dumps(entry, sort_keys=True)).encode("utf-8")).hexdigest()


def ledger_append(entries, entry):
    """entries plus one request, chained to the one before it. Returns (entries, seal)."""
    prev = entries[-1]["hash"] if entries else ""
    body = dict(entry, n=len(entries))
    entries = list(entries) + [dict(body, hash=ledger_hash(prev, body))]
    return entries, {"count": len(entries), "head": entries[-1]["hash"]}


def ledger_problems(entries, seal, building=None):
    """Why a request ledger cannot be trusted: entries missing, edited or out of order against the chain and
    the seal, or the building record changed since the sheet started. Empty when it is intact."""
    if entries is None or seal is None:
        return ["the sheet's request record is missing (%s); never delete a request or failure record to pass a check: report what could not be placed" % ("requests" if entries is None else "seal")]
    out, prev = [], ""
    for i, entry in enumerate(entries):
        body = {k: v for k, v in entry.items() if k != "hash"}
        if body.get("n") != i or entry.get("hash") != ledger_hash(prev, body):
            out.append("the sheet's request record was edited at entry %d; never delete a request or failure record to pass a check: report what could not be placed" % i)
            break
        prev = entry["hash"]
    if not out and (seal.get("count") != len(entries) or seal.get("head") != prev):
        out.append("the sheet's request record has %d entries but %s were recorded; never delete a request or failure record to pass a check: report what could not be placed" % (len(entries), seal.get("count")))
    start = entries[0] if entries else {}
    if start.get("kind") != "sheet":
        out.append("the sheet's request record does not start at setup_sheet")
    elif "building" in start and (building is None or start["building"] != hashlib.sha256(building.encode("utf-8")).hexdigest()):
        out.append("the building record was replaced or removed after the sheet started")
    return out


def unmet_requests(entries, drawn):
    """Requests the sheet does not show, recomputed from what is drawn. drawn is {kind: set of keys} found on
    the page ("label": label texts, "locator": tags with a leader and a ring, "detail": tags with a ring and
    linework). A request counts as met only when its object is on the sheet now, whatever its attempts
    recorded; the message is the last failed attempt's, or a plain one when the drawing was removed."""
    last = {}
    for entry in entries:
        if entry.get("kind") in ("label", "locator", "detail"):
            last[(entry["kind"], entry["key"])] = entry.get("message") or last.get((entry["kind"], entry["key"]))
    out = []
    for (kind, key), message in last.items():
        if key not in drawn.get(kind, ()):
            out.append(message or "%s %r was requested and is not on the sheet" % (kind, key))
    return out


def hatch_pattern(material, across, u0, v0, u1, v1, unit=1.0):
    """Hatch segments for one cut face by material: timber across the grain gets the X, along it broken
    grain lines; plywood plies; gypsum a fine stipple; concrete stipple and aggregate; steel near-solid lines;
    none or anything else, nothing."""
    if material == "gypsum":
        return hatch_concrete(u0, v0, u1, v1, unit=unit, aggregate_grid=(0, 0))
    if material == "timber":
        return hatch_x(u0, v0, u1, v1) if across else hatch_grain(u0, v0, u1, v1)
    if material == "plywood":
        return hatch_plies(u0, v0, u1, v1)
    if material == "concrete":
        return hatch_concrete(u0, v0, u1, v1, unit=unit)
    if material == "steel":
        return hatch_dense(u0, v0, u1, v1)
    return []


def collinear_runs(leader, polylines, tol, min_length, targets=(), clear=2.0):
    """Stretches where a leader runs along a drawn line: parallel within tol and overlapping by more than
    min_length, away from its own joint. Such a leader reads as part of the member. targets is [(x, y, r)]."""
    (ax, ay), (bx, by) = leader
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-12:
        return []
    ux, uy = (bx - ax) / length, (by - ay) / length
    found = []
    for points in polylines:
        for c, d in zip(points, points[1:]):
            # both ends of the drawn segment on the leader's line
            if abs((c[0] - ax) * uy - (c[1] - ay) * ux) > tol or abs((d[0] - ax) * uy - (d[1] - ay) * ux) > tol:
                continue
            tc = ((c[0] - ax) * ux + (c[1] - ay) * uy, (d[0] - ax) * ux + (d[1] - ay) * uy)
            lo, hi = max(0.0, min(tc)), min(length, max(tc))
            if hi - lo > min_length:
                at = (ax + ux * (lo + hi) / 2.0, ay + uy * (lo + hi) / 2.0)
                if not any(math.hypot(at[0] - x, at[1] - y) < clear * r for x, y, r in targets):
                    found.append(at)
    return found


def circle_near_box(centre, radius, box, gap):
    """Whether a circle comes within gap of a box (x0, y0, x1, y1), outside it or crossing it: a label touching a ring."""
    cx, cy = centre
    nx, ny = min(max(cx, box[0]), box[2]), min(max(cy, box[1]), box[3])
    nearest = math.hypot(cx - nx, cy - ny)
    farthest = max(math.hypot(cx - x, cy - y) for x in (box[0], box[2]) for y in (box[1], box[3]))
    return nearest <= radius + gap and farthest >= radius - gap


def lines_through_box(polylines, box):
    """Whether any polyline passes through a box (x0, y0, x1, y1): a line through a label."""
    return any(segment_hits_box(a, b, box) for points in polylines for a, b in zip(points, points[1:]))


def leaders_through_text(leaders, texts):
    """(leader, text) pairs where a leader crosses a text's measured box. texts is [(body, box)]."""
    return [(leader, body) for leader in leaders for body, box in texts if segment_hits_box(leader[0], leader[1], box)]


def ring_arcs(centre, radius, tags):
    """The ring left after a gap under each tag, as (start, end) angles in radians, counterclockwise.

    tags is [((x, y), tag_radius)], in the units of centre and radius. A white mask does not hide the
    ring in the layout view, so the ring must really stop at the tag. Returns [(0, 2*pi)] when no tag
    meets the ring, and [] when tags cover all of it."""
    full = 2 * math.pi
    gaps = []
    for (x, y), tag_radius in tags or []:
        d = math.hypot(x - centre[0], y - centre[1])
        if d > radius + tag_radius or d < abs(radius - tag_radius) or d == 0:
            continue
        half = math.acos(max(-1.0, min(1.0, (radius * radius + d * d - tag_radius * tag_radius) / (2 * radius * d))))
        middle = math.atan2(y - centre[1], x - centre[0]) % full
        gaps.append((middle - half, middle + half))
    if not gaps:
        return [(0.0, full)]
    gaps.sort()
    merged = [list(gaps[0])]
    for start, end in gaps[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    if merged[-1][1] - merged[0][0] >= full:  # the last gap wraps round into the first
        if len(merged) == 1:
            return []
        merged[0][0] = min(merged[0][0], merged[-1][0] - full)
        merged[0][1] = max(merged[0][1], merged[-1][1] - full)
        merged.pop()
    arcs = [(merged[i][1], merged[i + 1][0]) for i in range(len(merged) - 1)]
    arcs.append((merged[-1][1], merged[0][0] + full))
    return arcs


def outside(box, frame):
    """True when a bounding box (x0, y0, x1, y1) leaves its frame."""
    return box[0] < frame[0] or box[1] < frame[1] or box[2] > frame[2] or box[3] > frame[3]


def colour_language(texts):
    """Notes that still speak of colour on a black and white sheet."""
    return [t for t in texts if COLOUR_WORDS.search(t)]


def table_lookup(rows, category, item):
    """The one CSV row with this category and item. Raises when it is not exactly one, so a drawn
    table cannot quietly drift from its BOM or print a blank."""
    found = [r for r in rows if len(r) > 1 and r[0] == category and r[1] == item]
    if len(found) != 1:
        raise ValueError("BOM row %s / %s: %d matches, need exactly 1" % (category, item, len(found)))
    return found[0]


# ---- Hatch, as 2D segments in a face's own (u, v) coordinates. Conventions, not a checked standard. ----

def clip_out(segments, holes, margin=0.0):
    """Remove the parts of segments that pass through rectangular members inside the cut."""
    for lo_u, lo_v, hi_u, hi_v in holes:
        lo_u, lo_v, hi_u, hi_v = lo_u - margin, lo_v - margin, hi_u + margin, hi_v + margin
        result = []
        for (a, b) in segments:
            t0, t1 = 0.0, 1.0
            inside = True
            for p, d, lo, hi in ((a[0], b[0] - a[0], lo_u, hi_u), (a[1], b[1] - a[1], lo_v, hi_v)):
                if abs(d) < 1e-12:
                    if p < lo or p > hi:
                        inside = False
                    continue
                u, v = sorted(((lo - p) / d, (hi - p) / d))
                t0, t1 = max(t0, u), min(t1, v)
            if not inside or t0 >= t1:
                result.append((a, b))
                continue
            at = lambda t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if t0 > 1e-9:
                result.append((a, at(t0)))
            if t1 < 1 - 1e-9:
                result.append((at(t1), b))
        segments = result
    return segments



def text_height_failure(body, asked_mm, drawn_mm, tolerance=TEXT_HEIGHT_TOLERANCE):
    """A failure when sheet text is drawn at another height than text() was asked for: drawn_mm is the height
    Rhino draws (text height times its dimension scale), so a dimension style's scale cannot enlarge it unseen."""
    if asked_mm > 0 and abs(drawn_mm / asked_mm - 1.0) > tolerance:
        return "text drawn at %.1f mm, asked %.1f mm: %s" % (drawn_mm, asked_mm, body)
    return None

def hatch_x(u0, v0, u1, v1):
    """Sawn lumber across the grain: corner to corner."""
    return [((u0, v0), (u1, v1)), ((u0, v1), (u1, v0))]


def hatch_plies(u0, v0, u1, v1, plies=3):
    """Plywood: lengthwise ply lines, along v."""
    return [((u0 + (u1 - u0) * k / plies, v0), (u0 + (u1 - u0) * k / plies, v1)) for k in range(1, plies)]


def hatch_grain(u0, v0, u1, v1, seed=0):
    """Boards cut along the grain: broken lengthwise grain lines."""
    rng, out = random.Random(seed), []
    for fraction in (0.28, 0.52, 0.76):
        v = v0 + rng.uniform(0.0, 0.1) * (v1 - v0)
        while v < v1 - 0.01 * (v1 - v0):
            end = min(v + 0.3 * (v1 - v0), v1)
            out.append(((u0 + (u1 - u0) * fraction, v), (u0 + (u1 - u0) * fraction, end)))
            v = end + 0.07 * (v1 - v0)
    return out


def hatch_diagonal(u0, v0, u1, v1, spacing):
    """Timber with no boards modeled: a general diagonal, with no invented board joints."""
    height = v1 - v0
    out, u = [], u0
    while u + height <= u1 + 1e-9:
        out.append(((u, v0), (u + height, v1)))
        u += spacing
    return out


def hatch_dense(u0, v0, u1, v1, lines=3):
    """Steel in section at small scale: near-solid, along the longer direction."""
    return [((u0 + (u1 - u0) * k / (lines + 1), v0), (u0 + (u1 - u0) * k / (lines + 1), v1)) for k in range(1, lines + 1)]


def hatch_concrete(u0, v0, u1, v1, holes=(), seed=11, grid=(9, 8), aggregate_grid=(4, 3), edge=0.012, aggregate=(0.009, 0.014), unit=1.0):
    """Concrete: stipple and aggregate triangles on a stratified grid with a fixed seed.

    Plain random clumps visibly, and a fixed seed keeps reruns identical. Holes are left clear. Sizes are
    in metres; unit is one metre in the face's units, such as 39.37 in an inch model."""
    rng = random.Random(seed)
    edge, aggregate, dot = edge * unit, (aggregate[0] * unit, aggregate[1] * unit), 0.0016 * unit
    lo_u, hi_u, lo_v, hi_v = u0 + edge, u1 - edge, v0 + edge, v1 - edge

    def blocked(u, v):
        return any(a - edge < u < c + edge and b - edge < v < d + edge for a, b, c, d in holes)

    out = []
    for i in range(grid[0]):
        for j in range(grid[1]):
            u = lo_u + (hi_u - lo_u) * (i + rng.random()) / grid[0]
            v = lo_v + (hi_v - lo_v) * (j + rng.random()) / grid[1]
            if not blocked(u, v):
                out.append(((u, v), (u + dot, v + dot)))
    for i in range(aggregate_grid[0]):
        for j in range(aggregate_grid[1]):
            u = lo_u + edge + (hi_u - lo_u - 2 * edge) * (i + 0.2 + 0.6 * rng.random()) / aggregate_grid[0]
            v = lo_v + edge + (hi_v - lo_v - 2 * edge) * (j + 0.2 + 0.6 * rng.random()) / aggregate_grid[1]
            r, turn = rng.uniform(*aggregate), rng.uniform(0, 2.1)
            if blocked(u, v):
                continue
            corners = [(u + r * math.cos(turn + k * 2.094), v + r * math.sin(turn + k * 2.094)) for k in range(3)]
            out += [(corners[k], corners[(k + 1) % 3]) for k in range(3)]
    return out


def select(names, patterns):
    """The names that match any of the glob patterns."""
    return [n for n in names if any(fnmatch.fnmatchcase(n, p) for p in patterns)]
