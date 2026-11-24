#! python3
"""Quantities from the model (Arch Studio, as-rhino-bom).

Reads every object under a layer path and puts each one in exactly one line of a bill of
quantities. The run fails, and writes no CSV, when any object cannot be placed.

Runs by file path through run_python, with __rhino_doc__ passed in:

    P = "<absolute path of this skill's folder>/scripts/as-bom.py"
    exec(compile(open(P).read(), P, "exec"), {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_MODE": "run", "AS_BOM": SPEC})

AS_MODE  "run" writes the CSVs; "check" reports the same reconciliation and writes nothing;
         "names" lists every name and layer under the scopes, to write the rules from.

AS_BOM (all lengths in the document's units; the full format is in references/quantities.md):
  covers       what this BOM covers, in words; required
  out          existing or creatable folder for the CSVs; required by "run"
  scopes       [{"layer": "Building::Option A", "label": "option-a"}, ...]
  sections     {"key": {"w": .038, "d": .14, "label": "2x6 (38x140)", "stock": 3.6, "drives_design": false}}
  kerf         saw kerf for nesting; default 0
  length_group near-identical cuts share a line when the whole line's span is within this length;
               default 25 mm in the document's units, 0 groups identical lengths only; a rule can
               set its own. Nesting always uses every exact length
  rules        [{"match": name or [names], "layer": optional glob, "category", "item", "size",
                 "measure", ...}], first match wins
  excluded     [{"match": ..., "layer": ..., "reason": "..."}], objects deliberately left out
  allowances   [{"category", "item", "size", "qty", "unit", "total", "total_unit",
                 "source": "calculated" | "assumed", "note"}], lines with no object behind them
  not_counted  [{"item": "...", "reason": "..."}]; required, and listed in every CSV

Standard library and RhinoCommon only. Rhino is imported only by the document reader, so the
logic also runs without Rhino.
"""
import csv
import fnmatch
import math
import os
import re
import time

SOURCES = ("measured", "calculated", "assumed")
SOURCE_LABEL = {"measured": "Measured from model", "calculated": "Calculated", "assumed": "Assumed"}
MEASURES = ("count", "section_length", "volume_over_section", "longest", "hypotenuse", "plan_area",
            "volume", "volume_over_thickness", "volume_over_pipe", "half_area")
CUT_MEASURES = ("section_length", "volume_over_section", "longest", "hypotenuse")
HEADER = ["Category", "Item", "Size", "Qty", "Unit", "Cut length", "Total", "Total unit", "Objects", "Source"]
UNITS = {"Meters": "m", "Millimeters": "mm", "Centimeters": "cm", "Inches": "in", "Feet": "ft"}
PER_METRE = {"m": 1.0, "mm": 1000.0, "cm": 100.0, "in": 1 / 0.0254, "ft": 1 / 0.3048}
DEFAULT_GROUP_METRES = 0.025  # a working value for "near-identical", not a fabrication tolerance


class BomError(Exception):
    """A specification the script cannot run."""


def _names(match):
    return [match] if isinstance(match, str) else list(match or [])


def matches(entry, name, layer_path):
    """A rule, or an exclusion, applies to an object name and its layer path below the scope."""
    if not name or not any(fnmatch.fnmatchcase(name, n) for n in _names(entry.get("match"))):
        return False
    return not entry.get("layer") or fnmatch.fnmatchcase(layer_path, entry["layer"])


def nest(cuts, stock, kerf=0.0):
    """First-fit descending with kerf. A cut longer than the stock is spliced from whole lengths.

    Returns (stock lengths needed, cuts that needed a splice)."""
    if stock <= 0:
        raise BomError("stock length must be positive, got %r" % stock)
    pieces, spliced = [], 0
    for cut in cuts:
        if cut > stock:
            spliced += 1
        while cut > stock:
            pieces.append(stock)
            cut -= stock
        pieces.append(cut)
    bins = []
    for piece in sorted(pieces, reverse=True):
        for i, room in enumerate(bins):
            if room >= piece + kerf:
                bins[i] = room - piece - kerf
                break
        else:
            bins.append(stock - piece)
    return len(bins), spliced


def group_lengths(lengths, tolerance):
    """Cut lengths as groups, shortest first. Measured from each group's shortest length, so that a
    long run of small steps cannot chain into one line."""
    groups = []
    for length in sorted(lengths):
        if groups and length - groups[-1][0] <= tolerance + 1e-9:
            groups[-1].append(length)
        else:
            groups.append([length])
    return groups


def length_tolerance(rule, spec, unit):
    """The rule's grouping length, else the specification's, else 25 mm. An unknown unit groups identical lengths only."""
    for owner in (rule, spec):
        if owner.get("length_group") is not None:
            return float(owner["length_group"])
    return DEFAULT_GROUP_METRES * PER_METRE.get(unit, 0.0)


def section_length(dims, section, tol=0.003):
    """The length of a straight member from its sorted bounding box, removing width and depth."""
    left = list(dims)
    for size in (section["w"], section["d"]):
        i = min(range(len(left)), key=lambda j: abs(left[j] - size))
        if abs(left[i] - size) >= tol:
            raise ValueError("bounding box %s does not fit section %s x %s; a sloped or rotated member needs "
                             "volume_over_section" % ([round(x, 4) for x in dims], section["w"], section["d"]))
        left.pop(i)
    return left[0]


def measure_value(rule, obj, sections):
    """The rule's measure for one object. Raises ValueError when the object cannot give it."""
    kind = rule["measure"]
    dims = obj["dims"]
    section = sections.get(rule.get("section")) if rule.get("section") else None

    def need(value, what):
        if value is None or value != value or value <= 0:
            raise ValueError("%s is unavailable on this object (open or invalid geometry?)" % what)
        return value

    if kind == "count":
        return 1.0
    if kind == "section_length":
        return section_length(dims, section)
    if kind == "volume_over_section":
        return need(obj["volume"](), "volume") / (section["w"] * section["d"])
    if kind == "longest":
        return dims[2]
    if kind == "hypotenuse":
        return math.hypot(dims[2], dims[1]) + float(rule.get("allowance", 0))
    if kind == "plan_area":
        return dims[1] * dims[2]
    if kind == "volume":
        return need(obj["volume"](), "volume")
    if kind == "volume_over_thickness":
        return need(obj["volume"](), "volume") / float(rule["thickness"])
    if kind == "volume_over_pipe":
        return need(obj["volume"](), "volume") / (math.pi * (float(rule["dia"]) / 2) ** 2)
    if kind == "half_area":
        return need(obj["area"](), "area") / 2.0
    raise ValueError("unknown measure %r" % kind)


def total_unit(rule, unit):
    """The unit a measure's total is in."""
    kind = rule["measure"]
    if kind == "count":
        return "pcs"
    if kind in ("plan_area", "volume_over_thickness", "half_area"):
        return unit + "2"
    if kind == "volume":
        return unit + "3"
    return unit


def validate(spec, need_out=False):
    """Every problem with the specification, as text. Empty when it can run."""
    problems = []
    for key in ("covers", "scopes", "rules"):
        if not spec.get(key):
            problems.append("missing %s" % key)
    if "not_counted" not in spec:
        problems.append("missing not_counted: list what the model does not contain, with the reason; an unmentioned omission reads as zero")
    if need_out and not spec.get("out"):
        problems.append("missing out: the folder for the CSVs")
    sections = spec.get("sections") or {}

    def bad_group(owner):
        value = owner.get("length_group")
        return value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0)

    if bad_group(spec):
        problems.append("length_group must be a length of 0 or more")
    for i, rule in enumerate(spec.get("rules") or []):
        where = "rule %d (%s)" % (i, rule.get("match"))
        if bad_group(rule):
            problems.append("%s: length_group must be a length of 0 or more" % where)
        for key in ("match", "category", "item", "measure"):
            if not rule.get(key):
                problems.append("%s: missing %s" % (where, key))
        if rule.get("measure") and rule["measure"] not in MEASURES:
            problems.append("%s: unknown measure %s" % (where, rule["measure"]))
        if rule.get("source", "measured") not in SOURCES:
            problems.append("%s: source must be one of %s" % (where, ", ".join(SOURCES)))
        needs_section = rule.get("measure") in ("section_length", "volume_over_section") or rule.get("cut")
        if needs_section and rule.get("section") not in sections:
            problems.append("%s: section %r is not in sections" % (where, rule.get("section")))
        if rule.get("cut") and rule.get("measure") not in CUT_MEASURES:
            problems.append("%s: cut needs a length measure" % where)
    for entry in spec.get("excluded") or []:
        if not entry.get("reason"):
            problems.append("exclusion %s: missing reason" % entry.get("match"))
    for entry in spec.get("allowances") or []:
        if entry.get("source") not in ("calculated", "assumed"):
            problems.append("allowance %s: source must be calculated or assumed, because no object was measured" % entry.get("item"))
    for entry in spec.get("not_counted") or []:
        if not entry.get("item") or not entry.get("reason"):
            problems.append("not_counted entry needs item and reason: %s" % entry)
    return problems


def describe(rule, note=""):
    """The Source text of a line: the source, then what the reader must not assume."""
    kind = rule.get("source", "measured")
    parts = [SOURCE_LABEL[kind]]
    for extra in (rule.get("note"), note):
        if extra:
            parts.append(extra)
    if rule.get("to_engineer"):
        parts.append("product to be engineered; a count does not validate the connection")
    return "; ".join(parts)


def item_label(rule):
    item = rule["item"]
    if rule.get("material_assumed"):
        return item + " (material assumed)"
    if rule.get("material_to_confirm"):
        return item + ", material to confirm"
    return item


def build(objects, spec, unit="m"):
    """Place every object in one line and reconcile. `objects` is a list of dicts with
    name, layer (path below the scope), dims (sorted bounding box), volume() and area()."""
    sections = spec.get("sections") or {}
    lines, cuts, cut_rows, purchase = {}, {}, {}, {}
    excluded, unclassified, errors, used = {}, {}, [], set()
    placed = 0

    for obj in objects:
        name, layer = obj.get("name") or "", obj.get("layer") or ""
        rule = next((r for r in spec["rules"] if matches(r, name, layer)), None)
        if rule is None:
            drop = next((e for e in spec.get("excluded") or [] if matches(e, name, layer)), None)
            if drop is not None:
                key = (name, drop["reason"])
                excluded[key] = excluded.get(key, 0) + 1
            else:
                key = (name or "(no name)", layer)
                unclassified[key] = unclassified.get(key, 0) + 1
            continue
        used.add(id(rule))
        try:
            value = measure_value(rule, obj, sections)
        except (ValueError, KeyError, ZeroDivisionError) as exc:
            errors.append("%s on %s: %s" % (name, layer, exc))
            continue
        placed += 1
        per = float(rule.get("per", 1))
        if rule.get("cut") or rule["measure"] == "section_length":
            length = round(value, 3)
            key = (rule["category"], item_label(rule), rule["section"], describe(rule), length_tolerance(rule, spec, unit))
            cut_rows.setdefault(key, []).append(length)
            cuts.setdefault(rule["section"], []).append(length)
        else:
            tunit = total_unit(rule, unit)
            waste = float(rule.get("waste", 0))
            if rule.get("qty_is_total"):
                qty = value * (1 + waste)
                qunit = rule.get("unit") or (tunit + (" incl %d%% waste" % round(waste * 100) if waste else ""))
            else:
                qty = per
                qunit = rule.get("unit", "pcs")
            total = value if rule["measure"] != "count" else per
            key = (rule["category"], item_label(rule), rule.get("size", ""), qunit, describe(rule, ("%d%% waste, working value" % round(waste * 100)) if waste else ""), tunit)
            q0, t0, n0 = lines.get(key, (0.0, 0.0, 0))
            lines[key] = (q0 + qty, t0 + total, n0 + 1)
        if rule.get("purchase"):
            group = rule["purchase"]["group"]
            entry = purchase.setdefault(group, {"purchase": rule["purchase"], "total": 0.0, "category": rule["category"], "size": rule.get("size", "")})
            entry["total"] += value

    rows, line_objects, sources = [HEADER], 0, {k: 0 for k in SOURCES}

    def emit(row, kind, objs):
        nonlocal line_objects
        rows.append(row)
        sources[kind] += 1
        line_objects += objs

    schedule, groups = [], []
    for (category, item, key, source, tolerance), lengths in cut_rows.items():
        groups += [(key, item, category, source, group) for group in group_lengths(lengths, tolerance)]
    for key, item, category, source, group in sorted(groups, key=lambda g: (g[0], g[1], g[4][0], g[3])):
        qty, label, shortest, longest = len(group), sections[key].get("label", key), group[0], group[-1]
        emit([category, item, label, qty, "pcs", shortest if shortest == longest else "%s to %s" % (shortest, longest), round(sum(group), 3), unit, qty, source], "measured" if source.startswith(SOURCE_LABEL["measured"]) else ("assumed" if source.startswith("Assumed") else "calculated"), qty)
        if shortest != longest:
            schedule += [[item, label, length, group.count(length)] for length in sorted(set(group))]
    purchases = {}
    for key in sorted(cuts):
        section, c = sections[key], cuts[key]
        total = sum(c)
        rows.append(["Cut lengths TOTAL", section.get("label", key), "", len(c), "cut pieces", "", round(total, 3), unit, "", "Measured from model"])
        sources["measured"] += 1
        if section.get("stock"):
            bars, spliced = nest(c, float(section["stock"]), float(spec.get("kerf", 0)))
            purchases[key] = bars
            why = "cuts nested first-fit descending with kerf; stock length is an assumption"
            if section.get("drives_design"):
                why += "; this stock length drives the design, so changing it moves joints and supports"
            if spliced:
                why += "; %d cuts are longer than stock and need a splice" % spliced
            rows.append(["Purchase", section.get("label", key), "%s %s stock" % (section["stock"], unit), bars, "stock lengths", "", "", "", "", "Calculated, " + why])
            sources["calculated"] += 1

    for (category, item, size, qunit, source, tunit), (q, t, n) in sorted(lines.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        emit([category, item, size, round(q, 2), qunit, "", round(t, 3), tunit, n, source], "measured" if source.startswith(SOURCE_LABEL["measured"]) else ("assumed" if source.startswith("Assumed") else "calculated"), n)

    for group in sorted(purchase):
        entry = purchase[group]
        buy, waste = entry["purchase"], float(entry["purchase"].get("waste", 0))
        amount = entry["total"] * (1 + waste)
        note = "%d%% waste, working value" % round(waste * 100)
        if buy.get("sheet_area"):
            rows.append(["Purchase", group, entry["size"], int(math.ceil(amount / float(buy["sheet_area"]))), buy.get("sheet_label", "sheets"), "", round(entry["total"], 3), unit + "2", "", "Calculated from the measured area, " + note])
        else:
            rows.append(["Purchase", group, entry["size"], round(amount, 2), buy.get("unit", unit + "2"), "", round(entry["total"], 3), unit + "2", "", "Calculated from the measured quantity, " + note])
        sources["calculated"] += 1

    for entry in spec.get("allowances") or []:
        kind = entry["source"]
        text = "NOT MODELED: " + SOURCE_LABEL[kind] + ("; " + entry["note"] if entry.get("note") else "")
        rows.append([entry.get("category", "Allowance"), entry["item"], entry.get("size", ""), entry.get("qty", ""), entry.get("unit", ""), "", entry.get("total", ""), entry.get("total_unit", ""), 0, text])
        sources[kind] += 1

    counted = line_objects
    not_excluded = sum(excluded.values())
    total_objects = len(objects)
    failures = []
    if unclassified:
        failures.append("%d objects are not in any line" % sum(unclassified.values()))
    if errors:
        failures.append("%d objects could not be measured" % len(errors))
    if not errors and counted + not_excluded + sum(unclassified.values()) != total_objects:
        failures.append("reconciliation: %d objects in the scope, %d placed, %d excluded, %d unclassified" % (total_objects, counted, not_excluded, sum(unclassified.values())))
    if counted != placed and not errors:
        failures.append("%d objects were placed but only %d reached a line" % (placed, counted))
    return {"rows": rows, "total": total_objects, "counted": counted, "excluded": excluded, "unclassified": unclassified,
            "errors": errors, "failures": failures, "sources": sources, "schedule": schedule,
            "unused": [r["match"] for r in spec["rules"] if id(r) not in used], "purchases": purchases, "unit": unit}


def varies(results):
    """What is the same and what differs between scopes. `results` maps a label to build()'s result."""
    tables = {}
    for label, res in results.items():
        table = {}
        for row in res["rows"][1:]:
            if len(row) == len(HEADER):
                table[(row[0], row[1], row[2], row[4], row[5])] = (row[3], row[6])
        tables[label] = table
    keys = sorted(set().union(*[set(t) for t in tables.values()]), key=str)
    labels = list(tables)
    same, different = 0, []
    for key in keys:
        values = [tables[label].get(key) for label in labels]
        if all(v == values[0] for v in values):
            same += 1
        else:
            different.append((key, values))
    return {"labels": labels, "same": same, "different": different}


def status(label, result, spec):
    sources = result["sources"]
    state = "FAILED: " + "; ".join(result["failures"]) + " - " if result["failures"] else ""
    return ("BOM: %s%s - %d objects: %d counted, %d excluded, %d unclassified - %d lines (%d measured, %d calculated, %d assumed)"
            " - not counted: %d items - covers: %s" % (state, label, result["total"], result["counted"], sum(result["excluded"].values()),
                                                       sum(result["unclassified"].values()), sum(sources.values()), sources["measured"],
                                                       sources["calculated"], sources["assumed"], len(spec.get("not_counted") or []), spec.get("covers")))


def write_csv(path, result, spec, stamp):
    rows = list(result["rows"])
    rows += [[], ["Reconciliation"], ["Objects in scope", result["total"]], ["Counted in lines", result["counted"]],
             ["Excluded", sum(result["excluded"].values())], ["Unclassified", sum(result["unclassified"].values())],
             [], ["Covers", spec["covers"]], ["Model state", stamp]]
    if result["excluded"]:
        rows += [[], ["Excluded", "Count", "Reason"]] + [[name, count, reason] for (name, reason), count in sorted(result["excluded"].items())]
    rows += [[], ["Not counted", "Reason"]] + [[e["item"], e["reason"]] for e in spec.get("not_counted") or []]
    if result["schedule"]:
        rows += [[], ["Cut schedule", "Exact lengths behind each line that gives a range"], ["Item", "Size", "Cut length", "Qty"]] + result["schedule"]
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        csv.writer(handle).writerows(rows)


def print_report(results, spec):
    for label, res in results.items():
        for (name, layer), count in sorted(res["unclassified"].items())[:40]:
            print("  unclassified: %d x %s on %s" % (count, name, layer))
        if len(res["unclassified"]) > 40:
            print("  unclassified: ... and %d more names" % (len(res["unclassified"]) - 40))
        for err in res["errors"][:40]:
            print("  not measured: " + err)
        for match in res["unused"]:
            print("  note: rule matched nothing in %s: %s" % (label, match))
        print(status(label, res, spec))
    if len(results) > 1:
        diff = varies(results)
        print("Same in every scope: %d lines. Different: %d." % (diff["same"], len(diff["different"])))
        for key, values in diff["different"][:60]:
            print("  %s | %s: %s" % (key[1], key[2], " / ".join("%s=%s" % (l, (v[0] if v else "-")) for l, v in zip(diff["labels"], values))))


# ---- Rhino document reader ----

def read_scope(doc, scope):
    """Every live object under a layer path, hidden and locked included."""
    import Rhino
    import Rhino.Geometry as G

    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.HiddenObjects = True
    settings.LockedObjects = True
    out = []
    for item in doc.Objects.GetObjectList(settings):
        layer = doc.Layers[item.Attributes.LayerIndex]
        full = None if layer.IsDeleted else layer.FullPath
        if not full or not (full == scope or full.startswith(scope + "::")):
            continue
        box = item.Geometry.GetBoundingBox(True)

        def volume(geometry=item.Geometry):
            props = G.VolumeMassProperties.Compute(geometry)
            return props.Volume if props is not None else None

        def area(geometry=item.Geometry):
            props = G.AreaMassProperties.Compute(geometry)
            return props.Area if props is not None else None

        out.append({"name": item.Attributes.Name or "", "layer": full[len(scope) + 2:],
                    "dims": sorted([box.Max.X - box.Min.X, box.Max.Y - box.Min.Y, box.Max.Z - box.Min.Z]),
                    "volume": volume, "area": area})
    return out


def siblings_without_bom(doc, scopes):
    """Layers beside each scope that this run did not cover: said in the report."""
    wanted = set(s["layer"] for s in scopes)
    parents = set(s["layer"].rsplit("::", 1)[0] for s in scopes if "::" in s["layer"])
    missing = set()
    for layer in doc.Layers:
        full = None if layer.IsDeleted else layer.FullPath
        if full and "::" in full and full.rsplit("::", 1)[0] in parents and full not in wanted:
            missing.add(full)
    return sorted(missing)


def run(doc, spec, write):
    problems = validate(spec, need_out=write)
    if problems:
        for problem in problems:
            print("  spec: " + problem)
        print("BOM: FAILED: the specification is incomplete")
        print("ASBOM status=fail reason=spec")
        return 1
    unit = UNITS.get(str(doc.ModelUnitSystem), str(doc.ModelUnitSystem))
    results, failed = {}, False
    for scope in spec["scopes"]:
        objects = read_scope(doc, scope["layer"])
        if not objects:
            print("  no objects under %s: check the layer path" % scope["layer"])
            failed = True
            continue
        results[scope.get("label") or scope["layer"]] = build(objects, spec, unit)
    print_report(results, spec)
    failed = failed or any(r["failures"] for r in results.values())
    for name in siblings_without_bom(doc, spec["scopes"]):
        print("  no BOM for: " + name)
    for entry in spec.get("not_counted") or []:
        print("  not counted: %s (%s)" % (entry["item"], entry["reason"]))
    if failed:
        print("ASBOM status=fail files=0")
        return 1
    if write:
        os.makedirs(spec["out"], exist_ok=True)
        stamp = "%d objects in the document at %s" % (len(list(doc.Objects)), time.strftime("%Y-%m-%d %H:%M"))
        written = []
        for scope in spec["scopes"]:
            label = scope.get("label") or scope["layer"]
            path = os.path.join(spec["out"], "bom-%s.csv" % re.sub(r"[^A-Za-z0-9._-]+", "-", label).strip("-"))
            write_csv(path, results[label], spec, stamp)
            written.append(path)
        for path in written:
            print("  wrote " + path)
    print("ASBOM status=pass files=%d" % (len(results) if write else 0))
    return 0


def main():
    doc = globals()["__rhino_doc__"]
    mode = globals().get("AS_MODE", "run")
    spec = globals().get("AS_BOM") or {}
    if mode == "names":
        for scope in spec.get("scopes") or []:
            counts = {}
            for obj in read_scope(doc, scope["layer"]):
                key = (obj["layer"], obj["name"] or "(no name)")
                counts[key] = counts.get(key, 0) + 1
            print("%s: %d objects" % (scope["layer"], sum(counts.values())))
            for (layer, name), count in sorted(counts.items()):
                print("  %5d  %s | %s" % (count, layer, name))
        return
    run(doc, spec, write=mode == "run")


if "__rhino_doc__" in globals():
    main()
