---
description: Create a controlled document from its template, substitute the project code, and register it
argument-hint: "<TYPE> — e.g. PRD, SRS, DSN, RVW, QAR, REL"
---

Create a new controlled document, following the rules in the `document-control`
skill.

## Steps

1. Read `project/project.yml` and take `meta.code`. If the file does not exist,
   tell the user to run `/kickoff` first, and stop.

2. Check that the requested `TYPE` is in the document type registry in the
   `document-control` skill. If it is not, show the table of valid types and ask
   which one they meant. **Never invent a new type.**

3. Work out the sequence number — read `project/REGISTER.md` and count existing
   documents of this type. The first is `001`. **An existing document does not
   mean this must be a revision:** a different question is a new document (`002`),
   whereas changed content in the same document is a revision. Explain the
   difference before deciding.

4. Copy the template from the `assets/` directory of the owning skill, per the
   registry table in `document-control` — for example `PRD` comes from
   `.claude/skills/product-owner/assets/prd-template.md`. If no template exists
   for that type, build the document from the standard control header and tell the
   user there was no template.

5. Place the file in the folder for its stage:

   | Stage | Folder |
   |---|---|
   | product | `project/1-product/` |
   | analysis | `project/2-analysis/` |
   | design | `project/3-design/` |
   | review, quality | `project/5-quality/` |
   | release | `project/6-release/` |

6. Replace every `XXX` with `meta.code`, set the revision to `00`, set today's
   date, set the status to `ร่าง`, and take the author from `meta.owner`.
   **A document still containing `XXX` was not created properly** — check before
   finishing.

7. Fill in only the fields `project.yml` genuinely answers. Leave the rest as empty
   structure. **Do not guess content.** Collect the relevant `TBD` fields into the
   document's open-questions section.

8. Register it in `project/REGISTER.md` in the same edit — a register updated later
   is a register that was wrong in between.

9. Report three lines — which file was created where, how many sections were filled
   from `project.yml`, and which sections the student has to write themselves, with
   the skill that helps.

Requested type: `$ARGUMENTS`
