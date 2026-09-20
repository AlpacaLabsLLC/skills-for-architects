---
type: llm
focus: { source: file, path: cleaned.csv }
---

The source file left the width and depth of the task light (code LI.S-06) empty, and gave its height as 22 in.
PASS if the cleaned file leaves that row's width and depth empty, blank or explicitly unknown, and carries a height converted from 22 inches (about 559 mm).
FAIL if width or depth have been filled in with any number, or if the row is missing.
