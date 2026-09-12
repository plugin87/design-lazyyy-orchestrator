---
description: Raise a change request when source documents contradict each other
argument-hint: "[short summary of the contradiction]"
---

Open a change request, or add an entry to an existing one.

## Why this command exists

When the analyst or the developer finds that the source documents contradict each
other, there are three options: pick one and build on it · stop and wait ·
**or record it as a change request and keep working on a declared assumption.**

The third is the right one, and it is the loop most often missing — people raise
requests, but nothing receives them, so the requests pile up unread. This command
closes that loop.

## Steps

1. Read `project/project.yml` and `project/REGISTER.md`.

2. Check whether `CR-XXX-001` already exists.
   - It does — append the new entry and bump the revision per the procedure in the
     `document-control` skill.
   - It does not — create it from
     `.claude/skills/system-analyst/assets/change-request-template.md` in
     `project/2-analysis/`.

3. Ask the user for all four of these, in one message, if they have not already
   said:

   - Which documents and which sections contradict each other (with document codes
     and section numbers)
   - What the two readings are
   - Which reading the work will proceed on while this is unresolved, and why
   - What this blocks, or that it blocks nothing

4. Write the entry into the change request, with the date and who raised it.

5. Record the working assumption in `project.yml` under `assumptions`, linked to
   the request entry — so that when it is resolved, it is clear what has to change.

6. Add a row to the outstanding-requests table in `project/REGISTER.md`.

7. Tell the user who has to decide — per the `scope.approver` field — and that
   outstanding requests will appear in `/status` until they are closed.

## Rules that cannot be broken

**Never edit the source document yourself.** Documents have owners and a revision
procedure. The analyst does not edit the PRD; the developer does not edit the SRS.

**Never close a request by deleting it.** Closing means recording what was decided,
by whom, and on what date. A request that simply disappears takes the record of the
decision with it.

Contradiction found: `$ARGUMENTS`
