---
name: orchestrator
description: Run the whole six-stage pipeline autonomously, making every decision without asking, then hand the result to the correcter which decides whether the work may stand. Use this skill when the user wants the project driven end to end without being asked at each step — "ทำให้จบเลย", "รันทั้งสายงาน", "ตัดสินใจแทนได้เลย", "orchestrate the whole thing", "run it autonomously". Also use it to resume an autonomous run that the correcter stopped, and to add new checks to the correcter. Do NOT use it to do the work of one role — invoke that role's skill directly (product-owner, system-analyst, developer, code-reviewer, quality-assurance, devops-release).
---

# Orchestrator

Runs the pipeline without asking, and is not trusted to say whether its own
output is correct. Those two sentences are the whole design.

An autonomous agent that both produces work and certifies it has no way to
notice its own blind spot. So certification is taken away from it and given to
`tools/correcter/`, which is deterministic code — it does not read intent,
does not weigh arguments, and cannot be persuaded.

## The loop

```
เลือกระยะถัดไปจาก stage ใน project.yml
  → ทำงานของบทบาทนั้นตาม skill ของมัน
  → บันทึกทุกการตัดสินใจลง decision log
  → รัน python3 tools/correcter/verify.py
      ├ รหัส 0  PASS       เลื่อน stage แล้ววนต่อ
      ├ รหัส 1  CORRECTED  รันคำสั่งแก้ที่ correcter บอก แล้วตรวจซ้ำ
      └ รหัส 2  BLOCKED    หยุด รายงาน ห้ามเดินต่อ
```

**วนได้ไม่เกินสามรอบต่อระยะ** ถ้ารอบที่สามยังไม่ PASS ให้ถือว่า BLOCKED
เพราะการแก้แล้วตรวจซ้ำที่ไม่ลู่เข้า แปลว่าปัญหาไม่ได้อยู่ตรงที่กำลังแก้

### ขั้นที่ห้ามข้าม — การทบทวนอิสระก่อนปิดระยะ build

`correcter` จับได้เฉพาะสิ่งที่มีคนคิดจะเขียนตัวตรวจไว้แล้ว
มันไม่มีทางจับสิ่งที่ผู้เขียนมองไม่เห็นตั้งแต่แรก เพราะตัวตรวจก็เขียนโดยคนเดียวกัน

ก่อนปิดระยะ `build` ต้องเรียกสองบทบาทนี้เป็น subagent เสมอ

```
Agent(subagent_type: "code-reviewer",     prompt: <โค้ด + SRS · ไม่มีเหตุผลของผู้เขียน>)
Agent(subagent_type: "quality-assurance", prompt: <ระบบ + PRD SRS DSN · ไม่มีเจตนาของผู้สร้าง>)
```

**ห้ามส่งบทสนทนาของ orchestrator ต่อไปให้สองตัวนี้** ส่งเฉพาะของที่ต้องตรวจ
กับสเปกที่ใช้เทียบ · ผู้ทบทวนที่เห็นเหตุผลของผู้เขียน จะถูกเหตุผลนั้นโน้มน้าว
แล้วหยุดเป็นผู้ทบทวน

**เมื่อทั้งสองคืนข้อค้นพบ ให้ยืนยันข้อร้ายแรงด้วยตัวเองก่อนรับ** — รันคำสั่งที่มันบอก
อย่ารับเพราะมันเขียนมาน่าเชื่อ และอย่าปฏิเสธเพราะมันขัดกับสิ่งที่เพิ่งรายงานไป

**ทุกข้อบกพร่องชนิดใหม่ที่มันเจอ ต้องกลายเป็นตัวตรวจใน `correcter`** ไม่งั้นรอบหน้า
ก็ต้องพึ่งโชคว่าจะมีใครสังเกตอีก

## ข้อจำกัดที่ต้องรู้ก่อนใช้

**`.claude/agents/` ถูกอ่านตอนเริ่ม session เท่านั้น** — subagent ที่เพิ่งสร้าง
จะยังเรียกไม่ได้จนกว่าจะเริ่ม session ใหม่ เรียกแล้วจะได้ `Agent type not found`

ทางแก้ชั่วคราวถ้าจำเป็นต้องรันในรอบเดียวกับที่สร้าง — เรียก `general-purpose`
แล้วฉีดนิยามบทบาทเข้าไปในคำสั่ง · **ยังได้การแยกคอนเท็กซ์ ซึ่งเป็นคุณสมบัติหลัก**
แต่ไม่ได้ allowlist ของเครื่องมือ จึงต้องเขียนข้อห้ามลงในคำสั่งแทน
และข้อห้ามที่เขียนไว้ในคำสั่ง อ่อนกว่าข้อห้ามที่บังคับด้วยเครื่องมือเสมอ

## กติกาที่ทำให้ระบบนี้เชื่อถือได้

### 1. ตัดสินใจได้ทุกอย่าง แต่ต้องบันทึกทุกอย่าง

ทุกการตัดสินใจที่ทำแทนเจ้าของโครงการ ลงในตารางบันทึกการตัดสินใจของเอกสารนั้น
พร้อม **ชั้นของหลักฐาน** สามชั้นเดียวกับที่ correcter ใช้

| ชั้น | หมายถึง | ตัวอย่าง |
|---|---|---|
| `VERIFIED` | มีความจริงให้เทียบ และเทียบแล้ว | เทสต์ผ่าน · อัตราส่วนความต่างสีคำนวณได้ |
| `ASSERTED` | ยังไม่มีความจริงให้เทียบ | ค่าฐาน 180 วินาที · ท่านี้ปลอดภัย |
| `INFERRED` | อนุมานจากสิ่งที่เจ้าของโครงการพูด | "แค่ดูท่าทาง" ⇒ ไม่มีระบบนับเซ็ต |

**ห้ามเขียนข้ออ้างชั้น `ASSERTED` โดยไม่ติดป้าย** นี่คือกติกาข้อเดียวที่ถ้าพัง
แล้วทั้งระบบพังตาม เพราะทุกอย่างปลายน้ำจะดูน่าเชื่อถือทั้งที่ไม่มีฐานรองรับ

### 2. BLOCKED แปลว่าหยุด ไม่ใช่แปลว่าหาทางอ้อม

`correcter` คืน BLOCKED เมื่อมีข้ออ้างที่ **ไม่มีความจริงในโลกให้เทียบ**
กำลังค้ำประตูอยู่ เช่นท่าออกกำลังกายที่ยังไม่มีผู้เชี่ยวชาญรับรอง

เมื่อเจอ BLOCKED ให้ทำสามอย่างนี้ ตามลำดับ

1. ทำงานที่เหลือ **ทุกอย่าง** ที่ไม่ขึ้นกับสิ่งที่ถูกบล็อกให้จบก่อน
2. เตรียมของให้คนที่ต้องมาตัดสินใช้งานได้ทันที เช่นแบบตรวจ เครื่องมือวัด จดหมายนำ
3. รายงานว่าเหลืออะไร ใครต้องทำ และทำไมระบบทำแทนไม่ได้

**สิ่งที่ห้ามทำ** — เติมค่าที่ยังไม่รู้เพื่อให้ผ่าน · ปิดตัวตรวจ · เปลี่ยนเกณฑ์
ให้ต่ำลงจนผ่าน · ตีความ BLOCKED ว่าเป็นคำแนะนำ

### 3. ประตูที่ดีคือสคริปต์ ไม่ใช่การพิจารณา

เมื่อพบข้อบกพร่องชนิดใหม่ อย่าแก้ที่ผลอย่างเดียว **ให้เพิ่มตัวตรวจใน
`tools/correcter/checks.py` ด้วย** เพื่อให้รอบหน้าไม่ต้องอาศัยความจำของใคร

การตรวจในรอบก่อนพบข้อบกพร่องสามอย่างที่โมเดลซึ่งมีบริบทครบยังพลาด —
การอ้างเลขฉบับเก่า 30 จุด · รหัสกรณีทดสอบที่ไม่มีเทสต์ 5 รหัส · ตัวเลขขัดกัน
ทั้งสามอย่างเป็นงานกลไกล้วน และทั้งสามอย่างถูกข้ามเพราะกำลังคิดเรื่องอื่นอยู่

## ระยะและเงื่อนไขเลื่อน

| stage | ทำอะไร | เลื่อนเมื่อ |
|---|---|---|
| `intake` | project-intake | project.yml ครบ · G1 ผ่าน |
| `product` | product-owner · project-manager | PRD EST WBS SCH · G1 ผ่าน |
| `analysis` | system-analyst | SRS · G2 ผ่าน |
| `design` | full-stack-design | DSN · G3 ผ่าน |
| `build` | developer | โค้ด · G4 ผ่าน |
| `review` | code-reviewer | RVW · G5 ผ่าน |
| `quality` | quality-assurance | QAR |
| `release` | devops-release | REL · G6 ผ่าน |

**เลื่อน `stage` ได้ก็ต่อเมื่อ correcter คืน PASS เท่านั้น** ประตูที่ผ่านเพราะ
ผู้ทำงานคิดว่าผ่าน ไม่ใช่ประตู

## เมื่อเจ้าของโครงการสั่งให้เติมช่องว่างเอง

เกิดขึ้นได้ และทำได้ แต่ต้องทำแบบนี้

- เติมด้วยค่าที่สมเหตุสมผล **และติดป้าย `[สมมติ A-xx]` ในเนื้อเอกสารทุกจุดที่ใช้**
- ลงทะเบียนใน `assumptions` ของ project.yml พร้อมระบุว่าสมมติขึ้น ไม่ใช่รู้จริง
- เขียนตารางว่าถ้าข้อสมมติผิดแล้วจะเกิดอะไร และพิสูจน์อย่างไร
- **correcter จะยังคืน BLOCKED อยู่ดี ถ้าข้อสมมตินั้นค้ำประตู** — ซึ่งถูกแล้ว
  เอกสารเดินต่อได้ แต่การปล่อยสู่ผู้ใช้จริงเดินต่อไม่ได้

การเติมช่องว่างทำให้ **งานเดินต่อ** ไม่ได้ทำให้ **ข้ออ้างเป็นจริง**

## การเพิ่มตัวตรวจ

```python
def check_something() -> list[Claim]:
    ...
    return [Claim(
        id="ABC-01",
        text="สิ่งที่อ้าง",
        level=Level.VERIFIED,          # ต้องมี evidence เสมอ ไม่งั้นโยน ValueError
        evidence="คำสั่งที่รันซ้ำได้",
        fix="คำสั่งที่แก้เองได้ ถ้ามี",
        blocks_gate="G6",              # ใส่เมื่อชั้นเป็น ASSERTED และมันค้ำประตูอยู่
    )]
```

แล้วเพิ่มเข้า `ALL` ท้ายไฟล์

**ชั้น `VERIFIED` ที่ไม่มี `evidence` จะโยนข้อผิดพลาดทันที** ตั้งใจให้เป็นแบบนั้น
เพราะการเขียนว่าตรวจแล้วโดยไม่บอกว่าตรวจด้วยอะไร คือรูปแบบที่พบบ่อยที่สุด
ของการยืนยันที่ยืนยันไม่ได้

## ไฟล์ที่เกี่ยวข้อง

- `tools/correcter/verify.py` — ตัวตัดสิน · รหัสออก 0 PASS · 1 CORRECTED · 2 BLOCKED
- `tools/correcter/checks.py` — ตัวตรวจแต่ละตัว
- `tools/correcter/claims.py` — นิยามชั้นของข้ออ้างและกฎการตัดสิน
- `tools/correcter/fix_references.py` — ตัวแก้การอ้างฉบับเก่า
