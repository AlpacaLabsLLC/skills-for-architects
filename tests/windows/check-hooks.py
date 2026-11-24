"""Windows CI: validate what tests/windows/run-hooks-no-python.sh recorded. python check-hooks.py <output dir>"""
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
repo = Path(__file__).resolve().parents[2]
fails = []


def ok(cond, label, detail=""):
    if not cond:
        fails.append("%s %s" % (label, str(detail)[:600]))


def rec(name):
    return ((out / (name + ".out")).read_text(encoding="utf-8"), (out / (name + ".err")).read_text(encoding="utf-8"),
            int((out / (name + ".rc")).read_text().strip()))


# The commands the run used are the ones hooks.json registers.
registered = json.loads((repo / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
commands = [h["command"] for event in registered.values() for group in event for h in group["hooks"]]
used = (out / "commands.txt").read_text(encoding="utf-8").splitlines()
ok(sorted(commands) == sorted(used), "hooks.json commands match the ones run", (commands, used))

root = (out / "plugin-root.txt").read_text(encoding="utf-8").strip()
root_fwd = root.replace("\\", "/")
tmp_fwd = (out / "tmp-root.txt").read_text(encoding="utf-8").strip().replace("\\", "/")

for name in ("pointer", "pointer-derived"):
    stdout, stderr, rc = rec(name)
    ok(rc == 0 and stderr == "", name + ": exit 0, nothing on stderr", (rc, stderr))
    try:
        line = json.loads(stdout)["hookSpecificOutput"]["additionalContext"]
    except Exception as e:
        fails.append("%s: one JSON line: %s %r" % (name, e, stdout[:300]))
        continue
    index = root_fwd + "/skills/as-rhino-index.md"
    ok("read %s with run_python" % index in line, name + ": names this version's index with forward slashes", line)
    ok(Path(index).is_file() or name == "pointer-broken", name + ": the index exists at that path", index)
    lessons = tmp_fwd + "/home/.claude/plugins/data/as-skills-for-architects/rhino-lessons"
    ok(line.endswith("Their lessons folder: %s." % lessons), name + ": names the lessons folder", line)
    ok("\n" not in line and len(line.encode()) < 2048, name + ": one short line", len(line.encode()))

stdout, stderr, rc = rec("pointer-broken")
ok(rc == 0 and stdout == "" and stderr == "", "pointer-broken: silent, exit 0", (rc, stdout, stderr))

stdout, stderr, rc = rec("welcome")
ok(rc == 0 and json.loads(stdout)["hookSpecificOutput"]["hookEventName"] == "SessionStart", "welcome: JSON line", stdout)
ok("incomplete" not in stdout, "welcome: finds the installed package", stdout)

stdout, stderr, rc = rec("version-off")
ok(rc == 0 and stdout == "" and stderr == "", "version-check off: silent", (rc, stdout, stderr))
stdout, stderr, rc = rec("version-seed")
ok(rc == 0 and stdout == "" and stderr == "", "version-check first run: silent", (rc, stdout, stderr))
ok((out / "version-seed.cache").read_text().strip() == "seeded", "version-check first run: seeds its cache")

stdout, stderr, rc = rec("disclaimer-marked")
try:
    decision = json.loads(stdout)
    ok(rc == 0 and decision["decision"] == "block" and "missing the canonical disclaimer block" in decision["reason"],
       "disclaimer: flags a marked file without the block, from a Windows path", stdout)
except Exception as e:
    fails.append("disclaimer-marked: %s %r %r" % (e, stdout[:300], stderr[:300]))
stdout, stderr, rc = rec("disclaimer-plain")
ok(rc == 0 and stdout == "", "disclaimer: silent on a plain file", (rc, stdout, stderr))

if fails:
    print("FAIL:\n  " + "\n  ".join(fails))
    sys.exit(1)
print("PASS: every hook runs under Git Bash on Windows with no Python, jq or node, as hooks.json registers it")
