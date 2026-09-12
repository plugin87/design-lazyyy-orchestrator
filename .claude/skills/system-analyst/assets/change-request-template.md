# Change request — [document set]

| รายการ | รายละเอียด |
|---|---|
| รหัสเอกสาร | CR-XXX-001 |
| ฉบับแก้ไขครั้งที่ | 00 |
| วันที่มีผลบังคับใช้ | YYYY-MM-DD |
| สถานะ | ร่าง / รอทบทวน / อนุมัติแล้ว |
| เอกสารอ้างอิง | [PRD-XXX-001 rev NN] |
| ผู้จัดทำ | [ผู้พบข้อขัดแย้ง] |
| Origin | [which findings / which checklist item this closes] |
| Request count | [N] |
| Requested by | [role] |

---

## 1. Why this is a request, not an edit

State the clause that forbids you from editing upstream documents directly, and
commit to giving pasteable text so the controller doesn't have to rewrite you.

> Discoveries made during design that change a requirement must be handled by
> issuing a revision of the affected document. The recipient must not amend the
> requirement unilaterally.
> — [source clause]

## 2. Request summary

Sort so the reader sees severity and scope impact without opening the detail.

| # | Document | Clause | Closes finding | Severity | Changes scope/effort/metrics? |
|---|---|---|---|---|---|
| CR-01 | | | | High / Medium / Low | No |
| CR-02 | | | | | **Yes — see §N** |

Call out separately which requests need impact assessment before approval.

---

## 3. Requests

Repeat per request. Group by severity, not by document.

### CR-NN · [one-line title]

| Item | Value |
|---|---|
| Document | [code, clause] |
| Closes | [finding ID] |
| Severity | |

**Evidence of the problem**

Quote the conflicting statements with their source clauses, or show the
arithmetic. Do not paraphrase — a paraphrase invites an argument about whether
the conflict is real.

| Statement | Source |
|---|---|
| | |

**Proposed change**

| | Text |
|---|---|
| **Current** | [exact current wording] |
| **Proposed** | [exact replacement wording] |

For new clauses, give the full text as a block quote ready to paste.

**Alternative** — where a different resolution is legitimate, state it and its
consequence. You propose; the controller decides.

**Impact** — on scope, effort, and metrics. "None" is a valid answer and should
be stated explicitly, not left blank.

---

## 4. Attachment — [supporting work]

Where a request says "break this down" or "add the missing detail", attaching a
proposed draft turns an instruction into something actionable. Mark it clearly
as a proposal, not a verified figure.

Where a bottom-up draft disagrees with a top-down figure, **report the gap
rather than forcing a match** — the gap is information about whether work is
missing or padding is hidden.

---

## 5. Combined impact and recommended order

### 5.1 Combined impact

| Dimension | Effect |
|---|---|
| Scope | |
| Effort | |
| Metrics | |
| Schedule | |

### 5.2 Recommended order

Order by what unblocks the most for the least time. Make the cheap high-leverage
items visibly first.

| # | Request | Time | Why this position |
|---|---|---|---|
| 1 | | | |

### 5.3 What this request set does not cover

| Item | Why not |
|---|---|
| Decisions awaiting an answer | These are decisions, not document edits — see [open questions register] |
| Assumptions awaiting confirmation | Same |
| Work blocked by an external dependency | Name the dependency and the unblock condition |

## 6. Revision history

| Rev | Date | Clauses | Substance and reason | Author | Approver |
|---|---|---|---|---|---|
| 00 | | All | First issue | | |
