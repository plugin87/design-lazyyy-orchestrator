# Test design and traceability

Converting acceptance criteria into tests that fail for the right reason, and
proving nothing was missed.

---

## 1. From acceptance criterion to test case

An acceptance criterion states an intent. A test case states an executable
procedure. The gap between them is data, preconditions, and observability.

**Acceptance criterion (from the requirements):**

> Given the user has a 6-day cycle with 5 training days and 1 rest day, started
> 8 days ago, when the app is opened, then day 3 of the cycle is shown with
> that day's items, without the user selecting anything.

**Test case:**

```
TC-S1-001   Cycle position after wrap-around
Traces to   S1 / AC 5.1.1
Priority    High (must-have requirement, core differentiator)
Type        Functional, positive

Preconditions
  - App installed, no prior data
  - Device date set to 2026-08-01, time 09:00, timezone Asia/Bangkok
  - Day-start offset at default (00:00)

Setup data
  - Program "P1": cycle length 6
      day 1 training (3 items), day 2 training (3), day 3 training (4),
      day 4 training (3), day 5 training (3), day 6 rest
  - Enrolment start date 2026-07-24 (8 days before)

Steps
  1. Launch the app
  2. Observe the day view without interacting

Expected result
  - Header shows "Day 3"
  - Exactly the 4 items configured for day 3 are listed, in configured order
  - No selection or navigation was required
  - Elapsed time from launch to list rendered ≤ 2s

Postconditions
  - No data written
```

What made it executable: concrete dates, a named data set, an unambiguous
expected result, and the non-functional check folded in rather than left to a
separate "performance testing" phase that never happens.

**Expected results must be observable.** If two competent testers could
disagree about whether it passed, rewrite it. "The list appears correctly" is
not a result; "exactly these 4 items, in this order" is.

---

## 2. Choosing a technique

Do not write test cases by intuition and then count them. Pick the technique
that matches the shape of the logic — it tells you how many cases you need and
when you can stop.

| Technique | Use when | Produces |
|---|---|---|
| Equivalence partitioning | An input has classes that behave alike | One case per class |
| Boundary value analysis | Any numeric or date range | min−1, min, min+1, max−1, max, max+1 |
| Decision table | Several conditions combine to determine behaviour | One case per meaningful combination |
| State transition | Entity with a status field | One case per valid edge, plus attempts at invalid ones |
| Pairwise | Many independent parameters | Coverage of all pairs, far fewer cases than exhaustive |
| Error guessing | Experience of how this breaks | The cases the catalogue below lists |

Boundary analysis earns its place most often. A capacity requirement of "1 to
14 days per cycle" needs cases at 0, 1, 2, 13, 14, and 15 — and the 0 and 15
cases are the ones that reveal whether the constraint lives in the schema or
only in the form.

### Decision tables

When behaviour depends on a combination, tabulate rather than prose.

| # | Has program? | Today is | Network | Expected |
|---|---|---|---|---|
| 1 | No | — | Any | Route to program setup, never a blank screen |
| 2 | Yes | Training day | Online | Day view with items |
| 3 | Yes | Training day | Offline | Identical to #2, no network error, no spinner |
| 4 | Yes | Rest day | Online | Explicit rest-day view |
| 5 | Yes | Rest day | Offline | Identical to #4 |
| 6 | Yes | Before start date | Any | Defined behaviour — specify, don't leave to the implementation |

Row 6 is the value of the technique: filling the grid exposes a case the
requirements never mentioned. Report it as a gap.

---

## 3. Edge-case catalogue: date, time, and recurrence

Give this disproportionate coverage. It is pure logic, cheap to test, and its
bugs surface months later on a user's device and never on yours.

| Case | Setup | Watch for |
|---|---|---|
| Day-start offset | Offset 03:00, act at 00:30 | Belongs to the previous program day |
| Day-start offset, upper edge | Offset 03:00, act at 03:01 | First moment of the new day |
| Month boundary | 31 Jan → 1 Feb | Day arithmetic that assumes 30-day months |
| Year boundary | 31 Dec → 1 Jan | Year rollover in derived values and cache keys |
| Leap day | Cycle spanning 29 Feb 2028 | Off-by-one in elapsed-day counts |
| Non-leap 29 Feb | Feb 2027 | Any code that constructs 29 Feb unconditionally |
| DST forward | 23-hour local day | Elapsed-days computed from hours |
| DST backward | 25-hour day, repeated local hour | Duplicate or lost program day |
| Timezone travel east | UTC+7 → UTC+12 | Local date jumps forward; day skipped |
| Timezone travel west | UTC+12 → UTC+7 | Local date jumps back; day repeated |
| Clock set backwards | Device date moved back 2 days | Negative elapsed days |
| Clock set forward | Moved forward 400 days | Position far past cycle end |
| Start date in the future | Enrolment starts tomorrow | Must be defined, not negative or crashing |
| Exact cycle multiple | Elapsed = 0, 6, 12 with cycle 6 | Modulo returning 0 instead of position 1 |
| Cycle length 1 | Single-day cycle | Degenerate modulo |
| Cycle length at max | 14 days | Boundary of the stated capacity |
| Rest day at position 1 | Program starts on a rest day | First-run flow lands on a rest view |
| All days are rest days | Pathological config | Must not present as an error state |

### Offline and sync cases

| Case | Watch for |
|---|---|
| Airplane mode, every capability exercised | No network errors, no spinners, all writes succeed |
| Write offline, force-quit, relaunch | Data intact — proves the write was durable, not in memory |
| Offline for 30 days, then reconnect | Batch size, chunking, no timeout, no data loss |
| Same record edited on two offline devices | Conflict rule applied as specified, result stated |
| Same item completed on two devices | Union, per the append-only rule; no duplicate count |
| Sync interrupted mid-batch | Resumable; no half-applied state |
| Server returns 4xx for one item | Item quarantined; the rest of the batch still syncs |
| Device clock ahead of server | Ordering uses server receipt, not device time |

### Storage, migration, and lifecycle

| Case | Watch for |
|---|---|
| Storage full during a write | Write refused, existing data intact, actionable message |
| Permission denied on storage | Fails closed with a real message, not a crash |
| Upgrade from every previously shipped version | Migration path tested from each, not just the last |
| Downgrade to an older build | Detects a newer schema and refuses to write rather than corrupting |
| Migration fails midway | Old data intact, nothing partially written, retry offered |
| Data at stated capacity limits | Performance budget still met at 20 programs / 30 items / 3 years |
| Data beyond stated limits | Degrades gradually; never rejects a write, never loses data |

### Accessibility

| Case | Watch for |
|---|---|
| Screen reader on a completed item | Status announced, not conveyed by colour alone |
| System text size at maximum | No truncation, no overlap, no unreachable controls |
| Touch targets | Meet the stated minimum size |
| Contrast | Meets the stated standard and level |
| Keyboard or switch navigation (web) | Every action reachable; focus order sensible |

---

## 4. Coverage rules

- **Every acceptance criterion produces at least one test case.** No exceptions;
  an AC with no test is either untestable — a defect in the AC — or forgotten.
- **Every requirement gets at least one negative case.** A suite that only
  proves the system works when nothing goes wrong proves very little.
- **Non-functional requirements get test cases too.** Latency budgets,
  capacity, accessibility, migration. If they live only in a prose section,
  nobody checks them.
- **Traceability runs both ways** — see section 5.
- **Count cases per requirement and look at the distribution.** A must-have
  requirement with two cases and a nice-to-have with fifteen is a signal about
  where attention went, not about where risk is.

---

## 5. Traceability matrix

Two directions, both required.

**Forward — requirement to design to test.** Proves nothing was dropped.

| Req | Statement | Design element | Test cases | Status |
|---|---|---|---|---|
| S1 | Show today's items on launch | `ENROLMENT`, `PROGRAM_DAY`, BR-01, UC-01, Day view | TC-S1-001…009 | Covered |
| S2 | Record completion status | `EXECUTION_LOG`, BR-03/04, UC-03 | TC-S2-001…011 | Covered |
| S3 | Fully functional offline | ADR-002 local-first, outbox | TC-S3-001…008 | Covered |
| S6 | 7 and 30 day history | *(deferred — model must not block)* | — | Deferred, not blocked |

**Backward — test to requirement.** Proves nothing was invented.

| Test | Traces to | Notes |
|---|---|---|
| TC-S1-001 | S1 / AC 5.1.1 | |
| TC-X-014 | **none** | Investigate: undocumented behaviour or scope creep |

A test with no requirement is not automatically wrong — it is often a real edge
case nobody wrote down. Either way it needs resolving: raise the missing
requirement, or delete the test.

**Report the gaps, don't just build the table.** The output that matters is the
list of requirements with no tests, tests with no requirements, and design
elements with no requirement behind them.

---

## 6. Test data

Specify the data sets once and reference them, rather than restating setup in
every case.

```
DS-01  Minimal    1 program, 1-day cycle, 1 item              — degenerate cases
DS-02  Typical    1 program, 6-day cycle (5 training, 1 rest) — most functional cases
DS-03  Capacity   20 programs, 14-day cycles, 30 items/day,
                  3 years of history                          — performance, pagination
DS-04  Migration  Data written by each previously shipped
                  schema version                              — upgrade path
DS-05  Conflict   Same records edited on two devices while
                  both offline                                — sync resolution
```

DS-03 and DS-04 are the ones teams skip, and they are exactly the ones that
catch the defects that reach production.
