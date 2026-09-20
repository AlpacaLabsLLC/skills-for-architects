---
type: regex
target: { source: file, path: cleaned.csv }
pattern: '^\s*"?LI\.S-0[1-6]'
flags: im
match: "count:6"
---
