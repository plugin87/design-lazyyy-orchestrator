---
name: quality-assurance
description: The quality gate that verifies a built implementation against its spec across three dimensions — functional correctness, visual and design-system fidelity, and accessibility — and returns a single verdict of PASS, PASS WITH ADVISORIES, or BLOCK. Use this whenever a feature, component or page has been implemented and needs verification before it ships: "check my implementation", "verify against the design", "is this ready to merge", "does this meet the acceptance criteria", or a pre-deploy review — even when the word QA is not used. Do NOT use it to judge the code itself for correctness, reuse and maintainability — that is the code-reviewer skill; not to build the visual-regression test harness — that is qa-testing-visual-regression; and not to decide whether the release may proceed — that is devops-release.

---

# Quality Assurance

A gate that answers one question: **is this implementation ready to ship?**

It checks the work against its spec on three axes and returns a single verdict —
`PASS`, `PASS WITH ADVISORIES`, or `BLOCK` — backed by findings the developer can act on.

This skill does **not** rewrite the feature. It verifies, reports, and (only when
asked) applies the smallest fix that clears a blocker. Keep the reviewer and the
author roles separate: report first, fix second, and never do both silently.

## Inputs to gather first

Start at `project/project.yml` — it already holds the conformance level, the
supported browsers, and the design reference this gate needs. If it does not
exist, run `project-intake`. If `quality.*` is blank, ask round 6 from
`project-intake`'s `references/question-bank.md` — WCAG level, browsers, and
which file counts as "the design" — and write the answers back so the next
review does not re-litigate them.

Then establish what "correct" means for this specific change. Do not invent a
spec — if a source of truth is missing, say so in the report rather than
guessing.

1. **What changed** — the diff, branch, PR, or the specific component/page/route
   under review. Scope the gate to this; do not audit the whole codebase.
2. **Functional spec** — acceptance criteria (often produced by the `product-owner`
   skill), a ticket, or explicit user requirements. This is the pass/fail rubric
   for the functional dimension.
3. **Design source of truth** — the Figma frame, and the design tokens the project
   builds on (colors, spacing, type, radii). Visual QA compares the build to *this*,
   not to the reviewer's taste.
4. **Accessibility target** — the conformance level required (default **WCAG 2.2
   Level AA**; government / DGA work is often the trigger). Note any locale
   requirements (e.g. Thai-language content, RTL, i18n).

If any input is absent, run the dimensions you *can*, and list the missing input as
an explicit gap in the report — a gate with an unknown spec is not a PASS.

## Workflow

1. **Scope** — identify exactly what's under review and pull the four inputs above.
2. **Select dimensions** — run all three by default. Skip one only if the change
   genuinely can't touch it (e.g. a pure copy change won't need functional test
   authoring) and record why it was skipped.
3. **Run each selected dimension** — read the matching reference file and follow it:
   - Functional correctness → `references/functional.md`
   - Visual & design-system fidelity → `references/visual.md`
   - Accessibility (WCAG) → `references/accessibility.md`
   Read only the references for the dimensions you're running. Track the pass with
   `assets/qa-checklist.md` so "skipped" and "not checked" never get confused.
4. **Classify every finding** by severity (see below) — this is what turns a pile
   of observations into a gate decision.
5. **Emit the QA report** in the format below (`assets/qa-report-template.md` for
   the long form). The verdict is derived from the findings, not chosen freely: any
   `BLOCKER` ⇒ `BLOCK`; no blockers but ≥1 `MAJOR`/`MINOR` ⇒ `PASS WITH ADVISORIES`;
   nothing above `NIT` ⇒ `PASS`.
6. **Stop.** Do not start fixing unless the user asks. If they do, fix the smallest
   thing that clears each blocker, then re-run only the affected dimension.

## Severity scale

Apply the same scale across all three dimensions so the verdict is comparable.

- **BLOCKER** — ships broken or excludes users: functional regression, data loss,
  a WCAG Level A failure, a component that doesn't match the approved design in a
  way users will notice. Blocks the gate.
- **MAJOR** — real defect, not ship-stopping alone: a WCAG AA failure, a token
  drift a designer would reject in review, a missing edge-case handler.
- **MINOR** — small, low-impact: off-by-a-few-px spacing, a non-critical console
  warning, a missing but non-required aria attribute.
- **NIT** — preference or polish; never affects the verdict. Report sparingly.

Calibrate honestly. Inflating a nit to a blocker erodes trust in the gate; burying
a real exclusion as a nit is worse. When unsure between two levels, state the
user-facing consequence and let that decide.

## Report format

Emit exactly this structure. Keep findings specific and actionable — every one
should name *where*, *what*, and *the fix*.

```
## Quality Assurance — <component / feature / PR>

**Verdict:** BLOCK | PASS WITH ADVISORIES | PASS
**Scope:** <what was reviewed>  ·  **Spec source:** <ticket / Figma / criteria, or "MISSING">

### Functional            [PASS | ADVISORIES | BLOCK | SKIPPED — reason]
- [BLOCKER] <file:line> — <what's wrong> → <fix>
- [MINOR]   <file:line> — <what's wrong> → <fix>

### Visual & Design System [PASS | ADVISORIES | BLOCK | SKIPPED — reason]
- [MAJOR]   <element> — token drift: uses <actual> vs <expected token> → <fix>

### Accessibility (WCAG 2.2 AA) [PASS | ADVISORIES | BLOCK | SKIPPED — reason]
- [BLOCKER] <element> — <SC number + name>: <what fails> → <fix>

### Gaps
- <any missing spec / untestable area that limits confidence in this gate>
```

If the change is trivial and clean, the report can be three lines — don't pad it.
The point is a trustworthy verdict, not a long document. For a formal review
(release gate, client handoff, audit trail), use `assets/qa-report-template.md`,
which adds criteria coverage, what was actually run, and the next action.

## Files in this skill

- `references/functional.md` — building the rubric from acceptance criteria, what
  to check across happy path / edges / failures, Vitest + Playwright conventions
- `references/visual.md` — design-source comparison, token compliance, responsive
  and state coverage, Playwright visual regression
- `references/accessibility.md` — the three-layer method (axe-core → keyboard →
  semantics), contrast, WCAG 2.2 additions, Thai-language notes
- `assets/qa-checklist.md` — tickable run sheet across all three dimensions
- `assets/qa-report-template.md` — full QA report with coverage tables

## How this fits the pipeline

This is the **last gate before the deployment/DevOps tier**. Upstream, the
`product-owner` skill defines the acceptance criteria this gate scores against;
implementation skills produce the code it reviews. A `BLOCK` verdict sends work
back to implementation, not forward to deploy.
