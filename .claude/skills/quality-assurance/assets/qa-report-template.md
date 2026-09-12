# Quality Assurance — <component / feature / PR>

| รายการ | รายละเอียด |
|---|---|
| รหัสเอกสาร | QAR-XXX-001 |
| ฉบับแก้ไขครั้งที่ | 00 |
| วันที่มีผลบังคับใช้ | YYYY-MM-DD |
| สถานะ | ร่าง / รอทบทวน / อนุมัติแล้ว |
| เอกสารอ้างอิง | [REQ-XXX-001 rev NN · DSN-XXX-001 rev NN] |
| ผู้จัดทำ | [ชื่อ] |

**Verdict:** BLOCK | PASS WITH ADVISORIES | PASS
**Scope:** <what was reviewed — diff, branch, route, component>
**Spec source:** <ticket / acceptance criteria / Figma frame, or "MISSING">
**Date:** <YYYY-MM-DD>  ·  **Reviewer:** <who / which agent>

> Verdict is derived, not chosen: any BLOCKER ⇒ BLOCK; no blockers but ≥1
> MAJOR/MINOR ⇒ PASS WITH ADVISORIES; nothing above NIT ⇒ PASS.

---

## Functional            [PASS | ADVISORIES | BLOCK | SKIPPED — reason]

- [BLOCKER] `<file:line>` — <what's wrong; expected X, got Y> → <fix>
- [MAJOR]   `<file:line>` — <what's wrong> → <fix>
- [MINOR]   `<file:line>` — <what's wrong> → <fix>

**Criteria coverage**

| # | Acceptance criterion | Result | Evidence |
|---|---|---|---|
| 1 | <criterion> | met / failed / untestable | <test name, file:line, or manual step> |

---

## Visual & Design System [PASS | ADVISORIES | BLOCK | SKIPPED — reason]

- [MAJOR] `<element / selector>` — token drift: uses `<actual>` vs `<expected token>` → <fix>
- [MAJOR] `<element>` — breaks in <theme / breakpoint> → <fix>
- [MINOR] `<element>` — <missing state / spacing> → <fix>

**Coverage run:** themes <light/dark/…> · breakpoints <mobile/tablet/desktop> ·
states <default/hover/focus/active/disabled/loading/error>

---

## Accessibility (WCAG 2.2 AA) [PASS | ADVISORIES | BLOCK | SKIPPED — reason]

- [BLOCKER] `<element>` — <SC number + name>: <what fails> → <fix>
- [MAJOR]   `<element>` — <SC number + name>: <what fails> → <fix>

**Layers run:** automated (axe-core, states: <…>) · keyboard · semantics/screen reader

---

## Gaps

- <missing spec, unavailable environment, or untestable area that limits
  confidence in this verdict>

---

## Next action

- **If BLOCK:** back to implementation. Blockers to clear: <list>
- **If PASS WITH ADVISORIES:** ship-able; advisories tracked as <tickets / follow-up>
- **If PASS:** clear to proceed to the deployment tier
