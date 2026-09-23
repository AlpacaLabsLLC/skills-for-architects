# Studio policy references

This governance contract describes ownership and live policy access. The studio's own policy remains the authority for its AI-use choices. It complements provenance, source citation, data handling, record ownership and host permissions at their existing authoritative sources; do not duplicate those rules or invent a blanket precedence order.

## Configuration — owned by studio

The studio skill owns the `Firm policy` reference and `Firm policy adoption` choice in STUDIO.md's Data governance section. Skill Maker consumes them read-only. The choice is `existing`, `default` or `declined`; `declined` has reference `None`. A missing reference in an older studio means no configured policy, not permission to adopt one. A nonempty reference must be respected even if its adoption label is absent; contradictory or malformed configuration needs a precise clarification before affected actions.

During fresh studio setup ask once: “Do you have an AI-use policy to use, or would you like to adopt Arch Studio’s default?” Accept a decline. Show the complete [default template](../studio/templates/studio/ai-policy.md) before adoption; silence is not adoption. Include the chosen reference, exact files and manifest changes in the existing concrete setup preview. Its approval covers that set; do not add another approval round. Preserve a recorded choice during ordinary work and unrelated setting edits. Existing studios are configured only on explicit request to the studio owner; no automatic migration.

- **Existing:** inspect the supplied document and verify complete actual host readability. Reference its authoritative locator in place, without copying it into the studio. Resolve relative paths from the owning studio root. Local, synchronized and connected-document locators need the host's actual read capability; a connected URL is not proof of access. Do not record successful adoption of an unreadable document.
- **Default:** use the resolved Standards root from STUDIO.md or the confirmed setup inputs, never an assumed folder name or home path. Prepare the template at `<resolved standards root>/governance/ai-policy.md`; record its studio-relative locator. Include the policy and manifest in the same protected preparation/readback set. A preexisting target is not overwritten implicitly; inspect it and obtain only missing authorization for a requested change.
- **Declined:** record `Firm policy = None` and `Firm policy adoption = declined`, without creating a policy file or reopening the interview later.

Existing policy changes use the ordinary governed document-edit contract; Skill Maker neither rewrites policy nor configures STUDIO.md. MCP delivers this generic contract and template, not private policy hosting, access, distribution or compliance certification.

## Consumption — generated skills

For relevant studio or project procedures, Skill Maker adds a task-appropriate governance step and explains the dependency in the generated README. Retain the live lookup behavior below in the procedure; do not copy the policy's current rules into the skill. Read the current policy during creation when it is needed to establish the procedure's requirements. No policy text, private locator or originating studio identity belongs in a public-catalog bundle, including examples, README, metadata and auxiliary files.

1. Resolve the current owning studio through the existing context contract on every invocation. Revalidate studio identity before resumed policy-dependent actions. Do not carry a previous studio's policy into another studio; if identity is ambiguous, ask only the question needed to resolve it. Standalone/global use does not require studio creation: apply existing host/user governance and disclose that no studio policy was resolved.
2. Read STUDIO.md's current `Firm policy` reference and the complete current policy before policy-dependent actions. Record the source and revision actually read in execution evidence (document revision, timestamp or content hash where available; do not invent one). No configured policy or an explicit decline leaves existing governance in force, without a new setup interview.
3. If a configured document cannot be read completely, name the unavailable document, pause policy-dependent actions and request restored access or supplied current content. Never silently substitute the default, reuse an old snapshot or claim compliance. Independent work may continue.
4. Apply it together with applicable governance, including provenance. If requirements conflict, name both sources and pause only the affected action for resolution; do not silently weaken either rule. Preserve authorization already given for the current task and scope.
5. Read the policy again on the next invocation, and revalidate it before resumed policy-dependent actions. Reconcile policy changes against prepared outputs before publishing them. Central policy edits take effect without rewriting the generated skill.

Embed these operational instructions in the generated skill so private skills do not depend on an installed Arch Studio path. Refer to the current studio's recorded reference, not the author's policy pathname. Adapt the step to the task without dropping its unreadable-policy, context-change or conflict handling. Public-catalog procedures use generic context-aware handling where relevant. Do not force policy-specific work into unrelated standalone procedures.

Existing generated skills adopt this step only through an explicitly authorized update to that named skill. Preserve Skill Maker's destination precedence, no-clobber protection and full readback. Saving a skill does not prove discovery, governed execution or organization-wide installation.
