# ภาพประกอบของห้องบัญชาการ

ทุกไฟล์ในโฟลเดอร์นี้เป็นของ **ไม่บังคับ** ไม่มีก็ใช้สอนได้ ห้องจะวาดฉากด้วย CSS แทน
ระบบตรวจเองว่ามีไฟล์ไหนบ้าง แล้วหยิบมาใช้อัตโนมัติ

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `room-empty.png` | ฉากห้องเปล่า **ตัวที่ใช้จริง** — ไม่มีจอ ไม่มีป้าย มีแท่น 11 ตัว |
| `room-bg.png` | ฉากเก่าที่มีจอกับป้ายอบมา · ใช้เป็นตัวสำรองถ้าไม่มี `room-empty.png` |
| `crew-<id>.png` | ตัวละครหนึ่งตัว พื้นโปร่ง เต็มตัวเห็นเท้า · `<id>` ต้องตรงกับ `id` ใน `roster.json` |
| `crew-fullbody.png` | แผ่นรวม 8 ตัวที่ยังไม่ตัด · เก็บไว้ตัดใหม่ได้ |
| `walk-<id>.png` | แถบสองท่า (ก้าวซ้าย·ก้าวขวา) · ถ้ามี ระบบจะสลับเฟรมเป็นวงจรเดินจริง |

---

## สร้างฉากใหม่

เครื่องมือสร้างภาพของ `codex exec` **ไม่มี** (ยืนยันแล้วด้วย `tool_search` ที่คืนค่าว่าง)
และ `imagegen` แบบ CLI ต้องใช้ `OPENAI_API_KEY` ซึ่งบัญชีแบบ ChatGPT ไม่มีให้

วิธีที่ใช้ได้จริงคือสร้างในเบราว์เซอร์ แล้วบันทึกลงโฟลเดอร์นี้

### prompt สำหรับฉาก

```
Create one wide 3:2 landscape image, 1536x1024, of an EMPTY futuristic
mission-control command centre interior. Photoreal 3D render, cinematic,
symmetrical eye-level view looking into the room. Dark navy and charcoal
architecture with warm bronze trim, neon rim lighting in cyan and amber, tall
angled windows on both sides showing a dusk city skyline, polished dark stone
floor with faint concentric glowing circles in the middle, a wide staircase and
mezzanine at the back, a few potted plants.

CRITICAL: the room must be COMPLETELY EMPTY of people, and there must be NO
writing of any kind. Absolutely no text, no letters, no numbers, no labels, no
logos, no emblems, no signage anywhere. No holographic screens and no display
panels: every desk surface is bare and dark, and the back wall is a plain dark
panelled wall with soft neon edge lighting and no screen.

Arrange ELEVEN empty raised desk podiums, each a dark rounded platform with a
thin neon light strip around its base, laid out so all eleven are clearly
visible and none overlap: FIVE across the back of the room in a gentle arc, and
SIX across the foreground in a wider arc, with the open glowing floor circle
between the two arcs. Leave clear empty space above and behind each podium so a
standing character can be composited there later.

Moody but not murky: the podiums and the floor must read clearly.
```

**ทำไมต้องย้ำว่าห้ามมีตัวหนังสือ** — รอบแรกที่ไม่ได้ย้ำ ได้ฉากที่มีป้ายชื่อกับจอ
อบมาในภาพ พอวางตัวละครกับการ์ดข้อมูลทับ กลายเป็นอ่านไม่ออกทั้งจอ

---

## สร้างทีมงาน

ขอเป็น **แผ่นรวมหลายตัวในภาพเดียว** ไม่ใช่ทีละตัว เพราะตัวละครในภาพเดียวกัน
จะสไตล์ ขนาด และแสงตรงกัน ส่วนภาพที่สร้างแยกกันจะไม่เข้าชุด

### prompt สำหรับทีมงาน

```
Create one wide 16:9 landscape image. Eight full-body Pixar-style 3D cartoon
characters standing in a single row, evenly spaced, all at the same scale and in
the same neutral standing pose: facing three-quarter front, arms relaxed at
their sides, feet fully visible and flat on the ground, head to toe inside the
frame. Pure flat WHITE background, no floor, no shadow, no text, no labels, no
frames, no circles. Leave a clear white gap between each character.

From left to right:
(1) young man, dark curly hair, glowing blue AR visor glasses, navy-black
    techwear bodysuit with cyan circuit lines
(2) young man, neat dark hair, ornate gold and bronze armour with a compass
    emblem on the chest
(3) young man, wavy brown hair, deep purple cape over dark purple and silver
    armour with a gold emblem
(4) young man, light grey-brown swept hair, blue AR glasses, black technical
    jacket with blue circuit lines
(5) young woman, dark hair in a high ponytail, green goggles pushed up on her
    forehead, green and black tactical suit
(6) young woman, black hair with magenta streaks in a ponytail, magenta and
    purple tech jacket
(7) young man, dark hair, black and green tech armour with a glowing green core
    on the chest
(8) young man, dark hair, navy blazer over a white tee, holding a tablet at his
    side

Bright even lighting, crisp clean edges so every silhouette separates cleanly
from the white background.
```

อยากได้เพิ่มอีกสามตัว (`project-intake` · `document-control` · `devops-release`)
ให้ขอในแชตเดิม ต่อท้ายว่า *"in exactly the same style, framing, lighting and
scale as the previous one"* แล้วบรรยายสามตัวใหม่ — สไตล์จะเข้าชุดกับแปดตัวแรก

---

## ตัดตัวละครออกจากแผ่นรวม

```sh
python3 tools/monitor/cut-crew.py <ไฟล์แผ่นรวม> <id1,id2,id3,...>
```

ตัวตัดคีย์พื้นด้วย **flood fill จากขอบภาพ** ไม่ใช่ลบทุกพิกเซลที่ขาว
เพราะตัวละครมีสีขาวอยู่ในตัว (เสื้อยืด เครื่องหมายถูก) การลบขาวทั้งภาพจะเจาะทะลุ
ส่วนขาวที่ต่อเนื่องกับขอบเท่านั้นที่เป็นพื้นหลังจริง

ถ้าตัวละครยืนชิดกันจนไม่มีช่องขาวคั่น ตัวตัดจะหาจุดที่พิกเซลบางที่สุดแล้วผ่าตรงนั้น

---

## เพิ่มตำแหน่งใหม่เข้าห้อง

แก้ `tools/monitor/roster.json` อย่างเดียว ไม่ต้องแตะ CSS หรือ JS

```json
{
  "id": "my-role",
  "name": "MY ROLE",
  "title": "PRINCIPAL SOMETHING",
  "th": "ชื่อไทย",
  "agent": "ชื่อ agent ใน .claude/agents/",
  "x": 50, "y": 80,
  "color": "#7DD3FC",
  "glyph": "M4 12h16"
}
```

- `x` `y` เป็นเปอร์เซ็นต์บนฉาก · `y < 60` ถือเป็นแถวหลัง ตัวจะเล็กลงตามระยะ
  และการ์ดข้อมูลจะเปิดลงแทนที่จะเปิดขึ้น
- `glyph` คือ `d` ของ `<path>` ใน SVG 24×24 · ขึ้นบนจอโฮโลแกรมประจำโต๊ะ
- agent ตัวเดียวมีได้หลายโต๊ะ — ใส่ `pathPrefix` แล้วระบบเลือกโต๊ะจาก path ที่มันเขียนจริง
  (`developer` ใช้วิธีนี้แยกหน้าบ้านกับหลังบ้าน)
