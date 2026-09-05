# /as:master-schedule

Owns adopted FF&E item/schedule records and the optional `product-library.csv`. Explicit adoption creates immutable Markdown revisions; host-operated workbooks remain pinned views. See [record contract](../../studio/ffe/README.md) for revision, reconciliation and recovery commands. The existing 33-column library workflow remains compatible.

## Usage

```text
/as:master-schedule
```

The skill finds the nearest `PROJECT.md`, validates the complete 33-column CSV, and reports its status. With confirmation, it can create an empty library or import a user-exported CSV. Writes use deterministic RFC 4180 quoting, UTF-8 without BOM, CRLF record endings, and atomic replacement.

Legacy `master-schedule.json` and `canoa.json` files are preserved as evidence. They are not treated as product rows and are never contacted or migrated automatically.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Local setup, status, import, and safety workflow |
| `scripts/csv-library.py` | Exact-schema validation and atomic CSV mutation |

## License

MIT
