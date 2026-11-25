# RhinoCommon patterns

Patterns for scripts run through Rhino's `run_python` tool (first measured on Rhino 8, CPython 3; they hold on Rhino 9). Each one states the failure it avoids. They were exercised in the 2026-09-28/29 modeling sessions and in the maintainers' modeling evaluations.

## Script skeleton

```python
import traceback, Rhino, System
G = Rhino.Geometry
d = __rhino_doc__            # injected document handle; do not rely on scriptcontext

def model_view(d):
    """Make a model viewport the active view. With a layout active, added objects land on its page."""
    if isinstance(d.Views.ActiveView, Rhino.Display.RhinoPageView):
        views = list(d.Views.GetViewList(True, False))   # model views only
        if not views:
            raise RuntimeError("no model viewport to build in; open one (for example Perspective) and run again")
        d.Views.ActiveView = views[0]
    return d.Views.ActiveView

try:
    model_view(d)
    # --- constants (document units) ---
    BAY = 144.0
    # --- build ---
    # --- checks: one short line each ---
    print("posts", 12)
    d.Views.Redraw()
except Exception:
    print(traceback.format_exc())
```

- **Use `run_python`, not `run_csharp`.** `run_csharp` returned empty output and no error when a script failed to compile.
- **No property setters in constructors.** `Rhino.DocObjects.Layer(Name="Walls")` raises `TypeError: No overload for method 'Layer..ctor{}' takes '0' arguments` in Rhino 8's CPython; construct, then assign (`L = Layer(); L.Name = ...`). The same holds for every RhinoCommon type.
- **Print short lines.** One multi-kilobyte `print` was dropped whole while the same text split into lines came back intact. Rhino command-line messages can appear in stdout; parse only your own lines.

## Python traps in Rhino 8

These are Python and binding behaviours, not API facts, so the API reference does not show them:

| Trap | Use |
|---|---|
| `System.Math.cos(a)` | `math.cos(a)` |
| a Python list passed to a collection overload (`Brep.CreateBooleanDifference([a], [b], tol)` bound to the single-`Brep` overload) | `from System.Collections.Generic import List`, build `List[G.Brep]()` and `.Add` each item |
| `len()` on a Rhino list | `.Count` |
| `GH_DataMapping.None` (a Python syntax error) | `System.Enum.ToObject(GH_DataMapping, 0)` |

## Verify by measurement

Measure the result in the document; the constants describe intent, not what was built.

```python
# height of anything above a point (for example a handrail above a stair nosing)
seg = G.LineCurve(G.Point3d(x, y, z + 20), G.Point3d(x, y, z + 60))
ok, _, hits = G.Intersect.Intersection.CurveBrep(seg, brep, 0.01)
top = max(h.Z for h in hits) if ok and hits else None

# walking surfaces: horizontal faces with open space above, whichever way the solid's normals point
amp = G.AreaMassProperties.Compute(face.DuplicateFace(False))
is_top = not brep.IsPointInside(G.Point3d(amp.Centroid.X, amp.Centroid.Y, face_bbox.Max.Z + 0.05), 0.001, False)
```

Group repeated elements before checking them (risers per flight, not across the whole stair), measure every instance rather than a sample, and measure clear widths between the actual faces.

## Units

```python
units = str(d.ModelUnitSystem)      # e.g. "Inches", "Millimeters"
scale = Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Feet, d.ModelUnitSystem)  # feet -> document units
```

Read units before the first constant; convert briefed values with `UnitScale`, and report in document units.

## Layers and names

```python
def layer(path, color=None):
    """Create or find a layer by full path, e.g. 'Barn::Structure::Posts'."""
    parent = None
    for part in path.split("::"):
        full = part if parent is None else d.Layers[parent].FullPath + "::" + part
        j = d.Layers.FindByFullPath(full, -1)
        if j < 0:
            L = Rhino.DocObjects.Layer(); L.Name = part
            if parent is not None:
                L.ParentLayerId = d.Layers[parent].Id
            if color is not None:
                L.Color = System.Drawing.Color.FromArgb(*color)
            j = d.Layers.Add(L)
        parent = j
    return parent

def attrs(layer_index, name):
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = layer_index; a.Name = name
    a.Space = Rhino.DocObjects.ActiveSpace.ModelSpace   # with model_view(d) first: model, not a layout page
    return a
```

Look layers up by full path, never by short name: the same child name exists under many parents. A deleted layer returns `None` for `FullPath`, so filter `not l.IsDeleted` before reading it.

## Geometry

```python
d.Objects.AddLine(G.Line(G.Point3d(0,0,0), G.Point3d(0,0,H)), attrs(L_POST, "post"))
d.Objects.AddPolyline(G.Polyline([p0, p1, p2, p3, p0]), a)
d.Objects.AddPoint(G.Point3d(x, y, z), a)

# planar surface with holes: outer loop plus inner loops, all closed and coplanar
outer = G.Polyline([...]).ToNurbsCurve()
holes = [G.Rectangle3d(G.Plane.WorldXY, G.Interval(x0, x1), G.Interval(y0, y1)).ToNurbsCurve() for ...]
breps = G.Brep.CreatePlanarBreps([outer] + holes, d.ModelAbsoluteTolerance)
# expect one brep; its face should have len(holes) + 1 loops

# extrusion of a closed planar curve to a solid
ext = G.Extrusion.Create(curve, height, True)          # cap=True; height sign follows the curve plane normal
brep = ext.ToBrep()

# box from a centre and sizes: Box takes intervals, Center Box components take HALF sizes
box = G.Box(G.Plane(center, G.Vector3d.XAxis, G.Vector3d.YAxis),
            G.Interval(-L/2, L/2), G.Interval(-T/2, T/2), G.Interval(-H/2, H/2)).ToBrep()
```

## Booleans

```python
def solid_ok(b):
    return b is not None and b.IsSolid and G.VolumeMassProperties.Compute(b) is not None

before = [G.VolumeMassProperties.Compute(b).Volume for b in parts]
res = G.Brep.CreateBooleanUnion(parts, d.ModelAbsoluteTolerance)
if not res or len(res) != 1 or not solid_ok(res[0]):
    # keep the parts, name them, report the failure
    ...
```

A union once returned a wrong fragment with no error, and returned `None` on coincident faces. Check `IsSolid` and volume before and after, and for a difference confirm the volume dropped by the cutter's overlap.

Thin solids fail booleans: a 1 mm layer failed against a trim box at tolerance 0.001. Clamp its bounding box to the trim, or build it from strips.

## SubD

```python
mesh = G.Mesh.CreateFromBox(G.Box(...), nx, ny, nz)   # quad cage
subd = G.SubD.CreateFromMesh(mesh)
d.Objects.AddSubD(subd, a)
```

Build SubD from a quad mesh cage; report face and vertex counts from the SubD object.

The smoothed SubD sits inside its cage, so a cage built to the briefed size comes out smaller. Build it, measure `GetBoundingBox(True)`, scale the cage by target over measured on each axis, and rebuild (two or three passes converge).

## Curvature

```python
sc = srf.CurvatureAt(u, v)          # SurfaceCurvature; srf is a Surface (brep.Faces[0] works)
k, h = sc.Gaussian, sc.Mean         # sphere of radius 10: Gaussian 0.01
```

There is no `SurfaceCurvature.Evaluate`. Sample a grid of (u, v) over `srf.Domain(0)` and `srf.Domain(1)` and report the minimum and maximum Gaussian curvature; a Gaussian vault has both signs.

## Transforms and arrays

```python
xf = G.Transform.Rotation(angle_radians, G.Vector3d.ZAxis, center)
copy = brep.DuplicateBrep(); copy.Transform(xf)
```

## Finding and clearing your own objects

```python
def objects_on(path):
    j = d.Layers.FindByFullPath(path, -1)
    return [] if j < 0 else list(d.Objects.FindByLayer(d.Layers[j]) or [])

def clear_parent(parent):
    """Rebuild, do not patch: delete this task's objects under the parent before regenerating."""
    for L in [l for l in d.Layers if not l.IsDeleted and (l.FullPath == parent or l.FullPath.startswith(parent + "::"))]:
        for o in d.Objects.FindByLayer(L) or []:
            d.Objects.Delete(o, True)
```

## Counts

Count live objects by enumeration, with hidden and locked objects on; otherwise an object on a hidden layout drops out:

```python
s = Rhino.DocObjects.ObjectEnumeratorSettings(); s.HiddenObjects = True; s.LockedObjects = True
live = list(d.Objects.GetObjectList(s))
```

`d.Objects.Count` and `save_doc` include deleted objects still held for undo (83,244 against 32,214 live; 256 against 253).

## Captures

Capture only when the user is watching or asks, or when a printed check cannot settle the question. Render in the script, not with the capture tool:

```python
v = d.Views.GetViewList(True, False)[0]; vp = v.ActiveViewport
vp.SetProjection(Rhino.Display.DefinedViewportProjection.Perspective, "Perspective", True)
vp.SetCameraLocations(target, camera); vp.CameraUp = G.Vector3d.ZAxis
vp.ZoomBoundingBox(bbox); v.Redraw()
v.CaptureToBitmap(System.Drawing.Size(640, 560)).Save(path)   # then read the PNG
```

The capture tool's `cameraLocation`/`target` produced an empty view, its `view` argument turned the Perspective viewport into a second Front view, and its images arrived as text that could not be viewed (about 30k tokens each). Scripted captures worked every time.

## Documents

Never rely on `close_doc` or `open_doc` for a fresh document. On Rhino 8 for Mac, `close_doc` saved and reported success while the document stayed open, and closed the open Grasshopper definitions; `open_doc` threw and imported nothing. Build under a new parent layer instead, and say the document is not saved unless the user asked for a save.

`save_doc` writes a copy and leaves the document untitled: `d.Path` stays `None` and Rhino still reports unsaved changes. Verify the copy with `File3dm.Read` (object count, a named object, a layer path), and tell the user to use Save As.
