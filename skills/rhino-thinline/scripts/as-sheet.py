#! python3
"""Black and white vector sheets from a Rhino model (Arch Studio, as-rhino-thinline).

A library, not a program: the sheet script you write in run_python loads it and calls these functions.

    P = "<absolute path of this skill's folder>/scripts/as-sheet.py"
    S = {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P}
    exec(compile(open(P).read(), P, "exec"), S)
    sheet = S["setup_sheet"](d, "Sheet 1", 914.4, 609.6, target, direction, 1 / 40.0, "Sheet 1")

Page positions are in page units; multiply mm by S["mm"](d). World positions are in model units.
Weights in WEIGHTS are starting values accepted on screen and not proven in print.
"""
import csv
import hashlib
import itertools
import json
import math
import os
import time

import Rhino
import Rhino.Geometry as G
import System
import System.Drawing as SD
from Rhino.Geometry import HiddenLineDrawing, HiddenLineDrawingParameters

HERE = os.path.dirname(os.path.abspath(globals().get("AS_SCRIPT_FILE") or globals().get("__file__") or "."))
_core = os.path.join(HERE, "as-sheet-core.py")
exec(compile(open(_core, encoding="utf-8").read(), _core, "exec"), globals())

# Line weights in mm, set as layer PlotWeight. Provisional: accepted on screen, not proven in print.
WEIGHTS = {
    "main_outline": 0.35, "main_edge": 0.18, "main_receding": 0.09, "main_guide": 0.09,
    "detail_outline": 0.50, "detail_edge": 0.18, "detail_hatch": 0.09,
    "annotation": 0.18, "locator": 0.25, "ring": 0.50,
}


def mm(doc):
    """One millimetre in page units."""
    return Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Millimeters, doc.PageUnitSystem)


def live_objects(doc):
    """Every live object, hidden and locked included."""
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.HiddenObjects = True
    settings.LockedObjects = True
    return list(doc.Objects.GetObjectList(settings))


def layer_path(doc, item):
    layer = doc.Layers[item.Attributes.LayerIndex]
    return None if layer.IsDeleted else layer.FullPath


def layer_index(doc, path, weight=None):
    """Find or create a black layer by full path, with an optional PlotWeight in mm."""
    index = doc.Layers.FindByFullPath(path, -1)
    if index < 0:
        layer = Rhino.DocObjects.Layer()
        if "::" in path:
            parent, leaf = path.rsplit("::", 1)
            layer.Name, layer.ParentLayerId = leaf, doc.Layers[layer_index(doc, parent)].Id
        else:
            layer.Name = path
        layer.Color = SD.Color.Black
        index = doc.Layers.Add(layer)
    if weight is not None:
        layer = doc.Layers[index]
        layer.PlotWeight, layer.Color, layer.PlotColor = weight, SD.Color.Black, SD.Color.Black
        layer.CommitChanges()
    return index


def clear(doc, root):
    """Delete the objects on a layer and its sublayers, so a rerun replaces, not adds."""
    for layer in [x for x in doc.Layers if not x.IsDeleted and x.FullPath and (x.FullPath == root or x.FullPath.startswith(root + "::"))]:
        for item in list(doc.Objects.FindByLayer(layer) or []):
            doc.Objects.Delete(item, True)


def find_page(doc, name):
    found = [v for v in doc.Views.GetPageViews() if v.PageName == name]
    if not found:
        raise ValueError("no layout named %s" % name)
    return found[0]


def page_attr(doc, page, index, name):
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex, attr.Name = index, name
    attr.Space = Rhino.DocObjects.ActiveSpace.PageSpace
    attr.ViewportId = page.MainViewport.Id
    return attr


def strings_of(doc):
    table = getattr(doc, "Strings", None) if doc is not None else None
    return [(table.GetKey(i), table.GetValue(i)) for i in range(table.Count)] if table is not None else []


def new_page(doc, name, width_mm, height_mm, page_units=None):
    """Create a layout and make it active. Refuses an existing name, so a rerun cannot stack pages, and refuses a
    window document that is not the active one: see the unconfirmed hazard in references/sheets.md. A headless
    document is never the active one, so it is accepted, and the active document's strings are compared around
    the page creation; a change is reported, never kept quiet."""
    active = Rhino.RhinoDoc.ActiveDoc
    headless = bool(getattr(doc, "IsHeadless", False))
    if not headless and (active is None or active.RuntimeSerialNumber != doc.RuntimeSerialNumber):
        raise ValueError("this document is not Rhino's active document; make it active before creating a page")
    watch = active if headless and active is not None else None
    before = strings_of(watch)
    if [p for p in doc.Views.GetPageViews() if p.PageName == name]:
        raise ValueError("a layout named %s already exists; use it or remove it first" % name)
    if page_units is not None:
        doc.AdjustPageUnitSystem(page_units, False)
    one_mm = mm(doc)
    page = doc.Views.AddPageView(name, width_mm * one_mm, height_mm * one_mm)
    if page is None:
        raise ValueError("could not add the layout %s" % name)
    doc.Views.ActiveView = page
    if watch is not None and strings_of(watch) != before:
        print("WARNING: creating the page changed the strings of Rhino's active document")
    return page


def plot_rect(doc, page, index, box, name, weight):
    """A page rectangle with its own plot weight in mm: sheet border, title column."""
    x0, y0, x1, y1 = box
    attr = page_attr(doc, page, index, name)
    attr.PlotWeightSource = Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
    attr.PlotWeight = weight
    points = [G.Point3d(x0, y0, 0), G.Point3d(x1, y0, 0), G.Point3d(x1, y1, 0), G.Point3d(x0, y1, 0), G.Point3d(x0, y0, 0)]
    return doc.Objects.AddCurve(G.Polyline(points).ToNurbsCurve(), attr)


BUILDING_KEY = "as-sheet:building"
REQUESTS_KEY = "as-sheet:requests"      # every label, locator and detail asked for, chained (ledger_append)
SEAL_KEY = "as-sheet:requests-seal"     # count and head hash of the requests; check_sheet fails a mismatch


def string_value(doc, key):
    """A document string by key, or None. Reads by index, so it needs only Count, GetKey and GetValue."""
    table = getattr(doc, "Strings", None) if doc is not None else None
    for i in range(table.Count if table is not None else 0):
        if table.GetKey(i) == key:
            return table.GetValue(i)
    return None


def record_request(doc, kind, key, message=None, **extra):
    """Append one request to the sheet's ledger: kind "sheet", "label", "locator" or "detail", its key (label
    text or detail tag) and, for a failed attempt, the failure. check_sheet recomputes from the sheet whether
    each request is drawn, and fails a ledger that was edited or deleted: a request is never withdrawn."""
    stored = string_value(doc, REQUESTS_KEY)
    entries = json.loads(stored) if stored else []
    entry = dict(extra, kind=kind, key=key)
    if message:
        entry["message"] = message
    entries, seal = ledger_append(entries, entry)
    doc.Strings.SetString(REQUESTS_KEY, json.dumps(entries))
    doc.Strings.SetString(SEAL_KEY, json.dumps(seal))


def new_sheet(doc, name, width_mm, height_mm, root, margin_mm=12.0, title_column_mm=160.0, page_units=None):
    """The page, its border and title column, and the drawing field beside the title column. It also starts the
    sheet's request ledger, which check_sheet needs (covering the building record when a view has made one): a sheet
    not started here fails check_sheet. Returns {"page", "field", "title"}. Sheet layers go under root. It chooses
    no view: as-rhino-axon's setup_sheet puts the main detail in the field."""
    started = string_value(doc, REQUESTS_KEY)
    first = (json.loads(started) or [{}])[0] if started else {}
    if started and first.get("kind") == "sheet" and first.get("key") != name:
        # One sheet per document: the request record, the building record and the main drawing's settings are
        # document-wide, so a second sheet's requests would land in the first sheet's record and fail its check.
        raise ValueError("this document already holds the sheet %r, and its request, building and main drawing records "
                         "are for that sheet only; draw %r in another document that holds the model but no sheet, "
                         "and never delete the records to make room" % (first.get("key"), name))
    if started is None:
        building = doc.Strings.GetValue(BUILDING_KEY)
        record_request(doc, "sheet", name, **({"building": hashlib.sha256(building.encode("utf-8")).hexdigest()} if building else {}))
    page = new_page(doc, name, width_mm, height_mm, page_units)
    one_mm = mm(doc)
    width, height, margin = width_mm * one_mm, height_mm * one_mm, margin_mm * one_mm
    title_x = width - margin - title_column_mm * one_mm
    index = layer_index(doc, root + "::Border")
    plot_rect(doc, page, index, (margin, margin, width - margin, height - margin), "Sheet border", WEIGHTS["ring"])
    title_box = (title_x, margin, width - margin, height - margin)
    plot_rect(doc, page, index, title_box, "Title column", WEIGHTS["detail_outline"])
    field = (margin, margin, title_x, height - margin)
    return {"page": page, "field": field, "title": title_box}


def text(doc, page, index, x, y, body, height, name, bold=False, justification=None, font="Helvetica"):
    """Add page text and return its id. Raises when Rhino refuses it.

    With no justification, x is the left of the text and y is its top, so the text hangs below y. For
    another anchor pass one, such as G.TextJustification.MiddleCenter."""
    plane = G.Plane(G.Point3d(x, y, 0), G.Vector3d.ZAxis)
    attr = page_attr(doc, page, index, name)
    attr.SetUserString(TEXT_HEIGHT_KEY, "%.4f" % (height / mm(doc)))
    if justification is None:
        guid = doc.Objects.AddText(body, plane, height, font, bold, False, attr)
    else:
        guid = doc.Objects.AddText(body, plane, height, font, bold, False, justification, attr)
    if guid == System.Guid.Empty:
        raise ValueError("text failed: " + body)
    # Page text takes the document's current dimension style, whose dimension scale multiplies its height: Rhino's
    # Foot-Inch Architectural style has 96, which turns 7 mm text into 670 mm. Sheet text is sized on the page itself.
    entity = doc.Objects.FindId(guid).Geometry
    if abs(entity.DimensionScale - 1.0) > 1e-9:
        entity.DimensionScale = 1.0
        if not doc.Objects.Replace(guid, entity):
            raise ValueError("text scale could not be reset: " + body)
    return guid


def text_box(doc, guid):
    """Measured bounding box of text, as (x0, y0, x1, y1). Estimates by character have been wrong by half."""
    box = doc.Objects.FindId(guid).Geometry.GetBoundingBox(True)
    return box.Min.X, box.Min.Y, box.Max.X, box.Max.Y


def add_line(doc, page, index, a, b, name):
    return doc.Objects.AddLine(G.Point3d(a[0], a[1], 0), G.Point3d(b[0], b[1], 0), page_attr(doc, page, index, name))


def add_circle(doc, page, index, centre, radius, name):
    return doc.Objects.AddCircle(G.Circle(G.Point3d(centre[0], centre[1], 0), radius), page_attr(doc, page, index, name))


def solid_pattern_index(doc):
    """The document's Solid hatch pattern, added when the table has none."""
    found = doc.HatchPatterns.FindName("Solid")
    if found is not None:
        return found.Index
    index = doc.HatchPatterns.Add(Rhino.DocObjects.HatchPattern.Defaults.Solid)
    if index < 0:
        raise ValueError("could not add the Solid hatch pattern")
    return index


def white_mask(doc, page, index, centre, radius, name):
    """A solid white disc that hides linework behind a balloon. Add it before the ring; object and plot colour both white."""
    disc = G.Circle(G.Point3d(centre[0], centre[1], 0), radius).ToNurbsCurve()
    hatches = G.Hatch.Create(disc, solid_pattern_index(doc), 0, 1, 0.001)
    attr = page_attr(doc, page, index, name)
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attr.ObjectColor = SD.Color.White
    attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
    attr.PlotColor = SD.Color.White
    for hatch in hatches:
        doc.Objects.AddHatch(hatch, attr)


def leader_dot(doc, page, index, at, name, radius_mm=0.6):
    """A solid black dot where a leader lands on the part, so the reader knows which part it names."""
    disc = G.Circle(G.Point3d(at[0], at[1], 0), radius_mm * mm(doc)).ToNurbsCurve()
    attr = page_attr(doc, page, index, name)
    for hatch in G.Hatch.Create(disc, solid_pattern_index(doc), 0, 1, 0.001):
        doc.Objects.AddHatch(hatch, attr)


def label(doc, page, index, body, world_anchor, at, main_detail, height_mm=2.5):
    """A component label: text at `at` (page units, the text's left end on its middle line) and an orthogonal
    leader from the text to the part, ending in a dot on it. The anchor is a world point on the part, projected
    through the main detail, so the dot sits on the real part. Returns the text id."""
    one_mm = mm(doc)
    p = G.Point3d(world_anchor)
    p.Transform(main_detail.WorldToPageTransform)
    guid = text(doc, page, index, at[0], at[1], body, height_mm * one_mm, "Label text", False, G.TextJustification.MiddleLeft)
    x0, y0, x1, y1 = text_box(doc, guid)
    start = (x0 - 1.0 * one_mm, at[1]) if p.X < x0 else (x1 + 1.0 * one_mm, at[1])
    add_line(doc, page, index, start, (p.X, at[1]), "Label leader")
    if abs(p.Y - at[1]) > 1e-6:
        add_line(doc, page, index, (p.X, at[1]), (p.X, p.Y), "Label leader")
    leader_dot(doc, page, index, (p.X, p.Y), "Label dot")
    return guid


def visible_points(doc, main_detail, world_points):
    """Every world point counts as visible here: conventions choose no view. as-rhino-axon, loaded after this file,
    replaces this with its occlusion test, which drops points another part covers in the main view."""
    return list(world_points)


def place_label(doc, page, index, body, world_points, main_detail, main_root, height_mm=2.5, gap_mm=8.0):
    """A component label in the clear space nearest its part: the shortest straight leader, in any of four
    directions, from clear paper (beside the drawing, or inside it, such as over a window's open glass) to a dot
    on the part, crossing no main linework, other leader, ring or text, with the text clear of them too. world_points are points on the
    part's visible faces; points another part covers in the main view are dropped first (visible_points). The one
    nearest the outline with a clear route wins. Returns the world point, or None when no point is visible or no
    route is clear: then nothing is drawn and check_sheet fails the sheet, naming the label."""
    one_mm = mm(doc)
    lines, box = page_curves(doc, page, main_root)
    obstacles = lines + page_obstacles(doc, page)
    outline = (box.Min.X, box.Min.Y, box.Max.X, box.Max.Y)
    world_points = visible_points(doc, main_detail, world_points)
    if not world_points:
        record_request(doc, "label", body, "label %r: every point given is covered by another part in the main view; give points on the part's visible faces or change the view" % body)
        return None
    targets = []
    for world in world_points:
        p = G.Point3d(world)
        p.Transform(main_detail.WorldToPageTransform)
        targets.append((p.X, p.Y))
    probe = text(doc, page, index, 0, 0, body, height_mm * one_mm, "Label text", False, G.TextJustification.MiddleCenter)
    x0, y0, x1, y1 = text_box(doc, probe)
    doc.Objects.Delete(probe, True)
    size = (x1 - x0, y1 - y0)
    found = pick_label(targets, outline, gap_mm * one_mm, obstacles, 1.5 * one_mm, size, tuple(d * one_mm for d in (8, 14, 20, 30, 45)), 1.0 * one_mm)
    if found is None:
        record_request(doc, "label", body, "label %r: no leader to the part stays clear of the main drawing, the other leaders and text; give other points on the part or move the drawing" % body)
        return None
    k, side, start, end = found
    bx = label_box(side, start, size, 1.0 * one_mm)
    text(doc, page, index, (bx[0] + bx[2]) / 2.0, (bx[1] + bx[3]) / 2.0, body, height_mm * one_mm, "Label text", False, G.TextJustification.MiddleCenter)
    record_request(doc, "label", body)
    add_line(doc, page, index, start, end, "Label leader")
    leader_dot(doc, page, index, end, "Label dot")
    return world_points[k]


def callout(doc, page, index, number, anchor, offset, radius, height):
    """A numbered balloon over a white mask, with a straight leader to a dot on the anchor."""
    q = (anchor[0] + offset[0], anchor[1] + offset[1])
    dx, dy = anchor[0] - q[0], anchor[1] - q[1]
    length = math.hypot(dx, dy)
    start = (q[0] + dx / length * radius, q[1] + dy / length * radius)
    add_line(doc, page, index, start, anchor, "Callout leader %s" % number)
    leader_dot(doc, page, index, anchor, "Callout dot %s" % number)
    white_mask(doc, page, index, q, radius, "Callout backing %s" % number)
    add_circle(doc, page, index, q, radius, "Callout balloon %s" % number)
    return text(doc, page, index, q[0], q[1], str(number), height, "Callout number %s" % number, True, G.TextJustification.MiddleCenter)


def detail_tag(doc, page, index, tag, centre_mm, radius_mm=7.0):
    """The tag on a detail ring: a white mask, a circle and the tag text, named "Detail tag ..." so
    check_sheet can find it and fail any line drawn through it."""
    one_mm = mm(doc)
    c = (centre_mm[0] * one_mm, centre_mm[1] * one_mm)
    white_mask(doc, page, index, c, radius_mm * one_mm, "Detail tag mask %s" % tag)
    add_circle(doc, page, index, c, radius_mm * one_mm, "Detail tag ring %s" % tag)
    return text(doc, page, index, c[0], c[1], tag, 4.0 * one_mm, "Detail tag text %s" % tag, True, G.TextJustification.MiddleCenter)


def locator(doc, page, index, tag, ring_centre, ring_radius, world_target, main_detail, route=None, ring_at=None, legs=None):
    """An orthogonal leader from a detail ring to the real joint on the main drawing. legs, from
    place_locator, overrides the route."""
    point = G.Point3d(world_target)
    point.Transform(main_detail.WorldToPageTransform)
    stop = 5.0 * mm(doc)
    for a, b in legs or locator_route(ring_centre, ring_radius, (point.X, point.Y), stop, route):
        add_line(doc, page, index, a, b, "Locator leader %s" % tag)
    add_circle(doc, page, index, (point.X, point.Y), stop, "Locator ring %s" % tag)
    return point.X, point.Y


def page_curves(doc, page, root):
    """Polylines and page extents of the curves under a layer root on a page."""
    lines, box = [], G.BoundingBox.Empty
    for layer in [x for x in doc.Layers if not x.IsDeleted and x.FullPath and (x.FullPath == root or x.FullPath.startswith(root + "::"))]:
        for item in doc.Objects.FindByLayer(layer) or []:
            if item.Attributes.ViewportId == page.MainViewport.Id and isinstance(item.Geometry, G.Curve):
                lines.append(polyline_points(item.Geometry, 0.05 * mm(doc)))
                box.Union(item.Geometry.GetBoundingBox(True))
    return lines, box


def page_obstacles(doc, page):
    """Polylines a new locator or label must not cross besides the main drawing: other details' rings, the
    leaders already drawn and the boxes of all page text."""
    out = []
    for item in live_objects(doc):
        if item.Attributes.ViewportId != page.MainViewport.Id:
            continue
        if (item.Attributes.Name or "").startswith(("Bubble ring", "Locator leader", "Label leader")) and isinstance(item.Geometry, G.Curve):
            out.append(polyline_points(item.Geometry, 0.05 * mm(doc)))
        elif isinstance(item.Geometry, G.TextEntity):
            b = item.Geometry.GetBoundingBox(True)
            out.append([(b.Min.X, b.Min.Y), (b.Max.X, b.Min.Y), (b.Max.X, b.Max.Y), (b.Min.X, b.Max.Y), (b.Min.X, b.Min.Y)])
    return out


def title_block(doc, page, index, frame, title_rows, cells, padding_mm=7.0):
    """A title block on an explicit grid. title_rows is [(text, height_mm, bold)] from the top; cells is
    rows of [(label, value)], one shared baseline per row, one padding constant."""
    one_mm = mm(doc)
    x0, y0, x1, y1 = frame
    pad = padding_mm * one_mm
    y = y1 - 6 * one_mm
    for body, height, bold in title_rows:
        text(doc, page, index, x0 + pad, y, body, height * one_mm, "Title", bold)
        y -= (height + 5.0) * one_mm
    row_height = 18.0 * one_mm
    add_line(doc, page, index, (x0, y0 + row_height * len(cells)), (x1, y0 + row_height * len(cells)), "Title block rule")
    for r, row in enumerate(cells):
        top = y0 + row_height * (len(cells) - r)
        add_line(doc, page, index, (x0, top - row_height), (x1, top - row_height), "Title block rule")
        width = (x1 - x0) / float(len(row))
        for c, (label, value) in enumerate(row):
            x = x0 + c * width
            if c:
                add_line(doc, page, index, (x, top - row_height), (x, top), "Title block rule")
            text(doc, page, index, x + pad, top - 3.5 * one_mm, label, 2.6 * one_mm, "Title label", True)
            text(doc, page, index, x + pad, top - 10.5 * one_mm, value, 3.1 * one_mm, "Title value")


def bom_rows(path):
    """A BOM CSV as lists; pair with table_lookup so a drawn table fails on any mismatch."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def polyline_points(curve, tolerance):
    ok, polyline = curve.TryGetPolyline()
    if not ok:
        ok, polyline = curve.ToPolyline(tolerance, 0.1, 0, 0).TryGetPolyline()
    return [(p.X, p.Y) for p in polyline] if ok else []


def read_sheet(doc, page_name, root, frames, field=None):
    """What check_sheet reads from a sheet's own objects under a layer root, collected once: text and its boxes,
    leaders, locator rings, detail tags, label dots and the composite's extents, with the text-frame failures.
    Returns the collection (a dict) for check_conventions, as-rhino-axon's check_view and check_layout."""
    page = find_page(doc, page_name)
    one_mm = mm(doc)
    failures, texts, segments, locators, boxes, targets, drawing, rings = [], [], [], [], [], [], [], []
    extents = G.BoundingBox.Empty if field is not None else None
    tagged, tags, page_lines, label_legs, dots = [], {}, [], [], []
    drawn_names = {}
    items = []
    for layer in [x for x in doc.Layers if not x.IsDeleted and x.FullPath and (x.FullPath == root or x.FullPath.startswith(root + "::"))]:
        items += [i for i in (doc.Objects.FindByLayer(layer) or []) if i.Attributes.ViewportId == page.MainViewport.Id]
    for item in items:
        name = item.Attributes.Name or ""
        drawn_names.setdefault(name, []).append(item)
        if isinstance(item.Geometry, G.TextEntity):
            box = item.Geometry.GetBoundingBox(True)
            bounds = (box.Min.X, box.Min.Y, box.Max.X, box.Max.Y)
            texts.append(item.Geometry.PlainText)
            boxes.append((item.Geometry.PlainText, bounds))
            for pattern, frame in frames:
                if fnmatch.fnmatchcase(name, pattern) and outside(bounds, frame):
                    failures.append("text outside its frame: %s" % item.Geometry.PlainText)
            asked = item.Attributes.GetUserString(TEXT_HEIGHT_KEY)
            if asked:
                drawn = item.Geometry.TextHeight * item.Geometry.DimensionScale / one_mm
                failure = text_height_failure(item.Geometry.PlainText, float(asked), drawn)
                if failure:
                    failures.append(failure)
        elif "Locator leader" in name or "label leader" in name.lower():
            c = item.Geometry
            segments.append(((c.PointAtStart.X, c.PointAtStart.Y), (c.PointAtEnd.X, c.PointAtEnd.Y)))
            if "Locator leader" in name:
                locators.append(segments[-1])
                tagged.append((name.split()[-1], segments[-1]))
            else:
                label_legs.append(segments[-1])
        elif name == "Label dot":
            b = item.Geometry.GetBoundingBox(True)
            dots.append(((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0, 1.5 * one_mm))
        if name.startswith("Detail tag ring") and isinstance(item.Geometry, G.Curve):
            b = item.Geometry.GetBoundingBox(True)
            tags[name.split()[-1]] = ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0, (b.Max.X - b.Min.X) / 2.0)
        elif isinstance(item.Geometry, G.Curve) and not name.startswith(("Detail tag", "Bubble ring")):
            page_lines.append((name, item.Geometry))
        if name.startswith("Bubble ring") and isinstance(item.Geometry, G.Curve):
            rings.append((name.split()[-1], polyline_points(item.Geometry, 0.05 * one_mm)))
        elif "Locator ring" in name:
            c = item.Geometry.GetBoundingBox(True)
            targets.append(((c.Min.X + c.Max.X) / 2.0, (c.Min.Y + c.Max.Y) / 2.0, (c.Max.X - c.Min.X) / 2.0))
        if field is not None and name not in ("Sheet border", "Title column") and not isinstance(item.Geometry, getattr(G, "DetailView", ())):
            b = item.Geometry.GetBoundingBox(True)
            centre = ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0)
            if not outside(centre * 2, field):
                extents.Union(b)
    return dict(locals())


def check_conventions(s):
    """Drawing conventions on a read sheet: lines through labels and detail tags, labels touching rings, locator
    leaders through other rings or into their own detail, leaders sharing a segment, and the request ledger (an
    edited or deleted record fails, and every requested label, locator and detail must be drawn). Adds to s["failures"]."""
    doc, failures, boxes, page_lines, one_mm, rings, tags, tagged, label_legs, drawn_names = [s[k] for k in ('doc', 'failures', 'boxes', 'page_lines', 'one_mm', 'rings', 'tags', 'tagged', 'label_legs', 'drawn_names')]
    for body, bounds in boxes:
        pad = 0.5 * one_mm
        grown = (bounds[0] - pad, bounds[1] - pad, bounds[2] + pad, bounds[3] + pad)
        for name, curve in page_lines:
            if name.startswith(("Detail tag", "Sheet border", "Title")) or "Locator" in name:
                continue
            b = curve.GetBoundingBox(True)
            if b.Max.X < grown[0] or b.Min.X > grown[2] or b.Max.Y < grown[1] or b.Min.Y > grown[3]:
                continue
            if lines_through_box([polyline_points(curve, 0.05 * one_mm)], grown):
                failures.append("a line runs through the label %r: %s" % (body[:40], name or "unnamed"))
                break
        for ring_tag, ring in rings:
            xs, ys = [p[0] for p in ring], [p[1] for p in ring]
            if not xs:
                continue
            centre, radius = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0), (max(xs) - min(xs)) / 2.0
            if body != ring_tag and circle_near_box(centre, radius, bounds, 1.0 * one_mm):
                failures.append("the label %r touches the ring of detail %s" % (body[:40], ring_tag))
    for tag_name, (cx, cy, r) in tags.items():
        for name, curve in page_lines:
            b = curve.GetBoundingBox(True)
            if b.Max.X < cx - r or b.Min.X > cx + r or b.Max.Y < cy - r or b.Min.Y > cy + r:
                continue
            if through_circle(polyline_points(curve, 0.05 * one_mm), (cx, cy), r):
                failures.append("a line runs through detail tag %s: %s" % (tag_name, name or "unnamed"))
                break
    circles = {}
    for ring_tag, ring in rings:
        circles.setdefault(ring_tag, []).extend(ring)
    for ring_tag, pts in list(circles.items()):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        circles[ring_tag] = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, (max(xs) - min(xs)) / 2.0) if pts else None
    for tag, leader in tagged:
        for ring_tag, ring in rings:
            if ring_tag != tag and leader_crossings([leader], [ring], []):
                failures.append("locator leader %s through the ring of detail %s" % (tag, ring_tag))
        own = circles.get(tag)
        if own and point_segment_distance(own[:2], leader[0], leader[1]) < 0.98 * own[2]:
            failures.append("locator leader %s enters its own detail" % tag)
    for i, (tag_a, a) in enumerate(tagged):
        for tag_b, b in tagged[i + 1:]:
            if tag_a != tag_b and collinear_runs(a, [list(b)], 0.3 * one_mm, 1.0 * one_mm):
                failures.append("locator leaders %s and %s share a segment" % (tag_a, tag_b))
    every = [("locator " + t, s) for t, s in tagged] + [("label", s) for s in label_legs]
    for i, (na, a) in enumerate(every):
        for nb, b in every[i + 1:]:
            if (na == "label" or nb == "label") and collinear_runs(a, [list(b)], 0.3 * one_mm, 1.0 * one_mm):
                failures.append("a label leader shares a segment with another leader (%s, %s)" % (na, nb))
    stored = string_value(doc, BUILDING_KEY)
    ledger, seal = string_value(doc, REQUESTS_KEY), string_value(doc, SEAL_KEY)
    ledger, seal = (json.loads(ledger) if ledger else None), (json.loads(seal) if seal else None)
    failures += ledger_problems(ledger, seal, stored)
    if ledger:
        def tagged_names(prefix):
            return {n[len(prefix):] for n in drawn_names if n.startswith(prefix)}
        drawn = {"label": {i.Geometry.PlainText for i in drawn_names.get("Label text", []) if isinstance(i.Geometry, G.TextEntity)},
                 "locator": tagged_names("Locator leader ") & tagged_names("Locator ring "),
                 "detail": tagged_names("Bubble ring ") & tagged_names("Bubble linework ")}
        failures += unmet_requests(ledger, drawn)


def check_layout(s):
    """Layout conventions on a read sheet: margins of the composite against the fixed MIN_MARGIN_MM (with field),
    axis-aligned leaders, no locator leader through text, no colour language. Adds to s["failures"]."""
    failures, field, extents, one_mm, segments, locators, boxes, texts = [s[k] for k in ('failures', 'field', 'extents', 'one_mm', 'segments', 'locators', 'boxes', 'texts')]
    if field is not None and extents.IsValid:
        found = margins((extents.Min.X, extents.Min.Y, extents.Max.X, extents.Max.Y), field)
        print("margins mm", {k: round(v / one_mm, 1) for k, v in found.items()})
        for side, value in found.items():
            if value < MIN_MARGIN_MM * one_mm:
                failures.append("%s margin %.1f mm, under %.1f" % (side, value / one_mm, MIN_MARGIN_MM))
    for segment in axis_aligned(segments):
        failures.append("diagonal leader: %s" % (segment,))
    for _leader, body in leaders_through_text(locators, boxes):
        failures.append("locator leader through text: %s" % body)
    for note in colour_language(texts):
        failures.append("colour language on a black and white sheet: %s" % note)


def check_sheet(doc, page_name, root, frames, field=None):
    """The conventions half of a sheet check, for linework drawn by any view: text inside frames, lines clear of
    labels and tags, leaders axis-aligned and not through text or rings, no colour language, margins against the
    fixed MIN_MARGIN_MM with field, and the request ledger (an edited or deleted request, seal or building record
    fails, and every requested label, locator and detail must be drawn). No limit is a parameter: when a check
    fails, fix the sheet, never the check. Never delete a failure record or request to pass a check; report what
    could not be placed. as-rhino-axon replaces this with the full check (these plus the view), in one order.

    frames is [(name glob, (x0, y0, x1, y1))]. Returns failures, empty when none."""
    s = read_sheet(doc, page_name, root, frames, field)
    check_conventions(s)
    check_layout(s)
    return s["failures"]


def preview_sheet(doc, page, path, dpi=100):
    """Draw the layout's own page objects to a PNG at dpi, so the sheet can be looked at (procedure step 5)
    where there is no viewport. Rhino's view capture draws nothing for a headless document, so this
    rasterises the vector objects itself: curves at their plot weights, white masks, text. Live detail
    content is not drawn (main_linework hides it anyway).

    Returns a text summary, also printed, for a host that shows tool results as text only: the PNG path,
    the closest pairs of detail rings, locator leaders and text with their distances in mm, the elements
    closest to the drawing field's edge, and any detail ring that is mostly empty."""
    one_mm = mm(doc)
    px = dpi / 25.4 / one_mm
    width, height = int(page.PageWidth * px), int(page.PageHeight * px)
    bitmap = SD.Bitmap(width, height)
    g = SD.Graphics.FromImage(bitmap)
    g.Clear(SD.Color.White)
    g.SmoothingMode = SD.Drawing2D.SmoothingMode.AntiAlias
    black, white = SD.SolidBrush(SD.Color.Black), SD.SolidBrush(SD.Color.White)

    def points(curve):
        return System.Array[SD.PointF]([SD.PointF(float(x * px), float(height - y * px)) for x, y in polyline_points(curve, 0.05 * one_mm)])

    def weight(item):
        a = item.Attributes
        w = a.PlotWeight if a.PlotWeightSource == Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject else doc.Layers[a.LayerIndex].PlotWeight
        return max(1.0, (w if w > 0 else 0.13) * dpi / 25.4)

    items = sorted((i for i in live_objects(doc) if i.Attributes.ViewportId == page.MainViewport.Id), key=lambda i: i.RuntimeSerialNumber)
    for item in items:
        geometry = item.Geometry
        if isinstance(geometry, G.Hatch):
            fill = white if item.Attributes.ObjectColor.R > 200 and item.Attributes.ColorSource == Rhino.DocObjects.ObjectColorSource.ColorFromObject else black
            for loop in geometry.Get3dCurves(True) or []:
                pts = points(loop)
                if len(pts) > 2:
                    g.FillPolygon(fill, pts)
        elif isinstance(geometry, G.Curve):
            pts = points(geometry)
            if len(pts) > 1:
                pen = SD.Pen(SD.Color.Black, float(weight(item)))
                g.DrawLines(pen, pts)
                pen.Dispose()
        elif isinstance(geometry, G.TextEntity):
            b = geometry.GetBoundingBox(True)
            lines = geometry.PlainText.count("\n") + 1
            size = max(4.0, (b.Max.Y - b.Min.Y) * px / lines * 0.95)
            font = SD.Font("Helvetica", float(size), SD.GraphicsUnit.Pixel)
            g.DrawString(geometry.PlainText, font, black, SD.PointF(float(b.Min.X * px), float(height - b.Max.Y * px)))
            font.Dispose()
    g.Dispose()
    bitmap.Save(path, SD.Imaging.ImageFormat.Png)
    bitmap.Dispose()
    summary = "PNG: %s\n%s" % (path, sheet_summary(doc, page))
    print(summary)
    return summary


def sheet_summary(doc, page):
    """layout_summary of a page's own objects: detail rings, locator leaders and text, the field taken as the
    sheet border less the title column (or the page), and how much of each detail ring its linework fills."""
    one_mm = mm(doc)
    rings, content, elements, border, title = {}, {}, [], None, None
    items = [i for i in live_objects(doc) if i.Attributes.ViewportId == page.MainViewport.Id]
    for item in items:   # the frames first, so the title column's text can be left out
        b = item.Geometry.GetBoundingBox(True)
        if item.Attributes.Name == "Sheet border":
            border = (b.Min.X, b.Min.Y, b.Max.X, b.Max.Y)
        elif item.Attributes.Name == "Title column":
            title = (b.Min.X, b.Min.Y, b.Max.X, b.Max.Y)
    for item in items:
        name, g = item.Attributes.Name or "", item.Geometry
        b = g.GetBoundingBox(True)
        if name in ("Sheet border", "Title column"):
            continue
        elif name.startswith("Bubble ring"):
            rings.setdefault(name.split()[-1], G.BoundingBox.Empty).Union(b)
        elif name.startswith("Bubble linework"):
            content.setdefault(name.split()[-1], G.BoundingBox.Empty).Union(b)
        elif name.startswith("Locator leader") and isinstance(g, G.Curve):
            elements.append(("leader %s" % name.split()[-1], name.split()[-1], ("poly", polyline_points(g, 0.05 * one_mm))))
        elif isinstance(g, G.TextEntity) and not name.startswith("Detail tag") and not (title and b.Min.X >= title[0]):
            body = " ".join(g.PlainText.split())[:30]
            tag = name.split()[-1] if name.split() and name.split()[-1][:1] == "D" and name.split()[-1][1:].isdigit() else ""
            elements.append(("text '%s'" % body, tag, ("poly", [(b.Min.X, b.Min.Y), (b.Max.X, b.Min.Y), (b.Max.X, b.Max.Y), (b.Min.X, b.Max.Y), (b.Min.X, b.Min.Y)])))
    fills = {}
    for tag, b in rings.items():
        r = (b.Max.X - b.Min.X) / 2.0
        elements.append(("ring %s" % tag, tag, ("circle", (b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0, r)))
        c = content.get(tag)
        fills[tag] = 0.0 if c is None or not c.IsValid else min(1.0, (c.Max.X - c.Min.X) * (c.Max.Y - c.Min.Y) / (math.pi * r * r))
    page_box = (0.0, 0.0, page.PageWidth, page.PageHeight)
    field = border or page_box
    if title:
        field = (field[0], field[1], title[0], field[3])
    return layout_summary(elements, field, one_mm, fills=fills)


def export_pdf(doc, page, path, dpi=300):
    """Vector PDF of a layout. Colour stays on PrintColor with everything already black."""
    pdf = Rhino.FileIO.FilePdf.Create()
    settings = Rhino.Display.ViewCaptureSettings(page, dpi)
    settings.OutputColor = Rhino.Display.ViewCaptureSettings.ColorMode.PrintColor
    pdf.AddPage(settings)
    pdf.Write(path)
    return path
