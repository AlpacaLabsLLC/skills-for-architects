# /architect — Smart Router

Describe your task and get routed to the right agent or skill. Start here if you don't know which of 34 skills to call.

## Usage

```
/architect [describe what you need]
```

## Examples

| Input | Routes to |
|-------|-----------|
| `/architect task chair, mesh back, under $800` | Product & Materials Researcher agent |
| `/architect 375 Sterling Place Brooklyn` | Asks: site context or zoning? |
| `/architect I need a space program for 200 people` | Workplace Strategist agent |
| `/architect check if 120 Broadway is landmarked` | `/nyc-landmarks` directly |
| `/architect parse this EPD` | `/epd-parser` directly |
| `/architect make a deck from this report` | Brand Manager agent |

## How It Works

1. Reads your input and classifies intent
2. Routes to the right agent or skill — no keyword matching, just natural language understanding
3. If ambiguous, asks one clarifying question
4. Loads the agent file at runtime and follows its workflow

The router contains no orchestration logic. Agent files are the single source of truth.

## License

MIT
