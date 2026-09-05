#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

SCRIPT="skills/project/scripts/project-workspace.sh"
[ -x "$SCRIPT" ] || { echo "missing executable project helper" >&2; exit 1; }

ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT"' EXIT

PROJECT="$ROOT/260901-SMI-MUSEUM-EXPANSION"
"$SCRIPT" init "$PROJECT" "Museum Expansion" 260901-SMI-MUSEUM-EXPANSION client active SMI "Smith Institution"

for file in PROJECT.md CLAUDE.md AGENTS.md TASKS.md TIMELOG.md; do
  [ -f "$PROJECT/$file" ] || { echo "missing project file: $file" >&2; exit 1; }
done
for dir in decisions meetings site-reports docs/plans .claude/skills .agents/skills; do
  [ -d "$PROJECT/$dir" ] || { echo "missing project directory: $dir" >&2; exit 1; }
done
grep -q 'decisions/' "$PROJECT/PROJECT.md"
grep -Fq '| Format version | 3 |' "$PROJECT/PROJECT.md"
grep -Fq '| Project ID | 260901-SMI-MUSEUM-EXPANSION |' "$PROJECT/PROJECT.md"
grep -Fq '| Project | Museum Expansion |' "$PROJECT/PROJECT.md"
grep -Fq '| Type | client |' "$PROJECT/PROJECT.md"
grep -Fq '| Status | active |' "$PROJECT/PROJECT.md"
grep -Fq '| Client code | SMI |' "$PROJECT/PROJECT.md"
grep -Fq '| Client | Smith Institution |' "$PROJECT/PROJECT.md"
! grep -q '^## Decisions$' "$PROJECT/PROJECT.md"
! grep -q '^## \(Site\|Zoning\|Program\|Code\)$' "$PROJECT/PROJECT.md"
grep -Fq 'Maintained by the project skill and the project team.' "$PROJECT/PROJECT.md"
if grep -Fq '/as:' "$PROJECT/PROJECT.md"; then
  echo "generated project record contains a host-specific slash command" >&2
  exit 1
fi
grep -q 'Read `PROJECT.md` before project work' "$PROJECT/AGENTS.md"
grep -Fq 'Before making scope commitments, read `agreement/AGREEMENT.md` when it exists.' "$PROJECT/AGENTS.md"
grep -Fq 'For commercial work, discover the project-local `proposals/`, `agreement/`, and `INVOICES.md` records read-only before acting.' "$PROJECT/AGENTS.md"
grep -Fq 'Project-specific Codex skills live in `.agents/skills/`' "$PROJECT/AGENTS.md"
grep -Fxq '@AGENTS.md' "$PROJECT/CLAUDE.md"
grep -Fxq '## Claude Code' "$PROJECT/CLAUDE.md"
if grep -Fq 'Read `PROJECT.md` before project work' "$PROJECT/CLAUDE.md"; then
  echo "generated CLAUDE.md duplicates shared AGENTS.md instructions" >&2
  exit 1
fi

INTERNAL_PROJECT="$ROOT/260901-ALP-ARCHITECTURE-STUDIO"
"$SCRIPT" init "$INTERNAL_PROJECT" "Architecture Studio" 260901-ALP-ARCHITECTURE-STUDIO internal active ALP —
grep -Fq '| Type | internal |' "$INTERNAL_PROJECT/PROJECT.md"
grep -Fq '| Client code | ALP |' "$INTERNAL_PROJECT/PROJECT.md"
grep -Fq '| Client | — |' "$INTERNAL_PROJECT/PROJECT.md"
! grep -q '^## \(Site\|Zoning\|Program\|Code\)$' "$INTERNAL_PROJECT/PROJECT.md"

FIRM_PROJECT="$ROOT/Client Work/Museum Expansion"
"$SCRIPT" init "$FIRM_PROJECT" "Museum Expansion — Phase 2" firm-042 client active A1P "Smith Institution"
grep -Fq '| Project ID | firm-042 |' "$FIRM_PROJECT/PROJECT.md"
grep -Fq '| Project | Museum Expansion — Phase 2 |' "$FIRM_PROJECT/PROJECT.md"
grep -Fq '| Client code | A1P |' "$FIRM_PROJECT/PROJECT.md"

PORTFOLIO_PROJECT="$ROOT/260901-NYC-LIBRARY"
"$SCRIPT" init "$PORTFOLIO_PROJECT" "Library" 260901-NYC-LIBRARY client prospective NYC "New York City" portfolio
[ ! -f "$PORTFOLIO_PROJECT/TASKS.md" ]
grep -Fq 'resolved by the tasklist skill from this project and the studio skill that owns it' "$PORTFOLIO_PROJECT/PROJECT.md"
grep -Fq 'resolved by the tasklist skill from this project and the studio skill that owns it' "$PROJECT/PROJECT.md"

if "$SCRIPT" init "$PROJECT" "Museum Expansion" 260901-SMI-MUSEUM-EXPANSION client active SMI "Smith Institution"; then
  echo "project overwrite unexpectedly succeeded" >&2
  exit 1
fi

if "$SCRIPT" init "$PROJECT/nested-project" "Nested Project" nested-001 internal active INT —; then
  echo "nested project unexpectedly succeeded" >&2
  exit 1
fi

SYMLINK_TARGET="$ROOT/symlink-target"
SYMLINK_PROJECT="$ROOT/symlink-project"
mkdir -p "$SYMLINK_TARGET"
ln -s "$SYMLINK_TARGET" "$SYMLINK_PROJECT"
if "$SCRIPT" init "$SYMLINK_PROJECT" "Symlink Project" link-001 internal active INT —; then
  echo "symlinked project target unexpectedly succeeded" >&2
  exit 1
fi

if "$SCRIPT" init "$ROOT/unsafe-id" Invalid 'bad|id' client active SMI "Smith Institution"; then
  echo "project identity containing a reserved table character unexpectedly accepted" >&2
  exit 1
fi

DIFFERENT_FOLDER="$ROOT/user-selected-folder"
"$SCRIPT" init "$DIFFERENT_FOLDER" "Different Folder" 260901-SMI-RIGHT-ID client active SMI "Smith Institution"
grep -Fq '| Project ID | 260901-SMI-RIGHT-ID |' "$DIFFERENT_FOLDER/PROJECT.md"

echo "✓ project helper creates universal v3 bundles without coupling identity, name, code, and directory"
