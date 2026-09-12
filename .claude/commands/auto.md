---
description: Run the whole pipeline automatically with the room open, and stop on the correcter's verdict
---

Run the pipeline end to end without asking the student anything, with mission
control open so they can watch it happen.

```bash
bash tools/auto.sh
```

That script opens the room at http://localhost:4173, invokes the `orchestrator`
skill, and stops when `tools/correcter/verify.py` returns a verdict.

## What decides when it stops

Not this command, and not the orchestrator. `verify.py` returns three things and
only these three are allowed to end the run:

| exit | verdict | what happens |
|---|---|---|
| 0 | `PASS` | the work stands, the stage advances |
| 1 | `CORRECTED` | fixable without a person — fix, run again, at most three rounds |
| 2 | `BLOCKED` | needs a person or a fact from the real world — stop and say so |

**`BLOCKED` is not a failure to route around.** Do not fill in a value that is
not known, weaken a check, or skip the correcter to get past it. A pipeline that
can always finish is a pipeline that proves nothing.

## Rehearsing

To show the whole flow without waiting for real agents — in a class, or before
one — replay the recorded run:

```bash
bash tools/auto.sh --demo
```

## If the room stays dark while the pipeline runs

Hooks are read when a session starts. A session that was already open before
`.claude/settings.json` gained its `hooks` block sends nothing. Restart it, then
check `.monitor/events.jsonl` is growing.
