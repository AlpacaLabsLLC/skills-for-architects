# /as:studio

Architecture Studio’s control plane: initialize a portable studio workspace, list or register projects, create a project through the project-owned scaffold, or route an architecture task.

Invoking `/as:studio` with no arguments shows the Architecture Studio mark, creator and ALPA ownership, license, contact, and repository provenance. If no studio is open, it offers four paths: set up a studio, use the installed tools without setup, learn with an example, or open an existing studio. Tools-only use creates no files or copied skills, and `/as:studio` remains available whenever persistent settings and project records become useful.

Studio setup records working units, default country/state-or-region/city, project-naming policy, folder taxonomy, and the local-data governance boundary before creating files. Naming can use the AS suggestion, preserve a firm convention, or impose no convention. Folder taxonomy separately uses the human-readable AS standard or the user's own recorded hierarchy. Each question or confirmation uses one interaction gate rather than a prose question followed by a duplicate UI prompt.

```text
/as:studio init
/as:studio status
/as:studio create-project
/as:studio register-project 10-PROJECTS/CLIENT/260901-SMI-MUSEUM-EXPANSION
/as:studio set-project-naming firm "Use the Deltek project number"
/as:studio set-project-status 260901-SMI-MUSEUM-EXPANSION on-hold
/as:studio archive-project 260901-SMI-MUSEUM-EXPANSION
/as:studio migrate migration.tsv
/as:studio updates status
/as:studio updates enable
/as:studio updates disable
/as:studio I need a space program for 200 people
```

`STUDIO.md` is the sole studio manifest and the studio skill is its only writer. Studio-owned custom skills live in `.agents/skills/` on Codex or `.claude/skills/` on Claude Code; project memory remains owned by the project skill. New studios also reserve a studio-only connector boundary with an empty `.mcp.json`; no connector or authentication is configured, and project scaffolds never receive this file.

The AS folder standard creates parallel `Projects/`, `Operations/`, `Standards/`, and `References/` roots. Projects use `Projects/{Client Account or Internal}/{YYYYMM} {Project Name}`; a firm-defined taxonomy may record different safe relative roots and a different convention. There is no separate workspace `templates/` folder.

Workspace format 3 registers all internal and client work in one section-bounded, header-keyed Projects table: Project ID, Project, Client, Code, Type, Status, Folder, Opened, and Folder ID. Project ID, display name, code, readable folder, and Folder ID are independent. Project and Folder IDs are immutable; human names and paths may change. A minimal `.as-folder.json` at every AS-indexed folder provides the durable pointer, while the manifest path stays legible and status reports path drift. The AS Project ID convention remains advisory. Every valid unique row remains resolvable regardless of status or naming policy.

Studio migration is transactional and recovery-aware. It preserves registered project folders, emits a tab-separated `migration-verification` summary after successful verification, and removes verified rollback transactions. If any restore cannot be verified, the command reports the failed operation and preserves the hidden transaction directory with snapshots and `ROLLBACK-FAILURES.tsv` for manual recovery.

Under the AS convention, Project and Client remain distinct when constructing an ID. For client `SOM` and project `Strategy consulting`, suggest `260901-SOM-STRATEGY-CONSULTING`; do not repeat the client name in the project slug.

Studios default to project task mode, with one canonical `TASKS.md` per project. `/as:studio tasks mode portfolio` can move an empty studio to one studio-root register; populated registers require an explicit migration so two writable task sources can never drift.

Background update checking is disabled by default. The `updates` commands manage a global local preference explicitly. When enabled, the check sends no project content or Architecture Studio identifier, but Cloudflare handles ordinary web-request metadata such as IP address, headers, and timestamps.
