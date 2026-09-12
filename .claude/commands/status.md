---
description: Summarise the project — which stage, which documents exist, what is still TBD
---

Summarise the state of the student's project. Read the actual files every time;
never summarise from memory of the conversation.

## What to read

1. `project/project.yml` — stage, gate results, `TBD` fields, open questions, assumptions
2. `project/REGISTER.md` — documents, revisions, statuses, outstanding change requests
3. The `.md` files under `project/` — to check the register matches reality

## Report

```
## Project status — <name> (<code>)

**Stage:** <stage>   **Last gate:** <id> <pass/not yet> on <date>

### Documents
| Code | Title | Rev | Status | Matches register |
|---|---|---|---|---|

### Outstanding
- <n> TBD fields — <which ones>
- <n> unresolved change requests
- <n> assumptions nobody has confirmed

### Mismatches
<where the register and the files disagree — be specific; if there are none, say
everything matches>

### Next
<one to three items, in the order they should be done, with the command or skill>
```

## Always flag these when found

- A register entry whose revision does not match the document's own header
- A document in the folder that is not in the register
- A document whose code still contains `XXX`
- A `TBD` field with no matching entry in `open_questions`
- A stage that has advanced despite the last gate result being `fail`
- A change request that has been open a long time with no movement

Keep it short. A project that just started deserves ten lines, not a page.
