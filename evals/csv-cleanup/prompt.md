---
description: Clean a messy FF&E schedule CSV without inventing or losing data
tags: [core, fixtures]
max_turns: 30
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
---

Clean up the furniture schedule at fixtures/schedule.csv: make the codes, manufacturer names, finishes and dimensions consistent, and put every dimension in millimetres. Keep every row and don't fill in anything that isn't in the file. Save the result as cleaned.csv in the working directory.
