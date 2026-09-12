# Requirements analysis

Everything between receiving a requirements document and being allowed to
design against it.

---

## 1. Handoff intake

A handoff is not a pile of documents; it's a claim that the documents are
consistent, current, and sufficient. Verify the claim before you rely on it.

### Intake checklist

- [ ] **Document register** — every document received, with its code, revision
      number, and effective date recorded in your own notes
- [ ] **Revision match** — the revision you received matches the revision the
      handoff says you should have. A mismatch stops work until confirmed
- [ ] **Primary document identified** — which one wins when two disagree
- [ ] **ID scheme understood** — where requirement IDs are defined, and which
      documents must mirror them
- [ ] **Scope of this pass** — which requirements are in, out, and deferred
- [ ] **Open issues extracted** — every "TBD", "to be decided", "not yet
      determined" pulled into one list
- [ ] **Decisions extracted** — every recorded decision, especially recent ones
      that reversed an earlier decision
- [ ] **Constraints acknowledged** — capacity, budget, team size, legal,
      platform, deadline
- [ ] **Notification path agreed** — who tells you when a revision lands that
      changes your scope

### Reversed decisions are the highest-risk item in any handoff

When a decision log shows decision 15.10 reversing decision 15.8, everything
written between them may still reflect the old world. Search the whole document
set for statements consistent with the *superseded* decision — they are almost
always still there, and they read as authoritative. Report them as defects
against the document, don't just work around them.

### Output of intake: three lists

**Decided** — you may design against these.

**Open, not blocking** — design proceeds; record the assumption you used and
what changes if the answer differs.

**Open and blocking** — for each, name the deliverable it blocks and the
mechanism. Weak: "need clarity on accounts." Strong: "whether an account is
mandatory at first launch decides whether data keys to the device or the user,
which is the primary key of every table — blocks the entire data model."

A blocking item that blocks only one deliverable does not block the rest. Stage
the work and say so.

---

## 2. Conflict taxonomy

Requirements conflict in predictable ways. Hunt these specifically.

| # | Conflict | Typical phrasing | Why it's fatal if missed |
|---|---|---|---|
| 1 | Offline vs server dependency | "fully functional offline" + "checks entitlement on launch" | Decides the entire storage architecture |
| 2 | Unbounded vs performance | "unlimited items" + "loads in under 2s at p95" | Unbounded is untestable; the budget is the real requirement |
| 3 | Retention vs deletion | "never delete user data" + "purge after expiry" | Legal exposure in both directions |
| 4 | Instant vs durable | "appears immediately" + "confirmed saved before displayed" | Decides optimistic vs pessimistic write path |
| 5 | Device-bound vs multi-device | data tied to install + sync across devices | Changes every primary key |
| 6 | Privacy vs analytics | sensitive attribute collected to compute a metric | Consent, retention, and deletion obligations |
| 7 | Single-user vs sharing | "no multi-user" + "share a plan with a friend" | Ownership and authorization model |
| 8 | Anonymous use vs personalization | no account required + per-user recommendations | Identity model |
| 9 | Stated priority vs dependency order | a "could-have" that a "must-have" needs | Sequencing is wrong, not the priority |
| 10 | Metric vs capability | a success metric nothing in scope can move | The product can't prove it worked |

### How to report a conflict

Report the pair, not the symptom. Then propose, but do not decide.

```
Conflict — REQ S3 (offline) vs REQ P2 (entitlement check)

S3 requires every v1 capability to work with no network.
P2.7 requires entitlement to be verified before write access.

These are simultaneously satisfiable only if entitlement state is cached
locally and treated as authoritative until the next successful check.

Impact if unresolved: the write path cannot be designed; blocks the data
layer and 6 test cases.

Options: (a) cache entitlement with a grace window — needs a window length;
(b) drop the offline guarantee for write operations — contradicts S3, which
is a must-have.

Recommendation: (a). Needs a decision on window length from the product owner.
```

---

## 3. Converting adjectives into requirements

An adjective is a requirement that hasn't been written yet. Convert every one.

| Adjective | Ask | Becomes |
|---|---|---|
| Fast | Which operation, measured where, at what percentile, on what device? | "Launch to list rendered ≤ 2s at p95 on a mid-tier device 3 years old" |
| Unlimited | What volume must perform to budget? What happens past it? | Capacity table + "degrades gradually, never rejects a write" |
| Secure | Against whom, protecting what, to what standard? | Named threats + controls + a standard to audit against |
| Reliable | How much loss is acceptable? How is it measured? | "Zero user-data loss; crash rate < 1 per 1,000 sessions" |
| Accessible | Which standard, which level, verified how? | "WCAG 2.1 AA, mobile-applicable criteria, verified by screen-reader pass" |
| Scalable | To what number, by when, at what cost? | Cost and latency at 100 / 1k / 10k users |
| Intuitive | What can a first-time user do unaided, in how long? | Task-completion criterion, testable |
| Real-time | What latency budget? What happens when it's exceeded? | A number and a fallback |

Two rules:

- **Never guess the number.** Propose one, mark it a proposal, and get it
  confirmed. A proposed number gets corrected; a silent guess gets built.
- **A requirement with no measurement method is not testable.** Write how it
  will be measured next to the number, or it will never be checked.

---

## 4. Non-functional requirements: extract, don't inherit

NFRs arrive scattered — some in a performance section, most buried inside
functional requirements and design notes. Sweep the whole document set and
build one table, because NFRs are what actually decides the architecture.

Categories to sweep for:

| Category | Look for |
|---|---|
| Performance | Latency budgets, percentiles, throughput, cold vs warm start |
| Capacity | Row counts, item limits, history depth, storage per user |
| Availability | Uptime target, offline behaviour, degraded modes |
| Durability | Acceptable data loss (usually zero), backup, recovery point |
| Security | Auth model, sensitive data classes, transport, at-rest |
| Privacy / legal | Consent, deletion rights, export rights, jurisdiction |
| Accessibility | Standard and level, screen reader, text scaling, touch targets |
| Localisation | Languages now, languages later, no hardcoded strings |
| Compatibility | OS versions, browsers, screen sizes, orientation |
| Maintainability | Schema migration, upgrade paths, logging |
| Portability | What must survive a platform change |
| Testability | What must be testable without a UI |
| Observability | Events required to compute each success metric |

The observability row is the one teams skip and then discover, post-launch,
that the success metric cannot be computed. Check each stated metric against
the event list and report any metric with no supporting event as a gap.

---

## 5. Requirement quality checks

Run each requirement through these. Report failures to the author.

- **Atomic** — one requirement per statement. "And" in a requirement usually
  means two requirements and one of them has no test.
- **Testable** — you can describe the test that fails when it's violated.
- **Unambiguous** — no adjective, no "etc.", no "and so on". "And other
  things" is unbounded scope wearing a small word.
- **Necessary** — traces to a stated user problem or a constraint.
- **Implementation-free** — states the observable outcome, not the mechanism.
  "A cached response is returned" is a design decision smuggled into a
  requirement; "the list renders within 2s with no network" is the requirement.
- **Consistent** — doesn't contradict another requirement (section 2).
- **Feasible** — buildable within the stated constraints. If not, say so with
  the arithmetic.
- **Traceable** — has a stable ID used identically everywhere.

---

## 6. Elicitation: questions that produce facts

When a requirement is thin and the author is available, ask about behaviour
that already happened, not intentions.

**About the current workaround** — there is always one, and it's the real spec:
- Walk me through the last time you did this. What did you actually open?
- What did you have to remember that the tool didn't remember for you?
- What has gone wrong doing it this way? How did you find out?

**About boundaries** — where the model breaks:
- What's the largest one of these you've ever had?
- What happens on the first day? The day after the last day?
- Has anyone ever needed two of these at once?
- What would you do if this were wrong — could you fix it, or would it be stuck?

**About failure** — what the design must survive:
- What must never happen, even if everything else breaks?
- If the network is down for a week, what still needs to work?
- Who notices first when this breaks, and how?

**About the edges of scope**:
- What did you deliberately leave out, and why?
- What might get asked for in six months that we shouldn't block now?

That last question is what separates "extensible" from a slogan: it produces
the specific future requirement the schema must not prevent.

---

## 7. Assumption register

Every gap you designed past becomes an assumption with an owner and an impact.

| ID | Assumption | Because | If wrong | Owner | By when |
|---|---|---|---|---|---|
| A1 | Data keys to the device, not an account | Account requirement undecided | Every table's primary key changes; ~2 weeks rework | Product owner | Before data layer starts |
| A2 | History depth capped at 3 years | Stated in capacity table | Query and index design changes | Product owner | Confirmed |

Rules: an assumption with no "if wrong" is not an assumption, it's a guess. An
assumption whose "if wrong" is expensive gets escalated rather than filed.
