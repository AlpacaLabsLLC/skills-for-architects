# Arch Studio — {{STUDIO_NAME}}

> Portable studio manifest. The studio skill is the only writer of this registry.
> Project details remain in each project’s `PROJECT.md`.

## Studio defaults

| Setting | Value |
|---|---|
| Format version | 3 |
| Document model | 1 |
| Studio | {{STUDIO_NAME}} |
| Document path template | {{DOCUMENT_PATH_TEMPLATE}} |
| Working units | {{WORKING_UNITS}} |
| Country | {{COUNTRY}} |
| State/region | {{STATE_REGION}} |
| City | {{CITY}} |
| Task register | {{TASK_MODE}} |
| Project naming | {{NAMING_POLICY}} |
| Project ID convention | {{PROJECT_ID_CONVENTION}} |
| Folder taxonomy | {{FOLDER_TAXONOMY}} |
| Project folder convention | {{PROJECT_FOLDER_CONVENTION}} |
| Folder ID | {{STUDIO_FOLDER_ID}} |
| Projects root | {{PROJECTS_ROOT}} |
| Projects folder ID | {{PROJECTS_FOLDER_ID}} |
| Operations root | {{OPERATIONS_ROOT}} |
| Operations folder ID | {{OPERATIONS_FOLDER_ID}} |
| Standards root | {{STANDARDS_ROOT}} |
| Standards folder ID | {{STANDARDS_FOLDER_ID}} |
| References root | {{REFERENCES_ROOT}} |
| References folder ID | {{REFERENCES_FOLDER_ID}} |

## Data governance

| Setting | Value |
|---|---|
| Firm policy | {{FIRM_POLICY}} |
| Firm policy adoption | {{FIRM_POLICY_ADOPTION}} |

The recorded policy complements existing governance, including provenance; it does not replace those authoritative rules. Read the current referenced document for policy-dependent work. `None` with `declined` records an explicit choice to continue under existing governance without adopting a policy.

This local version stores studio and project records in this workspace. Arch Studio does not send them to or store them with ALPA. Content provided to the configured LLM is handled by that provider under the user’s account and data terms. Future cloud-based versions may require an account and use different storage.

## Studio resources

- Ongoing studio operations and administrative records: `{{OPERATIONS_ROOT}}/`
- Firm-wide standards and reusable templates: `{{STANDARDS_ROOT}}/`
- External references, including code references: `{{REFERENCES_ROOT}}/`

Project work and project outputs remain inside their registered owning project under `{{PROJECTS_ROOT}}/`, unless the recorded firm taxonomy places an existing project elsewhere.

## Projects

<!-- projects:start -->
| Project ID | Project | Client | Code | Type | Kind | Status | Folder | Opened | Folder ID |
|---|---|---|---|---|---|---|---|---|---|
<!-- projects:end -->

## Firm stages

The following names are confirmed firm vocabulary, not asserted external normative phase definitions.

<!-- stages:start -->
| Kind | Value |
|---|---|
{{STAGE_ROWS}}
<!-- stages:end -->

## Proposed scopes by Kind

<!-- default-scopes:start -->
| Kind | Value |
|---|---|
{{DEFAULT_SCOPE_ROWS}}
<!-- default-scopes:end -->
