# Scaffold for adding a new role

This folder is **not a skill** and is not loaded by Claude Code, because it does
not live under `.claude/skills/`. It is a starting point to copy.

## Use it

```sh
cp -R templates/role-skill .claude/skills/<role-name>
```

Then fill in the placeholders in `SKILL.md` and work through the checklist below.

## Checklist

- [ ] The folder name matches `name` in the frontmatter exactly — if it does not,
      the skill will not load
- [ ] `description` is under 1024 characters
- [ ] `description` contains the actual phrasings a student would type, in both
      Thai and English
- [ ] `description` ends with `Do NOT use for… — that is the X skill`
- [ ] You have read the descriptions of every neighbouring skill and can state the
      boundary in a sentence — unstable routing means two students ask the same
      thing and get different answers
- [ ] There is an `## Intake` section that reads `project/project.yml` before
      starting work
- [ ] The role's questions are added to
      `.claude/skills/project-intake/references/question-bank.md`
- [ ] The fields the role owns are added to
      `.claude/skills/project-intake/assets/project.yml.template`
- [ ] If it produces a document — the type and template path are registered in
      `.claude/skills/document-control/SKILL.md`
- [ ] If it owns a gate — the criteria and stage order are added to
      `.claude/commands/gate.md`
- [ ] It appears in the tables in `WORKFLOW.md` and `README.md`

## What makes the skills in this set different

**They can refuse.** A role that answers "sure, here you go" every time is worth
nothing. A role that can say what is missing and why the work cannot move on is
the thing the student is here to learn.

**They say when they do not know.** No skill in this set guesses; they write `TBD`.

**They know who they are not.** The `Do NOT use for` line is not ceremony — it is
what lets 24 skills coexist without competing for the same request.
