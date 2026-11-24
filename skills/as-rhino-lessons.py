#! python3
"""Local lessons for the as-rhino skills (Arch Studio): write, read and promote.

One plain text file per skill and one firm rules file, in the plugin's data folder, which
Claude Code keeps across plugin updates. The startup hook names the folder; pass it as
AS_LESSONS_DIR. Nothing here touches the model, the checker, its tests or answer keys.

Runs by file path through run_python (no Rhino needed):

    P = "<absolute path of the skills folder>/as-rhino-lessons.py"
    exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_MODE": "read",
         "AS_SKILL": "rhino-model", "AS_LESSONS_DIR": "<folder named by the startup line>"})

AS_MODE
  read     firm rules for the skill, then its lessons, repeats counted, newest first
  write    append AS_LESSONS = [{"tag": "U" | "F" | "M" | "J", "kind": "practice" | "preference",
           "text": "...", "user_said": "...", "user_wrote": false}]. Every lesson declares a kind:
           practice (how to build in Rhino: construction, normals, joins, duplicates, tolerances)
           or preference (the user's own: tolerances, layers, naming, or a design preference the
           user stated). A preference needs tag U and user_said, what the user said; it is kept
           with the lesson. Anything else is refused, so a design, architectural or engineering
           rule the agent inferred is never stored. The script cannot judge the text: the kind is
           declared by the agent under the skill's rules, and the script enforces the declaration. Terms in AS_PRIVATE (project, client, people, places, the
           document name) and paths, emails, phone numbers, URLs and street addresses are
           stripped unless user_wrote is true: the user wrote that wording into the lesson
  offer    lessons that may become firm rules: only [U] lessons with a kind (the user's own
           preferences or practice) not already covered by a firm rule. A lesson written
           before kinds existed is read but never offered until a kind is added to its line. Lessons about tools,
           scripts or checks ([F], [M], [J]) are never offered, however often they repeat.
           Ask the user with ask_user before promoting, each candidate in plain words
  promote  AS_PROMOTE = {"ids": ["a1b2c3"], "confirmed": true, "answer": "<the user's
           ask_user answer>", "scope": "skill" | "all", "wording": {"a1b2c3": "<the rule
           as the user saw it>"}}. Refused without both confirmed and answer, or for an id
           the offer did not list. wording is optional; when given, the firm rule keeps it.
           "declined": [ids] records the candidates the user turned down (a "None" answer
           declines them all) in declined.txt, so they are not offered again

Tags: [U] user correction, [F] failure then fix, [M] measured, [J] judgment (unconfirmed).
Kinds: practice or preference, written after the tag: "time [U] preference: text (user said: ...)".

From a shell or a test: python3 as-rhino-lessons.py MODE --skill S --dir D [--json FILE],
where FILE holds {"lessons": [...], "private": [...], "promote": {...}}.

Standard library only.
"""
import hashlib
import json
import os
import re
import sys
import time

SKILLS = ("rhino-model", "rhino-bom", "rhino-display", "rhino-thinline", "rhino-axon")
TAGS = {"U": "user correction", "F": "failure then fix", "M": "measured", "J": "judgment, unconfirmed"}
FIRM = "firm-rules.txt"
DECLINED = "declined.txt"
SUBDIR = "rhino-lessons"
MAX_TEXT = 300
MAX_READ = 30
KINDS = {"practice": "modeling practice", "preference": "the user's own preference, stated by the user"}
MAX_SAID = 200
LINE = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) \[([UFMJ])\] (?:(practice|preference): )?(.+)$")
RULE = re.compile(r"^(\d{4}-\d\d-\d\d) (rhino-[a-z]+|all): (.+?)(?: \(from ([0-9a-f]{6})\))?$")
STOP = set("a an the to of in on at and or is are be by for with it its that this as from when "
           "than then so do does".split())

HEADERS = {
    "lessons": ("# Arch Studio lessons for {skill}, written by the skill at the end of each run.\n"
                "# One lesson per line: time [tag] text. Tags: [U] user correction, [F] failure then\n"
                "# fix, [M] measured, [J] judgment (unconfirmed). Kinds: practice, or preference (the\n"
                "# user's own, with what the user said). Plain text; edit or delete freely.\n"),
    "firm": ("# Arch Studio firm rules for the as-rhino skills. A rule is added only after the user\n"
             "# agreed to it. One rule per line: date skill-or-all: text (from lesson id).\n"),
    "declined": ("# Preferences the user chose not to make firm rules; they are not offered again.\n"
                 "# One per line: date skill: lesson id text. Delete a line to have it offered again.\n"),
}

# A lesson that proposes changing a measuring instrument is refused, not stored.
INSTRUMENT = re.compile(r"as-check(-model)?\.py|as-pdf-check\.py|\bchecker\b|\bgrader\b|"
                        r"(requirements|pdf|sheet|model) check|answer key|\bexpected/|\bevals?/|\btests?\b", re.I)
CHANGE = re.compile(r"\b(edit|change|modify|patch|relax|loosen|disable|bypass|skip|delete|remove|rewrite|"
                    r"widen|lower|comment out|override)\b", re.I)
NEGATION = re.compile(r"\b(never|don't|do not|not)\b", re.I)

PATTERNS = [
    ("<email>", re.compile(r"\b[\w.+-]+@[\w-]+(\.[\w-]+)+\b")),
    ("<url>", re.compile(r"\b(https?://|www\.)\S+", re.I)),
    ("<path>", re.compile(r"(~|[A-Za-z]:)?[\\/](Users|home|Documents|Desktop|Volumes|mnt|private|var|tmp)[\\/]\S*", re.I)),
    ("<path>", re.compile(r"\b[A-Za-z]:\\\S+")),
    ("<path>", re.compile(r"(?<![\w:])/(?:[\w.-]+/)+[\w.-]*")),
    ("<path>", re.compile(r"\S+\.3dm\b", re.I)),
    ("<place>", re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s+){1,3}(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|"
                           r"Drive|Dr|Way|Place|Pl|Court|Ct|Calle|Rua)\b\.?")),
    ("<place>", re.compile(r"-?\d{1,3}\.\d{3,},\s*-?\d{1,3}\.\d{3,}")),
    ("<phone>", re.compile(r"\+\d[\d ()-]{7,}\d|\(\d{3}\)\s?\d{3}[-.]\d{4}\b|\b\d{3}[-.]\d{3}[-.]\d{4}\b")),
]


class LessonError(Exception):
    """A request the script refuses."""


def sanitize_id(text):
    return re.sub(r"[^A-Za-z0-9_-]", "-", text)


def derive_data_dir(plugin_root):
    """The plugin data folder for an install under .../plugins/cache/<marketplace>/<plugin>/<version>.

    Mirrors Claude Code's ${CLAUDE_PLUGIN_DATA}: .../plugins/data/<plugin@marketplace with every
    character other than a letter, digit, _ or - replaced by ->. None when the layout is not that.
    """
    parts = os.path.normpath(os.path.abspath(plugin_root)).split(os.sep)
    if len(parts) < 5 or parts[-5:-3] != ["plugins", "cache"]:
        return None
    marketplace, plugin = parts[-3], parts[-2]
    return os.sep.join(parts[:-5] + ["plugins", "data", sanitize_id(plugin + "@" + marketplace)])


def plugin_root_of(script_file):
    return os.path.dirname(os.path.dirname(os.path.abspath(script_file)))


def resolve_dir(given=None, script_file=None, environ=None):
    """The lessons folder: the one the startup line named, else CLAUDE_PLUGIN_DATA, else derived."""
    environ = os.environ if environ is None else environ
    if given:
        folder = os.path.abspath(os.path.expanduser(given))
    elif environ.get("CLAUDE_PLUGIN_DATA"):
        folder = os.path.join(environ["CLAUDE_PLUGIN_DATA"], SUBDIR)
    else:
        data = derive_data_dir(plugin_root_of(script_file)) if script_file else None
        if not data:
            raise LessonError("no lessons folder: pass AS_LESSONS_DIR, the folder the Arch Studio startup line names")
        folder = os.path.join(data, SUBDIR)
    real = os.path.realpath(folder)
    if script_file:
        root = os.path.realpath(plugin_root_of(script_file))
        if real == root or real.startswith(root + os.sep):
            raise LessonError("refused: the lessons folder is inside the installed plugin, next to the checker and its tests")
    for marker in (".claude-plugin", "skills", "evals"):
        if os.path.isdir(os.path.join(real, marker)):
            raise LessonError("refused: %s looks like a plugin or repository folder, not a lessons folder" % folder)
    return folder


def normalize(text):
    words = re.sub(r"[^a-z0-9<>]+", " ", text.lower()).split()
    return [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words if w not in STOP]


def similar(a, b):
    sa, sb = set(normalize(a)), set(normalize(b))
    if not sa or not sb:
        return False
    return len(sa & sb) / float(len(sa | sb)) >= 0.75


def lesson_id(text):
    return hashlib.sha1(" ".join(normalize(text)).encode("utf-8")).hexdigest()[:6]


def strip_private(text, private=(), user_wrote=False):
    """Return (clean text, list of what was removed). User-written wording is kept as written."""
    text = " ".join(str(text).split())
    if user_wrote:
        return text, []
    removed = []
    for term in sorted({t.strip() for t in private if t and len(t.strip()) >= 2}, key=len, reverse=True):
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.I)
        if pattern.search(text):
            removed.append(term)
            text = pattern.sub("<project>", text)
    for label, pattern in PATTERNS:
        for m in pattern.finditer(text):
            removed.append(m.group(0))
        text = pattern.sub(label, text)
    return text, removed


def check_text(text):
    if len(text) > MAX_TEXT:
        raise LessonError("refused: a lesson is one short line (at most %d characters)" % MAX_TEXT)
    real = [w for w in re.sub(r"<[a-z]+>", " ", text).split() if re.search(r"[A-Za-z]", w)]
    if len(real) < 3:
        raise LessonError("refused: too little left after stripping private details: %r" % text)
    if INSTRUMENT.search(text) and CHANGE.search(text) and not NEGATION.search(text):
        raise LessonError("refused: a lesson never changes the checker, its tests or answer keys: %r" % text)


def _path(folder, skill):
    if skill not in SKILLS:
        raise LessonError("unknown skill %r; one of %s" % (skill, ", ".join(SKILLS)))
    return os.path.join(folder, skill + ".txt")


def _read_lines(path):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip() and not ln.startswith("#")]


def load_lessons(folder, skill):
    out = []
    for ln in _read_lines(_path(folder, skill)):
        m = LINE.match(ln)
        if m:
            out.append({"time": m.group(1), "tag": m.group(2), "kind": m.group(3), "text": m.group(4)})
    return out


def load_rules(folder):
    out = []
    for ln in _read_lines(os.path.join(folder, FIRM)):
        m = RULE.match(ln)
        if m:
            out.append({"date": m.group(1), "scope": m.group(2), "text": m.group(3), "from": m.group(4)})
    return out


def load_declined(folder, skill):
    ids = set()
    for ln in _read_lines(os.path.join(folder, DECLINED)):
        m = re.match(r"^\d{4}-\d\d-\d\d (rhino-[a-z]+): ([0-9a-f]{6})\b", ln)
        if m and m.group(1) == skill:
            ids.add(m.group(2))
    return ids


def clusters(lessons):
    """Group repeats: the same lesson in other words, counted once per run."""
    groups = []
    for les in lessons:
        for g in groups:
            if similar(g["text"], les["text"]):
                g["runs"].add(les["time"])
                g["tags"].add(les["tag"])
                g["kinds"].add(les["kind"])
                if les["tag"] == "U":
                    g["ukinds"].add(les["kind"])
                if les["time"] >= g["last"]:
                    g["last"], g["text"], g["tag"], g["kind"] = les["time"], les["text"], les["tag"], les["kind"]
                break
        else:
            groups.append({"id": lesson_id(les["text"]), "text": les["text"], "tag": les["tag"], "kind": les["kind"],
                           "tags": {les["tag"]}, "kinds": {les["kind"]}, "runs": {les["time"]}, "last": les["time"],
                           "ukinds": {les["kind"]} if les["tag"] == "U" else set()})
    for g in groups:
        g["count"] = len(g["runs"])
    return sorted(groups, key=lambda g: g["last"], reverse=True)


def offerable(folder, skill):
    firm = {r["from"] for r in load_rules(folder) if r["from"]} | load_declined(folder, skill)
    firm_text = [r["text"] for r in load_rules(folder) if r["scope"] in (skill, "all")]
    out = []
    for g in clusters(load_lessons(folder, skill)):
        if g["id"] in firm or any(similar(g["text"], t) for t in firm_text):
            continue
        if g["ukinds"] & set(KINDS):   # a [U] lesson that declared practice or preference
            out.append(g)
    return out


def do_read(folder, skill):
    rules = [r for r in load_rules(folder) if r["scope"] in (skill, "all")]
    groups = clusters(load_lessons(folder, skill))
    lines = ["LESSONS %s: %d firm rules, %d lessons (%s)" % (skill, len(rules), len(groups), folder)]
    if rules:
        lines.append("Firm rules (the user agreed to these; follow them):")
        lines += ["- %s" % r["text"] for r in rules]
    if groups:
        lines.append("Lessons from earlier runs on this machine (apply where they fit; name any you apply in the report):")
        for g in groups[:MAX_READ]:
            note = "unconfirmed" if g["tags"] == {"J"} and g["count"] < 2 else ""
            seen = "seen in %d runs" % g["count"] if g["count"] > 1 else ""
            extra = ", ".join(x for x in (seen, note) if x)
            kind = "%s: " % g["kind"] if g["kind"] else ""
            if not g["kind"]:
                extra = ", ".join(x for x in (extra, "no kind: read only, never promoted") if x)
            lines.append("- [%s] %s%s%s" % (g["tag"], kind, g["text"], " (%s)" % extra if extra else ""))
        if len(groups) > MAX_READ:
            lines.append("- ... %d older lessons not shown" % (len(groups) - MAX_READ))
    if not rules and not groups:
        lines.append("No lessons yet.")
    return "\n".join(lines)


def do_write(folder, skill, lessons, private=(), now=None):
    if not isinstance(lessons, list):
        raise LessonError("AS_LESSONS is a list of {tag, text}")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    before = clusters(load_lessons(folder, skill))
    keep, report, seen = [], [], []
    for item in lessons:
        tag = str(item.get("tag", "")).strip("[] ").upper()
        if tag not in TAGS:
            raise LessonError("tag %r is not one of U, F, M, J" % item.get("tag"))
        kind = str(item.get("kind", "")).strip().lower()
        if kind not in KINDS:
            raise LessonError("refused: every lesson declares kind 'practice' (modeling practice) or 'preference' "
                              "(the user's own, as the user stated it); got %r. A design, architectural or engineering "
                              "rule you inferred is not saved: mention it to the user instead" % item.get("kind"))
        text, removed = strip_private(item.get("text", ""), private, bool(item.get("user_wrote")))
        check_text(text)
        if kind == "preference":
            said, more = strip_private(item.get("user_said", ""), private, bool(item.get("user_wrote")))
            if tag != "U" or not said.strip():
                raise LessonError("refused: a preference is the user's own: tag U and user_said, what the user said. "
                                  "Something you inferred is not a preference: mention it to the user instead")
            if len(said) > MAX_SAID:
                raise LessonError("refused: user_said is at most %d characters" % MAX_SAID)
            removed += more
            text = "%s (user said: %s)" % (text, said.replace("\n", " "))
        if any(similar(text, s) for s in seen):
            continue
        seen.append(text)
        repeat = next((g for g in before if similar(g["text"], text)), None)
        keep.append("%s [%s] %s: %s" % (stamp, tag, kind, text))
        note = " (repeats %s, now %d runs)" % (repeat["id"], repeat["count"] + 1) if repeat else ""
        report.append("- [%s] %s: %s%s%s" % (tag, kind, text, note, " - stripped %d private detail(s)" % len(removed) if removed else ""))
    if not keep:
        return "LESSONS %s: nothing to write" % skill
    os.makedirs(folder, exist_ok=True)
    path = _path(folder, skill)
    new = not os.path.isfile(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:
            f.write(HEADERS["lessons"].format(skill=skill))
        f.write("\n".join(keep) + "\n")
    offer = offerable(folder, skill)
    tail = ("%d can be offered as firm rules: run AS_MODE offer and ask the user with ask_user" % len(offer)
            if offer else "none to offer as firm rules: ask nothing")
    return "\n".join(["LESSONS %s: wrote %d to %s" % (skill, len(keep), path)] + report + [tail])


def do_offer(folder, skill):
    offer = offerable(folder, skill)
    if not offer:
        return "OFFER %s: none (only the user's own corrections with a kind qualify); ask nothing" % skill
    lines = ["OFFER %s: candidates below, from the user's own corrections. Drop any that is about a tool, "
             "a script or a check, or that a firm rule already covers. Ask about the rest in one ask_user "
             "question: each option is the rule in plain words an architect would recognise (no id, no tag), "
             "plus 'None, keep them as lessons'. Write none without a yes; pass the chosen ids with the wording shown, "
             "and every candidate the user did not choose as declined, so it is not asked again." % skill]
    for g in offer:
        lines.append("- %s %s" % (g["id"], g["text"]))
    return "\n".join(lines)


def do_promote(folder, skill, promote, now=None):
    promote = promote or {}
    if promote.get("confirmed") is not True or not str(promote.get("answer", "")).strip():
        raise LessonError("refused: ask the user with ask_user first, then pass confirmed: true and their answer")
    if promote.get("scope", "skill") not in ("skill", "all"):
        raise LessonError("scope is 'skill' or 'all'")
    scope = skill if promote.get("scope", "skill") == "skill" else "all"
    offer = {g["id"]: g for g in offerable(folder, skill)}
    ids = list(promote.get("ids") or [])
    declined = list(promote.get("declined") or [])
    if not ids and not declined:
        raise LessonError("no ids to promote or decline")
    missing = [i for i in ids + declined if i not in offer]
    legacy = [g["id"] for g in clusters(load_lessons(folder, skill)) if g["id"] in missing and not (g["ukinds"] & set(KINDS)) and "U" in g["tags"]]
    if legacy:
        raise LessonError("refused: %s has no kind (written before kinds); add 'practice: ' or 'preference: ' after its tag "
                          "in the lessons file before it can be promoted" % ", ".join(legacy))
    if missing:
        raise LessonError("refused: not offered for %s: %s (run AS_MODE offer)" % (skill, ", ".join(missing)))
    if set(ids) & set(declined):
        raise LessonError("an id is either promoted or declined, not both")
    day = time.strftime("%Y-%m-%d", time.gmtime(now))
    if declined:
        dpath = os.path.join(folder, DECLINED)
        dnew = not os.path.isfile(dpath)
        os.makedirs(folder, exist_ok=True)
        with open(dpath, "a", encoding="utf-8") as f:
            if dnew:
                f.write(HEADERS["declined"])
            for i in declined:
                f.write("%s %s: %s %s\n" % (day, skill, i, offer[i]["text"]))
    if not ids:
        return "PROMOTE %s: none promoted; %d declined, not offered again (%s)" % (skill, len(declined), os.path.join(folder, DECLINED))
    wording = promote.get("wording") or {}
    if not isinstance(wording, dict) or any(k not in ids for k in wording):
        raise LessonError("wording maps promoted ids to the rule as the user saw it")
    texts = {}
    for i in ids:
        if i in wording:
            text, _ = strip_private(wording[i], (), False)
            check_text(text)
            texts[i] = text
        else:
            texts[i] = offer[i]["text"]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, FIRM)
    new = not os.path.isfile(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:
            f.write(HEADERS["firm"])
        for i in ids:
            f.write("%s %s: %s (from %s)\n" % (day, scope, texts[i], i))
    return "\n".join(["PROMOTE %s: %d firm rule(s) written to %s" % (skill, len(ids), path)]
                     + ["- %s" % texts[i] for i in ids])


def run(mode, skill, folder, lessons=None, private=(), promote=None, now=None):
    if skill not in SKILLS:
        raise LessonError("unknown skill %r; one of %s" % (skill, ", ".join(SKILLS)))
    if mode == "read":
        return do_read(folder, skill)
    if mode == "write":
        return do_write(folder, skill, lessons or [], private, now)
    if mode == "offer":
        return do_offer(folder, skill)
    if mode == "promote":
        return do_promote(folder, skill, promote, now)
    raise LessonError("AS_MODE is read, write, offer or promote")


def _from_globals(g):
    try:
        folder = resolve_dir(g.get("AS_LESSONS_DIR"), g.get("AS_SCRIPT_FILE"))
        private = list(g.get("AS_PRIVATE") or [])
        doc = g.get("__rhino_doc__")
        for attr in ("Name", "Path"):
            value = getattr(doc, attr, None) if doc is not None else None
            if value:
                private.append(str(value))
                stem = os.path.splitext(os.path.basename(str(value)))[0]
                if len(stem) >= 4:
                    private.append(stem)
        print(run(g.get("AS_MODE", "read"), g.get("AS_SKILL"), folder, g.get("AS_LESSONS"), private,
                  g.get("AS_PROMOTE")))
    except LessonError as e:
        print("LESSONS ERROR: %s" % e)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Local lessons for the as-rhino skills")
    ap.add_argument("mode", choices=("read", "write", "offer", "promote"))
    ap.add_argument("--skill", required=True)
    ap.add_argument("--dir")
    ap.add_argument("--json", help="file with lessons, private and promote")
    a = ap.parse_args(argv)
    data = {}
    if a.json:
        with open(a.json, encoding="utf-8") as f:
            data = json.load(f)
    try:
        folder = resolve_dir(a.dir, __file__)
        print(run(a.mode, a.skill, folder, data.get("lessons"), data.get("private") or (), data.get("promote")))
    except LessonError as e:
        print("LESSONS ERROR: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
elif "AS_MODE" in globals() and "AS_SCRIPT_FILE" in globals():
    _from_globals(globals())
