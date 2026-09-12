---
description: Open mission control — the room where you watch the pipeline's agents work
---

Start the monitor and tell the student what they are looking at.

## Start it

```bash
node tools/monitor/server.mjs &
```

Then open http://localhost:4173 and click **เข้าห้อง** (the click is what lets the
browser start audio; nothing else depends on it).

To rehearse without running the pipeline — or to show the whole flow in a class
without waiting for real agents — replay the recorded run instead:

```bash
node tools/monitor/server.mjs --replay .monitor/sample-run.jsonl --speed 1.6 &
```

## What the room is showing

Every light comes from a hook that actually fired. Say this plainly, because the
point of the room is that it cannot show work that did not happen:

| On screen | Where it comes from |
|---|---|
| A desk lights up | `SubagentStart` — that role was really dispatched |
| The filename on a desk screen | `tool_input.file_path` of a real `Write`/`Edit` |
| Front-of-house vs back-of-house desk | the path itself — `src/` or `server/` |
| The speech bubble on handoff | `last_assistant_message` from `SubagentStop` |
| The verdict card | the exit line of `tools/correcter/verify.py` |
| Stage rail and the six gates | `stage:` and `gates:` in `project/project.yml` |
| XP, level, streak | counts of the above — no invented numbers |

## If the room stays dark

1. `python3 tools/monitor/emit.py --selftest` — proves the receiver works
2. `cat .monitor/events.jsonl` — proves hooks are reaching it
3. Hooks are read when a session starts, so a session that was already open
   when `.claude/settings.json` changed will not be sending anything. Restart it.

## Turning it off

Delete the `hooks` block from `.claude/settings.json`. Nothing else in the
pipeline depends on the monitor.
