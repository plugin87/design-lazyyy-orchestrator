---
name: project-intake
description: Open a new project by interviewing the student, then write the answers to project/project.yml — the shared memory every other role skill reads before it starts work. Use this skill whenever a project is being started, named, or scoped for the first time — "let's start a project", "เริ่มโปรเจกต์ใหม่", "kickoff", "ตั้งโครงการ", "I want to build X for the bootcamp" — and whenever another skill needs project context that project.yml does not yet contain. Also use it to review or repair an existing project.yml, to fill gaps left as TBD, or to answer "what has this project already decided?". Do NOT use it to write the actual PRD, SRS, sprint plan, or any deliverable document — this skill only gathers and records facts; the owning role skill writes the document.

---

# Project Intake

This skill exists because of one failure mode. A student says "make me a booking
app" and gets back a twelve-page PRD full of invented users, invented metrics,
and invented constraints. It looks like work. It teaches nothing, because every
decision in it was made by the model rather than by the student.

The job here is to ask instead of assume, and to write the answers somewhere the
rest of the pipeline can read them.

## What project.yml is

One file at `project/project.yml`. It is the shared memory of the whole
pipeline — product-owner writes to it, system-analyst reads it and adds to it,
quality-assurance reads it to know what "correct" means. A fact answered once is
never asked again.

It is not a deliverable. Nobody submits project.yml. It is the notes that make
the deliverables possible.

The schema lives in `assets/project.yml.template`. Copy it verbatim on first
run; never invent fields.

## Workflow

1. **Check what exists.** Read `project/project.yml`. If it is missing, this is
   a fresh start. If it exists, read it fully before asking anything — asking a
   student to repeat themselves is the fastest way to lose their trust in the
   tool.
2. **Ask the opening round.** Five questions, one batch. See below.
3. **Play the answers back.** A short summary in the student's own words, and
   ask for confirmation. Do not skip this: it is where students catch
   themselves saying something they did not mean.
4. **Write the file.** Only after confirmation.
5. **Say what happens next.** Name the next command and the next role — usually
   `/gate` to see what is missing, or the `product-owner` skill to write the PRD.

## The opening round

Ask exactly these five, together, in one message:

1. What is this project called?
2. Give me a three-letter code for it — it goes into every document code, as in
   `PRD-XXX-001`
3. What problem does this solve, in one sentence?
4. Who are the users, and what do they do today without this?
5. How much time is there, and who is working on it?

Five is the ceiling, not a target. If the student has already answered some of
these in conversation, ask only what is left.

Ask in the student's own language. The wording here is the intent of each
question, not a script to read out.

The rest of the question bank — the rounds each later role runs — is in
`references/question-bank.md`. Each entry there records why the question is
asked and which field of which document the answer lands in. Read it before
running a round for a role other than intake.

## Rules that make this work

**Never invent an answer.** When the student does not know, write
`TBD — ต้องการ [คน/ข้อมูล]` into the field and add an entry to
`open_questions`. A gap is visible and gets filled. An invention is invisible
and gets built.

**Label guesses as guesses.** When a student estimates a number rather than
knowing it — user counts, session volume, available days — record it under
`assumptions` with who guessed and when. Later, when a forecast built on it
turns out wrong, the chain is traceable.

**Ask in batches, never one at a time.** A five-question message respects the
student's attention. Five separate messages is an interrogation, and they start
answering carelessly by the third.

**Never ask what the file already answers.** Every re-asked question tells the
student the tool is not paying attention.

**Confirm before writing.** Play back, then write. Writing first and correcting
later leaves wrong facts sitting in shared memory where other roles will read
them.

**Do not solve the problem.** The student says "so I need a mobile app with
offline sync" — that is a solution, and it is not yours to accept or refine
here. Record it under `assumptions` as *the student's proposed solution*, and
let product-owner do the work of pushing back to the problem.

## Field conventions

| Field | Format | Notes |
|---|---|---|
| `meta.code` | 3 uppercase letters | Replaces `XXX` in every document code. Must be unique per student project. |
| `meta.started` | `YYYY-MM-DD` | Absolute dates only. Never "last week". |
| `stage` | one of the pipeline stages | `intake` on creation. Only `/gate` advances it. |
| any unknown | `TBD — ต้องการ [คน/ข้อมูล]` | Never blank, never a plausible placeholder. |

## Output

Write `project/project.yml`. Create `project/REGISTER.md` from the empty
register in the `document-control` skill if it does not exist yet. Create
nothing else — no PRD, no folder full of empty documents. Documents are created
one at a time by `/doc-new`, when their turn comes.

Close by telling the student two things: how many fields are still `TBD`, and
what to run next.

## Reference files

- `references/question-bank.md` — every round, every role, with the reason for
  each question and where the answer lands
- `assets/project.yml.template` — the schema, to be copied verbatim
