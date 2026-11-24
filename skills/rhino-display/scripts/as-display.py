#! python3
"""Image exports that are checked against the requested display mode (Arch Studio, as-rhino-display).

The file on disk is what gets checked, not the viewport. A batch fails when any file does not
match the requested mode, is blank, or when the document was left changed.

Runs by file path through run_python (uses __rhino_doc__):

    P = "<absolute path of this skill's folder>/scripts/as-display.py"
    exec(compile(open(P).read(), P, "exec"), {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_MODE": "export", "AS_EXPORT": SPEC})

AS_MODE  "modes"   list the display modes in this Rhino
         "export"  capture every shot in AS_EXPORT, then check every file
         "verify"  check existing files: AS_EXPORT = {"mode": "Arctic", "files": ["/abs/a.png", ...]}

AS_EXPORT for "export":
  out    folder for the PNGs; required
  mode   display mode name, for every shot; required
  size   [width, height], default [1920, 1080]
  supersample  capture at this multiple and scale down, default 2
  view   name of the view to use, default the active view
  shots  [{"name": "front-birdseye", "direction": [-.5, -.5, .707], "layers": ["Building::Option A"],
           "hide": ["Building::Option A::Framing"], "fill": .86, "projection": "perspective"}]
         direction points from the model to the camera; "top" and "birdseye" are shorthand.
         layers are shown with their sublayers and frame the shot; every other model layer is hidden.
         The camera is always placed outside those layers: interior views are not supported.
  expect "neutral" or "any"; default from the mode (see EXPECT).
  max_coloured_pct  default 0.1; min_content_pct default 0.2

Rhino, and System.Drawing when present, are imported only where needed, so the checks also run
without Rhino: they read the PNG with the standard library.
"""
import json
import math
import os
import struct
import time
import zlib

# Modes whose output must carry no colour. Any other mode is checked for being its named mode
# and not blank, and its colour is not judged: nothing in a file proves it was "Shaded".
EXPECT = {"arctic": "neutral", "monochrome": "neutral"}
CHROMA = 12          # a sample is coloured when max(R,G,B) - min(R,G,B) is above this
CONTENT_DELTA = 14   # a sample is content when it differs from the corner colour by more than this
SAMPLE_STEP = 7
SETTLE = 6
DIRECTIONS = {"birdseye": (-0.5, -0.5, math.sqrt(0.5)), "top": (0.0, 0.0, 1.0)}


class ExportError(Exception):
    """The batch cannot run or did not hold."""


def read_png(path):
    """(width, height, rows of (r, g, b) access) with the standard library. 8-bit, non-interlaced."""
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ExportError("not a PNG: %s" % path)
    pos, idat, palette, header = 8, [], None, None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"PLTE":
            palette = chunk
        elif kind == b"IDAT":
            idat.append(chunk)
        pos += 12 + length
    width, height, depth, colour, _c, _f, interlace = header
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(colour)
    if depth != 8 or interlace or channels is None:
        raise ExportError("unsupported PNG format in %s" % path)
    raw = zlib.decompress(b"".join(idat))
    stride = width * channels
    rows, prev = [], bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        kind = raw[start]
        row = bytearray(raw[start + 1:start + 1 + stride])
        if kind == 1:
            for i in range(channels, stride):
                row[i] = (row[i] + row[i - channels]) & 255
        elif kind == 2:
            for i in range(stride):
                row[i] = (row[i] + prev[i]) & 255
        elif kind == 3:
            for i in range(stride):
                left = row[i - channels] if i >= channels else 0
                row[i] = (row[i] + (left + prev[i]) // 2) & 255
        elif kind == 4:
            for i in range(stride):
                a = row[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                row[i] = (row[i] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 255
        rows.append(row)
        prev = row

    def pixel(x, y):
        row = rows[y]
        if colour == 2 or colour == 6:
            i = x * channels
            return row[i], row[i + 1], row[i + 2]
        if colour == 3:
            i = row[x] * 3
            return palette[i], palette[i + 1], palette[i + 2]
        v = row[x * channels]
        return v, v, v

    return width, height, pixel


def _reader(path):
    """System.Drawing inside Rhino, where a 4K file decodes quickly; the standard library otherwise."""
    try:
        import System.Drawing as SD
    except ImportError:
        return read_png(path) + (None,)
    bitmap = SD.Bitmap(path)

    def pixel(x, y):
        c = bitmap.GetPixel(x, y)
        return c.R, c.G, c.B

    return bitmap.Width, bitmap.Height, pixel, bitmap


def measure(path, step=SAMPLE_STEP):
    """Share of samples that are coloured, and that differ from the background."""
    width, height, pixel, closer = _reader(path)
    try:
        corners = [pixel(0, 0), pixel(width - 1, 0), pixel(0, height - 1), pixel(width - 1, height - 1)]
        background = [sum(c[i] for c in corners) / 4.0 for i in range(3)]
        total = coloured = content = 0
        for y in range(0, height, step):
            for x in range(0, width, step):
                r, g, b = pixel(x, y)
                total += 1
                if max(r, g, b) - min(r, g, b) > CHROMA:
                    coloured += 1
                if abs(r - background[0]) + abs(g - background[1]) + abs(b - background[2]) > CONTENT_DELTA:
                    content += 1
    finally:
        if closer is not None:
            closer.Dispose()
    return {"width": width, "height": height, "samples": total,
            "coloured_pct": round(100.0 * coloured / total, 3), "content_pct": round(100.0 * content / total, 3)}


def expected_for(mode, override=None):
    """"neutral" when the file must carry no colour, otherwise "any"."""
    return override or EXPECT.get((mode or "").strip().lower(), "any")


def judge(stats, mode, spec=None):
    """Why a measured file does not match the requested mode. Empty when it matches."""
    spec = spec or {}
    max_coloured = float(spec.get("max_coloured_pct", 0.1))
    min_content = float(spec.get("min_content_pct", 0.2))
    out = []
    if stats["content_pct"] < min_content:
        out.append("blank: %.3f%% of samples differ from the background, minimum %.3f%%" % (stats["content_pct"], min_content))
    if expected_for(mode, spec.get("expect")) == "neutral" and stats["coloured_pct"] > max_coloured:
        out.append("coloured: %.3f%% of samples have colour, but %s must have none (maximum %.3f%%)" % (stats["coloured_pct"], mode, max_coloured))
    return out


def verify_files(files, mode, spec=None):
    """One result per file. Unreadable or missing files fail."""
    results = []
    for path in files:
        entry = {"file": path, "mode": mode, "failures": []}
        try:
            entry.update(measure(path))
            entry["failures"] = judge(entry, mode, spec)
        except Exception as exc:
            entry["failures"] = ["could not read: %s" % exc]
        results.append(entry)
    return results


def report(results, mode, spec=None):
    """Print every file and the batch line. Returns True when every file matches."""
    if not results:
        print("Export: FAILED - no files to check")
        print("ASEXPORT status=fail files=0")
        return False
    expect = expected_for(mode, (spec or {}).get("expect"))
    bad = 0
    for entry in sorted(results, key=lambda e: not e["failures"]):
        if entry["failures"]:
            bad += 1
        state = "FAIL" if entry["failures"] else "ok"
        detail = "; ".join(entry["failures"]) or ("coloured %s%%, content %s%%" % (entry.get("coloured_pct"), entry.get("content_pct")))
        print("  %s %s: %s" % (state, os.path.basename(entry["file"]), detail))
    colour = "" if expect == "neutral" else " Colour was not judged for this mode; the file was checked for not being blank."
    if bad:
        print("Export: FAILED - %d of %d files do not match %s.%s" % (bad, len(results), mode, colour))
    else:
        print("Export: %d files match %s.%s" % (len(results), mode, colour))
    print("ASEXPORT status=%s files=%d failed=%d mode=%s" % ("fail" if bad else "pass", len(results), bad, mode))
    return not bad


def aim(points, direction, tan_half_height, aspect, fill=0.86):
    """Camera target and distance that fit points in a perspective frame, from the points alone.

    points are (x, y, z); direction points from the model toward the camera. No trial capture is
    needed, which is the point: repeated captures to find framing were what disturbed views."""
    z = _unit(direction)
    x = _unit(_cross((0.0, 0.0, 1.0) if abs(z[2]) < 0.999 else (0.0, 1.0, 0.0), z))
    y = _cross(z, x)
    centre = tuple(sum(p[i] for p in points) / float(len(points)) for i in range(3))
    local = []
    for p in points:
        v = tuple(p[i] - centre[i] for i in range(3))
        local.append((_dot(v, x), _dot(v, y), _dot(v, z)))
    half_x, half_y = tan_half_height * aspect, tan_half_height
    cx = cy = 0.0
    distance = max(max(abs(a), abs(b)) for a, b, _c in local) * 4 + 1.0
    for _ in range(40):
        xs = [(a - cx) / (distance - c) for a, _b, c in local]
        ys = [(b - cy) / (distance - c) for _a, b, c in local]
        cx += (max(xs) + min(xs)) / 2 * distance
        cy += (max(ys) + min(ys)) / 2 * distance
        distance = max(max(abs(a - cx) / (half_x * fill) + c for a, _b, c in local),
                       max(abs(b - cy) / (half_y * fill) + c for _a, b, c in local))
    target = tuple(centre[i] + x[i] * cx + y[i] * cy for i in range(3))
    camera = tuple(target[i] + z[i] * distance for i in range(3))
    return target, camera


def _dot(a, b):
    return sum(u * v for u, v in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(v):
    n = math.sqrt(_dot(v, v))
    return tuple(c / n for c in v)


# ---- Rhino ----

def state_snapshot(doc):
    """What an export must leave unchanged: layer visibility and colour, materials, object count."""
    layers = sorted((L.FullPath, L.IsVisible, L.Color.ToArgb(), L.RenderMaterialIndex) for L in doc.Layers if not L.IsDeleted and L.FullPath)
    return {"layers": layers, "materials": doc.Materials.Count, "objects": sum(1 for _ in doc.Objects)}


def leftovers(doc):
    """Objects and layers named as temporary, which a capture would show."""
    names = []
    for item in doc.Objects:
        name = (item.Attributes.Name or "").lower()
        if name.startswith("temp") or name.startswith("_capture"):
            names.append(item.Attributes.Name)
    return sorted(set(names))


def _in(path, roots):
    return any(path == r or path.startswith(r + "::") for r in roots)


def isolate(doc, shot):
    """Show the shot's layers. Parents of what is shown stay on. Returns what to restore."""
    shown, hidden = shot.get("layers") or [], shot.get("hide") or []
    restore = []
    for layer in doc.Layers:
        if layer.IsDeleted or not layer.FullPath:
            continue
        path = layer.FullPath
        visible = (_in(path, shown) and not _in(path, hidden)) or any(s.startswith(path + "::") for s in shown)
        if layer.IsVisible != visible:
            restore.append((layer.Id, layer.IsVisible))
            layer.IsVisible = visible
            layer.CommitChanges()
    return restore


def restore_layers(doc, restore):
    for layer_id, visible in restore:
        layer = doc.Layers.FindId(layer_id)
        if layer is not None:
            layer.IsVisible = visible
            layer.CommitChanges()


def frame_points(doc, shot):
    """Bounding box corners of the visible objects of the shot, as tuples."""
    import Rhino

    points = []
    for item in doc.Objects.GetObjectList(Rhino.DocObjects.ObjectEnumeratorSettings()):
        path = doc.Layers[item.Attributes.LayerIndex].FullPath
        if _in(path, shot.get("layers") or []) and not _in(path, shot.get("hide") or []):
            points += [(p.X, p.Y, p.Z) for p in item.Geometry.GetBoundingBox(True).GetCorners()]
    return points


def capture_shot(doc, view, shot, mode_name, mode, size, supersample, folder):
    """One capture by the safe method: script-set camera, settle, capture with the mode named."""
    import Rhino
    import Rhino.Geometry as G
    import System.Drawing as SD
    from System.Drawing.Drawing2D import InterpolationMode, PixelOffsetMode, SmoothingMode
    from System.Drawing.Imaging import ImageFormat

    vp = view.ActiveViewport
    points = frame_points(doc, shot)
    if not points:
        raise ExportError("%s: no objects on its layers" % shot["name"])
    direction = shot.get("direction", "birdseye")
    direction = DIRECTIONS[direction] if isinstance(direction, str) else tuple(direction)
    if shot.get("projection") == "parallel":
        vp.ChangeToParallelProjection(True)
    else:
        vp.ChangeToPerspectiveProjection(True, float(shot.get("lens", 50.0)))
    ok, left, right, bottom, top, near, _far = vp.GetFrustum()
    aspect = float(size[0]) / size[1]
    target, camera = aim(points, direction, top / near, aspect, float(shot.get("fill", 0.86)))
    vp.SetCameraLocations(G.Point3d(*target), G.Point3d(*camera))
    vp.CameraUp = G.Vector3d.YAxis if abs(direction[2]) > 0.999 else G.Vector3d.ZAxis
    if shot.get("projection") == "parallel":
        box = G.BoundingBox.Empty
        for p in points:
            box.Union(G.Point3d(*p))
        vp.ZoomBoundingBox(box)
    vp.DisplayMode = mode
    view.Redraw()
    for _ in range(SETTLE):
        Rhino.RhinoApp.Wait()
        time.sleep(0.25)
    big = view.CaptureToBitmap(SD.Size(size[0] * supersample, size[1] * supersample), mode)
    if big is None:
        raise ExportError("%s: the capture returned nothing" % shot["name"])
    bitmap = SD.Bitmap(size[0], size[1])
    graphics = SD.Graphics.FromImage(bitmap)
    graphics.InterpolationMode = InterpolationMode.HighQualityBicubic
    graphics.SmoothingMode = SmoothingMode.HighQuality
    graphics.PixelOffsetMode = PixelOffsetMode.HighQuality
    graphics.DrawImage(big, 0, 0, size[0], size[1])
    graphics.Dispose()
    big.Dispose()
    path = os.path.join(folder, "%s.png" % shot["name"])
    bitmap.Save(path, ImageFormat.Png)
    bitmap.Dispose()
    return path


def export(doc, spec):
    import Rhino

    for key in ("out", "mode", "shots"):
        if not spec.get(key):
            raise ExportError("AS_EXPORT is missing %s" % key)
    found = Rhino.Display.DisplayModeDescription.FindByName(spec["mode"])
    if found is None:
        raise ExportError("no display mode named %s; run AS_MODE modes" % spec["mode"])
    view = doc.Views.Find(spec["view"], False) if spec.get("view") else doc.Views.ActiveView
    if view is None:
        raise ExportError("view not found: %s" % spec.get("view"))
    os.makedirs(spec["out"], exist_ok=True)
    size = spec.get("size") or [1920, 1080]
    supersample = int(spec.get("supersample", 2))
    before = state_snapshot(doc)
    stray = leftovers(doc)
    vp = view.ActiveViewport
    saved_view = Rhino.DocObjects.ViewportInfo(vp)
    saved_mode = vp.DisplayMode
    files, mode_failures, restore = [], {}, []
    try:
        for shot in spec["shots"]:
            restore_layers(doc, restore)
            restore = isolate(doc, shot)
            files.append(capture_shot(doc, view, shot, spec["mode"], found, size, supersample, spec["out"]))
            actual = view.ActiveViewport.DisplayMode.EnglishName
            if actual != found.EnglishName:
                mode_failures[files[-1]] = "the viewport was in %s, not %s" % (actual, found.EnglishName)
    finally:
        restore_layers(doc, restore)
        vp.SetViewProjection(saved_view, True)
        vp.DisplayMode = saved_mode
        view.Redraw()
    results = verify_files(files, spec["mode"], spec)
    for entry in results:
        if entry["file"] in mode_failures:
            entry["failures"].append(mode_failures[entry["file"]])
    held = state_snapshot(doc) == before
    if stray:
        print("  flag: temporary objects are in the model and may show in the files: %s" % ", ".join(stray[:10]))
    if not held:
        print("  FAIL: the document changed during the export: layers, materials or object count")
    with open(os.path.join(spec["out"], "export-manifest.json"), "w", encoding="utf-8") as handle:
        json.dump({"mode": spec["mode"], "files": results, "document_unchanged": held}, handle, indent=1)
    for entry in results:
        if entry["failures"]:
            folder, name = os.path.split(entry["file"])
            os.replace(entry["file"], os.path.join(folder, "FAILED-" + name))
            print("  moved aside: FAILED-" + name)
    return report(results, spec["mode"], spec) and held


def main():
    import Rhino

    doc = globals().get("__rhino_doc__") or Rhino.RhinoDoc.ActiveDoc
    mode = globals().get("AS_MODE", "export")
    spec = globals().get("AS_EXPORT") or {}
    if mode == "modes":
        for item in Rhino.Display.DisplayModeDescription.GetDisplayModes():
            print(item.EnglishName)
        return
    if mode == "verify":
        report(verify_files(spec.get("files") or [], spec.get("mode"), spec), spec.get("mode"), spec)
        return
    try:
        export(doc, spec)
    except ExportError as exc:
        print("Export: FAILED - %s" % exc)
        print("ASEXPORT status=fail files=0")


if "__rhino_doc__" in globals():
    main()
