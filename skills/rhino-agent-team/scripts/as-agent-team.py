#! python3
"""Helpers and the team check for several agents on one Rhino model (Arch Studio, as-rhino-agent-team).

Every agent works in its own .3dm file in one shared folder. setout.3dm, written by the coordinator before anyone
builds, holds the revision, the owners, the datum and levels, each owner's share of shared space, the required
points and the minimum sizes. Other agents' work is read from their files as last saved, never edited. Inside one
file, rhino-model's requirements check is the check; this one measures across files. Conventions: references/protocol.md.

Runs by file path through run_python (uses __rhino_doc__, the agent's own open document):

    P = "<absolute path of this skill's folder>/scripts/as-agent-team.py"
    ns = {"__rhino_doc__": __rhino_doc__, "AS_SCRIPT_FILE": P, "AS_TEAM": {"folder": "<shared folder>", "me": "Plumbing", "round": 3}}
    exec(compile(open(P).read(), P, "exec"), ns)
    print(ns["summary"]())

AS_TEAM  folder  the shared folder; required
           me      this agent's owner name as listed in the set-out, or "coordinator"
           round   the round number the user gave
AS_MODE    unset   define the helpers only
           "check" read every file in the folder and print the team check; with AS_TEAM "write": true the
                   coordinator also writes reports/round-<n>.json in the folder

The check reads the saved files with Rhino.FileIO.File3dm and changes none of them. Rhino is imported only where
needed, so the check's logic (analyse) also runs without Rhino on plain records.
"""
import json
import os
import uuid

SETOUT = "setout.3dm"
STAMP = "setout_revision"
OWN_CHECK = "as:requirements-check"
OWN_REQ = "as:requirements"
NOW_FP = "__geom_fp_now__"          # set by read_file: geometry_fp of the file as saved
PLUGIN_KEY = "as:team-plugin"        # plugin version that last wrote this file's team stamps
HELPER_KEY = "as:team-helper"        # this helper's own fingerprint, same file


def plugin_version(script=None):
    """The installed plugin's version, read from .claude-plugin/plugin.json three folders above this script."""
    script = script or globals().get("AS_SCRIPT_FILE") or ""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(script)))))
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json")) as handle:
            return str(json.load(handle).get("version") or "unknown")
    except (OSError, ValueError):
        return "unknown"


def helper_version(script=None):
    """A fingerprint of the helpers a team relies on: this file and rhino-model's requirements check
    (`as-check.py`, `as-check-model.py`), so a locally edited copy of any of them shows as a mismatch even on
    the same plugin version. A helper that is missing counts in the fingerprint as missing."""
    import hashlib
    script = os.path.abspath(script or globals().get("AS_SCRIPT_FILE") or "")
    skills = os.path.dirname(os.path.dirname(os.path.dirname(script)))
    files = [script] + [os.path.join(skills, "rhino-model", "scripts", n) for n in ("as-check.py", "as-check-model.py")]
    digest = hashlib.sha256()
    for path in files:
        try:
            with open(path, "rb") as handle:
                digest.update(hashlib.sha256(handle.read()).digest())
        except OSError:
            if path == script:
                return "unknown"
            digest.update(b"missing:" + os.path.basename(path).encode("utf-8"))
    return "h2-" + digest.hexdigest()[:12]


def version_mismatches(strings, owner_files):
    """Owner files whose plugin or helper stamp differs from the set-out's, the coordinator's install (no Rhino)."""
    want = (strings.get(SETOUT, {}).get(PLUGIN_KEY), strings.get(SETOUT, {}).get(HELPER_KEY))
    out = []
    if not want[0] or not want[1]:
        return [{"file": SETOUT, "plugin": want[0], "helper": want[1], "reason": "the set-out has no version stamp"}]
    for f in sorted(owner_files):
        got = (strings.get(f, {}).get(PLUGIN_KEY), strings.get(f, {}).get(HELPER_KEY))
        if got != want:
            out.append({"file": f, "plugin": got[0], "helper": got[1], "coordinator_plugin": want[0], "coordinator_helper": want[1],
                        "reason": "no version stamp" if not all(got) else "different plugin or helper version from the coordinator's"})
    return out
NOTES = "Notes"
REQUESTS = "Interface::Penetrations"
KINDS = ("issue", "request", "change", "reply", "ruling")
# issue    a problem found in or with someone's objects, addressed to the owner of the object that must change
# request  an open design value or a need only the coordinator (or, through it, the user) can answer
# change   a change order, addressed to the coordinator, who reissues the set-out
# reply    an answer to any of the above; ruling: the coordinator's decision (who moves, or a set-out change)
OPEN_KINDS = ("issue", "request", "change", "ruling")
STATUSES = ("open", "answered", "closed")


class TeamError(Exception):
    """The protocol was not followed or the folder is incomplete."""


# ------------------------------------------------------------------ boxes (no Rhino)
def overlap(a, b, tol=0.1):
    """The shared box of two boxes [x0, y0, z0, x1, y1, z1] when they overlap by more than tol on every axis, else None.
    Touching is not overlap."""
    r = (max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3]), min(a[4], b[4]), min(a[5], b[5]))
    return r if (r[3] - r[0] > tol and r[4] - r[1] > tol and r[5] - r[2] > tol) else None


def inside(r, b, pad=0.5):
    return all(r[i] >= b[i] - pad for i in range(3)) and all(r[i] <= b[i] + pad for i in range(3, 6))


def near(a, b, pad):
    return all(a[i] - pad <= b[i + 3] and b[i] - pad <= a[i + 3] for i in range(3))


def brief(r):
    return {"file": r["file"], "layer": r["layer"], "name": r["name"], "id": r["id"], "box": [round(v, 2) for v in r["bb"]]}


def geometry_fp(rows):
    """Same value as rhino-model's as-check.py geometry_fp: object ids, layers and bounding boxes to 0.001,
    Notes left out. Recomputed from the saved file and compared with the one stored at check time."""
    import hashlib
    keep = sorted("%s|%s|%s" % (i.lower(), layer, ",".join("%.3f" % (round(v, 3) + 0.0) for v in bb))
                  for i, layer, bb in rows if layer != "Notes" and not layer.startswith("Notes::"))
    return "g1-" + hashlib.sha256("\n".join(keep).encode("utf-8")).hexdigest()[:16]


FAULT_KINDS = ("clash", "through_shell", "unserved", "undersize", "reservation", "note")
# The issue kinds a review note may carry, one per list in the team check: clashes, unopened_crossings,
# unserved_points, own_check_failures (undersized runs), share_breaks, notes_for_coordinator.


def _box_of(r):
    return tuple(r.get("bb") or r.get("box"))


def levels_from(host_records):
    """The set-out's levels read off the host's floors (no Rhino): one level per floor or slab, at the top of that
    solid, named by the object's name without its ' slab' / ' subfloor' / ' floor' suffix. Ceilings and joist
    undersides are not levels; put them in `numbers`."""
    out = {}
    for r in host_records:
        layer, name = r.get("layer", ""), (r.get("name") or "").strip()
        if not (layer.endswith("::Floors") or "::Floors::" in layer) or not name:
            continue
        label = name
        for suffix in (" slab", " subfloor", " floor"):
            if label.lower().endswith(suffix):
                label = label[: -len(suffix)]
        out[label] = round(_box_of(r)[5], 3)
    return [{"name": n, "z": z} for n, z in sorted(out.items(), key=lambda kv: kv[1])]


def normalize_levels(levels):
    """Levels as a list of {"name", "z"}, sorted by z. Accepts the same as a dict {name: z}."""
    if isinstance(levels, dict):
        levels = [{"name": n, "z": z} for n, z in levels.items()]
    out = []
    for item in levels or []:
        if not isinstance(item, dict) or not str(item.get("name") or "").strip() or item.get("z") is None:
            raise TeamError("each level needs a name and a z: %r" % (item,))
        out.append({"name": str(item["name"]).strip(), "z": float(item["z"])})
    return sorted(out, key=lambda l: l["z"])


def setout_check(setout_data, host_records=None, tol=0.5, requests=None):
    """What is wrong with a set-out before it is issued (no Rhino): {"problems": [...], "warnings": [...]}.
    Problems: levels that do not sit on a host floor, host floors with no level, shares inside a host solid
    (outside the host's openings), overlapping shares of two owners. A share marked `crossing` (share(..., crossing=True))
    may pass through a host solid, but only inside a host opening or an opening request of its own owner (`requests`:
    records with `box` and user `from`), so an owner whose run must cross a host wall can keep that piece in a share. Warnings: a share far larger than its
    owner's largest minimum run size in both of its smaller dimensions."""
    problems, warnings = [], []
    try:
        levels = normalize_levels(setout_data.get("levels"))
    except TeamError as exc:
        levels = []
        problems.append(str(exc))
    if not levels:
        problems.append("the set-out has no levels: use levels_from(<the host's objects>)")
    shares = setout_data.get("shares") or []
    if host_records:
        floors = levels_from(host_records)
        for l in levels:
            if not any(abs(l["z"] - f["z"]) <= tol for f in floors):
                problems.append("level %s at z %s is not on a floor of the host (ceilings belong in numbers, not levels)" % (l["name"], l["z"]))
        for f in floors:
            if not any(abs(l["z"] - f["z"]) <= tol for l in levels):
                problems.append("host floor %s at z %s has no level" % (f["name"], f["z"]))
        solids = [r for r in host_records if "::Openings" not in r.get("layer", "") and r.get("kind", "solid") in ("solid", "open")]
        openings = [r for r in host_records if "::Openings" in r.get("layer", "")]
        for s in shares:
            allowed = [_box_of(o) for o in openings]
            if s.get("crossing"):
                allowed += [_box_of(q) for q in (requests or []) if (q.get("user") or {}).get("from", "").lower() == str(s.get("owner", "")).lower()]
            for h in solids:
                reg = overlap(s["box"], _box_of(h))
                if reg is not None and not any(inside(reg, b) for b in allowed):
                    if s.get("crossing"):
                        problems.append("crossing share %s (%s) runs into host solid %s where no opening exists or is requested by %s"
                                        % (s.get("zone"), s.get("owner"), h.get("name"), s.get("owner")))
                    else:
                        problems.append("share %s (%s) runs into host solid %s; keep shares clear of the host's solids outside its openings, "
                                        "or draw the crossing as its own share with crossing=True where an opening exists or is requested"
                                        % (s.get("zone"), s.get("owner"), h.get("name")))
                    break
    # Every space more than one owner needs (a shaft, a gap in a wall) is declared with the owners that pass
    # through it, and each of them gets a share inside it.
    spaces = setout_data.get("shared_spaces") or []
    owner_names = set(o["name"] for o in setout_data.get("owners", []))
    if shares and not spaces:
        problems.append("the set-out declares no shared_spaces: list every space more than one owner needs (shafts, gaps in walls), "
                        "with its box and every owner whose runs pass through it")
    for space in spaces:
        for owner in space.get("owners", []):
            if owner not in owner_names:
                problems.append("%s: %s is not an owner in the set-out" % (space.get("name"), owner))
            elif not any(s["owner"] == owner and overlap(s["box"], space["box"]) is not None for s in shares):
                problems.append("%s: no share for %s; give every owner that passes through it a share before issuing" % (space.get("name"), owner))
    for i, a in enumerate(shares):
        for b in shares[i + 1:]:
            if a["owner"] != b["owner"] and overlap(a["box"], b["box"]) is not None:
                problems.append("shares overlap: %s (%s) and %s (%s)" % (a.get("zone"), a["owner"], b.get("zone"), b["owner"]))
    sizes = setout_data.get("min_sizes") or {}
    for s in shares:
        need = [max(v) if isinstance(v, (list, tuple)) else float(v) for k, v in sizes.items() if k.split("::")[0] == s["owner"]]
        if need:
            dims = sorted(s["box"][i + 3] - s["box"][i] for i in range(3))
            if dims[0] > 4 * max(need) and dims[1] > 4 * max(need):
                warnings.append("share %s (%s) is %.0f x %.0f in across, over four times %s's largest run (%.0f in): size it to the runs it holds"
                                % (s.get("zone"), s["owner"], dims[0], dims[1], s["owner"], max(need)))
    return {"problems": problems, "warnings": warnings}


def owner_digest(setout_data, owner):
    """What an owner builds to in a set-out revision (no Rhino): its own shares, its own required points, and the
    levels and datum everyone shares. Equal digests in two revisions mean nothing of that owner's moved."""
    import hashlib
    rnd = lambda v: [round(float(x), 3) for x in v]
    own = {"shares": sorted([s.get("zone") or "", rnd(s["box"]), bool(s.get("crossing"))] for s in setout_data.get("shares", []) if s.get("owner") == owner),
           "points": sorted([p.get("name") or "", p.get("system") or "", p.get("role") or "", rnd(p["at"])] for p in setout_data.get("points", []) if p.get("owner") == owner),
           "levels": setout_data.get("levels"), "datum": setout_data.get("datum")}
    return hashlib.sha256(json.dumps(own, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]


def current_since(setout_data, owner):
    """The oldest revision from which this owner's shares, points, levels and datum are unchanged up to now (no Rhino).
    A file or opening request stamped at that revision or later is current: a reissue that did not touch the owner
    carries its work forward. Needs the per-owner digests issue() records; without them, the current revision."""
    rev = int(setout_data["revision"])
    past = setout_data.get("owner_digests") or {}
    now, since = owner_digest(setout_data, owner), rev
    for r in range(rev - 1, 0, -1):
        if (past.get(str(r)) or {}).get(owner) != now:
            break
        since = r
    return since


def _stamp_int(v):
    try:
        return int(str(v))
    except (TypeError, ValueError):
        return None


def setout_problems(setout_data, host_records=None, requests=None):
    """What stops a set-out from being issued: setout_check()'s problems (no Rhino). The team check, issue() and
    the coordinator's summary() and preflight() all run it, so a set-out redrawn mid-run cannot leave overlapping
    shares, an owner without a share in a space it passes through, or levels off the host's floors."""
    return setout_check(setout_data, host_records, requests=requests)["problems"]


def stamp_status(stamped, current):
    """'current', or 'stale' with both revisions, for a file's stamp against the set-out (no Rhino)."""
    if stamped is None or str(stamped) == "":
        return "not stamped (set-out is at revision %s)" % current
    if str(stamped) == str(current):
        return "current"
    return "stale: stamped revision %s, set-out is at revision %s; read its change, rebuild what moved, check, stamp again" % (stamped, current)


def own_check_state(file_strings):
    """'pass', or why this owner's own rhino-model check does not count: missing, failed, run on an older
    requirements revision, or the file changed after the check ran."""
    def load(key):
        try:
            return json.loads(file_strings.get(key) or "{}")
        except ValueError:
            return None
    result, req = load(OWN_CHECK), load(OWN_REQ)
    if result is None or req is None:
        return "unreadable"
    if not result:
        return "missing"
    if result.get("status") != "pass":
        return result.get("status") or "missing"
    if str(result.get("rev")) != str(req.get("revision", 1)):
        return "checked requirements rev %s, current rev %s" % (result.get("rev"), req.get("revision", 1))
    if not result.get("geom_fp"):
        return "no fingerprint stored with the check"
    if result.get("geom_fp") != file_strings.get(NOW_FP):
        return "file changed after its check ran"
    return "pass"


# ------------------------------------------------------------------ the check (no Rhino)
def analyse(setout, records, strings, penetrates=None, limit=40, round_no=None, host_geometry=None):
    """setout: {'revision', 'owners' [{name, file}], 'host' (optional owner whose elements others pass through),
    'points' [{owner, system, role, name, at}], 'shares' [{owner, zone, box}]}.
    records: every object of every owner file: {file, layer, root, name, id, user, bb, kind ('solid', 'open', 'dot', 'other'), text}.
    strings: {file: {document strings}}: its setout_revision stamp and rhino-model's as:requirements-check result.
    Inside-one-file checks (names, closed solids, duplicates, sizes) are rhino-model's and are not repeated here.
    penetrates(a, b): True when two solids share volume; default: their boxes overlap (Rhino refines it).
    round_no: the current round; a note open with no reply more than one round after it was written is
    flagged to the coordinator. Without it, nothing is flagged."""
    penetrates = penetrates or (lambda a, b: True)
    rev = str(setout["revision"])
    owners = [o["name"] for o in setout["owners"]]
    roots_of = {}
    for o in setout["owners"]:
        roots_of.setdefault(o["file"], set()).add(o["name"])
    host = setout.get("host")
    solids = [r for r in records if r["kind"] in ("solid", "open") and r["root"] in owners and not (host and r["layer"].startswith(host + "::Openings"))]
    openings = [r for r in records if host and r["layer"].startswith(host + "::Openings")]
    requests = [r for r in records if r["layer"].startswith(REQUESTS)]
    dots = [r for r in records if r["kind"] == "dot" and r["layer"] == NOTES]

    clashes, unopened = [], []
    for i, a in enumerate(solids):
        for b in solids[i + 1:]:
            if a["root"] == b["root"]:
                continue
            reg = overlap(a["bb"], b["bb"])
            if reg is None:
                continue
            crossing = host in (a["root"], b["root"])
            if crossing and any(inside(reg, o["bb"]) for o in openings):
                continue
            if not penetrates(a, b):
                continue
            (unopened if crossing else clashes).append({"a": brief(a), "b": brief(b), "region": [round(v, 2) for v in reg]})

    owner_of = dict((o["name"].lower(), o["name"]) for o in setout["owners"])
    since = dict((o["name"], current_since(setout, o["name"])) for o in setout["owners"])

    def fresh(stamped, owner):
        s, need = _stamp_int(stamped), since.get(owner, int(rev))
        return s is not None and need <= s <= int(rev)
    req_owner = lambda p: owner_of.get(str(p["user"].get("from", "")).lower(), p["user"].get("from"))
    current = [p for p in requests if fresh(p["user"].get("setout_revision"), req_owner(p))]
    unanswered = [brief(p) for p in current if host and not any(inside(p["bb"], o["bb"]) for o in openings)]
    orphan = [brief(o) for o in openings if not any(inside(p["bb"], o["bb"]) for p in current)]

    breaks = []
    for r in solids:
        for z in setout["shares"]:
            if z["owner"] != r["root"] and overlap(r["bb"], z["box"]) is not None:
                breaks.append({"object": brief(r), "zone": z["zone"], "shared_to": z["owner"]})

    served, unserved = [], []
    systems = sorted(set((p["owner"], p["system"]) for p in setout.get("points", [])))
    for owner, system in systems:
        # A run connects back to its source through pieces that touch, and may pass through the owner's own
        # equipment (a panel, an air handler); the point itself must be touched by a run of its system.
        own_runs = [r for r in solids if r["layer"] == "%s::%s" % (owner, system) or r["layer"].startswith("%s::%s::" % (owner, system))]
        runs = own_runs + [r for r in solids if r["layer"] == "%s::Equipment" % owner or r["layer"].startswith("%s::Equipment::" % owner)]
        src = [p for p in setout["points"] if (p["owner"], p["system"]) == (owner, system) and p["role"] == "source"]
        reach = set()
        if src and own_runs:
            sp = src[0]["at"]
            todo = [i for i, r in enumerate(runs) if near(r["bb"], tuple(sp) * 2, 1.5)]
            reach = set(todo)
            while todo:
                i = todo.pop()
                for j, r in enumerate(runs):
                    if j not in reach and near(runs[i]["bb"], r["bb"], 0.3):
                        reach.add(j)
                        todo.append(j)
        for p in setout["points"]:
            if (p["owner"], p["system"]) != (owner, system) or p["role"] != "point":
                continue
            ok = any(near(runs[i]["bb"], tuple(p["at"]) * 2, 1.5) for i in reach if i < len(own_runs))
            (served if ok else unserved).append("%s %s: %s" % (owner, system, p["name"]))

    ownership = [brief(r) for r in records if r["root"] in owners and r["root"] not in roots_of.get(r["file"], set())]
    # A file no agent writes (a given shell: "given": true in the set-out) has no stamp, own check or version
    # to compare; its geometry is still measured for clashes, crossings and openings.
    given = set(o["file"] for o in setout["owners"] if o.get("given"))
    written = [f for f in sorted(roots_of) if f not in given]
    stale_files = sorted(f for f in written if not all(fresh(strings.get(f, {}).get(STAMP), o) for o in roots_of[f]))
    own = dict((f, own_check_state(strings.get(f, {}))) for f in written)
    versions = version_mismatches(strings, written)
    # The set-out check runs inside every team check, against the host's saved geometry when the host is an
    # owner file, so a share redrawn mid-run that overlaps another or runs into the host cannot settle.
    # host_geometry: the host's saved objects when the host is not an owner file (read by check() from the set-out's
    # host_file); otherwise the host owner's own objects among the records.
    host_file = next((o["file"] for o in setout["owners"] if o["name"] == setout.get("host")), None)
    host_geom = host_geometry if host_geometry else [r for r in records if r["file"] == host_file and r["root"] == setout.get("host")]
    gaps = setout_problems(setout, host_geom or None, requests)
    own_failing = [{"file": f, "status": s} for f, s in sorted(own.items()) if s != "pass"]
    own_failures = {}
    for f, s in own.items():
        if s == "fail":
            try:
                own_failures[f] = json.loads(strings.get(f, {}).get(OWN_CHECK) or "{}").get("failed") or []
            except ValueError:
                own_failures[f] = []
    stale_req = [p for p in requests if p not in current]
    stale_open = [o for o in openings if not fresh(o["user"].get("setout_revision"), host)] if host else []
    stale_refs = [brief(p) for p in stale_req + stale_open]
    # Per owner, what is stale and what to do. re-stamp: the item still holds (a request still inside the owner's
    # shares or a host opening; an opening still covering a current request); rebuild: what it was built to moved.
    rounds_of = setout.get("revision_rounds") or {}
    stale_by_owner = {}

    def add_stale(owner, item):
        issued = _stamp_int(rounds_of.get(str(since.get(owner, rev))))
        item["since"] = since.get(owner, int(rev))
        item["for_coordinator"] = bool(round_no is not None and issued is not None and int(round_no) >= issued + 1)
        stale_by_owner.setdefault(owner, []).append(item)
    own_boxes = lambda o: [s["box"] for s in setout.get("shares", []) if s.get("owner") == o]
    for f in stale_files:
        for o in sorted(roots_of[f]):
            add_stale(o, {"kind": "file", "item": f, "stamped": strings.get(f, {}).get(STAMP), "action": "rebuild"})
    for p in stale_req:
        o = req_owner(p)
        holds = any(inside(p["bb"], b) for b in own_boxes(o)) or any(inside(p["bb"], x["bb"]) for x in openings)
        add_stale(o, {"kind": "request", "item": p["id"], "name": p["name"], "stamped": p["user"].get("setout_revision"), "action": "re-stamp" if holds else "rebuild"})
    for x in stale_open:
        holds = any(inside(p["bb"], x["bb"]) for p in current)
        add_stale(host, {"kind": "opening", "item": x["id"], "name": x["name"], "stamped": x["user"].get("setout_revision"), "action": "re-stamp" if holds else "rebuild"})
    malformed = [r["id"] for r in dots if r["user"].get("kind") not in KINDS or r["user"].get("status") not in STATUSES
                 or not r["user"].get("from") or not r["user"].get("to")]
    asks = [r for r in dots if r["user"].get("kind") in OPEN_KINDS]
    replied = set(r["user"].get("reply_to") for r in dots if r["user"].get("kind") == "reply")
    open_notes = []
    for r in asks:
        if r["user"].get("status") == "closed":
            continue
        nid = r["user"].get("note_id") or r["id"]
        written = r["user"].get("round", "")
        age = (int(round_no) - int(written)) if round_no is not None and str(written).isdigit() else None
        open_notes.append({"id": nid, "file": r["file"], "from": r["user"].get("from"), "to": r["user"].get("to"),
                           "kind": r["user"].get("kind"), "round": written, "replied": nid in replied,
                           "text": (r.get("text") or "")[:160], "by": r["user"].get("by"), "fault_key": r["user"].get("fault_key"),
                           "at": r.get("at"),
                           "for_coordinator": bool(age is not None and age >= 1 and nid not in replied and r["user"].get("to") != "coordinator")})
    open_by_owner = {}
    for n in open_notes:
        open_by_owner.setdefault(n["to"], []).append(n["id"])
    escalated = [n for n in open_notes if n["for_coordinator"]]

    counts = {"clashes": len(clashes), "share_breaks": len(breaks), "unopened_crossings": len(unopened),
              "requests_without_opening": len(unanswered), "points_required": len(served) + len(unserved), "points_served": len(served),
              "ownership_breaks": len(ownership), "stale_files": len(stale_files), "stale_references": len(stale_refs) + len(orphan),
              "open_notes": len(open_notes), "notes_for_coordinator": len(escalated), "malformed_notes": len(malformed),
              "own_checks_not_passing": len(own_failing), "version_mismatches": len(versions),
              "setout_gaps": len(gaps)}
    counts["coordination_faults"] = counts["clashes"] + counts["share_breaks"] + counts["unopened_crossings"] + counts["requests_without_opening"]
    done = (counts["coordination_faults"] == 0 and counts["points_served"] == counts["points_required"] and counts["ownership_breaks"] == 0
            and counts["stale_files"] == 0 and counts["stale_references"] == 0 and counts["open_notes"] == 0 and counts["malformed_notes"] == 0
            and counts["own_checks_not_passing"] == 0 and counts["version_mismatches"] == 0 and counts["setout_gaps"] == 0 and len(solids) > 0)
    return {"revision": setout["revision"], "counts": counts, "settled": done,
            "clashes": clashes[:limit], "share_breaks": breaks[:limit], "unopened_crossings": unopened[:limit],
            "requests_without_opening": unanswered[:limit], "orphan_openings": orphan[:limit], "unserved_points": unserved,
            "ownership_breaks": ownership[:limit], "stale_files": stale_files, "stale_references": stale_refs[:limit],
            "stale_by_owner": stale_by_owner, "current_since": since,
            "open_notes": open_notes[:limit], "open_notes_by_addressee": open_by_owner,
            "notes_for_coordinator": escalated[:limit], "malformed_notes": malformed[:limit], "own_checks": own,
            "own_check_failures": own_failures, "version_mismatches": versions, "setout_gaps": gaps, "given_files": sorted(given),
            "coordinator_version": {"plugin": strings.get(SETOUT, {}).get(PLUGIN_KEY), "helper": strings.get(SETOUT, {}).get(HELPER_KEY)}}


def status_line(result):
    c = result["counts"]
    if result["settled"]:
        head = "Team: settled at set-out revision %s" % result["revision"]
    else:
        parts = ["%d %s" % (c[k], k.replace("_", " ")) for k in ("clashes", "share_breaks", "unopened_crossings", "requests_without_opening",
                                                                     "ownership_breaks", "stale_files", "stale_references", "open_notes", "notes_for_coordinator",
                                                                     "malformed_notes", "own_checks_not_passing", "version_mismatches", "setout_gaps") if c[k]]
        if c["points_served"] < c["points_required"]:
            parts.append("%d of %d required points served" % (c["points_served"], c["points_required"]))
        head = "Team: not settled at set-out revision %s - %s" % (result["revision"], ", ".join(parts) or "no work in the files")
    return head + "\nASTEAM settled=%s faults=%d revision=%s" % (str(result["settled"]).lower(), c["coordination_faults"], result["revision"])


# ------------------------------------------------------------------ reading files (Rhino)
def _bb(g):
    b = g.GetBoundingBox(True)
    return (b.Min.X, b.Min.Y, b.Min.Z, b.Max.X, b.Max.Y, b.Max.Z)


def _user(a):
    u = a.GetUserStrings()
    return {k: u[k] for k in u.AllKeys}


def _kind(g):
    import Rhino.Geometry as G
    if isinstance(g, G.TextDot):
        return "dot"
    if isinstance(g, G.Extrusion):
        g = g.ToBrep()
    if isinstance(g, G.Brep):
        return "solid" if g.IsSolid else "open"
    if isinstance(g, G.Mesh):
        return "solid" if g.IsClosed else "open"
    return "other"


def read_file(path, label):
    """(records, strings) of one saved .3dm, read without opening it as a document."""
    import Rhino
    import Rhino.Geometry as G
    f = Rhino.FileIO.File3dm.Read(path)
    if f is None:
        raise TeamError("cannot read %s" % path)
    s = f.Strings
    strings = dict((s.GetKey(i), s.GetValue(i)) for i in range(s.Count))
    recs, rows = [], []
    for o in f.Objects:
        g = o.Geometry
        rows.append((str(o.Attributes.ObjectId), f.AllLayers.FindIndex(o.Attributes.LayerIndex).FullPath, _bb(g)))
        if isinstance(g, G.InstanceReferenceGeometry):
            continue
        layer = f.AllLayers.FindIndex(o.Attributes.LayerIndex).FullPath
        rec = {"file": label, "layer": layer, "root": layer.split("::")[0], "name": o.Attributes.Name or "", "id": str(o.Attributes.ObjectId),
               "user": _user(o.Attributes), "bb": _bb(g), "kind": _kind(g), "g": g}
        if rec["kind"] == "dot":
            rec["text"] = g.Text
            rec["at"] = [g.Point.X, g.Point.Y, g.Point.Z]
        elif isinstance(g, G.Point):
            q = g.Location
            rec["at"] = [q.X, q.Y, q.Z]
        recs.append(rec)
    strings[NOW_FP] = geometry_fp(rows)
    return recs, strings


def setout_from(records):
    """The set-out data from setout.3dm's records."""
    out = {"revision": None, "owners": [], "host": None, "priority": [], "numbers": {}, "points": [], "shares": []}
    heads = [r for r in records if r["layer"] == "Setout::Data" and "data" in r["user"]]
    if len(heads) != 1:
        raise TeamError("setout.3dm needs exactly one object on Setout::Data with a 'data' user string; found %d" % len(heads))
    out.update(json.loads(heads[0]["user"]["data"]))
    for r in records:
        if r["layer"] == "Setout::Points" and "at" in r:
            out["points"].append({"owner": r["user"].get("owner"), "system": r["user"].get("system"), "role": r["user"].get("role"),
                                  "name": r["name"], "at": r["at"]})
        elif r["layer"].startswith("Share::"):
            out["shares"].append({"owner": r["user"].get("owner") or r["layer"].split("::")[1], "zone": r["user"].get("zone") or r["name"],
                                        "by": r["user"].get("by"), "box": [round(v, 3) for v in r["bb"]],
                                        "crossing": str(r["user"].get("crossing", "")).lower() == "true"})
    if out["revision"] is None or not out["owners"]:
        raise TeamError("set-out data needs 'revision' and 'owners'")
    return out


def _penetrates(a, b):
    """True when two solids share volume. Touching is not a clash. Same test as the maintainers' measuring script."""
    import Rhino.Geometry as G
    ba, bb_ = [x["g"].ToBrep() if isinstance(x["g"], G.Extrusion) else x["g"] for x in (a, b)]
    if not isinstance(ba, G.Brep) or not isinstance(bb_, G.Brep):
        return True
    ca = G.Point3d(*[(b["bb"][i] + b["bb"][i + 3]) / 2 for i in range(3)])
    cb = G.Point3d(*[(a["bb"][i] + a["bb"][i + 3]) / 2 for i in range(3)])
    if (ba.IsSolid and ba.IsPointInside(ca, 0.01, True)) or (bb_.IsSolid and bb_.IsPointInside(cb, 0.01, True)):
        return True
    ok, crvs, pts = G.Intersect.Intersection.BrepBrep(ba, bb_, 0.001)
    if crvs is None or len(crvs) == 0:
        return False
    if not (ba.IsSolid and bb_.IsSolid):
        return True
    common = G.Brep.CreateBooleanIntersection([ba], [bb_], 0.001)
    if common and sum(abs(G.VolumeMassProperties.Compute(c).Volume) for c in common if G.VolumeMassProperties.Compute(c)) > 0.01:
        return True
    for p, q in ((ba, bb_), (bb_, ba)):
        for e in p.Edges:
            for t in (e.PointAtStart, e.PointAt(e.Domain.Mid)):
                if q.IsPointInside(t, 0.01, True):
                    return True
    return False


def host_path(setout_data, folder):
    """The host's saved file: the host owner's file, else the set-out's `host_file` (a host that is not an owner, such
    as a given shell nobody writes), else the one .3dm in the folder that is neither the set-out nor an owner file.
    None when there is none, or more than one candidate (no Rhino)."""
    for o in setout_data.get("owners", []):
        if o["name"] == setout_data.get("host"):
            return os.path.join(folder, o["file"])
    if setout_data.get("host_file"):
        return os.path.join(folder, os.path.basename(setout_data["host_file"]))
    known = set([SETOUT] + [o["file"] for o in setout_data.get("owners", [])])
    try:
        others = sorted(f for f in os.listdir(folder) if f.lower().endswith(".3dm") and f not in known)
    except OSError:
        return None
    return os.path.join(folder, others[0]) if len(others) == 1 else None


def setout_notes(setout_records):
    """The coordinator's own notes (rulings, issues, replies) in setout.3dm, as team-check records labelled with the
    set-out's file name (no Rhino). Invariant 7: its own open rulings and issues block settled too."""
    return [dict(r, file=SETOUT) for r in setout_records if r.get("kind") == "dot" and r.get("layer") == NOTES]


def check(folder, round_no=None, write=False):
    crecs, setout_strings = read_file(os.path.join(folder, SETOUT), "setout")
    setout = setout_from(crecs)
    records, strings = list(setout_notes(crecs)), {SETOUT: setout_strings}
    for name in sorted(set(o["file"] for o in setout["owners"])):
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            raise TeamError("owner file %s is missing from %s" % (name, folder))
        recs, file_strings = read_file(path, name)
        records += recs
        strings[name] = file_strings
    host = host_path(setout, folder)
    owner_files = set(o["file"] for o in setout["owners"])
    host_geometry = None
    if host and os.path.basename(host) not in owner_files and os.path.isfile(host):
        host_geometry = read_file(host, os.path.basename(host))[0]   # measured for the set-out check only
    result = analyse(setout, records, strings, _penetrates, round_no=round_no, host_geometry=host_geometry)
    result["host_checked"] = os.path.basename(host) if host and os.path.isfile(host) else None
    if write and round_no is not None:
        out = os.path.join(folder, "reports", "round-%s.json" % round_no)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out + ".tmp", "w") as handle:
            json.dump(result, handle, indent=1)
        os.replace(out + ".tmp", out)
        result["written"] = out
    return result


# ------------------------------------------------------------------ helpers for an agent's own document (Rhino)
CFG = globals().get("AS_TEAM") or {}


def _doc():
    doc = globals().get("__rhino_doc__")
    if doc is None:
        raise TeamError("no open Rhino document: run this through the Rhino tools' run_python")
    me = CFG.get("me")
    want = SETOUT if me == "coordinator" else _my_file()
    if not doc.Path or os.path.basename(doc.Path) != want or os.path.dirname(os.path.abspath(doc.Path)) != os.path.abspath(CFG["folder"]):
        raise TeamError("the open document is %s; %s works only in %s" % (doc.Path or "untitled", me, os.path.join(CFG["folder"], want)))
    return doc


def setout():
    return setout_from(read_file(os.path.join(CFG["folder"], SETOUT), "setout")[0])


def _my_file():
    for o in setout()["owners"]:
        if o["name"] == CFG.get("me"):
            return o["file"]
    raise TeamError("%s is not an owner in setout.3dm" % CFG.get("me"))


def _layer(doc, path):
    import Rhino
    i = doc.Layers.FindByFullPath(path, -1)
    if i >= 0:
        return i
    parent = None
    for part in path.split("::"):
        full = part if parent is None else doc.Layers[parent].FullPath + "::" + part
        i = doc.Layers.FindByFullPath(full, -1)
        if i < 0:
            layer = Rhino.DocObjects.Layer()
            layer.Name = part
            if parent is not None:
                layer.ParentLayerId = doc.Layers[parent].Id
            i = doc.Layers.Add(layer)
        parent = i
    return parent


def _model_view(doc):
    """With a layout active, Rhino puts added objects on its page; make a model view active first."""
    view = doc.Views.ActiveView
    if view is not None and getattr(view, "PageName", None) is not None:
        views = list(doc.Views.GetViewList(True, False))  # model views only
        if not views:
            raise RuntimeError("a layout is active and the document has no model view; open Perspective and run again")
        doc.Views.ActiveView = views[0]


def _attrs(doc, layer, name, **user):
    import Rhino
    _model_view(doc)
    a = Rhino.DocObjects.ObjectAttributes()
    a.Space = Rhino.DocObjects.ActiveSpace.ModelSpace
    a.LayerIndex = _layer(doc, layer)
    a.Name = name
    for k, v in user.items():
        a.SetUserString(k, str(v))
    return a


def box(x0, y0, z0, x1, y1, z1):
    import Rhino.Geometry as G
    return G.Box(G.BoundingBox(min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1))).ToBrep()


def others(owner=None):
    """Records of the other owners' files as last saved (read only)."""
    me = CFG.get("me")
    out = []
    for o in setout()["owners"]:
        if o["name"] != me and (owner is None or o["name"] == owner):
            out += read_file(os.path.join(CFG["folder"], o["file"]), o["file"])[0]
    return out


def notes():
    """{'to_me', 'mine', 'others'} across every file as last saved; the open document counts as 'mine' as it is now."""
    me = CFG.get("me")
    doc = _doc()
    mine = [{"id": o.Attributes.GetUserString("note_id"), "text": o.Geometry.Text, "user": _user(o.Attributes)}
            for o in doc.Objects if o.Attributes.GetUserString("note_id") and not o.IsDeleted]
    files = [o["file"] for o in setout()["owners"]] + [SETOUT]
    mine_file = SETOUT if me == "coordinator" else _my_file()
    rest = []
    for f in sorted(set(files) - {mine_file}):
        path = os.path.join(CFG["folder"], f)
        if os.path.isfile(path):
            rest += [dict(r, id=r["user"].get("note_id") or r["id"]) for r in read_file(path, f)[0] if r["kind"] == "dot" and r["layer"] == NOTES]
    return {"mine": mine, "to_me": [n for n in rest if n["user"].get("to") in (me, "everyone")],
            "others": [n for n in rest if n["user"].get("to") not in (me, "everyone")]}


def note(to, text, at, kind="request", reply_to=None, issue_kind=None, object=None):
    """Leave a note (text dot on Notes) in the open document, at the place it is about.
    kind issue: a problem with someone's objects, to the owner of the object that must change (never fix theirs);
    request: an open design value, to the coordinator; change: a change order, to the coordinator;
    reply: an answer, with reply_to; ruling: coordinator only."""
    import Rhino.Geometry as G
    if kind not in KINDS:
        raise TeamError("kind must be one of %s" % ", ".join(KINDS))
    if issue_kind is not None and (kind != "issue" or issue_kind not in FAULT_KINDS):
        raise TeamError("issue_kind goes on an issue note and is one of %s, the team check's lists; "
                        "a direction about a set-out change is a ruling, not an issue" % ", ".join(FAULT_KINDS))
    if kind == "ruling" and CFG.get("me") != "coordinator":
        raise TeamError("only the coordinator rules")
    if kind in ("change", "request") and to != "coordinator":
        raise TeamError("a %s goes to the coordinator; an issue with another owner's objects is kind issue" % kind)
    doc = _doc()
    nid = uuid.uuid4().hex[:8]
    user = {"note_id": nid, "from": CFG.get("me"), "to": to, "kind": kind, "status": "answered" if kind == "reply" else "open",
            "round": CFG.get("round", "")}
    if reply_to:
        user["reply_to"] = reply_to
    if issue_kind is not None:
        user["issue_kind"] = issue_kind
    if object is not None:
        user["object"] = str(object)
    doc.Objects.AddTextDot(G.TextDot(text, G.Point3d(*at)), _attrs(doc, NOTES, "%s note" % kind, **user))
    return nid


def close(note_id):
    """Close a note of your own once it is dealt with."""
    doc = _doc()
    for o in doc.Objects:
        if o.Attributes.GetUserString("note_id") == note_id:
            a = o.Attributes.Duplicate()
            a.SetUserString("status", "closed")
            a.SetUserString("closed_round", str(CFG.get("round", "")))
            doc.Objects.ModifyAttributes(o, a, True)
            return note_id
    raise TeamError("no note %s in your file" % note_id)


def stamp(revision=None):
    """Record which set-out revision this file is built to (default: the current one). Stamp only after your own
    requirements check passed on that revision."""
    doc = _doc()
    current = setout()["revision"]
    revision = current if revision is None else revision
    doc.Strings.SetString(STAMP, str(revision))
    doc.Strings.SetString(PLUGIN_KEY, plugin_version())
    doc.Strings.SetString(HELPER_KEY, helper_version())
    # Report against the set-out as it is now: never call a file current that is stamped to an older revision.
    return {"stamped": revision, "setout_revision": current, "status": stamp_status(revision, current)}


def restamp_requests():
    """Owner: re-stamp, to the current set-out revision, every opening request of yours that still holds: still
    inside one of your shares (crossing shares included) or a host opening as last saved. The team check lists
    these as action "re-stamp". Returns the ids re-stamped; requests that no longer hold are left for you to rebuild."""
    doc = _doc()
    data = setout()
    me = CFG.get("me")
    boxes = [s["box"] for s in data["shares"] if s.get("owner") == me]
    boxes += [_box_of(r) for r in host_records() if "::Openings" in r.get("layer", "")]
    done = []
    for o in list(doc.Objects):
        if doc.Layers[o.Attributes.LayerIndex].FullPath.startswith(REQUESTS) and str(o.Attributes.GetUserString("setout_revision")) != str(data["revision"]):
            b = _bb(o.Geometry)
            if any(inside(b, x) for x in boxes):
                a = o.Attributes.Duplicate()
                a.SetUserString("setout_revision", str(data["revision"]))
                doc.Objects.ModifyAttributes(o, a, True)
                done.append(str(o.Id))
    return done


def request_opening(x0, y0, z0, x1, y1, z1, through):
    """Ask the host owner for an opening where a run of yours passes through its elements."""
    doc = _doc()
    return str(doc.Objects.AddBrep(box(x0, y0, z0, x1, y1, z1), _attrs(doc, REQUESTS, "Opening request through %s" % through,
                                                                      through=through, setout_revision=setout()["revision"], **{"from": CFG.get("me")})))


def share(owner, zone, x0, y0, z0, x1, y1, z1, crossing=False):
    """Coordinator only, while writing or reissuing the set-out: give an owner a box of shared space under a zone
    name, replacing a zone of the same name. Shares of two owners must not overlap. crossing=True: a short share
    where the owner's run passes through the host (a wall, a floor); it may sit in host solids only inside a host
    opening or the owner's own opening request."""
    if CFG.get("me") != "coordinator":
        raise TeamError("only the coordinator hands out space")
    doc = _doc()
    if owner not in [o["name"] for o in setout()["owners"]]:
        raise TeamError("%s is not an owner in setout.3dm" % owner)
    release(zone, quiet=True)
    extra = {"crossing": "true"} if crossing else {}
    return str(doc.Objects.AddBrep(box(x0, y0, z0, x1, y1, z1), _attrs(doc, "Share::" + owner, zone, owner=owner, zone=zone, by="coordinator",
                                                                      round=CFG.get("round", ""), **extra)))


def release(zone, quiet=False):
    """Coordinator only, while reissuing the set-out: remove a share by zone name."""
    doc = _doc()
    gone = 0
    for o in list(doc.Objects):
        if doc.Layers[o.Attributes.LayerIndex].FullPath.startswith("Share::") and o.Attributes.GetUserString("zone") == zone:
            doc.Objects.Delete(o, True)
            gone += 1
    if not gone and not quiet:
        raise TeamError("no share named %s" % zone)
    return gone


def missing_files(setout_data, present):
    """Owner files the set-out names that are not in the folder (no Rhino)."""
    return sorted(set(o["file"] for o in setout_data.get("owners", [])) - set(present))


def preflight():
    """Before anything else, every agent: the shared folder, the set-out, every owner file, and whether the open
    document is this agent's own file. Returns {"clear": bool, "problems": [...], "next": [...]}; each problem is a
    user action. The coordinator's preflight does not require the set-out before it has written one: it is clear
    with the next step to take, since writing the set-out is its first job."""
    problems, next_steps = [], []
    folder = CFG.get("folder")
    me = CFG.get("me")
    if not folder or not os.path.isdir(folder):
        return {"clear": False, "problems": ["the shared folder %s is not reachable from this session" % folder], "next": []}
    present = os.listdir(folder)
    doc = globals().get("__rhino_doc__")
    if doc is None:
        problems.append("no open Rhino document: follow rhino-setup")
    if SETOUT not in present:
        if me == "coordinator":
            target = os.path.join(folder, SETOUT)
            if doc is not None and (not doc.Path or os.path.abspath(doc.Path) != os.path.abspath(target)):
                next_steps.append("save your open document as %s, then write the set-out (write_setout, points, share)" % target)
            else:
                next_steps.append("write the set-out (write_setout, points, share) and run check_setout() before the owners' first turn")
            return {"clear": not problems, "problems": problems, "next": next_steps}
        problems.append("no %s yet: the coordinator writes the set-out before anyone builds" % SETOUT)
    else:
        try:
            data = setout()
            given = set(o["file"] for o in data["owners"] if o.get("given"))
            problems += ["owner file %s is missing from the shared folder" % f for f in missing_files(data, present)
                         if f in given or me == "coordinator"]
            if me not in ["coordinator"] + [o["name"] for o in data["owners"]]:
                problems.append("%s is not an owner in the set-out" % me)
            if me == "coordinator":
                next_steps += setout_problems(data)
        except TeamError as exc:
            problems.append(str(exc))
    if doc is not None and not problems:
        try:
            _doc()
        except TeamError as exc:
            if me != "coordinator" and SETOUT in present:
                # an owner's own file may not exist yet in round 1: it saves it there
                next_steps.append(str(exc) + "; save your open document there before you build")
            else:
                problems.append(str(exc))
    return {"clear": not problems, "problems": problems, "next": next_steps}


def write_setout(data):
    """Coordinator only: write the set-out data (revision 1, before anyone builds). data: revision, owners, host,
    datum, levels, priority, numbers, min_sizes. Points go on Setout::Points and shares through share()."""
    if CFG.get("me") != "coordinator":
        raise TeamError("only the coordinator writes the set-out")
    doc = _doc()
    for key in ("revision", "owners", "levels"):
        if key not in data:
            raise TeamError("set-out data needs %s" % key)
    data = dict(data, levels=normalize_levels(data["levels"]))
    import Rhino.Geometry as G
    for o in list(doc.Objects):
        if doc.Layers[o.Attributes.LayerIndex].FullPath == "Setout::Data":
            doc.Objects.Delete(o, True)
    data = dict(data)
    data.setdefault("revision_rounds", {str(data["revision"]): CFG.get("round", "")})
    doc.Objects.AddPoint(G.Point3d(0, 0, 0), _attrs(doc, "Setout::Data", "Set-out data", data=json.dumps(data)))
    doc.Strings.SetString(STAMP, str(data["revision"]))
    doc.Strings.SetString(PLUGIN_KEY, plugin_version())
    doc.Strings.SetString(HELPER_KEY, helper_version())
    return data["revision"]


def host_records():
    """The host's objects as last saved: the host owner's file, or the set-out's `host_file` when the host is not
    an owner (see host_path()); [] when there is no host file. issue() and check_setout() use it, so a share
    redrawn into new host geometry (a post added by a change) is caught."""
    path = host_path(setout(), CFG["folder"])
    return read_file(path, os.path.basename(path))[0] if path and os.path.isfile(path) else []


def owner_requests():
    """Every owner's opening requests as last saved (records on Interface::Penetrations with user `from`)."""
    out = []
    for o in setout()["owners"]:
        path = os.path.join(CFG["folder"], o["file"])
        if os.path.isfile(path):
            out += [r for r in read_file(path, o["file"])[0] if r["layer"].startswith(REQUESTS)]
    return out


CHECK_BY = "team-check"     # the `by` user string on issue notes written by post_fault_notes()


def _centre(b):
    return [round((b[i] + b[i + 3]) / 2.0, 3) for i in range(3)]


def _who(o):
    return o.get("name") or o.get("id") or ""


def fault_notes(result, setout_data):
    """The issue notes the team check's fault list calls for (no Rhino): one per fault, addressed to the one owner who
    must move, at the object. [{"key", "to", "issue_kind", "object", "at", "text"}]. `key` names the fault by owner and
    object name, so the same fault keeps the same key across rounds even when an owner rebuilds the object.
    Routing (step 6): a clash goes to the owner whose share does not hold the clash, else to the lower one in the
    priority order, else to the later owner in the set-out; a run through the host and a share break go to the owner
    of the run; a request the host has not answered goes to the host; an unserved point and a failed `within` check
    go to their owner; a note left unanswered for a round goes to its addressee. Notes written by this helper are not
    escalated again: they close themselves when their fault is gone."""
    owners = [o["name"] for o in setout_data.get("owners", [])]
    owner_of_file = {}
    for o in setout_data.get("owners", []):
        owner_of_file.setdefault(o["file"], []).append(o["name"])
    root = lambda b: b["layer"].split("::")[0]
    priority = [str(x).lower() for x in setout_data.get("priority") or []]

    def rank(owner):
        hits = [i for i, x in enumerate(priority) if owner.lower() in x]
        return min(hits) if hits else len(priority)

    def holds(owner, region):
        return any(s.get("owner") == owner and overlap(region, s["box"]) is not None for s in setout_data.get("shares", []))
    out = []

    def add(key, to, kind, obj, at, text):
        if to and not any(x["key"] == key for x in out):
            out.append({"key": key, "to": to, "issue_kind": kind, "object": obj, "at": at, "text": text})
    for c in result.get("clashes", []):
        a, b = c["a"], c["b"]
        oa, ob = root(a), root(b)
        if holds(oa, c["region"]) and not holds(ob, c["region"]):
            mover, keeper = ob, oa
        elif holds(ob, c["region"]) and not holds(oa, c["region"]):
            mover, keeper = oa, ob
        elif rank(oa) != rank(ob):
            mover, keeper = (oa, ob) if rank(oa) > rank(ob) else (ob, oa)
        else:
            mover, keeper = (oa, ob) if owners.index(oa) > owners.index(ob) else (ob, oa)
        mine, theirs = (a, b) if root(a) == mover else (b, a)
        pair = sorted(["%s:%s" % (oa, _who(a)), "%s:%s" % (ob, _who(b))])
        add("clash|%s|%s" % tuple(pair), mover, "clash", _who(mine), _centre(c["region"]),
            "%s clashes with %s's %s: move yours clear (%s keeps its place)." % (_who(mine), keeper, _who(theirs), keeper))
    host = setout_data.get("host")
    for c in result.get("unopened_crossings", []):
        run = c["a"] if root(c["a"]) != host else c["b"]
        add("through_shell|%s:%s" % (root(run), _who(run)), root(run), "through_shell", _who(run), _centre(c["region"]),
            "%s passes through %s with no opening: reroute it, or request an opening there." % (_who(run), host))
    for q in result.get("requests_without_opening", []):
        add("through_shell|request|%s" % _who(q), host, "through_shell", _who(q), _centre(q["box"]),
            "Opening request %s has no opening yet: add one covering it." % _who(q))
    for br in result.get("share_breaks", []):
        o = br["object"]
        add("reservation|%s:%s|%s" % (root(o), _who(o), br["zone"]), root(o), "reservation", _who(o), _centre(o["box"]),
            "%s is inside %s's share %s: move it into your own share or free space." % (_who(o), br["shared_to"], br["zone"]))
    points = dict(("%s %s: %s" % (p["owner"], p["system"], p["name"]), p) for p in setout_data.get("points", []))
    for u in result.get("unserved_points", []):
        p = points.get(u)
        if p:
            add("unserved|%s" % u, p["owner"], "unserved", p["name"], list(p["at"]),
                "%s is not served: connect it to its source through your %s runs." % (p["name"], p["system"]))
    for f, failed in sorted((result.get("own_check_failures") or {}).items()):
        for name in failed:
            if str(name).startswith("within"):
                for o in owner_of_file.get(f, []):
                    add("undersize|%s|%s" % (o, name), o, "undersize", name, [0, 0, 0],
                        "Your own check fails %s: a run outside your shares or under its minimum size." % name)
    for n in result.get("notes_for_coordinator", []):
        if n.get("by") == CHECK_BY or n.get("to") not in owners:
            continue
        add("note|%s" % n["id"], n["to"], "note", n["id"], n.get("at") or [0, 0, 0],
            "Note %s from %s has had no reply for a round: answer it." % (n["id"], n.get("from")))
    return out


def sync_plan(wanted, open_check_notes):
    """Which notes to write and which to close (no Rhino). wanted: fault_notes(); open_check_notes: this helper's own
    open notes as {"id", "fault_key", "to"}. A fault with an open note for the same key and owner gets no second one; an
    open note whose fault is gone is closed."""
    have = dict(((n.get("fault_key"), n.get("to")), n["id"]) for n in open_check_notes)
    write = [w for w in wanted if (w["key"], w["to"]) not in have]
    keep = set((w["key"], w["to"]) for w in wanted)
    close_ids = [nid for k, nid in have.items() if k not in keep]
    return {"write": write, "close": close_ids, "kept": len(wanted) - len(write)}


def post_fault_notes(result=None):
    """Coordinator, every round: turn the team check's fault list into issue notes. Writes one `issue` note per fault at
    the object, addressed to the owner who must move, marked by="team-check" with its fault_key; writes none for a fault
    whose note is still open; closes its own notes whose fault the check no longer lists. Save afterwards, then run the
    team check with "write": True. Returns {"written", "closed", "kept", "notes"}."""
    if CFG.get("me") != "coordinator":
        raise TeamError("only the coordinator posts the team check's fault notes")
    result = result if result is not None else check(CFG["folder"], CFG.get("round"))
    data = setout()
    doc = _doc()
    mine = [{"id": o.Attributes.GetUserString("note_id"), "fault_key": o.Attributes.GetUserString("fault_key"), "to": o.Attributes.GetUserString("to")}
            for o in doc.Objects if not o.IsDeleted and o.Attributes.GetUserString("by") == CHECK_BY
            and o.Attributes.GetUserString("status") not in ("closed",)]
    plan = sync_plan(fault_notes(result, data), mine)
    written = []
    for w in plan["write"]:
        nid = note(w["to"], w["text"], w["at"], kind="issue", issue_kind=w["issue_kind"], object=w["object"])
        for o in doc.Objects:
            if o.Attributes.GetUserString("note_id") == nid:
                a = o.Attributes.Duplicate()
                a.SetUserString("by", CHECK_BY)
                a.SetUserString("fault_key", w["key"])
                doc.Objects.ModifyAttributes(o, a, True)
        written.append(nid)
    for nid in plan["close"]:
        close(nid)
    return {"written": written, "closed": plan["close"], "kept": plan["kept"], "notes": plan["write"]}


def check_setout(host=None):
    """Coordinator: run after writing or reissuing the set-out, and fix every problem before the owners' turn.
    `host`: the host's objects (dicts with layer, name and box or bb) when the host is not an owner file."""
    return setout_check(setout(), host if host is not None else host_records(), requests=owner_requests())


def issue(description, **updates):
    """Coordinator only: reissue the set-out after a change, and run the set-out check on it. Returns
    {"revision", "setout_check"}. Raises the revision by one, records the plain
    description of what changed (owners read it before they rebuild) and applies any updates to the data.
    Redraw the shares it affects with share() and release() in the same turn, before the owners' turn."""
    if not description or not description.strip():
        raise TeamError("say in plain words what changed and why")
    old = setout()
    data = dict(old)
    for key in ("points", "shares"):
        data.pop(key, None)
    data.update(updates)
    history = list(data.get("history", []))
    history.append({"revision": data["revision"], "change": data.get("change")})
    # What each owner built to in the outgoing revision, so the team check can carry forward any owner the new
    # revision does not touch (its shares, points, levels and datum unchanged), instead of making everything stale.
    digests = dict(data.get("owner_digests") or {})
    digests[str(old["revision"])] = dict((o["name"], owner_digest(old, o["name"])) for o in old["owners"])
    rounds = dict(data.get("revision_rounds") or {})
    rounds[str(int(old["revision"]) + 1)] = CFG.get("round", "")
    data.update(revision=int(data["revision"]) + 1, change=description.strip(), history=history, owner_digests=digests, revision_rounds=rounds)
    revision = write_setout(data)
    # The set-out check runs on every reissue. Shares are usually redrawn right after: run check_setout()
    # again once they are, and the team check refuses settled while any problem remains.
    return {"revision": revision, "setout_check": setout_check(setout(), host_records(), requests=owner_requests())}

def save():
    """Save the open document in place so the others read it next round. Returns the path."""
    import Rhino
    doc = _doc()
    if not doc.WriteFile(doc.Path, Rhino.FileIO.FileWriteOptions()):
        raise TeamError("could not save %s" % doc.Path)
    return doc.Path


def summary():
    """Call first every round."""
    c = setout()
    doc = _doc()
    n = notes()
    return {"me": CFG.get("me"), "round": CFG.get("round"), "plugin": plugin_version(), "helper": helper_version(), "setout_revision": c["revision"], "change": c.get("change"), "my_stamp": doc.Strings.GetValue("setout_revision"),
            "my_stamp_status": stamp_status(doc.Strings.GetValue("setout_revision"), c["revision"]) if CFG.get("me") != "coordinator" else None,
            "setout_gaps": setout_problems(c) if CFG.get("me") == "coordinator" else None,
            "owners": [o["name"] for o in c["owners"]], "host": c.get("host"), "priority": c.get("priority"),
            "shares": [(r["owner"], r["zone"]) for r in c["shares"]], "notes_to_me": n["to_me"],
            "my_open_notes": [x for x in n["mine"] if x["user"].get("status") not in ("closed", "answered")],
            # the coordinator reads every open note, not only those addressed to it
            "all_open_notes": [x for x in n["to_me"] + n["others"] if x["user"].get("kind") in OPEN_KINDS and x["user"].get("status") != "closed"]
            if CFG.get("me") == "coordinator" else None}


if globals().get("AS_MODE") == "check":
    _result = check(CFG["folder"], CFG.get("round"), bool(CFG.get("write")))
    print(status_line(_result))
    print(json.dumps(_result, indent=1)[:20000])
