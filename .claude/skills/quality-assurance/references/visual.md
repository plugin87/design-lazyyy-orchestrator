# Visual & Design-System Fidelity

Verify the build matches the *approved design*, and that it does so **by using the
design system** — not by hand-tuned values that happen to look right. Two builds
can look identical in a screenshot and only one is correct: the one built from
tokens. Both dimensions matter here.

## Table of contents
- Compare against the source of truth
- Token compliance (the part that matters most)
- Responsive & state coverage
- Visual regression with Playwright
- Common findings and their severity

## Compare against the source of truth

The reference is the Figma frame and the project's tokens — not the reviewer's
preference. If there's no approved design for what shipped, that's a gap: report
it and review only token compliance.

Check, in the built UI:
- **Layout & spacing** — alignment, padding/margin, gaps match the frame.
- **Typography** — family, size, weight, line-height, letter-spacing, and
  truncation/overflow behaviour.
- **Color** — fills, text, borders, states — matched to the intended token.
- **Elevation, radius, borders** — shadows, corner radii, stroke weights.
- **Iconography & imagery** — correct assets, sizes, and optical alignment.

## Token compliance — check this first

A pixel-perfect screenshot built from magic numbers is a **MAJOR** finding, not a
pass. The design system is the contract.

- **No raw values where a token exists.** `#1a1a1a`, `padding: 13px`,
  `border-radius: 7px` are drift if the system defines a token for that role.
  Flag each with the actual value *and* the token it should reference.
- **Right token for the right role.** Using a border color token for text, or a
  surface token for a border, is drift even if the hex matches — the intent is
  wrong and it will break under theming.
- **Theme integrity.** Verify it holds in every theme the project supports
  (light/dark, brand variants). Hard-coded colors usually pass one theme and
  fail the other — a fast way to surface drift.
- **Component API over overrides.** Prefer the design-system component's supported
  props/variants over ad-hoc `className` overrides that fight the system.

> When a specific brand color is mandated by CI, the mandated token is the correct
> value — match the design system's defined token, don't substitute a visually
> similar one.

## Responsive & state coverage

A component isn't done at one width in one state. Verify:
- **Breakpoints** — mobile, tablet, desktop; no overflow, no broken wrapping, no
  overlap at the awkward in-between widths.
- **Interactive states** — default, hover, focus, active, disabled, loading,
  error, selected. Focus especially (it also carries into accessibility).
- **Content extremes** — long strings, empty, RTL if supported, and localized
  copy (e.g. Thai line-breaking and text height vs Latin).

## Visual regression with Playwright

For components that shouldn't drift over time, pin them with snapshots.

- Use `toHaveScreenshot()` on stable, seeded states; mask genuinely dynamic
  regions (timestamps, avatars) rather than loosening the threshold globally.
- Snapshot the meaningful states (default / hover / error), not one catch-all.
- Keep snapshots deterministic — fixed viewport, fonts loaded, animations
  disabled, clock controlled. A flaky snapshot is worse than none; it trains
  people to ignore the gate.
- A diff is a *prompt to judge*, not an automatic fail: an intended redesign
  updates the baseline; an unintended change is the finding.

## Common findings and their severity

- Build visibly diverges from the approved design in a way users notice → **BLOCKER**
- Raw value where a token exists / wrong-role token → **MAJOR**
- Breaks in dark mode or a supported theme → **MAJOR**
- Layout breaks at a real breakpoint → **MAJOR**
- Missing a non-critical interactive state → **MINOR**
- Sub-pixel spacing difference no one will see → **NIT**
