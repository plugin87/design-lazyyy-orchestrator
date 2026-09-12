#!/usr/bin/env bash
# pipeline — drive the six stages, one focused call per role.
#
#   bash tools/pipeline.sh                run every stage that is not done
#   bash tools/pipeline.sh product        run one stage
#
# Why this exists next to auto.sh: handing the whole pipeline to one autonomous
# orchestrator meant it spent its budget reading the repository and never
# reached a role. The sequence is not the interesting decision — it is fixed by
# the gates — so the shell holds it, and each agent gets one job with one
# deliverable and a much smaller thing to read.
set -uo pipefail
cd "$(dirname "$0")/.."

WORKSPACE="$(readlink project 2>/dev/null)"
WORKSPACE="$(cd "$(dirname "${WORKSPACE:-.}")" 2>/dev/null && pwd)"
ADD=(); [ -d "${WORKSPACE:-}" ] && ADD=(--add-dir "$WORKSPACE")

say()  { printf '\n\033[36m▶ %s\033[0m\n' "$*"; }

# Progress the room can show without anybody inventing a number: which stage of
# seven, and when it started. How far through a stage an agent is, is not
# knowable — so it is not claimed.
STAGE_N=0
STAGE_TOTAL=7
# Each role runs as a top-level `claude -p`, not as a subagent, so no
# SubagentStart hook fires and no desk would ever light up — the room looked
# asleep while a role was working. The stage marker carries the role name so the
# room can wake the right character from this instead.
mark() {
  local name="$1" agent="$2" state="${3:-running}"
  [ "$state" = running ] && STAGE_N=$((STAGE_N + 1))
  python3 - "$name" "$agent" "$STAGE_N" "$STAGE_TOTAL" "$state" <<'PY'
import json, sys, time, pathlib
name, agent, n, total, state = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
log = pathlib.Path(".monitor/events.jsonl")
log.parent.mkdir(exist_ok=True)
rec = {"ts": round(time.time(), 3), "kind": "stage", "stage": name, "agent": agent,
       "index": n, "total": total, "state": state}
with log.open("a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
}
warn() { printf '\033[33m  ! %s\033[0m\n' "$*"; }

# One turn as one role. Kept deliberately narrow: the role, the deliverable,
# and the rule that outranks finishing.
# `expect` is the file this stage has to leave behind. Without it a stage that
# died — hit a usage limit, errored, gave up — still reported `done`, the bar
# still read 100%, and the room showed a finished run with three empty stages.
# A gate that always passes is exactly what this pipeline exists to prevent, so
# it must not be built into the pipeline itself.
role() {
  local agent="$1" stage="$2" want="$3" task="$4" expect="${5:-}"
  # Stamped before the role starts, so `expect` can ask whether THIS run wrote
  # the file rather than only whether a file is there. A run whose agents were
  # all killed used to sail through four stages in seconds, reporting `done` on
  # documents a previous run had left behind.
  local started_at; started_at="$(date +%s)"
  mark "$stage" "$agent" running
  say "$stage · $agent → $want  ($STAGE_N/$STAGE_TOTAL)"
  claude -p "คุณคือบทบาท $agent ในสายงานนี้ ทำงานนี้ให้จบในเทิร์นเดียว

$task

กติกาที่สำคัญกว่าการทำให้เสร็จ
- อ่าน project/project.yml ก่อน · project/ เป็น symlink ชี้ไป $(readlink project)
- เขียนผ่าน project/... เท่านั้น ห้ามสร้าง projects/ ใน repo นี้
- ห้ามแก้ tools/correcter/ ไม่ว่ากรณีใด
- ไม่รู้อะไรให้เขียน TBD — ต้องการ [คน/ข้อมูล] แล้วเพิ่มใน open_questions · ห้ามเดา
- **ห้ามค้นหา** · ทุก path ที่ต้องใช้บอกไว้ในโจทย์แล้ว
  ห้ามรัน ls -R, find, หรือ grep -r ทั้ง repo · เปิดเฉพาะไฟล์ที่ระบุชื่อมา
  สองรอบก่อนหน้าใช้เวลาหมดไปกับการค้นหา แล้วไม่ได้ไฟล์สักไฟล์

ปิดท้ายด้วยบรรทัดเดียวว่าสร้างไฟล์อะไรไว้ที่ไหน" \
    --permission-mode acceptEdits "${ADD[@]}" 2>&1 | sed 's/^/    /' | tail -6

  if [ -n "$expect" ] && [ ! -s "$expect" ]; then
    warn "$stage ไม่ได้ผลลัพธ์ · ไม่พบ $expect"
    mark "$stage" "$agent" failed
    FAILED="$FAILED $stage"
    return 1
  fi
  if [ -n "$expect" ]; then
    local touched; touched="$(stat -f %m "$expect" 2>/dev/null || stat -c %Y "$expect" 2>/dev/null || echo 0)"
    if [ "$touched" -lt "$started_at" ]; then
      warn "$stage ไม่ได้แตะ $expect ในรอบนี้ · ไฟล์เป็นของรอบก่อน"
      mark "$stage" "$agent" failed
      FAILED="$FAILED $stage"
      return 1
    fi
  fi
  mark "$stage" "$agent" done
}

gate() {
  say "correcter"
  python3 tools/correcter/verify.py 2>&1 | tail -4
  return "${PIPESTATUS[0]}"
}

# Announce the run itself, not just its stages. Started from the button or from
# a shell, the room has to show the same thing — and the stop control has to be
# offered in both cases, or it lies about what it can do.
runmark() {
  python3 - "$1" "${2:-}" <<'PY'
import json, sys, time, pathlib, os
state, code = sys.argv[1], sys.argv[2]
log = pathlib.Path(".monitor/events.jsonl"); log.parent.mkdir(exist_ok=True)
rec = {"ts": round(time.time(), 3), "kind": "run", "state": state, "pid": os.getppid()}
if code: rec["code"] = int(code)
with log.open("a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
}
FAILED=""
runmark started

# The handler used to announce the end and then fall through, because a bash
# trap does not exit on its own. Pressing stop emitted `run ended code=130`,
# the room showed the run finished, and the pipeline carried on into the next
# stage and started another `claude -p`. The person pressing stop is the person
# trying to stop the spend, so the button lying costs them money.
#
# Kill the whole process group first — the in-flight `claude -p` is a child and
# outlives a plain `exit` — then announce, then leave.
halt() {
  trap - INT TERM
  kill -TERM -$$ 2>/dev/null || true
  sleep 1
  kill -KILL -$$ 2>/dev/null || true
  runmark ended 130
  exit 130
}
trap halt INT TERM

STAGES="${1:-all}"
run_stage() { [ "$STAGES" = all ] || [ "$STAGES" = "$1" ]; }

run_stage product && {
  role product-owner product "PRD" \
    "อ่าน 2 ไฟล์นี้เท่านั้น:
  project/project.yml
  .claude/skills/product-owner/assets/prd-template.md
แล้วเขียน project/1-product/PRD-HWK-001.md ตามโครงของเทมเพลต
ต้องมี user story อย่างน้อย 4 เรื่อง แต่ละเรื่องมีเกณฑ์ยอมรับที่ตรวจได้จริง และมีเส้นทางผิดพลาดอย่างน้อย 1 ข้อต่อเรื่อง
จากนั้นสร้าง project/REGISTER.md จาก .claude/skills/document-control/assets/register-template.md แทน XXX ด้วย HWK และใส่บรรทัดของ PRD-HWK-001" \
    "project/1-product/PRD-HWK-001.md"
}
run_stage analysis && {
  role system-analyst analysis "SRS" \
    "อ่าน 3 ไฟล์นี้เท่านั้น:
  project/project.yml
  project/1-product/PRD-HWK-001.md
  .claude/skills/system-analyst/assets/srs-template.md
แล้วเขียน project/2-analysis/SRS-HWK-001.md
ต้องมีแบบจำลองข้อมูล สถาปัตยกรรมพร้อมเหตุผลที่ปฏิเสธทางเลือกอื่น และตารางตรวจย้อนกลับจากทุกเกณฑ์ยอมรับใน PRD ไปยังรหัสกรณีทดสอบ TC-xx
เติมบรรทัด SRS-HWK-001 ลง project/REGISTER.md" \
    "project/2-analysis/SRS-HWK-001.md"
}
run_stage design && {
  role full-stack-design design "DSN" \
    "อ่าน 3 ไฟล์นี้เท่านั้น:
  project/project.yml
  project/2-analysis/SRS-HWK-001.md
  .claude/skills/design-systems-architecture/assets/dsn-template.md
แล้วเขียน project/3-design/DSN-HWK-001.md
ต้องมีโทเคนสี ตัวอักษร ระยะห่าง และอัตราส่วนความต่างสีเป็นตัวเลขจริงอย่างน้อย 6 คู่ พร้อมตารางสถานะของทุกหน้าจอ
เติมบรรทัด DSN-HWK-001 ลง project/REGISTER.md" \
    "project/3-design/DSN-HWK-001.md"
}
run_stage build && {
  role developer build "โค้ดที่รันได้จริง" \
    "อ่าน 3 ไฟล์นี้เท่านั้น:
  project/project.yml
  project/2-analysis/SRS-HWK-001.md
  .claude/skills/developer/assets/definition-of-done.md
แล้วสร้างแอปจริงใน project/4-build ตาม stack ที่ระบุใน project.yml
ต้องรันคำสั่งเหล่านี้จริงและผ่านจริง ห้ามเขียนแล้วเดาว่าผ่าน:
  npm install
  npm run build
  npm test
มีเทสต์อย่างน้อยเส้นทางหลัก 1 และเส้นทางผิดพลาด 1
ถ้าคำสั่งไหนไม่ผ่าน ให้แก้จนผ่านก่อนจบเทิร์น" \
    "project/4-build/package.json"
}
run_stage review && {
  role code-reviewer review "RVW" \
    "อ่านโค้ดใน project/4-build และ .claude/skills/code-reviewer/assets/review-report-template.md
แล้วเขียน project/5-quality/RVW-HWK-001.md
ระบุความรุนแรงทุกข้อ และปิดท้ายด้วยคำตัดสิน APPROVE หรือ REQUEST CHANGES
คุณแก้โค้ดไม่ได้ · รายงานอย่างเดียว
เติมบรรทัด RVW-HWK-001 ลง project/REGISTER.md" \
    "project/5-quality/RVW-HWK-001.md"
}
run_stage quality && {
  role quality-assurance quality "QAR" \
    "อ่าน project/1-product/PRD-HWK-001.md, โค้ดใน project/4-build, และ .claude/skills/quality-assurance/assets/qa-report-template.md
รันเทสต์จริงด้วย npm test แล้วแนบผลจริงลงรายงาน
เขียน project/5-quality/QAR-HWK-001.md ปิดท้ายด้วย PASS หรือ PASS WITH ADVISORIES หรือ BLOCK
เติมบรรทัด QAR-HWK-001 ลง project/REGISTER.md" \
    "project/5-quality/QAR-HWK-001.md"
}
run_stage release && {
  role devops-release release "REL" \
    "อ่าน project/5-quality/QAR-HWK-001.md และ .claude/skills/devops-release/assets/release-record-template.md
เขียน project/6-release/REL-HWK-001.md
ต้องมีรายการตรวจก่อนปล่อย แผนถอยกลับ และแผนเฝ้าระวังที่ระบุสัญญาณกับเกณฑ์เป็นตัวเลข
เติมบรรทัด REL-HWK-001 ลง project/REGISTER.md" \
    "project/6-release/REL-HWK-001.md"
}

gate
CODE=$?
if [ -n "$FAILED" ]; then
  warn "ระยะที่ไม่ได้ผลลัพธ์:$FAILED"
  warn "อย่าอ่านคำตัดสินข้างล่างว่าเป็นผลของสายงานเต็ม"
fi

case $CODE in
  0) say "PASS — สายงานเดินจบ" ;;
  1) say "CORRECTED — ยังมีข้อที่แก้ได้เอง" ;;
  2) say "BLOCKED — ต้องใช้คนจริง" ;;
esac
runmark ended "$CODE"
say "ไฟล์ที่ได้"
find project/ -type f -not -path '*/.git/*' -not -path '*node_modules*' | sort | sed 's/^/    /'
