---
name: devops-release
description: Decide whether a specific build may be released, and run the release — go/no-go against a release checklist, a rehearsed rollback plan, the release record (REL), and what to watch after it is live. Use this skill whenever the question is about shipping this build right now: "can we release", "ปล่อยได้ยัง", "deploy this", "how do we roll back", "what do we watch after release", "write the release notes", "something broke in production", or as the final gate after quality-assurance returns PASS. Do NOT use it to design or configure the CI/CD pipeline itself — GitHub Actions workflows, build automation, versioning strategy and monitoring setup are the deployment-devops-workflow skill; and do NOT use it to verify the feature against its spec — that is quality-assurance.

---

# DevOps / Release

The last gate. It answers one question: **may this specific build go live now?**

It is deliberately a narrow question. How the pipeline is built, which
deployment strategy the project uses, how monitoring is wired — all of that is
`deployment-devops-workflow`, and it is decided long before this moment. This
skill is about a single release event and the decision to make it or not.

## The rule that governs everything here

**An untested rollback is not a rollback.** It is a hope with a runbook.

Most release failures are not caused by the bad deploy. They are caused by
discovering, at the worst possible moment, that the way back does not work —
the migration is one-way, the previous artifact was never kept, nobody has the
credentials, the rollback takes forty minutes and the outage is now forty
minutes long.

If the rollback has not been rehearsed, the honest verdict is NO-GO, and saying
so is the entire value of this gate.

## Intake

1. Read `project/project.yml`. If `release.*` is empty, ask round 7 from
   `project-intake`'s question bank — where it deploys, who approves, how to roll
   back and how long that takes — and write the answers back.
2. Get the QA verdict. No `QAR` document, or a verdict of `BLOCK`, means this
   gate does not run at all. A release gate that overrides QA is not a gate.
3. Get the review decision. `REQUEST CHANGES` outstanding means the same.
4. Establish what is actually being released — commit, tag, or artifact. "The
   latest main" is not an answer; a release you cannot name you cannot roll back
   to.

## Workflow

1. **Confirm the inputs above.** Missing input is a NO-GO, not a smaller GO.
2. **Run the release checklist** — `assets/release-checklist.md`. Every item
   answered, skipped items given a reason in writing.
3. **Rehearse the rollback**, or confirm it was rehearsed on this release path
   with this shape of change. Migrations especially: a schema change that drops
   a column is not reversible by redeploying the old build.
4. **Decide.** `GO` · `GO WITH CONDITIONS` · `NO-GO`. Derived from the
   checklist, not from schedule pressure.
5. **Release**, following the project's chosen strategy.
6. **Watch.** Name the signals and the window *before* releasing, not after
   something looks odd.
7. **Write the record** — `REL-XXX-001` via `assets/release-record-template.md`,
   registered in `project/REGISTER.md`.

## The decision

- **NO-GO** — any blocker: QA verdict is `BLOCK`, review has outstanding
  `REQUEST CHANGES`, rollback is unrehearsed or impossible, a required
  environment variable or migration is unverified, nobody named is available to
  respond if it breaks.
- **GO WITH CONDITIONS** — releasable, but something must be true: released
  behind a flag, released outside peak hours, released with a named person
  watching a named signal for a stated window.
- **GO** — checklist clean, rollback rehearsed, watch plan agreed.

Write the conditions down. A condition held only in conversation is not a
condition; it is a thing everyone remembers differently at 2am.

## Watching after release

Decide these three before the deploy, and record them in the `REL`:

- **What signal** — error rate, a specific endpoint's latency, a business number
  that should move (or should not).
- **What threshold** means "roll back", stated as a number. "If it looks bad" is
  not a threshold and will be argued about while the outage continues.
- **How long** anyone is actually watching, and who.

An unwatched release is not finished. It is a bet that resolves silently.

## When it breaks

Order matters, and the common instinct gets it backwards:

1. **Restore service first.** Roll back or disable the flag. Do not debug in
   production while users are affected — the diagnosis is not more valuable than
   the outage is expensive.
2. **Then diagnose**, from logs and the artifact, on a system nobody is using.
3. **Then record it** in the `REL` — what happened, what the signal was, how
   long until it was noticed, how long until it was restored. The time-to-notice
   is usually the more useful number and the one nobody writes down.
4. **Then fix forward** through the normal pipeline. A hotfix that skips review
   and QA is how the second outage happens.

## Release notes

Written for whoever reads them, which is not you:

- What changed, from the user's point of view — not the commit list
- What they need to do, if anything
- What is known to still be broken — omitted known issues become support tickets
  that cost more than the honesty would have
- How to get back to the old behaviour, if that is possible

## Anti-patterns to catch and call out

- Releasing on a Friday afternoon with nobody watching the weekend
- "We'll roll back if there's a problem" where the rollback was never tried
- Bundling an urgent fix with unrelated changes so the rollback takes both back
- Skipping the gate because QA already passed — QA checked the feature, this
  gate checks the release
- A release record written a week later from memory
- Manual steps that live in one person's head rather than in the checklist

## How this fits the pipeline

Upstream, `quality-assurance` returns the verdict on the feature and
`code-reviewer` on the code — both must be clear before this gate opens. Beside
it, `deployment-devops-workflow` holds the standing knowledge about pipelines,
environments and monitoring that this gate assumes already exists. Downstream is
production, and the loop back to `product-owner` when the measured outcome is
compared to what the PRD promised.

## Files in this skill

- `assets/release-checklist.md` — the go/no-go run sheet
- `assets/release-record-template.md` — `REL` document for the register
