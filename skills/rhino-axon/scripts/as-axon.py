#! python3
"""The view for axonometric sheets from a Rhino model (Arch Studio, as-rhino-axon): camera and projection,
exclusions and crop, hidden-line occlusion, joint and detail-cut selection, and the building lock.

A library, not a program. It loads as-rhino-thinline's conventions library (line weights, styles, hatch, labels and
leaders, tags, title block, sheet layout, the request record and the PDF check) into the same namespace first, so
one load gives a script both:

    P = "<absolute path of this skill's folder>/scripts/as-axon.py"
    S = {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P}
    exec(compile(open(P).read(), P, "exec"), S)
    sheet = S["setup_sheet"](d, "Sheet 1", 914.4, 609.6, target, direction, 1 / 40.0, "Sheet 1")

The handoff: main_linework and cut_detail draw linework on the page (layers under their out_root, named for
thinline's stroke classes and weights) and keep their sources on the document; thinline's annotation and checks
read that linework from the page and never choose a view.
"""
import json
import math
import os
import time

import Rhino
import Rhino.Geometry as G
import System
from Rhino.Geometry import HiddenLineDrawing, HiddenLineDrawingParameters

_axon_file = os.path.abspath(globals().get("AS_SCRIPT_FILE") or globals().get("__file__") or ".")
_thinline = os.path.join(os.path.dirname(_axon_file), "..", "..", "rhino-thinline", "scripts", "as-sheet.py")
_thinline = os.path.normpath(_thinline)
globals()["AS_SCRIPT_FILE"] = _thinline        # thinline finds its own core from this
exec(compile(open(_thinline, encoding="utf-8").read(), _thinline, "exec"), globals())
globals()["AS_SCRIPT_FILE"] = _axon_file
HERE = os.path.dirname(_axon_file)
_axon_core = os.path.join(HERE, "as-axon-core.py")
exec(compile(open(_axon_core, encoding="utf-8").read(), _axon_core, "exec"), globals())


def model_add(doc, brep, index, name):
    """Add to model space even while a page view is active. Default attributes land in page space
    there, and the detail then shows blank."""
    attr = Rhino.DocObjects.ObjectAttributes()
    attr.LayerIndex, attr.Name = index, name
    guid = doc.Objects.AddBrep(brep, attr)
    fixed = doc.Objects.FindId(guid).Attributes.Duplicate()
    fixed.Space, fixed.ViewportId = Rhino.DocObjects.ActiveSpace.ModelSpace, System.Guid.Empty
    doc.Objects.ModifyAttributes(guid, fixed, True)
    return guid


def building_fingerprints(doc, root):
    """{id: layer|type|box} of every model-space object outside the sheet's root: the building as it stands."""
    out = {}
    for item in live_objects(doc):
        if item.Attributes.Space != Rhino.DocObjects.ActiveSpace.ModelSpace or isinstance(item.Geometry, G.InstanceReferenceGeometry):
            continue
        path = layer_path(doc, item) or ""
        if path == root or path.startswith(root + "::"):
            continue
        b = item.Geometry.GetBoundingBox(True)
        out[str(item.Id)] = "%s|%s|%s" % (path, type(item.Geometry).__name__, ",".join("%.4f" % v for v in (b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z)))
    return out


def setup_sheet(doc, name, width_mm, height_mm, target, direction, scale, root, margin_mm=12.0, title_column_mm=160.0, page_units=None):
    """The page, its border and title column (as-rhino-thinline's new_sheet), and the main parallel detail flush with them.

    Returns the page, the detail and the two page boxes. Sheet layers go under root. The building (every
    model-space object outside root) is recorded here, before the sheet's request ledger starts; check_sheet fails
    if any of it is later changed or removed: the sheet is drawn from the model, never by editing it."""
    if not doc.Strings.GetValue(BUILDING_KEY):
        doc.Strings.SetString(BUILDING_KEY, json.dumps({"root": root, "objects": building_fingerprints(doc, root)}))
    sheet = new_sheet(doc, name, width_mm, height_mm, root, margin_mm, title_column_mm, page_units)
    page, field = sheet["page"], sheet["field"]
    detail = parallel_detail(doc, page, field[:2], field[2:], target, direction, scale, "Main detail", layer_index(doc, root + "::Details"))
    return {"page": page, "detail": detail, "field": field, "title": sheet["title"]}


def parallel_detail(doc, page, corner0, corner1, target, direction, scale, name=None, index=None):
    """A parallel detail at scale (page length / model length, 1:40 is 0.025). Order matters: projection, commit,
    re-fetch, camera, commit, re-fetch, scale. SetScale fails in any other order."""
    detail = page.AddDetailView(name or "Detail", G.Point2d(*corner0), G.Point2d(*corner1), Rhino.Display.DefinedViewportProjection.Perspective)
    if detail is None:
        raise ValueError("could not add the detail view")
    attr = detail.Attributes.Duplicate()
    attr.Name = name or "Detail"
    if index is not None:
        attr.LayerIndex = index
    doc.Objects.ModifyAttributes(detail.Id, attr, True)
    detail = doc.Objects.FindId(detail.Id)
    detail.Viewport.ChangeToParallelProjection(True)
    detail.CommitViewportChanges()
    detail.CommitChanges()
    detail = doc.Objects.FindId(detail.Id)
    pull_back = 100.0 * Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Meters, doc.ModelUnitSystem)
    detail.Viewport.SetCameraLocations(target, target + G.Vector3d(*direction) * pull_back)
    detail.Viewport.CameraUp = G.Vector3d.ZAxis
    detail.CommitViewportChanges()
    detail.CommitChanges()
    detail = doc.Objects.FindId(detail.Id)
    per_model = scale * Rhino.RhinoMath.UnitScale(doc.ModelUnitSystem, doc.PageUnitSystem)
    if not detail.DetailGeometry.SetScale(1.0, doc.ModelUnitSystem, per_model, doc.PageUnitSystem):
        raise ValueError("SetScale refused")
    detail.CommitChanges()
    detail.CommitViewportChanges()
    return doc.Objects.FindId(detail.Id)


def pan_detail(doc, detail, page_dx, page_dy, scale):
    """Move a drawing on the page by panning its camera; the scale holds. Re-project afterwards."""
    vp = detail.Viewport
    per_model = scale * Rhino.RhinoMath.UnitScale(doc.ModelUnitSystem, doc.PageUnitSystem)
    move = vp.CameraX * (-page_dx / per_model) + vp.CameraY * (-page_dy / per_model)
    vp.SetCameraLocations(vp.CameraTarget + move, vp.CameraLocation + move)
    detail.CommitViewportChanges()
    detail.CommitChanges()
    return doc.Objects.FindId(detail.Id)


def hide_in_detail(doc, detail):
    """Hide every model layer in one detail. Page-space linework is not drawn through a detail, so it
    stays. A layer added later is visible here until this runs again."""
    detail_id = detail.Viewport.Id
    for layer in [x for x in doc.Layers if not x.IsDeleted and x.FullPath]:
        layer.SetPerViewportVisible(detail_id, False)
        layer.CommitChanges()


def hidden_line_parameters(viewport, tolerance):
    params = HiddenLineDrawingParameters()
    params.AbsoluteTolerance = tolerance
    params.Flatten, params.IncludeHiddenCurves = True, False
    params.IncludeTangentEdges, params.IncludeTangentSeams = False, False
    params.SetViewport(viewport)
    return params


def world_to_page_mapping(drawing, detail, box):
    """Solve the map from hidden-line output to page coordinates, from three corners of a box, and confirm it."""
    to_hidden = drawing.WorldToHiddenLine
    to_page = detail.WorldToPageTransform
    corners = list(box.GetCorners())
    for trio in itertools.combinations(corners, 3):
        hidden, paged = [], []
        for world in trio:
            a, b = G.Point3d(world), G.Point3d(world)
            a.Transform(to_hidden)
            b.Transform(to_page)
            hidden.append((a.X, a.Y))
            paged.append((b.X, b.Y))
        try:
            fx, fy = solve_affine(hidden, paged)
        except ValueError:
            continue
        xf = G.Transform.Identity
        xf.M00, xf.M01, xf.M03 = fx
        xf.M10, xf.M11, xf.M13 = fy
        return xf, fx, fy
    raise ValueError("could not map the projection: all reference corners were collinear")


def visible_segments(drawing):
    for segment in drawing.Segments:
        if segment is not None and str(segment.SegmentVisibility) == "Visible" and segment.CurveGeometry is not None:
            yield segment


def object_outlines(geometries, plane, to_hidden):
    """{tag: polylines} of each object's projected outline in hidden-line coordinates. The hidden-line
    silhouette types miss some outline edges of a box (they come back as creases); an edge on its own
    object's outline is drawn as outline."""
    out = {}
    for tag, geometry in geometries:
        brep = geometry if isinstance(geometry, G.Brep) else (geometry.ToBrep() if hasattr(geometry, "ToBrep") else None)
        mesh = G.Mesh()
        if isinstance(geometry, G.Mesh):
            mesh.Append(geometry)
        elif brep is not None:
            for part in G.Mesh.CreateFromBrep(brep, G.MeshingParameters.FastRenderMesh) or []:
                mesh.Append(part)
        lines = []
        for polyline in mesh.GetOutlines(plane) or []:
            points = []
            for p in polyline:
                q = G.Point3d(p)
                q.Transform(to_hidden)
                points.append((q.X, q.Y))
            lines.append(points)
        out[str(tag)] = lines
    return out


MAIN_KEY = "as-sheet:main-sources"


def merge_overlaps(pieces, tolerance=None, touching=()):
    """[(name, id, geometry)] with interpenetrating pieces of one name joined by a boolean union, so the
    hidden-line pass does not draw one run's edges through another where they overlap (pipe runs at an
    elbow). Pieces that only touch stay apart. A union that does not give one solid keeps the originals."""
    if not pieces:
        return []
    doc_tol = tolerance or 0.001
    boxes = []
    for _name, _guid, geometry in pieces:
        b = geometry.GetBoundingBox(True)
        boxes.append((b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z))
    out, merged = list(pieces), set()
    for group in overlap_groups(boxes, [n for n, _g, _x in pieces], 10 * doc_tol, touching):
        breps = [pieces[i][2] if isinstance(pieces[i][2], G.Brep) else pieces[i][2].ToBrep() for i in group]
        if any(b is None for b in breps):
            continue
        union = G.Brep.CreateBooleanUnion(breps, doc_tol)
        if union and len(union) == 1:
            out[group[0]] = (pieces[group[0]][0], pieces[group[0]][1], union[0])
            merged.update(group[1:])
    if merged:
        print("merged", len(merged), "overlapping pieces into the piece they overlap")
    return [x for i, x in enumerate(out) if i not in merged]


def crop_copies(pieces, crop, tolerance):
    """In-memory copies of [(name, id, geometry)] cut to a crop box (x0, y0, z0, x1, y1, z1): a cut-away view
    without touching the model. Pieces wholly inside are kept, wholly outside dropped, the rest cut."""
    box = G.BoundingBox(*crop)
    cutter = G.Brep.CreateFromBox(box)
    out = []
    for name, guid, geometry in pieces:
        b = geometry.GetBoundingBox(True)
        if not G.BoundingBox.Intersection(b, box).IsValid:
            continue
        if box.Contains(b.Min) and box.Contains(b.Max):
            out.append((name, guid, geometry))
            continue
        brep = geometry if isinstance(geometry, G.Brep) else (geometry.ToBrep() if hasattr(geometry, "ToBrep") else None)
        for part in (G.Brep.CreateBooleanIntersection(brep, cutter, tolerance) or []) if brep is not None else []:
            out.append((name, guid, part))
    return out


def main_linework(doc, page, detail, source_root, out_root, weights=None, tolerance=0.001, min_mm=0.15, receding_from=0.6, exclude=None, join_touching=(), crop=None):
    """Replace a detail's live model with vector linework on the page.

    Filled plates hide what is behind: hidden curves are dropped by the projection. Three stroke
    classes go on three layers (outline, edge, receding). Only source_root is projected: one layer
    path or a list, such as every owner's top layer in an assembled team model. exclude is a list of
    layer paths or globs left out, such as "*::Sheathing", so the frame and services behind show.
    Solids and meshes are projected and curves become guides; anything else (text dots, points) is
    skipped and counted. Overlapping pieces of one layer are joined first, and pieces of layers matching
    join_touching (service runs, such as "*::Drain") also when they only touch. crop (x0, y0, z0, x1, y1, z1)
    draws a cut-away piece: copies are cut to that box in memory and the model is not touched. Only the assembly's
    outline against the paper is drawn heavy; member edges are medium, and members toward the back
    (receding_from of the depth) light. The sources and exclusions are kept on the document for cut_detail.
    Every model layer is then hidden in this detail, so nothing else
    shows through and the sheet is static: it must be regenerated after a model change."""
    for src in ([source_root] if isinstance(source_root, str) else list(source_root)):
        if out_root == src or out_root.startswith(src + "::") or src.startswith(out_root + "::"):
            raise ValueError("refused: out_root %r overlaps the source layer %r; draw the sheet under its own root layer" % (out_root, src))
    w = dict(WEIGHTS, **(weights or {}))
    one_mm = mm(doc)
    clear(doc, out_root)
    layers = {"outline": layer_index(doc, out_root + "::Outline", w["main_outline"]),
              "edge": layer_index(doc, out_root + "::Edge", w["main_edge"]),
              "receding": layer_index(doc, out_root + "::Receding", w["main_receding"])}
    params = hidden_line_parameters(detail.Viewport, tolerance)
    guides, box, items, solids, skipped, left_out, picked = [], G.BoundingBox.Empty, {}, 0, {}, 0, []
    for item in live_objects(doc):
        path = layer_path(doc, item)
        if not path or not layer_selected(path, source_root):
            continue
        if layer_selected(path, exclude or []):
            left_out += 1
            continue
        if isinstance(item.Geometry, G.Curve):
            guides.append(item.Geometry)
            continue
        kind = type(item.Geometry).__name__
        if kind not in PROJECTED:
            skipped[kind] = skipped.get(kind, 0) + 1
            continue
        picked.append((path, item.Id, item.Geometry))
    if crop is not None:      # a cut-away piece of the model, drawn from copies: the model itself is never edited
        picked = crop_copies(picked, crop, doc.ModelAbsoluteTolerance)
    projected = merge_overlaps(picked, touching=join_touching)
    doc.Strings.SetString(MAIN_KEY, json.dumps({"roots": [source_root] if isinstance(source_root, str) else list(source_root), "exclude": list(exclude or []),
                                                "crop": list(crop) if crop is not None else None}))
    for path, guid, geometry in projected:
        params.AddGeometry(geometry, G.Transform.Identity, guid)
        box.Union(geometry.GetBoundingBox(True))
        items[str(guid)] = geometry.GetBoundingBox(True).Center
        solids += 1
    print("excluded", left_out, "skipped", skipped)
    if not solids:
        raise ValueError("nothing to project under %s" % (source_root,))
    started = time.time()
    drawing = HiddenLineDrawing.Compute(params, True)
    if drawing is None:
        raise ValueError("the hidden-line drawing returned nothing")
    print("solids", solids, "guides", len(guides), "seconds", round(time.time() - started, 1))
    xf, fx, fy = world_to_page_mapping(drawing, detail, box)
    # the assembly's outline against the paper: an edge with no object on one side. Each object's own projected
    # outline is the region it covers (one mesh of everything is not reliable: GetOutlines can return nothing).
    to_hidden = drawing.WorldToHiddenLine
    regions = []
    for lines in object_outlines([(guid, geometry) for _p, guid, geometry in projected], G.Plane(box.Center, detail.Viewport.CameraZ), to_hidden).values():
        for poly in lines:
            if len(poly) > 2:
                xs, ys = [q[0] for q in poly], [q[1] for q in poly]
                regions.append(((min(xs), min(ys), max(xs), max(ys)), poly))
    near_outline = max(1e-6, 0.0005 * box.Diagonal.Length)
    print("map to page", [round(v, 5) for v in fx + fy])
    camera_z = detail.Viewport.CameraZ
    depth = {key: G.Vector3d(centre) * camera_z for key, centre in items.items()}
    near, far = max(depth.values()), min(depth.values())
    span = max(near - far, 1e-9)
    buckets, types = {}, {}
    for segment in visible_segments(drawing):
        curve = segment.CurveGeometry
        if curve.GetLength() * abs(fx[0]) < min_mm * one_mm:
            continue
        parent = segment.ParentCurve
        kind = str(parent.SilhouetteType) if parent is not None else "None"
        types[kind] = types.get(kind, 0) + 1
        owner = parent.SourceObject.Tag if parent is not None and parent.SourceObject is not None else None
        key = str(owner) if owner is not None else ""
        mid = curve.PointAtNormalizedLength(0.5)
        tangent = curve.TangentAt(curve.Domain.Mid)
        edge = against_paper((mid.X, mid.Y), (tangent.X, tangent.Y), 2 * near_outline, regions)
        stroke = main_stroke(kind, edge, (near - depth.get(key, near)) / span, receding_from)
        if stroke is None:
            continue
        copy = curve.DuplicateCurve()
        copy.Transform(xf)
        buckets.setdefault((key, stroke), []).append(copy)
    print("types", types)
    added = 0
    for (_owner, stroke), curves in buckets.items():
        for joined in (G.Curve.JoinCurves(curves, 0.02 * one_mm) or curves):
            doc.Objects.AddCurve(joined, page_attr(doc, page, layers[stroke], "Linework " + stroke))
            added += 1
    to_page = detail.WorldToPageTransform
    if guides:
        layers["guide"] = layer_index(doc, out_root + "::Guides", w["main_guide"])
    for guide in guides:
        copy = guide.DuplicateCurve()
        copy.Transform(to_page)
        doc.Objects.AddCurve(copy, page_attr(doc, page, layers["guide"], "Explosion guide"))
    hide_in_detail(doc, detail)
    page.Redraw()
    Rhino.RhinoApp.Wait()
    print("curves added", added)
    return {"curves": added, "solids": solids, "types": types, "scale_x": fx[0], "skipped": skipped, "excluded": left_out}


def main_blockers(doc):
    """(breps, crop) the main view draws, from what main_linework kept on the document: solids on its source
    layers less its exclusions, and its crop box or None. Meshes are not included. ([], None) before main_linework."""
    stored = string_value(doc, MAIN_KEY)
    if not stored:
        return [], None
    main = json.loads(stored)
    out = []
    for item in live_objects(doc):
        if item.Attributes.Space != Rhino.DocObjects.ActiveSpace.ModelSpace or not isinstance(item.Geometry, (G.Brep, G.Extrusion)):
            continue
        path = layer_path(doc, item) or ""
        if not layer_selected(path, main["roots"]) or layer_selected(path, main.get("exclude") or []):
            continue
        out.append(item.Geometry if isinstance(item.Geometry, G.Brep) else item.Geometry.ToBrep())
    return out, main.get("crop")


def xyz(p):
    return (p.X, p.Y, p.Z)


def ray_covered(brep, a, b, span, tol):
    """True when the part of segment a-b within span (parameters along it) meets brep: a surface it crosses, or a
    start inside it (a crop's cut face, or a point inside another solid)."""
    box = brep.GetBoundingBox(True)
    ab = clip_segment_to_box(xyz(a), xyz(b), (box.Min.X, box.Min.Y, box.Min.Z, box.Max.X, box.Max.Y, box.Max.Z))
    if ab is None or ab[1] < span[0] or ab[0] > span[1]:
        return False
    entry = a + (b - a) * span[0]
    if brep.IsPointInside(entry, tol, True):
        return True
    found, overlaps, points = G.Intersect.Intersection.CurveBrep(G.LineCurve(a, b), brep, tol)
    if not found:
        return False
    length = a.DistanceTo(b)
    hits = [a.DistanceTo(p) / length for p in points or []] + [a.DistanceTo(c.PointAtStart) / length for c in overlaps or []]
    return any(span[0] - 1e-9 <= t <= span[1] + 1e-9 for t in hits)


def visible_points(doc, main_detail, world_points, blockers=None, crop=None):
    """The world points no part of the main view covers, seen along the main detail's camera: a short ray from each
    point toward the camera meets no drawn solid (within the crop box, if the view is a cut-away). A point on a
    face turned away from the camera is covered by its own part. blockers and crop default to main_blockers."""
    tol = doc.ModelAbsoluteTolerance
    if blockers is None:
        blockers, crop = main_blockers(doc)
    if not blockers:
        return list(world_points)
    camera = main_detail.Viewport.CameraDirection
    toward = G.Vector3d(-camera.X, -camera.Y, -camera.Z)
    toward.Unitize()
    reach = 0.0
    for brep in blockers:
        reach = max(reach, brep.GetBoundingBox(True).Diagonal.Length)
    keep = []
    for world in world_points:
        p = G.Point3d(world)
        a, b = p + toward * (10 * tol), p + toward * (2 * reach + 1)
        span = clip_segment_to_box(xyz(a), xyz(b), tuple(crop)) if crop else (0.0, 1.0)
        if span is None or not any(ray_covered(brep, a, b, span, tol) for brep in blockers):
            keep.append(world)
    return keep


def really_meets(geometry, cutter, window_centre, tolerance):
    """Whether a member whose boolean came back empty has any real contact with the window. Bounding
    boxes overlap for members that never touch it, and those are not failures. When the intersection
    itself cannot be computed, this answers True, so a real failure is still reported."""
    ok, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(geometry, cutter, tolerance)
    if not ok or (curves is not None and len(curves)) or (points is not None and len(points)):
        return True
    return geometry.IsSolid and geometry.IsPointInside(window_centre, tolerance, False)


def cut_pieces(doc, sources, window, offset, out_layer, tolerance=0.0005):
    """Cut sources to a window box, move them by offset, add them in model space, return {name: [boxes]} and ids.

    sources is a list of (name, brep, box). A thin layer does not boolean reliably at tight tolerance,
    so a piece thinner than 2 mm is clamped to the window with its bounding box instead."""
    wb = G.BoundingBox(*window)
    cutter = G.Brep.CreateFromBox(wb)
    move = G.Transform.Translation(offset)
    index = layer_index(doc, out_layer)
    made, ids = {}, []
    for name, geometry, box in sources:
        if box.Max.X <= wb.Min.X or box.Min.X >= wb.Max.X or box.Max.Y <= wb.Min.Y or box.Min.Y >= wb.Max.Y or box.Max.Z <= wb.Min.Z or box.Min.Z >= wb.Max.Z:
            continue
        thin = min(box.Max.X - box.Min.X, box.Max.Y - box.Min.Y, box.Max.Z - box.Min.Z) < 0.002 * Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Meters, doc.ModelUnitSystem)
        if wb.Contains(box.Min) and wb.Contains(box.Max):
            parts = [geometry.DuplicateBrep()]
        elif thin:
            parts = [G.Brep.CreateFromBox(G.BoundingBox(max(box.Min.X, wb.Min.X), max(box.Min.Y, wb.Min.Y), max(box.Min.Z, wb.Min.Z), min(box.Max.X, wb.Max.X), min(box.Max.Y, wb.Max.Y), min(box.Max.Z, wb.Max.Z)))]
        else:
            parts = G.Brep.CreateBooleanIntersection(geometry, cutter, tolerance)
            if not parts:
                if really_meets(geometry, cutter, wb.Center, tolerance):
                    print("cut failed:", name)
                continue
        for part in parts:
            part.Transform(move)
            ids.append(model_add(doc, part, index, name))
            made.setdefault(name, []).append(part.GetBoundingBox(True))
    return made, ids


def cut_faces(brep, plane, toward_camera, tolerance=1e-4):
    """Faces of a cut piece lying on the cut plane and facing the camera: the only faces that get hatch."""
    out = []
    for face in brep.Faces:
        ok, face_plane = face.TryGetPlane(tolerance)
        if not ok:
            continue
        normal = G.Vector3d(face_plane.Normal)
        if face.OrientationIsReversed:
            normal.Reverse()
        if abs(plane.DistanceTo(face_plane.Origin)) < tolerance and normal * toward_camera > 0 and abs(abs(normal * plane.Normal) - 1) < 1e-6:
            out.append(face)
    return out


def face_box(face):
    """Bounding box of the trimmed face. BrepFace.GetBoundingBox returns the untrimmed surface on a cut
    face, which puts hatch and label anchors in the wrong place."""
    return face.DuplicateFace(False).GetBoundingBox(True)


def face_lines(segments, origin, u_axis, v_axis, outward, offset):
    """Hatch segments on a real cut face, in 3D, offset outward so they pass through the same hidden-line solve."""
    lift = outward * offset
    return [G.LineCurve(origin + u_axis * a[0] + v_axis * a[1] + lift, origin + u_axis * b[0] + v_axis * b[1] + lift) for a, b in segments]


def round_detail(doc, page, tag, breps, hatch, direction, centre_mm, radius_mm, scale, out_root, weights=None, tolerance=0.0002, ring_tags=None, cut_edges=None):
    """A circular detail, as linework: Rhino details are rectangular. Project, split against the ring,
    keep pieces whose midpoint is inside. ring_tags is [((x_mm, y_mm), radius_mm)]: the ring stops
    under each tag, and no linework is drawn under one. An edge on its piece's projected outline is drawn
    as outline, and so is every curve in cut_edges (the edges of the cut faces). With scale None, the
    largest standard scale that fits the content in the ring is used; it is on the returned function
    as P.scale (page length / model length). Returns P, the world-to-page function for this detail."""
    record_request(doc, "detail", tag)
    w = dict(WEIGHTS, **(weights or {}))
    one_mm = mm(doc)
    paths = {True: ("::Outline", w["detail_outline"]), False: ("::Edge", w["detail_edge"]), "h": ("::Hatch", w["detail_hatch"]), "ring": ("::Ring", w["ring"])}
    layers = {"ring": layer_index(doc, out_root + "::Ring", w["ring"])}      # the others only when they get curves: no empty layers
    box = G.BoundingBox.Empty
    for guid in breps:
        box.Union(doc.Objects.FindId(guid).Geometry.GetBoundingBox(True))
    temp = parallel_detail(doc, page, (100 * one_mm, 100 * one_mm), (300 * one_mm, 300 * one_mm), box.Center, direction, scale or 0.1, "temporary")
    params = hidden_line_parameters(temp.Viewport, tolerance)
    for guid in breps:
        params.AddGeometry(doc.Objects.FindId(guid).Geometry, G.Transform.Identity, guid)
    for curve in hatch or []:
        params.AddGeometry(curve, G.Transform.Identity, "H")
    for curve in cut_edges or []:
        params.AddGeometry(curve, G.Transform.Identity, "C")
    drawing = HiddenLineDrawing.Compute(params, True)
    to_hidden = drawing.WorldToHiddenLine
    view_plane = G.Plane(box.Center, temp.Viewport.CameraZ)
    doc.Objects.Delete(temp.Id, True)
    outlines = object_outlines([(guid, doc.Objects.FindId(guid).Geometry) for guid in breps], view_plane, to_hidden)
    near = max(1e-6, 0.0005 * box.Diagonal.Length)
    per_model = (scale or 0.0) * Rhino.RhinoMath.UnitScale(doc.ModelUnitSystem, doc.PageUnitSystem)
    segments, content = [], G.BoundingBox.Empty
    for segment in visible_segments(drawing):
        curve = segment.CurveGeometry
        parent = segment.ParentCurve
        if parent is not None and parent.SourceObject is not None and str(parent.SourceObject.Tag) in ("H", "C"):
            segments.append((curve, "h" if str(parent.SourceObject.Tag) == "H" else True))
            if str(parent.SourceObject.Tag) == "C":     # cut edges are content: a square-on section is mostly cut edges
                content.Union(curve.GetBoundingBox(True))
            continue
        outline = parent is not None and stroke_class(str(parent.SilhouetteType)) == "outline"
        if not outline and parent is not None and parent.SourceObject is not None:
            mid = curve.PointAtNormalizedLength(0.5)
            outline = near_polyline((mid.X, mid.Y), outlines.get(str(parent.SourceObject.Tag), []), near)
        segments.append((curve, outline))
        content.Union(curve.GetBoundingBox(True))
    if not scale:
        span = max(content.Max.X - content.Min.X, content.Max.Y - content.Min.Y)
        n = fit_scale_denominator(span * Rhino.RhinoMath.UnitScale(doc.ModelUnitSystem, Rhino.UnitSystem.Millimeters), 2 * radius_mm, 0.8)
        scale = 1.0 / n
        per_model = scale * Rhino.RhinoMath.UnitScale(doc.ModelUnitSystem, doc.PageUnitSystem)
    middle = content.Center
    tx, ty = centre_mm[0] * one_mm - per_model * middle.X, centre_mm[1] * one_mm - per_model * middle.Y
    xf = G.Transform.Identity
    xf.M00, xf.M11, xf.M03, xf.M13 = per_model, per_model, tx, ty

    def to_page(world):
        p = G.Point3d(world)
        p.Transform(to_hidden)
        return G.Point3d(per_model * p.X + tx, per_model * p.Y + ty, 0)

    centre = G.Point3d(centre_mm[0] * one_mm, centre_mm[1] * one_mm, 0)
    radius = radius_mm * one_mm
    ring = G.Circle(centre, radius).ToNurbsCurve()
    kept = {True: [], False: [], "h": []}
    cutters = [ring] + [G.Circle(G.Point3d(x * one_mm, y * one_mm, 0), r * one_mm).ToNurbsCurve() for (x, y), r in ring_tags or []]
    tag_circles = [(G.Point3d(x * one_mm, y * one_mm, 0), r * one_mm) for (x, y), r in ring_tags or []]
    for curve, key in segments:
        copy = curve.DuplicateCurve()
        copy.Transform(xf)
        parameters = []
        for cutter in cutters:
            hits = Rhino.Geometry.Intersect.Intersection.CurveCurve(copy, cutter, 0.0002, 0.0002)
            parameters += [h.ParameterA for h in hits if h.IsPoint] if hits else []
        for piece in (copy.Split(sorted(parameters)) if parameters else [copy]) or []:
            mid = piece.PointAtNormalizedLength(0.5)
            if mid.DistanceTo(centre) < radius and piece.GetLength() > 0.08 * one_mm and not any(mid.DistanceTo(c) < r for c, r in tag_circles):
                kept[key].append(piece)
    added, drawn = 0, []
    for key in (True, False, "h"):
        if kept[key]:
            drawn += [(key, c) for c in (G.Curve.JoinCurves(kept[key], 0.0005) or kept[key])]
    # no stacked duplicates: a cut edge, an outline and a hatch line can land on the same line
    sig = []
    for _k, c in drawn:          # compared by box and length, as the duplicate check does: a joined loop may start anywhere
        b = c.GetBoundingBox(True)
        sig.append((b.Min.X, b.Min.Y, b.Max.X, b.Max.Y, c.GetLength()))
    for i in dedupe_curves(sig, 0.02 * one_mm):
        key, c = drawn[i]
        if key not in layers:
            layers[key] = layer_index(doc, out_root + paths[key][0], paths[key][1])
        doc.Objects.AddCurve(c, page_attr(doc, page, layers[key], "Bubble linework %s" % tag))
        added += 1
    circle = G.Circle(centre, radius)
    for start, end in ring_arcs(centre_mm, radius_mm, ring_tags):
        if end - start >= 2 * math.pi - 1e-9:
            add_circle(doc, page, layers["ring"], (centre.X, centre.Y), radius, "Bubble ring %s" % tag)
        else:
            doc.Objects.AddArc(G.Arc(circle, G.Interval(start, end)), page_attr(doc, page, layers["ring"], "Bubble ring %s" % tag))
    to_page.scale = scale
    print(tag, "curves", added, "scale 1:%g" % round(1.0 / scale, 3))
    return to_page, added


def solids_in(doc, window, skip_roots=(), roots=None):
    """[(layer leaf, brep, box)] of every model-space solid that reaches into a window box: the joint's
    members and whatever adjoins them there, so a detail shows the joint in context. roots limits it to
    those layers; skip_roots (paths or globs) leaves layers out."""
    wb = G.BoundingBox(*window)
    out = []
    for item in live_objects(doc):
        if item.Attributes.Space != Rhino.DocObjects.ActiveSpace.ModelSpace or not isinstance(item.Geometry, (G.Brep, G.Extrusion)):
            continue
        path = layer_path(doc, item) or ""
        if layer_selected(path, list(skip_roots)) or (roots is not None and not layer_selected(path, list(roots))):
            continue
        brep = item.Geometry if isinstance(item.Geometry, G.Brep) else item.Geometry.ToBrep()
        b = brep.GetBoundingBox(True)
        if G.BoundingBox.Intersection(b, wb).IsValid:
            out.append((path.split("::")[-1], brep, b, "%s %s" % (path, item.Attributes.Name or "")))
    return out


def cut_detail(doc, page, tag, sources, window, direction, centre_mm, radius_mm, scale, out_root, materials=None, offset=None,
               tag_angle=135.0, tag_radius_mm=7.0, weights=None, skip_roots=None, join_touching=(), section=None):
    """One call for a round detail of a joint: cut the members to the window, join overlapping pieces of one
    member, hatch every real cut face by material and draw its edges as outline, project into the ring and
    tag it.

    window is (x0, y0, z0, x1, y1, z1) in model units, around the joint: keep it to the joint and the start of
    each member. sources is [(name, brep, box)]; None takes every solid reaching into the window (solids_in),
    limited to what the main view shows: main_linework's source layers less its exclusions, so the adjoining
    members show and nothing the main view leaves out appears. The sheet's own layers (skip_roots, by
    default the root of out_root) are left out too. join_touching as in main_linework. Only true cut faces
    are hatched: faces on a window plane of a member that continues past it, clipped to the face's own outline.
    materials is [(name glob, material)], first match wins: timber (X across the grain, grain lines along it),
    plywood, gypsum, concrete, steel and none. Unmatched pieces take the material their layer path and name
    imply (material_for: gypsum is not wood, glass and membranes get none).

    section=(axis, at, keep) makes a section detail: one cut plane, axis "x", "y" or "z" at coordinate `at`,
    keeping the side below it (keep=-1) or above it (keep=1), seen square on from the removed side. Head and
    sill details of a window or door use one vertical plane through the glass. The cut pieces are temporary:
    they are deleted after projection, so nothing is left in model space.
    scale None fits the content to the ring at a standard scale. Prints a warning when no face is cut, since
    the detail then shows no section. Returns (to_page, curves added, report); report["scale"] is 1:n."""
    metre = Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Meters, doc.ModelUnitSystem)
    offset = offset if offset is not None else G.Vector3d(0, 0, -1000.0 * metre)
    if section is not None:
        k = "xyz".index(section[0])
        lo, hi = list(window[:3]), list(window[3:])
        if section[2] < 0:
            hi[k] = section[1]
        else:
            lo[k] = section[1]
        window = tuple(lo) + tuple(hi)
        direction = tuple((-section[2] if i == k else 0.0) for i in range(3))
    wb = G.BoundingBox(*window)
    if sources is None:
        # what the main view shows: its source layers less its exclusions, so a detail never shows what the main view leaves out
        main = json.loads(doc.Strings.GetValue(MAIN_KEY) or "{}") if doc.Strings.GetValue(MAIN_KEY) else {}
        skip = list(skip_roots or (out_root.split("::")[0],)) + list(main.get("exclude", []))
        sources = solids_in(doc, window, skip, main.get("roots"))
    pieces, labels = [], {}
    for source in sources:
        _made, ids = cut_pieces(doc, [tuple(source[:3])], window, offset, out_root + "::Cut")
        pieces += [(source[0], guid, source[2]) for guid in ids]
        for guid in ids:
            labels[str(guid)] = source[3] if len(source) > 3 else source[0]
    joined = merge_overlaps([(name, guid, doc.Objects.FindId(guid).Geometry) for name, guid, _box in pieces], touching=join_touching)
    keep = set(str(g) for _n, g, _x in joined)
    for name, guid, geometry in joined:
        doc.Objects.Replace(guid, geometry)
    for _n, guid, _b in pieces:
        if str(guid) not in keep:
            doc.Objects.Delete(guid, True)
    source_box = dict((str(g), b) for _n, g, b in pieces)
    to_camera = G.Vector3d(*direction) if isinstance(direction, (tuple, list)) else G.Vector3d(direction)
    to_camera.Unitize()
    planes = []
    for axis in range(3):
        component = (to_camera.X, to_camera.Y, to_camera.Z)[axis]
        if abs(component) < 1e-6 or (section is not None and axis != "xyz".index(section[0])):
            continue
        sign = 1 if component > 0 else -1
        coordinate = ((wb.Max.X, wb.Max.Y, wb.Max.Z) if sign > 0 else (wb.Min.X, wb.Min.Y, wb.Min.Z))[axis] + (offset.X, offset.Y, offset.Z)[axis]
        normal = G.Vector3d(*[sign if i == axis else 0 for i in range(3)])
        planes.append((axis, G.Plane(G.Point3d(*[coordinate if i == axis else 0 for i in range(3)]), normal), normal))
    hatch, edges, report = [], [], {"pieces": len(joined), "cut_faces": 0, "hatch": {}, "hatch_outside": 0}
    for name, guid, geometry in joined:
        material = next((m for pattern, m in (materials or []) if fnmatch.fnmatchcase(name, pattern)), None) or material_for(labels.get(str(guid), name))
        b = source_box[str(guid)]
        sizes = (b.Max.X - b.Min.X, b.Max.Y - b.Min.Y, b.Max.Z - b.Min.Z)
        for axis, plane, normal in planes:
            at = plane.Origin.X if axis == 0 else plane.Origin.Y if axis == 1 else plane.Origin.Z
            at -= (offset.X, offset.Y, offset.Z)[axis]
            low, high = ((b.Min.X, b.Max.X), (b.Min.Y, b.Max.Y), (b.Min.Z, b.Max.Z))[axis]
            if not true_cut(low, high, at, 1e-3 * metre):
                continue
            for face in cut_faces(geometry, plane, to_camera, 1e-3 * metre):
                fb = face_box(face)
                u_axis, v_axis = [i for i in range(3) if i != axis]
                extent = (fb.Max.X - fb.Min.X, fb.Max.Y - fb.Min.Y, fb.Max.Z - fb.Min.Z)
                du, dv = extent[u_axis], extent[v_axis]
                report["cut_faces"] += 1
                loop = face.OuterLoop.To3dCurve()
                if loop is not None:
                    loop.Translate(normal * (0.001 * metre))
                    edges.append(loop)
                segments = hatch_pattern(material, sizes.index(max(sizes)) == axis, 0, 0, du, dv, metre)
                if segments and loop is not None:
                    # clip to the face's real outline in its own (u, v): a sloped sill's cut face is not its box
                    ok, pl = loop.TryGetPolyline()
                    pts = list(pl) if ok else [loop.PointAt(t) for t in loop.DivideByCount(64, True)]
                    poly = [((p - fb.Min)[u_axis], (p - fb.Min)[v_axis]) for p in pts]
                    segments = clip_to_polygon(segments, poly)
                    report["hatch_outside"] += sum(1 for a, c in segments if not point_in_polygon(((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0), poly))
                if segments:
                    report["hatch"][material] = report["hatch"].get(material, 0) + 1
                    u = G.Vector3d(*[1 if i == u_axis else 0 for i in range(3)])
                    v = G.Vector3d(*[1 if i == v_axis else 0 for i in range(3)])
                    hatch += face_lines(segments, fb.Min, u, v, normal, 0.001 * metre)
    if not report["cut_faces"]:
        print("WARNING: detail %s has no cut face; move its window so it cuts the members" % tag)
    angle = math.radians(tag_angle)
    at = (centre_mm[0] + radius_mm * math.cos(angle), centre_mm[1] + radius_mm * math.sin(angle))
    to_page, added = round_detail(doc, page, tag, [g for _n, g, _x in joined], hatch, direction, centre_mm, radius_mm, scale, out_root,
                                  weights, ring_tags=[(at, tag_radius_mm)], cut_edges=edges)
    report["scale"] = "1:%g" % round(1.0 / to_page.scale, 3)
    detail_tag(doc, page, layer_index(doc, out_root + "::Ring", dict(WEIGHTS, **(weights or {}))["ring"]), tag, at, tag_radius_mm)
    for _n, guid, _x in joined:                  # the cut pieces were only for the projection
        doc.Objects.Delete(guid, True)
    cut_index = doc.Layers.FindByFullPath(out_root + "::Cut", -1)
    if cut_index >= 0 and not list(doc.Objects.FindByLayer(doc.Layers[cut_index]) or []):
        doc.Layers.Delete(cut_index, True)
    print(tag, report)
    return to_page, added, report


def place_locator(doc, page, index, tag, ring_centre, ring_radius, world_points, main_detail, main_root, gap_mm=6.0):
    """Pick the joint for a detail and draw its locator. world_points are the requested joint's contacts;
    the one nearest the detail ring whose leader crosses no main linework, other detail ring or text wins, on a simple route or one
    that jogs around the drawing's outline. Returns the world point to cut the detail from, or None when
    no clean leader exists: then nothing is drawn and check_sheet fails the sheet, naming the detail."""
    one_mm = mm(doc)
    lines, box = page_curves(doc, page, main_root)
    lines += page_obstacles(doc, page)
    targets = []
    for world in world_points:
        p = G.Point3d(world)
        p.Transform(main_detail.WorldToPageTransform)
        targets.append((p.X, p.Y))
    found = pick_locator(targets, ring_centre, ring_radius, 5.0 * one_mm, lines, (box.Min.X, box.Min.Y, box.Max.X, box.Max.Y), gap_mm * one_mm)
    if found is None:
        record_request(doc, "locator", tag, "detail %s: none of its %d joints can be reached by a leader clear of the main drawing, the other details and text; choose another joint or move the detail" % (tag, len(targets)))
        return None
    record_request(doc, "locator", tag)
    i, legs = found
    locator(doc, page, index, tag, ring_centre, ring_radius, world_points[i], main_detail, legs=legs)
    return world_points[i]


def check_view(s, main_root=None, detail=None, scale=None):
    """The view on a read sheet (as-rhino-thinline's read_sheet): the building recorded by setup_sheet is unchanged;
    with main_root (main_linework's out_root), no locator or label leader crosses the main drawing away from its own
    joint, each locator ring sits on a drawn line, and no locator leader runs along a drawn edge; with detail and
    scale, the scale reads back from the detail. Adds to s["failures"]."""
    doc, page, failures, one_mm, drawing, locators, label_legs, targets, dots = [s[k] for k in ('doc', 'page', 'failures', 'one_mm', 'drawing', 'locators', 'label_legs', 'targets', 'dots')]
    stored = string_value(doc, BUILDING_KEY)
    if stored:
        snap = json.loads(stored)
        removed, changed = building_changes(snap["objects"], building_fingerprints(doc, snap["root"]))
        if removed or changed:
            failures.append("the building was edited after the sheet started: %d objects removed, %d changed; the sheet must be drawn from the model, never by editing it" % (len(removed), len(changed)))
    if main_root:
        for layer in [x for x in doc.Layers if not x.IsDeleted and x.FullPath and (x.FullPath == main_root or x.FullPath.startswith(main_root + "::"))]:
            for item in doc.Objects.FindByLayer(layer) or []:
                if item.Attributes.ViewportId == page.MainViewport.Id and isinstance(item.Geometry, G.Curve):
                    drawing.append(polyline_points(item.Geometry, 0.05 * one_mm))
        for leader, at in leader_crossings(locators, drawing, targets):
            failures.append("locator leader across the main drawing at (%.1f, %.1f) mm" % (at[0] / one_mm, at[1] / one_mm))
        for leader, at in leader_crossings(label_legs, drawing, dots, clear=1.0):
            failures.append("label leader across the main drawing at (%.1f, %.1f) mm" % (at[0] / one_mm, at[1] / one_mm))
        for x, y, r in targets:
            if not near_polyline((x, y), drawing, r):
                failures.append("locator ring at (%.1f, %.1f) mm is not on the main drawing" % (x / one_mm, y / one_mm))
        for leader in locators:
            for at in collinear_runs(leader, drawing, 0.3 * one_mm, 3.0 * one_mm, targets)[:1]:
                failures.append("locator leader runs along a drawn edge at (%.1f, %.1f) mm" % (at[0] / one_mm, at[1] / one_mm))
    if detail is not None and scale:
        ratio = doc.Objects.FindId(detail.Id).DetailGeometry.PageToModelRatio
        print("scale read back 1:%.3f" % (1.0 / ratio))
        if scale_mismatch(ratio, scale):
            failures.append("scale reads back 1:%.3f, expected 1:%.3f" % (1.0 / ratio, 1.0 / scale))


def check_sheet(doc, page_name, root, frames, main_root=None, detail=None, scale=None, field=None):
    """Check a sheet: as-rhino-thinline's conventions and this skill's view, in one list and one order.

    Conventions (check_conventions, check_layout): text inside frames, lines clear of labels and tags, leaders
    axis-aligned and not through text or rings, no colour language, margins against the fixed MIN_MARGIN_MM with
    field, and the request ledger: every requested label, locator and detail is recomputed against what the page
    shows, and an edited or deleted request, seal or building record fails. View (check_view): the building
    recorded by setup_sheet is unchanged; with main_root (main_linework's out_root), leaders reach their joints
    without crossing the main drawing; with detail and scale, the scale reads back. No limit is a parameter: when
    a check fails, fix the sheet, never the check. Never delete a failure record or request to pass a check; report
    what could not be placed.

    frames is [(name glob, (x0, y0, x1, y1))]. Returns failures, empty when none. Locator leaders and
    rings are found by their names, "Locator leader ..." and "Locator ring ...", which locator() gives them."""
    s = read_sheet(doc, page_name, root, frames, field)
    check_conventions(s)
    check_view(s, main_root, detail, scale)
    check_layout(s)
    return s["failures"]
