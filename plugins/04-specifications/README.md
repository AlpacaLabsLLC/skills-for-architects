# Specifications

A Claude Code plugin for construction documentation. Generate CSI MasterFormat outline specifications from a materials list — organized by division with three-part sections, performance criteria, and standards references.

## The Problem

Specification writing is tedious and repetitive — mapping materials to CSI divisions, writing three-part specs with the right language, referencing standards. Architects spend hours producing outline specs that follow the same structural patterns every time.

## The Solution

A skill that knows CSI MasterFormat 2020 and produces properly formatted outline specs. Give it a materials list — pasted, from a file, or described verbally — and it maps each material to the correct division, writes three-part sections (General, Products, Execution), and flags items that need professional review.

```
┌──────────────────────────────────┐
│         DESIGNER INPUT           │
│                                  │
│  Materials list                  │
│  "porcelain tile,                │
│   steel studs,                   │
│   gypsum board..."               │
└─────────────┬────────────────────┘
              │
              ▼
   ┌───────────────────┐
   │   Spec Writer     │
   │                   │
   │  Materials →      │
   │  CSI divisions →  │
   │  3-part specs     │
   │                   │
   │  Divisions:       │
   │  03-26            │
   │  (Concrete →      │
   │   Electrical)     │
   │                   │
   │  Part 1: General  │
   │  Part 2: Products │
   │  Part 3: Execution│
   │                   │
   │  [REVIEW REQUIRED]│
   │  flags on generic │
   │  or safety specs  │
   └─────────┬─────────┘
             │
             ▼
   ┌───────────────────┐
   │  Markdown file    │
   │  outline-specs-   │
   │  [project].md     │
   └───────────────────┘
```

## Data Flow

| Step | What happens |
|------|-------------|
| **Parse** | Reads materials list (pasted, file, or verbal) and classifies into CSI divisions |
| **Generate** | Writes 3-part outline specs — General, Products, Execution — with standards references |
| **Annotate** | Adds `[REVIEW REQUIRED]` flags on generic specs, life-safety sections, assumed criteria |
| **Export** | Saves markdown file |

Covers 11 CSI MasterFormat 2020 divisions (03 Concrete through 26 Electrical). Uses proper spec language — "shall", "provide", "verify", imperative mood, no contractions.

## Skills

| Skill | Description |
|-------|-------------|
| [spec-writer](skills/spec-writer/) | CSI outline specification writer — maps materials to MasterFormat 2020 divisions with three-part specs |

## Install

**Claude Desktop:**

1. Open the **+** menu → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the **Specifications** plugin

**Claude Code (terminal):**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 04-specifications@skills-for-architects
```

**Manual:**

```bash
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/04-specifications/skills/spec-writer ~/.claude/skills/spec-writer
```

## License

MIT
