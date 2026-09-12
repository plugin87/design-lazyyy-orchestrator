#!/usr/bin/env bash
# Build controlled documents to PDF and DOCX from the .md sources under project/
#
# Usage
#     bash tools/build-docs.sh              every document carrying a control header
#     bash tools/build-docs.sh SRS-BKG-001  one named document
#
# Prerequisites
#     brew install pandoc
#     npm install --prefix tools @mermaid-js/mermaid-cli
#
# Mermaid blocks are rendered to images under project/assets/ before pandoc sees them.
# Passed through raw they appear as source code in the delivered file, which is unreadable.

set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC_DIR="project"

command -v pandoc >/dev/null || { echo "pandoc not found — install with: brew install pandoc"; exit 1; }
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME"; exit 1; }
[ -x tools/node_modules/.bin/mmdc ] || {
  echo "mmdc not found — install with: npm install --prefix tools @mermaid-js/mermaid-cli"; exit 1; }
[ -d "$SRC_DIR" ] || { echo "No $SRC_DIR directory — run /kickoff to start a project first"; exit 1; }

# Resolve a document code to its source file — documents are spread across stage folders
find_doc() {
  find "$SRC_DIR" -name "$1.md" -not -path '*/assets/*' -print -quit
}

if [ $# -gt 0 ]; then
  DOCS=("$@")
else
  # Find files carrying a control header — a row shaped  | รหัสเอกสาร | ABC-XXX-001 |
  # That shape separates controlled documents from files that merely mention the phrase.
  DOCS=()
  while IFS= read -r F; do DOCS+=("$(basename "$F" .md)"); done < <(
    grep -rlE '^\| รหัสเอกสาร \| [A-Z]{2,4}-[A-Z]+-[0-9]+ \|' "$SRC_DIR" --include='*.md' 2>/dev/null | sort || true
  )
fi

[ ${#DOCS[@]} -gt 0 ] || { echo "No documents to build under $SRC_DIR"; exit 0; }

mkdir -p docs "$SRC_DIR/assets"

for D in "${DOCS[@]}"; do
  SRC=$(find_doc "$D")
  [ -n "$SRC" ] || { echo "Skipping $D — no source file found under $SRC_DIR"; continue; }

  echo "$D"

  if grep -q 'XXX' <<<"$D"; then
    echo "  skipped — the code is still XXX, so the project code was never substituted"
    continue
  fi

  # Step 1 — render mermaid blocks to images, yielding a .md that references them
  python3 tools/render-mermaid.py "$SRC" "/tmp/$D.render.md"

  # Step 2 — PDF via Chrome, which gets Thai line breaking and vowel placement right
  pandoc "/tmp/$D.render.md" -f gfm -t html5 -s --embed-resources \
    --resource-path=".:$PWD" --variable pagetitle="$D" \
    -c docs/print-th.css -o "/tmp/$D.html"
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --virtual-time-budget=12000 --print-to-pdf="docs/$D.pdf" "file:///tmp/$D.html" 2>/dev/null

  # Step 3 — DOCX, embedding the same images
  pandoc "/tmp/$D.render.md" -f gfm --resource-path=".:$PWD" -o "docs/$D.docx"

  REV=$(grep -m1 'ฉบับแก้ไขครั้งที่ |' "$SRC" | sed 's/.*| \([0-9]*\) |.*/\1/')
  echo "  revision ${REV:-unknown} — PDF and DOCX built"
done

echo
echo "Documents are in docs/  ·  diagram images are in $SRC_DIR/assets"
echo "Edit the .md only — .pdf and .docx are overwritten on every build"
