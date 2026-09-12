#!/usr/bin/env bash
# auto — one command: open the room, run the whole pipeline, stop on a verdict.
#
#   bash tools/auto.sh --brief "..."   take a brief, run the pipeline for real
#   bash tools/auto.sh                 continue a project that already has one
#   bash tools/auto.sh --demo          replay the recorded run instead
#   bash tools/auto.sh --no-open       do not open a browser
#
# The loop is the correcter's, not this script's. `verify.py` returns 0/1/2 and
# that is the only thing allowed to decide whether the work stands — this file
# just keeps calling until it says so, and stops when it says stop.
set -uo pipefail
cd "$(dirname "$0")/.."

PORT=4173
OPEN=1
DEMO=0
BRIEF=""
while [ $# -gt 0 ]; do
  case "$1" in
    --demo)    DEMO=1 ;;
    --no-open) OPEN=0 ;;
    --port)    shift; PORT="${1:-4173}" ;;
    --brief)   shift; BRIEF="${1:-}" ;;
    *)         [ -z "$BRIEF" ] && BRIEF="$1" ;;
  esac
  shift
done

say() { printf '\n\033[36m▶ %s\033[0m\n' "$*"; }

# `project/` is a symlink into a workspace that usually sits outside this repo.
# Writing through it resolves to a path Claude Code has not been granted, so in
# headless mode the run stops dead on a permission prompt nobody can answer.
# --add-dir grants the workspace up front. Without this the pipeline hangs.
WORKSPACE="$(readlink project 2>/dev/null)"
WORKSPACE="$(cd "$(dirname "${WORKSPACE:-.}")" 2>/dev/null && pwd)"
ADD_DIR=()
[ -n "$WORKSPACE" ] && [ -d "$WORKSPACE" ] && ADD_DIR=(--add-dir "$WORKSPACE")

# ── the room ───────────────────────────────────────────────────────────────
# A monitor that is already up is very likely the one that launched this script
# (the run button spawns it), so killing "the old server" would kill the caller
# and orphan the run. Reuse a healthy one instead; only replace a dead port.
ROOM=""
if curl -sf -m 2 "http://localhost:$PORT/state" >/dev/null 2>&1; then
  say "ใช้ห้องที่เปิดอยู่แล้วที่พอร์ต $PORT"
  REUSED=1
elif lsof -ti :$PORT >/dev/null 2>&1; then
  say "พอร์ต $PORT ถูกยึดไว้แต่ไม่ตอบสนอง — ปิดทิ้ง"
  lsof -ti :$PORT | xargs kill 2>/dev/null
  sleep 1
  REUSED=0
else
  REUSED=0
fi

if [ "${REUSED:-0}" = 1 ]; then
  :
elif [ "$DEMO" = 1 ]; then
  say "เปิดห้องโหมดเล่นซ้ำ"
  node tools/monitor/server.mjs --replay .monitor/sample-run.jsonl --speed 1.4 --port "$PORT" --allow-run &
  ROOM=$!
else
  say "เปิดห้องโหมดสด"
  mkdir -p .monitor
  : > .monitor/events.jsonl
  node tools/monitor/server.mjs --port "$PORT" --allow-run &
  ROOM=$!
fi
# only tear down a room this script actually opened
[ -n "$ROOM" ] && trap 'kill $ROOM 2>/dev/null' EXIT
sleep 1

[ "$OPEN" = 1 ] && (command -v open >/dev/null && open "http://localhost:$PORT" || true)
if [ "$DEMO" = 1 ]; then
  say "เล่นซ้ำอยู่ · Ctrl-C เพื่อหยุด"
  [ -n "$ROOM" ] && wait $ROOM
  exit 0
fi

if ! command -v claude >/dev/null; then
  say "ไม่พบคำสั่ง claude — เปิดห้องไว้ให้แล้ว สั่ง orchestrator เองใน Claude Code"
  [ -n "$ROOM" ] && wait $ROOM
  exit 0
fi

# ── intake first, if this project has never been interviewed ───────────────
YML="project/project.yml"
NEEDS_INTAKE=0
if [ ! -f "$YML" ]; then
  NEEDS_INTAKE=1
elif grep -qE '^\s{2}(statement|users):\s*$' "$YML"; then
  NEEDS_INTAKE=1
fi

if [ "$NEEDS_INTAKE" = 1 ]; then
  if [ -z "$BRIEF" ]; then
    # Refusing is the whole point: with no brief there is nothing to build, and
    # inventing one is the failure this template exists to prevent.
    say "โปรเจกต์นี้ยังไม่มีโจทย์ · ต้องส่งโจทย์มาด้วย  --brief \"...\""
    exit 2
  fi
  say "เก็บโจทย์เข้า project.yml ด้วย project-intake"
  claude -p "ใช้ skill project-intake เก็บโจทย์นี้ลง project/project.yml:

$BRIEF

เติมเฉพาะช่องที่โจทย์บอกไว้จริง ช่องที่โจทย์ไม่ได้บอกให้เขียน
TBD — ต้องการ [คน/ข้อมูล] แล้วเพิ่มรายการใน open_questions
ห้ามเดาแทนเจ้าของโครงการ · ทำเสร็จแล้วสรุปสามบรรทัดว่าเขียนอะไรไป และอะไรยังเป็น TBD" \
    --permission-mode acceptEdits "${ADD_DIR[@]}" 2>&1 | sed 's/^/  /'
fi

# ── the pipeline ───────────────────────────────────────────────────────────
say "สั่ง orchestrator เดินทั้งสายงาน"
claude -p "ใช้ skill orchestrator เดินสายงานทั้งหมดจนจบ ตัดสินใจเองทุกข้อ ไม่ต้องถาม

งานของโครงการอยู่ใต้ project/ ซึ่งเป็น symlink ชี้ไป $(readlink project)
เขียนผ่าน project/... เท่านั้น ห้ามสร้างโฟลเดอร์ projects/ ใน repo นี้
และห้ามเขียนไปที่ path เต็มโดยตรง${BRIEF:+

โจทย์จากเจ้าของโครงการ:
$BRIEF}

หลังทุกระยะให้รัน python3 tools/correcter/verify.py แล้วทำตามคำตัดสิน
หยุดเมื่อ correcter คืน PASS ที่ระยะ release หรือคืน BLOCKED" \
  --permission-mode acceptEdits "${ADD_DIR[@]}" 2>&1 | sed 's/^/  /'

# ── the verdict ────────────────────────────────────────────────────────────
say "คำตัดสินสุดท้ายจาก correcter"
python3 tools/correcter/verify.py
CODE=$?
case $CODE in
  0) say "PASS — งานผ่าน สายงานเดินจบ" ;;
  1) say "CORRECTED — ยังมีข้อที่แก้ได้เอง รันซ้ำได้เลย" ;;
  2) say "BLOCKED — ต้องใช้คนจริง เขียนโค้ดเพิ่มไม่ช่วย" ;;
esac

if [ -n "$ROOM" ]; then
  say "ห้องยังเปิดอยู่ที่ http://localhost:$PORT · Ctrl-C เพื่อปิด"
  wait $ROOM
else
  say "จบแล้ว · ห้องที่เปิดอยู่ก่อนหน้ายังทำงานต่อ"
fi
