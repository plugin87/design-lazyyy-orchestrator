# Estimation, Velocity, and Forecasting

Contents:
1. Relative sizing (story points)
2. Planning poker, run properly
3. Three-point / PERT
4. Reference class forecasting
5. Velocity: computing and using it
6. Throughput forecasting (no points)
7. Monte Carlo, the cheap version
8. Capacity math worked example
9. Estimation traps

---

## 1. Relative sizing (story points)

Points measure size and uncertainty combined, relative to other work — not
hours. The value is that humans compare well and predict absolutely badly.

Use a modified Fibonacci scale: 1, 2, 3, 5, 8, 13. Stop there. If something is
a 20, it's an epic that hasn't been split.

**Anchor with reference stories.** Pick two or three completed stories the team
remembers and fix them as the definition of 2 and 5. Re-anchor when the team
changes. Without anchors, points inflate quietly over a year and velocity
becomes meaningless.

Rough meaning in practice:

| Points | Feels like |
|---|---|
| 1 | Trivial, known, done in a sitting |
| 2 | Small, understood, no unknowns |
| 3 | Normal story, minor unknowns |
| 5 | Substantial, some unknowns, several parts |
| 8 | Large; consider splitting |
| 13 | Split it. Not negotiable in practice. |

Points are per-team. Comparing velocity between teams measures nothing and
corrodes trust immediately.

---

## 2. Planning poker, run properly

1. PO reads the story and the acceptance criteria.
2. Team asks questions until the shape is clear (not until every detail is
   resolved).
3. Everyone reveals simultaneously — simultaneity is the whole point; anchoring
   destroys the estimate.
4. If the spread is one step, take the higher and move on.
5. If wider, the highest and lowest explain their reasoning, then re-vote. Two
   rounds maximum; if it doesn't converge, the story needs splitting or a spike.

The disagreement is the deliverable. A 3-vs-13 split almost always means one
person knows about a dependency, a legacy quirk, or a test surface the other
doesn't.

Timebox refinement to two minutes per story on average. Deep discussions get
parked, not resolved in the room.

---

## 3. Three-point / PERT

For a single uncertain item:

```
Expected  = (O + 4M + P) / 6
Std dev   = (P − O) / 6
```

Where O = optimistic (everything goes right), M = most likely, P = pessimistic
(realistic bad case, not catastrophe).

**Example:** data migration — O = 3d, M = 6d, P = 15d.

```
Expected = (3 + 24 + 15) / 6 = 7 days
Std dev  = (15 − 3) / 6 = 2 days
```

Report as "7 days ± 2; ~85% confident by 9 days." The spread is the signal: a
wide P–O gap means you don't understand the work yet, and the correct response
is often a spike rather than a bigger number.

To combine several independent items, sum the expected values and combine the
deviations as the square root of the sum of squares — not by adding the
deviations, which massively overstates total risk.

---

## 4. Reference class forecasting

Ask: what actually happened the last N times we did something like this?

This beats every bottom-up estimate in accuracy, and teams almost never do it
because each project feels unique. It isn't. Keep a simple record: project
type, original estimate, actual, ratio. Within a year you'll know your team's
optimism multiplier — commonly somewhere between 1.3x and 2x — and you can
apply it explicitly instead of pretending it doesn't exist.

If a stakeholder rejects a padded number, the reference class data is the
argument: "the last five projects like this took 1.6x the initial estimate;
this figure includes that."

---

## 5. Velocity: computing and using it

- Count only work that met the Definition of Done inside the sprint. No partial
  credit — partial credit is what makes velocity lie.
- Use a rolling average of the last 3–5 sprints, and always carry the min and
  max alongside it.
- Discard sprints distorted by holidays or half the team on leave, or normalize
  them by capacity (points per available person-day) instead.
- Expect a new team to take 3–4 sprints before velocity means anything.

**Forecast:**

```
Sprints remaining = backlog points ÷ velocity
```

Run it three times, at min, average, and max velocity, and report all three.

**Example:** 180 points remaining; last five sprints were 28, 34, 31, 22, 35.
Average 30, min 22, max 35.

```
Optimistic:  180 / 35 = 5.1 → 6 sprints
Likely:      180 / 30 = 6.0 → 6 sprints
Pessimistic: 180 / 22 = 8.2 → 9 sprints
```

So: 6–9 sprints, most likely 6–7. Then add the assumption line: no scope
growth, team stable, dependency X on time. If scope has been growing ~5% per
sprint historically, model that too — it's the most common reason forecasts
break.

---

## 6. Throughput forecasting (no points)

Mature teams often drop estimation entirely and forecast from item counts,
which works because story sizes cluster more than people expect.

Track items completed per week. Forecast:

```
Weeks remaining = items remaining ÷ weekly throughput (use the range)
```

Also track **cycle time** (in-progress → done) per item and use its 85th
percentile as your reliable per-item commitment. "85% of stories finish within
6 days" is a far more useful promise to a stakeholder than an estimate.

If you're moving a team off points, run both for a few sprints so the forecasts
can be compared before the old data is abandoned.

---

## 7. Monte Carlo, the cheap version

You don't need a tool. Take the last 10 sprints' velocities, and simulate:
randomly draw a velocity, subtract from remaining work, repeat until the work
is gone, count sprints. Do that ~1,000 times in a spreadsheet or a few lines of
script. The distribution of results gives you real confidence levels: "50% by
sprint 6, 85% by sprint 8."

This is the most credible thing you can put in front of a nervous stakeholder,
because it uses only the team's own history and makes the uncertainty explicit
rather than arguable.

---

## 8. Capacity math worked example

Team of 5, two-week sprint (10 working days).

```
Gross:                          5 × 10 = 50 person-days
Public holiday (1 day, all):            −5
Planned leave (one person, 3d):         −3
On-call rotation (0.5 person):          −5
Ceremonies & meetings (~15%):           −5.5
                                      ------
Available:                              31.5 person-days
Buffer for interruptions (18%):         −5.7
                                      ------
Plannable:                              ~26 person-days
```

That's roughly half the naive number. Teams that plan against the 50 and blame
the team for missing it are measuring their own arithmetic.

---

## 9. Estimation traps

- **Estimates becoming commitments.** Once that happens, the team inflates
  defensively and you lose all signal. Separate the two explicitly in how you
  report.
- **The 90% done story.** Work that carries over repeatedly usually has an
  unresolved dependency or unclear acceptance criteria. Investigate the story,
  not the person.
- **Anchoring.** Never say a number before the team does. "I was thinking
  three days?" ends the estimation session.
- **Ignoring the long tail.** Code review, QA, integration, deployment,
  documentation, and bug-fix loops routinely equal the implementation time.
- **Point inflation.** Same-sized work drifting upward over quarters. Re-anchor
  with reference stories every few months.
- **Comparing teams.** Guarantees inflation and hides real problems.
- **Averaging to avoid conflict.** The outlier usually knows something.
