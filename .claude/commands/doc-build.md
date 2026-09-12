---
description: Build PDF and DOCX from the .md documents in project/
argument-hint: "[document code, e.g. PRD-BKG-001 — leave empty to build everything]"
allowed-tools: Bash(bash tools/build-docs.sh:*), Bash(npm install --prefix tools:*), Bash(which pandoc:*), Read, Glob
---

Build the delivery documents from their sources.

## Before running

Check the prerequisites. If one is missing, give the install command and stop —
do not start a build that will fail halfway.

- `pandoc` — install with `brew install pandoc`
- `tools/node_modules/.bin/mmdc` — install with
  `npm install --prefix tools @mermaid-js/mermaid-cli`

## Run

```sh
bash tools/build-docs.sh $ARGUMENTS
```

## After running

Report which files were produced, and mention these three the first time a
project is built:

1. Mermaid blocks are rendered to images before pandoc sees them — **if you see
   raw diagram source in the PDF, that step did not run.** Check that `mmdc` is
   actually installed.
2. The PDF has no page numbers or footers. If they are required, add them in the
   `.docx`.
3. The `.docx` uses pandoc's default font, not Sarabun.

## Rule

Edit the `.md` only. The `.pdf` and `.docx` are overwritten on every build, so an
edit made there is lost silently.
