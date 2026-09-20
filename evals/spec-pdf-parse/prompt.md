---
description: Extract product specs from a PDF data sheet into a CSV row
tags: [core, fixtures]
max_turns: 30
allowed_tools: [Read, Write, Edit, Glob, Grep, Bash, Skill]
---

Pull the product data out of fixtures/ac-4820-data-sheet.pdf into a schedule row I can paste into my FF&E library, and save it as products.csv in the working directory. I need the model number, manufacturer, dimensions, finishes and list price, in the units the sheet uses.
