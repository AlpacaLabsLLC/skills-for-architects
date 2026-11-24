#!/usr/bin/env python3
"""Rhino pointer (Arch Studio): SessionStart hook, run through lib/as-run-python.sh.

The Rhino AI panel cannot load plugin skills, so this adds one short line naming the skill
index in this installed plugin version and the folder the as-rhino skills keep their lessons
in. That folder is Claude Code's plugin data folder (CLAUDE_PLUGIN_DATA), which survives
plugin updates; the panel has no plugin variables, so the line is how a skill finds it.
No input, no network, no writes. Any problem means no output and exit 0, so it can never
block a session.
"""
import json
import os
import re
import sys

LINE = ("Arch Studio: if the user names an as-rhino skill or Arch Studio in Rhino, read %s with "
        "run_python; with a Skill tool, use it instead. Read again after compaction.")
LESSONS = " Their lessons folder: %s."


def data_dir(root, environ):
    """CLAUDE_PLUGIN_DATA, else the same folder derived from a .../plugins/cache/<mkt>/<plugin>/<ver> root."""
    if environ.get("CLAUDE_PLUGIN_DATA"):
        return environ["CLAUDE_PLUGIN_DATA"]
    parts = os.path.normpath(root).split(os.sep)
    if len(parts) < 5 or parts[-5:-3] != ["plugins", "cache"]:
        return None
    ident = re.sub(r"[^A-Za-z0-9_-]", "-", parts[-2] + "@" + parts[-3])
    return os.sep.join(parts[:-5] + ["plugins", "data", ident])


def main():
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index = os.path.join(root, "skills", "as-rhino-index.md")
        if os.path.isfile(index):
            line = LINE % index
            data = data_dir(root, os.environ)
            if data and os.path.isfile(os.path.join(root, "skills", "as-rhino-lessons.py")):
                line += LESSONS % os.path.join(data, "rhino-lessons")
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                     "additionalContext": line}}), flush=True)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
