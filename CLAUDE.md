# Rules for this repository

This repo is a **teaching template**, not a project of its own. The user is a
student on the AI Design System Bootcamp, running their own project through a
six-stage pipeline.

---

## The rule everything else rests on — never invent what you do not know

Every skill in this set declares this rule itself, and it is the reason the Q&A
mechanism exists at all.

The student cannot answer ⇒ write `TBD — ต้องการ [คน/ข้อมูล]` and add an entry to
`open_questions` in `project/project.yml`.
A number the student estimated rather than knew ⇒ record it under `assumptions`
with its source.

**A fabricated requirement is worse than a blank one, because it gets built.**
A gap is visible and someone fills it; an invention is invisible and gets built on.

When context is missing, **ask** — up to five questions, in a single message,
never one at a time.

---

## The student's work lives in `project/` only

**`project/` is a symlink.** It points at one project inside a workspace that
normally sits outside this repository — the template ships empty, and several
projects share one clone. Write through `project/...` and the symlink puts the
file where it belongs.

Two things follow, and both have already gone wrong once:

- **Never create a `projects/` directory here.** If `project/` seems to be
  missing a folder, the fix is to create it *through* the symlink
  (`project/4-build/`), not to invent a sibling tree that nothing reads.
- **Never resolve the symlink and write to the absolute path.** The target moves
  when the student switches projects; `project/` is what stays correct.

To see where it currently points: `readlink project`.

| Location | Holds | Editable |
|---|---|---|
| `project/` | The student's documents and work (a symlink) | Yes — the only place they edit |
| `.claude/skills/` | Knowledge and templates | Only when improving the template itself |
| `.claude/commands/` | Commands | Same |
| `tools/`, `docs/print-th.css` | Tooling | Same |
| `docs/*.pdf`, `docs/*.docx`, `handoff/` | Generated output | **Never** — overwritten on every build |

**Do not put example project content back into `.claude/skills/`.** The template
is empty by design; the student has to think of the content. The templates carry
structure and an explanation of what each field wants, and nothing else.

---

## Documents

- Edit the `.md` only. The `.pdf` and `.docx` are generated from it and
  overwritten by every `bash tools/build-docs.sh`.
- Document codes come from `meta.code` in `project/project.yml`. A document still
  containing `XXX` was not created properly.
- Create documents with `/doc-new <TYPE>` only, so the register entry is written
  in the same edit.
- Revision procedure, the stale-reference sweep, and register upkeep are in the
  `document-control` skill.
- Document body text is written in Thai. The templates in `assets/` carry English
  headings as structural scaffolding — translate the headings when writing the
  real document, and keep the numbering.

---

## Gates

`/gate` checks the actual files; it does not ask whether something was done. A
gate that always passes is not a gate — if the evidence cannot be found, it has
not passed. Advance `stage:` only on a real pass, and never delete the history of
a gate that previously failed.

---

## Roles stay separate

The pipeline splits into roles so that every question has an owner. Collapsing
them lets mistakes that should have been caught slip through silently.

- The analyst finds contradicting requirements ⇒ raise a change request (`/cr`).
  **Not** pick one and build on it, and not edit the source document.
- The developer finds a wrong spec ⇒ the same.
- The code reviewer does not fix the code. Report first; fix only when asked.
- Quality assurance does not write new features.
- The student may play every role (solo mode), but one at a time — not all of
  them at once.

---

## When the student says "just do it for me"

That is fine, but do it *as that role* rather than skipping the process: read
`project.yml` first, ask what is still unknown, follow that skill's workflow, and
close by saying which decisions you made for them so they can overrule.

Handing back a flawless document the student did not think through is helping
them pass without learning anything.

---

## Language

Write everything in English — skills, commands, documentation, tooling, and
commit messages. When adding a new file, English is the default; do not ask.

Thai belongs in exactly one layer, and adding more of it anywhere else is a
mistake:

- **Document templates** under each skill's `assets/`, because they become Thai
  official-format deliverables
- **Strings the tooling matches against those templates** — the control header row
  `| รหัสเอกสาร |`, the status values, the `TBD — ต้องการ [คน/ข้อมูล]` marker, and
  the month labels drawn into the Gantt image. Changing these breaks
  `build-docs.sh`, which finds documents by that header.
- **Trigger phrases inside skill descriptions**, because that is what students
  actually type

Ask the student questions in their own language. The wording in the question bank
is the intent of each question, not a script to read out.
