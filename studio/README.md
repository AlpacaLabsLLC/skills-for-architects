# Distributed Studio contracts

These are package-owned contracts, not a studio workspace. Actual STUDIO.md,
PROJECT.md, decisions, agreements and ledgers belong to user-owned workspaces.
The [workspace model](../docs/workspace-model.md) defines format 3, identity,
record ownership and migration. Skills retain mutation authority; a cluster
membership or a downloaded template grants none.

`templates/studio/` owns the shared studio scaffolding, including `.mcp.json`.
Skill-private record templates remain with their record owner until a coordinated
migration is useful. Hosting these files does not provide shared writable storage.
