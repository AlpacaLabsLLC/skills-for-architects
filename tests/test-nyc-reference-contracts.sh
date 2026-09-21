#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node tests/test-nyc-code-routing.mjs
node --test tests/source-lookup.test.mjs
node tools/integrations/source-health.mjs --validate
