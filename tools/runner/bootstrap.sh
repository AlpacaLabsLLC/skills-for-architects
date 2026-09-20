#!/bin/sh
# Download the pinned installer directly; source code never passes through the model.
set -eu
AS_BOOTSTRAP_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
AS_BOOTSTRAP_TMP=$(mktemp -d)
trap 'rm -rf "$AS_BOOTSTRAP_TMP"' EXIT HUP INT TERM
case "$(uname -m)" in
  arm64) AS_UV_URL='https://github.com/astral-sh/uv/releases/download/0.12.13/uv-aarch64-apple-darwin.tar.gz'; AS_UV_SHA='7e6ddb9316acc00f2296c82ff4d99977870ee34b2f0ddcae9444d714db9364ed' ;;
  x86_64) AS_UV_URL='https://github.com/astral-sh/uv/releases/download/0.12.13/uv-x86_64-apple-darwin.tar.gz'; AS_UV_SHA='5e287ef61cb6a9b61b3a83fef124fd143e400468a7dac794230147a810e17119' ;;
  *) echo 'Unsupported bootstrap architecture' >&2; exit 2 ;;
esac
curl --fail --silent --show-error --location "$AS_UV_URL" --output "$AS_BOOTSTRAP_TMP/uv.tar.gz"
AS_UV_ACTUAL=$(shasum -a 256 "$AS_BOOTSTRAP_TMP/uv.tar.gz" | cut -d ' ' -f 1)
[ "$AS_UV_ACTUAL" = "$AS_UV_SHA" ] || { echo 'Installer hash mismatch' >&2; exit 2; }
tar -xzf "$AS_BOOTSTRAP_TMP/uv.tar.gz" -C "$AS_BOOTSTRAP_TMP"
AS_UV_BIN=$(find "$AS_BOOTSTRAP_TMP" -type f -name uv -print)
"$AS_UV_BIN" run --no-project --python 3.13.7 --managed-python "$AS_BOOTSTRAP_DIR/install.py" --uv "$AS_UV_BIN" "$@"
