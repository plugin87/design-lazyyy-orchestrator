#!/usr/bin/env python3
"""correcter — ตรวจความถูกต้องของทั้งโครงการ แล้วตัดสินว่าเดินต่อได้หรือไม่

    python3 tools/correcter/verify.py           ตรวจทั้งหมด
    python3 tools/correcter/verify.py --json    ผลเป็น JSON สำหรับ orchestrator
    python3 tools/correcter/verify.py --check document_consistency

รหัสออก
    0  PASS       ผ่าน เดินต่อได้
    1  CORRECTED  พบข้อบกพร่องที่แก้ได้เอง · orchestrator ต้องแก้แล้วเรียกซ้ำ
    2  BLOCKED    ต้องใช้คนหรือข้อมูลจากโลกจริง · เดินต่อไม่ได้

เหตุผลที่แยกรหัส 1 กับ 2 ออกจากกัน
    รหัส 1 คือสิ่งที่ระบบอัตโนมัติควรจัดการเอง
    รหัส 2 คือสิ่งที่ระบบอัตโนมัติ **ต้องไม่** จัดการเอง
    การรวมสองอย่างนี้เป็นรหัสเดียว คือจุดที่ระบบเริ่มปลอมการยืนยัน
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import checks  # noqa: E402
from claims import Claim, Level, Report, Verdict  # noqa: E402

EXIT = {Verdict.PASS: 0, Verdict.CORRECTED: 1, Verdict.BLOCKED: 2}
MARK = {Level.VERIFIED: "ตรวจแล้ว", Level.ASSERTED: "ยังไม่มีฐาน",
        Level.UNVERIFIABLE: "ตรวจไม่ได้", Level.CONTRADICTED: "ขัดแย้ง"}


def run(selected: str | None = None) -> Report:
    """เรียกตัวตรวจทุกตัว แล้วไม่ยอมให้ตัวไหนหายไปเงียบ ๆ

    กติกาสองข้อที่บังคับตรงนี้ ไม่ใช่ในตัวตรวจแต่ละตัว เพราะตัวตรวจที่เขียนใหม่
    พรุ่งนี้ก็ต้องอยู่ใต้กติกาเดียวกันโดยไม่ต้องมีใครเตือน

    1. ตัวตรวจที่คืนรายการว่าง = ไม่ได้ตรวจอะไร · ไม่ใช่ "ไม่มีปัญหา"
       รุ่นก่อนแยกสองอย่างนี้ไม่ออก 8 ตัวจาก 17 จึงเงียบหายไปทั้งชุด
    2. ตัวตรวจที่ระเบิด = ข้อบกพร่อง ไม่ใช่เหตุให้ทั้งรายงานหายไป
       รุ่นก่อนปล่อย KeyError จาก content.json ขึ้นมาฆ่า verify.py ทั้งตัว
       แล้วไม่มีคำตัดสินออกมาเลย ซึ่งแย่กว่าคำตัดสินที่ตก
    """
    report = Report()

    for fn in checks.ALL:
        if selected and fn.__name__ != f"check_{selected}":
            continue
        try:
            produced = fn()
        except Exception as exc:
            report.add(Claim(
                id=f"ERR-{fn.__name__[6:][:9].upper()}",
                text=f"ตัวตรวจ {fn.__name__} ระเบิดระหว่างทำงาน — {type(exc).__name__}: {exc}",
                level=Level.CONTRADICTED,
                evidence=f"เรียก checks.{fn.__name__}()",
                fix=f"แก้ {fn.__name__} ใน tools/correcter/checks.py ให้รับมือกรณีนี้ได้",
            ))
            continue
        if not produced:
            report.add(Claim(
                id=f"NUL-{fn.__name__[6:][:9].upper()}",
                text=f"ตัวตรวจ {fn.__name__} ไม่ได้ตรวจอะไรเลย และไม่บอกว่าทำไม",
                level=Level.UNVERIFIABLE,
                evidence=f"เรียก checks.{fn.__name__}() แล้วได้รายการว่าง",
                needs="ให้ตัวตรวจคืน Claim ชั้น UNVERIFIABLE พร้อมบอกว่าหาอะไรไม่เจอที่ path ไหน",
            ))
            continue
        for c in produced:
            report.add(c)

        # ตัวกันประตูเงียบอยู่หัวทะเบียน · ถ้ารหัสโครงการอ่านไม่ได้ ตัวตรวจครึ่งหนึ่ง
        # จะหาเอกสารไม่เจอแล้วรายงานเหมือนไม่มีปัญหา การเดินต่อจึงไม่ได้ให้ข้อมูล
        # อะไร นอกจากรายการยาว ๆ ที่อ่านเหมือนผ่าน
        if fn is checks.check_project_code_resolves:
            if any(c.level in (Level.CONTRADICTED, Level.UNVERIFIABLE) for c in produced):
                return report
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check")
    a = ap.parse_args()

    report = run(a.check)
    verdict = report.verdict()

    if a.json:
        print(json.dumps({
            "verdict": verdict.value,
            "counts": {
                "verified": len(report.verified),
                "asserted": len(report.asserted),
                "unverifiable": len(report.unverifiable),
                "not_applicable": len(report.not_applicable),
                "contradicted": len(report.contradicted),
            },
            "claims": [{
                "id": c.id, "level": c.level.value, "text": c.text,
                "evidence": c.evidence, "fix": c.fix, "blocks_gate": c.blocks_gate,
                "checked": c.checked, "needs": c.needs,
            } for c in report.claims],
        }, ensure_ascii=False, indent=2))
        return EXIT[verdict]

    width = max((len(c.id) for c in report.claims), default=6)
    blocking = [c for c in report.asserted if c not in report.standing]

    for group, title in ((report.unverifiable, "ยังไม่ได้ตรวจ · หาของที่ต้องตรวจไม่เจอ"),
                         (report.contradicted, "ขัดแย้งกับของจริง"),
                         (blocking, "ยังไม่มีความจริงให้เทียบ และกั้นสายงาน"),
                         (report.verified, "ตรวจกับของจริงแล้ว")):
        if not group:
            continue
        print(f"\n── {title} · {len(group)} ข้อ")
        for c in group:
            n = f"  [{c.checked} ชิ้น]" if c.checked else ""
            print(f"  {c.id.ljust(width)}  {c.text}{n}")
            if c.needs:
                print(f"  {' ' * width}  ต้องการ: {c.needs}")
            if c.fix:
                print(f"  {' ' * width}  แก้ได้ด้วย: {c.fix}")

    # กติกาที่โครงการนี้ไม่ได้ประกาศ · ไม่กั้น แต่ต้องเห็น
    # ตัวตรวจที่เงียบเพราะไม่เกี่ยวข้อง กับตัวตรวจที่เงียบเพราะพัง หน้าตาเหมือนกันหมด
    # ถ้าไม่มีอะไรถูกพิมพ์ออกมา — และรุ่นก่อนไม่พิมพ์ทั้งคู่
    if report.not_applicable:
        print(f"\n── ไม่เกี่ยวกับโครงการนี้ · {len(report.not_applicable)} ข้อ")
        print("   โครงการไม่ได้ประกาศกติกาเหล่านี้ไว้ จึงไม่มีอะไรให้ตรวจ — ไม่ใช่ผ่าน")
        for c in report.not_applicable:
            print(f"  {c.id.ljust(width)}  {c.text}")
            print(f"  {' ' * width}  {c.evidence}")

    # เงื่อนไขที่ยังเปิดอยู่ แต่มีกลไกอื่นบังคับ · ต้องไม่หายไปจากรายงาน
    # เงื่อนไขที่ถูกย้ายออกจากคำตัดสินแล้วไม่ถูกรายงาน คือเงื่อนไขที่ถูกยกเลิกเงียบๆ
    if report.standing:
        print(f"\n── เงื่อนไขที่ยังเปิดอยู่ · {len(report.standing)} ข้อ")
        print("   ไม่กั้นสายงาน เพราะมีกลไกบังคับของตัวเอง — แต่ยังไม่หายไป")
        for c in report.standing:
            print(f"\n  {c.id.ljust(width)}  {c.text}")
            print(f"  {' ' * width}  กั้น: {c.blocks.value}")
            print(f"  {' ' * width}  บังคับด้วย: {c.enforced_by}")

    print(f"\n{'═' * 60}")
    print(f"คำตัดสิน: {verdict.value}")
    if verdict is Verdict.CORRECTED:
        print("  มีข้อบกพร่องที่แก้ได้เอง · แก้แล้วเรียกซ้ำ")
    elif verdict is Verdict.BLOCKED:
        if report.unverifiable:
            print(f"  ตัวตรวจ {len(report.unverifiable)} ตัวยังไม่ได้ตรวจอะไร — "
                  f"สายงานนี้ยังพิสูจน์ไม่ได้ว่าใช้ได้")
        else:
            print("  สายงานเดินต่อไม่ได้")
    elif report.standing:
        print("  สายงานเดินได้ · แต่เงื่อนไขที่ยังเปิดอยู่ข้างบนยังไม่หมดไป")
    return EXIT[verdict]


if __name__ == "__main__":
    sys.exit(main())
