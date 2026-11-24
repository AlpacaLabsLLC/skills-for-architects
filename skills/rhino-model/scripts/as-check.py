#! python3
"""Requirements check (Arch Studio, rhino v7).

Requirements are what a model is checked against: a JSON document string stored in the
.3dm under `as:requirements`, in as-check-model.py's format, with extra keys:
  sources   {"<check name>": "<source>"}  e.g. {"heights Seat": "default: 15-16 in"}
  stated    ["<requirement that is not measured>", ...]
  brief     the brief the requirements were written from, in the user's words
  change    why this revision exists ("first revision", "brief changed: ...", "user correction: ...")
  revision  set by write mode: 1, 2, ...; earlier revisions are kept, newest last, in
            `as:requirements-history`
  intended  declared connections that the clash check excuses, each {"a": glob, "b": glob, "why": ...}
  code      {"jurisdiction": ..., "used": ..., "status": "adopted" | "stand-in" | "none"}: which code the
            values come from, and whether it is the local one. A stand-in is flagged in every report
  after_geometry  set by write mode when requirements change once geometry exists (see flags below)

Modes (AS_MODE: caller's globals, else the process environment):
  check (default)  run as-check-model.py plus baseline checks, print each check
                   (measured, required, source), failures first, then what was and was
                   not checked and any flags; store the result in
                   `as:requirements-check`; end with
                   ASCHECK status=<pass|fail|unchecked> checks=a/b stated=n fp=<fingerprint> rev=<n>
                   The stored result also holds `rev` (the requirements revision checked) and `geom_fp`
                   (geometry_fp: ids, layers and boxes, recomputable from the saved file)
                   A check with nothing to measure prints NOT MEASURED and counts as unmet
  list             print the requirements as a table, without measuring
  write            store AS_REQUIREMENTS (a dict or JSON string from the caller's globals) as
                   the next revision, archive the previous one, print what changed and
                   ASREQUIREMENTS saved rev=<n> checks=<count>; the last check becomes stale
  history          print every revision: number, change, brief, check count

Runs by file path from Rhino's run_python tool (uses __rhino_doc__; falls back to
RhinoDoc.ActiveDoc). RhinoCommon and the standard library only.
"""
import contextlib
import io
import json
import os
import re
import tempfile
import time

import Rhino

KEY = "as:requirements"
RESULT_KEY = "as:requirements-check"
HISTORY_KEY = "as:requirements-history"
HISTORY_MAX = 30
META = ("sources", "stated", "brief", "change", "revision", "time", "intended", "code", "after_geometry")
# What a check name measures, for the report's "checked" line.
KINDS = (("dimensions and positions", ("extent", "object", "bbox", "heights", "points", "centroids", "props", "on_surface", "units")),
         ("counts", ("layer", "grid", "spacing", "bond", "parent")),
         ("clearances", ("clear", "inside")),
         ("clashes", ("clash",)), ("connectivity", ("network",)), ("connections", ("hardware", "bears")),
         ("proportions and coverage", ("proportion", "cover")),
         ("set-out shares and sizes", ("within",)),
         ("geometry and names", ("named", "valid", "closed", "subd", "baseline")),
         ("Grasshopper", ("slider_response", "gh")))
USER_DRIVEN = ("user correction", "brief changed")
HERE = os.path.dirname(os.path.abspath(globals().get("AS_SCRIPT_FILE") or globals().get("__file__") or "."))
CHECKER = os.path.join(HERE, "as-check-model.py")

d = globals().get("__rhino_doc__") or Rhino.RhinoDoc.ActiveDoc


def fingerprint(doc):
    """Changes whenever an object is added, replaced or deleted."""
    serials = [o.RuntimeSerialNumber for o in doc.Objects]
    return "%d-%d" % (len(serials), max(serials) if serials else 0)


def geometry_rows(doc):
    """(object id, layer path, bounding box) of every object, as geometry_fp reads them."""
    rows = []
    for o in doc.Objects:
        b = o.Geometry.GetBoundingBox(True)
        rows.append((str(o.Id), doc.Layers[o.Attributes.LayerIndex].FullPath, (b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z)))
    return rows


def geometry_fp(rows):
    """A fingerprint of the geometry that survives saving: object ids, layers and bounding boxes to 0.001.
    Notes are left out, so answering a note after the check does not make it stale. rhino-agent-team
    recomputes the same value from the saved file to tell whether the file changed after its check ran."""
    import hashlib
    keep = sorted("%s|%s|%s" % (i.lower(), layer, ",".join("%.3f" % (round(v, 3) + 0.0) for v in bb))
                  for i, layer, bb in rows if layer != "Notes" and not layer.startswith("Notes::"))
    return "g1-" + hashlib.sha256("\n".join(keep).encode("utf-8")).hexdigest()[:16]


def objs_under(doc, parent):
    out = []
    for o in doc.Objects:
        lp = doc.Layers[o.Attributes.LayerIndex].FullPath
        if lp == parent or lp.startswith(parent + "::"):
            out.append(o)
    return out


def baseline(doc, req):
    """Checks every model gets, whatever its requirements say."""
    res = []
    add = lambda n, ok, act: res.append({"check": "baseline " + n, "pass": bool(ok), "actual": act})
    parent = req.get("parent", "")
    objs = objs_under(doc, parent) if parent else []
    add("objects", len(objs) > 0, {"count": len(objs)})
    unnamed = [str(o.Id)[:8] for o in objs if not (o.Attributes.Name or "").strip()]
    add("named", not unnamed, {"unnamed": len(unnamed)})
    try:
        import Grasshopper
        from Grasshopper.Kernel import GH_RuntimeMessageLevel, IGH_ActiveObject
        errs = []
        for gdoc in Grasshopper.Instances.DocumentServer:
            errs += [o.Name for o in gdoc.Objects if isinstance(o, IGH_ActiveObject)
                     and o.RuntimeMessageLevel == GH_RuntimeMessageLevel.Error]
        add("grasshopper errors", not errs, {"errors": errs})
    except Exception:
        pass  # Grasshopper not loaded: nothing to check
    return res


FIXED = {"baseline objects": "at least 1 object under the parent",
         "baseline named": "every object named",
         "baseline grasshopper errors": "no Grasshopper component in error",
         "named": "every object named", "valid": "valid geometry",
         "parent": "parent layer exists"}


def requirement(name, e):
    """A requirement in words, from its check name and spec."""
    if e is None:
        if name.startswith("closed"):
            return "every object a closed solid"
        return FIXED.get(name, "")
    if not isinstance(e, dict):
        return str(e)
    if name.startswith("heights"):
        return "top at z %s +/- %s" % (", ".join(str(p[2]) for p in e.get("at", [])), e.get("tol", 0.05))
    if name.startswith("layer"):
        return "%s-%s objects%s%s" % (e.get("min"), e.get("max"), (" of type " + e["type"]) if e.get("type") else "",
                                      (" (" + e["derived"] + ")") if e.get("derived") else "")
    if name.startswith("clash"):
        return "no overlap with %s" % (", ".join(text_of(a) for a in e["against"]) if e.get("against") else "anything else under the parent")
    if name.startswith("network"):
        return "every %s reaches %s through %s" % (text_of(e.get("fixtures")), text_of(e.get("to")), text_of(e.get("pipes", "its pipes")))
    if name.startswith("hardware"):
        if e.get("placeholder"):
            return "named as a placeholder; no connection checked"
        past = e.get("past")
        return "touches %s%s (plausibility only)" % (", ".join(text_of(j) for j in e.get("joins", [])),
                                                     "; extends %s past %s" % (past["by"], text_of(past["of"])) if past else "")
    if name.startswith("within"):
        parts = []
        if e.get("boxes"):
            parts.append("inside %d share box(es)" % len(e["boxes"]))
        if e.get("avoid"):
            parts.append("out of %d other share box(es)" % len(e["avoid"]))
        if e.get("min_section") is not None:
            parts.append("no side under %s" % e["min_section"])
        return "; ".join(parts) or "nothing to check"
    if name.startswith("proportion"):
        return "size along %s over the smaller other size in %s to %s" % (e.get("axis", "z"), e["ratio"][0], e["ratio"][1])
    if name.startswith("cover"):
        return "%s covers the face across %s from %s to %s, except %d opening(s)" % (text_of(e.get("items", "it")), e.get("axis", "y"), e["region"][0], e["region"][1], len(e.get("holes", [])))
    if name.startswith("bears"):
        return "vertical members rest on %s across their footprint" % (", ".join(text_of(x) for x in e["on"]) if e.get("on") else "material below")
    if name.startswith("extent"):
        rng = lambda r: ("%s to %s" % tuple(r) if r[0] is not None and r[1] is not None
                         else (">= %s" % r[0] if r[0] is not None else "<= %s" % r[1]))
        return ", ".join("%s %s" % (k, rng((list(v) + [None, None])[:2])) for k, v in e.items()
                         if k[:4] in ("min_", "max_", "mid_") or k.startswith("size_"))
    if name.startswith("object") or name == "bbox":
        return "size %s +/- %s" % (" x ".join(str(v) for v in e.get("size", [])), e.get("tol"))
    keys = [k for k in e if k not in ("match", "exclude", "layer", "name")]
    return ", ".join("%s %s" % (k, e[k]) for k in keys)[:120]


def listed(req):
    """(check name, requirement text) for each requirement, without measuring."""
    rows = []
    if "units" in req:
        rows.append(("units", req["units"]))
    rows.append(("parent", "layer '%s' exists" % req.get("parent", "?")))
    for child, spec in req.get("layers", {}).items():
        rows.append(("layer " + child, requirement("layer", spec)))
    if "bbox" in req:
        rows.append(("bbox", requirement("bbox", req["bbox"])))
    if req.get("named"):
        rows.append(("named", FIXED["named"]))
    for child in req.get("closed", []):
        rows.append(("closed " + child, requirement("closed", None)))
    for key, spec in req.get("objects", {}).items():
        rows.append(("object " + key, requirement("object", spec)))
    for child, spec in req.get("heights", {}).items():
        rows.append(("heights " + child, requirement("heights", spec)))
    for child, spec in req.get("extent", {}).items():
        rows.append(("extent " + child, requirement("extent", spec)))
    skip = {"case", "level", "units", "parent", "layers", "bbox", "named", "closed", "objects",
            "heights", "extent", "valid"} | set(META)
    for key, val in req.items():
        if key in skip:
            continue
        if isinstance(val, dict):
            for child, spec in val.items():
                rows.append(("%s %s" % (key, child), requirement(key, spec)))
        else:
            rows.append((key, json.dumps(val)[:120]))
    return rows


def actual(r):
    a = r.get("actual")
    off = a.get("out_of_range") if isinstance(a, dict) else None
    if isinstance(a, dict) and "measured" in a:
        a = a["measured"]
    if isinstance(a, dict):
        a = {k: v for k, v in a.items() if k != "detail"}
    s = json.dumps(a)
    s = s if len(s) <= 120 else s[:117] + "..."
    return s + (" (out of range: %s)" % ", ".join(off) if off else "")


def document_state(doc):
    """What the open document itself shows. A copy written by save_doc leaves it untitled, so this
    cannot say a copy was written; never report an untitled document as if nothing had been saved."""
    if not doc.Path:
        return "untitled"
    return "unsaved changes to %s" % os.path.basename(doc.Path) if doc.Modified else "saved to %s" % os.path.basename(doc.Path)


def kind_of(name):
    first = name.split(" ")[0]
    for kind, keys in KINDS:
        if first in keys:
            return kind
    return "other"


def covered(res):
    """Counts of checks run, by what they measure."""
    counts = {}
    for r in res:
        if r.get("not_measured"):
            continue
        k = kind_of(r["check"])
        counts[k] = counts.get(k, 0) + 1
    return ["%d %s" % (counts[k], k) for k, _ in KINDS + (("other", ()),) if k in counts]


def not_checked(req):
    """What this report does not establish, from what the requirements did not ask for."""
    out = [label for key, label in (("clash", "clashes"), ("network", "connectivity"), ("hardware", "connections")) if not req.get(key)]
    return out + ["structure", "code compliance"]


def wide_counts(req):
    """Layer count ranges too loose to mean much. A range from the layout is tight."""
    out = []
    for child, spec in req.get("layers", {}).items():
        lo, hi = spec.get("min"), spec.get("max")
        if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and hi - lo > max(2, 0.2 * hi):
            out.append("layer %s %s-%s" % (child, lo, hi))
    return out


def size_moved(before, after, share=0.01):
    """True when an overall size moved on any axis by more than `share` of its largest dimension."""
    return any(abs(a - b) > share * max(before) for a, b in zip(before, after))


def derived_drift(reference, sizes, req):
    """Counts with a `derived` note whose layer changed size since this revision was first measured.
    A prompt to work the count out again: it cannot see a change inside an unchanged extent, or why a
    constant was set."""
    out = []
    for child, was in reference.items():
        now = sizes.get(child)
        note = req.get("layers", {}).get(child, {}).get("derived")
        if now and note and size_moved(was, now):
            out.append({"layer": child, "was": was, "now": now, "derived": note})
    return out


def revision_flags(doc, req):
    """Revisions written once geometry existed, oldest first."""
    flags = []
    for r in load_history(doc) + [req]:
        late = r.get("after_geometry")
        if late:
            flags.append(dict(late, rev=r.get("revision", 1), change=r.get("change", "")))
    return flags


def code_flag(req):
    code = req.get("code") or {}
    if code.get("status") == "stand-in":
        return "%s is a stand-in: no local code for %s" % (code.get("used", "a foreign code"), code.get("jurisdiction", "this site"))
    if code.get("status") == "none":
        return "no code applied"
    return ""


def summary(passed, total, stated, doc, req, late, wide, empty=0, drift=0):
    """The one line the reply opens with, for the architect: score, what was not measured or checked, the
    code basis and the save state. Integrity flags for the agent go to notes(), not here."""
    parts = ["Requirements: %d/%d met" % (passed, total)]
    if empty:
        parts.append("%d with nothing to measure" % empty)
    if stated:
        parts.append("%d not measured" % len(stated))
    parts.append("not checked: " + ", ".join(not_checked(req)))
    if code_flag(req):
        parts.append(code_flag(req))
    parts.append(document_state(doc))
    return " \u00b7 ".join(parts)


def notes(late, wide, drift):
    """Integrity flags for the agent to act on and record in as:run-notes; never part of the reply's opening line."""
    parts = []
    if late:
        parts.append("%d revision%s written after geometry existed" % (len(late), "" if len(late) == 1 else "s"))
    if wide:
        parts.append("%d count range%s too wide" % (len(wide), "" if len(wide) == 1 else "s"))
    if drift:
        parts.append("%d derived count%s may be stale: recompute and write a revision, or confirm the count is unchanged" % (drift, "" if drift == 1 else "s"))
    return "Check notes (for as:run-notes, not the reply): " + "; ".join(parts) if parts else ""


def run_check(req):
    tmp = os.path.join(tempfile.gettempdir(), "as-requirements-%d.json" % os.getpid())
    with open(tmp, "w") as f:
        json.dump(req, f)
    g = {"__rhino_doc__": d, "CASE": tmp, "__name__": "check_model"}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(open(CHECKER).read(), CHECKER, "exec"), g)
        res = list(g.get("res", []))
    except Exception as e:
        res = list(g.get("res", [])) + [{"check": "checker", "pass": False, "actual": "%s: %s" % (type(e).__name__, e)}]
    finally:
        os.remove(tmp)
    return res + baseline(d, req), dict(g.get("derived_sizes") or {})


def text_of(s):
    return s if isinstance(s, str) else json.dumps(s)


def load_history(doc):
    try:
        h = json.loads(doc.Strings.GetValue(HISTORY_KEY) or "[]")
        return h if isinstance(h, list) else []
    except ValueError:
        return []


def write(doc, new):
    """Store `new` as the next revision; print the diff against the previous one."""
    if isinstance(new, str):
        new = json.loads(new)
    if not isinstance(new, dict) or not new.get("parent"):
        raise ValueError("requirements must be a JSON object with a 'parent' layer")
    if not str(new.get("brief", "")).strip():
        raise ValueError("requirements need a 'brief': the brief they were written from")
    raw = doc.Strings.GetValue(KEY)
    old = json.loads(raw) if raw else None
    rev = int(old.get("revision", 1)) + 1 if old else 1
    new = dict(new, revision=rev, time=time.time())
    new.setdefault("change", "first revision" if rev == 1 else "")
    if rev > 1 and not str(new["change"]).strip():
        raise ValueError("a new revision needs a 'change': why the requirements changed")
    rows = dict(listed(new))
    before = dict(listed(old)) if old else {}
    changed = [n for n in rows if n not in before or before[n] != rows[n]] + [n for n in before if n not in rows]
    try:
        last = json.loads(doc.Strings.GetValue(RESULT_KEY) or "{}")
    except ValueError:
        last = {}
    measured = bool(last.get("total") or last.get("measured_before"))
    objects = len(objs_under(doc, new["parent"]))
    new.pop("after_geometry", None)  # set only here, never carried from the caller or a prior revision
    if objects or measured:
        failing = [n for n in changed if n in last.get("failed", [])]
        if changed:
            new["after_geometry"] = {"objects": objects, "changed": changed, "failing": failing}
    sources = new.get("sources", {})
    unsourced = [n for n in rows if n not in sources and n != "parent"]
    if old:
        hist = load_history(doc) + [old]
        doc.Strings.SetString(HISTORY_KEY, json.dumps(hist[-HISTORY_MAX:]))
    doc.Strings.SetString(KEY, json.dumps(new))
    doc.Strings.SetString(RESULT_KEY, json.dumps({"status": "stale", "rev": rev, "time": time.time(),
                                                  "measured_before": measured, "failed": last.get("failed", [])}))
    print("Requirements rev %d for %s: %s" % (rev, new["parent"], new["change"]))
    if old:
        for n in rows:
            if n not in before:
                print("  added    %s  %s" % (n, rows[n]))
            elif before[n] != rows[n]:
                print("  changed  %s  %s -> %s" % (n, before[n], rows[n]))
        for n in before:
            if n not in rows:
                print("  removed  %s" % n)
        old_st, new_st = [text_of(x) for x in old.get("stated", [])], [text_of(x) for x in new.get("stated", [])]
        for x in new_st:
            if x not in old_st:
                print("  added    not measured: %s" % x)
        for x in old_st:
            if x not in new_st:
                print("  removed  not measured: %s" % x)
    if unsourced:
        print("  no source: %s (add one to 'sources', even \"default\" or \"brief\")" % ", ".join(unsourced))
    late = new.get("after_geometry")
    if late:
        print("  flag: written after geometry existed (%d objects); changed: %s%s. The report will say so. "
              "If this only makes a real failure pass, undo it; if the design changed, keep it and report it." % (
                  late["objects"], ", ".join(late["changed"])[:200], "; was failing: " + ", ".join(late["failing"])[:120] if late["failing"] else ""))
    for w in wide_counts(new):
        print("  flag: count range too wide to mean much: %s. Derive min and max from the layout (add 'derived')." % w)
    if code_flag(new):
        print("  flag: " + code_flag(new))
    cited = " ".join(text_of(v) for v in sources.values())
    if not new.get("code") and re.search(r"\b(ADA|IBC|IPC|IRC|NFPA|UNIT)\b", cited):
        print("  flag: sources cite a code but 'code' is not set: name the jurisdiction and whether this code is the local one.")
    for item in new.get("intended", []):
        print("  declared connection: %s to %s (%s)" % (text_of(item.get("a")), text_of(item.get("b")), item.get("why", "NO REASON: refused by the clash check")))
    print("ASREQUIREMENTS saved rev=%d checks=%d stated=%d" % (rev, len(rows), len(new.get("stated", []))))


def history(doc):
    raw = doc.Strings.GetValue(KEY)
    revs = load_history(doc) + ([json.loads(raw)] if raw else [])
    if not revs:
        print("No requirements in this document (%s)." % KEY)
        return
    for r in revs:
        print("rev %s  %s  checks=%d  %s" % (r.get("revision", 1), time.strftime("%Y-%m-%d %H:%M", time.localtime(r.get("time", 0))) if r.get("time") else "-",
                                          len(listed(r)), r.get("change", "")))
        if r.get("brief"):
            print("        brief: %s" % r["brief"][:200])


def main(mode):
    if mode == "write":
        write(d, globals().get("AS_REQUIREMENTS"))
        return
    if mode == "history":
        history(d)
        return
    fp = fingerprint(d)
    raw = d.Strings.GetValue(KEY)
    if not raw:
        print("No requirements in this document (%s). Ask the agent to write them from the brief." % KEY)
        if mode == "check":
            d.Strings.SetString(RESULT_KEY, json.dumps({"status": "unchecked", "fp": fp, "geom_fp": geometry_fp(geometry_rows(d)), "time": time.time()}))
            print("ASCHECK status=unchecked checks=0/0 stated=0 fp=%s rev=0" % fp)
        return
    req = json.loads(raw)
    src = req.get("sources", {})
    source = lambda n: src.get(n) or ("baseline" if n.startswith("baseline") else "")
    stated = req.get("stated", [])
    rev = req.get("revision", 1)
    head = "%s (%s) - requirements rev %s" % (req.get("parent", "?"), d.Name or "untitled", rev)

    if mode == "list":
        print("Requirements list: " + head)
        if req.get("brief"):
            print("  brief: %s" % req["brief"])
        for name, text in listed(req):
            s = source(name)
            print("  %s  %s%s" % (name, text, " | " + s if s else ""))
        for s in stated:
            print("  not measured: %s" % (s if isinstance(s, str) else json.dumps(s)))
        for item in req.get("intended", []):
            print("  declared connection: %s to %s (%s)" % (text_of(item.get("a")), text_of(item.get("b")), item.get("why", "")))
        if code_flag(req):
            print("  code: " + code_flag(req))
        print("  plus baseline: objects exist, every object named, no Grasshopper errors")
        return

    res, sizes = run_check(req)
    try:
        previous = json.loads(d.Strings.GetValue(RESULT_KEY) or "{}")
    except ValueError:
        previous = {}
    # Sizes are kept from the first check of a revision; write mode drops them, so a new revision starts clean.
    reference = dict(sizes, **(previous.get("derived_sizes") or {})) if previous.get("rev") == rev else sizes
    drift = derived_drift(reference, sizes, req)
    passed = sum(1 for r in res if r["pass"])
    status = "pass" if passed == len(res) else "fail"
    empty = [r["check"] for r in res if r.get("not_measured")]
    print("Requirements check: " + head)
    for r in sorted(res, key=lambda r: r["pass"]):  # failures first
        text, s = requirement(r["check"], r.get("expected")), source(r["check"])
        print("  %s  %s  measured %s%s%s" % ("PASS" if r["pass"] else "NOT MEASURED" if r.get("not_measured") else "FAIL", r["check"], actual(r),
                                         " | required " + text if text else "", " | " + s if s else ""))
        for line in (r.get("actual") or {}).get("detail", []) if isinstance(r.get("actual"), dict) else []:
            print("        %s" % line)
    for s in stated:
        print("  ----  not measured: %s" % (s if isinstance(s, str) else json.dumps(s)))
    late = revision_flags(d, req)
    wide = wide_counts(req)
    print("  Checked: " + ", ".join(covered(res)))
    print("  Not checked: " + ", ".join(not_checked(req)) + ". A passing score means only that the checks listed here passed.")
    for f in late:
        print("  flag: rev %s written after geometry existed (%d objects); changed: %s%s. Reason given: %s" % (
            f["rev"], f["objects"], ", ".join(f["changed"])[:200], "; was failing: " + ", ".join(f["failing"])[:120] if f["failing"] else "", f["change"]))
    for w in wide:
        print("  flag: count range too wide to mean much: " + w)
    for f in drift:
        print("  flag: layer %s changed size since rev %s was first measured (%s to %s), and its count is derived (%s). If a count or spacing would change, write a new revision; never set a constant to keep the old count." % (
            f["layer"], rev, " x ".join(str(v) for v in f["was"]), " x ".join(str(v) for v in f["now"]), f["derived"]))
    if code_flag(req):
        print("  flag: " + code_flag(req))
    # Reader-facing counts leave out revisions the user asked for, unless a failing check was changed.
    raised = [f for f in late if f["failing"] or not str(f["change"]).lower().startswith(USER_DRIVEN)]
    print(summary(passed, len(res), stated, d, req, raised, wide, len(empty), len(drift)))
    if notes(raised, wide, len(drift)):
        print(notes(raised, wide, len(drift)))
    d.Strings.SetString(RESULT_KEY, json.dumps({
        "status": status, "passed": passed, "total": len(res), "stated": len(stated), "fp": fp, "geom_fp": geometry_fp(geometry_rows(d)),
        "rev": rev, "time": time.time(), "failed": [r["check"] for r in res if not r["pass"]], "not_measured": empty,
        "derived_sizes": reference}))
    print("ASCHECK status=%s checks=%d/%d stated=%d fp=%s rev=%s" % (status, passed, len(res), len(stated), fp, rev))


def mode():
    """AS_MODE from the caller's globals, else the live process environment. A value set
    through .NET is invisible to Python's os.environ (read once when Rhino's Python
    starts), so read it through System.Environment first."""
    if globals().get("AS_MODE"):
        return globals()["AS_MODE"]
    try:
        import System
        value = System.Environment.GetEnvironmentVariable("AS_MODE")
        if value:
            return value
    except Exception:
        pass
    return os.environ.get("AS_MODE", "check")


main(mode())
