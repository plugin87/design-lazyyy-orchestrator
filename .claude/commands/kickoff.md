---
description: Open a new project — ask the opening questions and write project/project.yml
argument-hint: "[project name, if you already have one]"
---

Open a new project for the student, using the `project-intake` skill.

## Steps

1. Check whether `project/project.yml` already exists.
   - **It exists** — read the whole file, then report how many fields are
     answered, how many are still `TBD`, and what stage the project is at. Then
     ask whether to fill the gaps or start a new project over the top.
     **Never overwrite without asking.**
   - **It does not exist** — go to step 2.

2. Invoke the `project-intake` skill and ask the five opening questions **in a
   single message**. If the user supplied some of this in the command arguments,
   ask only for what is missing.

3. Play the answers back for confirmation before writing the file. Do not skip
   this — it is where students catch themselves saying something they did not
   mean.

4. Once confirmed:
   - Write `project/project.yml` from `assets/project.yml.template` in the
     `project-intake` skill, keeping every comment in the file intact.
   - Create `project/REGISTER.md` from `assets/register-template.md` in the
     `document-control` skill, substituting the project code for `XXX`.
   - Set `stage: intake`.
   - For anything the student did not know, write
     `TBD — ต้องการ [คน/ข้อมูล]` and add an entry to `open_questions`.
   - For any number the student estimated rather than knew, add an entry to
     `assumptions`.

5. **Create nothing else.** No PRD, no folders full of empty files. Documents are
   created one at a time by `/doc-new`, when their turn comes.

6. Close with three lines — what was written, how many fields are still `TBD` and
   which ones, and what to run next (usually `/gate` to see what is missing, or
   the `product-owner` skill to start the PRD).

Arguments: `$ARGUMENTS`
