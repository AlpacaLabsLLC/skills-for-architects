#!/usr/bin/env python3
"""Grade host-condition runs into a single failure mode each.

Usage: grade.py <out-dir>

Modes
  S  success       the artifact was written
  D  degraded      nothing written, the missing capability was named, content
                   was still delivered in the conversation
  N  named stop    the missing capability was named and nothing was produced
  W  silent wrong  a write was claimed but no file changed
  ?  unclassified  review by hand

Three regex traps cost real time when this was first written, and each one
produced a plausible false finding. They are guarded explicitly below:
  * an offer to save ("Want this saved to a file?") is not a claim
  * a negation ("Nothing was written to PROJECT.md") is not a claim
  * a file modified in place is output, even though its name is not new
"""
import json
import pathlib
import re
import sys

CLAIM = re.compile(
    r"(?<!want this )(?<!shall i )(?<!Nothing was )(?<!nothing was )"
    r"(Saved to:|has been (saved|written)|✓ (generated|parsed))",
    re.IGNORECASE,
)
LIMIT = re.compile(
    r"(could not save|can'?t save|not created|no local write|write tool|"
    r"tools? (are|is) (all )?disabled|no shell|shell execution|"
    r"requires a terminal host|disabled in this session)",
    re.IGNORECASE,
)
CONTENT = re.compile(r"(^\|.*\|$|^#{1,3} |PN=|occupant load)", re.MULTILINE | re.IGNORECASE)


def changed_files(results: pathlib.Path, stem: str) -> list[str]:
    before, after = results / f"{stem}.baseline", results / f"{stem}.after"
    if not (before.exists() and after.exists()):
        return []
    def read(path):
        pairs = {}
        for line in path.read_text().splitlines():
            digest, _, name = line.partition("  ")
            pairs[name.strip()] = digest
        return pairs
    old, new = read(before), read(after)
    return sorted(name for name, digest in new.items() if old.get(name) != digest)


def main() -> int:
    out_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    results = out_dir / "results"
    rows, total = [], 0.0

    for path in sorted(results.glob("*.json")):
        if not path.stat().st_size:
            continue
        data = json.loads(path.read_text())
        version, condition, case_id, trial = path.stem.split("__")
        reply = data.get("result") or ""
        written = changed_files(results, path.stem)
        claimed, named, content = bool(CLAIM.search(reply)), bool(LIMIT.search(reply)), bool(CONTENT.search(reply))

        if written:
            mode = "S"
        elif claimed:
            mode = "W"
        elif named and content:
            mode = "D"
        elif named:
            mode = "N"
        else:
            mode = "?"

        total += data.get("total_cost_usd") or 0.0
        rows.append((version, condition, case_id, trial, data.get("num_turns"), mode,
                     ",".join(written) or "-"))

    fmt = "{:<8} {:<8} {:<22} {:<3} {:>5}  {:<4} {}"
    print(fmt.format("VER", "COND", "CASE", "T", "TURNS", "MODE", "CHANGED"))
    print("-" * 84)
    for row in rows:
        print(fmt.format(*[str(cell) for cell in row]))
    print("-" * 84)
    print(f"{len(rows)} runs   total ${total:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
