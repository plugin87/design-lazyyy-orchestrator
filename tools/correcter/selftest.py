#!/usr/bin/env python3
"""ตรวจตัวตรวจ — correcter ต้องตกได้ ไม่ใช่ผ่านได้เสมอ

    python3 tools/correcter/selftest.py

มาตรฐานพิสูจน์ข้อ 9 ใน BUILD-THIS.md เขียนไว้ว่า *"รันตัวตรวจกับโปรเจกต์เปล่า —
ถ้ามันผ่าน แปลว่ามันไม่ได้ตรวจอะไร"* ไฟล์นี้คือข้อนั้น ทำให้รันได้

ที่มา
    วัดเมื่อ 2026-09-12 ก่อนซ่อม · ชี้ `project/` ไปที่ที่ไม่มีอยู่จริง แล้วรัน
    `verify.py` ผลคือ 8 ใน 17 ตัวคืนรายการว่างเงียบ ๆ อีก 2 ตัวรายงานว่าผ่าน
    บนของศูนย์ชิ้น รวมเป็น 10 ใน 17 ที่ไม่ได้ตรวจอะไรเลย แต่คำตัดสินออกมาเป็น
    CORRECTED ซึ่งอ่านเหมือน "เกือบผ่าน"

ข้อที่สำคัญที่สุดคือข้อสุดท้าย — ตัวตรวจทุกตัวต้องคืนข้ออ้างอย่างน้อยหนึ่งข้อ
เสมอ ข้อนั้นคือสิ่งที่ทำให้ความเงียบกลับมาอีกไม่ได้ รวมถึงตัวตรวจที่ยังไม่ถูกเขียน
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
VERIFY = HERE / "verify.py"

PASS, CORRECTED, BLOCKED = 0, 1, 2

ok = True


def report(name: str, passed: bool, detail: str = "") -> None:
    global ok
    ok = ok and passed
    print(f"  {'ผ่าน  ' if passed else 'ตก    '} {name}")
    if detail:
        for line in detail.splitlines():
            print(f"         {line}")


def run_verify(project: Path) -> tuple[int, dict]:
    """รัน verify.py โดยชี้ `project/` ไปยังที่ที่กำหนด

    `project/` เป็น symlink ที่ปลายทางเปลี่ยนได้ · การทดสอบจึงสลับปลายทางชั่วคราว
    แล้วคืนค่าเดิมเสมอ ไม่ว่าจะเกิดอะไรขึ้นระหว่างทาง
    """
    link = ROOT / "project"
    saved = os.readlink(link) if link.is_symlink() else None
    existed = link.exists() or link.is_symlink()
    try:
        if existed:
            link.unlink()
        link.symlink_to(project)
        r = subprocess.run([sys.executable, str(VERIFY), "--json"],
                           cwd=ROOT, capture_output=True, text=True)
        try:
            return r.returncode, json.loads(r.stdout)
        except json.JSONDecodeError:
            return r.returncode, {"_stdout": r.stdout, "_stderr": r.stderr}
    finally:
        if link.is_symlink() or link.exists():
            link.unlink()
        if saved is not None:
            link.symlink_to(saved)


# ── 1 · โปรเจกต์เปล่าต้องไม่ผ่าน ──────────────────────────────────────────────
def test_empty_project() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        code, out = run_verify(Path(tmp))
        verdict = out.get("verdict")
        report("โปรเจกต์เปล่าไม่ผ่าน",
               code == BLOCKED,
               f"ได้ {verdict} รหัส {code} · ต้องเป็น BLOCKED รหัส {BLOCKED}")

        unver = out.get("counts", {}).get("unverifiable", 0)
        report("โปรเจกต์เปล่าบอกได้ว่าตัวไหนตรวจไม่ได้",
               unver > 0,
               f"ตัวที่รายงานว่าตรวจไม่ได้ {unver} ตัว · ต้องมากกว่า 0 "
               f"— ความเงียบคือสิ่งที่ทั้งไฟล์นี้มีไว้กัน")

        verified = [c for c in out.get("claims", []) if c.get("level") == "VERIFIED"]
        report("โปรเจกต์เปล่าไม่มีข้ออ้างว่าผ่านสักข้อ",
               not verified,
               "ผ่านบนของที่ไม่มีอยู่: " + ", ".join(c["id"] for c in verified[:6]))


# ── 2 · เอกสารที่ขัดกันเองต้องถูกจับได้ ───────────────────────────────────────
def test_contradiction_is_caught() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "1-product").mkdir()
        (p / "project.yml").write_text(
            "meta:\n  name: ทดสอบ\n  code: TST\nstage: product\n", encoding="utf-8")
        head = ("| รายการ | รายละเอียด |\n|---|---|\n"
                "| รหัสเอกสาร | {code} |\n| ฉบับแก้ไขครั้งที่ | {rev} |\n"
                "| สถานะ | ร่าง |\n| เอกสารอ้างอิง | {refs} |\n")
        (p / "1-product" / "PRD-TST-001.md").write_text(
            head.format(code="PRD-TST-001", rev="02", refs="-"), encoding="utf-8")
        # อ้างฉบับ 01 ทั้งที่ของจริงเป็นฉบับ 02 — ความขัดแย้งที่เทียบได้จากไฟล์
        (p / "1-product" / "SRS-TST-001.md").write_text(
            head.format(code="SRS-TST-001", rev="00", refs="PRD-TST-001 rev 01"),
            encoding="utf-8")

        code, out = run_verify(p)
        doc = next((c for c in out.get("claims", []) if c["id"] == "DOC-01"), None)
        report("เอกสารที่อ้างฉบับผิดถูกจับได้",
               doc is not None and doc["level"] == "CONTRADICTED",
               f"DOC-01 ได้ชั้น {doc['level'] if doc else 'ไม่มีข้ออ้างนี้เลย'} "
               f"· ต้องเป็น CONTRADICTED")
        report("โปรเจกต์ที่เอกสารขัดกันเองไม่ผ่าน",
               code != PASS,
               f"ได้ {out.get('verdict')} รหัส {code}")


# ── 3 · ไม่มีตัวตรวจตัวไหนเงียบได้ ───────────────────────────────────────────
def test_no_check_is_silent() -> None:
    sys.path.insert(0, str(HERE))
    import checks  # noqa: E402

    silent, exploded = [], []
    for fn in checks.ALL:
        try:
            produced = fn()
        except Exception as exc:                      # noqa: BLE001
            exploded.append(f"{fn.__name__}: {type(exc).__name__}: {exc}")
            continue
        if not produced:
            silent.append(fn.__name__)

    report("ตัวตรวจทุกตัวคืนข้ออ้างอย่างน้อยหนึ่งข้อ",
           not silent,
           "คืนรายการว่าง: " + ", ".join(silent) +
           "\nรายการว่างอ่านเหมือน 'ไม่มีปัญหา' ทั้งที่แปลว่า 'ไม่ได้ตรวจ'")
    report("ไม่มีตัวตรวจตัวไหนระเบิด",
           not exploded,
           "\n".join(exploded))

    registered = {f.__name__ for f in checks.ALL}
    defined = {n for n in dir(checks) if n.startswith("check_")}
    orphans = sorted(defined - registered)
    report("ตัวตรวจที่เขียนไว้ ถูกลงทะเบียนครบ",
           not orphans,
           "เขียนไว้แต่ไม่อยู่ใน ALL: " + ", ".join(orphans) +
           "\nกลไกที่เขียนไว้แล้วไม่ได้ต่อสาย คือกลไกที่ไม่มีอยู่")


# ── 4 · ข้ออ้างที่ผ่าน ต้องประกาศว่าเทียบไปกี่ชิ้น ─────────────────────────────
def test_verified_declares_its_evidence() -> None:
    sys.path.insert(0, str(HERE))
    from claims import Claim, Level  # noqa: E402

    for label, kwargs in (("ไม่ประกาศจำนวนชิ้น", dict(evidence="e")),
                          ("ประกาศว่าเทียบ 0 ชิ้น", dict(evidence="e", checked=0))):
        try:
            Claim("X-01", "ข้ออ้างทดสอบ", Level.VERIFIED, **kwargs)
            report(f"ข้ออ้างที่ผ่านโดย{label} ถูกปฏิเสธ", False,
                   "สร้างได้สำเร็จ ทั้งที่ควรถูกปฏิเสธ")
        except ValueError:
            report(f"ข้ออ้างที่ผ่านโดย{label} ถูกปฏิเสธ", True)


if __name__ == "__main__":
    print("\ncorrecter selftest — ตัวตรวจต้องตกได้\n")
    for t in (test_empty_project, test_contradiction_is_caught,
              test_no_check_is_silent, test_verified_declares_its_evidence):
        print(f"{t.__doc__ or t.__name__}")
        t()
        print()
    print("═" * 60)
    print("ผ่านทั้งหมด" if ok else "มีข้อที่ตก — correcter ยังเชื่อไม่ได้")
    sys.exit(0 if ok else 1)
