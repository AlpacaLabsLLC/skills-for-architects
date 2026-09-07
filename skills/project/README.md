# /as:project

The single interface for Architecture Studio project setup and memory.

```text
/as:project init
/as:project status
/as:project remember the site area is 12,500 sf
/as:project record-decision the client selected Scheme B
/as:project decisions
/as:project supersede 0003
/as:project migrate
```

`PROJECT.md` owns sourced current facts. `decisions/*.md` owns durable reasoning and status. There is no duplicated Decisions table. When a project belongs to a studio, create it through the studio skill so that skill remains the only writer of `STUDIO.md`. Project scaffolds include `AGENTS.md` and `.agents/skills/` for Codex alongside `CLAUDE.md` and `.claude/skills/` for Claude Code.

Format version 3 uses one universal project record for internal and client work. Project ID, free-form display name, client code, directory, and Folder ID are separate values. Project and Folder IDs are immutable; human folder names may change. The project root carries a minimal `.as-folder.json`, while a studio registry retains both its readable path and durable Folder ID. The AS naming option suggests uppercase `YYMMDD-CCC-PROJECT-NAME`, while firm-defined and no-convention projects preserve user-supplied identities and folders. `PROJECT.md` records Type, Status, Created, Client code, and Client, while Site, Zoning, Program, and Code sections are added only when relevant.

The AS convention uses a confirmed three-letter client code and suggests `INT` for internal work. Firm-defined and no-convention projects preserve the firm's own code without translating it into AS syntax, or record `—` when no code exists.

Project and Client are separate identity fields. Under the AS convention, client `SOM` and project `Strategy consulting` produce the suggestion `260901-SOM-STRATEGY-CONSULTING`, not `260901-SOM-SOM-STRATEGY-CONSULTING`.

Older records migrate only through a confirmed preview. Standalone migration recognizes the generated version-2 `CLAUDE.md`, replaces it with the canonical `@AGENTS.md` import, adds the project Folder ID, and preserves the original directory. Custom Claude instructions require separate review and confirmation. A valid legacy standalone root `PROPOSALS.md` blocks project-only migration because its register and proposal files require studio-owned conversion. Studio-owned migration preserves registered folders while adding project Folder IDs and updating the bounded registry, project identity, and known structured Project ID references transactionally; possible prose references are reported rather than rewritten speculatively.
