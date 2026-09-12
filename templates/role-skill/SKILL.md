---
name: <must match this folder's name exactly>
description: <what it does — one sentence, stating the outcome rather than the topic>. Use this skill whenever <the situations that should trigger it — write the actual phrasings a student would type, in Thai and English>. Do NOT use it for <the neighbouring work that is not this> — that is the <other skill> skill.
---

# <Role name>

<One or two paragraphs — what question this role answers, and why it is separate.
Write it so the reader can see what would be missed if the role did not exist,
not merely what the role does.>

## Intake

This section is what makes the role ask instead of guess. Every role needs it.

1. Read `project/project.yml` first. If it does not exist, run `project-intake`.
2. Ask only what is still blank for this role — <name the three or four questions,
   and add that set to `project-intake/references/question-bank.md`>.
3. Write the answers back to `project.yml` under `<the fields this role owns>` so
   the next role does not have to ask again.

## Workflow

<The order to work in, one imperative per step, each followed by a short reason.
Why this order matters — and what breaks when a step is skipped — is more useful
than the list of steps on its own.>

1. **<Imperative>** — <why>
2. **<Imperative>** — <why>

## <The rule or standard this role owns>

<For example, developer owns the Definition of Done, and code-reviewer owns the
severity scale. If this role is a gate, its criteria must be able to refuse, and
they must also appear in `.claude/commands/gate.md`.>

## Anti-patterns to catch and call out

<What this role should flag even when nobody asked. One per line, specific enough
to actually recognise — not a general principle.>

- <a mistake that shows up often>

## Output conventions

- Deliver the work itself, not a description of how you would do it
- When you do not know, write `TBD — ต้องการ [คน/ข้อมูล]`; never guess
- You may decide on the user's behalf, but say so in one line at the end so it
  can be overruled

## How this fits the pipeline

<Which role hands work in, and via which document · who receives it · which gate
sits between them · and the route back when a problem is found.>

## Files in this skill

- `references/<name>.md` — <deeper knowledge that does not belong in SKILL.md;
  loaded only when it is actually needed>
- `assets/<name>-template.md` — <a document template or checklist>
