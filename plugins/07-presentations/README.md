# Presentations

A Claude Code plugin for visual communication. Generate self-contained HTML slide decks with an editorial design system, and create harmonious color palettes from descriptions, images, or brand references — all output as standalone files you can open in any browser.

## The Problem

Architects and designers spend hours building slide decks — fighting PowerPoint layouts, aligning elements, maintaining visual consistency. Color selection is often ad hoc, without systematic consideration of contrast ratios, harmony, or accessibility. Both tasks take time away from design thinking.

## The Solution

Two skills that handle the visual production work. The slide deck generator builds complete HTML presentations from a topic or outline, using a 22-type design system with consistent typography, layout, and navigation. The color palette generator creates systematic palettes with WCAG contrast checks from any starting point — a description, a mood, a photo, or a brand reference.

```
┌──────────────────────────────────────────────────────────────┐
│                     DESIGNER INPUT                           │
│                                                              │
│  Topic, outline,       OR       "warm earthy tones for a     │
│  data, or document              boutique hotel lobby"         │
│  to present                     or an image file             │
└─────────────┬────────────────────────────┬───────────────────┘
              │                            │
              ▼                            ▼
   ┌───────────────────┐        ┌───────────────────┐
   │  Slide Deck       │        │  Color Palette    │
   │  Generator        │        │  Generator        │
   │                   │        │                   │
   │  22 slide types:  │        │  8-12 colors in   │
   │  • Title          │        │  4 groups:        │
   │  • Heading+Body   │        │  • Primary (2-3)  │
   │  • Stats          │        │  • Secondary (2-3)│
   │  • Data Table     │        │  • Neutral (2-3)  │
   │  • Bar Chart      │        │  • Accent (1-2)   │
   │  • Timeline       │        │                   │
   │  • Comparison     │        │  For each color:  │
   │  • Image grids    │        │  HEX, RGB, HSL,   │
   │  • Statements     │        │  suggested use,   │
   │  • ...            │        │  contrast ratios  │
   │                   │        │                   │
   │  Design system:   │        │  WCAG AA checked  │
   │  Helvetica, left- │        │  (4.5:1 text,     │
   │  aligned, massive │        │   3:1 large text) │
   │  whitespace,      │        │                   │
   │  editorial layout │        │  From: text,      │
   │                   │        │  image, brand,    │
   │  Keyboard + touch │        │  single color,    │
   │  navigation       │        │  or combination   │
   └─────────┬─────────┘        └─────────┬─────────┘
             │                            │
             ▼                            ▼
   ┌───────────────────┐        ┌───────────────────┐
   │  presentation.html│        │  palette-         │
   │                   │        │  [name].html      │
   │  Self-contained   │        │                   │
   │  single file —    │        │  Self-contained   │
   │  open in any      │        │  single file —    │
   │  browser, share   │        │  uses its own     │
   │  as-is, no deps   │        │  palette colors   │
   └───────────────────┘        └───────────────────┘
```

## Data Flow

### Slide Deck Generator

| Step | What happens |
|------|-------------|
| **Understand** | Reads input — topic, outline, document, or data |
| **Plan** | Selects slide types, plans narrative arc, decides count |
| **Build** | Writes self-contained HTML with CSS, navigation, and responsive typography |
| **Save** | Single `.html` file, no dependencies |

22 slide types cover titles, text, statistics, data tables, bar charts, timelines, comparisons, image grids, and full-bleed images. Every deck follows composition rules — alternate backgrounds, limit dark slides to 1-2, headlines state insights not topics.

### Color Palette Generator

| Step | What happens |
|------|-------------|
| **Interpret** | Reads input — text description, image, brand reference, or single color |
| **Generate** | Creates 8-12 colors in four groups with harmony rules (analogous, complementary, triadic) |
| **Validate** | Checks WCAG AA contrast ratios for all pairings, flags failures |
| **Export** | Self-contained HTML file that uses its own palette for styling |

Considers warm/cool balance, dominant/supporting/accent proportions, and tinted neutrals (never pure `#FFFFFF`).

## Skills

| Skill | Description |
|-------|-------------|
| [slide-deck-generator](skills/slide-deck-generator/) | Self-contained HTML slide decks with 22 slide types and an editorial design system |
| [color-palette-generator](skills/color-palette-generator/) | Harmonious color palettes from descriptions, images, or brand references with WCAG contrast checks |

## Install

**Claude Desktop:**

1. Open the **+** menu → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the **Presentations** plugin

**Claude Code (terminal):**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 07-presentations@skills-for-architects
```

**Manual:**

```bash
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/07-presentations/skills/slide-deck-generator ~/.claude/skills/slide-deck-generator
```

## License

MIT
