#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
node "$ROOT/tools/integrations/source-health.mjs" --validate
node --test "$ROOT/tests/source-contracts.test.mjs"
