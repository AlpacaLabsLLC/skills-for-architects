---
type: regex
target: { source: file, path: cleaned.csv }
pattern: '\b(?:in|IN|inch|inches)\b'
match: not_contains
---
