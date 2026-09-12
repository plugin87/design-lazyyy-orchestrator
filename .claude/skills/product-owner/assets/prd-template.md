# [Product / Feature Name]

| รายการ | รายละเอียด |
|---|---|
| รหัสเอกสาร | PRD-XXX-001 |
| ฉบับแก้ไขครั้งที่ | 00 |
| วันที่มีผลบังคับใช้ | YYYY-MM-DD |
| สถานะ | ร่าง / รอทบทวน / อนุมัติแล้ว |
| เอกสารอ้างอิง | — |
| ผู้จัดทำ | [ชื่อ] |

**Engineering:** [name] · **Design:** [name] · **Sign-off:** [name]

---

## 1. Summary

Two or three sentences. What we're building, for whom, and the outcome it
produces. Someone should be able to read only this and know whether to keep
reading.

## 2. Problem

Who has the problem, how often it occurs, and what they do today instead.
Include evidence: support ticket volume, session data, interview quotes,
sales-blocked deals. If there's no evidence, say so — an assumption labelled as
an assumption is fine; an assumption dressed as a fact is not.

## 3. Why now

What changed. A deadline, a competitor, a platform deprecation, a shift in the
data. If nothing changed, this belongs lower in the backlog.

## 4. Goals and success metrics

| Metric | Today | Target | Measured by | Owner |
|---|---|---|---|---|
| | | | | |

Include at least one **guardrail metric** — something that must not get worse
(conversion, latency, support volume, churn).

## 5. Non-goals

What this explicitly does not do. Be generous here; it prevents scope fights
later.

## 6. Users and use cases

Primary user, secondary users, and anyone affected downstream (support, ops,
finance). For each: what they need to accomplish and how often.

## 7. Requirements

Ordered by priority. Reference stories rather than duplicating them.

**Must**
- …

**Should**
- …

**Could**
- …

**Won't (this release)**
- …

## 8. Experience

Link to designs or flows. Note the states that must exist: empty, loading,
error, partial, permission-denied, offline. Note accessibility target
(e.g. WCAG 2.1 AA) and locales in scope.

## 9. Non-functional requirements

Performance budget, availability, security and privacy handling, data
retention, analytics events, compliance obligations.

## 10. Dependencies and risks

| Item | Type | Owner | Impact if it slips | Mitigation |
|---|---|---|---|---|
| | Dependency / Risk | | | |

## 11. Rollout

Flagging, phased %, internal dogfood, pilot cohort, migration of existing data,
comms to users and support, rollback plan and its trigger condition.

## 12. Open questions

| Question | Owner | Needed by |
|---|---|---|
| | | |

## 13. Decision log

| Date | Decision | Made by | Rationale |
|---|---|---|---|
| | | | |
