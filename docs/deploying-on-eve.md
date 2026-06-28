# Deploying Architecture Studio on eve

Architecture Studio is distributed today as Claude Desktop and Claude Code plugins. eve is the deployment path when you want those workflows to run as a durable web agent with route auth, subagents, tools, sandboxing, and production hosting.

The canonical guide lives on ALPA:

https://alpa.llc/docs/deploying-architecture-studio-on-eve/

Use this repo note as the short implementation map.

## Recommended shape

Create a separate eve app instead of converting this plugin repo in place:

```bash
eve init architecture-studio-eve
cd architecture-studio-eve
```

Then migrate the useful Architecture Studio surface into eve's filesystem layout:

```text
architecture-studio-eve/
├── agent/
│   ├── agent.ts
│   ├── instructions.md
│   ├── channels/
│   ├── skills/
│   ├── tools/
│   ├── sandbox/
│   └── subagents/
└── evals/
```

eve derives identities from paths:

- `agent/skills/project-dossier.md` becomes the `project-dossier` skill.
- `agent/tools/search_norma.ts` becomes the `search_norma` tool.
- `agent/subagents/site-planner/agent.ts` becomes the `site-planner` subagent.

## What to migrate first

Start with a narrow production slice:

- Root `Architecture Studio` routing instructions
- `project-dossier`
- `decision`
- `product-research`
- `product-data-cleanup`
- `master-schedule`
- `spec-writer`
- `environmental-analysis`
- `zoning-analysis-nyc`
- `workplace-programmer`

Then add subagents:

- `site-planner`
- `nyc-zoning-expert`
- `workplace-strategist`
- `product-and-materials-researcher`
- `ffe-designer`
- `sustainability-specialist`
- `brand-manager`

Keep skills procedural. Put external calls, file writes, product-library lookup, and project-memory updates behind eve tools or connections.

## Minimal root agent

```ts
import { defineAgent } from "eve";

export default defineAgent({
  model: "anthropic/claude-opus-4.8",
  reasoning: "high",
});
```

String model IDs route through Vercel AI Gateway. For direct provider access, install the relevant AI SDK provider package and pass the provider model object instead.

## Auth and deployment

Do not ship a browser-facing production agent with placeholder auth.

For a Vercel-hosted starting point:

```ts
import { eveChannel } from "eve/channels/eve";
import { localDev, vercelOidc } from "eve/channels/auth";

export default eveChannel({
  auth: [vercelOidc(), localDev()],
});
```

For firm deployments, replace or extend this with app session auth, SSO, JWT/OIDC, or another verifier that maps users and teams into the session.

Deploy with:

```bash
eve info
eve build
eve link
eve deploy
```

Verify:

```bash
curl https://<your-app>/eve/v1/health
eve dev https://<your-app>
```

## Norma

Use Norma as the product and material memory layer. Product and FF&E agents should check firm-owned product memory before relying only on public web search.

Typical tools:

- search product records
- normalize product data
- attach products to projects
- store substitutions and approvals
- preserve source URLs and manufacturer facts

## More detail

Read the ALPA guide:

https://alpa.llc/docs/deploying-architecture-studio-on-eve/
