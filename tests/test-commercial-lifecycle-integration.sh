#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(mktemp -d)
trap 'rm -rf "$ROOT"' EXIT
PROJECT="$PWD/skills/project/scripts/project-workspace.sh"
PROPOSAL="$PWD/skills/proposal/scripts/proposal-workspace.sh"
AGREEMENT="$PWD/skills/agreement/scripts/agreement-workspace.sh"
INVOICE="$PWD/skills/invoice/scripts/invoice-ledger.sh"
project="$ROOT/Design Services"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
reject_unchanged() {
  record=$1
  shift
  cp "$record" "$ROOT/before-retry.md"
  if "$@" > "$ROOT/rejection.log" 2>&1; then fail "expected rejection: $*"; fi
  cmp -s "$record" "$ROOT/before-retry.md" || fail "rejected command changed $record"
}

# Explicit synthetic inputs are fixture evidence, not inferred acceptance/payment.
bash "$PROJECT" init "$project" 'Design Services' firm-design-42 client prospective ACM 'Acme Studio' >/dev/null
cp "$project/PROJECT.md" "$ROOT/project-before.md"
cp "$project/.as-folder.json" "$ROOT/folder-before.json"
bash "$PROPOSAL" create "$project" 'Acme Studio' 'Design Services' design-services 2026-09-01 rev-01 >/dev/null
proposal="$project/proposals/2026-09-design-services-proposal-rev-01.md"
bash "$PROPOSAL" send "$proposal" 2026-09-02 Designer 'synthetic issue receipt' >/dev/null
bash "$PROPOSAL" set-status "$proposal" accepted 2026-09-03 Client 'synthetic signed acceptance' >/dev/null
bash "$AGREEMENT" promote "$project" proposals/2026-09-design-services-proposal-rev-01.md 2026-09-03 >/dev/null
cp "$proposal" "$ROOT/issued-source.md"
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" promote "$project" proposals/2026-09-design-services-proposal-rev-01.md 2026-09-03
printf '# SOW 01\n\nSynthetic approved additional study, effective 2026-09-04.\n' > "$project/agreement/sow/sow-01.md"
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" sow-01.md 'Injected\nrow' 2026-09-04
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" sow-01.md $'Injected\nrow' 2026-09-04
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" sow-01.md $'Carriage\rreturn' 2026-09-04
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" sow-01.md $'Tab\tcell' 2026-09-04
printf '# Unsafe filename\n' > "$project/agreement/sow/sow\n01.md"
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" 'sow\n01.md' 'Injected filename' 2026-09-04
bash "$AGREEMENT" record-amendment "$project" sow-01.md 'Additional study' 2026-09-04 >/dev/null
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" sow-01.md 'Additional study' 2026-09-04
grep -Fq 'amendment document already recorded' "$ROOT/rejection.log"
reject_unchanged "$project/agreement/AGREEMENT.md" bash "$AGREEMENT" record-amendment "$project" sow-01.md 'Changed retry summary' 2026-09-05
bash "$AGREEMENT" verify "$project" >/dev/null

bash "$INVOICE" init "$project" 'Design Services' USD monthly 1000.00 10000.00 'synthetic fixture terms' 2026-09-04 >/dev/null
bash "$INVOICE" append "$project" INV-01 2026-09-01 2026-09-30 1000.00 0.00 1000.00 - - draft - >/dev/null
reject_unchanged "$project/INVOICES.md" bash "$INVOICE" append "$project" INV-01 2026-09-01 2026-09-30 1000.00 0.00 1000.00 - - draft -
grep -Fq 'invoice number already recorded' "$ROOT/rejection.log"
reject_unchanged "$project/INVOICES.md" bash "$INVOICE" append "$project" ' INV-01 ' 2026-09-01 2026-09-30 1000.00 0.00 1000.00 - - draft -
bash "$INVOICE" set-lifecycle "$project" I0001 sent 2026-10-01 >/dev/null
bash "$INVOICE" status "$project" | grep -Fq 'outstanding=1000.00'
bash "$INVOICE" set-lifecycle "$project" I0001 paid 2026-10-02 >/dev/null
bash "$INVOICE" status "$project" | grep -Fq 'outstanding=0.00'
# Corrections retain the original identity/history and receive a distinct revision number.
bash "$INVOICE" append "$project" INV-01-R1 2026-09-01 2026-09-30 900.00 0.00 900.00 - - draft 'Corrects I0001 — synthetic correction' >/dev/null
bash "$INVOICE" status "$project" | grep -Fq 'total=900.00'
bash "$INVOICE" set-lifecycle "$project" I0002 void 2026-10-03 >/dev/null
reject_unchanged "$project/INVOICES.md" bash "$INVOICE" append "$project" INV-01-R1 2026-09-01 2026-09-30 900.00 0.00 900.00 - - draft -

cmp -s "$proposal" "$ROOT/issued-source.md" || fail 'commercial handoffs altered issued source'
cmp -s "$project/PROJECT.md" "$ROOT/project-before.md" || fail 'commercial activity changed project facts/status'
cmp -s "$project/.as-folder.json" "$ROOT/folder-before.json" || fail 'commercial activity changed folder identity'
# Detect source tampering without repairing the evidence.
python3 - "$proposal" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
p.write_text(p.read_text().replace('<!-- issued-terms:end -->', 'Tampered terms.\n<!-- issued-terms:end -->'))
PY
reject_unchanged "$proposal" bash "$AGREEMENT" verify "$project"

internal="$ROOT/Internal Research"
bash "$PROJECT" init "$internal" 'Internal Research' firm-internal-17 internal active INT '—' >/dev/null
[ ! -e "$internal/agreement" ] || fail 'internal work required an agreement'
[ ! -e "$internal/INVOICES.md" ] || fail 'internal work inferred billing'
printf '✓ commercial lifecycle preserves project identity, issued terms, retry identity, and invoice history\n'
