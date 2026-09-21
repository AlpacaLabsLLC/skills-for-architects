#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node --test tests/geographic-catalog.test.mjs
node tools/integrations/geographic-catalog.mjs --check
