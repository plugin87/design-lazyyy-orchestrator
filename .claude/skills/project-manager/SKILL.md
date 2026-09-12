---
name: project-manager
description: Plan and run delivery — sprint planning, estimation, velocity and forecasting, timelines and critical path, risk registers, and stakeholder communication. Use this skill whenever the user is dealing with HOW and WHEN work gets delivered — planning a sprint, sizing or estimating work, working out capacity, forecasting a ship date, building or replanning a timeline, chasing a slipping project, writing a status update or escalation, running a standup/retro/kickoff, tracking risks and dependencies, or reporting to stakeholders. Trigger it on casual phrasings too — "will we make the deadline", "we're behind", "how do I tell the client", "how many points can we take", "what's blocking us", "write the weekly update". Do NOT use for defining what to build, writing PRDs, user stories, or backlog prioritization — that is the product-owner skill.

---

# Project Manager

Delivery management is mostly about making reality visible early. Projects
rarely fail from one dramatic event; they fail from a series of small slips
that nobody added up until the end. The core loop is: plan honestly, measure
actuals, forecast from actuals rather than hope, and tell people the truth
while there's still time to act on it.

Two principles run through everything below:

- **Forecast with ranges, never single dates.** "Between Nov 12 and Nov 26,
  most likely Nov 19" is information. "Nov 19" is a promise you didn't have
  the data to make.
- **Escalate early and small.** A risk raised four weeks out is a scheduling
  conversation. The same risk raised three days out is a crisis with an
  audience.

## Intake

1. Read `project/project.yml` first. If it does not exist, run `project-intake`
   before planning anything — a schedule built on an unrecorded capacity number
   is a schedule nobody can defend when it slips.
2. Ask only what is still blank for this role. The questions are in
   `project-intake`'s `references/question-bank.md`, round 2: real available
   days after leave and meetings, iteration length, and whether the deadline is
   genuinely fixed.
3. Write the answers back to `project.yml` under `delivery`, and record any
   number the student estimated rather than knew under `assumptions` — when a
   forecast built on it turns out wrong, the chain has to be traceable.

## Choose the mode

| The user is… | Go to |
|---|---|
| Planning the next sprint | Sprint planning, below |
| Sizing work / arguing about points | `references/estimation-and-velocity.md` |
| Asking when something will be done | Forecasting, below + same reference |
| Building or fixing a timeline | Timeline & critical path, below |
| Worried about something going wrong | `references/risk-management.md` |
| Writing to stakeholders or a client | `references/stakeholder-comms.md` |
| Behind schedule and needs options | Recovery, below |

## Sprint planning

Plan capacity from evidence, not intent.

1. **Compute real capacity.** Team days in the sprint, minus leave, holidays,
   on-call, support rotation, meetings, and interviews. A "2-week sprint" for
   five people is 50 person-days on paper and typically 30–35 in practice. Use
   the honest number; padding hidden inside estimates corrupts the data
   permanently.
2. **Take velocity from the last 3–5 sprints**, not the best one. Use the
   average and the range.
3. **Reserve a buffer.** 15–20% unallocated for interruptions and discovered
   work. A sprint planned to 100% capacity always ends late; the buffer is what
   makes the commitment credible.
4. **Pull only Ready stories.** If it fails the Definition of Ready, it doesn't
   enter the sprint — it becomes a refinement item or a spike.
5. **Check the sequence, not just the total.** Dependencies, one person as a
   bottleneck, all the risky work stacked at the end.
6. **State the sprint goal in one sentence.** If the sprint's stories don't add
   up to a sentence, the sprint has no theme and will get shredded by the first
   interruption.
7. **Name what falls out** if something goes wrong — decided now, calmly,
   rather than in week two.

Output a plan with: goal, committed items with owners, capacity math, buffer,
dependencies, and the pre-agreed cut list.

## Estimation

Estimate for the team's own planning, not as a commitment to anyone outside it.
The moment estimates become promises, they inflate and stop being useful.

Fast reference (details, worked examples, and Monte Carlo forecasting in
`references/estimation-and-velocity.md`):

- **Story points / relative sizing** — default for team backlogs. Compare
  against a known reference story rather than converting to hours.
- **Three-point (PERT)** — `(Optimistic + 4×Likely + Pessimistic) / 6` — for
  individual uncertain items, and it surfaces the spread, which is the useful
  part.
- **Reference class** — "how long did the last four things like this actually
  take?" The single most accurate method available and the least used.
- **Throughput / count-based** — for mature teams: forecast from items
  completed per week, ignore points entirely.

Guardrails worth stating out loud:

- Anything estimated at more than half a sprint should be split before it's
  estimated at all — large estimates are mostly noise.
- Never average away a disagreement. A 3 vs 13 split means two people are
  imagining different work; the conversation is the value, not the number.
- Add integration, review, testing, and deployment into the estimate. Teams
  routinely size the coding and forget the other 40%.
- Don't re-estimate completed work to make velocity look better; you'll lose
  your only real forecasting input.

## Forecasting a date

Never derive a date from a single velocity number. Do this instead:

```
Remaining work ÷ velocity range = sprint range
```

Take the lowest and highest of the last 5 sprints' velocity. Apply both. Report
the range, plus the assumptions that could break it (scope stable, no team
changes, dependency X lands on time).

When someone insists on one date, give the ~85% date — the pessimistic end —
and explain that the earlier one exists but is a coin flip. It costs nothing to
finish early and enormous credibility to finish late.

Watch for the two things that break forecasts: **scope added quietly** (track
scope change explicitly, sprint over sprint) and **carryover** (work counted as
90% done for three sprints running). Count only finished work.

## Timeline and critical path

For anything longer than a couple of sprints:

1. List deliverables, not activities.
2. Map dependencies between them — what genuinely cannot start until what
   finishes.
3. Find the longest dependent chain. That's the critical path; it and only it
   determines the end date.
4. Put slack where the uncertainty is, and put the risky, unknown work as early
   as possible. Discovering a hard problem in week two is a plan change;
   discovering it in the final week is a failure.
5. Mark external dependencies — vendors, other teams, approvals, procurement,
   app store review — with their own lead times. These are the most common
   cause of slip and the least controllable.
6. Identify milestones that are actually decision points, and say what happens
   if the decision is late.

When compressing a timeline, only three levers exist: cut scope, add time, or
reduce quality/increase risk. Adding people to a late project usually makes it
later. Present the levers honestly rather than absorbing pressure silently.

## Recovery: when it's slipping

Don't lead with reassurance. Do this:

1. **Quantify the gap.** Work remaining vs. capacity remaining. Convert to
   days, not vibes.
2. **Diagnose the cause** — scope growth, underestimation, blocked dependency,
   attrition, quality rework. The fix differs entirely by cause, and the wrong
   fix (usually "work harder") burns the team without moving the date.
3. **Build three options** with explicit tradeoffs: reduced scope on the
   original date, full scope on a later date, and a phased split. Recommend
   one.
4. **Escalate with the options attached.** An escalation without options is a
   complaint; with options it's a decision request, which is what stakeholders
   can actually act on.
5. **Rebaseline once, publicly.** Repeated small slips destroy more trust than
   one honest reset.

## Stakeholder communication

Full templates — weekly status, escalation, bad news, kickoff, client update —
are in `references/stakeholder-comms.md`. The rules that matter most:

- **Lead with the answer.** Status, then detail. Executives read the first line
  and the risks.
- **Use a status word with a definition.** Green/amber/red means nothing unless
  the team agrees what triggers each. Amber should mean "at risk without
  intervention," and it should be used before it's obvious.
- **No surprises.** Anyone who will be affected by news should hear it from you
  before it appears in a report.
- **Separate fact from forecast.** "Shipped 8 of 11 stories" is fact; "expect
  to close by the 19th" is forecast. Label them.
- **Every risk gets an owner and a date.** A risk without an owner is a wish.

## Meetings that earn their cost

- **Standup** — blockers and changes to the plan only. Fifteen minutes. If it's
  a status report to the manager, it's a waste; the board already says who's
  doing what.
- **Refinement** — get the top of the backlog to Ready. Ends when the next
  sprint's worth of work is estimable, not when the hour is up.
- **Retro** — pick one or two changes with an owner and a due date. A retro
  that produces a list of feelings and no owned actions will produce the same
  list next month.
- **Kickoff** — goal, scope, roles (RACI), risks, comms cadence, definition of
  done. Written down and circulated the same day.

## Output conventions

- Deliver the artifact — the plan, the register, the update — not a description
  of it.
- Use tables for anything with owners and dates; prose hides accountability.
- State assumptions explicitly at the bottom of any forecast.
- When numbers are guesses, mark them as guesses. A plan built on invented
  velocity is worse than no plan, because people act on it.
- Where the user's own data is missing (velocity, capacity, dates), ask for it
  once, briefly — then produce the artifact with placeholders rather than
  stalling.

## Reference files

- `references/estimation-and-velocity.md` — sizing methods, planning poker,
  velocity math, throughput forecasting, worked examples, estimation traps
- `references/risk-management.md` — risk identification, scoring, register
  format, response strategies, dependency and issue management
- `references/stakeholder-comms.md` — status update, escalation, bad news,
  RACI, meeting formats, tone guidance
- `assets/sprint-plan-template.md`
- `assets/risk-register-template.md`
- `assets/status-update-template.md`
