# design-lazyyy-skills

A teaching template for the **AI Design System Bootcamp** — 24 Claude Code skills
wired into one pipeline that runs from an idea to a shipped release.

The template is **deliberately empty, but it knows how to ask.** A student clones
it, runs `/kickoff`, answers questions, and their answers fill the document
templates. There is no worked example to copy from, and nothing invents content
on the student's behalf.

---

## Start in five minutes

```sh
git clone git@github.com:plugin87/design-lazyyy-skills.git my-project
cd my-project
claude
```

Then, in Claude Code:

```
/kickoff
```

It asks five questions — project name, a three-letter code, the problem in one
sentence, who the users are and what they do today instead, and how much time
there is.

Answer "I don't know" freely. That gets recorded as `TBD`, not guessed at.

```
/gate            what is missing before you can move on
/doc-new PRD     create the requirements document from its template
/status          where the project stands right now
```

---

## The pipeline

```
intake → what/why → how it's buildable → design → build → review → release
           G1              G2              G3      G4      G5      G6
```

The full flow diagram and every gate's criteria are in [`WORKFLOW.md`](WORKFLOW.md).

---

## The skills

### Core

| Skill | What it does |
|---|---|
| `project-intake` | Interviews the student and writes `project/project.yml`, the shared memory every role reads |
| `document-control` | Document codes, revisions, the register, and building Thai-formatted PDF/DOCX |

### Pipeline roles

| Skill | Answers the question |
|---|---|
| `product-owner` | What are we building, and why |
| `project-manager` | How, and by when |
| `system-analyst` | How is it actually buildable |
| `developer` | Is it built, and is it done |
| `code-reviewer` | Should this code enter the codebase |
| `quality-assurance` | Is it ready to ship |
| `devops-release` | May this build go live now |

### UX/UI and frontend — 15 skills

**Foundations** `design-fundamentals` · `web-accessibility-a11y`
· `design-systems-architecture` · `web-performance-optimization`
· `anti-ai-design-patterns`

**Design** `figma-expert-workflows` · `responsive-universal-design`
· `inclusive-design-patterns`

**Build** `frontend-framework-guide` · `css-styling-pixel-perfect`

**Integrate and ship** `design-to-code-workflow` · `design-tokens-system`
· `component-library-mastery` · `qa-testing-visual-regression`
· `deployment-devops-workflow`

---

## Say this, get that

| When the student says | The skill that runs |
|---|---|
| "start a new project" · "เริ่มโปรเจกต์ใหม่" | `project-intake` |
| "write me a spec" · "what should we build first" | `product-owner` |
| "will we make the deadline" · "how much can we take on" | `project-manager` |
| "design the data model" · "is this spec buildable" | `system-analyst` |
| "why does this look wrong" · "pick a palette" | `design-fundamentals` |
| "set up design tokens" · "sync tokens with Figma" | `design-tokens-system` |
| "start building this" · "is this story done" | `developer` |
| "review my code" · "can I merge this" | `code-reviewer` |
| "check my implementation" · "does it match the design" | `quality-assurance` |
| "can we release" · "how do we roll back" | `devops-release` |
| "how are document codes formed" · "how do I issue a revision" | `document-control` |

Every skill's description ends with a `Do NOT use for… — that is the X skill`
line, so the same question routes to the same skill every time. Unstable routing
means two students ask the same thing and get different answers, which teaches
them the tool cannot be trusted.

---

## Commands

| Command | What it does |
|---|---|
| `/kickoff` | Opens a project, asks the questions, writes `project.yml` |
| `/gate` | Checks the current gate, names what is missing, records the result |
| `/doc-new <TYPE>` | Creates a document from its template, substitutes the project code, registers it |
| `/doc-build` | Builds PDF and DOCX from the `.md` sources |
| `/cr` | Opens a change request when source documents contradict each other |
| `/status` | Summarises where the project stands |

---

## Layout

```
.claude/skills/       24 skills
.claude/commands/     6 commands
project/              the student's work — the only place they edit
  project.yml         shared memory across every role
  REGISTER.md         the document register
  1-product/ … 6-release/
templates/role-skill/ scaffold for adding a new role
tools/                document build and diagram rendering scripts
docs/                 print-th.css, and generated PDF/DOCX
examples/             one brand, three visual systems, as design-system reference
```

---

## Building PDF and DOCX

```sh
brew install pandoc
npm install --prefix tools @mermaid-js/mermaid-cli

bash tools/build-docs.sh              # every document
bash tools/build-docs.sh PRD-BKG-001  # one document
bash tools/make-handoff.sh            # package a handoff set
```

Documents follow Thai official document formatting — Sarabun 16pt body, 14pt
tables, A4, margins per the Thai government correspondence regulation, defined in
`docs/print-th.css`.

**Mermaid blocks are rendered to images first.** Passed to pandoc raw, a diagram
appears as source code in the delivered PDF, which is worse than no diagram —
`build-docs.sh` calls `render-mermaid.py` before every build for exactly this
reason.

---

## Install as a plugin, to use across projects

```
/plugin marketplace add plugin87/design-lazyyy-skills
/plugin install design-lazyyy@design-lazyyy-skills
```

Cloning gives you the skills, commands, templates and tooling. Installing as a
plugin gives you the skills and commands anywhere, but not the `project/`
workspace or the document build scripts.

---

## Adding a role

1. Copy `templates/role-skill/` to `.claude/skills/<role-name>/`
2. The folder name must match `name` in the frontmatter exactly
3. End the `description` with `Do NOT use for… — that is the X skill`, then check
   it against every neighbouring skill
4. Add an `## Intake` section that reads `project.yml` before starting work
5. If the role produces a document, register its type and template path in
   `document-control`
6. If the role owns a gate, add its criteria to `.claude/commands/gate.md`
7. Add it to the tables in `WORKFLOW.md` and this README

The full checklist is in [`templates/role-skill/README.md`](templates/role-skill/README.md).

---

## What this template holds to

**Never invent what you do not know.** An unanswered field becomes
`TBD — ต้องการ [คน/ข้อมูล]`, never a plausible guess. A fabricated requirement is
worse than a blank one, because it gets built.

**A gate must be able to refuse.** A gate that always passes is not a gate.

**Traceability runs both ways.** requirement → design → screen → test case → code,
and back again.

**Report the problem, do not silently fix it.** A contradiction between documents
becomes a change request, not a private decision.

The rules Claude follows in every session are in [`CLAUDE.md`](CLAUDE.md).

---

## A note on language

Everything in the repository is written in English — skills, commands,
documentation, tooling, and commit messages.

Thai survives in exactly one layer: the **document templates** under each skill's
`assets/`, because they become Thai official-format deliverables, and the strings
the tooling has to match against them — the control header row
(`| รหัสเอกสาร |`), the status values, the `TBD — ต้องการ [คน/ข้อมูล]` marker, and
the month labels drawn into the Gantt image. Skill descriptions also keep their
Thai trigger phrases, because that is what students actually type.

---

## License

MIT — see [`LICENSE`](LICENSE)
