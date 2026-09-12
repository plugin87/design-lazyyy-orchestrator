# Quality Assurance — run sheet

A tickable pass to work through while running the gate. It records *what was
actually checked*, so "SKIPPED" and "not checked" never get confused. The
reasoning behind each line lives in `references/`.

## 0. Inputs

- [ ] Scope fixed — diff / branch / PR / route under review, and nothing wider
- [ ] Functional spec located (acceptance criteria / ticket) — or logged as a gap
- [ ] Design source of truth located (Figma frame + tokens) — or logged as a gap
- [ ] Accessibility target set (default WCAG 2.2 AA) + locale requirements noted
- [ ] Dimensions to run decided; any skip has a recorded reason

## 1. Functional — `references/functional.md`

- [ ] Rubric written from the spec *before* reading the implementation
- [ ] Happy path completes and produces the specified result
- [ ] Edge cases: empty / single / many / max length / boundary values
- [ ] Failure paths: network error, unauthorized, concurrent action
- [ ] Error handling: usable messages, no crash, no data loss, no stuck UI
- [ ] State & side effects: cleanup runs, no double-submit, optimistic updates reconcile
- [ ] Adjacent flows the diff touches transitively still work
- [ ] Contract honest: props / API shapes / types match caller expectations
- [ ] Risky behaviour pinned by tests (Vitest / Playwright), queried by role not test-id

## 2. Visual & design system — `references/visual.md`

- [ ] Token compliance checked **first** — no raw values where a token exists
- [ ] Token roles correct (no border token used for text, etc.)
- [ ] Layout, spacing, typography, color, radius, elevation match the frame
- [ ] Icons and imagery: correct asset, size, optical alignment
- [ ] Every supported theme verified (light / dark / brand variants)
- [ ] Breakpoints verified incl. awkward in-between widths
- [ ] Interactive states verified: default, hover, focus, active, disabled, loading, error, selected
- [ ] Content extremes: long strings, empty, localized copy (Thai line-breaking), RTL if supported
- [ ] Snapshots deterministic where used (fixed viewport, fonts loaded, animation off, clock controlled)

## 3. Accessibility — `references/accessibility.md`

**Automated**
- [ ] axe-core run across states that matter, not just initial load
- [ ] Every violation triaged (Level A ⇒ BLOCKER, otherwise ≥ MAJOR)

**Keyboard**
- [ ] All interactive elements reachable and operable by keyboard alone (2.1.1)
- [ ] No keyboard traps (2.1.2)
- [ ] Focus visible, not obscured, meets appearance bar (2.4.7, 2.4.11)
- [ ] Tab order follows reading order; dialog focus enters and returns (2.4.3)
- [ ] Focus never stranded on removed content

**Semantics**
- [ ] Semantic HTML used before ARIA
- [ ] Accessible name + role for every control (4.1.2); inputs have labels (1.3.1, 3.3.2)
- [ ] Heading structure and landmarks correct
- [ ] Dynamic state announced (expanded, selected, live regions)
- [ ] Images: meaningful have alt, decorative are hidden (1.1.1)
- [ ] Errors associated with the field and not signalled by color alone (3.3.1, 1.4.1)

**Visual / WCAG 2.2**
- [ ] Text ≥ 4.5:1, large text ≥ 3:1, non-text ≥ 3:1 — verified per theme (1.4.3, 1.4.11)
- [ ] Usable at 200% zoom and 320px reflow (1.4.10, 1.4.4)
- [ ] `prefers-reduced-motion` respected; no flashing > 3×/sec
- [ ] Target size ≥ 24×24 or adequately spaced (2.5.8)
- [ ] Redundant entry and accessible authentication checked (3.3.7, 3.3.8)
- [ ] `lang` correct on document and on language-switching content (3.1.1, 3.1.2)

## 4. Decide

- [ ] Every finding has severity, location, and a concrete fix
- [ ] Severities calibrated honestly against user-facing consequence
- [ ] Verdict derived from findings, not chosen
- [ ] Gaps listed explicitly
- [ ] Report emitted — then **stop**; fix only if asked
