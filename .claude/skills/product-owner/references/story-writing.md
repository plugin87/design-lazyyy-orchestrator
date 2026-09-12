# Story Writing and Slicing

Contents:
1. Vertical slicing — why it matters
2. Nine ways to split a story that's too big
3. Worked before/after examples
4. Epic structure
5. Spikes
6. Story smells

---

## 1. Vertical slicing

A good story cuts through every layer — UI, logic, data — and delivers
something a real user could use, even if narrow. A bad story cuts across one
layer and delivers nothing until its siblings arrive.

Horizontal (avoid): "Build the orders API" / "Build the orders screen" /
"Add the orders table."

Vertical (prefer): "A customer can see their last order on the account page."
Later: "...can see all orders from the past year." Later: "...can filter by
date."

The test: if this story shipped alone tonight, could anyone do something new
tomorrow? If no, it's a task, not a story. Tasks are fine — they just live
inside a story rather than beside it.

---

## 2. Nine ways to split a story that's too big

Try these in order; the first two solve most cases.

**1. By workflow step.** Take the end-to-end flow and ship the steps that
matter first. Checkout → ship "pay with saved card" before "add new card,"
"apply promo," "gift wrap."

**2. By happy path vs. edge cases.** Story one handles the case that covers 80%
of traffic. Story two handles expired sessions, partial failures, retries. Only
do this when the edge case genuinely can wait — not for data loss or security
paths.

**3. By user role.** Ship for the admin first, then the standard user, then the
anonymous visitor. Or the reverse — whoever has the sharper pain.

**4. By data variation.** One currency, then many. One file type, then all.
English, then localized.

**5. By interface.** Web first, then mobile app, then email. Or: get it working
via an internal tool before building the customer-facing UI.

**6. By CRUD operation.** Create and read now; update and delete next. Frequently
the read alone is the valuable half.

**7. By manual-then-automated.** Ship the outcome with a human in the loop
(ops team runs a script), then automate. Real value, a fraction of the build,
and you learn whether it's worth automating at all.

**8. By performance tier.** Make it correct first, fast second — as its own
story with a stated budget ("p95 under 400ms"), not as a vague follow-up.

**9. By rules complexity.** Ship the simple pricing rule; add tiered discounts,
regional tax, and promo stacking as separate stories.

If none of these apply, the story is probably an epic. Write it as one.

---

## 3. Worked examples

**Before:** "As a user, I want a better dashboard."

Problems: no specific user, no capability, no outcome, unsizeable, untestable.

**After:**
> As a warehouse supervisor starting a shift, I want the dashboard to open on
> today's unfulfilled orders sorted by promised ship time, so that I can assign
> pickers without building the list by hand.

Acceptance criteria:
```
Given a supervisor with at least one unfulfilled order for today
When they open the dashboard
Then unfulfilled orders appear first, sorted by promised ship time ascending

Given a supervisor with no unfulfilled orders for today
When they open the dashboard
Then an empty state explains that all of today's orders are fulfilled and
links to tomorrow's queue

Given more than 200 unfulfilled orders
When the dashboard loads
Then the first 50 render within 1s at p95 and the rest paginate
```

---

**Before:** "Add SSO."

That's an epic. Split by identity provider and by workflow step:

1. An existing employee can sign in with the company Google account and land on
   the same home screen as a password login.
2. A new employee's account is created on first SSO sign-in with the default
   role.
3. An admin can force SSO-only for the org, disabling password login.
4. SAML support for enterprise customers (separate epic — different buyer,
   different testing surface).

Note story 1 delivers real value alone: people stop typing passwords. Story 3
is the one legal actually wanted; making it explicit surfaces that early.

---

**Before:** "Improve checkout conversion."

That's an outcome, not a story — which is good, keep it as the epic's goal
statement, then generate candidate stories against it and prioritize. Don't
convert an outcome into a single story; you'll lose the ability to cut.

---

## 4. Epic structure

An epic needs only:

- **Goal** — the measurable outcome, one sentence
- **Why now** — what changed that makes this the moment
- **Users affected** — and roughly how many
- **Stories** — ordered, each one shippable
- **Out of scope** — the things people will otherwise assume are included
- **Open questions** — with an owner beside each

Everything else is decoration. If the epic needs more than a page, it's a PRD.

---

## 5. Spikes

A spike is a timeboxed research task that produces a decision, not code. Use
one when the team can't estimate a story because of genuine unknowns.

Rules that keep spikes from becoming projects:

- State the question in one sentence, and the timebox in hours or days.
- Name the artifact it produces: a recommendation, a benchmark number, a
  throwaway prototype.
- The spike's output must unblock a specific story — reference it by name.
- Never let a spike carry story points as if it were delivery; it's an
  investment in reducing variance.

---

## 6. Story smells

- Contains the word "and" in the title — usually two stories.
- Uses "support", "handle", or "manage" — vague verbs hiding scope.
- Has acceptance criteria that reference a specific component, library, or
  table name.
- Nobody can name who complains when it's missing.
- Estimate is more than half a sprint — split it.
- Has been rewritten three times and still isn't clear — the underlying problem
  isn't understood. Go back to discovery instead of rewording.
