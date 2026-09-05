#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
TEMPLATE_DIR="$SCRIPT_DIR/../templates"
PROJECT_TEMPLATE_DIR="$SCRIPT_DIR/../../project/templates"
TASK_TEMPLATE_DIR="$SCRIPT_DIR/../../tasklist/templates"
PROJECT_SCRIPT="$SCRIPT_DIR/../../project/scripts/project-workspace.sh"
PROPOSAL_SCRIPT="$SCRIPT_DIR/../../proposal/scripts/proposal-workspace.sh"
REGISTRY_PARSER="$SCRIPT_DIR/../../project/scripts/project-registry.awk"
FOLDER_IDENTITY_SCRIPT="$SCRIPT_DIR/../../project/scripts/folder-identity.sh"

die() {
  printf 'studio-workspace: %s\n' "$*" >&2
  exit 1
}

# shellcheck source=../../project/scripts/folder-identity.sh
. "$FOLDER_IDENTITY_SCRIPT"

validate_root() {
  case "${1:-}" in
    ''|/|.|..|"$HOME") die "unsafe studio target: ${1:-<empty>}" ;;
  esac
  case "$1" in
    *$'\n'*|*$'\r'*|*$'\t'*) die "studio target contains control characters" ;;
  esac
  [ ! -L "$1" ] || die "studio target may not be a symlink: $1"
}

validate_new_studio_target() {
  validate_root "$1"
  base=$(basename -- "$1")
  case "$base" in
    ''|.|..|.*) die "studio directory name is invalid" ;;
    *$'\n'*|*$'\r'*|*$'\t'*) die "studio directory name contains control characters" ;;
  esac
}

validate_text() {
  [ -n "${2:-}" ] || die "$1 is required"
  case "$2" in
    *'|'*|*$'\n'*|*$'\r'*|*$'\t'*) die "$1 contains a reserved character" ;;
  esac
}

escape_sed() {
  printf '%s' "$1" | sed 's/[\\&|]/\\&/g'
}

file_sha256() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v openssl >/dev/null 2>&1; then
    openssl dgst -sha256 "$1" | awk '{print $NF}'
  else
    die "no SHA-256 tool is available"
  fi
}

render() {
  source_file=$1
  target_file=$2
  studio_name=$(escape_sed "$3")
  working_units=$(escape_sed "$4")
  country=$(escape_sed "$5")
  state_region=$(escape_sed "$6")
  city=$(escape_sed "$7")
  naming_policy=$(escape_sed "${8:-as}")
  project_id_convention=$(escape_sed "${9:-YYMMDD-CCC-PROJECT-NAME}")
  folder_taxonomy=$(escape_sed "${10:-as}")
  project_folder_convention=${11:-}
  if [ -z "$project_folder_convention" ]; then
    project_folder_convention='Projects/{Client Account or Internal}/{YYYYMM} {Project Name}'
  fi
  project_folder_convention=$(escape_sed "$project_folder_convention")
  projects_root=$(escape_sed "${12:-Projects}")
  operations_root=$(escape_sed "${13:-Operations}")
  standards_root=$(escape_sed "${14:-Standards}")
  references_root=$(escape_sed "${15:-References}")
  studio_folder_id=$(escape_sed "${16:-}")
  projects_folder_id=$(escape_sed "${17:-}")
  operations_folder_id=$(escape_sed "${18:-}")
  standards_folder_id=$(escape_sed "${19:-}")
  references_folder_id=$(escape_sed "${20:-}")
  sed \
    -e "s|{{STUDIO_NAME}}|$studio_name|g" \
    -e "s|{{WORKING_UNITS}}|$working_units|g" \
    -e "s|{{COUNTRY}}|$country|g" \
    -e "s|{{STATE_REGION}}|$state_region|g" \
    -e "s|{{CITY}}|$city|g" \
    -e "s|{{NAMING_POLICY}}|$naming_policy|g" \
    -e "s|{{PROJECT_ID_CONVENTION}}|$project_id_convention|g" \
    -e "s|{{FOLDER_TAXONOMY}}|$folder_taxonomy|g" \
    -e "s|{{PROJECT_FOLDER_CONVENTION}}|$project_folder_convention|g" \
    -e "s|{{PROJECTS_ROOT}}|$projects_root|g" \
    -e "s|{{OPERATIONS_ROOT}}|$operations_root|g" \
    -e "s|{{STANDARDS_ROOT}}|$standards_root|g" \
    -e "s|{{REFERENCES_ROOT}}|$references_root|g" \
    -e "s|{{STUDIO_FOLDER_ID}}|$studio_folder_id|g" \
    -e "s|{{PROJECTS_FOLDER_ID}}|$projects_folder_id|g" \
    -e "s|{{OPERATIONS_FOLDER_ID}}|$operations_folder_id|g" \
    -e "s|{{STANDARDS_FOLDER_ID}}|$standards_folder_id|g" \
    -e "s|{{REFERENCES_FOLDER_ID}}|$references_folder_id|g" \
    "$source_file" > "$target_file"
}

require_format() {
  file=$1
  label=$2
  version=$(awk -F'|' 'function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s} /^\|/ && trim($2)=="Format version" {print trim($3); exit}' "$file")
  [ "$version" = 3 ] || die "$label format version is ${version:-absent}; version 3 is required (migrate explicitly before writing)"
}

project_field() {
  awk -F'|' -v key="$2" 'function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s} /^\|/ && trim($2)==key {print trim($3); exit}' "$1"
}

validate_project_id() {
  local project_id=${1:-}
  validate_text "project id" "$project_id"
  case "$project_id" in .|..|' '*|*' '|\#|---|:---|---:|:---:) die "project id is reserved or has surrounding spaces" ;; esac
  [ "${#project_id}" -le 160 ] || die "project id must be 160 characters or fewer"
}

validate_project_type() {
  case "${1:-}" in internal|client) ;; *) die "project type is invalid: ${1:-<empty>}" ;; esac
}

validate_project_status() {
  case "${1:-}" in prospective|active|on-hold|lost|withdrawn|completed|archived) ;;
    *) die "project status is invalid: ${1:-<empty>}" ;;
  esac
}

validate_client_code() {
  local client_code=${1:-}
  validate_text "client code" "$client_code"
  [ "${#client_code}" -le 80 ] || die "client code must be 80 characters or fewer"
}

validate_naming_policy() {
  case "${1:-}" in as|firm|none) ;; *) die "project naming policy must be as, firm, or none" ;; esac
}

validate_folder_taxonomy() {
  case "${1:-}" in as|firm) ;; *) die "folder taxonomy must be as or firm" ;; esac
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

validate_managed_roots() {
  local root
  for root in "$@"; do
    safe_relative_path "$root" || die "managed root must be a safe relative path: ${root:-<empty>}"
  done
  [ "$1" != "$2" ] && [ "$1" != "$3" ] && [ "$1" != "$4" ] &&
    [ "$2" != "$3" ] && [ "$2" != "$4" ] && [ "$3" != "$4" ] ||
    die "managed roots must be distinct"
}

project_path_is_reserved() {
  local studio=$1
  local path=$2
  local projects_root operations_root standards_root references_root reserved
  local projects_folder_id operations_folder_id standards_folder_id references_folder_id
  projects_root=$(project_field "$studio/STUDIO.md" "Projects root")
  operations_root=$(project_field "$studio/STUDIO.md" "Operations root")
  standards_root=$(project_field "$studio/STUDIO.md" "Standards root")
  references_root=$(project_field "$studio/STUDIO.md" "References root")
  projects_folder_id=$(project_field "$studio/STUDIO.md" "Projects folder ID")
  operations_folder_id=$(project_field "$studio/STUDIO.md" "Operations folder ID")
  standards_folder_id=$(project_field "$studio/STUDIO.md" "Standards folder ID")
  references_folder_id=$(project_field "$studio/STUDIO.md" "References folder ID")
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

resolve_registered_project_path() {
  local studio=$1
  local cached_path=$2
  local folder_id=${3:-}
  if [ -z "$folder_id" ]; then
    printf '%s\n' "$cached_path"
    return 0
  fi
  actual=$(folder_identity_resolve "$studio" "$folder_id" project)
  [ "$actual" != . ] || die "project folder identity resolves to the studio root"
  printf '%s\n' "$actual"
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

ensure_group_ancestor_configs() {
  local studio=$1
  local relative_path=$2
  local cursor directory
  cursor=$(dirname -- "$relative_path")
  while [ "$cursor" != . ]; do
    directory="$studio/$cursor"
    [ -d "$directory" ] && [ ! -L "$directory" ] || die "project ancestor is missing or symlinked: $cursor"
    if [ -e "$directory/$FOLDER_IDENTITY_FILE" ] || [ -L "$directory/$FOLDER_IDENTITY_FILE" ]; then
      folder_identity_require "$directory" >/dev/null
    else
      folder_identity_ensure "$directory" group >/dev/null
    fi
    cursor=$(dirname -- "$cursor")
  done
}

ensure_registered_folder_chain() {
  local studio=$1
  local relative_path=$2
  folder_identity_ensure "$studio" studio >/dev/null
  ensure_group_ancestor_configs "$studio" "$relative_path"
  folder_identity_ensure "$studio/$relative_path" project
}

validate_opened_date() {
  printf '%s\n' "${1:-}" | grep -Eq '^[0-9]{4}-(0[1-9]|1[0-2])-[0-9]{2}$' || die "project opened date must use YYYY-MM-DD"
}

registry_rows() {
  awk -f "$REGISTRY_PARSER" "$1/STUDIO.md" > "$2" || die "STUDIO.md Projects table is invalid"
}

write_registry() {
  local studio=$1
  local rows=$2
  local target=$3
  local source=${4:-$studio/STUDIO.md}
  awk -v rows_file="$rows" '
    /<!-- projects:start -->/ {
      print
      print "| Project ID | Project | Client | Code | Type | Status | Folder | Opened | Folder ID |"
      print "|---|---|---|---|---|---|---|---|---|"
      while ((getline row < rows_file) > 0) {
        split(row, value, "\t")
        print "| " value[1] " | " value[2] " | " value[3] " | " value[4] " | " value[5] " | " value[6] " | " value[7] " | " value[8] " | " value[9] " |"
      }
      close(rows_file)
      inside=1
      next
    }
    /<!-- projects:end -->/ {inside=0; print; next}
    !inside {print}
  ' "$source" > "$target"
}

require_studio() {
  local folder_taxonomy projects_root operations_root standards_root references_root
  local studio_folder_id projects_folder_id operations_folder_id standards_folder_id references_folder_id
  validate_root "$1"
  [ -d "$1" ] || die "studio root is not a directory: $1"
  [ -f "$1/STUDIO.md" ] && [ ! -L "$1/STUDIO.md" ] || die "STUDIO.md is missing or symlinked at $1"
  require_format "$1/STUDIO.md" "Studio"
  folder_taxonomy=$(project_field "$1/STUDIO.md" "Folder taxonomy")
  if [ -n "$folder_taxonomy" ]; then
    validate_folder_taxonomy "$folder_taxonomy"
    projects_root=$(project_field "$1/STUDIO.md" "Projects root")
    operations_root=$(project_field "$1/STUDIO.md" "Operations root")
    standards_root=$(project_field "$1/STUDIO.md" "Standards root")
    references_root=$(project_field "$1/STUDIO.md" "References root")
    validate_managed_roots "$projects_root" "$operations_root" "$standards_root" "$references_root"
    studio_folder_id=$(project_field "$1/STUDIO.md" "Studio folder ID")
    projects_folder_id=$(project_field "$1/STUDIO.md" "Projects folder ID")
    operations_folder_id=$(project_field "$1/STUDIO.md" "Operations folder ID")
    standards_folder_id=$(project_field "$1/STUDIO.md" "Standards folder ID")
    references_folder_id=$(project_field "$1/STUDIO.md" "References folder ID")
    folder_identity_require "$1" studio "$studio_folder_id" >/dev/null
    projects_root=$(folder_identity_resolve "$1" "$projects_folder_id" projects)
    operations_root=$(folder_identity_resolve "$1" "$operations_folder_id" operations)
    standards_root=$(folder_identity_resolve "$1" "$standards_folder_id" standards)
    references_root=$(folder_identity_resolve "$1" "$references_folder_id" references)
    folder_identity_require "$1/$projects_root" projects "$projects_folder_id" >/dev/null
    folder_identity_require "$1/$operations_root" operations "$operations_folder_id" >/dev/null
    folder_identity_require "$1/$standards_root" standards "$standards_folder_id" >/dev/null
    folder_identity_require "$1/$references_root" references "$references_folder_id" >/dev/null
  elif [ -e "$1/projects" ] || [ -L "$1/projects" ]; then
    [ -d "$1/projects" ] && [ ! -L "$1/projects" ] || die "legacy studio projects directory is invalid or symlinked"
    physical_studio=$(cd -P -- "$1" && pwd)
    physical_projects=$(cd -P -- "$1/projects" && pwd)
    [ "$physical_projects" = "$physical_studio/projects" ] || die "legacy studio projects directory may not be symlinked"
  fi
}

require_owned_studio_file() {
  owned_studio=$1
  owned_name=$2
  owned_requirement=$3
  owned_file="$owned_studio/$owned_name"
  if [ ! -e "$owned_file" ]; then
    [ "$owned_requirement" = optional ] && return 0
    die "$owned_name is missing at $owned_studio"
  fi
  [ -f "$owned_file" ] && [ ! -L "$owned_file" ] || die "$owned_name must be a non-symlink regular file owned by the studio"
  owned_physical_studio=$(cd -P -- "$owned_studio" && pwd)
  owned_physical_parent=$(cd -P -- "$(dirname -- "$owned_file")" && pwd)
  [ "$owned_physical_parent" = "$owned_physical_studio" ] || die "$owned_name resolves outside the studio root"
}

require_safe_project() {
  local studio=$1
  local relative_path=$2
  local expected_folder_id=${3:-}
  local project physical_studio physical_project
  local project_id project_name project_type project_status client_code client created
  safe_relative_path "$relative_path" || die "unsafe registered project path: $relative_path"
  project_path_is_reserved "$studio" "$relative_path" && die "registered project path uses a reserved studio resource folder: $relative_path"
  project="$studio/$relative_path"
  [ ! -L "$project" ] || die "registered project may not be a symlink: $relative_path"
  [ -f "$project/PROJECT.md" ] || die "PROJECT.md not found at $relative_path"
  [ ! -L "$project/PROJECT.md" ] || die "PROJECT.md may not be a symlink: $relative_path"
  require_format "$project/PROJECT.md" "Project"
  physical_studio=$(cd -P -- "$studio" && pwd)
  physical_project=$(cd -P -- "$project" && pwd)
  case "$physical_project/" in "$physical_studio"/*/) ;; *) die "project resolves outside its studio: $relative_path" ;; esac
  [ "$physical_project" = "$physical_studio/$relative_path" ] || die "registered project path may not contain symlinks: $relative_path"
  if ancestor=$(project_ancestor "$studio" "$relative_path"); then die "registered project is nested inside another project: $ancestor"; fi
  project_id=$(project_field "$project/PROJECT.md" "Project ID")
  project_name=$(project_field "$project/PROJECT.md" "Project")
  project_type=$(project_field "$project/PROJECT.md" "Type")
  project_status=$(project_field "$project/PROJECT.md" "Status")
  client_code=$(project_field "$project/PROJECT.md" "Client code")
  client=$(project_field "$project/PROJECT.md" "Client")
  created=$(project_field "$project/PROJECT.md" "Created")
  validate_project_id "$project_id"
  validate_text "project name" "$project_name"
  validate_project_type "$project_type"
  validate_project_status "$project_status"
  validate_client_code "$client_code"
  validate_text "client" "$client"
  validate_opened_date "$created"
  if [ "$project_type" = client ] && [ "$client" = — ]; then die "client project requires a client display name"; fi
  if [ -e "$project/TASKS.md" ] && [ -L "$project/TASKS.md" ]; then
    die "TASKS.md may not be a symlink: $relative_path"
  fi
  if [ -n "$expected_folder_id" ]; then
    folder_identity_require "$project" project "$expected_folder_id" >/dev/null
  elif [ -e "$project/$FOLDER_IDENTITY_FILE" ] || [ -L "$project/$FOLDER_IDENTITY_FILE" ]; then
    folder_identity_require "$project" project >/dev/null
  fi
}

init_studio() {
  target=$1
  name=$2
  working_units=$3
  country=$4
  state_region=$5
  city=$6
  naming_policy=${7:-as}
  project_id_convention=${8:-}
  folder_taxonomy=${9:-as}
  project_folder_convention=${10:-}
  projects_root=${11:-}
  operations_root=${12:-}
  standards_root=${13:-}
  references_root=${14:-}
  if [ -z "$project_id_convention" ]; then
    case "$naming_policy" in
      as) project_id_convention=YYMMDD-CCC-PROJECT-NAME ;;
      none) project_id_convention='No convention' ;;
      firm) die "firm project naming requires a convention" ;;
    esac
  fi
  case "$folder_taxonomy" in
    as)
      [ -z "$project_folder_convention" ] || [ "$project_folder_convention" = 'Projects/{Client Account or Internal}/{YYYYMM} {Project Name}' ] ||
        die "AS folder taxonomy uses the standard project-folder convention"
      [ -z "$projects_root" ] || [ "$projects_root" = Projects ] || die "AS folder taxonomy uses Projects as its project root"
      [ -z "$operations_root" ] || [ "$operations_root" = Operations ] || die "AS folder taxonomy uses Operations as its operations root"
      [ -z "$standards_root" ] || [ "$standards_root" = Standards ] || die "AS folder taxonomy uses Standards as its standards root"
      [ -z "$references_root" ] || [ "$references_root" = References ] || die "AS folder taxonomy uses References as its references root"
      project_folder_convention='Projects/{Client Account or Internal}/{YYYYMM} {Project Name}'
      projects_root=Projects
      operations_root=Operations
      standards_root=Standards
      references_root=References
      ;;
    firm)
      [ -n "$project_folder_convention" ] || die "firm folder taxonomy requires a project-folder convention"
      [ -n "$projects_root" ] && [ -n "$operations_root" ] && [ -n "$standards_root" ] && [ -n "$references_root" ] ||
        die "firm folder taxonomy requires projects, operations, standards, and references roots"
      ;;
    *) die "folder taxonomy must be as or firm" ;;
  esac
  validate_new_studio_target "$target"
  validate_text "studio name" "$name"
  validate_text "working units" "$working_units"
  validate_text "country" "$country"
  validate_text "state or region" "$state_region"
  validate_text "city" "$city"
  validate_naming_policy "$naming_policy"
  validate_text "project id convention" "$project_id_convention"
  validate_folder_taxonomy "$folder_taxonomy"
  validate_text "project folder convention" "$project_folder_convention"
  validate_managed_roots "$projects_root" "$operations_root" "$standards_root" "$references_root"

  if [ -e "$target" ] && [ ! -d "$target" ]; then
    die "target exists and is not a directory: $target"
  fi
  if [ -d "$target" ] && [ -n "$(find "$target" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
    die "target directory is not empty: $target"
  fi

  mkdir -p "$target/.claude/skills" "$target/.agents/skills" \
    "$target/$projects_root" "$target/$operations_root" "$target/$standards_root" "$target/$references_root"
  studio_folder_id=$(folder_identity_ensure "$target" studio)
  ensure_group_ancestor_configs "$target" "$projects_root"
  ensure_group_ancestor_configs "$target" "$operations_root"
  ensure_group_ancestor_configs "$target" "$standards_root"
  ensure_group_ancestor_configs "$target" "$references_root"
  projects_folder_id=$(folder_identity_ensure "$target/$projects_root" projects)
  operations_folder_id=$(folder_identity_ensure "$target/$operations_root" operations)
  standards_folder_id=$(folder_identity_ensure "$target/$standards_root" standards)
  references_folder_id=$(folder_identity_ensure "$target/$references_root" references)
  if [ "$folder_taxonomy" = as ]; then
    mkdir -p "$target/$projects_root/Internal"
    folder_identity_ensure "$target/$projects_root/Internal" internal >/dev/null
  fi
  render "$TEMPLATE_DIR/STUDIO.md" "$target/STUDIO.md" "$name" "$working_units" "$country" "$state_region" "$city" \
    "$naming_policy" "$project_id_convention" "$folder_taxonomy" "$project_folder_convention" \
    "$projects_root" "$operations_root" "$standards_root" "$references_root" \
    "$studio_folder_id" "$projects_folder_id" "$operations_folder_id" "$standards_folder_id" "$references_folder_id"
  render "$TEMPLATE_DIR/CLAUDE.md" "$target/CLAUDE.md" "$name" "$working_units" "$country" "$state_region" "$city" \
    "$naming_policy" "$project_id_convention" "$folder_taxonomy" "$project_folder_convention" \
    "$projects_root" "$operations_root" "$standards_root" "$references_root"
  render "$TEMPLATE_DIR/AGENTS.md" "$target/AGENTS.md" "$name" "$working_units" "$country" "$state_region" "$city" \
    "$naming_policy" "$project_id_convention" "$folder_taxonomy" "$project_folder_convention" \
    "$projects_root" "$operations_root" "$standards_root" "$references_root"
  cp "$TEMPLATE_DIR/operations-README.md" "$target/$operations_root/README.md"
  cp "$TEMPLATE_DIR/standards-README.md" "$target/$standards_root/README.md"
  cp "$TEMPLATE_DIR/references-README.md" "$target/$references_root/README.md"
  cp "$TEMPLATE_DIR/.mcp.json" "$target/.mcp.json"
  printf 'created studio: %s\n' "$target"
}

register_project() {
  studio=$1
  project_id=$2
  project_name=$3
  relative_path=$4
  require_studio "$studio"
  validate_text "project id" "$project_id"
  validate_text "project name" "$project_name"
  validate_text "project path" "$relative_path"
  safe_relative_path "$relative_path" || die "project path must be a safe relative descendant of the studio"
  require_safe_project "$studio" "$relative_path"

  file_id=$(project_field "$studio/$relative_path/PROJECT.md" "Project ID")
  file_name=$(project_field "$studio/$relative_path/PROJECT.md" "Project")
  [ "$file_id" = "$project_id" ] || die "registration Project ID does not match PROJECT.md"
  [ "$file_name" = "$project_name" ] || die "registration project name does not match PROJECT.md"
  client=$(project_field "$studio/$relative_path/PROJECT.md" "Client")
  client_code=$(project_field "$studio/$relative_path/PROJECT.md" "Client code")
  project_type=$(project_field "$studio/$relative_path/PROJECT.md" "Type")
  project_status=$(project_field "$studio/$relative_path/PROJECT.md" "Status")
  opened=$(project_field "$studio/$relative_path/PROJECT.md" "Created")

  rows=$(mktemp "$studio/.studio-register-rows.XXXXXX")
  registry_rows "$studio" "$rows"
  if awk -F'\t' -v id="$project_id" -v path="$relative_path" \
    '$1==id || $7==path {found=1} END {exit found ? 0 : 1}' "$rows"; then
    rm -f "$rows"
    die "project id or path is already registered"
  fi
  folder_id=$(ensure_registered_folder_chain "$studio" "$relative_path")
  require_safe_project "$studio" "$relative_path" "$folder_id"
  if awk -F'\t' -v folder_id="$folder_id" '$9!="" && $9==folder_id {found=1} END {exit found ? 0 : 1}' "$rows"; then
    rm -f "$rows"
    die "folder identity is already registered"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$project_id" "$project_name" "$client" "$client_code" "$project_type" "$project_status" "$relative_path" "$opened" "$folder_id" >> "$rows"
  tmp=$(mktemp "$studio/.studio-manifest.XXXXXX")
  write_registry "$studio" "$rows" "$tmp"
  rm -f "$rows"
  mv "$tmp" "$studio/STUDIO.md"
  printf 'registered project: %s\n' "$relative_path"
}

set_project_status() {
  studio=$1
  project_id=$2
  requested_status=$3
  require_studio "$studio"
  validate_text "project id" "$project_id"
  validate_project_id "$project_id"
  validate_project_status "$requested_status"
  rows=$(mktemp "$studio/.studio-status-rows.XXXXXX")
  registry_rows "$studio" "$rows"
  matches=$(awk -F'\t' -v id="$project_id" '$1==id {n++} END {print n+0}' "$rows")
  if [ "$matches" -ne 1 ]; then
    rm -f "$rows"
    die "project id is not registered: $project_id"
  fi
  cached_path=$(awk -F'\t' -v id="$project_id" '$1==id {print $7; exit}' "$rows")
  folder_id=$(awk -F'\t' -v id="$project_id" '$1==id {print $9; exit}' "$rows")
  relative_path=$(resolve_registered_project_path "$studio" "$cached_path" "$folder_id")
  require_safe_project "$studio" "$relative_path" "$folder_id"
  [ "$(project_field "$studio/$relative_path/PROJECT.md" "Project ID")" = "$project_id" ] || {
    rm -f "$rows"
    die "registered Project ID does not match PROJECT.md"
  }
  transaction=$(mktemp -d "$studio/.project-status-transaction.XXXXXX")
  cp "$studio/STUDIO.md" "$transaction/STUDIO.md"
  cp "$studio/$relative_path/PROJECT.md" "$transaction/PROJECT.md"
  committed=0
  rollback_status_failure() {
    rollback_status_label=$1
    rollback_status_target=$2
    rollback_status_reason=$3
    printf '%s\t%s\t%s\n' "$rollback_status_label" "$rollback_status_target" "$rollback_status_reason" >> "$transaction/ROLLBACK-FAILURES.tsv"
    printf 'studio-workspace: rollback restore failed: %s (%s)\n' "$rollback_status_label" "$rollback_status_reason" >&2
    rollback_status_failed=1
  }
  restore_status_snapshot() {
    restore_status_label=$1
    restore_status_source=$2
    restore_status_target=$3
    if [ "${ARCH_STUDIO_FAIL_RESTORE_AT:-}" = "$restore_status_label" ]; then
      rollback_status_failure "$restore_status_label" "$restore_status_target" "injected restore failure"
    elif ! cp "$restore_status_source" "$restore_status_target"; then
      rollback_status_failure "$restore_status_label" "$restore_status_target" "copy failed"
    elif ! cmp -s "$restore_status_source" "$restore_status_target"; then
      rollback_status_failure "$restore_status_label" "$restore_status_target" "verification failed"
    fi
  }
  rollback_project_status() {
    [ "$committed" -eq 0 ] || return 0
    rollback_status_failed=0
    : > "$transaction/ROLLBACK-FAILURES.tsv"
    restore_status_snapshot status-studio "$transaction/STUDIO.md" "$studio/STUDIO.md"
    restore_status_snapshot status-project "$transaction/PROJECT.md" "$studio/$relative_path/PROJECT.md"
    [ "$rollback_status_failed" -eq 0 ]
  }
  finalize_project_status() {
    final_status=$1
    trap - EXIT HUP INT TERM
    if [ "$committed" -eq 0 ]; then
      if rollback_project_status; then
        rm -rf "$transaction"
      else
        printf 'studio-workspace: rollback incomplete; transaction preserved: %s\n' "$transaction" >&2
      fi
    else
      rm -rf "$transaction"
    fi
    rm -f "$rows"
    exit "$final_status"
  }
  trap 'finalize_project_status $?' EXIT
  trap 'finalize_project_status 129' HUP
  trap 'finalize_project_status 130' INT
  trap 'finalize_project_status 143' TERM

  project_tmp=$(mktemp "$studio/$relative_path/.project-status.XXXXXX")
  awk -F'|' -v changed="$(date +%Y-%m-%d)" -v requested="$requested_status" '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /^\|/ && trim($2)=="Status" {print "| Status | " requested " | studio status update | " changed " |"; found=1; next}
    {print}
    END {if (!found) exit 2}
  ' "$studio/$relative_path/PROJECT.md" > "$project_tmp" || { rm -f "$project_tmp"; die "PROJECT.md has no Status field"; }
  mv "$project_tmp" "$studio/$relative_path/PROJECT.md"
  updated_rows=$(mktemp "$studio/.studio-status-updated.XXXXXX")
  awk -F'\t' -v OFS='\t' -v id="$project_id" -v requested="$requested_status" '$1==id {$6=requested} {print}' "$rows" > "$updated_rows"
  tmp=$(mktemp "$studio/.studio-manifest.XXXXXX")
  write_registry "$studio" "$updated_rows" "$tmp"
  rm -f "$updated_rows"
  mv "$tmp" "$studio/STUDIO.md"
  [ "${ARCH_STUDIO_FAIL_AT:-}" != status-after-manifest ] || die "injected failure after status manifest replacement"
  [ "$(project_field "$studio/$relative_path/PROJECT.md" "Status")" = "$requested_status" ] || die "project status verification failed"
  verify_rows=$(mktemp "$studio/.studio-status-verify.XXXXXX")
  registry_rows "$studio" "$verify_rows"
  [ "$(awk -F'\t' -v id="$project_id" '$1==id {print $6}' "$verify_rows")" = "$requested_status" ] || { rm -f "$verify_rows"; die "registry status verification failed"; }
  rm -f "$verify_rows"
  committed=1
  rm -rf "$transaction"
  rm -f "$rows"
  trap - EXIT HUP INT TERM
  printf 'project status: %s -> %s\n' "$project_id" "$requested_status"
}

set_project_naming() {
  studio=$1
  naming_policy=$2
  project_id_convention=$3
  require_studio "$studio"
  validate_naming_policy "$naming_policy"
  validate_text "project id convention" "$project_id_convention"
  policy_count=$(awk -F'|' 'function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s} /^\|/ && trim($2)=="Project naming" {n++} END {print n+0}' "$studio/STUDIO.md")
  convention_count=$(awk -F'|' 'function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s} /^\|/ && trim($2)=="Project ID convention" {n++} END {print n+0}' "$studio/STUDIO.md")
  [ "$policy_count" -le 1 ] && [ "$convention_count" -le 1 ] || die "STUDIO.md contains duplicate project naming settings"
  current_policy=$(project_field "$studio/STUDIO.md" "Project naming")
  current_convention=$(project_field "$studio/STUDIO.md" "Project ID convention")
  if [ "$current_policy" = "$naming_policy" ] && [ "$current_convention" = "$project_id_convention" ]; then
    printf 'project naming unchanged: %s (%s)\n' "$naming_policy" "$project_id_convention"
    return 0
  fi
  tmp=$(mktemp "$studio/.studio-naming.XXXXXX")
  awk -F'|' -v policy="$naming_policy" -v convention="$project_id_convention" -v has_policy="$policy_count" -v has_convention="$convention_count" '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /^\|/ && trim($2)=="Project naming" {print "| Project naming | " policy " |"; next}
    /^\|/ && trim($2)=="Project ID convention" {print "| Project ID convention | " convention " |"; next}
    /^\|/ && trim($2)=="Task register" {
      print
      if (!has_policy) print "| Project naming | " policy " |"
      if (!has_convention) print "| Project ID convention | " convention " |"
      next
    }
    {print}
  ' "$studio/STUDIO.md" > "$tmp"
  mv "$tmp" "$studio/STUDIO.md"
  [ "$(project_field "$studio/STUDIO.md" "Project naming")" = "$naming_policy" ] || die "project naming policy verification failed"
  [ "$(project_field "$studio/STUDIO.md" "Project ID convention")" = "$project_id_convention" ] || die "project ID convention verification failed"
  printf 'project naming: %s (%s)\n' "$naming_policy" "$project_id_convention"
}

status_studio() {
  studio=$1
  require_studio "$studio"
  naming_policy=$(project_field "$studio/STUDIO.md" "Project naming")
  project_id_convention=$(project_field "$studio/STUDIO.md" "Project ID convention")
  case "$naming_policy" in
    as|firm|none) naming_state="$naming_policy (${project_id_convention:-missing convention})" ;;
    '') naming_state="unknown (choose as, firm, or none before creating another project)" ;;
    *) naming_state="invalid ($naming_policy)" ;;
  esac
  printf 'naming: %s\n' "$naming_state"
  folder_taxonomy=$(project_field "$studio/STUDIO.md" "Folder taxonomy")
  project_folder_convention=$(project_field "$studio/STUDIO.md" "Project folder convention")
  operations_root=$(project_field "$studio/STUDIO.md" "Operations root")
  standards_root=$(project_field "$studio/STUDIO.md" "Standards root")
  references_root=$(project_field "$studio/STUDIO.md" "References root")
  case "$folder_taxonomy" in
    as|firm) taxonomy_state="$folder_taxonomy (${project_folder_convention:-missing convention})" ;;
    '') taxonomy_state="unknown (choose AS standard or a firm-defined taxonomy before creating another project)" ;;
    *) taxonomy_state="invalid ($folder_taxonomy)" ;;
  esac
  printf 'taxonomy: %s\n' "$taxonomy_state"
  task_mode=$(awk -F'|' '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /^\|/ && trim($2)=="Task register" {print trim($3); exit}
  ' "$studio/STUDIO.md")
  case "$task_mode" in
    project) task_state=project ;;
    portfolio)
      if [ -f "$studio/TASKS.md" ]; then task_state=portfolio; else task_state="invalid (portfolio TASKS.md missing)"; fi
      ;;
    *) task_state=invalid ;;
  esac
  printf 'tasks: %s\n' "$task_state"

  connector_manifest="$studio/.mcp.json"
  if [ ! -e "$connector_manifest" ]; then
    connector_state=missing
  elif [ ! -f "$connector_manifest" ]; then
    connector_state=invalid
  else
    connector_state=$(node -e '
      const fs = require("fs");
      try {
        const value = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
        const servers = value && value.mcpServers;
        if (typeof value !== "object" || Array.isArray(value) ||
            typeof servers !== "object" || servers === null || Array.isArray(servers)) {
          process.exit(2);
        }
        const isReserved = Object.keys(value).length === 1 && Object.keys(servers).length === 0;
        process.stdout.write(isReserved ? "empty-reserved" : "configured");
      } catch (_) {
        process.exit(2);
      }
    ' "$connector_manifest" 2>/dev/null) || connector_state=invalid
  fi
  printf 'connectors: %s\n' "$connector_state"

  rows=$(mktemp "$studio/.studio-status.XXXXXX")
  findings=$(mktemp "$studio/.studio-status-findings.XXXXXX")
  trap 'rm -f "$rows" "$findings"' EXIT
  registry_rows "$studio" "$rows"
  if [ -n "$folder_taxonomy" ]; then
    projects_root=$(project_field "$studio/STUDIO.md" "Projects root")
    projects_folder_id=$(project_field "$studio/STUDIO.md" "Projects folder ID")
    operations_folder_id=$(project_field "$studio/STUDIO.md" "Operations folder ID")
    standards_folder_id=$(project_field "$studio/STUDIO.md" "Standards folder ID")
    references_folder_id=$(project_field "$studio/STUDIO.md" "References folder ID")
    actual_projects_root=$(folder_identity_resolve "$studio" "$projects_folder_id" projects)
    actual_operations_root=$(folder_identity_resolve "$studio" "$operations_folder_id" operations)
    actual_standards_root=$(folder_identity_resolve "$studio" "$standards_folder_id" standards)
    actual_references_root=$(folder_identity_resolve "$studio" "$references_folder_id" references)
    if [ "$projects_root" != "$actual_projects_root" ]; then
      printf 'folder path mismatch: %s folder-id=%s current=%s\n' "$projects_root" "$projects_folder_id" "$actual_projects_root"
      printf 'drift\n' >> "$findings"
    fi
    if [ "$operations_root" != "$actual_operations_root" ]; then
      printf 'folder path mismatch: %s folder-id=%s current=%s\n' "$operations_root" "$operations_folder_id" "$actual_operations_root"
      printf 'drift\n' >> "$findings"
    fi
    if [ "$standards_root" != "$actual_standards_root" ]; then
      printf 'folder path mismatch: %s folder-id=%s current=%s\n' "$standards_root" "$standards_folder_id" "$actual_standards_root"
      printf 'drift\n' >> "$findings"
    fi
    if [ "$references_root" != "$actual_references_root" ]; then
      printf 'folder path mismatch: %s folder-id=%s current=%s\n' "$references_root" "$references_folder_id" "$actual_references_root"
      printf 'drift\n' >> "$findings"
    fi
    projects_root=$actual_projects_root
    operations_root=$actual_operations_root
    standards_root=$actual_standards_root
    references_root=$actual_references_root
  fi
  report_identity_drift() {
    drift_path=$1
    drift_field=$2
    drift_manifest=$3
    drift_project=$4
    [ "$drift_manifest" = "$drift_project" ] && return 0
    printf 'identity mismatch: %s field=%s manifest=%s project=%s\n' "$drift_path" "$drift_field" "$drift_manifest" "$drift_project"
    printf 'drift\n' >> "$findings"
  }

  managed_folder_count=$(awk -F'\t' '$9!="" {n++} END {print n+0}' "$rows")
  legacy_folder_count=$(awk -F'\t' '$9=="" {n++} END {print n+0}' "$rows")
  printf 'folder-identities: managed=%s legacy=%s\n' "$managed_folder_count" "$legacy_folder_count"
  awk -F'\t' '
    {ids[$1]++; paths[$7]++; if ($9!="") folders[$9]++}
    END {
      for (i in ids) if (ids[i]>1) print "duplicate id: " i
      for (p in paths) if (paths[p]>1) print "duplicate path: " p
      for (f in folders) if (folders[f]>1) print "duplicate folder id: " f
    }
  ' "$rows"

  while IFS=$'\t' read -r project_id project_name client client_code project_type project_status relative_path opened folder_id; do
    [ -n "$relative_path" ] || continue
    cached_path=$relative_path
    if [ -n "$folder_id" ]; then
      if ! folder_identity_valid_id "$folder_id"; then
        printf 'project invalid: %s reason=registry Folder ID is invalid\n' "$cached_path"
        printf 'invalid\n' >> "$findings"
        continue
      fi
      folder_matches=$(folder_identity_find "$studio" "$folder_id" || true)
      folder_match_count=$(printf '%s\n' "$folder_matches" | sed '/^$/d' | wc -l | tr -d ' ')
      if [ "$folder_match_count" -ne 1 ]; then
        printf 'project invalid: %s reason=folder identity %s resolves to %s managed folders\n' "$cached_path" "$folder_id" "$folder_match_count"
        printf 'invalid\n' >> "$findings"
        continue
      fi
      IFS=$'\t' read -r relative_path folder_kind <<< "$folder_matches"
      if [ "$folder_kind" != project ]; then
        printf 'project invalid: %s reason=folder identity %s has kind %s\n' "$cached_path" "$folder_id" "$folder_kind"
        printf 'invalid\n' >> "$findings"
        continue
      fi
      if [ "$cached_path" != "$relative_path" ]; then
        printf 'folder path mismatch: %s folder-id=%s current=%s\n' "$cached_path" "$folder_id" "$relative_path"
        printf 'drift\n' >> "$findings"
      fi
    fi
    project="$studio/$relative_path"
    audit_reason=
    safe_relative_path "$relative_path" || audit_reason="unsafe registry path"
    if [ -z "$audit_reason" ] && project_path_is_reserved "$studio" "$relative_path"; then audit_reason="project uses a reserved studio resource folder"; fi
    if [ -z "$audit_reason" ] && { [ ! -d "$project" ] || [ -L "$project" ]; }; then audit_reason="project directory is missing or symlinked"; fi
    if [ -z "$audit_reason" ] && { [ ! -f "$project/PROJECT.md" ] || [ -L "$project/PROJECT.md" ]; }; then audit_reason="PROJECT.md is missing or symlinked"; fi
    if [ -z "$audit_reason" ] && [ -n "$folder_id" ]; then
      parsed_folder=$(folder_identity_parse "$project") || audit_reason="$FOLDER_IDENTITY_FILE is missing or invalid"
      if [ -z "$audit_reason" ]; then
        IFS=$'\t' read -r parsed_folder_id parsed_folder_kind <<< "$parsed_folder"
        [ "$parsed_folder_id" = "$folder_id" ] || audit_reason="folder identity does not match the registry"
        [ "$parsed_folder_kind" = project ] || audit_reason="folder identity kind is not project"
      fi
    fi
    if [ -z "$audit_reason" ] && audit_ancestor=$(project_ancestor "$studio" "$relative_path"); then
      audit_reason="project is nested inside $audit_ancestor"
    fi
    if [ -z "$audit_reason" ]; then
      if audit_physical_project=$(cd -P -- "$project" 2>/dev/null && pwd); then
        audit_physical_studio=$(cd -P -- "$studio" && pwd)
        case "$audit_physical_project/" in "$audit_physical_studio"/*/) ;; *) audit_reason="project resolves outside its studio" ;; esac
        if [ -z "$audit_reason" ] && [ "$audit_physical_project" != "$audit_physical_studio/$relative_path" ]; then
          audit_reason="project path contains a symlink"
        fi
      else
        audit_reason="project path cannot be resolved"
      fi
    fi
    if [ -n "$audit_reason" ]; then
      printf 'project invalid: %s reason=%s\n' "$cached_path" "$audit_reason"
      printf 'invalid\n' >> "$findings"
      continue
    fi

    file_version=$(project_field "$project/PROJECT.md" "Format version")
    if [ "$file_version" != 3 ]; then
      printf 'project invalid: %s reason=format-version-%s\n' "$cached_path" "${file_version:-absent}"
      printf 'invalid\n' >> "$findings"
    fi
    file_id=$(project_field "$project/PROJECT.md" "Project ID")
    file_name=$(project_field "$project/PROJECT.md" "Project")
    file_client=$(project_field "$project/PROJECT.md" "Client")
    file_code=$(project_field "$project/PROJECT.md" "Client code")
    file_type=$(project_field "$project/PROJECT.md" "Type")
    file_status=$(project_field "$project/PROJECT.md" "Status")
    file_opened=$(project_field "$project/PROJECT.md" "Created")
    report_identity_drift "$cached_path" "Project ID" "$project_id" "$file_id"
    report_identity_drift "$cached_path" Project "$project_name" "$file_name"
    report_identity_drift "$cached_path" Client "$client" "$file_client"
    report_identity_drift "$cached_path" Code "$client_code" "$file_code"
    report_identity_drift "$cached_path" Type "$project_type" "$file_type"
    report_identity_drift "$cached_path" Status "$project_status" "$file_status"
    report_identity_drift "$cached_path" Opened "$opened" "$file_opened"
  done < "$rows"

  while IFS= read -r project_file; do
    project_dir=${project_file%/PROJECT.md}
    relative_path=${project_dir#"$studio/"}
    project_folder_id=
    if parsed_folder=$(folder_identity_parse "$project_dir"); then
      IFS=$'\t' read -r candidate_folder_id candidate_folder_kind <<< "$parsed_folder"
      if [ "$candidate_folder_kind" = project ]; then project_folder_id=$candidate_folder_id; fi
    fi
    if ! awk -F'\t' -v path="$relative_path" -v folder_id="$project_folder_id" \
      '$7==path || (folder_id!="" && $9==folder_id) {found=1} END {exit found ? 0 : 1}' "$rows"; then
      printf 'unregistered: %s\n' "$relative_path"
      printf 'unregistered\n' >> "$findings"
    fi
  done < <(find "$studio" \
    \( -path "$studio/.git" -o -path "$studio/.agents" -o -path "$studio/.claude" \
       -o -path "$studio/${operations_root:-operations}" -o -path "$studio/${standards_root:-standards}" -o -path "$studio/${references_root:-references}" \
       -o -name node_modules -o -name .next -o -name '.project-status-transaction.*' -o -name '.v3-migration-transaction.*' -o -name '.task-mode-transaction.*' \) -prune -o \
    -mindepth 2 -name PROJECT.md -type f -print 2>/dev/null)

  registered_count=$(wc -l < "$rows" | tr -d ' ')
  drift_count=$(awk '$0=="drift" {n++} END {print n+0}' "$findings")
  invalid_count=$(awk '$0=="invalid" {n++} END {print n+0}' "$findings")
  unregistered_count=$(awk '$0=="unregistered" {n++} END {print n+0}' "$findings")
  printf 'status-summary\tregistered=%s\tdrift=%s\tinvalid=%s\tunregistered=%s\n' "$registered_count" "$drift_count" "$invalid_count" "$unregistered_count"
  rm -f "$rows" "$findings"
  trap - EXIT
}

parse_migration_manifest() {
  manifest=$1
  output=$2
  awk -F'\t' '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    NR==1 {
      for (i=1; i<=NF; i++) {
        heading=trim($i)
        if (heading in column) exit 3
        column[heading]=i
      }
      required[1]="Old Project ID"; required[2]="Old Folder"; required[3]="Project ID"
      required[4]="Project"; required[5]="Client"; required[6]="Code"
      required[7]="Type"; required[8]="Status"; required[9]="Opened"
      for (i=1; i<=9; i++) if (!(required[i] in column)) exit 3
      next
    }
    NF>1 {
      print trim($(column["Old Project ID"])) "\t" trim($(column["Old Folder"])) "\t" \
            trim($(column["Project ID"])) "\t" trim($(column["Project"])) "\t" \
            trim($(column["Client"])) "\t" trim($(column["Code"])) "\t" \
            trim($(column["Type"])) "\t" trim($(column["Status"])) "\t" \
            trim($(column["Opened"]))
      rows++
    }
    END {if (NR<1) exit 3}
  ' "$manifest" > "$output" || die "migration manifest is invalid"
}

legacy_registry_rows() {
  studio=$1
  output=$2
  awk -F'|' '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /<!-- projects:start -->/ {starts++; inside=1; next}
    /<!-- projects:end -->/ {ends++; inside=0; next}
    inside && /^\|/ && !header {
      for (i=2; i<NF; i++) column[trim($i)]=i
      required[1]="Project ID"; required[2]="Project"; required[3]="Folder"; required[4]="Registration"; required[5]="Registered"
      for (i=1; i<=5; i++) if (!(required[i] in column)) exit 3
      header=1
      next
    }
    inside && /^\|/ {
      id=trim($(column["Project ID"]))
      if (id ~ /^:?-+:?$/) next
      print id "\t" trim($(column["Project"])) "\t" trim($(column["Folder"])) "\t" trim($(column["Registration"])) "\t" trim($(column["Registered"]))
      rows++
    }
    END {if (starts!=1 || ends!=1 || !header) exit 3}
  ' "$studio/STUDIO.md" > "$output" || die "version 2 STUDIO.md Projects table is invalid"
}

legacy_proposal_rows() {
  studio=$1
  manifest_rows=$2
  output=$3
  : > "$output"
  [ -e "$studio/PROPOSALS.md" ] || return 0
  [ -f "$studio/PROPOSALS.md" ] && [ ! -L "$studio/PROPOSALS.md" ] || die "legacy PROPOSALS.md must be a regular file"
  proposal_version=$(project_field "$studio/PROPOSALS.md" "Format version")
  [ "$proposal_version" = 2 ] || die "legacy proposal register format is ${proposal_version:-absent}; version 2 is required"
  raw=$(mktemp "$studio/.v2-proposal-register.XXXXXX")
  if ! awk -F'|' '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /<!-- proposals:start -->/ {starts++; inside=1; next}
    /<!-- proposals:end -->/ {ends++; inside=0; next}
    inside && /^\|/ && !header {
      for (i=2; i<NF; i++) column[trim($i)]=i
      required[1]="Number"; required[2]="Project ID"; required[3]="Client"; required[4]="Title"
      required[5]="Issued"; required[6]="Status"; required[7]="Path"
      for (i=1; i<=7; i++) if (!(required[i] in column)) exit 3
      header=1
      next
    }
    inside && /^\|/ {
      number=trim($(column["Number"]))
      if (number ~ /^:?-+:?$/) next
      print number "\t" trim($(column["Project ID"])) "\t" trim($(column["Client"])) "\t" \
        trim($(column["Title"])) "\t" trim($(column["Issued"])) "\t" trim($(column["Status"])) "\t" trim($(column["Path"]))
    }
    END {if (starts!=1 || ends!=1 || !header) exit 3}
  ' "$studio/PROPOSALS.md" > "$raw"; then
    rm -f "$raw"
    die "legacy PROPOSALS.md register is invalid"
  fi

  while IFS=$'\t' read -r number old_id client title issued status old_path; do
    [ -n "$number" ] || continue
    printf '%s\n' "$number" | grep -Eq '^[A-Z][A-Z0-9]{1,5}-[0-9]{4}$' || { rm -f "$raw"; die "legacy proposal number is invalid: $number"; }
    validate_text "legacy proposal project id" "$old_id"
    validate_text "legacy proposal client" "$client"
    validate_text "legacy proposal title" "$title"
    validate_opened_date "$issued"
    case "$status" in draft|sent|accepted|declined|superseded|'superseded by '*) ;; *) rm -f "$raw"; die "legacy proposal status is invalid: $status" ;; esac
    mapping_count=$(awk -F'\t' -v id="$old_id" '$1==id {n++} END {print n+0}' "$manifest_rows")
    [ "$mapping_count" -eq 1 ] || { rm -f "$raw"; die "legacy proposal does not map to exactly one project: $number"; }
    old_folder=$(awk -F'\t' -v id="$old_id" '$1==id {print $2; exit}' "$manifest_rows")
    new_id=$(awk -F'\t' -v id="$old_id" '$1==id {print $3; exit}' "$manifest_rows")
    case "$old_path" in "$old_folder"/proposals/*.md) ;; *) rm -f "$raw"; die "legacy proposal path is outside its registered project: $number" ;; esac
    [ "$(dirname -- "$old_path")" = "$old_folder/proposals" ] || { rm -f "$raw"; die "legacy proposal must be directly inside proposals/: $number"; }
    [ -f "$studio/$old_path" ] && [ ! -L "$studio/$old_path" ] || { rm -f "$raw"; die "legacy proposal file is missing or symlinked: $old_path"; }
    old_name=$(basename -- "$old_path")
    case "$old_name" in "$number"-*.md) ;; *) rm -f "$raw"; die "legacy proposal filename does not match its number: $number" ;; esac
    slug=${old_name#"$number"-}
    slug=${slug%.md}
    case "$slug" in ''|*[!a-z0-9-]*|-*|*-) rm -f "$raw"; die "legacy proposal slug is invalid: $old_path" ;; esac
    month=${issued%-??}
    series_count=$(awk -F'\t' -v id="$new_id" -v month="$month" -v slug="$slug" '$5==id && $10==month && $11==slug {n++} END {print n+0}' "$output")
    revision=$(printf 'rev-%02d' $((series_count + 1)))
    new_folder=$(awk -F'\t' -v id="$old_id" '$1==id {print $2; exit}' "$manifest_rows")
    new_path="$new_folder/proposals/$month-$slug-proposal-$revision.md"
    if awk -F'\t' -v path="$new_path" '$9==path {found=1} END {exit found ? 0 : 1}' "$output"; then rm -f "$raw"; die "proposal migration target collides: $new_path"; fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$number" "$old_id" "$client" "$title" "$new_id" "$issued" "$status" "$old_path" "$new_path" "$month" "$slug" "$revision" >> "$output"
  done < "$raw"
  rm -f "$raw"

  resolved=$(mktemp "$studio/.v2-proposal-resolved.XXXXXX")
  while IFS=$'\t' read -r number old_id client title new_id issued status old_path new_path month slug revision; do
    [ -n "$number" ] || continue
    related=—
    case "$status" in
      'superseded by '*)
        related_number=${status#superseded by }
        related_count=$(awk -F'\t' -v number="$related_number" '$1==number {n++} END {print n+0}' "$output")
        if [ "$related_count" -ne 1 ]; then
          rm -f "$resolved" "$output"
          die "legacy proposal supersession must resolve exactly once: $number -> $related_number"
        fi
        related_project=$(awk -F'\t' -v number="$related_number" '$1==number {print $5; exit}' "$output")
        if [ "$related_project" != "$new_id" ]; then
          rm -f "$resolved" "$output"
          die "legacy proposal supersession crosses project boundaries: $number -> $related_number"
        fi
        related_target=$(awk -F'\t' -v number="$related_number" '$1==number {print $9; exit}' "$output")
        related_folder=$(awk -F'\t' -v id="$old_id" '$1==id {print $2; exit}' "$manifest_rows")
        related_prefix="$related_folder/"
        case "$related_target" in
          "$related_prefix"proposals/*.md) related=${related_target#"$related_prefix"} ;;
          *)
            rm -f "$resolved" "$output"
            die "resolved supersession is not a project-relative proposal path: $number -> $related_number"
            ;;
        esac
        ;;
    esac
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$number" "$old_id" "$client" "$title" "$new_id" "$issued" "$status" "$old_path" "$new_path" "$month" "$slug" "$revision" "$related" >> "$resolved"
  done < "$output"
  mv "$resolved" "$output"
}

write_v3_registry_from_migration() {
  local studio=$1
  local manifest_rows=$2
  local target=$3
  local naming_policy=${4:-as}
  local project_id_convention=${5:-YYMMDD-CCC-PROJECT-NAME}
  local projected versioned folder_id
  projected=$(mktemp "$studio/.v3-registry-rows.XXXXXX")
  versioned=$(mktemp "$studio/.v3-studio-version.XXXXXX")
  : > "$projected"
  while IFS=$'\t' read -r _old_id old_folder new_id name client code project_type project_status opened; do
    [ -n "$old_folder" ] || continue
    folder_id=
    if [ -e "$studio/$old_folder/$FOLDER_IDENTITY_FILE" ] || [ -L "$studio/$old_folder/$FOLDER_IDENTITY_FILE" ]; then
      folder_id=$(folder_identity_require "$studio/$old_folder" project)
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$new_id" "$name" "$client" "$code" "$project_type" "$project_status" "$old_folder" "$opened" "$folder_id" >> "$projected"
  done < "$manifest_rows"
  awk -F'|' -v naming_policy="$naming_policy" -v project_id_convention="$project_id_convention" '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /^\|/ && trim($2)=="Format version" {print "| Format version | 3 |"; next}
    /^\|/ && (trim($2)=="Project naming" || trim($2)=="Project ID convention") {next}
    /^\|/ && trim($2)=="Task register" {
      print
      print "| Project naming | " naming_policy " |"
      print "| Project ID convention | " project_id_convention " |"
      next
    }
    {print}
  ' "$studio/STUDIO.md" > "$versioned"
  write_registry "$studio" "$projected" "$target" "$versioned"
  rm -f "$projected" "$versioned"
}

rewrite_portfolio_project_ids() {
  source=$1
  manifest_rows=$2
  target=$3
  awk -F'|' -v OFS='|' -v mapping_file="$manifest_rows" '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    BEGIN {
      while ((getline row < mapping_file)>0) {
        split(row, value, "\t")
        replacement[value[1]]=value[3]
      }
      close(mapping_file)
    }
    /^\|/ && !table {
      project_column=0
      for (i=2; i<NF; i++) if (trim($i)=="Project ID") project_column=i
      if (project_column) table=1
      print
      next
    }
    table && !/^\|/ {table=0; project_column=0; print; next}
    table && /^\|/ {
      current=trim($(project_column))
      if (current in replacement) $(project_column)=" " replacement[current] " "
      print
      next
    }
    {print}
  ' "$source" > "$target"
}

migrate_studio() {
  studio=$1
  manifest=$2
  mode=${3:-preview}
  naming_policy=${4:-as}
  project_id_convention=${5:-}
  if [ -z "$project_id_convention" ]; then
    case "$naming_policy" in
      as) project_id_convention=YYMMDD-CCC-PROJECT-NAME ;;
      none) project_id_convention='No convention' ;;
      firm) die "firm project naming requires a convention" ;;
    esac
  fi
  validate_root "$studio"
  [ -d "$studio" ] || die "studio root is not a directory: $studio"
  require_owned_studio_file "$studio" STUDIO.md required
  require_owned_studio_file "$studio" TASKS.md optional
  [ -f "$manifest" ] && [ ! -L "$manifest" ] || die "migration manifest must be a regular file"
  [ "$mode" = preview ] || [ "$mode" = --apply ] || die "migration mode must be preview or --apply"
  validate_naming_policy "$naming_policy"
  validate_text "project id convention" "$project_id_convention"
  version=$(project_field "$studio/STUDIO.md" "Format version")
  [ "$version" = 2 ] || die "studio migration requires format version 2; found ${version:-absent}"

  manifest_rows=$(mktemp "$studio/.v3-manifest-rows.XXXXXX")
  legacy_rows=$(mktemp "$studio/.v2-registry-rows.XXXXXX")
  parse_migration_manifest "$manifest" "$manifest_rows"
  legacy_registry_rows "$studio" "$legacy_rows"
  [ "$(wc -l < "$manifest_rows" | tr -d ' ')" = "$(wc -l < "$legacy_rows" | tr -d ' ')" ] || { rm -f "$manifest_rows" "$legacy_rows"; die "migration manifest must cover every registered project exactly once"; }
  awk -F'\t' '{old_ids[$1]++; old_paths[$2]++; new_ids[$3]++} END {for (x in old_ids) if(old_ids[x]!=1) exit 1; for(x in old_paths) if(old_paths[x]!=1) exit 1; for(x in new_ids) if(new_ids[x]!=1) exit 1}' "$manifest_rows" || { rm -f "$manifest_rows" "$legacy_rows"; die "migration manifest contains duplicate identities or folders"; }

  physical_studio=$(cd -P -- "$studio" && pwd)
  while IFS=$'\t' read -r old_id old_folder new_id name client code project_type project_status opened; do
    validate_text "old project id" "$old_id"
    validate_text "old project folder" "$old_folder"
    validate_project_id "$new_id"
    validate_text "project name" "$name"
    validate_text "client" "$client"
    validate_client_code "$code"
    validate_project_type "$project_type"
    validate_project_status "$project_status"
    validate_opened_date "$opened"
    safe_relative_path "$old_folder" || { rm -f "$manifest_rows" "$legacy_rows"; die "unsafe legacy project path: $old_folder"; }
    legacy_match=$(awk -F'\t' -v id="$old_id" -v path="$old_folder" '$1==id && $3==path {n++} END {print n+0}' "$legacy_rows")
    [ "$legacy_match" -eq 1 ] || { rm -f "$manifest_rows" "$legacy_rows"; die "manifest row does not uniquely match version 2 registry: $old_id"; }
    old_root="$studio/$old_folder"
    [ -d "$old_root" ] && [ ! -L "$old_root" ] && [ -f "$old_root/PROJECT.md" ] && [ ! -L "$old_root/PROJECT.md" ] || { rm -f "$manifest_rows" "$legacy_rows"; die "legacy project is missing or symlinked: $old_folder"; }
    physical_old_root=$(cd -P -- "$old_root" && pwd)
    case "$physical_old_root/" in "$physical_studio"/*/) ;; *) rm -f "$manifest_rows" "$legacy_rows"; die "legacy project resolves outside its studio: $old_folder" ;; esac
    [ "$physical_old_root" = "$physical_studio/$old_folder" ] || { rm -f "$manifest_rows" "$legacy_rows"; die "legacy project path may not contain symlinks: $old_folder"; }
    old_version=$(project_field "$old_root/PROJECT.md" "Format version")
    [ "$old_version" = 2 ] || { rm -f "$manifest_rows" "$legacy_rows"; die "legacy project format is not version 2: $old_folder"; }
    file_old_id=$(project_field "$old_root/PROJECT.md" "Project ID")
    [ -z "$file_old_id" ] || [ "$file_old_id" = "$old_id" ] || { rm -f "$manifest_rows" "$legacy_rows"; die "legacy Project ID mismatch: $old_folder"; }
    if [ "$project_type" = client ] && [ "$client" = — ]; then rm -f "$manifest_rows" "$legacy_rows"; die "client project requires a client display name: $old_id"; fi
  done < "$manifest_rows"
  proposal_rows=$(mktemp "$studio/.v2-proposal-rows.XXXXXX")
  legacy_proposal_rows "$studio" "$manifest_rows" "$proposal_rows"

  if [ "$mode" != --apply ]; then
    printf 'migration ready: studio/project format 2 -> 3\n'
    while IFS=$'\t' read -r old_id _old_folder new_id _rest; do printf '%s -> %s\n' "$old_id" "$new_id"; done < "$manifest_rows"
    while IFS=$'\t' read -r number _old_id _client _title _new_id _issued _status _old_path new_path _rest; do
      [ -n "$number" ] || continue
      printf '%s -> %s\n' "$number" "$new_path"
    done < "$proposal_rows"
    rm -f "$manifest_rows" "$legacy_rows" "$proposal_rows"
    return 0
  fi

  transaction=$(mktemp -d "$studio/.v3-migration-transaction.XXXXXX")
  cp "$studio/STUDIO.md" "$transaction/STUDIO.md"
  had_tasks=0
  if [ -f "$studio/TASKS.md" ]; then
    cp "$studio/TASKS.md" "$transaction/TASKS.md"
    had_tasks=1
  fi
  had_proposals=0
  if [ -f "$studio/PROPOSALS.md" ]; then cp "$studio/PROPOSALS.md" "$transaction/PROPOSALS.md"; had_proposals=1; fi
  cp "$manifest_rows" "$transaction/manifest-rows.tsv"
  cp "$proposal_rows" "$transaction/proposal-rows.tsv"
  if [ "$had_tasks" -eq 1 ]; then
    rewrite_portfolio_project_ids "$transaction/TASKS.md" "$manifest_rows" "$transaction/TASKS.expected.md"
  fi
  preserved_inventory="$transaction/preserved-files.tsv"
  folder_config_inventory="$transaction/folder-configs.tsv"
  : > "$preserved_inventory"
  : > "$folder_config_inventory"
  snapshot_index=0
  while IFS=$'\t' read -r _old_id old_folder _rest; do
    snapshot_index=$((snapshot_index + 1))
    cp "$studio/$old_folder/PROJECT.md" "$transaction/PROJECT.$(printf '%06d' "$snapshot_index").md"
    if [ -e "$studio/$old_folder/$FOLDER_IDENTITY_FILE" ] || [ -L "$studio/$old_folder/$FOLDER_IDENTITY_FILE" ]; then
      folder_identity_require "$studio/$old_folder" project >/dev/null
      cp "$studio/$old_folder/$FOLDER_IDENTITY_FILE" "$transaction/FOLDER.$(printf '%06d' "$snapshot_index").json"
      printf '%s\tpresent\n' "$snapshot_index" >> "$folder_config_inventory"
    else
      printf '%s\tabsent\n' "$snapshot_index" >> "$folder_config_inventory"
    fi
    while IFS= read -r -d '' preserved_source; do
      preserved_relative=${preserved_source#"$studio/$old_folder/"}
      case "$preserved_relative" in PROJECT.md|proposals/*.md) continue ;; esac
      case "$preserved_relative" in *$'\n'*|*$'\r'*|*$'\t'*) die "preserved project path contains control characters: $old_folder/$preserved_relative" ;; esac
      printf '%s\t%s\t%s\n' "$snapshot_index" "$preserved_relative" "$(file_sha256 "$preserved_source")" >> "$preserved_inventory"
    done < <(find "$studio/$old_folder" -type f -print0)
  done < "$manifest_rows"
  proposal_snapshot_index=0
  while IFS=$'\t' read -r _number _old_id _client _title _new_id _issued _status old_path _new_path _rest; do
    [ -n "$old_path" ] || continue
    proposal_snapshot_index=$((proposal_snapshot_index + 1))
    cp "$studio/$old_path" "$transaction/PROPOSAL.$(printf '%06d' "$proposal_snapshot_index").md"
  done < "$proposal_rows"
  committed=0
  rollback_migration_failure() {
    rollback_migration_label=$1
    rollback_migration_target=$2
    rollback_migration_reason=$3
    printf '%s\t%s\t%s\n' "$rollback_migration_label" "$rollback_migration_target" "$rollback_migration_reason" >> "$transaction/ROLLBACK-FAILURES.tsv"
    printf 'studio-workspace: rollback restore failed: %s (%s)\n' "$rollback_migration_label" "$rollback_migration_reason" >&2
    rollback_migration_failed=1
  }
  restore_migration_snapshot() {
    restore_migration_label=$1
    restore_migration_source=$2
    restore_migration_target=$3
    if [ "${ARCH_STUDIO_FAIL_RESTORE_AT:-}" = "$restore_migration_label" ]; then
      rollback_migration_failure "$restore_migration_label" "$restore_migration_target" "injected restore failure"
    elif ! cp "$restore_migration_source" "$restore_migration_target"; then
      rollback_migration_failure "$restore_migration_label" "$restore_migration_target" "copy failed"
    elif ! cmp -s "$restore_migration_source" "$restore_migration_target"; then
      rollback_migration_failure "$restore_migration_label" "$restore_migration_target" "verification failed"
    fi
  }
  remove_migration_path() {
    remove_migration_label=$1
    remove_migration_target=$2
    if [ "${ARCH_STUDIO_FAIL_RESTORE_AT:-}" = "$remove_migration_label" ]; then
      rollback_migration_failure "$remove_migration_label" "$remove_migration_target" "injected restore failure"
    elif [ -e "$remove_migration_target" ] || [ -L "$remove_migration_target" ]; then
      if ! rm -f "$remove_migration_target"; then
        rollback_migration_failure "$remove_migration_label" "$remove_migration_target" "remove failed"
      elif [ -e "$remove_migration_target" ] || [ -L "$remove_migration_target" ]; then
        rollback_migration_failure "$remove_migration_label" "$remove_migration_target" "verification failed"
      fi
    fi
  }
  rollback_v3_migration() {
    [ "$committed" -eq 0 ] || return 0
    rollback_migration_failed=0
    : > "$transaction/ROLLBACK-FAILURES.tsv"
    restore_migration_snapshot migration-studio "$transaction/STUDIO.md" "$studio/STUDIO.md"
    if [ "$had_tasks" -eq 1 ]; then
      restore_migration_snapshot migration-tasks "$transaction/TASKS.md" "$studio/TASKS.md"
    else
      remove_migration_path migration-tasks "$studio/TASKS.md"
    fi
    snapshot_index=0
    while IFS=$'\t' read -r _old_id old_folder _rest; do
      snapshot_index=$((snapshot_index + 1))
      if [ -d "$studio/$old_folder" ]; then
        restore_migration_snapshot migration-project "$transaction/PROJECT.$(printf '%06d' "$snapshot_index").md" "$studio/$old_folder/PROJECT.md"
        folder_config_state=$(awk -F'\t' -v index="$snapshot_index" '$1==index {print $2; exit}' "$transaction/folder-configs.tsv")
        if [ "$folder_config_state" = present ]; then
          restore_migration_snapshot migration-folder-config "$transaction/FOLDER.$(printf '%06d' "$snapshot_index").json" "$studio/$old_folder/$FOLDER_IDENTITY_FILE"
        else
          remove_migration_path migration-folder-config "$studio/$old_folder/$FOLDER_IDENTITY_FILE"
        fi
      else
        rollback_migration_failure migration-project "$studio/$old_folder/PROJECT.md" "project directory missing after rename rollback"
      fi
    done < "$transaction/manifest-rows.tsv"
    proposal_snapshot_index=0
    while IFS=$'\t' read -r _number _old_id _client _title _new_id _issued _status old_path new_path _rest; do
      [ -n "$old_path" ] || continue
      proposal_snapshot_index=$((proposal_snapshot_index + 1))
      old_dir=$(dirname -- "$old_path")
      new_name=$(basename -- "$new_path")
      remove_migration_path migration-proposal-target "$studio/$old_dir/$new_name"
      if [ -d "$studio/$old_dir" ]; then
        restore_migration_snapshot migration-proposal "$transaction/PROPOSAL.$(printf '%06d' "$proposal_snapshot_index").md" "$studio/$old_path"
      else
        rollback_migration_failure migration-proposal "$studio/$old_path" "proposal directory missing after rename rollback"
      fi
    done < "$transaction/proposal-rows.tsv"
    if [ "$had_proposals" -eq 1 ]; then
      restore_migration_snapshot migration-proposal-register "$transaction/PROPOSALS.md" "$studio/PROPOSALS.md"
    else
      remove_migration_path migration-proposal-register "$studio/PROPOSALS.md"
    fi
    [ "$rollback_migration_failed" -eq 0 ]
  }
  finalize_v3_migration() {
    final_status=$1
    trap - EXIT HUP INT TERM
    if [ "$committed" -eq 0 ]; then
      if rollback_v3_migration; then
        rm -rf "$transaction"
      else
        printf 'studio-workspace: rollback incomplete; transaction preserved: %s\n' "$transaction" >&2
      fi
    else
      rm -rf "$transaction"
    fi
    rm -f "$manifest_rows" "$legacy_rows" "$proposal_rows"
    exit "$final_status"
  }
  trap 'finalize_v3_migration $?' EXIT
  trap 'finalize_v3_migration 129' HUP
  trap 'finalize_v3_migration 130' INT
  trap 'finalize_v3_migration 143' TERM

  project_index=0
  while IFS=$'\t' read -r old_id old_folder new_id name client code project_type project_status opened; do
    project_index=$((project_index + 1))
    "$PROJECT_SCRIPT" migrate-record "$studio/$old_folder" "$new_id" "$name" "$project_type" "$project_status" "$code" "$client" "$opened" --apply >/dev/null
    folder_identity_ensure "$studio/$old_folder" project >/dev/null
    if [ "$project_index" -eq 1 ]; then
      case "${ARCH_STUDIO_FAIL_AT:-}" in migration-signal-after-first-project|migration-signal-after-first-rename) kill -TERM "$$" ;; esac
      case "${ARCH_STUDIO_FAIL_AT:-}" in migration-after-first-project|migration-after-first-rename) die "injected failure after first project upgrade" ;; esac
    fi
  done < "$manifest_rows"

  write_v3_registry_from_migration "$studio" "$manifest_rows" "$transaction/STUDIO.expected.md" "$naming_policy" "$project_id_convention"

  while IFS=$'\t' read -r number _old_id client title new_id issued status old_path _new_path _month slug revision related; do
    [ -n "$number" ] || continue
    old_name=$(basename -- "$old_path")
    project_folder=$(awk -F'\t' -v id="$new_id" '$3==id {print $2; exit}' "$manifest_rows")
    legacy_file="$studio/$project_folder/proposals/$old_name"
    "$PROPOSAL_SCRIPT" migrate-legacy "$legacy_file" "$studio/$project_folder" "$number" "$client" "$title" "$issued" "$status" "$slug" "$revision" --related "$related" --apply >/dev/null
  done < "$proposal_rows"
  [ ! -f "$studio/PROPOSALS.md" ] || rm "$studio/PROPOSALS.md"
  [ "${ARCH_STUDIO_FAIL_AT:-}" != migration-after-commercial ] || die "injected failure after commercial-record migration"

  if [ -f "$studio/TASKS.md" ]; then
    tasks_tmp=$(mktemp "$studio/.v3-tasks.XXXXXX")
    rewrite_portfolio_project_ids "$studio/TASKS.md" "$manifest_rows" "$tasks_tmp"
    mv "$tasks_tmp" "$studio/TASKS.md"
  fi
  studio_tmp=$(mktemp "$studio/.v3-studio.XXXXXX")
  write_v3_registry_from_migration "$studio" "$manifest_rows" "$studio_tmp" "$naming_policy" "$project_id_convention"
  mv "$studio_tmp" "$studio/STUDIO.md"
  [ "${ARCH_STUDIO_FAIL_AT:-}" != migration-after-manifest ] || die "injected failure after v3 manifest replacement"

  if [ "${ARCH_STUDIO_FAIL_AT:-}" = migration-corrupt-project-client ]; then
    corrupt_project=$(awk -F'\t' 'NR==1 {print $2; exit}' "$manifest_rows")
    corrupt_tmp=$(mktemp "$studio/$corrupt_project/.migration-corrupt.XXXXXX")
    awk -F'|' '
      function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
      /^\|/ && trim($2)=="Client" {print "| Client | CORRUPTED CLIENT | injected verification fault | 2026-01-01 |"; next}
      {print}
    ' "$studio/$corrupt_project/PROJECT.md" > "$corrupt_tmp"
    mv "$corrupt_tmp" "$studio/$corrupt_project/PROJECT.md"
  fi

  verify_rows="$transaction/registry-verify.tsv"
  registry_rows "$studio" "$verify_rows"
  manifest_count=$(wc -l < "$manifest_rows" | tr -d ' ')
  registry_count=$(wc -l < "$verify_rows" | tr -d ' ')
  [ "$registry_count" = "$manifest_count" ] || die "v3 registry verification failed"
  [ "$(project_field "$studio/STUDIO.md" "Format version")" = 3 ] || die "migrated studio version verification failed"
  cmp -s "$transaction/STUDIO.expected.md" "$studio/STUDIO.md" || die "migrated studio content verification failed"
  project_verify_index=0
  while IFS=$'\t' read -r old_id old_folder new_id name client code project_type project_status opened; do
    project_verify_index=$((project_verify_index + 1))
    project_root="$studio/$old_folder"
    [ -d "$project_root" ] && [ ! -L "$project_root" ] || die "migrated project directory is missing or symlinked: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Format version")" = 3 ] || die "migrated project version verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Project ID")" = "$new_id" ] || die "migrated project identity verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Project")" = "$name" ] || die "migrated project name verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Client")" = "$client" ] || die "migrated project client verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Client code")" = "$code" ] || die "migrated project code verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Type")" = "$project_type" ] || die "migrated project type verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Status")" = "$project_status" ] || die "migrated project status verification failed: $new_id"
    [ "$(project_field "$project_root/PROJECT.md" "Created")" = "$opened" ] || die "migrated project opened-date verification failed: $new_id"
    awk -F'\t' -v id="$new_id" -v name="$name" -v client="$client" -v code="$code" -v type="$project_type" -v status="$project_status" -v path="$old_folder" -v opened="$opened" '
      $1==id && $2==name && $3==client && $4==code && $5==type && $6==status && $7==path && $8==opened {found++}
      END {exit found==1 ? 0 : 1}
    ' "$verify_rows" || die "migrated registry row verification failed: $new_id"
  done < "$manifest_rows"

  tasks_state=absent
  if [ "$had_tasks" -eq 1 ]; then
    [ -f "$studio/TASKS.md" ] && [ ! -L "$studio/TASKS.md" ] || die "migrated TASKS.md is missing or symlinked"
    cmp -s "$transaction/TASKS.expected.md" "$studio/TASKS.md" || die "migrated task register differs from the expected structured-ID rewrite"
    awk -F'\t' '{print $1}' "$manifest_rows" > "$transaction/legacy-project-ids.tsv"
    awk -F'|' -v old_ids_file="$transaction/legacy-project-ids.tsv" '
      function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
      BEGIN {while ((getline id < old_ids_file)>0) old[id]=1; close(old_ids_file)}
      /^\|/ && !header {
        for (i=2; i<NF; i++) if (trim($i)=="Project ID") project_column=i
        if (project_column) {header=1; next}
      }
      header && /^\|/ {
        value=trim($(project_column))
        if (value !~ /^:?-+:?$/ && value in old) found=1
      }
      END {exit found ? 1 : 0}
    ' "$studio/TASKS.md" || die "migrated task register retains a legacy Project ID"
    tasks_state=verified
  else
    [ ! -e "$studio/TASKS.md" ] || die "migration created an unexpected TASKS.md"
  fi

  proposal_verify_index=0
  while IFS=$'\t' read -r number _old_id proposal_client title new_id issued legacy_status old_path new_path _month slug revision related; do
    [ -n "$new_path" ] || continue
    proposal_verify_index=$((proposal_verify_index + 1))
    proposal_file="$studio/$new_path"
    [ ! -e "$studio/$(dirname -- "$new_path")/$(basename -- "$old_path")" ] || die "legacy proposal remains after migration: $old_path"
    "$PROPOSAL_SCRIPT" status "$studio/$new_path" >/dev/null || die "migrated proposal verification failed: $new_path"
    [ "$(project_field "$proposal_file" "Project ID")" = "$new_id" ] || die "migrated proposal Project ID verification failed: $new_path"
    [ "$(project_field "$proposal_file" "Title")" = "$title" ] || die "migrated proposal title verification failed: $new_path"
    [ "$(project_field "$proposal_file" "Short title")" = "$slug" ] || die "migrated proposal short-title verification failed: $new_path"
    expected_revision="Rev. ${revision#rev-}"
    [ "$(project_field "$proposal_file" "Revision")" = "$expected_revision" ] || die "migrated proposal revision verification failed: $new_path"
    [ "$(project_field "$proposal_file" "Legacy number")" = "$number" ] || die "migrated proposal legacy-number verification failed: $new_path"
    case "$legacy_status" in 'superseded by '*|superseded) expected_proposal_status=superseded ;; *) expected_proposal_status=$legacy_status ;; esac
    [ "$(project_field "$proposal_file" "Status")" = "$expected_proposal_status" ] || die "migrated proposal status verification failed: $new_path"
    grep -Fq -- "| Proposal date | $issued |" "$proposal_file" || die "migrated proposal date verification failed: $new_path"
    grep -Fq -- "| To | $proposal_client |" "$proposal_file" || die "migrated proposal client verification failed: $new_path"
    grep -Fq -- "| Project | $new_id |" "$proposal_file" || die "migrated proposal issued-project verification failed: $new_path"
    grep -Fq -- "| $expected_proposal_status | — | legacy migration | legacy number $number | $related |" "$proposal_file" || die "migrated proposal lifecycle verification failed: $new_path"
    extracted_legacy="$transaction/PROPOSAL.$(printf '%06d' "$proposal_verify_index").extracted.md"
    awk -v project_id="$new_id" '
      $0=="| Project | " project_id " |" {project_row=1; next}
      project_row && !content && $0=="" {content=1; next}
      content && $0=="<!-- issued-terms:end -->" {done=1; exit}
      content {line[++count]=$0}
      END {
        if (!done) exit 3
        if (count>0 && line[count]=="") count--
        for (i=1; i<=count; i++) print line[i]
      }
    ' "$proposal_file" > "$extracted_legacy" || die "migrated proposal content boundary verification failed: $new_path"
    cmp -s "$transaction/PROPOSAL.$(printf '%06d' "$proposal_verify_index").md" "$extracted_legacy" || die "migrated proposal legacy content changed: $new_path"
  done < "$proposal_rows"

  preserved_count=0
  while IFS=$'\t' read -r inventory_index preserved_relative expected_hash; do
    [ -n "$preserved_relative" ] || continue
    preserved_count=$((preserved_count + 1))
    preserved_project=$(awk -F'\t' -v row="$inventory_index" 'NR==row {print $2; exit}' "$manifest_rows")
    preserved_target="$studio/$preserved_project/$preserved_relative"
    [ -f "$preserved_target" ] && [ ! -L "$preserved_target" ] || die "preserved project content is missing or symlinked: $preserved_project/$preserved_relative"
    [ "$(file_sha256 "$preserved_target")" = "$expected_hash" ] || die "preserved project content changed: $preserved_project/$preserved_relative"
  done < "$preserved_inventory"
  [ ! -e "$studio/PROPOSALS.md" ] || die "legacy proposal register remains after migration"
  proposal_count=$(wc -l < "$proposal_rows" | tr -d ' ')
  printf 'migration-verification\tprojects=%s\tregistry=%s\ttasks=%s\tproposals=%s\tpreserved-files=%s\n' \
    "$manifest_count" "$registry_count" "$tasks_state" "$proposal_count" "$preserved_count"
  committed=1
  rm -rf "$transaction"
  rm -f "$manifest_rows" "$legacy_rows" "$proposal_rows"
  trap - EXIT HUP INT TERM
  printf 'migrated studio: %s\n' "$studio"
}

task_mode_studio() {
  studio=$1
  requested=$2
  require_studio "$studio"
  case "$requested" in
    project|portfolio) ;;
    *) die "task mode must be project or portfolio" ;;
  esac

  current=$(awk -F'|' '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /^\|/ && trim($2)=="Task register" {print trim($3); exit}
  ' "$studio/STUDIO.md")
  [ -n "$current" ] || die "STUDIO.md has no Task register setting"
  [ "$current" != "$requested" ] || die "task mode is already $requested"

  rows=$(mktemp "$studio/.studio-task-mode-rows.XXXXXX")
  all_rows=$(mktemp "$studio/.studio-task-mode-all.XXXXXX")
  registry_rows "$studio" "$all_rows"
  : > "$rows"
  while IFS=$'\t' read -r project_id _project_name _client _code _type _status cached_path _opened folder_id; do
    [ -n "$cached_path" ] || continue
    relative_path=$(resolve_registered_project_path "$studio" "$cached_path" "$folder_id")
    printf '%s\t%s\t%s\n' "$project_id" "$relative_path" "$folder_id" >> "$rows"
  done < "$all_rows"
  rm -f "$all_rows"

  if awk -F'\t' '{ids[$1]++; paths[$2]++; if ($3!="") folders[$3]++} END {for (i in ids) if (ids[i]>1) exit 1; for (p in paths) if (paths[p]>1) exit 1; for (f in folders) if (folders[f]>1) exit 1}' "$rows"; then
    :
  else
    die "task mode requires unique project ids and paths"
  fi
  while IFS=$'\t' read -r _ relative_path folder_id; do
    [ -n "$relative_path" ] || continue
    safe_relative_path "$relative_path" || die "unsafe registered project path: $relative_path"
    require_safe_project "$studio" "$relative_path" "$folder_id"
  done < "$rows"

  # Snapshot every touched file. The EXIT trap restores the snapshot unless the
  # manifest replacement and topology verification both complete.
  transaction=$(mktemp -d "$studio/.task-mode-transaction.XXXXXX")
  cp "$studio/STUDIO.md" "$transaction/STUDIO.md"
  [ ! -f "$studio/TASKS.md" ] || cp "$studio/TASKS.md" "$transaction/studio.TASKS.md"
  snapshot_index=0
  while IFS=$'\t' read -r _ relative_path _folder_id; do
    [ -n "$relative_path" ] || continue
    snapshot_index=$((snapshot_index + 1))
    snapshot=$(printf 'project-%06d.TASKS.md' "$snapshot_index")
    [ ! -f "$studio/$relative_path/TASKS.md" ] || cp "$studio/$relative_path/TASKS.md" "$transaction/$snapshot"
  done < "$rows"
  committed=0
  rollback_task_mode() {
    [ "$committed" -eq 0 ] || return 0
    cp "$transaction/STUDIO.md" "$studio/STUDIO.md" 2>/dev/null || true
    if [ -f "$transaction/studio.TASKS.md" ]; then cp "$transaction/studio.TASKS.md" "$studio/TASKS.md"; else rm -f "$studio/TASKS.md"; fi
    snapshot_index=0
    while IFS=$'\t' read -r _ relative_path _folder_id; do
      [ -n "$relative_path" ] || continue
      snapshot_index=$((snapshot_index + 1))
      snapshot=$(printf 'project-%06d.TASKS.md' "$snapshot_index")
      if [ -f "$transaction/$snapshot" ]; then cp "$transaction/$snapshot" "$studio/$relative_path/TASKS.md"; else rm -f "$studio/$relative_path/TASKS.md"; fi
    done < "$rows"
  }
  cleanup_task_mode() { rm -rf "$transaction"; rm -f "$rows"; }
  signal_task_mode() {
    signal_status=$1
    trap - EXIT HUP INT TERM
    rollback_task_mode
    cleanup_task_mode
    exit "$signal_status"
  }
  trap 'rollback_task_mode; cleanup_task_mode' EXIT
  trap 'signal_task_mode 129' HUP
  trap 'signal_task_mode 130' INT
  trap 'signal_task_mode 143' TERM

  if [ "$requested" = portfolio ]; then
    [ ! -e "$studio/TASKS.md" ] || die "studio TASKS.md already exists"
    while IFS=$'\t' read -r project_id relative_path _folder_id; do
      [ -n "$relative_path" ] || continue
      register="$studio/$relative_path/TASKS.md"
      if [ -f "$register" ] && grep -Eq '^\| T[0-9]{4} \|' "$register"; then
        die "project $project_id has task rows; migration is required"
      fi
    done < "$rows"
    cp "$TASK_TEMPLATE_DIR/portfolio-tasks.md" "$transaction/studio.TASKS.new"
    [ "${ARCH_STUDIO_FAIL_AT:-}" != after-stage ] || die "injected failure after staging task mode"
    mv "$transaction/studio.TASKS.new" "$studio/TASKS.md"
    while IFS=$'\t' read -r _ relative_path _folder_id; do
      [ -n "$relative_path" ] || continue
      [ ! -f "$studio/$relative_path/TASKS.md" ] || rm "$studio/$relative_path/TASKS.md"
    done < "$rows"
  else
    [ -f "$studio/TASKS.md" ] || die "studio TASKS.md not found"
    if grep -Eq '^\| T[0-9]{4} \|' "$studio/TASKS.md"; then
      die "portfolio register has task rows; split migration is required"
    fi
    while IFS=$'\t' read -r _ relative_path _folder_id; do
      [ -n "$relative_path" ] || continue
      [ -f "$studio/$relative_path/PROJECT.md" ] || continue
      [ -e "$studio/$relative_path/TASKS.md" ] || cp "$PROJECT_TEMPLATE_DIR/TASKS.md" "$studio/$relative_path/TASKS.md"
    done < "$rows"
    rm "$studio/TASKS.md"
  fi

  tmp=$(mktemp "$studio/.studio-task-mode.XXXXXX")
  awk -F'|' -v requested="$requested" '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    /^\|/ && trim($2)=="Task register" {print "| Task register | " requested " |"; next}
    {print}
  ' "$studio/STUDIO.md" > "$tmp"
  [ "${ARCH_STUDIO_FAIL_AT:-}" != before-manifest ] || die "injected failure before task-mode manifest replacement"
  mv "$tmp" "$studio/STUDIO.md"
  [ "${ARCH_STUDIO_FAIL_AT:-}" != signal-after-manifest ] || kill -TERM "$$"
  [ "${ARCH_STUDIO_FAIL_AT:-}" != after-manifest ] || die "injected failure after task-mode manifest replacement"
  committed=1
  rm -rf "$transaction"
  rm -f "$rows"
  trap - EXIT HUP INT TERM
  printf 'task mode: %s\n' "$requested"
}

case "${1:-}" in
  init) [ "$#" -ge 7 ] && [ "$#" -le 15 ] || die "usage: $0 init <target> <studio-name> <working-units> <country> <state-region> <city> [as|firm|none] [project-id-convention] [as|firm folder-taxonomy] [project-folder-convention] [projects-root] [operations-root] [standards-root] [references-root]"; init_studio "$2" "$3" "$4" "$5" "$6" "$7" "${8:-as}" "${9:-}" "${10:-as}" "${11:-}" "${12:-}" "${13:-}" "${14:-}" "${15:-}" ;;
  register) [ "$#" -eq 5 ] || die "usage: $0 register <studio-root> <project-id> <project-name> <relative-path>"; register_project "$2" "$3" "$4" "$5" ;;
  set-status) [ "$#" -eq 4 ] || die "usage: $0 set-status <studio-root> <project-id> <prospective|active|on-hold|lost|withdrawn|completed|archived>"; set_project_status "$2" "$3" "$4" ;;
  set-naming) [ "$#" -eq 4 ] || die "usage: $0 set-naming <studio-root> <as|firm|none> <project-id-convention>"; set_project_naming "$2" "$3" "$4" ;;
  archive) [ "$#" -eq 3 ] || die "usage: $0 archive <studio-root> <project-id>"; set_project_status "$2" "$3" archived ;;
  migrate) [ "$#" -ge 3 ] && [ "$#" -le 6 ] || die "usage: $0 migrate <studio-root> <confirmed-manifest.tsv> [--apply] [as|firm|none] [project-id-convention]"; migrate_studio "$2" "$3" "${4:-preview}" "${5:-as}" "${6:-}" ;;
  status) [ "$#" -eq 2 ] || die "usage: $0 status <studio-root>"; status_studio "$2" ;;
  task-mode) [ "$#" -eq 3 ] || die "usage: $0 task-mode <studio-root> <project|portfolio>"; task_mode_studio "$2" "$3" ;;
  *) die "usage: $0 {init|register|set-status|set-naming|archive|migrate|status|task-mode} ..." ;;
esac
