#!/usr/bin/env bash

# Shared folder-identity primitives. Callers define die() so errors keep the
# owning helper's stable prefix or typed resolver shape.

FOLDER_IDENTITY_FILE=.as-folder.json

folder_identity_valid_id() {
  printf '%s\n' "${1:-}" | grep -Eq '^asf_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
}

folder_identity_valid_kind() {
  case "${1:-}" in
    studio|projects|operations|standards|references|internal|group|project) return 0 ;;
    *) return 1 ;;
  esac
}

folder_identity_new_id() {
  node -e 'process.stdout.write("asf_" + require("crypto").randomUUID())' ||
    die "could not generate a folder identity"
}

folder_identity_parse() {
  local directory=$1
  local config="$directory/$FOLDER_IDENTITY_FILE"
  [ -f "$config" ] && [ ! -L "$config" ] || return 1
  node -e '
    const fs = require("fs");
    try {
      const value = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
      const keys = Object.keys(value).sort().join(",");
      if (keys !== "folder_id,format,kind" || value.format !== 1) process.exit(2);
      if (!/^asf_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(value.folder_id)) process.exit(2);
      if (!/^(studio|projects|operations|standards|references|internal|group|project)$/.test(value.kind)) process.exit(2);
      process.stdout.write(value.folder_id + "\t" + value.kind);
    } catch (_) {
      process.exit(2);
    }
  ' "$config" 2>/dev/null
}

folder_identity_require() {
  local directory=$1
  local expected_kind=${2:-}
  local expected_id=${3:-}
  local parsed folder_id folder_kind
  [ -d "$directory" ] && [ ! -L "$directory" ] || die "managed folder is missing or symlinked: $directory"
  parsed=$(folder_identity_parse "$directory") || die "invalid or missing $FOLDER_IDENTITY_FILE at $directory"
  IFS=$'\t' read -r folder_id folder_kind <<< "$parsed"
  [ -z "$expected_kind" ] || [ "$folder_kind" = "$expected_kind" ] ||
    die "folder kind mismatch at $directory: expected $expected_kind, found $folder_kind"
  [ -z "$expected_id" ] || [ "$folder_id" = "$expected_id" ] ||
    die "folder identity mismatch at $directory: expected $expected_id, found $folder_id"
  printf '%s\n' "$folder_id"
}

folder_identity_ensure() {
  local directory=$1
  local kind=$2
  local requested_id=${3:-}
  local folder_id tmp
  [ -d "$directory" ] && [ ! -L "$directory" ] || die "managed folder is missing or symlinked: $directory"
  folder_identity_valid_kind "$kind" || die "invalid managed folder kind: ${kind:-<empty>}"
  if [ -e "$directory/$FOLDER_IDENTITY_FILE" ] || [ -L "$directory/$FOLDER_IDENTITY_FILE" ]; then
    folder_identity_require "$directory" "$kind" "$requested_id"
    return 0
  fi
  if [ -n "$requested_id" ]; then
    folder_identity_valid_id "$requested_id" || die "invalid folder identity: $requested_id"
    folder_id=$requested_id
  else
    folder_id=$(folder_identity_new_id)
  fi
  tmp=$(mktemp "$directory/.as-folder.XXXXXX")
  if ! printf '{\n  "format": 1,\n  "folder_id": "%s",\n  "kind": "%s"\n}\n' "$folder_id" "$kind" > "$tmp"; then
    rm -f "$tmp"
    die "could not write folder identity at $directory"
  fi
  mv "$tmp" "$directory/$FOLDER_IDENTITY_FILE"
  folder_identity_require "$directory" "$kind" "$folder_id" >/dev/null
  printf '%s\n' "$folder_id"
}

folder_identity_find() {
  local studio=$1
  local requested_id=$2
  local config directory parsed folder_id folder_kind relative content
  folder_identity_valid_id "$requested_id" || return 1
  while IFS= read -r -d '' config; do
    content=$(<"$config") || continue
    case "$content" in *"$requested_id"*) ;; *) continue ;; esac
    directory=${config%/$FOLDER_IDENTITY_FILE}
    parsed=$(folder_identity_parse "$directory") || continue
    IFS=$'\t' read -r folder_id folder_kind <<< "$parsed"
    [ "$folder_id" = "$requested_id" ] || continue
    relative=${directory#"$studio/"}
    [ "$directory" != "$studio" ] || relative=.
    printf '%s\t%s\n' "$relative" "$folder_kind"
  done < <(find "$studio" \
    \( -name .git -o -name .agents -o -name .claude -o -name node_modules -o -name .next -o -name dist -o -name build -o -name '.studio-*' -o -name '.project-*' -o -name '.v3-*' -o -name '.task-*' \) -prune -o \
    -name "$FOLDER_IDENTITY_FILE" -type f -print0 2>/dev/null)
}

folder_identity_resolve() {
  local studio=$1
  local requested_id=$2
  local expected_kind=$3
  local matches count relative folder_kind
  folder_identity_valid_id "$requested_id" || die "invalid folder identity: ${requested_id:-<empty>}"
  matches=$(folder_identity_find "$studio" "$requested_id" || true)
  count=$(printf '%s\n' "$matches" | sed '/^$/d' | wc -l | tr -d ' ')
  [ "$count" -eq 1 ] || die "folder identity $requested_id resolves to $count managed folders"
  IFS=$'\t' read -r relative folder_kind <<< "$matches"
  [ "$folder_kind" = "$expected_kind" ] ||
    die "folder identity $requested_id has kind $folder_kind instead of $expected_kind"
  printf '%s\n' "$relative"
}
