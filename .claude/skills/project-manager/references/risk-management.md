# Risk, Dependencies, and Issues

Contents:
1. Risk vs issue vs dependency
2. Finding risks worth tracking
3. Scoring
4. Response strategies
5. The register, and how to keep it alive
6. Dependency management
7. Common project risks by category
8. Escalation thresholds

---

## 1. Risk vs issue vs dependency

- **Risk** — hasn't happened; might. Has a probability. Managed by mitigation.
- **Issue** — has happened. Probability is 100%. Managed by resolution and an
  owner today.
- **Dependency** — something outside your control that the plan needs. Managed
  by lead time, confirmation, and a fallback.

Keeping them separate matters because they need different conversations. A
register that mixes them produces meetings where nobody knows if they're
planning or firefighting.

---

## 2. Finding risks worth tracking

Prompts that surface real ones:

- What are we assuming that, if wrong, changes the plan? (Assumptions are
  risks with better PR.)
- What has gone wrong on similar projects here before?
- What depends on a person or team we don't control?
- What are we doing for the first time?
- Where is the work stacked at the end of the schedule?
- What would we notice too late?
- If this fails in three months, what would the post-mortem say?

That last question is the highest-yield one — run it as a pre-mortem at
kickoff, with the whole team, and record every answer as a candidate risk.

Discard risks that are generic ("the team might get sick") unless you can name
a response. A register of unactionable risks trains people to ignore it.

---

## 3. Scoring

Score probability and impact 1–5, multiply for severity.

| Score | Probability | Impact (on date, cost, or quality) |
|---|---|---|
| 1 | Very unlikely (<10%) | Negligible, absorbed by buffer |
| 2 | Unlikely (~25%) | Minor slip, days |
| 3 | Possible (~50%) | Noticeable, a sprint |
| 4 | Likely (~75%) | Major, milestone moves |
| 5 | Near certain (>90%) | Critical, project goal at risk |

Bands: 1–6 monitor · 8–12 active mitigation · 15–25 escalate now.

Two refinements worth applying:

- **Time criticality.** A risk whose mitigation window closes soon outranks a
  higher-scoring risk you can address any time. Track "mitigate by" dates.
- **Detectability.** A risk you'd spot immediately is safer than one that stays
  invisible until launch. Where detection is poor, the first mitigation should
  be adding a signal — a canary, a checkpoint, a test — not solving the risk
  itself.

---

## 4. Response strategies

- **Avoid** — change the plan so the risk can't occur. Use a proven library
  instead of the unproven one. Strongest option; most often skipped because it
  means giving something up.
- **Mitigate** — reduce probability or impact. Prototype early, add a test,
  train a second person, stage the rollout.
- **Transfer** — move the exposure. Contract terms, insurance, vendor SLA,
  managed service.
- **Accept** — consciously, in writing, with a trigger for revisiting. Fine for
  low severity. "Accepted, revisit if the vendor hasn't confirmed by the 14th."
- **Contingency** — the plan you execute if it happens anyway, with its own
  trigger condition defined in advance. Every high-severity risk needs one,
  because deciding under pressure is when teams choose badly.

Each response needs a named owner and a date. "The team" is not an owner.

---

## 5. The register, and how to keep it alive

Fields: ID · description (cause → event → effect) · category · probability ·
impact · severity · response · owner · mitigate-by date · status · last
reviewed.

Write descriptions causally: "Because the payment vendor's sandbox is
unavailable until October, integration testing may start three weeks late,
which would push the release past the seasonal freeze." Compare that with
"Payment integration risk" — only one of them can be acted on.

Keeping it alive:

- Review the top 5–10 weekly, in a standing slot. Not the whole register.
- Close risks explicitly, with what happened. Closure is what builds team trust
  that the register is real.
- Add new risks whenever the plan changes; a replan without new risks is a
  replan nobody stress-tested.
- Promote a risk to an issue the moment it materializes, and say so out loud —
  quiet promotion is how projects lose weeks.

---

## 6. Dependency management

For every external dependency record: what you need, from whom, by when, the
confirmation status, and the fallback.

Practical rules:

- **Confirm in writing with the actual owner**, not with someone who says
  they'll pass it on.
- **Add lead time you don't control**: procurement, legal review, security
  review, app store review, vendor onboarding. These are routinely
  underestimated by weeks.
- **Set a check-in cadence** — a date you'll verify progress, well before the
  need-by date, so a slip is discoverable while alternatives still exist.
- **Have a fallback for anything on the critical path.** If there isn't one,
  that's the single most important thing in your status report.
- **Sequence dependent work early.** Late dependencies leave no room to react.

---

## 7. Common project risks by category

**People** — key person is the only one who knows a system; attrition;
competing allocation to another project; new team member ramp-up assumed to be
zero.

**Technical** — unproven technology; integration with a system nobody
understands; performance unknown until load; data migration quality; accrued
debt in the area being changed.

**Scope** — requirements still forming; stakeholder who hasn't engaged yet
appearing at review; "small" late additions; unstated non-functional
expectations.

**External** — vendor timelines; third-party API changes or deprecation;
regulatory dates; procurement; client-side approvals over holidays.

**Process** — no environment for testing; release windows and freezes; approval
chains; dependency on another team's release train.

The two that most reliably sink schedules in practice: approvals nobody
scheduled, and integration with a system that has no owner.

---

## 8. Escalation thresholds

Agree these at kickoff so escalation is procedure rather than personality:

- Any risk scoring 15+
- Any slip to a milestone on the critical path
- Any dependency unconfirmed within X days of its need-by date
- Any scope change above an agreed size
- Any issue the team can't resolve within a defined window (commonly 48 hours)

Escalate with: what happened, impact in dates/cost, what you've already tried,
two or three options with tradeoffs, your recommendation, and the decision you
need with its deadline. Escalation is a request for a decision, not a transfer
of anxiety.
