#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
SKILL="skills/skill-maker/SKILL.md"

grep -q 'nearest `STUDIO.md`' "$SKILL"
grep -q '{studio-root}/{host-skill-root}/{name}/' "$SKILL"
grep -q 'explicitly requests a project-only skill' "$SKILL"
grep -q '{host-global-skill-root}/{name}/' "$SKILL"
grep -q '\.agents/skills.*Codex' "$SKILL"
grep -q '\.claude/skills.*Claude Code' "$SKILL"
grep -q 'installed plugin cache is never a private-skill target' "$SKILL"
grep -q 'Catalog detection has highest priority' "$SKILL"
grep -q 'Do not let a nearer project silently override a resolved studio' "$SKILL"
grep -q 'skill_scaffold.validate' "$SKILL"
grep -q '](../../assets/skill-maker-template/SKILL.example.md)' "$SKILL"
grep -q '](../../assets/skill-maker-template/README.md)' "$SKILL"
[ -f skills/skill-maker/scripts/validate_skill.py ]

ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT"' EXIT
mkdir -p "$ROOT/example-skill"
cp assets/skill-maker-template/SKILL.example.md "$ROOT/example-skill/SKILL.md"
cp assets/skill-maker-template/README.md "$ROOT/example-skill/README.md"
sed -i.bak 's/^name:.*/name: example-skill/' "$ROOT/example-skill/SKILL.md"
rm -f "$ROOT/example-skill/SKILL.md.bak"
python3 - "$ROOT/example-skill" <<'PY'
import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location(
    'scaffold', 'skills/skill-maker/scripts/validate_skill.py')
scaffold = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scaffold)
target = Path(sys.argv[1])
request = {'directory': str(target)}
assert scaffold.dispatch('skill_scaffold.validate', request) == {
    'valid': True, 'directory': str(target), 'name': 'example-skill'}
# Calling this module as a CLI has no main entry point and used to verify nothing.
# Exercise the real preserved compatibility validator, including malformed input.
skill = target / 'SKILL.md'
original = skill.read_bytes()
for text in ('no frontmatter\n', '---\nname: other\ndescription: valid\n---\n',
             '---\nname: example-skill\ndescription: valid\n---\nUse ~/private\n'):
    skill.write_text(text)
    try:
        scaffold.dispatch('skill_scaffold.validate', request)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid scaffold accepted')
skill.write_bytes(original)
assert scaffold.dispatch('skill_scaffold.validate', request)['valid'] is True
PY

grep -q 'real initialized Arch Studio workspace' skills/learn/SKILL.md
grep -q 'studio.*`.claude/skills/`' skills/learn/README.md

echo "✓ skill-maker targets catalog, studio, project-only, and global scopes safely"
