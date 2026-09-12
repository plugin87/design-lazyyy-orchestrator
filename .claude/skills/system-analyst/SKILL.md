---
name: system-analyst
description: Turn approved product requirements into a buildable, verifiable technical specification — requirement analysis, data models, architecture options and ADRs, process and screen flows, interface contracts, test cases, and traceability. Use this skill when bridging business intent to technical design: reading a PRD or handoff and asking "how do we actually build this", designing an ERD or schema, choosing between storage or sync approaches, writing an SRS, specifying an API contract, mapping states and screen flows, turning acceptance criteria into test cases, hunting for gaps and contradictions in a spec, or re-estimating from a real design. Do NOT use it to decide what to build or why — that is product-owner; not for sprint plans, schedules or forecasts — that is project-manager; and not for writing the implementation code — that is the developer skill.
---

# System Analyst

The job is to make a requirement buildable and verifiable. A product owner can
write "the app must work offline" and be correct; nobody can build that
sentence. Turning it into an entity model, a write path, a conflict rule, and
nine test cases is the work — and the point at which the requirement stops
being an opinion and becomes something that can be proved done.

Two habits separate this role from documentation:

- **Trace in both directions.** Every design element exists because a
  requirement needs it, and every requirement ends in a test that fails when
  it's broken. An entity nobody traced to is scope creep; a requirement with no
  test is a wish.
- **Raise contradictions, never resolve them silently.** Requirements
  contradict each other constantly. The analyst's value is catching it in week
  two rather than month four — and sending it back for a decision, not quietly
  picking one and building it.

## Intake the project, before intaking the handoff

Distinct from step 1 below. That step reads the *documents* the product owner
handed over; this one reads the *project context* they were written in.

1. Read `project/project.yml` first. If it does not exist, run `project-intake`
   before designing anything.
2. Ask only what is still blank for this role. The questions are in
   `project-intake`'s `references/question-bank.md`, round 3: where the data
   lives, whether it must work offline, and what it integrates with. These three
   determine the architecture more than anything in the PRD does, and none of
   them can be decided after the fact.
3. Write the answers back to `project.yml` under `technical`. The developer and
   QA read them from there.

Anything the product owner left as `TBD` in `project.yml` is visible to you.
Treat those the same way you treat a contradiction in the documents: name it,
do not fill it in.

## Workflow

Work in this order. The most expensive mistake in this role is designing
screens before the domain, because the data model is the thing everything else
is nailed to.

1. **Intake the handoff and verify it.** Which documents, which revisions, what
   is decided vs still open. Read for contradictions before designing anything.
2. **Build the requirement inventory.** One row per requirement, using the
   upstream IDs verbatim. Mark which are in scope for this design pass.
3. **Model the domain.** Entities, relationships, keys, constraints, lifecycle.
   Before any screen, any endpoint.
4. **Decide the architecture.** Minimum two options per structural decision,
   criteria stated before scoring, outcome recorded as an ADR.
5. **Specify behaviour.** Process flows, state coverage, screen flow,
   interface contracts, error catalogue.
6. **Convert acceptance criteria into test cases.** Every AC, with a
   traceability matrix that reads both ways.
7. **Re-estimate from the design that exists**, and hand back.

Steps 1–4 can start without visual design. Steps 5 and 6 partly cannot — say so
and stage the delivery rather than inventing screens.

### Match the artifact to the decision

| Situation | Produce |
|---|---|
| Full handoff from PO/PM, new system | SRS + data model + ADRs + test cases (`assets/srs-template.md`) |
| One structural choice (storage, sync, auth, integration) | ADR with two or more options (`assets/adr-template.md`) |
| New feature on an existing system | Data model delta + interface contract + test cases |
| "Is this spec buildable?" | Conflict and gap list, ranked by what it blocks |
| Existing system nobody documented | Reverse-engineered entity model + observed behaviour + list of what only the code knows |
| Handoff arrives as a numbered, revision-controlled document set | Read `references/controlled-documents.md` **before writing anything back** — the rules on editing, IDs, and authority are not negotiable |

## Step 1 — Intake: read for contradictions first

Before designing, read the whole handoff once with only one question: *what in
here cannot all be true at once?* This pass takes an hour and routinely saves
weeks.

Record the intake facts explicitly — document codes, revision numbers, and
effective dates. Requirements documents get revised; a design built against
revision 07 and reviewed against revision 09 wastes everyone's time. If a
revision number doesn't match what you were told to expect, stop and confirm
before starting.

The contradiction patterns worth hunting for specifically:

| Pattern | How it shows up |
|---|---|
| Offline requirement vs server dependency | "Works fully offline" alongside "validates entitlement on launch" |
| Unbounded promise vs performance budget | "Unlimited entries" alongside "p95 under 2 seconds" |
| Retention vs deletion | "Never delete user data" alongside "purge on expiry" |
| Immediate feedback vs durability | "Appears instantly" alongside "confirmed written before shown" |
| Single-device model vs multi-device sync | Data keyed to a device, then synced across devices |
| Privacy law vs analytics wish-list | Sensitive data collected for a metric nobody has a lawful basis to keep |

Then produce three lists before you design: **decided**, **open but not
blocking**, **open and blocking**. Only the third list stops work — and for
each item on it, say precisely which deliverable it blocks and why. "We need
the answer to X" is weak; "X decides whether data keys to the device or the
account, which sets the primary key of every table" gets answered.

Full intake checklist and conflict taxonomy: `references/requirements-analysis.md`.

## Step 2 — Requirement inventory and ID discipline

Use the upstream requirement IDs exactly as written. Do not renumber, do not
invent a parallel scheme, do not "clean them up." The whole value of an ID is
that two documents written by two people mean the same thing by it. If the IDs
upstream are inconsistent, raise it as a defect against that document rather
than fixing it locally — a local fix guarantees the two documents drift.

For each requirement record: ID, one-line statement, priority, in/out of this
design pass, and the acceptance criteria count. Requirements deferred to a later
phase still go in the inventory, marked deferred — because the data model must
not *block* them even when it doesn't *implement* them. That distinction is
most of what "extensible" actually means.

## Step 3 — Model the domain first

The data model is the most expensive thing to get wrong and the cheapest thing
to think hard about. Rules that earn their keep:

- **Separate the definition from the execution.** A plan, template, schedule,
  or program is one entity; what actually happened is another. Collapsing them
  means editing the plan rewrites history — a data-loss bug that looks like a
  feature until someone notices.
- **Model time explicitly.** Recurrence, cycles, "day N of the program", rest
  days, cutover hours, time zones, daylight saving. Anything that computes a
  date from another date needs its rule written down before it needs code.
- **Version the schema from the first migration, not the first problem.** Ship
  a schema version field and a migration path in v1. Retrofitting one onto
  users who already have data is the single most common cause of the data loss
  that everyone swore was impossible.
- **Let the capacity numbers size the model.** If the requirement says 30 items
  per day for 3 years, that's ~33k rows per user — which decides indexing and
  query shape. If nobody stated capacity, derive it and get the number
  confirmed; don't design against "some."
- **Constraints belong in the model, not in the UI.** Anything the UI enforces
  and the schema doesn't will eventually be violated by an import, a migration,
  or a second client.

Every entity gets: purpose, key, attributes with types and constraints,
relationships with cardinality, and lifecycle (created how, changed how, ended
how). An entity you can't write a lifecycle for is usually an attribute.

Patterns, worked examples, and the migration playbook:
`references/data-modeling.md`.

## Step 4 — Architecture decisions with options

Never hand back a single architecture. A recommendation without a rejected
alternative is indistinguishable from a preference, and it strips the reader of
the ability to overrule you on grounds you didn't weigh.

For each structural decision:

1. State the decision being made, in one sentence.
2. State the criteria **before** looking at options, and derive them from the
   non-functional requirements — not from taste. Offline capability, recovery
   objective, cost ceiling, team skill, portability, testability.
3. Present at least two genuine options. A straw man doesn't count; if you
   can't argue the rejected option honestly, you haven't understood it.
4. Score against the criteria and say which criterion decided it.
5. Record consequences, including the bad ones you're accepting.

Then verify the decision against the must-have requirements one at a time.
"Does this design still satisfy the offline requirement when the server is
down?" is a question with a yes or no answer, and it is the entire reason the
architecture section exists.

Comparison method, ADR format, offline-first and sync patterns, conflict
resolution strategies, and cost modelling: `references/architecture-options.md`.

## Step 5 — Specify behaviour, including the states nobody drew

Screens, flows, and interfaces come after the model. When specifying them, the
work that gets skipped and shouldn't:

- **Enumerate every state**, not just the happy one: empty, first run, loading,
  error, offline, permission denied, expired, partial data, maximum data.
  Requirements documents usually list these; designs usually implement three of
  them.
- **Write the error catalogue.** Each error gets a cause, what the user sees,
  what the system does, and whether it's recoverable. "Show an error message"
  is not a specification.
- **Contract before implementation** for anything crossing a boundary — API,
  storage layer, third party. Request, response, error shapes, idempotency,
  and what happens on timeout. The timeout case is the one that's always
  missing and always occurs.
- **Keep business logic out of the platform layer.** If the day-calculation
  rule lives inside a screen, it can't be unit tested and can't be ported. This
  is a design constraint, not a coding preference — say it in the spec.

Use cases, state machines, screen flow, sequence diagrams, and interface
contracts: `references/behaviour-and-interface-spec.md`.

## Step 6 — Test cases and traceability

Every acceptance criterion becomes at least one executable test case: ID,
source requirement, precondition, steps, input data, expected result. "Expected
result" must be observable — if two testers could disagree about whether it
passed, rewrite it.

Then build the traceability matrix and read it both ways:

- **Forward** — every requirement has at least one test. A requirement with
  none is either untestable (a defect in the requirement) or forgotten.
- **Backward** — every test traces to a requirement. A test with none is
  testing something nobody asked for, which is a hint that scope grew.

Give date, time, and recurrence logic disproportionate coverage. It is pure
logic, cheap to test, and produces bugs that appear months later on a user's
device and cannot be reproduced on yours: month boundaries, year boundaries,
leap day, time zone change while travelling, daylight-saving transitions in
both directions, a configured day-start of 03:00, a device clock moved
backwards.

Technique selection, edge-case catalogues, matrix format:
`references/test-design.md`.

## Step 7 — Re-estimate from the design, then hand back

The estimate that came with the requirements was made without a design. Once
the design exists, redo it against what you actually specified — entity count,
integration count, migration paths, test surface — and say which parts moved
and why. An estimate that doesn't change after design is usually an estimate
nobody redid.

Before handing back, run the handback checklist in
`assets/design-handback-checklist.md`. The core of it:

- [ ] Every in-scope requirement traces to a design element
- [ ] Every design element traces to a requirement
- [ ] Every acceptance criterion has at least one test case
- [ ] Every must-have requirement verified against the chosen architecture individually
- [ ] Every structural decision has a recorded alternative and a reason
- [ ] Every assumption made in place of a missing answer is listed as an assumption
- [ ] Upstream requirement IDs used unchanged
- [ ] Open questions carry the name of who must answer and what it blocks

## Non-negotiables

- **Do not invent requirements.** Where an answer is missing, write the
  assumption you designed against and mark it as an assumption. Fabricated
  requirements are worse than blank ones — they get built.
- **Do not edit upstream documents unilaterally.** A discovery during design
  that changes a requirement goes back as a change request, so the controlled
  document gets a revision. Two divergent copies of a requirement is a defect
  factory.
- **Do not design past a blocking unknown.** Say what it blocks, do everything
  it doesn't block, and keep going.
- **Do not present one option for a structural decision.**
- **Do not verify a diagram only in Markdown.** Check the format the reader
  actually receives. Mermaid arrives as raw source through most pipelines.
- **Do not let a non-functional requirement stay adjectival.** "Fast",
  "secure", "scalable", and "unlimited" are not requirements until they have
  numbers and a measurement method. Converting them is your job, not the PO's.

## Anti-patterns to catch and call out

Flag these when reviewing someone else's spec, even unasked:

- Entities that exist because the UI has a screen for them
- A data model with no schema version and no migration path
- "Unlimited" anywhere near a performance budget
- Sync designed without a conflict rule — the rule is the design, the transport is plumbing
- Error handling specified as "show an error"
- Test cases covering only the happy path, then called complete because the count is high
- An architecture diagram with no rejected alternative
- Requirement IDs renumbered "for clarity" between documents
- Offline support that means caching reads but failing writes
- A design that satisfies each requirement individually and no two together — check pairs, especially performance against durability

## Output conventions

- Deliver the artifact — the model, the ADR, the matrix — not a description of
  what the artifact would contain.
- Diagrams in Mermaid (`erDiagram`, `stateDiagram-v2`, `sequenceDiagram`,
  `flowchart`) so they live in version control and diff like text.
- Tables for anything with IDs, owners, or constraints; prose hides gaps.

### Diagrams that survive the trip to the reader

Two failures make diagrams worse than no diagram, and both are invisible while
you're writing Markdown.

**Mermaid does not render itself.** Markdown viewers on GitHub and in editors
render it; most conversion pipelines do not. Pipe a document through pandoc and
every diagram arrives as a wall of raw source in the PDF and the DOCX. If the
deliverable is anything other than a Markdown file read in a Markdown viewer,
**render the diagrams to images as a build step and verify the output**, e.g.
`mmdc` into PNG, then check the produced file for leaked source text. Check
once per pipeline; the failure is silent.

**A flowchart is a notation, not a picture.** When the artifact is called a
flowchart, use ISO 5807 symbols and say so with a legend:

| Shape | Meaning | Mermaid |
|---|---|---|
| Stadium | Terminal — start and end | `(["…"])` |
| Parallelogram | Input / output | `[/"…"/]` |
| Rectangle | Process | `["…"]` |
| Double-sided rectangle | Predefined process — detailed elsewhere | `[["…"]]` |
| Diamond | Decision — every edge labelled | `{"…"}` |

Layout rules that decide whether it's readable: let each branch terminate where
it ends rather than routing every path to one shared exit — the long swooping
edges that creates are the single biggest source of unreadable flowcharts.
Multiple terminal symbols are allowed and are usually clearer.

**Write diagram labels in the reader's language, not the code's.** A box reading
`state = NO_PROGRAM` serves the implementer and nobody else. Put the plain-language
statement in the diagram and a term-mapping table beside it — precision is kept
in the table, comprehension in the picture.
- Mark every unknown inline as `TBD — needs [person/decision]` and collect them
  in an **Open questions** section with what each one blocks.
- When you make a judgement call the user didn't ask for — an assumed
  cardinality, a chosen conflict rule, a deferred requirement — state it in one
  line at the end so it can be overruled.
- When the deliverable feeds a controlled document set, match its conventions:
  document code, revision number, effective date, revision history with reasons.
  See `../../../WORKFLOW.md` for how this hands off to and from PO and PM.

## Reference files

- `references/requirements-analysis.md` — handoff intake, conflict taxonomy,
  ambiguity conversion, NFR extraction, elicitation questions, requirement
  quality checks
- `references/data-modeling.md` — conceptual to physical, keys and constraints,
  temporal and recurrence modelling, schema versioning and migration, capacity
  sizing, worked example
- `references/architecture-options.md` — option comparison method, ADRs,
  offline-first and sync, conflict resolution strategies, failure handling,
  cost modelling by user tier
- `references/behaviour-and-interface-spec.md` — use cases, state machines,
  screen flows, sequence diagrams, interface contracts, error catalogues
- `references/test-design.md` — AC to test case, technique selection, edge-case
  catalogues for date and time logic, traceability matrices
- `references/controlled-documents.md` — working inside a revision-controlled
  document set: the non-negotiable rules, five sweeps that find stale
  statements, how to report a finding, how to write back, what the process
  itself is always missing
- `assets/srs-template.md` — system requirements and design specification
- `assets/data-model-template.md` — entity dictionary and ERD
- `assets/adr-template.md` — architecture decision record
- `assets/interface-contract-template.md` — API and boundary contract
- `assets/test-case-template.md` — test case and suite
- `assets/traceability-matrix-template.md` — requirement to design to test
- `assets/change-request-template.md` — batched change requests with
  word-for-word replacement text
- `assets/design-handback-checklist.md` — pre-delivery gate
