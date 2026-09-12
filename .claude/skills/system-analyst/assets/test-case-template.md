# Test cases — [requirement ID / feature]

| รายการ | รายละเอียด |
|---|---|
| รหัสเอกสาร | TST-XXX-001 |
| ฉบับแก้ไขครั้งที่ | 00 |
| วันที่มีผลบังคับใช้ | YYYY-MM-DD |
| สถานะ | ร่าง / รอทบทวน / อนุมัติแล้ว |
| เอกสารอ้างอิง | [REQ-XXX-001 rev NN] |
| ผู้จัดทำ | นักวิเคราะห์ระบบ |
| Coverage rule | Every acceptance criterion produces at least one case; every requirement gets at least one negative case |

---

## 1. Test data sets

Define once, reference by ID. Restating setup in every case is how setup drifts.

| ID | Name | Contents | Used for |
|---|---|---|---|
| DS-01 | Minimal | | Degenerate and boundary cases |
| DS-02 | Typical | | Most functional cases |
| DS-03 | Capacity | At stated capacity limits | Performance, pagination |
| DS-04 | Migration | Data written by each shipped schema version | Upgrade paths |
| DS-05 | Conflict | Same records edited on two offline clients | Sync resolution |

## 2. Test case

Repeat per case.

```
TC-[REQ]-[NNN]   [Short title — the condition being tested, not "test the feature"]

Traces to        [requirement ID / AC reference]
Priority         High / Medium / Low — justified by the requirement's priority
Type             Functional | Negative | Boundary | State transition |
                 Performance | Accessibility | Migration | Sync
Technique        Equivalence class | Boundary value | Decision table |
                 State transition | Error guessing
Data set         [DS-NN, or inline if unique to this case]

Preconditions
  - [System state, with concrete values — dates, timezone, offsets]
  - [Device / environment state]

Setup data
  - [Exact records, not "a program"]

Steps
  1. [Single unambiguous action]
  2. …

Expected result
  - [Observable. If two testers could disagree, rewrite it.]
  - [Include the non-functional check where one applies — latency, announcement,
     touch target — rather than deferring it to a phase that never happens.]

Postconditions
  - [What was written, what was not]
```

## 3. Case index

| Test ID | Title | Traces to | Type | Priority | Status |
|---|---|---|---|---|---|
| | | | | | Not run / Pass / Fail / Blocked |

## 4. Coverage summary

| Requirement | AC count | Cases | Negative cases | NFR cases | Gap |
|---|---|---|---|---|---|
| | | | | | |

**Gaps to report** — not to quietly close:

| Gap | Kind | Action |
|---|---|---|
| | AC with no case / untestable AC / case with no requirement / undefined behaviour found while tabulating | |

A case with no requirement behind it is usually a real edge case nobody wrote
down. Raise the missing requirement or delete the case — do not leave it
untraced.

## 5. Edge-case coverage confirmation

Tick only what has an actual case ID behind it.

**Date, time, recurrence** — [see references/test-design.md §3]

- [ ] Day-start offset, both sides of the boundary
- [ ] Month boundary · [ ] Year boundary · [ ] Leap day · [ ] 29 Feb in a non-leap year
- [ ] DST forward · [ ] DST backward
- [ ] Timezone travel east · [ ] west
- [ ] Device clock moved backwards · [ ] forwards
- [ ] Exact cycle multiple (modulo returning 0)
- [ ] Minimum cycle length · [ ] maximum cycle length
- [ ] Start date in the future

**Offline and sync**

- [ ] Every capability exercised with no network
- [ ] Write offline, force-quit, relaunch — data intact
- [ ] Long offline period then reconnect — batching, no loss
- [ ] Same record edited on two offline clients — stated rule applied
- [ ] Sync interrupted mid-batch — resumable, no half-applied state
- [ ] One item rejected 4xx — rest of the batch still syncs

**Storage, migration, lifecycle**

- [ ] Storage full during a write
- [ ] Permission denied on storage
- [ ] Upgrade from every previously shipped version
- [ ] Downgrade — newer schema detected, writes refused
- [ ] Migration failure — old data intact, retry offered
- [ ] At stated capacity — performance budget still met
- [ ] Beyond stated capacity — degrades, never rejects a write

**Accessibility**

- [ ] Status announced by screen reader, not colour alone
- [ ] Maximum system text size — no truncation or overlap
- [ ] Touch targets meet the stated minimum
- [ ] Contrast meets the stated standard and level
