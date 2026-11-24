# Clash, connectivity and connection checks

Requirement keys for models with more than one system, read by the requirements check. Write them with the other requirements, before the first build script. The exact format is at the top of [as-check-model.py](../scripts/as-check-model.py).

## When to add them

| The model has | Add |
|---|---|
| Two systems that could run into each other (plumbing, ducts, structure, envelope) | `clash` for each system against the others |
| Envelope layers that lap at an opening (flashing, barrier, sheathing, cladding) | `clash` for each flashing against the layers it laps, which may touch it but not pass through it; flashing and membranes as closed solids listed in `closed`, because open surfaces are skipped |
| Fixtures, a supply or a drain | `network` for each of supply and drain |
| Bolts, hangers, ties or other connectors | `hardware`, or name them as placeholders |

A check that is not asked for is not run, and the status line says so. A selector that matches nothing never passes, so match the layer words and object names the build will really use.

## Clash

```json
"clash": {"Cold": {"against": ["Piers", "Girders", "Tank"]}},
"intended": [{"a": "cold riser*", "b": "tank*", "why": "the riser feeds the tank"}]
```

Each entry reports overlaps between its group and `against`, or everything else under the parent when `against` is left out. Faces that only touch are not a clash. Solids and centreline curves are tested; open surfaces and meshes are skipped and counted (an entry whose overlapping pairs were all skipped is not measured, and fails), and a pair that cannot be decided is named.

**Undecided pairs pass.** When two solids overlap in their boxes but neither the point test nor Rhino's boolean can settle it (faces that touch on a slope, or a part thinner than the sampling, where the boolean returns nothing), the pair does not fail the entry: the result counts it in `undecided` and lists it as `undecided: a x b`. Read each one in the model or a section and report how it was settled; an undecided pair is not proof that the parts are clear.

Each result gives the members matched on each side and the pairs tested. Read a zero with those counts:

| Members | Pairs tested | Result |
|---|---|---|
| On both sides | 0, no boxes overlap | Pass, printed as `clear` |
| None on a side the requirement names (a name glob, or a layer word whose `layers` entry does not allow zero) | 0 | Fail |
| None on any other side (everything else under the parent is empty, or a layer word with `"min": 0`) | 0 | `NOT MEASURED`: counts as unmet and is named on the status line |

`intended` declares connections that are meant to overlap. Each pair needs a `why`, and a bare wildcard is refused. Every excused pair is printed, so a declaration is visible rather than silent. Declare only real connections: a riser into a tank is one, and a riser through a pier never is. A declaration excuses the whole overlap of that pair, including one that runs too deep, so check those by section.

## Connectivity

```json
"network": {"Drain": {"pipes": ["Drain", "Fittings"], "fixtures": {"name": ["toilet bowl*", "basin*"]}, "to": {"name": ["sump*"]}}}
```

Every fixture must reach the `to` object through connected pipes. Pieces connect when they touch or overlap within `tol` (default 10x the document tolerance). A fixture that does not reach it and a pipe not connected to it both fail, and the report gives the nearest gap. Name one object per fixture in `fixtures` (the bowl, not the whole toilet). The check is topology only: slopes, diameters, traps and venting are not checked.

## Connections

```json
"hardware": {"Anchor": {"items": {"name": ["anchor*"]}, "joins": ["Piers", "Girders"], "past": {"of": "Girders", "by": 0.05, "axis": "z"}}}
```

Each item must touch every `joins` group and, with `past`, extend beyond the members it touches. This catches a bolt that stops short or reaches nothing. It is plausibility only: strength, nuts and washers, and a bolt lying in a seam between plies are not detected, so cut a section as well (the procedure's Check step).

When a connector is schematic, set `"placeholder": true` and put "placeholder" in the object name. The check then requires only the name and says no connection was checked.

## Proportion, cover and bearing

Cheap checks for envelopes and hardware, for any building and material:

```json
"proportion": {"Sealant": {"items": {"layer": "Sealant", "name": ["*bead*"]}, "axis": "y", "ratio": [0.4, 0.75]}},
"cover": {"Siding": {"items": "Siding", "axis": "y", "region": [[-24, 0], [35, 97]], "holes": [[[-1, 37], [35, 89]]]}},
"bears": {"Casing legs": {"items": {"layer": "Exterior Trim", "name": ["*casing*"]}, "on": [{"name": ["*sill*"]}]}}
```

- **`proportion`:** each item's size along `axis`, over the smaller of its other two sizes, lies in `ratio`. A sealant joint about half as deep as wide, measured across the wall, is `ratio` 0.4 to 0.75.
- **`cover`:** the items cover a face region with no gap: the face across `axis`, with the region and holes in the other two axes in x, y, z order. The holes are the openings with their trim and nothing else, so cladding or flashing that stops short of an opening fails.
- **`bears`:** every vertical member (taller than wide) rests on material across its whole foot (a 3 x 3 grid just below it). A casing leg or jamb cut flat over a sloped sill fails.
- **Hinges:** `hardware` with `"tol"` set to the document tolerance requires each leaf to touch its knuckle, and `clash` between the knuckles and the leaves catches parts modeled through each other.

## Flags in the report

- **Written after geometry existed.** A revision that changes measured checks once the model exists is listed with its reason. It reaches the `Check notes` line (for `as:run-notes`, never the reply's opening line) unless it is a user correction or brief change, and always when it changes a check that was failing. Requirements are set before the design; never change one to make a real failure pass. A revision for a design change, by you or the user, is correct even though it is listed ([the form-change rule](../SKILL.md#when-the-form-changes)).
- **Count range too wide.** Derive `min` and `max` from the layout constants and say how in `derived` (`"derived": "4 piers x 3 rows"`). A range with a spread above 2 and above 20% of the maximum is flagged.
- **Derived count may be stale.** A `layers` entry with a `derived` note is flagged, on the `Check notes` line too, when its layer's overall size has moved by more than 1% since the revision was first measured. The flag does not change the pass or fail result. It is a prompt to work the count out again, not proof that it is wrong, and it misses a change inside an unchanged extent. A new revision clears it ([the form-change rule](../SKILL.md#when-the-form-changes)).
- **Code.** Set `code` whenever a value comes from a code: `{"jurisdiction": "Example County", "used": "2010 ADA Standards", "status": "stand-in"}`. `status` is `adopted` when the local code's own text was used, `stand-in` when a foreign code stands in, and `none` when no code applies.
