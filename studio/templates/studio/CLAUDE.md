# {{STUDIO_NAME}} — Studio Instructions

This folder is the studio worksurface.

- Read `STUDIO.md` to find registered projects.
- Use the working-unit and default-jurisdiction settings in `STUDIO.md` unless a project records an explicit override.
- Firm-created Claude Code skills live in `.claude/skills/`; Codex skills use the parallel `.agents/skills/` root.
- Ongoing studio operations and administrative records live in `{{OPERATIONS_ROOT}}/`.
- Firm-wide standards and reusable templates live in `{{STANDARDS_ROOT}}/`.
- External references, including code references, live in `{{REFERENCES_ROOT}}/`.
- Project work and project outputs stay inside each registered project directory; `{{PROJECTS_ROOT}}/` is the default location.
- The recorded project-folder convention is `{{PROJECT_FOLDER_CONVENTION}}`.
- `.as-folder.json` carries immutable IDs for Arch Studio-managed folders; names and paths remain human-facing and may change through a confirmed studio operation.
- Project facts live in each project’s `PROJECT.md`.
- Decision rationale lives in each project’s registered documents of kind `decision` in `DOCUMENTS.csv`.
- Never treat the installed Arch Studio plugin cache as a project or private-skill destination.
- This local version does not store workspace data with ALPA. Treat the configured LLM provider and account terms as the boundary for content sent to the model.
