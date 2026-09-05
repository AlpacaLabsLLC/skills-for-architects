#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
REGISTRY_PARSER="$SCRIPT_DIR/project-registry.awk"
FOLDER_IDENTITY_SCRIPT="$SCRIPT_DIR/folder-identity.sh"

die() { printf 'invalid\t%s\n' "$*"; exit 2; }
# shellcheck source=folder-identity.sh
. "$FOLDER_IDENTITY_SCRIPT"
trim_field() { awk -F'|' -v key="$2" 'function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s} /^\|/ && trim($2)==key {print trim($3); exit}' "$1"; }
find_up() {
  cursor=$(cd -P -- "$1" && pwd)
  marker=$2
  while :; do
    [ -f "$cursor/$marker" ] && { printf '%s\n' "$cursor"; return; }
    [ "$cursor" = / ] && return 1
    cursor=${cursor%/*}; [ -n "$cursor" ] || cursor=/
  done
}
require_version() {
  version=$(trim_field "$1" "Format version")
  [ "$version" = 3 ] || die "$(basename "$1") format version is ${version:-absent}; version 3 required"
}
valid_identity_text() {
  local value=${1:-}
  [ -n "$value" ] || return 1
  case "$value" in *'|'*|*$'\n'*|*$'\r'*|*$'\t'*) return 1 ;; esac
  [ "${#value}" -le 160 ]
}
valid_project_id() {
  local value=${1:-}
  valid_identity_text "$value" || return 1
  case "$value" in .|..|' '*|*' '|\#|---|:---|---:|:---:) return 1 ;; esac
  return 0
}
safe_relative_path() {
  local path=${1:-}
  case "$path" in ''|/*|.|..|*/) return 1 ;; esac
  case "/$path/" in */../*|*/./*|*//* ) return 1 ;; esac
  case "$path" in *$'\n'*|*$'\r'*|*$'\t'*) return 1 ;; esac
  case "$path" in
    .git|.git/*|.agents|.agents/*|.claude|.claude/*|.studio-*|.project-*|.v3-*|.task-*|.as-*) return 1 ;;
  esac
  return 0
}

project_path_is_reserved() {
  local studio=$1
  local path=$2
  local projects_root operations_root standards_root references_root reserved
  local projects_folder_id operations_folder_id standards_folder_id references_folder_id
  projects_root=$(trim_field "$studio/STUDIO.md" "Projects root")
  operations_root=$(trim_field "$studio/STUDIO.md" "Operations root")
  standards_root=$(trim_field "$studio/STUDIO.md" "Standards root")
  references_root=$(trim_field "$studio/STUDIO.md" "References root")
  projects_folder_id=$(trim_field "$studio/STUDIO.md" "Projects folder ID")
  operations_folder_id=$(trim_field "$studio/STUDIO.md" "Operations folder ID")
  standards_folder_id=$(trim_field "$studio/STUDIO.md" "Standards folder ID")
  references_folder_id=$(trim_field "$studio/STUDIO.md" "References folder ID")
  if [ -n "$projects_folder_id" ]; then projects_root=$(folder_identity_resolve "$studio" "$projects_folder_id" projects); fi
  if [ -n "$operations_folder_id" ]; then operations_root=$(folder_identity_resolve "$studio" "$operations_folder_id" operations); fi
  if [ -n "$standards_folder_id" ]; then standards_root=$(folder_identity_resolve "$studio" "$standards_folder_id" standards); fi
  if [ -n "$references_folder_id" ]; then references_root=$(folder_identity_resolve "$studio" "$references_folder_id" references); fi
  if [ -n "$projects_root" ] && [ "$path" = "$projects_root" ]; then return 0; fi
  for reserved in "${operations_root:-operations}" "${standards_root:-standards}" "${references_root:-references}"; do
    case "$path" in "$reserved"|"$reserved"/*) return 0 ;; esac
  done
  return 1
}

validate_studio_taxonomy() {
  local studio=$1
  local taxonomy role root folder_id actual
  taxonomy=$(trim_field "$studio/STUDIO.md" "Folder taxonomy")
  [ -n "$taxonomy" ] || return 0
  case "$taxonomy" in as|firm) ;; *) die "studio Folder taxonomy is invalid" ;; esac
  folder_identity_require "$studio" studio "$(trim_field "$studio/STUDIO.md" "Studio folder ID")" >/dev/null
  for role in Projects Operations Standards References; do
    root=$(trim_field "$studio/STUDIO.md" "$role root")
    folder_id=$(trim_field "$studio/STUDIO.md" "$role folder ID")
    safe_relative_path "$root" || die "studio $role root is invalid"
    actual=$(folder_identity_resolve "$studio" "$folder_id" "$(printf '%s' "$role" | tr '[:upper:]' '[:lower:]')")
    folder_identity_require "$studio/$actual" "$(printf '%s' "$role" | tr '[:upper:]' '[:lower:]')" "$folder_id" >/dev/null
  done
}
project_ancestor() {
  local ancestor_studio=$1
  local ancestor_path
  ancestor_path=$(dirname -- "$2")
  while [ "$ancestor_path" != . ]; do
    if [ -f "$ancestor_studio/$ancestor_path/PROJECT.md" ]; then
      printf '%s\n' "$ancestor_path"
      return 0
    fi
    ancestor_path=$(dirname -- "$ancestor_path")
  done
  return 1
}
validate_project_identity() {
  file=$1
  project_id=$(trim_field "$file" "Project ID")
  project_type=$(trim_field "$file" "Type")
  project_status=$(trim_field "$file" "Status")
  client_code=$(trim_field "$file" "Client code")
  created=$(trim_field "$file" "Created")
  valid_project_id "$project_id" || die "PROJECT.md has an invalid Project ID"
  case "$project_type" in internal|client) ;; *) die "PROJECT.md has an invalid Type" ;; esac
  case "$project_status" in prospective|active|on-hold|lost|withdrawn|completed|archived) ;; *) die "PROJECT.md has an invalid Status" ;; esac
  valid_identity_text "$client_code" || die "PROJECT.md has an invalid Client code"
  printf '%s\n' "$created" | grep -Eq '^[0-9]{4}-(0[1-9]|1[0-2])-[0-9]{2}$' || die "PROJECT.md has an invalid Created date"
}
read_registry() {
  awk -f "$REGISTRY_PARSER" "$1/STUDIO.md" > "$2" 2>/dev/null || die "STUDIO.md Projects table is invalid"
}

start=${1:-.}
[ -d "$start" ] || die "context path is not a directory: $start"
project=$(find_up "$start" PROJECT.md || true)
studio=$(find_up "$start" STUDIO.md || true)

if [ -n "$project" ]; then
  [ ! -L "$project" ] && [ ! -L "$project/PROJECT.md" ] || die "project boundary may not be symlinked"
  require_version "$project/PROJECT.md"
  validate_project_identity "$project/PROJECT.md" "$project"
  if [ -n "$studio" ]; then
    [ ! -L "$studio" ] && [ ! -L "$studio/STUDIO.md" ] || die "studio boundary may not be symlinked"
    require_version "$studio/STUDIO.md"
    validate_studio_taxonomy "$studio"
    studio_physical=$(cd -P -- "$studio" && pwd)
    case "$project/" in "$studio_physical"/*/) ;; *) die "project resolves outside its owning studio" ;; esac
    relative_path=${project#"$studio_physical/"}
    safe_relative_path "$relative_path" || die "project has an unsafe studio-relative path"
    project_path_is_reserved "$studio" "$relative_path" && die "project is inside a reserved studio resource folder"
    if ancestor=$(project_ancestor "$studio_physical" "$relative_path"); then die "project is nested inside another project: $ancestor"; fi
    rows=$(mktemp)
    trap 'rm -f "$rows"' EXIT
    read_registry "$studio" "$rows"
    id_count=$(awk -F'\t' -v id="$project_id" '$1==id {n++} END {print n+0}' "$rows")
    [ "$id_count" -eq 1 ] || die "project is not uniquely registered in its owning studio"
    registry_path=$(awk -F'\t' -v id="$project_id" '$1==id {print $7; exit}' "$rows")
    registry_folder_id=$(awk -F'\t' -v id="$project_id" '$1==id {print $9; exit}' "$rows")
    registry_type=$(awk -F'\t' -v id="$project_id" '$1==id {print $5; exit}' "$rows")
    registry_status=$(awk -F'\t' -v id="$project_id" '$1==id {print $6; exit}' "$rows")
    if [ -n "$registry_folder_id" ]; then
      parsed_folder=$(folder_identity_parse "$project") || die "project folder identity is missing or invalid"
      IFS=$'\t' read -r project_folder_id project_folder_kind <<< "$parsed_folder"
      [ "$project_folder_kind" = project ] || die "project folder identity kind is not project"
      [ "$project_folder_id" = "$registry_folder_id" ] || die "project folder identity does not match its studio registration"
      folder_count=$(awk -F'\t' -v folder_id="$registry_folder_id" '$9==folder_id {n++} END {print n+0}' "$rows")
      [ "$folder_count" -eq 1 ] || die "project folder identity is not uniquely registered in its owning studio"
    else
      path_count=$(awk -F'\t' -v path="$relative_path" '$7==path {n++} END {print n+0}' "$rows")
      [ "$path_count" -eq 1 ] && [ "$registry_path" = "$relative_path" ] || die "legacy project path is not uniquely registered in its owning studio"
    fi
    [ "$registry_type" = "$project_type" ] || die "project Type does not match its studio registration"
    [ "$registry_status" = "$project_status" ] || die "project Status does not match its studio registration"
    task_mode=$(trim_field "$studio/STUDIO.md" "Task register")
    case "$task_mode" in
      project) register="$project/TASKS.md" ;;
      portfolio)
        register="$studio_physical/TASKS.md"
        [ -f "$register" ] && [ ! -L "$register" ] || die "portfolio task register is missing or symlinked"
        ;;
      *) die "studio Task register setting is invalid: ${task_mode:-absent}" ;;
    esac
    printf 'project\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$project" "$project_id" "$studio_physical" "$task_mode" "$register" "$registry_type" "$registry_status"
  else
    printf 'project\t%s\t%s\t-\tproject\t%s/TASKS.md\t%s\t%s\n' "$project" "$project_id" "$project" "$project_type" "$project_status"
  fi
  exit 0
fi

if [ -n "$studio" ]; then
  [ ! -L "$studio" ] && [ ! -L "$studio/STUDIO.md" ] || die "studio boundary may not be symlinked"
  require_version "$studio/STUDIO.md"
  validate_studio_taxonomy "$studio"
  studio_physical=$(cd -P -- "$studio" && pwd)
  rows=$(mktemp)
  choices=$(mktemp)
  invalids=$(mktemp)
  trap 'rm -f "$rows" "$choices" "$invalids"' EXIT
  read_registry "$studio" "$rows"

  append_invalid() {
    invalid_id=${1:--}
    invalid_path=${2:--}
    invalid_reason=$3
    printf 'invalid-project\t%s\t%s\t%s\n' "$invalid_id" "$invalid_path" "$invalid_reason" >> "$invalids"
  }

  while IFS=$'\t' read -r id name client code type status path opened folder_id; do
    id_count=$(awk -F'\t' -v value="$id" '$1==value {n++} END {print n+0}' "$rows")
    path_count=$(awk -F'\t' -v value="$path" '$7==value {n++} END {print n+0}' "$rows")
    if [ "$id_count" -ne 1 ]; then append_invalid "$id" "$path" "Project ID is registered $id_count times"; continue; fi
    if [ "$path_count" -ne 1 ]; then append_invalid "$id" "$path" "project path is registered $path_count times"; continue; fi
    if ! valid_project_id "$id"; then append_invalid "$id" "$path" "studio registration has an invalid Project ID"; continue; fi
    if [ -z "$name" ]; then append_invalid "$id" "$path" "studio registration has an empty Project name"; continue; fi
    if [ -z "$client" ]; then append_invalid "$id" "$path" "studio registration has an empty Client"; continue; fi
    if ! valid_identity_text "$code"; then append_invalid "$id" "$path" "studio registration has an invalid Code"; continue; fi
    case "$type" in internal|client) ;; *) append_invalid "$id" "$path" "studio registration has an invalid Type"; continue ;; esac
    case "$status" in prospective|active|on-hold|lost|withdrawn|completed|archived) ;; *) append_invalid "$id" "$path" "studio registration has an invalid Status"; continue ;; esac
    if ! printf '%s\n' "$opened" | grep -Eq '^[0-9]{4}-(0[1-9]|1[0-2])-[0-9]{2}$'; then append_invalid "$id" "$path" "studio registration has an invalid Opened date"; continue; fi
    if [ "$type" = client ] && [ "$client" = — ]; then append_invalid "$id" "$path" "client project registration requires a Client"; continue; fi
    if [ -n "$folder_id" ]; then
      if ! folder_identity_valid_id "$folder_id"; then append_invalid "$id" "$path" "studio registration has an invalid Folder ID"; continue; fi
      folder_count=$(awk -F'\t' -v value="$folder_id" '$9==value {n++} END {print n+0}' "$rows")
      if [ "$folder_count" -ne 1 ]; then append_invalid "$id" "$path" "Folder ID is registered $folder_count times"; continue; fi
      folder_matches=$(folder_identity_find "$studio" "$folder_id" || true)
      folder_match_count=$(printf '%s\n' "$folder_matches" | sed '/^$/d' | wc -l | tr -d ' ')
      if [ "$folder_match_count" -ne 1 ]; then append_invalid "$id" "$path" "Folder ID resolves to $folder_match_count managed folders"; continue; fi
      IFS=$'\t' read -r resolved_path folder_kind <<< "$folder_matches"
      if [ "$folder_kind" != project ]; then append_invalid "$id" "$path" "Folder ID kind is $folder_kind, not project"; continue; fi
      path=$resolved_path
    fi
    if ! safe_relative_path "$path"; then append_invalid "$id" "$path" "registered project path is unsafe"; continue; fi
    if project_path_is_reserved "$studio" "$path"; then append_invalid "$id" "$path" "project is inside a reserved studio resource folder"; continue; fi
    if ancestor=$(project_ancestor "$studio_physical" "$path"); then append_invalid "$id" "$path" "project is nested inside another project: $ancestor"; continue; fi
    candidate="$studio/$path"
    if [ ! -d "$candidate" ]; then append_invalid "$id" "$path" "registered project directory is missing"; continue; fi
    if [ -L "$candidate" ]; then append_invalid "$id" "$path" "registered project directory may not be symlinked"; continue; fi
    physical=$(cd -P -- "$candidate" && pwd)
    case "$physical/" in "$studio_physical"/*/) ;; *) append_invalid "$id" "$path" "registered project resolves outside its studio"; continue ;; esac
    if [ "$physical" != "$studio_physical/$path" ]; then append_invalid "$id" "$path" "registered project path may not contain symlinks"; continue; fi
    if [ ! -f "$candidate/PROJECT.md" ]; then append_invalid "$id" "$path" "PROJECT.md is missing"; continue; fi
    if [ -L "$candidate/PROJECT.md" ]; then append_invalid "$id" "$path" "PROJECT.md may not be symlinked"; continue; fi
    if [ -n "$folder_id" ]; then
      parsed_folder=$(folder_identity_parse "$candidate") || { append_invalid "$id" "$path" "project folder identity is missing or invalid"; continue; }
      IFS=$'\t' read -r file_folder_id file_folder_kind <<< "$parsed_folder"
      if [ "$file_folder_id" != "$folder_id" ] || [ "$file_folder_kind" != project ]; then append_invalid "$id" "$path" "project folder identity does not match its registration"; continue; fi
    fi
    version=$(trim_field "$candidate/PROJECT.md" "Format version")
    file_id=$(trim_field "$candidate/PROJECT.md" "Project ID")
    file_name=$(trim_field "$candidate/PROJECT.md" "Project")
    file_type=$(trim_field "$candidate/PROJECT.md" "Type")
    file_status=$(trim_field "$candidate/PROJECT.md" "Status")
    file_code=$(trim_field "$candidate/PROJECT.md" "Client code")
    file_client=$(trim_field "$candidate/PROJECT.md" "Client")
    file_created=$(trim_field "$candidate/PROJECT.md" "Created")
    if [ "$version" != 3 ]; then append_invalid "$id" "$path" "PROJECT.md format version is ${version:-absent}; version 3 required"; continue; fi
    if [ "$file_id" != "$id" ]; then append_invalid "$id" "$path" "PROJECT.md Project ID does not match its studio registration"; continue; fi
    if [ "$file_name" != "$name" ]; then append_invalid "$id" "$path" "PROJECT.md Project does not match its studio registration"; continue; fi
    if [ "$file_type" != "$type" ]; then append_invalid "$id" "$path" "PROJECT.md Type does not match its studio registration"; continue; fi
    if [ "$file_status" != "$status" ]; then append_invalid "$id" "$path" "PROJECT.md Status does not match its studio registration"; continue; fi
    if [ "$file_code" != "$code" ]; then append_invalid "$id" "$path" "PROJECT.md Client code does not match its studio registration"; continue; fi
    if [ "$file_client" != "$client" ]; then append_invalid "$id" "$path" "PROJECT.md Client does not match its studio registration"; continue; fi
    if [ "$file_created" != "$opened" ]; then append_invalid "$id" "$path" "PROJECT.md Created does not match its studio registration"; continue; fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$id" "$name" "$path" "$type" "$status" >> "$choices"
  done < "$rows"
  if [ ! -s "$rows" ]; then
    printf 'no-projects\t%s\n' "$studio_physical"
  else
    printf 'studio-picker\t%s\n' "$studio_physical"
    cat "$choices"
    cat "$invalids"
  fi
  exit 0
fi

printf 'no-context\n'
