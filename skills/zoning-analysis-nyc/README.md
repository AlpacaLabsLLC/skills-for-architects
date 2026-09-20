# /as:zoning-analysis-nyc

Analyze a selected NYC lot using original publisher datasets, maps and the applicable Zoning Resolution. The [source manifest](../../corpus/sources/catalog.json) guides retrieval; the repository carries no zoning rulebook or numerical control tables.

## Install

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install as@skills-for-architects
```

## Use

Invoke `/as:zoning-analysis-nyc` with an address, BBL or BIN and the requested analysis. The skill resolves material date/use/scope, retrieves original sources, verifies their applicability and calculates only from established rules and site inputs. Missing access, version evidence or geometry is reported explicitly.
