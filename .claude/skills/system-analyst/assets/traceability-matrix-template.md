# Traceability matrix — [system name]

| Item | Value |
|---|---|
| Document code | [TRC-XXX-001] |
| Revision | [00] |
| Source requirements | [PRD-XXX-001 rev NN §9, REQ-XXX-001 rev NN] |

The matrix is not the deliverable. **The gaps it exposes are.** Build it, then
read section 4.

---

## 1. Forward — requirement → design → test

Proves nothing was dropped.

| Req | Statement | Data model | Architecture / ADR | Behaviour spec | Test cases | Status |
|---|---|---|---|---|---|---|
| | | entities | ADR-NNN | UC / BR / state | TC-…-001…NNN | Covered / Partial / Not covered / Deferred |

Status meanings:

| Status | Means |
|---|---|
| Covered | Design element and at least one test case exist |
| Partial | Design exists, tests incomplete — say which AC is uncovered |
| Not covered | Nothing traces to it. This is a finding, not a row |
| Deferred | Out of this pass by decision. Record where the decision is written and confirm the model does not block it |

## 2. Backward — test → requirement

Proves nothing was invented.

| Test ID | Traces to | Notes |
|---|---|---|
| | | |
| | **none** | Investigate — undocumented behaviour or scope creep |

## 3. Design element → requirement

Proves the design has no free-floating parts. Every entity, endpoint, and
component earns its place.

| Design element | Kind | Traces to | Verdict |
|---|---|---|---|
| | entity / endpoint / component / ADR | | Justified / **unjustified — remove or raise the missing requirement** |

## 4. Findings

The output that matters.

### 4.1 Requirements with no test coverage

| Req | Why | Action |
|---|---|---|
| | untestable as written / forgotten / blocked on a missing decision | |

An untestable requirement is a defect in the requirement. Report it upstream
rather than writing a test that pretends.

### 4.2 Tests with no requirement

| Test | Behaviour tested | Action |
|---|---|---|
| | | Raise the missing requirement / delete the test |

### 4.3 Design elements with no requirement

| Element | Action |
|---|---|
| | Remove / raise the missing requirement |

### 4.4 Acceptance criteria not converted

| AC | Reason | Blocks |
|---|---|---|
| | needs visual design / needs an open decision | |

## 5. Coverage summary

| Metric | Count |
|---|---|
| Requirements in scope | |
| Requirements fully covered | |
| Acceptance criteria total | |
| Acceptance criteria with ≥ 1 test case | |
| Test cases total | |
| Test cases with no traced requirement | |
| Design elements with no traced requirement | |

**Coverage of acceptance criteria: [n] of [total].** State this number plainly.
Anything short of complete needs a line saying which are missing and why —
silent partial coverage reads as full coverage to everyone downstream.
