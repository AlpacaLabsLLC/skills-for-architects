# Display, views and materials

Read when setting up a view or material, or when a capture misbehaves.

## Safe capture

The method `as-batch-image-export.py` uses. Scripted captures worked every time; the capture tool's `cameraLocation` and `target` produced an empty view, and its `view` argument turned the Perspective viewport into a second Front view.

1. Use an existing view. Save it first: `ViewportInfo(vp)`, and restore with `vp.SetViewProjection(saved, True)`.
2. Show the shot's layers only, remembering what to restore.
3. Compute the camera from the object corners, in one step, with no trial captures. Use `vp.SetCameraLocations(target, camera)` and set `CameraUp` after. A fit that captures, measures and moves the camera repeatedly is slower and disturbs the view.
4. Set `vp.DisplayMode`, then `view.Redraw()`, then wait: six rounds of `Rhino.RhinoApp.Wait()` with a 0.25 s sleep. A capture taken at once may be stale.
5. Capture with the mode named, `view.CaptureToBitmap(Size(w * 2, h * 2), mode)`, scale down with bicubic interpolation, and save.
6. Read the file back. A capture that returned a picture of nothing fails as blank.

`AS_EXPORT` keys are listed at the top of [as-batch-image-export.py](../scripts/as-batch-image-export.py). Set `direction` to `birdseye` or `top` or a vector from the model to the camera. The camera always ends up outside the shot's layers, so an interior view cannot be framed this way.

The thresholds are working values, not calibrated: a sample is coloured above a channel spread of 12, a file fails above 0.1% coloured samples, and it is blank below 0.2% content. Override with `max_coloured_pct` and `min_content_pct`. A false failure prints the measured values.

## Views

Name a view with a script only when asked: `d.NamedViews.Add(name, view.ActiveViewportID)`. Use one existing view for a batch rather than creating views.

## Materials

Assign by layer, so a rebuild keeps it: find or add the material, then set `layer.RenderMaterialIndex` and commit. Object overrides do not survive a rebuild that clears the layer. Report which were assigned. Do not create a material to get a look for one capture.
