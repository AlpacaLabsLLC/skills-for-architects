# Quantities

The specification for `as-bom.py`. All of this comes from one working session with no baseline, so treat it as a working method, not a proven one.

## Specification

Lengths are in the document's units.

```python
SPEC = {
  "covers": "Everything in option A at the current model state",
  "out": "<folder the user chose>",
  "scopes": [{"layer": "Building::Option A", "label": "option-a"}],
  "kerf": 0.003,
  "sections": {
    "2x6": {"w": 0.038, "d": 0.14, "label": "2x6 (38x140)", "stock": 3.6},
    "G2x8": {"w": 0.038, "d": 0.184, "label": "2x8 girder", "stock": 4.88, "drives_design": True},
  },
  "rules": [
    {"match": ["Stud", "Top plate"], "category": "Lumber", "item": "2x6 framing", "measure": "section_length", "section": "2x6"},
    {"match": "Sloped joist", "category": "Lumber", "item": "Sloped joist", "measure": "volume_over_section", "section": "2x6", "cut": True},
    {"match": "Roof membrane", "category": "Roof", "item": "Membrane", "measure": "half_area", "qty_is_total": True,
     "purchase": {"group": "Membrane", "waste": 0.15, "unit": "m2 with laps"}},
    {"match": "Sheathing 12 mm", "category": "Sheet goods", "item": "Sheathing", "size": "12 mm", "measure": "volume_over_thickness", "thickness": 0.012,
     "purchase": {"group": "Plywood 12 mm", "sheet_area": 2.9768, "sheet_label": "sheets 1.22x2.44", "waste": 0.10}},
    {"match": "Drain*", "layer": "Plumbing*", "category": "Pipe", "item": "Drain", "size": "110 mm PVC", "measure": "volume_over_pipe", "dia": 0.11, "material_assumed": True},
    {"match": "Anchor bolt", "category": "Connectors", "item": "Anchor bolt", "measure": "count", "to_engineer": True},
  ],
  "excluded": [{"match": "Markup*", "reason": "user's markup, not part of the building"}],
  "allowances": [{"category": "Sheet goods", "item": "Interior lining", "qty": 12, "unit": "sheets", "source": "calculated", "note": "from wall area net of openings"}],
  "not_counted": [{"item": "Fasteners and nails", "reason": "not modeled"}, {"item": "Pipe fittings and traps", "reason": "not modeled"}],
}
```

A rule applies to a name, and to a layer path below the scope when `layer` is given. The first match wins. Each object is counted in one line.

Rule keys beyond those shown: `length_group` (see Grouping cut lengths), `per` (a count per object, such as 0.5 when two modeled parts make one item; fragile, so say so in `note`), `cut` (send a length measure to the cut list and nesting), `allowance` (added to `hypotenuse`), `waste` and `qty_is_total` (Qty is the total including waste), `unit` (labels Qty: a count label such as `sheets` or `pairs`, since Qty counts pieces unless `qty_is_total` is set; a length, area or volume unit there is refused, because Total already carries the measure in its own unit), `source` (`measured`, `calculated`, `assumed`), `note`, `material_to_confirm`.

## Picking the measure

| Measure | For | Note |
|---|---|---|
| `count` | Fixtures, hardware | One object, one item |
| `section_length` | Straight orthogonal members | Fails if the bounding box does not fit the section |
| `volume_over_section` | Sloped or rotated members | A bounding box is wrong for these |
| `hypotenuse` | Stringers | Longest two dimensions, plus `allowance` |
| `longest` | Battens and strips with no fixed section | |
| `plan_area` | Decks and slabs | Two largest dimensions |
| `volume_over_thickness` | Sheet goods | |
| `half_area` | Membranes | Volume over thickness was wrong at 1 mm |
| `volume_over_pipe` | Pipe | `dia` is the modeled outside diameter |
| `volume` | Concrete, solids | Say what was not modeled inside, such as reinforcement |

## Grouping cut lengths

Members with the same category, item, section and source share a line when their cut lengths are close. The line gives the count, one length or a `shortest to longest` range, the exact total, and the source. Each object is still counted once, so the reconciliation does not change, and every exact length still goes to nesting.

`length_group` sets how close: the whole span of a line stays within it. The default is 25 mm in the document's units, a working value rather than a fabrication tolerance, and 0 groups identical lengths only. Set it for the whole specification, or on a rule. On a curved plan where every member differs, set a wider value on that rule so the BOM stays readable.

When a line gives a range, the CSV lists each exact length and its count under `Cut schedule`, after the reconciliation. An item that still takes more than one line fails a [rhino-thinline](../../rhino-thinline/SKILL.md) table lookup, so give it a wider `length_group` or separate item names before drawing a table.

## Rules for the content

- **Sources.** A line that was estimated moves to measured when the element becomes modeled. An allowance has no object behind it and is never `measured`.
- **Assumed materials go inside the line** ("PVC (material assumed)", "material to confirm"), through `material_assumed` and `material_to_confirm`.
- **Stock.** Nest cuts per section. Give a section its own stock length when it needs one, and set `drives_design` when that length sets joints and supports: changing it changes the model.
- **Report what varies.** With several scopes the run prints what is the same in every scope and a table of what differs. Use that in the report.

## Unconfirmed defaults

Seen once with no test, and not adopted as rules. Ask the user before relying on them.

- Waste: 10% for plywood and cladding, 15% for wrap with laps.
- Model one purchasable item as one object. Counting two legs at 0.5 each worked but is fragile.
