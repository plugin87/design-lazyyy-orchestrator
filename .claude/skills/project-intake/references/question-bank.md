# Question bank

Every round of questions the pipeline asks, and what each answer is for.

Each entry has three parts:

- **Why ask** — what breaks later if this goes unanswered
- **Good / bad answer** — shown as examples, because the difference is easier to
  see than to describe
- **Where it lands** — the field in `project.yml`, and the document section that
  consumes it

**How to use it** — ask at most five questions per round, in a single message ·
skip anything `project.yml` already answers · when the student does not know,
write `TBD`, never a guess.

---

## Round 0 · Opening the project — `project-intake`

### 0.1 What is this project called

- **Why ask** — every document needs a name in its header, and the student needs
  to be able to refer to their own work.
- **Good** `Rehearsal room booking for the music club` — **Bad** `Final project`
- **Where it lands** `meta.name` → the header of every document

### 0.2 Give me a three-letter code

- **Why ask** — every document code in the system is built from it
  (`PRD-XXX-001`). Changing it later means sweeping every document at once,
  because supporting documents cite the main document's requirement IDs.
- **Good** `BKG` (from booking) — **Bad** `PROJECT1`, digits, non-Latin characters
- **Where it lands** `meta.code` → every document code

### 0.3 What problem does this solve, in one sentence

- **Why ask** — a project stated as a solution from the start means the whole
  pipeline designs a solution nobody ever checks against the problem. This is the
  most expensive and most common mistake in the entire process.
- **Good** `Club members double-book the rehearsal room three or four times a
  week because bookings are tracked in a chat group`
  — **Bad** `I want to build a booking website` (that is a solution, not a problem)
- **Where it lands** `problem.statement` → PRD §2 · SRS §1
- **If the student answers with a solution** do not correct it for them. Record it
  under `assumptions` as *the solution the student proposed*, and let
  `product-owner` do the work of pushing back to the problem.

### 0.4 Who are the users, and what do they do today without this

- **Why ask** — two parts. The first stops the answer being "users", which carries
  no information. The second matters more: **there is always an existing
  workaround.** If you cannot find it, the problem is not understood yet — and the
  workaround is the baseline the new thing has to beat.
- **Good** `About 20 members who rehearse regularly · today they post in the chat
  group and wait for someone to reply`
  — **Bad** `General users · nothing exists yet`
- **Where it lands** `problem.users`, `problem.today_workaround` → PRD §2 and §6

### 0.5 How much time is there, and who is working on it

- **Why ask** — this bounds the size of everything that follows. Unknown at the
  start means a scope that cannot be delivered, discovered at the point where
  cutting is hardest.
- **Good** `8 weeks, working alone, about 3 hours a day`
  — **Bad** `As fast as possible`
- **Where it lands** `delivery.people`, `delivery.days_available` → EST · WBS · SCH

---

## Round 1 · Before the PRD — `product-owner`

### 1.1 If this succeeds, which number moves, and from what to what

- **Why ask** — the most commonly failed question. A metric that **cannot go down**
  is not a metric, it is marketing, and it makes project failure undetectable.
- **Good** `Time to book drops from 15 minutes to under 2`
  — **Bad** `Users are happier`
- **Where it lands** `outcome.*` → PRD §4 · the post-release measurement
- **If the baseline is unknown** write `TBD` and note that it has to be measured
  first. Never guess a baseline — a guessed baseline makes every result downstream
  of it meaningless.

### 1.2 What are you explicitly *not* doing this round

- **Why ask** — a scope that only lists what is in is not a scope, because nothing
  holds back growth. The "not doing" list is what lets you say no later without an
  argument.
- **Good** `No payments, no mobile app, no usage reports this round`
  — **Bad** `Not sure yet` (if you are not sure, it is in scope)
- **Where it lands** `scope.out` → PRD §5, non-goals

### 1.3 Who says this is correct

- **Why ask** — every gate needs a decider. Even in solo mode you need to know
  whose criteria apply: the instructor, a hypothetical client, or real users —
  each gives a different answer.
- **Good** `The instructor, against the course rubric` — **Bad** `Me`, with no criteria
- **Where it lands** `scope.approver` → PRD header · used by `/gate`

### 1.4 What constraints cannot move

- **Why ask** — a constraint discovered late forces a redesign, which costs far
  more than knowing at the start.
- **Good** `Must ship by the 30th · must run on mobile · cannot store national ID numbers`
- **Where it lands** `scope.constraints` → PRD §9 · SRS §4

---

## Round 2 · Before planning — `project-manager`

### 2.1 After leave, meetings and other coursework, how many working days are actually left

- **Why ask** — the raw number and the real number differ by roughly half. Plans
  built on the raw number fail every time, and the planner usually blames the team
  for being slow when they are in fact measuring their own arithmetic.
- **Good** `8 weeks × 5 days = 40, minus 5 for midterms, so 35 days at 3 hours`
- **Where it lands** `delivery.days_available` → EST · SCH · capacity calculation

### 2.2 How long is one iteration

- **Why ask** — you need a rhythm at which you stop and check the forecast against
  reality. Iterations longer than two weeks mean you find out you are behind at the
  point where it is too late to act.
- **Where it lands** `delivery.iteration_length` → WBS · SCH

### 2.3 Is there a deadline that cannot move

- **Why ask** — a fixed deadline changes the prioritisation method entirely, from
  RICE to MoSCoW, because you have to have things ready to cut in advance rather
  than deciding what to drop with three days left.
- **Where it lands** `delivery.hard_deadline` → SCH · the prioritisation method in the PRD

---

## Round 3 · Before system design — `system-analyst`

### 3.1 Where does the data live — on the user's device, on a server, or both

- **Why ask** — this decides more about the architecture than anything else, and it
  cannot be answered after the fact. If the answer is "both", the next question
  follows immediately: what happens when the two disagree.
- **Good** `Server only, users need a connection`
  — **Bad** `In a database` (that does not answer the question)
- **Where it lands** `technical.data_location` → ARC · DM · the subject of an ADR

### 3.2 Does it have to work without a connection

- **Why ask** — "would be nice" is not an answer. Offline requires a sync mechanism,
  which is expensive and nearly impossible to add later.
- **Good** `No`, or `They need to see bookings they already made, but not create new ones`
- **Where it lands** `technical.offline` → ARC · becomes a must-have requirement

### 3.3 What does it integrate with

- **Why ask** — every integration point is a failure point, and integrations are
  underestimated without exception. This includes systems used only for sign-in.
- **Where it lands** `technical.integrations` → SRS dependencies · interface contracts

---

## Round 4 · Before visual design — `full-stack-design`

### 4.1 Is there already a brand, or a color and type guide

- **Why ask** — if there is, it has to be followed. If there is not, someone has to
  decide and record it, rather than letting each screen pick its own colors.
- **Where it lands** `design.brand` → DSN · design tokens

### 4.2 What devices is this primarily used on

- **Why ask** — mobile-first and desktop-first produce different structures.
  Deciding later means doing the work twice.
- **Where it lands** `design.devices` → DSN · breakpoints

### 4.3 Is there an existing design system, or is this from zero

- **Why ask** — extending and starting fresh are different-sized jobs, and token
  collisions with an existing system are very hard to unwind once built on.
- **Where it lands** `design.existing_system` → DSN

---

## Round 5 · Before writing code — `developer`

### 5.1 What language and framework, and why that one

- **Why ask** — the reason matters more than the choice, because it tells you what
  can still change later. "Because it is what I have been taught" is a real and
  honest reason.
- **Where it lands** `technical.stack` → ADR

### 5.2 Is there existing code

- **Why ask** — existing code brings constraints that are written down nowhere.
- **Where it lands** `technical.existing_code` → SRS dependencies

### 5.3 What does it mean for one piece of work to be done

- **Why ask** — this is development's exit gate. Without agreeing it up front,
  "done" comes to mean "I finished typing", which is not the same thing at all.
- **Good** `Tests written · suite passes · accessibility checked · reviewed · docs updated`
- **Where it lands** `build.definition_of_done` → used by `/gate` at G4

---

## Round 6 · Before quality assurance — `quality-assurance`

### 6.1 Which WCAG level applies

- **Why ask** — the level changes what counts as a blocker. The default is AA.
- **Where it lands** `quality.wcag` → the accessibility dimension's criteria

### 6.2 Which browsers and versions are supported

- **Why ask** — without agreeing this first, "it breaks in Safari" becomes an
  argument with no end.
- **Where it lands** `quality.browsers` → the scope of the check

### 6.3 Is there a design to compare against, and which file

- **Why ask** — **no spec is not a PASS.** With no design, the visual dimension
  cannot run, and that has to be recorded as a gap in the report rather than
  quietly passing.
- **Where it lands** `quality.design_reference` → the QA report header

---

## Round 7 · Before releasing — `devops-release`

### 7.1 Where does it deploy to

- **Why ask** — the destination determines the whole procedure, and how far back
  you can roll.
- **Where it lands** `release.target` → REL

### 7.2 If the release breaks, how do you roll back, and how long does it take

- **Why ask** — a rollback plan that has never been tried is not a plan. If this
  cannot be answered, the release cannot go ahead — not "ship it and work it out".
- **Where it lands** `release.rollback` → REL · a hard requirement of gate G6

### 7.3 Who presses the button

- **Why ask** — the final gate needs a person's name. "The team" is not a name.
- **Where it lands** `release.approver` → REL
