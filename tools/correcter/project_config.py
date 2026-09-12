"""อ่านค่าที่ตัวตรวจต้องใช้ ออกจาก project.yml — โดยไม่พึ่งไลบรารีภายนอก

ทำไมต้องมีไฟล์นี้
    ตัวตรวจรุ่นแรกฝังรหัสโครงการ `WKO` ไว้ในตัวอักษร ทั้งใน SRS-WKO-001
    PRD-WKO-001 QAR-WKO-001 และรูปแบบ `[A-Z]{2,4}-WKO-\\d+`

    ผลคือเมื่อ `project/` ชี้ไปยังโครงการอื่น ตัวตรวจเหล่านั้น **ไม่ได้ตก**
    แต่ **ไม่ได้ตรวจอะไรเลย** เพราะหาเอกสารที่ชื่อขึ้นต้นด้วย WKO ไม่เจอ
    แล้วคืนรายการว่าง · รายงานยังขึ้นว่า VERIFIED เหมือนเดิม

    ประตูที่เงียบเพราะหาของไม่เจอ อันตรายกว่าประตูที่ตก
    เพราะประตูที่ตกมีคนไปดู ส่วนประตูที่เงียบไม่มีใครรู้ว่ามันเลิกทำงานไปแล้ว

PyYAML ไม่ได้อยู่ในเครื่องทุกเครื่อง และ correcter ต้องรันได้เสมอ
ตัวอ่านนี้จึงรองรับเฉพาะรูปแบบที่ project.yml ใช้จริง — คีย์สองชั้น ค่าสเกลาร์
สิ่งที่อ่านไม่ออกจะคืน None ไม่ใช่เดา
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT = ROOT / "project"


def read() -> dict:
    """คืน dict สองชั้นของค่าสเกลาร์ใน project.yml · อ่านไม่ได้คืน {}"""
    f = PROJECT / "project.yml"
    if not f.exists():
        return {}
    out: dict = {}
    section = None
    for raw in f.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        top = re.match(r"^([a-z_]+):\s*(.*)$", raw)
        if top:
            section = top.group(1)
            out.setdefault(section, {})
            value = _scalar(top.group(2))
            if value is not None:
                out[section] = value       # คีย์ชั้นเดียว เช่น stage:
            continue
        sub = re.match(r"^  ([a-z_]+):\s*(.*)$", raw)
        if sub and section and isinstance(out.get(section), dict):
            out[section][sub.group(1)] = _scalar(sub.group(2))
    return out


def _scalar(text: str):
    """ตัดคอมเมนต์ท้ายบรรทัดแล้วคืนค่า · ว่างหรือเป็นรายการว่างคืน None"""
    text = re.sub(r"\s+#.*$", "", text).strip()
    if text in ("", "[]", "{}", "|", ">"):
        return None
    return text


def code() -> str | None:
    """รหัสโครงการสามตัวอักษร ที่ใช้ประกอบรหัสเอกสารทุกฉบับ

    คืน None เมื่ออ่านไม่ได้ · ตัวเรียกต้องตัดสินใจเองว่าจะถือว่าขัดแย้งหรือข้าม
    **ห้ามเดาจากชื่อโฟลเดอร์** เพราะ project/ เป็น symlink ที่เปลี่ยนปลายทางได้
    """
    meta = read().get("meta")
    if not isinstance(meta, dict):
        return None
    c = meta.get("code")
    return c if c and re.fullmatch(r"[A-Z]{2,4}", c) else None


def doc(kind: str) -> str | None:
    """รหัสเอกสารเต็มของชนิดนั้น เช่น doc("SRS") → "SRS-HWK-001" """
    c = code()
    return f"{kind}-{c}-001" if c else None


def get(path: str):
    """อ่านค่าด้วยเส้นทางจุด เช่น get("outcome.baseline")"""
    node = read()
    for part in path.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node
