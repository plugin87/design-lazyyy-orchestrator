# Architecture options and decisions

How to choose a structure, defend it, and record it so it can be overruled by
someone who knows something you don't.

---

## 1. The comparison method

Order matters. Criteria before options, or the criteria get written to fit the
option you already liked.

1. **State the decision in one sentence.** "How is user data stored on the
   device and reconciled with the server?" Not "which database?"
2. **Derive criteria from the non-functional requirements.** Each criterion
   cites the requirement it comes from. A criterion with no requirement behind
   it is a preference — drop it or get it adopted as a requirement.
3. **Weight the criteria.** Usually one or two dominate; say which.
4. **List at least two options you could genuinely defend.** A straw man
   invalidates the whole exercise.
5. **Score, then name the deciding criterion.** The sentence "X wins on
   criterion 3, which we weighted highest because requirement S3 is a
   must-have" is the actual output.
6. **Record the consequences you're accepting**, including the bad ones.
7. **Verify against each must-have requirement individually.**

### Criteria worth considering

| Criterion | Derived from | Ask |
|---|---|---|
| Offline capability | Availability NFR | Which operations still work with no network? |
| Durability | Data-loss NFR | What's lost if the process dies mid-write? |
| Latency | Performance NFR | Does the hot path stay inside budget at stated capacity? |
| Operational cost | Budget constraint | Cost at 100 / 1k / 10k users |
| Migration cost | Maintainability NFR | Can the schema change without user data loss? |
| Team capability | Resourcing constraint | Has anyone here done this before? |
| Portability | Portability NFR | What survives a platform change? |
| Testability | Testability NFR | Can the logic be tested without a UI or a network? |
| Failure blast radius | Reliability NFR | What breaks for users when this component is down? |
| Reversibility | Risk posture | How expensive is it to undo in three months? |

Reversibility deserves more weight than it usually gets. A cheap-to-reverse
decision made quickly beats an expensive-to-reverse decision made carefully.

### Scoring format

Comparative, not absolute. Numbers with no scale are decoration.

| Criterion | Weight | Option A: local-only | Option B: local-first + sync | Option C: server-only |
|---|---|---|---|---|
| Offline capability (S3, must) | High | Full | Full | **Fails** |
| Multi-device | Medium | None | Full | Full |
| Data durability on device loss | High | **None** | Full | Full |
| Build effort | High | 38 h | 385 h | 210 h |
| Operating cost at 1k users | Medium | 0 | ~$40/mo | ~$60/mo |
| Reversibility | Medium | Easy → B later | Hard | Hard |

**Decision:** B. Deciding criterion: S3 is a must-have and C fails it outright;
A satisfies S3 but fails the durability requirement, which the requirements
mark as zero-tolerance. B costs ~10× A in effort — that cost is the real
subject of the decision and should be escalated, not absorbed.

That last sentence is the analyst doing their job: the schedule impact of a
technical decision belongs in front of whoever owns the schedule.

---

## 2. Architecture Decision Records

One decision per record. Immutable once accepted — a changed mind produces a
new ADR that supersedes the old one, and the old one stays readable. The
history of rejected options is the most valuable part of the file six months
later.

See `assets/adr-template.md`. Minimum contents: context, decision, options
considered with why each was rejected, consequences (good and bad), and
verification against the must-have requirements.

Write the ADR when the decision is made, not at the end of the project. An ADR
written retroactively records the justification, not the reasoning, and those
are different things.

---

## 3. Local-first and sync

The dominant architecture question in any system with an offline requirement.

### The three shapes

| Shape | Reads | Writes | Offline | Cost |
|---|---|---|---|---|
| Server-only | Network | Network | Broken | Server + bandwidth |
| Local-only | Local | Local | Full | None; data dies with the device |
| Local-first + sync | Local | Local, then replicate | Full | Server + sync complexity |

Local-first is the only shape that satisfies "fully functional offline"
together with "data survives device loss." It is also several times the work of
either alternative — do not let that cost stay implicit.

### What local-first actually requires

- **Every write commits locally first** and the UI reflects it immediately. The
  network is a background concern that is allowed to fail.
- **An outbox** of unsynced changes, durable across app restarts.
- **Client-generatable IDs** (UUIDs), because a disconnected client must create
  records.
- **Idempotent server writes**, keyed by the client-generated ID, because
  retries are guaranteed.
- **A conflict rule** — see below.
- **Sync failure is invisible to the user** unless it persists long enough to
  matter. A red banner on every subway ride trains users to ignore banners.

### Conflict resolution — the rule *is* the design

Transport is plumbing. The conflict rule is the architecture. Pick per entity,
not once globally.

| Strategy | How it works | Good for | Cost of getting it wrong |
|---|---|---|---|
| Last-write-wins by timestamp | Highest `updated_at` wins | Single-user, low-contention records | Silent loss; device clocks lie |
| Last-write-wins by server receipt | Server arrival order decides | Same, without trusting client clocks | Silent loss; offline edits lose to later online ones |
| Per-field merge | Merge field by field | Records where fields are independent | Incoherent combined state |
| Append-only log | Never update; derive state from events | Execution/history records | Storage growth; needs compaction |
| CRDT | Structurally convergent types | Collaborative text, counters, sets | Library and payload complexity |
| Explicit user resolution | Ask the user | Rare, high-value conflicts | Terrible if it fires often |

Practical default for a single-user multi-device product: **append-only for
event/execution data** (two devices recording completions merge naturally — a
union, no conflict) and **last-write-wins on server receipt for definition
data** (plans, settings — conflicts are rare and the user can see and fix the
result).

Whatever you choose, write the losing case down explicitly: "if the same item
is marked complete on two devices while both are offline, the union applies and
the earlier timestamp is retained." That sentence is testable. "We use LWW" is
not.

### Sync failure modes to specify

Each needs a defined behaviour, not a shrug:

- Server unreachable (expected, frequent) → queue, retry with backoff, no UI change
- Server returns 5xx → same, but bound the retry count and log
- Server returns 4xx (client is wrong) → do not retry blindly; quarantine the item and surface it
- Auth token expired → refresh; if refresh fails, keep working locally read/write and retry later
- Clock skew between device and server → prefer server time for ordering
- Payload too large after a long offline period → chunk; specify the chunk size
- Partial sync interrupted → resumable; never leave a half-applied batch
- Local storage full → stop syncing *in*, keep accepting writes if possible, tell the user with a specific action

---

## 4. Verifying an architecture against must-haves

Do this one requirement at a time, in writing. Group verification hides
failures.

```
S1 — Shows today's items on launch
     Local read from indexed store; no network on the path. PASS

S2 — Records completion status
     Local write, optimistic UI, outbox entry. PASS

S3 — Fully functional with no network
     All v1 capabilities read and write locally. Sync is background-only and
     failure is silent. Entitlement uses last known local state (assumption A3).
     PASS, conditional on A3 being confirmed

11.1.1 — Launch to list ≤ 2s at p95
     Single indexed lookup over ~27k rows; no network. Expected well inside
     budget; must be measured on a real device before the claim stands. PASS,
     unverified — needs measurement
```

"PASS, unverified" is an honest and useful state. "PASS" on something you
haven't measured is not.

---

## 5. Server-side sizing and cost

When a server enters scope, the requirements rarely say how big. Produce the
numbers rather than waiting to be asked.

**Model per user, then multiply.** From the capacity work in
`data-modeling.md`: ~44k rows and ~9 MB per user per 3 years, plus sync traffic
of roughly one small batch per active day.

| Users | Storage | Requests/day (est.) | Typical monthly cost band |
|---|---|---|---|
| 100 | ~1 GB | ~1k | Free tier of most managed platforms |
| 1,000 | ~9 GB | ~10k | Small managed database + small compute |
| 10,000 | ~90 GB | ~100k | Managed database with replicas + autoscaling compute |

State the assumptions under the table (retention, active-user ratio, sync
frequency, region) and mark the whole thing as an estimate for budgeting, not a
quote. Then say which cost grows fastest — usually storage, because it never
goes down, while compute follows usage.

**Also specify, because these are what actually cause incidents:**

- Write-failure handling: what the client does when the server rejects a write
- Storage-full behaviour on both device and server
- Insufficient-permission handling: fail closed, log, surface a real message
- Backup and restore: what's backed up, how often, tested how, and the recovery
  point objective — an untested backup is a belief, not a control
- Monitoring: what's alerted on, and who receives it
- Deployment and rollback: how a bad release is reversed, and whether the
  schema change is compatible in both directions

---

## 6. Boundaries and where logic lives

- **Business logic sits in a layer with no platform dependency.** Date and
  cycle calculation, entitlement rules, aggregation — these should be testable
  with no UI and no network. This is a stated design constraint whenever
  portability or testability appears in the NFRs.
- **The storage layer is an interface, not a library call sprinkled through the
  code.** It changes at least once; make that change local.
- **Platform-specific code is a thin shell.** Whatever must be rewritten per
  platform should be small enough to rewrite.
- **Third parties get an adapter.** Never let a vendor's data shapes propagate
  into the domain model — vendors get replaced, and the model shouldn't care.

---

## 7. Decision hygiene

- Record the decision when it's made, with the date and who made it.
- Distinguish "decided by the owner" from "proposed by the analyst pending
  confirmation." Proposals that get filed as decisions are how teams end up
  building something nobody chose.
- When a decision reverses an earlier one, say so explicitly and sweep the
  document set for statements that still assume the old world.
- A decision that changes effort materially goes to whoever owns the schedule
  the same day. Not in the final report.
