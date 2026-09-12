# Prioritization

Contents:
1. Choosing a method
2. RICE
3. WSJF and cost of delay
4. MoSCoW
5. Kano
6. Impact/effort 2x2
7. Handling stakeholder pressure
8. How prioritization goes wrong

---

## 1. Choosing a method

| Use | When |
|---|---|
| RICE | Many candidates, rough quantitative data, no fixed date |
| WSJF | Flow-based delivery; delay is expensive and sizes vary widely |
| MoSCoW | Fixed date or fixed budget; you need a negotiable cut list |
| Kano | Deciding depth of investment in a feature already chosen |
| Impact/effort 2x2 | Live workshop, need convergence in 30 minutes |

The method matters less than applying one consistently and showing the inputs.
A visible mediocre model beats an invisible good one, because a visible model
can be argued with.

---

## 2. RICE

```
RICE = (Reach × Impact × Confidence) / Effort
```

- **Reach** — users or events affected per time period. Use a real unit:
  "1,200 sessions/month," not a 1–5 score.
- **Impact** — per-user effect on the goal. Standard scale: 3 massive, 2 high,
  1 medium, 0.5 low, 0.25 minimal.
- **Confidence** — how much you trust the above: 100% high, 80% medium,
  50% low. If it's below 50%, you need a spike, not a score.
- **Effort** — person-months (or person-weeks; just stay consistent).

**Worked example:**

| Feature | Reach/qtr | Impact | Conf. | Effort | RICE |
|---|---|---|---|---|---|
| Saved payment methods | 9,000 | 1 | 0.8 | 2 | 3,600 |
| Guest checkout | 14,000 | 2 | 0.8 | 3 | 7,467 |
| Order tracking page | 20,000 | 0.5 | 1.0 | 1 | 10,000 |
| Loyalty tier redesign | 3,000 | 3 | 0.5 | 6 | 750 |

Order: tracking page → guest checkout → saved payments → loyalty.

Notice the tracking page wins on modest impact and cheap effort. That's RICE
working correctly — but also its main weakness: it systematically favours small
safe wins over the one big bet that changes the business. Run RICE, then ask
explicitly whether anything strategic got starved. Reserve capacity for bets
outside the model rather than trying to make the model produce them.

---

## 3. WSJF and cost of delay

```
WSJF = Cost of Delay / Job Size
Cost of Delay = User/business value + Time criticality + Risk reduction
```

Score each component 1–10 relative to the others in the set — the numbers are
comparative, not absolute. Anchor by picking the smallest item in the set as
your 1.

Time criticality is the term people skip, and it's the one that carries the
real information: does the value decay? A tax feature before filing season and
the same feature after are different items.

WSJF's strength is that it makes small-and-urgent beat large-and-valuable
automatically, which is usually correct for flow. Its weakness is that
relative scoring drifts across sessions — re-anchor each time rather than
comparing this month's scores to last month's.

---

## 4. MoSCoW

- **Must** — release is worthless or illegal without it
- **Should** — painful to omit, but there's a workaround
- **Could** — nice, included only if things go well
- **Won't (this time)** — explicitly out, and named so nobody assumes it's in

The discipline: **Must should be under ~60% of effort.** If it's higher, the
release has no shock absorber and the date is fiction. When a stakeholder
insists everything is Must, the productive question is "what would you ship if
the deadline moved up two weeks?" — that reveals the real Musts fast.

The "Won't" column is the most valuable one. Write it down and circulate it;
almost all late-stage scope fights come from things that were never explicitly
excluded.

---

## 5. Kano

Classifies features by how satisfaction responds to investment:

- **Basic (must-be)** — absence causes anger, presence earns nothing. Password
  reset, uptime, correct totals. Meet the bar, spend nothing beyond it.
- **Performance (linear)** — more is better, proportionally. Speed, storage,
  search accuracy. Invest where you compete.
- **Delight (attractive)** — absence unnoticed, presence disproportionately
  loved. Invest selectively, and know delighters decay into basics over time
  (once one competitor has it, everyone must).
- **Indifferent** — users don't care. Stop building these; they're usually
  someone's pet idea.
- **Reverse** — some users actively dislike it. Make it optional or don't ship.

Use Kano to answer "how good does this need to be?" — not "should we build
it?" It's the right tool when the team is gold-plating a basic or
under-investing in a competitive performance attribute.

---

## 6. Impact/effort 2x2

Fastest way to get a room to agree. Axes: impact on the stated goal, effort to
build. Four quadrants: do now (high/low), plan (high/high), fill-in (low/low),
avoid (low/high).

Two rules make it honest: engineers place effort, not product; and no item may
sit on a line — force a side.

---

## 7. Handling stakeholder pressure

When someone insists their item jumps the queue, the response is not resistance
but exchange:

1. **Make the tradeoff visible.** "Yes — it displaces the payments work by two
   weeks. Confirming that's the trade?" Most requests evaporate here.
2. **Ask for the deadline's origin.** External commitment, regulatory date, or
   preference? Only two of those are real.
3. **Offer a smaller version.** Often 20% of the scope solves the actual
   trigger.
4. **Write the decision down** with who made it and when. Prevents the same
   argument next month and protects the team from being blamed for the trade.

Escalate on data, not feelings: "three teams requested capacity totalling
1.4x what we have; here's the order, here's what falls out."

---

## 8. How prioritization goes wrong

- **False precision.** RICE scores of 3,600 vs 3,540 are the same number. Round
  hard and treat close scores as ties broken by judgement.
- **Scoring the solution instead of the problem.** Score the outcome; solutions
  get cheaper after design.
- **Ignoring dependencies.** The top item may be blocked by the fourth. Order
  the list, then sanity-check the sequence for feasibility.
- **Ignoring maintenance and debt.** Reserve a standing share of capacity
  (commonly 15–25%) before prioritizing features, rather than letting debt
  compete and always lose.
- **Re-prioritizing constantly.** Churn costs more than a slightly wrong order.
  Set a cadence and hold it between reviews unless something genuinely changes.
- **Confusing urgency with importance.** Whoever asked most recently is not a
  ranking input.
