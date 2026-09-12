# Design handback checklist

Run before delivering a design back to whoever handed you the requirements.
Anything unticked is either finished first or declared as a known gap — not
left for the reviewer to discover.

| Item | Value |
|---|---|
| Deliverable | [SRS-XXX-001 rev NN and attachments] |
| Against | [handoff document code and revision] |
| Date | |

---

## 1. Intake integrity

- [ ] Every source document listed with the revision actually used
- [ ] Revisions match what the handoff specified; any mismatch was confirmed before work started
- [ ] Every conflict found in the source material is reported, none silently resolved
- [ ] Superseded decisions were swept for — statements still assuming the old world are listed
- [ ] Blocking open questions each name the deliverable they block and the mechanism

## 2. Traceability

- [ ] Every in-scope requirement traces to at least one design element
- [ ] Every design element traces to at least one requirement
- [ ] Every acceptance criterion has at least one test case
- [ ] Every test case traces to a requirement, or is listed as a finding
- [ ] Upstream requirement IDs used unchanged — no local renumbering
- [ ] Coverage stated as a number, with the missing items named

## 3. Data model

- [ ] Every entity, attribute, relationship, and constraint specified
- [ ] Definition and execution separated where the user can edit both
- [ ] Keys opaque and stable; client-generatable where records are created offline
- [ ] Delete rules stated per relationship
- [ ] Schema version and migration path present, tested from all prior shipped versions
- [ ] Temporal rules written out, including the day-boundary rule
- [ ] Capacity computed in rows and bytes against the stated budget
- [ ] Every deferred requirement checked: the model does not block it

## 4. Architecture

- [ ] Every structural decision has a recorded alternative and a stated reason
- [ ] Criteria derived from non-functional requirements, not preference
- [ ] Each must-have requirement verified individually, not as a group
- [ ] Claims marked "PASS, unverified" name the measurement still owed
- [ ] Failure behaviour specified for every external dependency
- [ ] Conflict rule stated per entity, with the losing case written out
- [ ] Operating cost estimated at the stated user tiers, with assumptions

## 5. Behaviour and interfaces

- [ ] Every state named in the requirements appears in the screen-state grid
- [ ] Every use case has alternate flows, not only the main flow
- [ ] Every entity with a status has a state machine with no trap states
- [ ] Error catalogue complete — no error resolves to "something went wrong"
- [ ] Every boundary has a contract including the timeout case
- [ ] Idempotency specified for every write a client can retry
- [ ] Business rules listed separately and testable without a UI

## 6. Tests

- [ ] Every acceptance criterion converted, or listed as blocked with the reason
- [ ] At least one negative case per requirement
- [ ] Non-functional requirements have test cases, not just prose
- [ ] Date, time, and recurrence edge cases covered against the catalogue
- [ ] Offline, sync, migration, and capacity data sets defined
- [ ] Expected results observable — no result two testers could disagree about

## 7. Estimate

- [ ] Re-estimated from the design that exists, not from judgement
- [ ] Each change explained by the design element that caused it
- [ ] Items whose effort moved materially were raised when discovered, not saved for this document
- [ ] Uncertainty stated where the design is still open

## 8. Honesty

- [ ] Every assumption listed with what breaks if it is wrong, and an owner
- [ ] Every judgement call the requester did not ask for is stated in one line so it can be overruled
- [ ] Nothing invented to fill a gap — gaps appear as gaps
- [ ] No upstream document was edited; changes discovered during design were raised as change requests
- [ ] Work that could not be completed is named, with the reason, rather than quietly scoped out

## 9. Document control (where the receiving side uses one)

- [ ] Document code, revision number, and effective date present
- [ ] Revision history records what changed, why, and the impact on scope, effort, and metrics
- [ ] Requirement ID scheme matches the primary document
- [ ] Output formats produced as the receiving side requires
