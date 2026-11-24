# Report template

The technical notes a run writes to the document string `as:run-notes` (the chat reply follows the Report section of the skill). Document units. Every number comes from the script's constants or its printed checks, never from reading a capture.

```markdown
## <Model name>, <units>

| Dimension | Value | Source |
|---|---|---|
| Bay spacing | 144 in | brief |
| Stud spacing | 16 in o.c. | default (assumption 2) |

| Layer | Objects | Check |
|---|---|---|
| Barn::Structure::Posts | 12 | 12 lines, 144 in grid |
| Barn::Envelope::Walls | 4 | planar, 7 holes total |

Grasshopper (when built): definition <name or unsaved>; sliders <names>;
<slider> moved to <value> → <observed output>; restored to <default>.

Assumptions: <numbered list, or "none">

Checks: <passed> of <total> passed. <Each failure, what was kept, and why.>
Not checked: <the list the requirements check printed>. A full score means only that the checks listed passed.
Connections cut: <each type and what it showed>, or "none".
Derived values adjusted: <each count or spacing changed by a form change, old and new value, and its revision>, or "none".
Capture: <view, visible object count> or "none; geometry checks only".
Document: not saved | saved to <path> | untitled, copy written to <path>, read back with File3dm.Read.
Time: active <minutes>; wall <minutes> when an idle gap occurred.

Undecided clash pairs: <each pair type, how it was settled>, or "none".
```
