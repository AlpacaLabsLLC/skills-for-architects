# Grasshopper definitions

Build a definition in one `run_python` script with the Grasshopper SDK. The pattern below was run against Rhino 8 for Mac on 2026-09-29: a Wall length slider moved from 240 to 480 in and the area output went from 28,800 to 57,600 sq in, then back.

## Rules

- **Use the SDK in `run_python`.** `g1_apply_graph` failed twice with an opaque error; single `g1_place_*` calls work but take one call per component (the diagrid took 18 calls). One script built the Dieste definition, with 11 sliders, and it solved with no runtime messages on its first run.
- **Create a document when none exists.** Grasshopper can start with no document, and every canvas call fails until one exists.
- **Leave the user's canvas as you found it.** Keep a reference to the active document, and restore it in a `finally` block. A script that fails after switching the canvas otherwise leaves an unnamed half-built definition active.
- **Read input names before wiring.** Print `[p.NickName for p in c.Params.Input]` in the same script and wire by index after checking; a guessed nickname (`inputs['S']` on the Square grid) raised `KeyError` and cost a retry.
- **Look up components, not parameters.** `ComponentServer.FindObjectByName("Rectangle", ...)` returned the Rectangle *parameter*. Filter proxies to `IGH_Component` instances, and read input nicknames from the instance before wiring.
- **Import the right namespaces.** `GH_NumberSlider` is in `Grasshopper.Kernel.Special`; `GH_SliderAccuracy` is in `Grasshopper.GUI.Base`, not `Grasshopper.Kernel`.
- **Expire before solving.** Components added to an already-solved document by script did not compute on `NewSolution(True)` until every object was expired first.
- **Flatten with components.** Boundary Surfaces made one surface per branch when the outer rectangle and the openings arrived in different branches; setting the input to Flatten did not take effect. Put Flatten Tree components on each curve stream.
- **Slider values are .NET `Decimal`.** Set with `System.Decimal(x)`; read with `float(str(v))`. `int()` on a Decimal raised halfway through a script and left a half-rewired definition, so compute every value before mutating anything.
- **Set enum values by number when the name is unreachable:** `GH_DataMapping.None` is a Python syntax error; use `System.Enum.ToObject(GH_DataMapping, 0)`.
- **Label sliders by `NickName`**, exactly as the brief names them. Checkers identify sliders by type, so setting `Name` as well is harmless but unnecessary.
- **Preview is invisible to captures.** Bake the default result to named layers before verifying or capturing.
- **Check the baked count after every bake.** After a save, a solve can report "Solution aborted" and return 0 solids, and a bake then clears the row. Reload, solve and bake again, and compare the count with the expected one.
- **Bake in stages when the user is watching.** With redraw off a whole row appears at once. Bake by assembly and redraw between assemblies.

## Pattern

```python
import traceback, Rhino, System, Grasshopper
from Grasshopper.Kernel import GH_Document, IGH_Component
from Grasshopper.Kernel.Special import GH_NumberSlider
from Grasshopper.GUI.Base import GH_SliderAccuracy
G = Rhino.Geometry
d = __rhino_doc__
srv = Grasshopper.Instances.ComponentServer
canvas = Grasshopper.Instances.ActiveCanvas
prev = canvas.Document if canvas else None
gdoc = GH_Document()
Grasshopper.Instances.DocumentServer.AddDocument(gdoc)
if canvas:
    canvas.Document = gdoc
ok = False
try:
    def comp(name, x, y):
        for p in srv.ObjectProxies:
            if p.Desc.Name == name and not p.Obsolete:
                c = p.CreateInstance()
                if isinstance(c, IGH_Component):
                    c.CreateAttributes(); c.Attributes.Pivot = System.Drawing.PointF(x, y)
                    gdoc.AddObject(c, False); return c
        raise ValueError("no component " + name)

    def slider(nick, lo, hi, val, x, y, integer=False):
        s = GH_NumberSlider(); s.CreateAttributes(); s.NickName = nick
        s.Slider.Minimum = System.Decimal(lo); s.Slider.Maximum = System.Decimal(hi)
        if integer:
            s.Slider.Type = GH_SliderAccuracy.Integer
        s.Slider.Value = System.Decimal(val)
        s.Attributes.Pivot = System.Drawing.PointF(x, y); gdoc.AddObject(s, False); return s

    W = slider("Wall length", 120, 480, 240, 0, 0, True)
    H = slider("Wall height", 96, 144, 120, 0, 40, True)
    rect = comp("Rectangle", 200, 0)           # inputs P, X, Y, R
    rect.Params.Input[1].AddSource(W); rect.Params.Input[2].AddSource(H)
    flat = comp("Flatten Tree", 300, 0); flat.Params.Input[0].AddSource(rect.Params.Output[0])
    bs = comp("Boundary Surfaces", 400, 0); bs.Params.Input[0].AddSource(flat.Params.Output[0])
    ar = comp("Area", 500, 0); ar.Params.Input[0].AddSource(bs.Params.Output[0])

    def solve():
        for o in gdoc.Objects:
            o.ExpireSolution(False)
        gdoc.NewSolution(True)
        return [float(str(v.Value)) for v in ar.Params.Output[0].VolatileData.AllData(True)]

    base = solve()
    errors = [o.NickName for o in gdoc.Objects if str(getattr(o, "RuntimeMessageLevel", "")) == "Error"]
    W.Slider.Value = System.Decimal(480); moved = solve()
    W.Slider.Value = System.Decimal(240); solve()
    print("errors", errors); print("area", base, "->", moved)

    # bake the default result
    li = d.Layers.FindByFullPath("Wall::Panel", -1)       # created beforehand with the layer helper
    a = Rhino.DocObjects.ObjectAttributes(); a.LayerIndex = li; a.Name = "wall panel"
    for g in bs.Params.Output[0].VolatileData.AllData(True):
        if isinstance(getattr(g, "Value", None), G.Brep):
            d.Objects.AddBrep(g.Value, a)
    ok = True
except Exception:
    print(traceback.format_exc())
finally:
    if not ok:                                   # do not leave a half-built definition behind
        Grasshopper.Instances.DocumentServer.RemoveDocument(gdoc)
        if canvas:
            canvas.Document = prev
d.Views.Redraw()
```

Keep the definition open and active when it succeeds: it is the deliverable. Save it only when the user asks, and report its file path or that it is unsaved.

## Slider test

For each slider the brief names, move it once to a value that changes the output in a predictable way, re-solve (expire first), compare the output with the expected change, then restore the default and re-solve. Report the moved value and the observed output in the report's Grasshopper table. A slider whose move does not change the output is unwired, and the definition is not done.

## Worked definitions

Built in the 2026-09-28/29 sessions; components read back from the saved definitions on 2026-09-29:

| Definition | Sliders | Components | Live check |
|---|---|---|---|
| Ruled diagrid | base radius, top radius, height, twist, U bays, V tiers, member radius | Circle ×2, Rotate, Radians, Ruled Surface, Divide Domain², Isotrim, Deconstruct Brep, List Item ×4, Line ×2, Pipe ×2, Length, Mass Addition | member count and total length reported from the definition |
| Dieste brick wall | wall length, wall height, amplitude, wavelength, origin X, top-curve samples, brick length/height/thickness, mortar joint, centroid offset | Range, Division, Pi, Multiplication, Sine, Construct Point ×4, Interpolate, Line, Ruled Surface, Contour, Flatten Tree ×2, Divide Length ×2, Dispatch, Cull Pattern ×4, Surface Closest Point, Evaluate Surface, Cross Product, Amplitude, Move, Construct Plane, Center Box, List Length | bricks per course grow toward the crown; alternate courses offset half a module |
| Window wall | wall length, wall height, window count | XZ Plane ×2, Rectangle ×2, Range, Construct Domain, Addition, Cull Index, Construct Point, Flatten Tree ×2, Boundary Surfaces | window count 5 → 34,560 sq in and 5 holes; wall length 480 → 52,416 sq in and 3 holes |
| Column grid | bays X, bays Y, spacing | Square (grid) | point count equals (bays X + 1) × (bays Y + 1) after each move |
