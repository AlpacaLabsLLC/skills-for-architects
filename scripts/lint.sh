#!/usr/bin/env bash
# Architecture Studio repo lint — flat single-plugin layout.
#
# Layout assumptions (v1.3.0 restructure):
#   skills/<name>/SKILL.md + README.md   — all skills, flat, one dir each
#   agents/<name>.md                     — subagents (agents/README.md is the index)
#   hooks/<name>.sh + hooks/hooks.json   — event-driven automations
#   .claude-plugin/plugin.json           — the one plugin manifest
#   .claude-plugin/marketplace.json      — single-entry marketplace, source "./"
#
# All counts are derived from the tree — never hardcoded here.
# Runs the full set of structural checks. Exits non-zero if any fail.
#
# Locally, missing optional tools (shellcheck, jq, PyYAML) downgrade their
# checks to a warning. In CI (CI=true) a missing tool fails the run hard —
# CI is the one place these checks are guaranteed, so they must never
# silently stop running there (ALPA-366).

set -uo pipefail

cd "$(dirname "$0")/.." || exit 1

FAIL=0
fail_check() { echo "  ✗ $1"; FAIL=1; }
pass_check() { echo "  ✓ $1"; }

# Warn-and-skip locally; hard-fail in CI.
skip_or_fail() {
  if [ "${CI:-}" = "true" ]; then
    fail_check "$1 not installed — required in CI (install step missing from lint.yml?)"
  else
    echo "  ! $1 not installed; skipping locally — CI enforces this check"
  fi
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ python3 is required to run this lint" >&2
  exit 1
fi

# 1. No .DS_Store tracked
echo "→ no .DS_Store tracked"
DSSTORE=$(git ls-files | grep '\.DS_Store$' || true)
if [ -n "$DSSTORE" ]; then
  fail_check "tracked .DS_Store files:"
  echo "$DSSTORE" | awk '{ print "      " $0 }'
else
  pass_check "none"
fi

# 2. JSON validity
echo "→ JSON validity"
if command -v jq >/dev/null 2>&1; then
  JSON_BAD=0
  JSON_TOTAL=0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    JSON_TOTAL=$((JSON_TOTAL + 1))
    if ! jq empty "$f" >/dev/null 2>&1; then
      fail_check "invalid JSON: $f"
      JSON_BAD=$((JSON_BAD + 1))
    fi
  done <<< "$(git ls-files '*.json')"
  [ "$JSON_BAD" -eq 0 ] && pass_check "$JSON_TOTAL files"
else
  skip_or_fail "jq"
fi

# 3. SKILL.md frontmatter
echo "→ SKILL.md frontmatter"
python3 - <<'PYEOF'
import os, sys, pathlib, subprocess
try:
    import yaml
except ImportError:
    if os.environ.get('CI') == 'true':
        print("  ✗ PyYAML not installed — required in CI (install step missing from lint.yml?)")
        sys.exit(1)
    print("  ! PyYAML not installed; skipping locally (pip install pyyaml) — CI enforces this check")
    sys.exit(2)

files = subprocess.check_output(['git', 'ls-files', '*SKILL.md']).decode().strip().split('\n')
errors = 0
for f in files:
    text = pathlib.Path(f).read_text()
    if not text.startswith('---\n'):
        print(f"  ✗ {f}: missing frontmatter delimiter")
        errors += 1
        continue
    end = text.find('\n---\n', 4)
    if end < 0:
        print(f"  ✗ {f}: unterminated frontmatter")
        errors += 1
        continue
    try:
        meta = yaml.safe_load(text[4:end])
    except Exception as e:
        print(f"  ✗ {f}: YAML parse error: {e}")
        errors += 1
        continue
    if not isinstance(meta, dict):
        print(f"  ✗ {f}: frontmatter is not a mapping")
        errors += 1
        continue
    for key in ('name', 'description'):
        if key not in meta:
            print(f"  ✗ {f}: missing required key '{key}'")
            errors += 1
if errors:
    sys.exit(1)
print(f"  ✓ {len(files)} files")
PYEOF
RC=$?
[ "$RC" -eq 1 ] && FAIL=1

# 4. Skill directory completeness
echo "→ skill directory completeness"
python3 - <<'PYEOF'
import sys, pathlib
errors = 0
skills = sorted(p for p in pathlib.Path('skills').iterdir()
                if p.is_dir() and not p.name.startswith('.'))
for s in skills:
    for required in ('SKILL.md', 'README.md'):
        if not (s / required).is_file():
            print(f"  ✗ {s}: missing {required}")
            errors += 1
if errors:
    sys.exit(1)
print(f"  ✓ {len(skills)} skill dirs, each with SKILL.md + README.md")
PYEOF
RC=$?
[ "$RC" -ne 0 ] && FAIL=1

# 5. Count consistency (derived from tree; a regex that matches nothing is a
#    FAILURE, not a silent pass — ALPA-365 #4)
echo "→ count consistency"
python3 - <<'PYEOF'
import sys, re, json, pathlib

errors = []

skill_dirs = sorted(p.name for p in pathlib.Path('skills').iterdir()
                    if p.is_dir() and not p.name.startswith('.'))
skill_count = len(skill_dirs)
agent_count = sum(1 for p in pathlib.Path('agents').glob('*.md')
                  if p.name != 'README.md')
rule_count = sum(1 for p in pathlib.Path('rules').glob('*.md')
                 if p.name != 'README.md')
hook_count = len(list(pathlib.Path('hooks').glob('*.sh')))

readme = pathlib.Path('README.md').read_text()

# Every "N skills" / "N agents" / "N rules" / "N hooks" claim in the root
# README must match the tree, and each kind must be claimed at least once.
for label, actual in (('skills', skill_count), ('agents', agent_count),
                      ('rules', rule_count), ('hooks', hook_count)):
    claims = re.findall(rf'\b(\d+) {label}\b', readme)
    if not claims:
        errors.append(f"README never states a '{label}' count (expected {actual})")
    for c in claims:
        if int(c) != actual:
            errors.append(f"README claims {c} {label}, actual {actual}")

# Skill catalog rows: [`/name`](./skills/dir). Every skill dir needs exactly
# one row; every row must point at a real dir; slash name must equal dir name.
rows = re.findall(r'\[`/([a-z0-9-]+)`\]\(\./skills/([a-z0-9-]+)\)', readme)
if not rows:
    errors.append("README skill catalog regex matched no rows — table missing or reformatted")
else:
    linked = [d for _, d in rows]
    for slash, d in rows:
        if slash != d:
            errors.append(f"README row `/{slash}` links to ./skills/{d} — slash name must equal dir name")
        if d not in skill_dirs:
            errors.append(f"README row `/{slash}` points to missing dir skills/{d}")
    for d in skill_dirs:
        if d not in linked:
            errors.append(f"skills/{d} has no row in the README skill catalog")
    for d in sorted(set(x for x in linked if linked.count(x) > 1)):
        errors.append(f"skills/{d} appears {linked.count(d)} times in the README skill catalog")

# Skill Groups table: per-group counts must sum to the real total.
group_counts = re.findall(r'^\|\s*\[[^\]]+\]\(#[a-z-]+\)\s*\|\s*(\d+)\s*\|', readme, re.MULTILINE)
if not group_counts:
    errors.append("README Skill Groups table regex matched no rows")
elif sum(map(int, group_counts)) != skill_count:
    errors.append(f"README Skill Groups counts sum to {sum(map(int, group_counts))}, actual {skill_count}")

# Help-menu skill headline.
menu = pathlib.Path('skills/skills/SKILL.md').read_text()
m = re.search(r'\*\*(\d+) skills, (\d+) agents\*\*', menu)
if not m:
    errors.append("skills/skills/SKILL.md missing '**N skills, M agents**' headline")
elif (int(m.group(1)), int(m.group(2))) != (skill_count, agent_count):
    errors.append(f"skills/skills/SKILL.md claims {m.group(1)} skills, {m.group(2)} agents; "
                  f"actual {skill_count} skills, {agent_count} agents")

# Root plugin.json + single-entry marketplace.json.
plugin = json.loads(pathlib.Path('.claude-plugin/plugin.json').read_text())
mp = json.loads(pathlib.Path('.claude-plugin/marketplace.json').read_text())

for key in ('name', 'version', 'description'):
    if not plugin.get(key):
        errors.append(f"plugin.json missing '{key}'")
if not re.fullmatch(r'\d+\.\d+\.\d+', plugin.get('version', '')):
    errors.append(f"plugin.json version '{plugin.get('version')}' is not semver X.Y.Z")
if not mp.get('metadata', {}).get('version'):
    errors.append("marketplace.json missing metadata.version")

entries = mp.get('plugins', [])
if len(entries) != 1:
    errors.append(f"marketplace.json must list exactly 1 plugin (flat layout), found {len(entries)}")
else:
    entry = entries[0]
    if entry.get('name') != plugin.get('name'):
        errors.append(f"marketplace entry name '{entry.get('name')}' != plugin.json name '{plugin.get('name')}'")
    if entry.get('source') != './':
        errors.append(f"marketplace entry source must be './', found '{entry.get('source')}'")

# Manifest descriptions state skill/agent counts — keep them honest too.
for label, text in (('plugin.json', plugin.get('description', '')),
                    ('marketplace.json', entries[0].get('description', '') if entries else '')):
    m = re.search(r'(\d+) skills and (\d+) agents', text)
    if not m:
        errors.append(f"{label} description missing 'N skills and M agents'")
    elif (int(m.group(1)), int(m.group(2))) != (skill_count, agent_count):
        errors.append(f"{label} description claims {m.group(1)} skills, {m.group(2)} agents; "
                      f"actual {skill_count}, {agent_count}")

if errors:
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
print(f"  ✓ {skill_count} skills, {agent_count} agents, {rule_count} rules, "
      f"{hook_count} hooks — counts consistent")
PYEOF
RC=$?
[ "$RC" -ne 0 ] && FAIL=1

# 6. Internal markdown links
echo "→ internal markdown links"
python3 - <<'PYEOF'
import sys, re, pathlib, subprocess
md_files = subprocess.check_output(['git', 'ls-files', '*.md']).decode().strip().split('\n')
link_re = re.compile(r'\]\((?!https?://|mailto:|#)([^)\s]+)(?:\s+"[^"]*")?\)')
errors = 0
for f in md_files:
    p = pathlib.Path(f)
    text = p.read_text()
    base = p.parent
    for m in link_re.finditer(text):
        target = m.group(1).split('#')[0]
        if not target:
            continue
        resolved = (base / target).resolve()
        if not resolved.exists():
            print(f"  ✗ {f}: broken link → {target}")
            errors += 1
if errors:
    sys.exit(1)
print(f"  ✓ {len(md_files)} markdown files scanned")
PYEOF
RC=$?
[ "$RC" -ne 0 ] && FAIL=1

# 7. No ~/ data paths in SKILL.md bodies (regression guard, ALPA-365 #1:
#    skills once hardcoded ~/Documents and ~/.claude paths that broke on
#    other machines). skills/learn is exempt — it TEACHES where personal
#    skills live (~/.claude/skills), which is instructional content, not a
#    data path the skill reads or writes.
echo "→ no ~/ paths in SKILL.md bodies"
TILDE_HITS=$(grep -n -e '[~]/\.claude' -e '[~]/Documents' skills/*/SKILL.md 2>/dev/null | grep -v '^skills/learn/' || true)
if [ -n "$TILDE_HITS" ]; then
  fail_check "tilde (~/) paths found in SKILL.md bodies:"
  echo "$TILDE_HITS" | awk '{ print "      " $0 }'
else
  pass_check "none (skills/learn exempt by design)"
fi

# 8. Slash-command resolution (regression guard, ALPA-365 #2: docs referenced
#    /architect, /history and skills-menu after renames). Every backticked
#    /name in a README.md, SKILL.md, or agents/*.md must resolve to a real
#    skills/<name>/ dir. skills/learn is exempt — it references skills the
#    learner builds in the sandbox (/minutes, /tasks, ...) plus Claude Code
#    built-ins, none of which ship in this repo.
echo "→ slash-command resolution"
python3 - <<'PYEOF'
import sys, re, pathlib, subprocess

# Claude Code built-in commands that legitimately appear in our docs.
BUILTINS = {'hooks', 'plugin', 'config', 'clear', 'help', 'mcp', 'init', 'agents'}

files = [f for f in subprocess.check_output(['git', 'ls-files']).decode().split('\n')
         if f and not f.startswith('skills/learn/')
         and (f.endswith('/README.md') or f == 'README.md'
              or f.endswith('SKILL.md') or re.fullmatch(r'agents/[^/]+\.md', f))]
skill_dirs = {p.name for p in pathlib.Path('skills').iterdir() if p.is_dir()}
slash_re = re.compile(r'`(/[a-z][a-z0-9-]*)')
errors = 0
for f in files:
    text = pathlib.Path(f).read_text()
    for i, line in enumerate(text.split('\n'), 1):
        for m in slash_re.finditer(line):
            name = m.group(1)[1:]
            if name in skill_dirs or name in BUILTINS:
                continue
            print(f"  ✗ {f}:{i}: `/{name}` does not resolve to skills/{name}/")
            errors += 1
if errors:
    sys.exit(1)
print(f"  ✓ {len(files)} docs scanned, all slash commands resolve")
PYEOF
RC=$?
[ "$RC" -ne 0 ] && FAIL=1

# 9. Disclaimer marker instruction in regulatory skills (regression guard,
#    ALPA-365 #3: the disclaimer pipeline is marker-driven — a regulatory
#    skill that never emits the marker silently escapes the hook). This list
#    mirrors the skills wired in the disclaimer-pipeline issue (ALPA-361);
#    grow it when a new regulatory skill ships.
echo "→ disclaimer marker in regulatory skills"
REGULATORY_SKILLS="
nyc-landmarks
nyc-dob-permits
nyc-dob-violations
nyc-acris
nyc-hpd
nyc-bsa
nyc-property-report
zoning-analysis-nyc
zoning-envelope
occupancy-calculator
epd-to-spec
"
MARKER='architecture-studio:requires-disclaimer'
MARKER_MISSING=0
MARKER_TOTAL=0
while IFS= read -r s; do
  [ -z "$s" ] && continue
  MARKER_TOTAL=$((MARKER_TOTAL + 1))
  if [ ! -f "skills/$s/SKILL.md" ]; then
    fail_check "regulatory skill skills/$s/SKILL.md not found (stale list in lint.sh?)"
    MARKER_MISSING=$((MARKER_MISSING + 1))
  elif ! grep -q "$MARKER" "skills/$s/SKILL.md"; then
    fail_check "skills/$s/SKILL.md missing '$MARKER' marker instruction"
    MARKER_MISSING=$((MARKER_MISSING + 1))
  fi
done <<< "$REGULATORY_SKILLS"
[ "$MARKER_MISSING" -eq 0 ] && pass_check "$MARKER_TOTAL regulatory skills carry the marker"

# 10. Referenced-file existence (regression guard, ALPA-365 #5: SKILL.md
#     bodies referenced support files that had been moved or deleted). Checks
#     backticked relative paths whose first segment is a real directory next
#     to the skill (or at repo root) — output-file templates (./report.md,
#     [slug] placeholders) are not existence claims and are skipped.
echo "→ referenced files exist"
python3 - <<'PYEOF'
import sys, re, pathlib, subprocess
files = subprocess.check_output(['git', 'ls-files', 'skills/*SKILL.md']).decode().split()
tok_re = re.compile(r'`([^`\s]+)`')
root = pathlib.Path('.')
errors = 0
checked = 0
for f in files:
    skill_dir = pathlib.Path(f).parent
    text = pathlib.Path(f).read_text()
    for m in tok_re.finditer(text):
        t = m.group(1)
        if t.startswith('${CLAUDE_PLUGIN_ROOT}/'):
            rel = t[len('${CLAUDE_PLUGIN_ROOT}/'):]
            checked += 1
            if not (root / rel).exists():
                print(f"  ✗ {f}: references missing file {t}")
                errors += 1
            continue
        # Placeholders and non-path tokens are not existence claims.
        if '/' not in t or t.startswith(('/', '~', '.', 'http', '#')):
            continue
        if any(c in t for c in '[]*{}(') or 'YYYY' in t:
            continue
        first = t.split('/')[0]
        for base in (skill_dir, root):
            if (base / first).is_dir():
                checked += 1
                if not (base / t.rstrip('/')).exists():
                    print(f"  ✗ {f}: references missing file {t}")
                    errors += 1
                break
if errors:
    sys.exit(1)
print(f"  ✓ {checked} referenced paths exist")
PYEOF
RC=$?
[ "$RC" -ne 0 ] && FAIL=1

# 11. Shellcheck on hook and repo scripts
echo "→ shellcheck on hooks/*.sh and scripts/*.sh"
if command -v shellcheck >/dev/null 2>&1; then
  if shellcheck hooks/*.sh scripts/*.sh; then
    pass_check "$(find hooks scripts -maxdepth 1 -name '*.sh' | wc -l | tr -d ' ') scripts"
  else
    fail_check "shellcheck issues"
  fi
else
  skip_or_fail "shellcheck"
fi

echo
if [ "$FAIL" -ne 0 ]; then
  echo "lint failed"
  exit 1
fi
echo "all checks passed"
