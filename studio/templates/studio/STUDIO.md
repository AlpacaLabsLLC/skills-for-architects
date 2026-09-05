# Architecture Studio — {{STUDIO_NAME}}

> Portable studio manifest. The studio skill is the only writer of this registry.
> Project details remain in each project’s `PROJECT.md`.

## Studio defaults

| Setting | Default |
|---|---|
| Format version | 3 |
| Working units | {{WORKING_UNITS}} |
| Country | {{COUNTRY}} |
| State / region | {{STATE_REGION}} |
| City | {{CITY}} |
| Task register | project |
| Project naming | {{NAMING_POLICY}} |
| Project ID convention | {{PROJECT_ID_CONVENTION}} |
| Folder taxonomy | {{FOLDER_TAXONOMY}} |
| Project folder convention | {{PROJECT_FOLDER_CONVENTION}} |
| Studio folder ID | {{STUDIO_FOLDER_ID}} |
| Projects root | {{PROJECTS_ROOT}} |
| Projects folder ID | {{PROJECTS_FOLDER_ID}} |
| Operations root | {{OPERATIONS_ROOT}} |
| Operations folder ID | {{OPERATIONS_FOLDER_ID}} |
| Standards root | {{STANDARDS_ROOT}} |
| Standards folder ID | {{STANDARDS_FOLDER_ID}} |
| References root | {{REFERENCES_ROOT}} |
| References folder ID | {{REFERENCES_FOLDER_ID}} |

## Data governance

This local version stores studio and project records in this workspace. Architecture Studio does not send them to or store them with ALPA. Content provided to the configured LLM is handled by that provider under the user’s account and data terms. Future cloud-based versions may require an account and use different storage.

## Studio resources

- Ongoing studio operations and administrative records: `{{OPERATIONS_ROOT}}/`
- Firm-wide standards and reusable templates: `{{STANDARDS_ROOT}}/`
- External references, including code references: `{{REFERENCES_ROOT}}/`

Project work and project outputs remain inside their registered owning project under `{{PROJECTS_ROOT}}/`, unless the recorded firm taxonomy places an existing project elsewhere.

## Projects

<!-- projects:start -->
| Project ID | Project | Client | Code | Type | Status | Folder | Opened | Folder ID |
|---|---|---|---|---|---|---|---|---|
<!-- projects:end -->
