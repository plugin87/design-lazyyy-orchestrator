---
name: document-control
description: Own the controlled-document system every role in this pipeline writes into — document codes, revision numbering, the register, cross-document consistency, and building Thai-formatted PDF/DOCX from Markdown. Use this skill whenever a document is created, renumbered, revised, or released; whenever the user asks about document codes (PRD-XXX-001), revision numbers, the document register, "which documents exist", "how do I issue a revision", "why is my diagram showing as raw code in the PDF", or Thai government document formatting; and whenever a change to one document requires sweeping the others for stale references. Do NOT use it to decide the CONTENT of a document — the owning role skill (product-owner, system-analyst, quality-assurance, developer, code-reviewer, devops-release) writes the content; this skill governs identity, numbering, and production.

---

# Document Control

Every deliverable in this pipeline is a controlled document. That means it has a
code, a revision number, and a register entry — and that a change to one
document is not finished until every document that references it has been
swept.

This exists for one reason: the roles hand work to each other by requirement ID.
When the codes drift, the handoff silently stops meaning anything, and nobody
notices until someone builds the wrong thing.

## Document codes

Format `<TYPE>-<CODE>-<SEQ>`

- `TYPE` — from the registry below. Fixed set. Do not invent types.
- `CODE` — three uppercase letters from `meta.code` in `project/project.yml`.
- `SEQ` — three digits, starting at `001`. A second document of the same type in
  the same project takes `002` (a re-estimate after design is `EST-XXX-002`, not
  a revision of `EST-XXX-001` — different document, different question).

Templates ship with `XXX` as the code placeholder. Substituting it is the first
thing `/doc-new` does; a document still containing `XXX` has not been created
properly.

## Registry of document types

Every type resolves to a template. `/doc-new` copies from these paths, all
relative to `.claude/skills/`.

| Stage | Type | Document | Template |
|---|---|---|---|
| product | `PRD` | เอกสารข้อกำหนดผลิตภัณฑ์ | `product-owner/assets/prd-template.md` |
| product | `REQ` | ข้อกำหนดความต้องการและเกณฑ์การยอมรับ | `product-owner/assets/req-template.md` |
| product | `EST` | การประมาณปริมาณงานและทะเบียนความเสี่ยง | `project-manager/assets/est-template.md` |
| product | `WBS` | โครงสร้างการแบ่งงานและรอบการทำงาน | `project-manager/assets/wbs-template.md` |
| product | `SCH` | กำหนดการโครงการ | `project-manager/assets/sch-template.md` |
| product | `TRN` | เอกสารส่งมอบงานให้นักวิเคราะห์ระบบ | `product-owner/assets/trn-template.md` |
| analysis | `SRS` | ข้อกำหนดซอฟต์แวร์และการออกแบบระบบ | `system-analyst/assets/srs-template.md` |
| analysis | `ARC` | สถาปัตยกรรมระบบ | `system-analyst/assets/arc-template.md` |
| analysis | `DM` | แบบจำลองข้อมูล | `system-analyst/assets/data-model-template.md` |
| analysis | `NAV` | ผังการไหลของหน้าจอ | `system-analyst/assets/nav-template.md` |
| analysis | `DAY` | กลไกเฉพาะที่กฎซับซ้อน | `system-analyst/assets/mechanism-template.md` |
| analysis | `TST` | กรณีทดสอบจากเกณฑ์การยอมรับ | `system-analyst/assets/test-case-template.md` |
| analysis | `CR` | คำขอเปลี่ยนแปลงเอกสาร | `system-analyst/assets/change-request-template.md` |
| design | `DSN` | ระบบออกแบบและข้อกำหนดหน้าจอ | `design-systems-architecture/assets/dsn-template.md` |
| review | `RVW` | รายงานผลการทบทวนโค้ด | `code-reviewer/assets/review-report-template.md` |
| quality | `QAR` | รายงานผลการประกันคุณภาพ | `quality-assurance/assets/qa-report-template.md` |
| release | `REL` | บันทึกการปล่อยของและแผนถอยกลับ | `devops-release/assets/release-record-template.md` |

Supporting templates that are not standalone controlled documents — an ADR lives
inside `ARC`, a story inside `REQ`, and the rest are working artifacts rather
than deliverables:

`system-analyst/assets/` — `adr-template.md` · `interface-contract-template.md`
· `traceability-matrix-template.md` · `design-handback-checklist.md` ·
`product-owner/assets/story-template.md` ·
`project-manager/assets/` — `sprint-plan-template.md` ·
`risk-register-template.md` · `status-update-template.md` ·
`developer/assets/definition-of-done.md` ·
`devops-release/assets/release-checklist.md` ·
`quality-assurance/assets/qa-checklist.md`

`DAY` is the odd one — it exists for a computation whose rules are too intricate
to bury inside the SRS (date arithmetic, pricing rules, scheduling logic). Use it
when a mechanism needs its own flowchart and its own test cases; skip it when it
does not. The type code is kept as `DAY` for continuity even when the mechanism
has nothing to do with dates.

## Where documents live

```
project/1-product/   PRD REQ EST WBS SCH TRN
project/2-analysis/  SRS ARC DM NAV DAY TST CR
project/3-design/    DSN
project/4-build/     (โค้ด · ไม่มีเอกสารควบคุมประจำระยะ)
project/5-quality/   RVW QAR
project/6-release/   REL
```

Edit the `.md` only. The `.pdf` and `.docx` are generated and overwritten on
every build — an edit made there is lost, silently.

## The control header

Every document opens with this block. It is what `build-docs.sh` uses to find
documents, so the pipe-table format is load-bearing, not decoration.

```markdown
| รายการ | รายละเอียด |
|---|---|
| รหัสเอกสาร | PRD-XXX-001 |
| ฉบับแก้ไขครั้งที่ | 00 |
| วันที่มีผลบังคับใช้ | YYYY-MM-DD |
| สถานะ | ร่าง / รอทบทวน / อนุมัติแล้ว |
| เอกสารอ้างอิง | — |
| ผู้จัดทำ | [ชื่อ] |
```

## Issuing a revision

A substantive change requires all four steps. Doing three of them produces a
document that lies about its own history.

1. เพิ่มเลขฉบับแก้ไขในหัวควบคุม และปรับวันที่มีผลบังคับใช้
2. บันทึกลงตารางประวัติการแก้ไข — ข้อที่แก้ · สาระสำคัญ · เหตุผล
3. ประเมินผลกระทบต่อขอบเขต ปริมาณงาน และตัวชี้วัด แล้วสรุปไว้ในเอกสาร
4. สร้าง `.pdf` และ `.docx` ใหม่ให้ตรงกับต้นฉบับ

Spelling, punctuation, and formatting fixes are not substantive. They do not get
a revision number.

**A revision is not a rewrite of history.** The previous revision's content stays
in the revision table. A student who deletes the old row to make the document
look cleaner has destroyed the only record of what was decided and why.

## Sweeping for stale references

When a requirement ID or document code changes in a source document, every
downstream document that quoted it is now wrong. Sweep in this order — each
method catches what the previous one misses:

1. `grep -rn "<รหัสเดิม>" project/` — direct hits
2. `grep -rn "ข้อ [0-9]" project/2-analysis/` — section-number citations, which
   break when sections are renumbered even though the code did not change
3. Read the traceability matrix end to end — an ID that appears in the matrix but
   nowhere else means a requirement lost its implementation
4. Read the revision tables — a downstream document at a revision older than the
   source document it cites has not absorbed the change yet
5. Read the register — a document listed at a revision that does not match its
   own header means someone edited without registering

Method 1 alone feels sufficient and never is.

## The register

`project/REGISTER.md` lists every document, its current revision, and its status.
Update it in the same edit that creates or revises a document — a register
updated later is a register that is wrong in between.

```markdown
# ทะเบียนเอกสารควบคุม

| รหัสเอกสาร | ชื่อเอกสาร | ฉบับแก้ไข | สถานะ | ปรับปรุงล่าสุด |
|---|---|---|---|---|
```

## Building PDF and DOCX

```sh
brew install pandoc
npm install --prefix tools @mermaid-js/mermaid-cli

bash tools/build-docs.sh              # ทุกฉบับที่มีหัวควบคุม
bash tools/build-docs.sh SRS-XXX-001  # เฉพาะฉบับที่ระบุ
```

**Mermaid blocks must be rendered to images first.** pandoc does not convert
` ```mermaid ` blocks — sent through raw, the diagram appears as source code in
the delivered PDF, which is worse than having no diagram. `build-docs.sh` calls
`render-mermaid.py` first for exactly this reason. Never bypass it.

Known limits, worth stating to the student rather than letting them discover:

- PDF has no page numbers or footers — the headless-Chrome path cannot set page
  margins content. If the assignment requires them, open the `.docx` and add
  them there.
- The `.docx` uses pandoc's default font, not Sarabun. Set it in the word
  processor, or build a `reference.docx`.
- Output is `.docx`, not `.doc`. Convert with
  `textutil -convert doc <file>.docx` if a `.doc` is genuinely required.

## Thai formatting

Defined in `docs/print-th.css` — Sarabun 16pt body, 14pt tables, A4, margins per
Thai official document regulation (top 25mm, bottom 20mm, left 30mm, right 20mm).
Sarabun is one of the national fonts designated by the 2010 cabinet resolution.

Document body text is Thai. The templates in each skill's `assets/` carry English
headings as structural scaffolding — translate the headings when writing the
actual document, and keep the numbering.

## Flowchart symbols

Flowcharts follow ISO 5807:

| สัญลักษณ์ | ความหมาย | mermaid |
|---|---|---|
| แคปซูล | จุดเริ่มต้นและจุดสิ้นสุด | `(["ข้อความ"])` |
| สี่เหลี่ยมด้านขนาน | นำเข้าและส่งออก | `[/"ข้อความ"/]` |
| สี่เหลี่ยมผืนผ้า | การประมวลผล | `["ข้อความ"]` |
| สี่เหลี่ยมผืนผ้าเส้นข้างคู่ | กระบวนการที่กำหนดไว้แล้ว | `[["ข้อความ"]]` |
| สี่เหลี่ยมข้าวหลามตัด | การตัดสินใจ | `{"ข้อความ"}` |

Labels are written in human language, not variable names; put the technical
names in a lookup table under the diagram. Each branch ends at its own terminator
— do not run long edges back to a single shared end node.

## Anti-patterns to catch

- Document created by copying another and forgetting to change the code
- Revision number bumped without a revision-table row
- `.docx` edited directly, then overwritten by the next build
- Requirement renumbered in the source and not swept downstream
- Register showing a revision the document itself does not claim
- `XXX` still sitting in a document code
