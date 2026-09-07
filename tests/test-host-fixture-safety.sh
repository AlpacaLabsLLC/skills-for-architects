#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
plugin=$PWD
root=$(mktemp -d)
trap 'rm -rf "$root"' EXIT
fail() { echo "FAIL: $*"; exit 1; }
mkdir "$root/existing"
printf 'keep\n' > "$root/existing/sentinel"
if bash evals/host-conditions/make-fixture.sh "$root/existing" "$plugin" >/dev/null 2>&1; then
  fail "existing fixture target was accepted"
fi
[ "$(cat "$root/existing/sentinel")" = keep ] || fail "existing content changed"
ln -s "$root/existing" "$root/link"
if bash evals/host-conditions/make-fixture.sh "$root/link" "$plugin" >/dev/null 2>&1; then
  fail "symlink target was accepted"
fi
[ -L "$root/link" ] || fail "symlink was replaced"
if bash evals/host-conditions/make-fixture.sh "$root/invalid" "$root/missing-plugin" >/dev/null 2>&1; then
  fail "invalid plugin was accepted"
fi
[ ! -e "$root/invalid" ] || fail "invalid plugin created partial fixture"
bash evals/host-conditions/make-fixture.sh "$root/fresh" "$plugin" >/dev/null
[ -f "$root/fresh/product-library.csv" ] || fail "fresh fixture missing"
echo "fixture safety passed"
