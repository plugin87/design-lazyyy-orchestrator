# mission control

ห้องบัญชาการที่แสดงว่า agent ตำแหน่งไหนกำลังทำอะไรอยู่ — **ตามเหตุการณ์จริง
ใน Claude Code ไม่ใช่แอนิเมชันที่เขียนสคริปต์ไว้**

```sh
node tools/monitor/server.mjs                                   # สด
node tools/monitor/server.mjs --replay .monitor/sample-run.jsonl # เล่นซ้ำ
```

เปิด <http://localhost:4173> แล้วกด **เข้าห้อง** (กดเพื่อให้เบราว์เซอร์ยอมเปิดเสียง)

ไม่มี dependency สักตัว — ใช้ `http` กับ `fs` ของ node ล้วน เพราะบทเรียนที่เริ่มด้วย
`npm install` พังหน้าห้องเรียน คือบทเรียนที่เริ่มไม่ดี

---

## ทำงานยังไง

```
Claude Code ──hooks (async)──▶ emit.py ──▶ .monitor/events.jsonl
                                                    │ tail
                                          server.mjs ──SSE──▶ ห้อง
                                                    │
                                   project/project.yml (stage · G1-G6)
```

`emit.py` มีกฎอยู่ข้อเดียวที่สำคัญกว่าทุกข้อ — **ห้ามคืนค่าที่ไม่ใช่ 0**
เพราะ hook ที่ล้มจะพิมพ์ข้อความผิดพลาดลงในบทสนทนาของนักเรียน
การเสียเฟรมหนึ่งเฟรมของแอนิเมชันนั้นถูก การทำให้ทุกคำสั่งในคาบดูเหมือนพังนั้นแพง

---

## บนจอมาจากไหน

| ที่เห็น | มาจาก |
|---|---|
| โต๊ะสว่างขึ้น | `SubagentStart` — ตำแหน่งนั้นถูกเรียกจริง |
| ชื่อไฟล์บนจอโต๊ะ | `tool_input.file_path` ของ `Write`/`Edit` จริง |
| หน้าบ้าน / หลังบ้าน แยกโต๊ะ | **ตัว path เอง** — `src/` หรือ `server/` |
| ข้อความตอนส่งงาน | `last_assistant_message` จาก `SubagentStop` |
| การ์ดคำตัดสิน | บรรทัดท้ายของ `tools/correcter/verify.py` |
| แถบระยะ · ประตู G1-G6 | `stage:` และ `gates:` ใน `project/project.yml` |
| XP · เลเวล · ผ่านติดกัน | นับจากข้างบนทั้งหมด **ไม่มีตัวเลขที่คิดขึ้นเอง** |

ห้องที่เงียบ แปลว่าสายงานเงียบ — ไม่ใช่ห้องเสีย

---

## เพิ่มตำแหน่งใหม่

แก้ `roster.json` อย่างเดียว ไม่ต้องแตะ CSS หรือ JS

```json
{ "id": "my-role", "name": "MY ROLE", "th": "ชื่อไทย",
  "agent": "ชื่อ agent ใน .claude/agents/", "x": 50, "y": 40, "color": "#7DD3FC" }
```

- `x` `y` เป็นเปอร์เซ็นต์บนฉาก · `y < 50` การ์ดจะเปิดลง · `x < 22` หรือ `> 78` การ์ดชิดขอบ
- ถ้ามีไฟล์ `public/art/crew-<id>.png` จะถูกหยิบมาใช้เอง
- agent ตัวเดียวมีได้หลายโต๊ะ — ใส่ `pathPrefix` แล้วระบบเลือกโต๊ะจาก path ที่มันเขียนจริง

---

## ภาพประกอบ

ทุกไฟล์เป็นของไม่บังคับ ไม่มีก็ยังใช้สอนได้ ระบบตรวจเองว่ามีอะไรบ้าง

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `art/room-bg.png` | ฉากห้อง (เบลอและหรี่ลงเป็นบรรยากาศ) |
| `art/room-empty.png` | ถ้ามี จะถูกใช้แทน — ฉากเปล่าไม่มีจอไม่มีป้าย ดีกว่า |
| `art/crew-<id>.png` | ตัวละครหนึ่งท่า |
| `art/walk-<id>.png` | แถบสองท่า (ก้าวซ้าย·ก้าวขวา) — ถ้ามี ระบบจะสลับเฟรมเป็นวงจรเดินจริง |

`art/CREW-PROMPT.txt` คือคำสั่งสำหรับสร้างตัวละครเต็มตัวแปดตัว

**สร้างภาพยังไง** — เครื่องมือ `image_gen` มีเฉพาะ codex โหมด interactive
`codex exec` เรียกไม่ได้ (ยืนยันแล้วด้วย `tool_search` ที่คืนค่าว่าง)

```sh
codex                      # โหมด interactive แล้ววางเนื้อหาใน CREW-PROMPT.txt
```

หรือถ้ามี `OPENAI_API_KEY` จะสั่งอัตโนมัติทั้งแปดตัวได้เลย

```sh
export OPENAI_API_KEY=...
python3 ~/.codex/skills/.system/imagegen/scripts/image_gen.py generate \
  --model gpt-image-2 --size 1024x1536 --prompt-file <ไฟล์คำสั่งของตัวนั้น> --out art/full-<id>.png
python3 ~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py art/full-<id>.png
```

---

## ห้องไม่ติด ทำยังไง

1. `python3 tools/monitor/emit.py --selftest` — พิสูจน์ว่าตัวรับทำงาน
2. `cat .monitor/events.jsonl` — พิสูจน์ว่า hook ส่งถึงจริง
3. **Claude Code อ่าน hooks ตอนเปิด session** — session ที่เปิดค้างอยู่ตั้งแต่ก่อนแก้
   `.claude/settings.json` จะไม่ส่งอะไรเลย ต้องเปิดใหม่

## ปิดการใช้งาน

ลบก้อน `hooks` ออกจาก `.claude/settings.json` ไม่มีส่วนอื่นของสายงานที่ขึ้นกับ monitor
