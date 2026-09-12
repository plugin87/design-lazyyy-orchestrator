#!/usr/bin/env python3
"""แก้เลขฉบับที่ล้าสมัย ทั้งในหัวควบคุมและในทะเบียน

    python3 tools/correcter/fix_references.py

แก้สองที่
    ช่อง "เอกสารอ้างอิง" ในหัวควบคุมของแต่ละเอกสาร
    คอลัมน์ฉบับแก้ไขในตารางเอกสารของ REGISTER.md
**ไม่แตะเนื้อความและตารางประวัติการแก้ไข** เพราะการอ้างฉบับเก่าในสองที่นั้น
เป็นการบันทึกบริบทตอนที่ตัดสิน ไม่ใช่ข้อผิดพลาด · ลบทิ้งคือลบประวัติ

เอกสารที่สถานะเป็น ยกเลิก ก็ไม่แตะ ด้วยเหตุผลเดียวกัน
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT = ROOT / "project"


def main() -> int:
    cur, files = {}, {}
    for f in PROJECT.rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        code = re.search(r"\| รหัสเอกสาร \| ([A-Z]{2,4}-[A-Z]+-\d+) \|", t)
        rev = re.search(r"\| ฉบับแก้ไขครั้งที่ \| (\d+) \|", t)
        if code and rev:
            cur[code.group(1)] = rev.group(1)
            files[code.group(1)] = f

    fixed = 0
    for code, f in sorted(files.items()):
        t = f.read_text(encoding="utf-8")
        status = re.search(r"\| สถานะ \| (.+?) \|", t)
        if status and status.group(1).strip() == "ยกเลิก":
            continue
        m = re.search(r"(\| เอกสารอ้างอิง \| )(.+?)( \|)", t)
        if not m:
            continue
        new = m.group(2)
        for other, rev in cur.items():
            new = re.sub(rf"{other} rev \d+", f"{other} rev {rev}", new)
        if new != m.group(2):
            f.write_text(t[:m.start(2)] + new + t[m.end(2):], encoding="utf-8")
            print(f"  {code}: {m.group(2)}  →  {new}")
            fixed += 1

    # ทะเบียนต้องตามฉบับในไฟล์เสมอ
    # ตัวแก้ฉบับก่อนแตะแต่หัวควบคุม ทำให้ลูป CORRECTED ไม่ลู่เข้าเมื่อทะเบียนค้าง
    reg = PROJECT / "REGISTER.md"
    if reg.exists():
        rt = reg.read_text(encoding="utf-8")
        out = []
        for line in rt.splitlines():
            m = re.match(r"(\| ([A-Z]{2,4}-[A-Z]+-\d+) \| .+? \| )(\d+)( \|)", line)
            if m and m.group(2) in cur and m.group(3) != cur[m.group(2)]:
                line = m.group(1) + cur[m.group(2)] + m.group(4) + line[m.end():]
                print(f"  ทะเบียน {m.group(2)}: rev {m.group(3)} → rev {cur[m.group(2)]}")
                fixed += 1
            out.append(line)
        new = "\n".join(out) + ("\n" if rt.endswith("\n") else "")
        if new != rt:
            reg.write_text(new, encoding="utf-8")

    print(f"แก้ {fixed} จุด" if fixed else "ไม่มีอะไรต้องแก้")
    return 0


if __name__ == "__main__":
    sys.exit(main())
