# Element recipes

Defaults fill gaps in a brief; every filled value is listed as an assumption in the report. The brief wins over a default. When the studio has adopted its own modeling standards, those win over these defaults; name the standard used.

Values are US customary because the reference sessions were modeled in inches; convert to document units with `UnitScale`. "Forces" is what the element requires of its neighbours, and building it is part of the element.

| Element | Defaults | Rules | Forces |
|---|---|---|---|
| Post grid | bay 12 ft; aisles 8 ft side, 12 ft centre | posts at every grid intersection | plates at post tops |
| Floor | joists 24 in on centre; girders on every post row | joists span the short direction; solve the framing depth before accepting a higher floor (flush-hung joists between double girders are much shallower than stacked joists) | transverse beams at every post line; a raised floor lengthens every ramp and resets step risers |
| Built-up member | staggered joints | lay out joints first: each lands on a support and no piece exceeds stock length | joints set the support positions |
| Toilet room | none | resolve door swing, hinge side, fixture offset and the turning circle together; never centre a fixture on the back wall by default | door and fixture move together |
| Connector hardware | none | a modeled bolt or hanger looks real and gets counted: model the actual connection, or name it a placeholder ([checks](checks.md)) | a section cut through one of each type |
| Stair | riser 7–8 in, tread 10–11 in, width 36–44 in, headroom 80 in | fit within one bay so the top nosing lands on a beam | floor opening from the headroom line; header, trimmers and split joists; guard at 36 in |
| Handrail (stair) | 34–38 in above the nosing line; both sides of egress stairs | the height holds at every nosing, including where a continuous rail turns at a landing or wraps a switchback: a transition may rise above 38 in but never drop below 34 in (a wrapped inner rail at 30–32 in over four treads failed review, 2026-09-30) | extensions at the top and bottom of each flight |
| Gable roof | 6:12 pitch; rafters 48 in on centre; one purlin per plane | ridge at mid-span of the aisle it covers | ridge line, plates, gable-end ties |
| Shed roof | 4:12 pitch | rises from the outer eave to the inner post | shed plate on the inner post row |
| Clerestory | band 36–48 in tall above the shed plate | frames inset 6 in from posts | inner posts taller than outer |
| Window | 36 × 48 in ground floor, 48 × 48 in upper; sill 36 in | one per bay per wall unless told otherwise | hole in the wall surface; in a stud wall, the framing below |
| Sliding door | 10 × 10 ft opening; two leaves; track 12 in above the head | leaves 4 in outside the wall; X brace per leaf | hole in the end wall; track long enough to open fully |
| Cladding | walls to the eave; roof planes as quads | surfaces with holes for every opening on that plane; lapped courses and flashing run unbroken above and below each opening, stopping only at its trim (`cover`) | none |
| Sealant joint | depth about half the width, over a backer rod | the bead is shallower than it is wide, never deeper; the rod sits behind it, filling the rest of the joint (`proportion`) | backer rod in every sealed joint |
| Trim on a sloped sill | casing legs and frame jambs cut to the sill's slope | a leg or jamb bears on the sill across its whole foot; a flat cut over a slope leaves a gap (`bears`) | none |
| Hinge | leaves and knuckle as separate solids | each leaf touches its knuckle within the document tolerance and nothing interpenetrates: the knuckle sits beside the leaves, not through them (`hardware` with `tol`, `clash`) | a hinge leaf on the jamb and one on the leaf or sash it carries |
| Stud wall | studs 16 in on centre; bottom plate and double top plate | every wall on every storey; gable-end studs up to the rafter line | each opening gets king and jack studs, a header and cripples |
| Steel exit door | 3070 hollow-metal leaf 1-3/4 in thick in a 16 ga double-rabbet frame; 5-3/4 in jamb, 2 in face | 1/8 in jamb and head clearance, 3/4 in undercut; 3 hinges; panic bar 34–48 in above the floor on the push side | closer and threshold; every part a closed, named solid |
| Ruled diagrid | ruled surface between two circles, top rotated by the twist angle; U × V panels | two diagonals per panel as centrelines, piped as members | member count and total length reported from the definition |
| Dieste brick wall | straight base, sine crown; brick 25 × 12 × 5.5 cm class; 1/2 in joints | courses by horizontal contour; running bond by half-module stations on alternate courses; each brick oriented to course tangent and surface normal | bricks per course grow toward the crown; no stacked joints |
| Gaussian vault | catenary sections across the span; rise varying sinusoidally along the length | loft through sections at 10 in spacing or closer; catenary, not parabola | Gaussian curvature of both signs |

## Acceptance reference

The framed barn from 2026-09-28 is the reference for framing briefs: 340 objects, including 224 studs at 16 in or less on centre, 24 plates, 1 header, 3 posts and beams, 30 floor joists, and 58 rafters and ridge, with one framed door opening. A framing model that omits studs, plates or opening framing is incomplete even when its massing is right.
