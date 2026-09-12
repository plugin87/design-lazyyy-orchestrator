# Working inside a controlled document system

Some handoffs arrive as a numbered, revision-controlled document set — an ISO-style
QMS, a regulated environment, a government or enterprise process. The analysis
work is the same; what changes is that **the documents are themselves under
control**, and violating that control causes more damage than a design mistake.

If the handoff has document codes, revision numbers, effective dates, and a
signature block, you are in one of these systems. Read this before writing
anything back.

---

## 1. The rules that are not negotiable

| # | Rule | Why |
|---|---|---|
| 1 | **Never edit an upstream document.** Discoveries go back as change requests. | Two divergent copies of a requirement is a defect factory. The system exists to guarantee one authoritative version. |
| 2 | **Use the upstream requirement IDs verbatim.** No renumbering, no "cleaning up". | The whole value of an ID is that two documents written by two people mean the same thing by it. |
| 3 | **Check the revision you received against the revision you were told to expect.** | A design built against rev 07 and reviewed against rev 09 wastes everyone's time. |
| 4 | **Every document you write back gets the same control header** — code, revision, effective date, status, revision history with reasons and impact. | Your output enters the same system; an uncontrolled document in a controlled set is the weakest link. |
| 5 | **Your documents are not authoritative over requirements.** Say so in the header. | See section 4. |

---

## 2. Reading a controlled set for defects

A revision-controlled set accumulates a specific kind of damage: **statements
that were true at revision N and were never updated at revision N+1.** Hunt for
these deliberately — they are the highest-yield findings in this environment.

### 2.1 The superseded-decision sweep

When the decision log shows a decision reversing an earlier one, **search the
whole set for text consistent with the superseded decision.** It is almost
always still there, and it still reads as authoritative.

Worked example: a decision log reverses "no device sync" to "sync included in
v1". Three separate defects survived:

- A priority table still listed the account system — which sync requires — as
  optional and deferred to the last phase
- A data section still said "no automatic backup; warn the user their data dies
  with the device" — untrue once sync exists
- A note on the offline requirement still cited the old out-of-scope clause,
  and cited the wrong clause number as well

None of these were caught by the authors. All three were caught by reading the
decision log first, then sweeping.

### 2.2 The partial-revision sweep

When a revision adds or restructures content, check whether **every part of the
document was updated, or only the summary.** Compare totals.

Worked example: a work-breakdown document was revised from 11 work packages
totalling 314 hours to 13 packages totalling 766 hours. The summary table was
updated; the detail sections were not. Consequences:

- The detail sections still summed to exactly 314 — the old figure
- Package numbers 3.10 and 3.11 pointed at **completely different work** in the
  table than in the detail
- 45% of the project's effort had no task breakdown at all, in a document whose
  own rules required breaking down anything over 8 hours

The check that found it was arithmetic: sum the parts, compare to the stated
total. Do this on every document that has both.

### 2.3 The dangling-reference sweep

Documents in a set point at each other constantly. Verify the targets exist.

Worked example: a product requirements document said technical architecture
"appears in the reference documents listed in section 3" — and section 3 listed
no architecture document. The promise had been dangling since before the
analyst arrived.

Check: every "see document X", every "per clause Y", every "listed in section
Z". Cross-document references break silently.

### 2.4 The counted-things sweep

Any number stated in prose ("all 31 acceptance criteria", "the 6 screen
states", "13 work packages") is a claim you can verify by counting. Do it.

Worked example: a handoff document stated 31 acceptance criteria in two places,
one of them an acceptance criterion for the delivery itself. The source
document contained 33. Delivering 33 risks "out of scope"; delivering 31 fails
completeness. Neither is acceptable, and the discrepancy would only have
surfaced at acceptance.

### 2.5 The intent-versus-scope sweep

Revision histories record *why* a change was made. Compare that stated intent
against what the scope documents actually ask for.

Worked example: a revision note said requirements were added "in order to
produce the software requirements specification and system design" — but the
handoff document defining the analyst's scope never asked for either. The owner
expected a document nobody had commissioned.

---

## 3. Reporting a finding

Never fix it. Report it in a form the document controller can act on without
re-deriving anything.

```
ข้อขัดแย้ง C-07 · [one-line title]

ระดับ  สูง / ปานกลาง / ต่ำ · [what it blocks, in hours or deliverables]

[Table of the conflicting statements, each with its source clause]

[Evidence — the arithmetic, the count, the quoted text]

ผลที่ตามมา  [what breaks if unresolved, concretely]

ข้อเสนอ  [proposed resolution — but you do not decide]
```

Two disciplines:

- **Quote the source text exactly.** A paraphrase invites an argument about
  whether the conflict is real.
- **Give the severity in terms of what it blocks**, not a bare adjective. "สูง"
  means nothing; "blocks 347 hours across two work packages" gets answered.

---

## 4. Writing back into the set

### 4.1 Declare your document's authority level

Every document you write back must state where it sits. Design documents are
authoritative for *design*; they are never authoritative for *requirements*.

Put this in the document, not in an email:

```
เอกสารฉบับนี้เป็นฉบับรวบรวม มิใช่ต้นฉบับของข้อกำหนดใด

- เมื่อขัดแย้งกับ [เอกสารต้นฉบับ] ให้ถือตามเอกสารต้นฉบับ
- ห้ามแก้ไขข้อกำหนดที่เอกสารฉบับนี้เท่านั้น
- เมื่อเอกสารต้นฉบับออกฉบับแก้ไขใหม่ ต้องทบทวนเอกสารฉบับนี้ในคราวเดียวกัน
- เอกสารฉบับนี้ไม่สร้างข้อกำหนดใหม่ · ข้อความที่เป็นการตัดสินใจของผู้จัดทำ
  ระบุไว้เป็นสมมติฐาน มิใช่ข้อกำหนด
```

Without this, a compiled document diverges from its sources within months and
nobody knows which is right.

### 4.2 The revision history is a real artifact

Most templates treat it as a formality. In a controlled set it is the only
record of *why*. Each row needs: what changed, why, and **the impact on scope,
effort, and metrics** — that last column is what makes the history usable for
planning rather than archaeology.

### 4.3 Consolidation must transform, not copy

If you are asked for a document whose content already exists elsewhere, do not
restate it. Compile and point:

- **State each requirement once, in one line**, with a back-reference — not the
  full text
- **Add what does not exist anywhere**: cross-document traceability, a
  consolidated open-issues register, a checklist against the acceptance criteria
- **Transform where you can**: non-functional requirements scattered across six
  sections become one table of measurable design constraints with the test that
  verifies each. That is not duplication; it is the analysis.

---

## 5. The change request

When findings accumulate, batch them into one change request rather than a
stream of emails. Give the document controller text they can paste.

See `assets/change-request-template.md`. The parts that matter:

- **เดิม / ใหม่ word-for-word.** If they have to rewrite your prose, they won't.
- **Group by severity**, and mark which requests change scope, effort, or
  metrics — those need impact assessment before approval.
- **A recommended order** with time estimates. Five requests that take under
  eight hours total and unblock hundreds of hours should be visibly first.
- **State what the request set does not cover** — decisions, assumptions
  awaiting confirmation, work blocked by external dependencies.

---

## 6. What the process itself will be missing

Controlled sets are strong on document integrity and weak on the same few
things every time. Check for these; they are usually absent and always matter.

| Gap | Why it happens | What to ask for |
|---|---|---|
| No agreed review cadence | The handoff has a field for it, left as "to be agreed" | A fixed interval. Without it, nothing catches a wrong design direction until acceptance |
| Unsigned handoff | Signature blocks left blank because work started anyway | Signatures. Until then your deliverables have no status in the system |
| No entry document | Each deliverable is controlled; the *set* is not | A covering document: index, cross-set traceability, consolidated registers |
| Pre-agreed scope-reduction list | A risk register says "reduce scope per the agreed list" and no such list exists | The list, written while calm |
| Deliverables never registered | Your documents exist but aren't in the master reference table | A change request adding them |

---

## 7. Checklist before handing back

- [ ] Every document has code, revision, effective date, status, and revision history
- [ ] Revision history states impact on scope, effort, and metrics
- [ ] Authority level declared — which document wins on conflict
- [ ] Upstream requirement IDs used unchanged
- [ ] Every finding reported as a change request, none fixed unilaterally
- [ ] Every counted claim in your own documents verified by counting
- [ ] Sums checked against stated totals in your own documents
- [ ] Every cross-reference points at something that exists
- [ ] Assumptions listed as assumptions, with owner and consequence-if-wrong
- [ ] Work that could not be completed named, with the reason and the unblock condition
