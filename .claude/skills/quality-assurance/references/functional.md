# Functional Correctness

Verify the implementation does what the spec says — across the happy path, the
edges, and the failures. The acceptance criteria are the rubric; each criterion is
either demonstrably met or it is a finding.

## Table of contents
- Establishing the rubric
- What to check
- How to verify (read → reason → test)
- Test authoring conventions (Vitest / Playwright)
- Common findings and their severity

## Establishing the rubric

Turn the spec into a checklist of verifiable statements *before* looking at the
code, so the code doesn't anchor your expectations. Each acceptance criterion
becomes one or more checks with a clear observable outcome. If a criterion is
vague ("should be fast"), pin it to something testable (a budget, a threshold) or
flag it as an untestable gap in the report.

## What to check

- **Happy path** — the primary user flow completes and produces the specified
  result. This is table stakes; a failure here is a `BLOCKER`.
- **Edge cases** — empty states, single item vs many, max lengths, boundary
  values, slow/failed network, unauthorized access, concurrent actions.
- **Error handling** — invalid input is rejected with a usable message; failures
  don't crash, lose data, or leave the UI in an inconsistent state.
- **State & side effects** — nothing leaks between renders; cleanup runs; no
  double-submits; optimistic updates reconcile or roll back.
- **Regressions** — the change didn't break an adjacent, previously-working flow.
  Check whatever the diff touches transitively.
- **Contract** — inputs/outputs, props, and API shapes match what callers expect;
  types are honest (no `any` hiding a real mismatch).

## How to verify

Prefer reasoning + targeted tests over clicking through blindly.

1. **Read the diff** against the rubric — map each criterion to the code that
   implements it. A criterion with no corresponding code is a finding.
2. **Reason about the edges** the code doesn't visibly handle — then confirm by
   test or by reading, not by assuming.
3. **Run or author tests** for anything you can't confirm by inspection, and for
   anything a future regression would silently break.
4. **Report** — for each failing check: `file:line — expected X, got Y → fix`.

## Test authoring conventions

Author tests that pin behaviour to the spec, not to the current implementation.

- **Unit / integration → Vitest + Testing Library.** Query by role/label/text the
  way a user perceives the UI, not by test-id or DOM structure — a test that
  breaks on a refactor but not on a behaviour change is testing the wrong thing.
  One behaviour per test; assert the observable outcome.
- **E2E → Playwright.** Cover the critical user journeys end to end. Use
  role-based locators (`getByRole`), web-first assertions (auto-retrying), and
  avoid fixed `waitForTimeout`. Keep them deterministic — seed data, control the
  clock, stub the network at the boundary.
- **Coverage is a signal, not a target.** A green suite that never exercises the
  failure paths is not a PASS. Judge by whether the *risky* behaviour is pinned,
  not by a percentage.

## Common findings and their severity

- Happy-path flow doesn't complete → **BLOCKER**
- Data loss / corruption on error → **BLOCKER**
- Unhandled edge case that a real user will hit → **MAJOR**
- Missing validation with a graceful-but-wrong fallback → **MAJOR**
- Console error/warning with no user impact → **MINOR**
- Missing test for a low-risk branch → **MINOR / NIT**
