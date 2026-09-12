#!/usr/bin/env bash
# Package a distributable handoff set
#
# Usage
#     bash tools/make-handoff.sh                    every document that exists
#     bash tools/make-handoff.sh SRS ARC DM TST     only the named types
#
# Rebuilds every document first, then collects the PDF and DOCX files into handoff/
# along with a contents listing telling the recipient where to start reading.
#
# The listing is built from the actual source files rather than a hardcoded list,
# so a newly added document appears in the set without editing this script.

set -euo pipefail
cd "$(dirname "$0")/.."

SRC_DIR="project"
[ -d "$SRC_DIR" ] || { echo "No $SRC_DIR directory — run /kickoff to start a project first"; exit 1; }

echo "Rebuilding every document"
bash tools/build-docs.sh

rm -rf handoff
mkdir -p handoff

# Pull a value out of the source file's control header.
# An unfilled field still lists every option separated by / — collapse that to a marker.
field() {
  local v
  v=$(grep -m1 "| $2 |" "$1" | sed 's/.*| \([^|]*\) |[[:space:]]*$/\1/' | xargs)
  case "$v" in *" / "*) echo "not set" ;; *) echo "$v" ;; esac
}
title() { grep -m1 '^# ' "$1" | sed 's/^# //'; }

# Collect documents carrying a control header, ordered by stage folder
DOCS=()
while IFS= read -r F; do DOCS+=("$F"); done < <(
  grep -rlE '^\| รหัสเอกสาร \| [A-Z]{2,4}-[A-Z]+-[0-9]+ \|' "$SRC_DIR" --include='*.md' 2>/dev/null | sort || true
)
[ ${#DOCS[@]} -gt 0 ] || { echo "No documents to hand off"; exit 0; }

# Filter to the named types, if any were given
if [ $# -gt 0 ]; then
  FILTERED=()
  for F in "${DOCS[@]}"; do
    CODE=$(basename "$F" .md)
    for WANT in "$@"; do
      [[ "$CODE" == "$WANT"-* || "$CODE" == "$WANT" ]] && FILTERED+=("$F") && break
    done
  done
  DOCS=("${FILTERED[@]}")
fi

# Strip the trailing YAML comment too, or the field's own explanation comes with the value
PROJECT=$(grep -m1 '^  name:' "$SRC_DIR/project.yml" 2>/dev/null \
  | sed -e 's/^  name:[[:space:]]*//' -e 's/[[:space:]]*#.*$//' | xargs || true)

{
  echo "Handoff set${PROJECT:+  ·  project: $PROJECT}"
  echo "Generated $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "Contents — every document is provided as both PDF and DOCX"
  echo
  for F in "${DOCS[@]}"; do
    CODE=$(basename "$F" .md)
    printf '  %-14s rev %-4s %-8s %s\n' \
      "$CODE" "$(field "$F" 'ฉบับแก้ไขครั้งที่')" "$(field "$F" 'สถานะ')" "$(title "$F")"
    for EXT in pdf docx; do
      [ -f "docs/$CODE.$EXT" ] && cp "docs/$CODE.$EXT" handoff/
    done
  done
  echo
  echo "Notes"
  echo
  echo "  Edit the .md files under $SRC_DIR only."
  echo "  The files in this set are regenerated on every revision; edits here are lost."
  echo
  echo "  Unresolved questions and unconfirmed assumptions are listed at the end"
  echo "  of each document. Read them before relying on any of this."
} > handoff/README.txt

echo
echo "Handoff set is in handoff/"
ls -1 handoff | sed 's/^/  /'
