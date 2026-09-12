---
name: full-stack-design
description: Own the design stage end to end — pick which of the fifteen design skills a given screen or system actually needs, sequence them, and produce the DSN document that gate G3 checks. Use this when the design stage opens, when a screen or component set has to be designed from an approved SRS, when the design deliverable is missing, or when someone asks "ออกแบบหน้าจอ", "ทำ design system", "เริ่มระยะออกแบบ". Do NOT use it to answer a single design question — invoke the specific skill (design-fundamentals, design-tokens-system, web-accessibility-a11y, and so on) directly.
---

# Full-stack design

The design stage has fifteen skills and one deliverable. This skill decides which
of the fifteen a given piece of work needs, in what order, and makes sure the
deliverable that gate G3 checks actually gets written.

It exists because the other fifteen are knowledge, not a role. Knowledge does not
open a stage, sequence itself, or notice that the stage deliverable is missing.

## Intake

1. อ่าน `project/project.yml` ก่อน · ถ้าไม่มีให้รัน `project-intake`
2. ถามเฉพาะที่ยังว่างสำหรับระยะนี้ · คำถามอยู่ใน `project-intake`'s
   `references/question-bank.md` รอบที่ 4 — มีคู่มือแบรนด์เดิมไหม อุปกรณ์หลักคืออะไร
   และงานนี้ต่อยอด design system เดิม หรือเริ่มจากศูนย์
3. เขียนคำตอบกลับลง `design.*` ใน `project.yml`

## ลำดับที่ใช้ได้จริง

```
1  ตัดสินฐาน        design-systems-architecture   ต่อยอดของเดิม หรือเริ่มใหม่
2  วางโทเคน         design-tokens-system          สี ตัวอักษร ระยะห่าง มุมโค้ง
   ตัดสินค่า        design-fundamentals           ค่าไหนถูกสำหรับงานนี้
   ตรวจตั้งแต่ต้น    inclusive-design-patterns     คู่สีที่ผ่านตั้งแต่ก่อนเขียนโค้ด
3  ออกแบบส่วนประกอบ  design-systems-architecture   สถานะครบชุดของแต่ละตัว
   ขนาดและระยะ      responsive-universal-design   เบรกพอยต์ เป้าแตะ
4  ออกแบบหน้าจอ      design-fundamentals           ลำดับความสำคัญบนหน้า
   สถานะของหน้า      inclusive-design-patterns     ว่าง โหลด ผิดพลาด
5  ตรวจก่อนส่ง       anti-ai-design-patterns       ก่อนเขียน DSN เสมอ
6  เขียน DSN         design-systems-architecture   ของส่งมอบที่ G3 ตรวจ
```

**ขั้นที่ 5 ห้ามข้าม** และห้ามทำท้ายสุดหลังเขียน DSN เสร็จ · การตรวจหลังเขียนจบ
กลายเป็นการหาเหตุผลให้สิ่งที่เขียนไปแล้ว ไม่ใช่การตรวจ

## สิบห้า skill ใช้เมื่อไหร่

| เมื่อคำถามคือ | เรียก |
|---|---|
| ค่าไหนถูก สีนี้ใช้ได้ไหม ลำดับความสำคัญผิดตรงไหน | `design-fundamentals` |
| โทเคนตั้งชื่อยังไง แจกจ่ายยังไง ทำไมค่าไม่ถึงปลายทาง | `design-tokens-system` |
| ระบบทั้งระบบจัดโครงยังไง ใครดูแล เวอร์ชันยังไง | `design-systems-architecture` |
| คู่สีนี้คนตาบอดสีแยกออกไหม ฟอร์มนี้กรอกได้ไหม | `inclusive-design-patterns` |
| โค้ดที่เขียนแล้วเข้าถึงได้จริงไหม axe ตกตรงไหน | `web-accessibility-a11y` |
| เบรกพอยต์เท่าไหร่ เป้าแตะใหญ่พอไหม | `responsive-universal-design` |
| ดูเป็นของที่เครื่องสร้างตรงไหน | `anti-ai-design-patterns` |
| เขียน CSS ยังไงให้ตรงแบบ | `css-styling-pixel-perfect` |
| โครงส่วนประกอบและสถานะใน React | `frontend-framework-guide` |
| แปลงแบบเป็นสเปกให้ dev | `design-to-code-workflow` |
| ทำงานในไฟล์ Figma | `figma-expert-workflows` |
| ทำไลบรารีส่วนประกอบเป็นของส่งมอบ | `component-library-mastery` |
| หน้าช้า Core Web Vitals ตก | `web-performance-optimization` |
| วางชุดทดสอบภาพและข้ามเบราว์เซอร์ | `qa-testing-visual-regression` |
| ทำไปป์ไลน์ปล่อยงาน | `deployment-devops-workflow` |

## ของส่งมอบ

`DSN-XXX-001` สร้างด้วย `/doc-new DSN` · เนื้อหาต้องมีครบตามที่ G3 ตรวจ

- โทเคนครบสี่กลุ่ม — สี ตัวอักษร ระยะห่าง และมุมโค้งเงาการเคลื่อนไหว
- **คู่สีทุกคู่ระบุอัตราส่วนความต่างเป็นตัวเลขที่คำนวณได้** ไม่ใช่คำว่า "ผ่าน"
- ส่วนประกอบทุกตัวมีสถานะครบชุด ไม่ใช่แค่สถานะปกติ
- หน้าจอทุกหน้ามีสถานะ ว่าง โหลด ผิดพลาด และไม่มีสิทธิ์ —
  **สถานะที่ไม่ต้องมี ให้เขียนว่าไม่ต้องมีพร้อมเหตุผล** ไม่ใช่เว้นช่องว่าง
  เพื่อให้ผู้ตรวจแยกออกระหว่าง "ตัดสินใจแล้ว" กับ "ตกหล่น"
- ผลการตรวจตาม `anti-ai-design-patterns` รายข้อ
- ตารางตรวจย้อนกลับจากข้อกำหนดถึงหน้าจอ

## ขอบเขต

- **ห้ามแก้ SRS หรือ PRD** เจอว่าแบบทำตามไม่ได้ ให้เปิด `/cr`
- ห้ามเขียนโค้ดจริง · ระบุข้อกำหนดให้ `developer` ไปทำ
- ห้ามเขียนว่าคู่สีผ่าน โดยไม่มีตัวเลข · ตัวเลขที่คำนวณได้คือสิ่งเดียวที่ตรวจซ้ำได้
