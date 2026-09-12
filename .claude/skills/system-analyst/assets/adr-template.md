# ADR-[NNN] — [Decision, stated as a noun phrase]

| Item | Value |
|---|---|
| Status | Proposed / Accepted / Superseded by ADR-NNN |
| Date | [date] |
| Decided by | [name and role — or "proposed by the analyst, pending confirmation"] |
| Supersedes | [ADR-NNN, or —] |

The `Decided by` line matters. A proposal filed as a decision is how a team
ends up building something nobody chose.

---

## Decision

One sentence. What was decided, in the active voice.

## Context

What forced this decision now. The constraints in play, the requirements that
bear on it, and what was already fixed before this decision was reached.

State the question being answered precisely — "how is user data stored on the
device and reconciled with the server", not "which database".

## Criteria

Derived from the non-functional requirements, written before the options were
scored. A criterion with no requirement behind it is a preference — drop it or
get it adopted as a requirement.

| # | Criterion | Weight | Derived from |
|---|---|---|---|
| 1 | | High/Med/Low | [req ID] |

## Options considered

### Option A — [name]

How it works, in two or three sentences.

**For:** …
**Against:** …

### Option B — [name]

…

### Option C — [name]

…

Each option must be one you could defend honestly. A straw man invalidates the
exercise.

## Comparison

| Criterion | Weight | Option A | Option B | Option C |
|---|---|---|---|---|
| | | | | |

## Decision and reasoning

[Option X]. The deciding criterion was [#N], because [requirement] is a
must-have and [rejected option] fails it outright / satisfies it only at a cost
of […].

Say plainly what this costs relative to the cheapest option, and whether that
cost needs escalating to whoever owns the schedule.

## Verification against must-have requirements

| Req | How this decision satisfies it | Verdict |
|---|---|---|
| | | PASS / PASS, unverified / FAIL |

Verify one requirement at a time. Group verification hides failures.
"PASS, unverified" means sound but unmeasured — name the measurement owed.

## Consequences

**Accepted good:**
- …

**Accepted bad:** — the ones you are choosing to live with
- …

**New work this creates:**
- …

**Reversibility:** [how expensive is undoing this in three months, and what
would trigger revisiting it]

## Assumptions

| ID | Assumption | If wrong | Owner |
|---|---|---|---|
| | | | |
