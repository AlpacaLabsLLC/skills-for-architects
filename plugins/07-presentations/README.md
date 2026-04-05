# Presentations

A Claude Code plugin for visual communication. Generate self-contained HTML slide decks, create harmonious color palettes, and batch-resize images for web, social, slides, and print — all from a single command.

## The Problem

Architects and designers spend hours on visual production work — fighting PowerPoint layouts, selecting colors without systematic contrast checks, and manually resizing the same image six times for different deliverables. All of it takes time away from design thinking.

## The Solution

Three skills that handle visual production. The slide deck generator builds complete HTML presentations from a topic or outline. The color palette generator creates systematic palettes with WCAG contrast checks from any starting point. The image resizer batch-exports project photos to every required format — web, social, slides, and print — in one step.

## Skills

| Skill | Description |
|-------|-------------|
| [slide-deck-generator](skills/slide-deck-generator/) | Self-contained HTML slide decks with 22 slide types and an editorial design system |
| [color-palette-generator](skills/color-palette-generator/) | Harmonious color palettes from descriptions, images, or brand references with WCAG contrast checks |
| [resize-images](skills/resize-images/) | Batch-resize photos for web (WebP), social (center-cropped), slides (4:3 and 16:9), and print (ARCH A/B/C at 300 DPI) |

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
ln -s $(pwd)/skills-for-architects/plugins/07-presentations/skills/color-palette-generator ~/.claude/skills/color-palette-generator
ln -s $(pwd)/skills-for-architects/plugins/07-presentations/skills/resize-images ~/.claude/skills/resize-images
```

## License

MIT
