---
description: Check the current stage's gate, name what is missing, and record the result in project.yml
argument-hint: "[G1|G2|G3|G4|G5|G6 — leave empty to check the current gate]"
---

Check the gate between stages, and record the result so it can be audited later.

## Before starting

Read `project/project.yml`. If it does not exist, tell the user to run `/kickoff`
first, and stop.

If no gate was named in the arguments, pick one from `stage:`

| stage | gate |
|---|---|
| `intake` | G1 |
| `product` | G1 |
| `analysis` | G2 |
| `design` | G3 |
| `build` | G4 |
| `review` | G5 |
| `quality` | G6 |
| `release` | report that the pipeline is complete |

## The rule that matters most

**Do not pass it because you want it to pass.** A gate that always passes is not a
gate. If the evidence cannot be found, it has not passed — say what would have to
exist for it to pass. Never assume the student probably did it: you must see the
file, the content, the actual tick.

**Check the artifacts, do not ask whether the work was done.** Open the files in
`project/` and read them.

## The gates

### G1 · Definition of Ready — requirements ready to hand to the analyst
The full criteria are in the `product-owner` skill under Definition of Ready.

- [ ] Problem and users are named specifically, not as "users"
- [ ] Acceptance criteria written, including at least one unhappy path
- [ ] Design or content available, or explicitly stated as not needed
- [ ] Dependencies identified
- [ ] Relevant non-functional requirements stated
- [ ] It is known how this will be measured after release — and
      `outcome.metric` is not a number that can only go up
- [ ] Sized, with no open research question blocking the estimate
- [ ] `scope.out` is not empty — a scope with no "not doing" list is not a scope

### G2 · Handback from the system analyst
Read `.claude/skills/system-analyst/assets/design-handback-checklist.md` and follow
it. The core of it:

- [ ] Every requirement traces to a design element, and every element back to a requirement
- [ ] Every acceptance criterion has at least one test case
- [ ] Must-have non-functional requirements are checked against the architecture
      one at a time, not in aggregate
- [ ] Every structural decision records the rejected alternatives and why
- [ ] Assumptions are labelled as assumptions, not mixed in with facts
- [ ] Requirement IDs are unchanged from the source; no new numbering

### G3 · Design system ready to build against

- [ ] `DSN-XXX-001` exists and is registered
- [ ] Tokens complete across all four groups — color, type, spacing, and the rest
- [ ] Every text-on-background pair states its measured contrast ratio, not "passes"
- [ ] Every component has its full state set, not just the default state
- [ ] Every screen has empty, loading, error and unauthorized states
- [ ] Reviewed against the `anti-ai-design-patterns` skill
- [ ] The document's traceability table links requirements to screens

### G4 · Definition of Done — development complete
The criteria live in `build.definition_of_done` in `project.yml`, and the full
template is at `.claude/skills/developer/assets/definition-of-done.md`.

If `build.definition_of_done` is still empty, the gate **fails** — say that the
criteria have to be agreed first. A gate with no criteria is not a gate.

### G5 · Code review

- [ ] `RVW-XXX-001` exists, or a recorded review report does
- [ ] No `BLOCKER` findings outstanding
- [ ] `MAJOR` findings are fixed, or recorded as deferred with who decided
- [ ] The decision is not `REQUEST CHANGES`

### G6 · Ready to release

- [ ] A QA report exists and its verdict is not `BLOCK`
- [ ] The release checklist at
      `.claude/skills/devops-release/assets/release-checklist.md` is complete
- [ ] **The rollback has actually been rehearsed** — never tried means fail
- [ ] The watch plan names the signal, a numeric threshold, who is watching, and
      for how long — all four

## Reporting

Print exactly this shape:

```
## Gate <id> · <name>

**Result:** PASS | NOT YET
**Checked against:** <the files actually opened>

### Passing
- <criterion> — <the evidence seen>

### Missing
- <criterion> — <what is absent, and what would make it pass>

### Next
<the command or skill to run>
```

## Recording the result

Append an entry under `gates:` in `project/project.yml`:

```yaml
- id: G1
  name: Definition of Ready
  checked: YYYY-MM-DD
  result: pass          # or fail
  missing:
    - <what was missing>
```

**Advance `stage:` only on a `pass`.** The stage order is
`intake → product → analysis → design → build → review → quality → release`.

On a `fail`, do not advance, and never delete earlier `gates` entries — the record
of what failed and why is what the student comes back to.

Arguments: `$ARGUMENTS`
