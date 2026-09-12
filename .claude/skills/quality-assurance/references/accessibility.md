# Accessibility (WCAG 2.2 Level AA)

Verify the implementation is usable by people using assistive technology and
non-mouse input. Default target: **WCAG 2.2 Level AA**. Automated tooling catches
roughly a third of issues — the rest needs keyboard, screen-reader, and human
judgement. A green axe run is a floor, not a pass.

## Table of contents
- The three-layer method
- Automated pass (axe-core)
- Keyboard & focus
- Screen-reader & semantics
- Contrast & visual
- WCAG 2.2 additions worth a specific look
- Locale / Thai-language notes
- Common findings and their severity

## The three-layer method

Run all three; each finds what the others miss.

1. **Automated** — axe-core catches contrast, missing names/alt, ARIA misuse,
   landmark and heading problems at scale.
2. **Keyboard** — unplug the mouse. Tab through the whole flow.
3. **Semantics / screen reader** — verify the accessibility tree conveys what the
   visual UI conveys.

## Automated pass (axe-core)

- Run via `@axe-core/playwright` (`AxeBuilder`) across the states that matter —
  default, opened menus/dialogs, error state — not just initial load. Interactive
  states hide most violations.
- Treat every violation as at least **MAJOR**; Level A violations are **BLOCKER**.
- Automated *silence is not conformance* — proceed to the manual layers.

## Keyboard & focus

- **Everything interactive is reachable and operable** by keyboard alone; nothing
  is mouse-only (SC 2.1.1).
- **No keyboard traps** — focus can always move on (SC 2.1.2).
- **Visible focus** — every focused element has a clearly visible indicator
  (SC 2.4.7); with WCAG 2.2, it must also not be hidden behind sticky headers and
  must meet the focus-appearance size/contrast bar (SC 2.4.11).
- **Logical order** — tab order follows reading/visual order (SC 2.4.3); focus
  moves sensibly into and out of dialogs and returns on close.
- **No focus loss** — removing/replacing content doesn't strand focus on a
  detached node.

## Screen-reader & semantics

- **Semantic HTML first.** A real `<button>`, `<a>`, `<nav>`, `<h1–h6>` over a
  `div` with ARIA bolted on. ARIA is a patch, not a default.
- **Accessible name & role** for every control (SC 4.1.2) — icon-only buttons need
  a label; inputs need programmatically associated `<label>`s (SC 1.3.1, 3.3.2).
- **Structure** — one logical `h1`, no skipped heading levels, landmarks present,
  lists marked up as lists.
- **State is announced** — expanded/collapsed, selected, checked, `aria-current`,
  and dynamic changes via a live region where appropriate.
- **Images** — meaningful images have alt text that conveys purpose; decorative
  images are empty-alt / hidden (SC 1.1.1).
- **Errors** — validation errors are associated with their field and announced,
  not signalled by color alone (SC 3.3.1, 1.4.1).

## Contrast & visual

- **Text contrast** ≥ 4.5:1 (≥ 3:1 for large text) (SC 1.4.3); **non-text**
  (UI boundaries, icons, focus rings, chart strokes) ≥ 3:1 (SC 1.4.11).
- Verify contrast against the *token* value in each theme — a token that passes in
  light may fail in dark.
- **Not by color alone** (SC 1.4.1) — links, states, and chart series need a second
  cue (underline, icon, label).
- **Reflow & zoom** — usable at 200% zoom and 320px reflow without loss of content
  or horizontal scrolling (SC 1.4.10, 1.4.4).
- **Motion** — respect `prefers-reduced-motion`; no content flashes > 3×/sec.

## WCAG 2.2 additions worth a specific look

These are newer and frequently missed:
- **2.4.11 Focus Not Obscured** — sticky/overlay elements must not hide the focused
  control.
- **2.5.8 Target Size (Minimum)** — interactive targets ≥ 24×24 CSS px (or adequate
  spacing). Watch dense toolbars and icon rows.
- **3.3.7 Redundant Entry** — don't force re-entering info already given in a flow.
- **3.3.8 Accessible Authentication** — no cognitive test (e.g. solving a puzzle,
  transcribing) as the only way to authenticate.

## Locale / Thai-language notes

- `lang` is set correctly on the document and on any content that switches language
  (SC 3.1.1 / 3.1.2) — matters for pronunciation and screen-reader voice.
- Thai has no inter-word spaces: don't rely on space-based truncation or
  word-count logic; verify line-breaking and that `lang="th"` drives correct
  wrapping. Check that Thai glyph height doesn't clip in fixed-height controls.
- If the product is bilingual, verify names, labels, and error messages are
  localized in the accessibility tree, not just visually.

## Common findings and their severity

- Keyboard trap / control unreachable by keyboard → **BLOCKER** (Level A)
- Control with no accessible name / form field with no label → **BLOCKER**
- Meaningful image with no alt / info conveyed by color alone → **BLOCKER**
- Text contrast below 4.5:1 (AA) → **MAJOR**
- Focus indicator missing or obscured → **MAJOR**
- Target smaller than 24×24 with no spacing → **MAJOR**
- Missing `aria-current` / minor semantic redundancy → **MINOR**
