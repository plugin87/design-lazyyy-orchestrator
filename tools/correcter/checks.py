"""ตัวตรวจแต่ละตัว — แต่ละตัวคืนรายการข้ออ้างพร้อมชั้นของมัน

กติกาในการเขียนตัวตรวจใหม่
  1. ห้ามคืนชั้น VERIFIED ถ้าไม่ได้เทียบกับของจริง · การอ่านเอกสารแล้วเชื่อ ไม่นับ
  2. ถ้าแก้เองได้ ให้ใส่คำสั่งแก้ไว้ในช่อง fix เพื่อให้ correcter แก้แล้วตรวจซ้ำ
  3. ถ้าเป็นเรื่องที่ต้องใช้คนหรือข้อมูลจากโลกจริง ให้ชั้น ASSERTED และระบุประตูที่ค้ำอยู่
"""
import json
import re
import subprocess
from pathlib import Path

import project_config as cfg
from claims import Blocks, Claim, Level

ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT = ROOT / "project"
BUILD = PROJECT / "4-build"


def missing(cid: str, what: str, where: str, needs: str) -> list[Claim]:
    """ตัวตรวจที่หาของไม่เจอ คืนข้ออ้างชั้นนี้ ไม่ใช่รายการว่าง

    รายการว่างอ่านเหมือน "ไม่มีปัญหา" ทั้งที่แปลว่า "ไม่ได้ตรวจ" และนั่นคือรูปแบบ
    ที่ทำให้ประตูครึ่งหนึ่งของชุดนี้เลิกทำงานโดยไม่มีใครรู้
    """
    return [Claim(id=cid, text=f"ตรวจไม่ได้ — {what}", level=Level.UNVERIFIABLE,
                  evidence=f"หาที่ {where}", needs=needs)]


def skipped(cid: str, rule: str, key: str) -> list[Claim]:
    """กติกาที่โครงการนี้ไม่ได้ประกาศไว้

    **ต้องมาจากการที่ project.yml ไม่ได้ประกาศเท่านั้น** ห้ามมาจากไฟล์ที่หายไป
    ไม่งั้นการลบไฟล์ทิ้งจะกลายเป็นวิธีปิดปากตัวตรวจ
    """
    return [Claim(id=cid, text=f"ไม่เกี่ยวกับโครงการนี้ — {rule}",
                  level=Level.NOT_APPLICABLE,
                  evidence=f"project.yml ไม่ได้ประกาศ {key}",
                  needs=f"ถ้ากติกานี้ใช้กับโครงการนี้ ให้ประกาศ {key} ใน project/project.yml")]


def _headers() -> tuple[dict, dict]:
    cur, files = {}, {}
    for f in PROJECT.rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        code = re.search(r"\| รหัสเอกสาร \| ([A-Z]{2,4}-[A-Z]+-\d+) \|", t)
        rev = re.search(r"\| ฉบับแก้ไขครั้งที่ \| (\d+) \|", t)
        if code and rev:
            cur[code.group(1)] = rev.group(1)
            files[code.group(1)] = f
    return cur, files


def check_project_code_resolves() -> list[Claim]:
    """รหัสโครงการต้องอ่านออกจาก project.yml ก่อนตัวตรวจอื่นจะมีความหมาย

    ตัวตรวจครึ่งหนึ่งในไฟล์นี้หาเอกสารด้วยรหัสโครงการ
    ถ้าอ่านรหัสไม่ได้ ตัวตรวจเหล่านั้นจะหาเอกสารไม่เจอแล้วคืนรายการว่าง
    ซึ่งอ่านเหมือน "ไม่มีปัญหา" ทั้งที่แปลว่า "ไม่ได้ตรวจ"

    ตัวตรวจนี้จึงมาก่อน และตกเสียงดังแทนที่จะปล่อยให้ทั้งชุดเงียบ
    """
    # ไม่มีไฟล์เลย กับมีไฟล์แต่เขียนผิด เป็นคนละเรื่อง และต้องได้คำตัดสินคนละอย่าง
    #
    #   ไม่มีไฟล์     → ตรวจไม่ได้ทั้งชุด · BLOCKED
    #   มีแต่รหัสเสีย → ข้อบกพร่องที่แก้ได้ · CORRECTED
    #
    # รุ่นก่อนให้ทั้งสองกรณีเป็น CONTRADICTED พร้อม fix ผลคือโปรเจกต์เปล่าได้คำตัดสิน
    # CORRECTED ซึ่งอ่านเหมือน "เกือบผ่าน" ทั้งที่ยังไม่ได้ดูอะไรเลยสักอย่าง
    # และมันชวนให้ orchestrator วนแก้ไปเรื่อย ๆ แทนที่จะหยุดแล้วไปหาคนมาตอบ
    if not (PROJECT / "project.yml").exists():
        return missing(
            "CFG-01", "ไม่มี project/project.yml — ยังไม่มีความจำร่วมให้ตัวตรวจอ่าน",
            str(PROJECT / "project.yml"),
            "/kickoff เพื่อสัมภาษณ์แล้วสร้าง project.yml · ต้องมีคนตอบคำถาม ห้ามเดาแทน")
    c = cfg.code()
    return [Claim(
        id="CFG-01",
        text=(f"รหัสโครงการ {c} อ่านได้จาก meta.code · ตัวตรวจที่หาเอกสารด้วยรหัสทำงานได้"
              if c else
              "meta.code ใน project.yml ว่างหรือไม่ใช่ตัวพิมพ์ใหญ่ 2–4 ตัว — "
              "ตัวตรวจที่หาเอกสารด้วยรหัสโครงการจะหาไม่เจอแล้วเงียบไปทั้งชุด"),
        level=Level.VERIFIED if c else Level.CONTRADICTED,
        evidence="อ่าน meta.code ใน project/project.yml",
        checked=1 if c else None,
    )]


def check_document_consistency() -> list[Claim]:
    """หัวควบคุม ทะเบียน และรหัสโครงการ — ทั้งหมดเทียบกับไฟล์จริงได้"""
    out = []
    cur, files = _headers()
    bad = []
    for code, f in files.items():
        t = f.read_text(encoding="utf-8")
        status = re.search(r"\| สถานะ \| (.+?) \|", t)
        if status and status.group(1).strip() == "ยกเลิก":
            continue
        m = re.search(r"\| เอกสารอ้างอิง \| (.+?) \|", t)
        if not m:
            continue
        for other, rev in cur.items():
            for hit in re.finditer(rf"{other} rev (\d+)", m.group(1)):
                if hit.group(1) != rev:
                    bad.append(f"{code} อ้าง {other} rev {hit.group(1)} · ปัจจุบัน rev {rev}")

    # โครงการที่ยังไม่เคยออกเอกสาร ยังไม่มีทะเบียน · อ่านไม่ได้ก็ยังไม่ใช่ความขัดแย้ง
    # ถ้าปล่อยให้ read_text โยนข้อผิดพลาด verify.py จะตายทั้งตัวแล้วไม่คืนคำตัดสินใดเลย
    # และการไม่มีคำตัดสิน แย่กว่าคำตัดสินที่ไม่ผ่าน เพราะไม่มีใครรู้ว่าเกิดอะไรขึ้น
    reg_file = PROJECT / "REGISTER.md"
    reg = reg_file.read_text(encoding="utf-8") if reg_file.exists() else ""
    for line in reg.splitlines():
        m = re.match(r"\| ([A-Z]{2,4}-[A-Z]+-\d+) \| .+? \| (\d+) \|", line)
        if m and m.group(1) in cur and m.group(2) != cur[m.group(1)]:
            bad.append(f"ทะเบียนบอก {m.group(1)} rev {m.group(2)} · ในไฟล์ rev {cur[m.group(1)]}")

    stale = [f.name for f in PROJECT.rglob("*.md") if "XXX" in f.read_text(encoding="utf-8")]
    bad += [f"{n} มีรหัส XXX ตกค้าง" for n in stale]

    if not cur and not bad:
        return missing(
            "DOC-01", "ยังไม่มีเอกสารที่มีหัวควบคุมให้เทียบสักฉบับ",
            f"{PROJECT}/**/*.md",
            "สร้างเอกสารด้วย /doc-new <TYPE> อย่างน้อยหนึ่งฉบับ")

    out.append(Claim(
        id="DOC-01",
        text=f"เอกสาร {len(cur)} ฉบับอ้างฉบับปัจจุบันของกันและกัน และทะเบียนตรงกับหัวควบคุม",
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence="python3 tools/correcter/verify.py --check document_consistency",
        fix="python3 tools/correcter/fix_references.py" if bad else None,
        checked=len(cur) if not bad else None,
    ))
    if bad:
        out[-1].text += " — พบ " + str(len(bad)) + " จุด: " + " · ".join(bad[:4])
    return out


def check_traceability() -> list[Claim]:
    """กรณีทดสอบที่ประกาศใน SRS ต้องมีเทสต์จริงที่อ้างรหัสนั้น"""
    _, files = _headers()
    srs = files.get(cfg.doc("SRS"))
    if not srs:
        return missing("TRC-01", f"ไม่พบ {cfg.doc('SRS') or 'SRS ของโครงการนี้'}",
                       f"{PROJECT}/**/*.md",
                       "/doc-new SRS — ตารางตรวจย้อนกลับเริ่มจากรหัส TC ที่ SRS ประกาศ")
    if not BUILD.exists():
        return missing("TRC-01", "ไม่มีระยะ build ให้ไล่หาเทสต์", str(BUILD),
                       "ต้องมีโค้ดใน project/4-build/ ก่อน จึงจะไล่ได้ว่ารหัส TC มีเทสต์จริง")
    declared = set(re.findall(r"\bTC-(\d\d)\b", srs.read_text(encoding="utf-8")))
    code = ""
    for d in ("tests", "e2e"):
        for p in (BUILD / d).rglob("*"):
            if not p.is_file():
                continue
            try:
                code += p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
    absent = sorted(declared - set(re.findall(r"TC-(\d\d)", code)))
    if not declared:
        return missing("TRC-01", "SRS ไม่ได้ประกาศรหัสกรณีทดสอบสักรหัส",
                       str(srs),
                       "เติมรหัส TC-xx ลงใน SRS — ข้อกำหนดที่ไม่มีเทสต์คือความหวัง")
    return [Claim(
        id="TRC-01",
        text=(f"กรณีทดสอบ {len(declared)} รหัสที่ประกาศใน SRS มีเทสต์จริงครบ"
              if not absent else
              f"ขาดเทสต์ที่อ้างรหัส: {' '.join('TC-' + m for m in absent)}"),
        level=Level.VERIFIED if not absent else Level.CONTRADICTED,
        evidence="เทียบรหัส TC ใน SRS กับไฟล์ใน tests/ และ e2e/",
        checked=len(declared) if not absent else None,
    )]


def _test_counts(output: str) -> tuple[int, int] | None:
    """อ่านจำนวนเทสต์ที่ผ่านและทั้งหมด จากผลรันของตัวรันเทสต์ที่รองรับ

    รองรับสองรูปแบบ เพราะโครงการในเทมเพลตนี้ไม่ได้ใช้ตัวรันเดียวกันทุกโครงการ
        vitest      Tests  69 passed (69)
        node:test   # pass 69  /  # fail 0

    ตัวอ่านรุ่นแรกรู้จักแต่ vitest · โครงการที่ใช้ `node --test` จึงถูกตัดสินว่า
    "รันเทสต์ไม่สำเร็จ อ่านผลไม่ได้" ทั้งที่เทสต์เขียวทั้งชุด
    ซึ่งผลักให้คนแก้ปัญหาด้วยการพิมพ์ข้อความให้ตรงรูปแบบที่ตัวตรวจรู้จัก
    แทนที่จะรายงานผลจริง — ตัวตรวจที่บีบให้โกหก คือตัวตรวจที่ออกแบบผิด
    """
    m = re.search(r"Tests\s+(\d+) passed \((\d+)\)", output)
    if m:
        return int(m.group(1)), int(m.group(2))
    p = re.search(r"^# pass (\d+)$", output, re.M)
    f = re.search(r"^# fail (\d+)$", output, re.M)
    if p and f:
        return int(p.group(1)), int(p.group(1)) + int(f.group(1))
    return None


def check_test_suite() -> list[Claim]:
    """รันเทสต์จริง แล้วเทียบจำนวนกับที่ QAR อ้างไว้

    คำสั่งรันมาจาก `domain_rules.test_command` ใน project.yml ถ้าโครงการประกาศไว้
    ค่าเริ่มต้นยังเป็น `npm test` เพราะเทมเพลตนี้ตั้งต้นด้วย Node — แต่โครงการที่
    ใช้อย่างอื่นไม่ต้องมาแก้ตัวตรวจอีกต่อไป
    """
    cmd = (cfg.get("domain_rules.test_command") or "npm test").split()
    if not (BUILD / "package.json").exists() and cmd[:2] == ["npm", "test"]:
        return missing("TST-01", "ไม่มีโค้ดในระยะ build ให้รันเทสต์",
                       str(BUILD / "package.json"),
                       "ต้องมีโปรเจกต์ในระยะ build ก่อน หรือประกาศ "
                       "domain_rules.test_command ถ้าไม่ได้ใช้ npm")
    try:
        r = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return missing("TST-01", f"รัน `{' '.join(cmd)}` ไม่ได้ — {exc}", str(BUILD),
                       "ตรวจว่า domain_rules.test_command ถูกต้อง และ project/4-build/ มีอยู่")
    counts = _test_counts(r.stdout + r.stderr)
    if not counts:
        return [Claim("TST-01", f"รัน `{' '.join(cmd)}` แล้วอ่านผลไม่ออก", Level.CONTRADICTED,
                      evidence=" ".join(cmd),
                      fix="ทำให้ตัวรันเทสต์รายงานผลในรูปแบบที่ _test_counts รู้จัก "
                          "หรือเพิ่มรูปแบบใหม่เข้าไปใน _test_counts")]
    passed, total = counts
    if total == 0:
        return missing("TST-01", "ชุดเทสต์รันได้แต่ไม่มีกรณีทดสอบสักกรณี", str(BUILD),
                       "เขียนเทสต์อย่างน้อยหนึ่งกรณี — ชุดเทสต์ว่างผ่านได้เสมอ")
    out = [Claim(
        id="TST-01",
        text=f"เทสต์ผ่าน {passed} จาก {total} กรณี",
        level=Level.VERIFIED if passed == total and r.returncode == 0 else Level.CONTRADICTED,
        evidence=" ".join(cmd),
        checked=total if passed == total and r.returncode == 0 else None,
    )]
    _, files = _headers()
    qar = files.get(cfg.doc("QAR"))
    if qar:
        claimed = re.search(r"\*\*(\d+) กรณีทดสอบ ผ่านทั้งหมด", qar.read_text(encoding="utf-8"))
        if claimed and int(claimed.group(1)) != total:
            out.append(Claim(
                id="TST-02",
                text=f"QAR อ้างว่ามี {claimed.group(1)} กรณี แต่รันจริงได้ {total}",
                level=Level.CONTRADICTED,
                evidence=f"npm test เทียบกับ {cfg.doc('QAR')}",
            ))
    return out


def check_gate_evidence() -> list[Claim]:
    """ประตูที่บันทึกว่าผ่าน ต้องมีหลักฐาน และเอกสารที่หลักฐานอ้าง ต้องมีอยู่จริง

    ประตูที่ผ่านโดยไม่มีหลักฐาน คือประตูที่ไม่ได้ตรวจอะไรเลย
    """
    y = PROJECT / "project.yml"
    if not y.exists():
        return missing("GAT-01", "ไม่มี project/project.yml ให้อ่านผลประตู", str(y),
                       "/kickoff เพื่อสร้าง project.yml")
    text = y.read_text(encoding="utf-8")
    gates, cur = [], None
    for line in text.splitlines():
        m = re.match(r"\s*- id: (G\d)", line)
        if m:
            cur = {"id": m.group(1), "result": None, "evidence": 0}
            gates.append(cur)
        elif cur is not None:
            if re.match(r"\s+result: (\w+)", line):
                cur["result"] = re.match(r"\s+result: (\w+)", line).group(1)
            elif re.match(r"\s+- ", line) and cur.get("_in_ev"):
                cur["evidence"] += 1
            cur["_in_ev"] = line.strip().startswith("evidence:") or (
                cur.get("_in_ev") and line.strip().startswith("- "))
        if line.strip() and not line.startswith(" "):
            cur = None
    passed = [g for g in gates if g["result"] == "pass"]
    naked = [g["id"] for g in passed if g["evidence"] == 0]
    codes = set(_headers()[0])
    missing_docs = []
    pc = cfg.code()
    if pc:
        for code in re.findall(rf"([A-Z]{{2,4}}-{pc}-\d+)", text):
            if code not in codes:
                missing_docs.append(code)
    bad = ([f"ประตู {g} ผ่านโดยไม่มีหลักฐาน" for g in naked]
           + [f"อ้างเอกสาร {c} ที่ไม่มีอยู่" for c in sorted(set(missing_docs))])
    if not gates:
        return missing("GAT-01", "ยังไม่มีประตูไหนถูกตรวจสักบาน",
                       f"{y} → gates:",
                       "/gate เพื่อตรวจประตูแรก — ประตูที่ยังไม่ถูกตรวจ ไม่ใช่ประตูที่ผ่าน")
    return [Claim(
        id="GAT-01",
        text=(f"ประตูที่ผ่าน {len(passed)} รายการมีหลักฐานครบ และเอกสารที่อ้างมีอยู่จริง"
              if not bad else " · ".join(bad[:4])),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence="อ่าน gates ใน project.yml เทียบกับไฟล์เอกสารจริง",
    )]


def _editorial_content() -> dict | None:
    """เนื้อหาบรรณาธิการที่ต้องผ่านการรับรองก่อนเผยแพร่ ถ้าโครงการนี้มี

    ไม่ใช่ทุกโครงการที่มี · แอปที่ผู้ใช้ป้อนข้อมูลของตัวเองล้วนไม่มีเนื้อหาชนิดนี้เลย
    ตัวตรวจสามตัวข้างล่างจึงข้ามอย่างเงียบๆ ได้ **เฉพาะเมื่อไม่มีแฟ้มเนื้อหา**
    ข้อผูกพันเชิงกฎหมายของโครงการที่ไม่มีเนื้อหาบรรณาธิการ ถูกเฝ้าโดย LAW-01 แทน
    ซึ่งบังคับให้ PRD ต้องแจกแจงข้อผูกพันของตัวเองออกมาเสมอ
    """
    f = BUILD / "src/data/content.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    key = cfg.get("domain_rules.content_items") or "items"
    return d if isinstance(d, dict) and isinstance(d.get(key), list) else None


def _content_key() -> str:
    """ชื่อคีย์ของรายการเนื้อหาใน content.json · เดิมฝังคำว่า exercises ไว้ตรง ๆ"""
    return cfg.get("domain_rules.content_items") or "items"


def _content_word() -> str:
    """คำเรียกของหนึ่งรายการ ใช้ในข้อความรายงาน · เดิมฝังคำว่า "ท่า" ไว้ตรง ๆ"""
    return cfg.get("domain_rules.content_word") or "รายการ"


def check_content_review() -> list[Claim]:
    """เนื้อหาที่ยังไม่มีผู้เชี่ยวชาญรับรอง — ตรวจด้วยเครื่องไม่ได้ตลอดกาล"""
    where = cfg.get("domain_rules.content_file")
    if not where:
        return skipped("CNT-01", "โครงการนี้ไม่มีแคตตาล็อกเนื้อหาที่ต้องมีผู้เชี่ยวชาญรับรอง",
                       "domain_rules.content_file")
    d = _editorial_content()
    if d is None:
        return missing("CNT-01", f"ประกาศ content_file ไว้ แต่อ่าน {where} ไม่ได้",
                       str(BUILD / where),
                       f"ไฟล์ต้องเป็น JSON ที่มีคีย์ {_content_key()} เป็นรายการ")
    word = _content_word()
    pub = [e for e in d[_content_key()] if e.get("published")]
    unreviewed = [e for e in pub if not e.get("reviewed_by")]
    if not pub:
        return missing("CNT-01", f"ยังไม่มี{word}ที่เผยแพร่ให้ตรวจการรับรอง", str(BUILD / where),
                       f"ต้องมี{word}ที่ตั้ง published อย่างน้อยหนึ่งรายการ")
    if not unreviewed:
        return [Claim("CNT-01", f"{word}ที่เผยแพร่ {len(pub)} รายการ ผ่านการรับรองครบ",
                      Level.VERIFIED, evidence=f"ตรวจ reviewed_by ใน {where}",
                      checked=len(pub))]
    return [Claim(
        id="CNT-01",
        text=(f"{word} {len(unreviewed)} จาก {len(pub)} ยังไม่มีผู้เชี่ยวชาญรับรอง — "
              f"เนื้อหาเป็นข้อมูลที่แก้ไขต่อเนื่อง จะมี{word}รอตรวจอยู่เสมอเป็นเรื่องปกติ"),
        level=Level.ASSERTED,
        blocks=Blocks.PUBLICATION,
        blocks_gate="G6",
        # เงื่อนไขนี้ไม่ต้องพึ่งคำตัดสินของ correcter เพราะมีกลไกบังคับอยู่แล้ว
        enforced_by=(cfg.get("domain_rules.publication_guard")
                     or "ประตูเผยแพร่ที่โครงการประกาศไว้"),
    )]


def _baseline() -> tuple[str, int, int] | None:
    """(ชื่อตัวชี้วัด, จำนวนตัวอย่างที่วัดแล้ว, จำนวนที่ต้องการ) · None = ไม่ได้ประกาศไว้

    รุ่นก่อนฝัง `G-01`, แฟ้ม `data/baseline.jsonl` และเลข 5 ไว้ในตัวอักษร ทั้งสาม
    อย่างเป็นของโครงการหนึ่งโครงการ ไม่ใช่ของสายงาน
    """
    metric = cfg.get("domain_rules.outcome_metric")
    where = cfg.get("domain_rules.baseline_file")
    if not metric or not where:
        return None
    try:
        want = int(cfg.get("domain_rules.baseline_samples") or 5)
    except (TypeError, ValueError):
        want = 5
    f = BUILD / where
    n = len(f.read_text(encoding="utf-8").strip().splitlines()) if f.exists() else 0
    return metric, n, want


def check_measured_metrics() -> list[Claim]:
    """ตัวชี้วัดที่ยังไม่เคยวัด — เลขคณิตถูกไม่ได้แปลว่าตัวป้อนจริง"""
    base = _baseline()
    if base is None:
        return skipped("MET-01", "โครงการนี้ไม่ได้ประกาศตัวชี้วัดผลลัพธ์กับค่าฐานของมัน",
                       "domain_rules.outcome_metric + baseline_file")
    metric, n, want = base
    if n >= want:
        return [Claim("MET-01", f"ค่าฐาน {metric} วัดแล้ว {n} ครั้ง", Level.VERIFIED,
                      evidence=f"นับบรรทัดใน {cfg.get('domain_rules.baseline_file')}",
                      checked=n)]
    return [Claim(
        id="MET-01",
        text=f"ค่าฐาน {metric} มี {n} ตัวอย่าง ต้องการ {want} — ตัวเลขที่เขียนไว้ยังเป็นการสมมติ",
        level=Level.ASSERTED,
        blocks=Blocks.OUTCOME_CLAIM,
        blocks_gate="G6",
        enforced_by="OUT-01 · ห้ามเอกสารใดอ้างว่าตัวชี้วัดบรรลุแล้ว",
    )]


def check_no_premature_outcome_claim() -> list[Claim]:
    """กลไกที่บังคับ MET-01 — ห้ามเอกสารใดอ้างว่าตัวชี้วัดบรรลุแล้ว ตราบใดที่ยังไม่มีข้อมูล

    การย้าย MET-01 ออกจากสิ่งที่กั้นสายงาน ต้องแลกด้วยกลไกที่บังคับมันจริง
    ไม่งั้นมันกลายเป็นการลดระดับความรุนแรงเฉยๆ ซึ่งคือสิ่งที่ correcter มีไว้กัน

    ตัวตรวจนี้อ่านเอกสารทุกฉบับ หาข้อความที่อ้างว่าผลลัพธ์เกิดขึ้นแล้ว
    """
    base = _baseline()
    if base is not None:
        metric, n, want = base
        if n >= want:
            return [Claim("OUT-01", f"ค่าฐานวัดแล้ว {n} ครั้ง · การอ้างผลลัพธ์ทำได้",
                          Level.VERIFIED,
                          evidence=f"นับบรรทัดใน {cfg.get('domain_rules.baseline_file')}",
                          checked=n)]

    # รูปแบบข้อความที่อ้างว่าผลลัพธ์เกิดขึ้นแล้ว ทั้งที่ยังไม่มีข้อมูล · รูปแบบสองแถวแรก
    # เคยฝังชื่อตัวชี้วัดกับเลข 180 ของโครงการหนึ่งไว้ ทำให้โครงการอื่นถูกตรวจไม่ครบ
    metric_pat = re.escape(base[0]) if base else r"[A-Z]{1,3}-\d{1,2}"
    CLAIMS = [
        rf"{metric_pat}\s*(บรรลุ|ผ่านแล้ว|ทำได้แล้ว|ดีขึ้น)",
        r"(ลดเวลา|ลดลง)จาก\s*[\d.,]+\s*\S+\s*เหลือ\s*[\d.,]+",
        r"ตัวชี้วัด.{0,20}(บรรลุ|สำเร็จ)แล้ว",
        r"พิสูจน์แล้วว่า.{0,20}(ได้ผล|ดีขึ้น)",
    ]
    hits, swept = [], 0
    for f in sorted(PROJECT.rglob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        swept += 1
        for pat in CLAIMS:
            for m in re.finditer(pat, text):
                hits.append(f"{f.name}: {m.group(0)[:50]}")

    if not swept:
        return missing("OUT-01", "ยังไม่มีเอกสารสักฉบับให้กวาดหาการอ้างผลลัพธ์",
                       f"{PROJECT}/**/*.md",
                       "สร้างเอกสารด้วย /doc-new <TYPE> — การกวาดเอกสารศูนย์ฉบับผ่านได้เสมอ")
    return [Claim(
        id="OUT-01",
        text=("ไม่มีเอกสารใดอ้างว่าตัวชี้วัดบรรลุแล้ว ขณะที่ค่าฐานยังไม่ถูกวัด"
              if not hits else
              "มีเอกสารอ้างว่าตัวชี้วัดบรรลุแล้ว ทั้งที่ค่าฐานยังไม่เคยวัด: " + " · ".join(hits[:3])),
        level=Level.VERIFIED if not hits else Level.CONTRADICTED,
        evidence="กวาดหาข้อความที่อ้างผลลัพธ์ในเอกสารทุกฉบับ",
        checked=swept if not hits else None,
    )]


def check_content_integrity() -> list[Claim]:
    """โครงสร้างของแคตตาล็อกเนื้อหา — อ้างอิงข้ามต้องชี้ไปยังของที่มีจริง

    รุ่นก่อนเขียน d["categories"] ด้วยวงเล็บเหลี่ยม ไม่ใช่ .get() ไฟล์ที่มีคีย์
    รายการแต่ไม่มีคีย์พี่น้องจึงโยน KeyError ขึ้นมาฆ่า verify.py ทั้งตัว
    และการไม่มีคำตัดสินเลย แย่กว่าคำตัดสินที่ตก
    """
    where = cfg.get("domain_rules.content_file")
    if not where:
        return skipped("CNT-02", "โครงการนี้ไม่มีแคตตาล็อกเนื้อหาให้ตรวจโครงสร้าง",
                       "domain_rules.content_file")
    d = _editorial_content()
    if d is None:
        return missing("CNT-02", f"ประกาศ content_file ไว้ แต่อ่าน {where} ไม่ได้",
                       str(BUILD / where),
                       f"ไฟล์ต้องเป็น JSON ที่มีคีย์ {_content_key()} เป็นรายการ")
    key, word = _content_key(), _content_word()
    items = d[key]
    if not items:
        return missing("CNT-02", f"แคตตาล็อกไม่มี{word}สักรายการ", str(BUILD / where),
                       f"เพิ่ม{word}อย่างน้อยหนึ่งรายการ — แคตตาล็อกว่างถูกโครงสร้างเสมอ")

    cats = {c.get("id") for c in d.get("categories", []) if isinstance(c, dict)}
    srcs = {x.get("id") for x in d.get("sources", []) if isinstance(x, dict)}
    bad = []
    for e in items:
        if not isinstance(e, dict):
            bad.append(f"{word}ที่ไม่ใช่ออบเจกต์")
            continue
        eid = e.get("id", "?")
        if "category_id" in e and e["category_id"] not in cats:
            bad.append(f"{eid} หมวดไม่มีจริง")
        if "source_id" in e and e["source_id"] not in srcs:
            bad.append(f"{eid} แหล่งอ้างอิงไม่มีจริง")
        for i, st in enumerate(e.get("steps", [])):
            if isinstance(st, dict) and st.get("order") != i + 1:
                bad.append(f"{eid} ลำดับขั้นตอนข้าม")
        for m in e.get("media", []):
            if isinstance(m, dict) and not str(m.get("alt_text", "")).strip():
                bad.append(f"{eid} alt ว่าง")
    ids = [e.get("id") for e in items if isinstance(e, dict)]
    if len(set(ids)) != len(ids):
        bad.append(f"รหัส{word}ซ้ำ")
    return [Claim(
        id="CNT-02",
        text=f"ข้อมูลเนื้อหา {len(items)} {word}ถูกต้องตามโครงสร้าง" if not bad
             else "ข้อมูลเนื้อหาผิดโครงสร้าง: " + " · ".join(bad[:5]),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence=f"ตรวจ {where} เทียบกับโครงสร้างที่ SRS กำหนด",
        checked=len(items) if not bad else None,
    )]


def check_release_gate_enforced() -> list[Claim]:
    """การสร้างงานผลิตต้องล้มเหลวเองถ้าเนื้อหายังไม่ถูกตรวจ

    ตัวตรวจนี้เป็นสิ่งที่ทำให้ CNT-01 ถูกย้ายออกจากคำตัดสินได้ · ถ้ามันเงียบ
    การย้ายนั้นกลายเป็นการลดระดับความรุนแรงเฉย ๆ
    """
    where = cfg.get("domain_rules.content_file")
    build_cmd = cfg.get("domain_rules.build_command")
    if not where or not build_cmd:
        return skipped("REL-01", "โครงการนี้ไม่ได้ประกาศประตูเนื้อหาที่ผูกกับการสร้างงานผลิต",
                       "domain_rules.content_file + build_command")
    d = _editorial_content()
    if d is None:
        return missing("REL-01", f"ประกาศ content_file ไว้ แต่อ่าน {where} ไม่ได้",
                       str(BUILD / where), "แก้ไฟล์เนื้อหาให้อ่านได้ก่อน")
    unreviewed = [e for e in d[_content_key()]
                  if e.get("published") and not e.get("reviewed_by")]
    try:
        r = subprocess.run(build_cmd.split(), cwd=BUILD, capture_output=True, text=True)
    except (FileNotFoundError, NotADirectoryError) as exc:
        return missing("REL-01", f"รัน `{build_cmd}` ไม่ได้ — {exc}", str(BUILD),
                       "ตรวจว่า domain_rules.build_command ถูกต้อง")
    should_fail = bool(unreviewed)
    did_fail = r.returncode != 0
    return [Claim(
        id="REL-01",
        text=("ประตูเนื้อหาปฏิเสธการสร้างงานผลิตตามที่ควร" if should_fail and did_fail
              else "การสร้างงานผลิตผ่านตามที่ควร" if not should_fail and not did_fail
              else "ประตูเนื้อหาไม่ทำงานตามที่ระบุไว้ — "
                   + ("มีเนื้อหายังไม่ถูกตรวจ แต่การสร้างงานผลิตผ่าน" if should_fail
                      else "เนื้อหาถูกตรวจครบ แต่การสร้างงานผลิตล้ม")),
        level=Level.VERIFIED if should_fail == did_fail else Level.CONTRADICTED,
        evidence=f"{build_cmd} แล้วดูรหัสออก",
        checked=1 if should_fail == did_fail else None,
    )]


def check_agent_boundaries() -> list[Claim]:
    """ข้อจำกัดเครื่องมือของ subagent ต้องยังบังคับกติกาของสายงานอยู่

    กติกาสองข้อในสายงานนี้ถูกบังคับด้วย allowlist ของเครื่องมือ ไม่ใช่ด้วยคำสั่ง
        ผู้ทบทวนโค้ดไม่แก้โค้ด
        ผู้ตรวจคุณภาพไม่เขียนฟีเจอร์

    ถ้ามีใครเติม Edit หรือ Write กลับเข้าไป กติกาจะกลับไปเป็นเรื่องของวินัย
    โดยไม่มีใครสังเกต · ตัวตรวจนี้จึงมีไว้เฝ้าตัวเฝ้า
    """
    agents = ROOT / ".claude" / "agents"
    if not agents.exists():
        return [Claim(
            id="AGT-01",
            text="ยังไม่มี .claude/agents/ — บทบาทยังไม่ถูกแยกคอนเท็กซ์",
            level=Level.ASSERTED,
        )]

    must_not_write = {"code-reviewer", "quality-assurance"}
    bad, seen = [], set()
    for f in sorted(agents.glob("*.md")):
        head = f.read_text(encoding="utf-8").split("---")[1]
        name = re.search(r"^name: (.+)$", head, re.M)
        tools = re.search(r"^tools: (.+)$", head, re.M)
        if not name:
            bad.append(f"{f.name} ไม่มีช่อง name")
            continue
        name = name.group(1).strip()
        seen.add(name)
        if name != f.stem:
            bad.append(f"{f.name} ช่อง name เป็น {name} ไม่ตรงชื่อไฟล์")
        if not re.search(r"^description: .+", head, re.M):
            bad.append(f"{name} ไม่มีช่อง description")
        if f"skills/{name}/SKILL.md" not in f.read_text(encoding="utf-8"):
            bad.append(f"{name} ไม่ได้ชี้ไปที่ skill ของตัวเอง")
        if name in must_not_write and tools:
            for banned in ("Edit", "Write", "NotebookEdit"):
                if re.search(rf"\b{banned}\b", tools.group(1)):
                    bad.append(f"{name} มีเครื่องมือ {banned} ซึ่งทำลายการแยกบทบาท")

    skills = {d.name for d in (ROOT / ".claude" / "skills").iterdir() if d.is_dir()}
    for name in seen:
        if name not in skills:
            bad.append(f"{name} เป็น agent แต่ไม่มี skill ชื่อเดียวกัน")

    # ทุกบทบาทในตารางระยะของ orchestrator ต้องมีทั้ง skill และ agent
    # ตารางที่อ้างบทบาทที่ไม่มีอยู่ ทำให้ลูปสะดุดตอนถึงระยะนั้นพอดี
    orch = ROOT / ".claude" / "skills" / "orchestrator" / "SKILL.md"
    if orch.exists():
        block = re.search(r"\| stage \|.*?\n\n", orch.read_text(encoding="utf-8"), re.S)
        if block:
            # คอลัมน์บทบาทไม่ได้ใส่ backtick · ต้องอ่านเป็นข้อความล้วนคั่นด้วย ·
            for row in re.finditer(r"^\| `[a-z]+` \| ([^|]+) \|", block.group(0), re.M):
                for role in re.findall(r"[a-z][a-z-]{3,}", row.group(1)):
                    if role not in seen:
                        bad.append(f"ตารางระยะอ้างบทบาท {role} ที่ไม่มี agent")
                    if role not in skills:
                        bad.append(f"ตารางระยะอ้างบทบาท {role} ที่ไม่มี skill")

    # กติกาภาษาของ repo — อังกฤษเป็นค่าตั้งต้น ไทยใช้ได้เฉพาะวลีที่เป็น trigger
    for f in sorted(agents.glob("*.md")):
        head = f.read_text(encoding="utf-8").split("---")[1]
        d = re.search(r"^description: (.+)$", head, re.M)
        if d and not re.search(r"[A-Za-z]{4,}", d.group(1).split("—")[0]):
            bad.append(f"{f.stem} คำอธิบายไม่มีภาษาอังกฤษ ขัดกติกาภาษาใน CLAUDE.md")

    return [Claim(
        id="AGT-01",
        text=(f"subagent {len(seen)} บทบาทครบตามตารางระยะ · คำอธิบายเป็นอังกฤษ · ผู้ทบทวนกับผู้ตรวจคุณภาพแก้ไฟล์ไม่ได้"
              if not bad else " · ".join(bad[:4])),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence="อ่าน frontmatter ของทุกไฟล์ใน .claude/agents/",
        checked=len(seen) if not bad else None,
    )]


def check_gates_can_fail() -> list[Claim]:
    """สคริปต์ตรวจที่ไม่เคยตั้งรหัสออก ไม่ใช่ประตู แต่เป็นรายงาน

    รูปแบบข้อบกพร่องนี้หลุดผ่านทั้งผู้เขียนและ correcter ไปพร้อมกันมาแล้ว
        e2e/online-only-check.cjs เคยมีแต่ console.log
        พิมพ์ ✗ ออกมาแล้วก็ยังจบด้วยรหัส 0
        คนที่รันเห็นข้อความว่าตรวจแล้ว แล้วเชื่อ

    ตัวตรวจนี้จึงเฝ้าว่า ทุกสคริปต์ใน e2e/ ต้องมีทางที่ทำให้ตัวเองตกได้
    """
    e2e = BUILD / "e2e"
    if not e2e.exists():
        return missing("GTE-01", "ไม่มีโฟลเดอร์สคริปต์ตรวจ", str(e2e),
                       "สร้าง project/4-build/e2e/ แล้วเขียนสคริปต์ตรวจอย่างน้อยหนึ่งตัว")
    scripts = sorted(e2e.glob("*.cjs"))
    if not scripts:
        return missing("GTE-01", "โฟลเดอร์สคริปต์ตรวจว่างเปล่า", str(e2e),
                       "สคริปต์ตรวจศูนย์ไฟล์ 'ตกได้ทุกไฟล์' เสมอ — ต้องมีอย่างน้อยหนึ่งตัว")
    bad = []
    for f in scripts:
        src = f.read_text(encoding="utf-8")
        if "process.exit" not in src and "process.exitCode" not in src:
            bad.append(f"{f.name} ไม่เคยตั้งรหัสออก — เป็นรายงาน ไม่ใช่การทดสอบ")
        if re.search(r"localhost:\d+", src) and "BASE" not in src:
            bad.append(f"{f.name} ฝังพอร์ตไว้ตายตัวโดยไม่มีทางเปลี่ยน")
    return [Claim(
        id="GTE-01",
        text=(f"สคริปต์ตรวจใน e2e/ ทั้ง {len(scripts)} ไฟล์ มีทางที่ทำให้ตัวเองตกได้"
              if not bad else " · ".join(bad[:4])),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence="อ่านสคริปต์ใน e2e/ หา process.exit และพอร์ตที่ฝังตาย",
        checked=len(scripts) if not bad else None,
    )]


def check_health_notice() -> list[Claim]:
    """คอมโพเนนต์ที่ข้อผูกพันตามกฎหมายบังคับให้แสดงทุกหน้า ต้องยังอยู่และไม่มีเงื่อนไข

    ที่มาของรูปแบบนี้ — โครงการหนึ่งพบว่า 7 จาก 30 รายการไม่มีฟิลด์คำเตือน
    หน้าเหล่านั้นจึงไม่มีคำเตือนเลย ทางแก้คือคำเตือนระดับหน้าที่ไม่ผูกกับข้อมูลรายรายการ
    รูปแบบใช้ซ้ำได้ · ชื่อไฟล์ใช้ซ้ำไม่ได้

    รุ่นก่อนฝัง HealthNotice.tsx กับ Detail.tsx ไว้ตรง ๆ และ **ไม่มีเงื่อนไขกันเลย**
    มันจึงตกในทุกโครงการที่ไม่ใช่แอปนั้น พร้อม fix=None แปลว่าแก้ไม่ได้ตลอดกาล
    """
    name = cfg.get("domain_rules.mandatory_component")
    if not name:
        return skipped("LAW-01", "โครงการนี้ไม่ได้ประกาศคอมโพเนนต์ที่กฎหมายบังคับให้แสดงทุกหน้า",
                       "domain_rules.mandatory_component")
    host = cfg.get("domain_rules.mandatory_component_host")
    hits = [f for f in BUILD.rglob(f"{name}.*") if f.is_file()]
    bad = []
    if not hits:
        bad.append(f"ไม่มีคอมโพเนนต์ {name} — คำเตือนระดับหน้าหายไป")
    elif host:
        page = BUILD / host
        if not page.exists():
            bad.append(f"ไม่มีหน้า {host} ที่ประกาศไว้ว่าต้องแสดง {name}")
        else:
            d = page.read_text(encoding="utf-8")
            if f"<{name}" not in d:
                bad.append(f"{host} ไม่ได้แสดง {name}")
            if re.search(rf"\{{[^}}]*&&\s*<{re.escape(name)}", d):
                bad.append(f"{name} ถูกผูกกับเงื่อนไข — ต้องแสดงเสมอ")
    tests = [f for f in BUILD.rglob("*") if f.is_file() and name.lower() in f.name.lower()
             and (".test." in f.name or ".spec." in f.name)]
    if not tests:
        bad.append(f"ไม่มีเทสต์ที่บังคับ {name}")
    return [Claim(
        id="LAW-01",
        text=(f"{name} แสดงโดยไม่มีเงื่อนไข และมีเทสต์บังคับ" if not bad else " · ".join(bad)),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence=f"หา {name} ใน project/4-build/ และเทสต์ที่อ้างชื่อมัน",
        checked=len(hits) + len(tests) if not bad else None,
        fix=None if not bad else f"สร้าง {name} และเทสต์ของมัน หรือถอด "
                                f"domain_rules.mandatory_component ถ้ากติกานี้เลิกใช้แล้ว",
    )]


def check_deliverable_ownership() -> list[Claim]:
    """บทบาทที่เป็นเจ้าของของส่งมอบ ต้องผลิตมันได้ หรือนิยามต้องบอกว่าใครผลิตให้

    ช่องโหว่นี้ผ่าน AGT-01 มาตลอด เพราะ AGT-01 ถามแค่ "reviewer ไม่มี Write ใช่ไหม"
    ไม่เคยถามต่อว่า "แล้วเอกสารที่ reviewer เป็นเจ้าของ ใครเขียน"

    ตารางระยะบอกว่า review → RVW และ quality → QAR
    แต่ทั้งสองบทบาทไม่มีเครื่องมือเขียนไฟล์ และตัวเองก็ห้ามเขียนไว้
    เอกสารสองฉบับนั้นจึงไม่มีใครในระบบผลิตได้เลย
    """
    agents = ROOT / ".claude" / "agents"
    orch = ROOT / ".claude" / "skills" / "orchestrator" / "SKILL.md"
    if not agents.exists():
        return missing("AGT-02", "ไม่มีโฟลเดอร์นิยาม subagent", str(agents),
                       "สร้าง .claude/agents/ — การแยกบทบาทบังคับด้วยไฟล์พวกนี้")
    if not orch.exists():
        return missing("AGT-02", "ไม่มี SKILL.md ของ orchestrator ที่ถือตารางระยะ", str(orch),
                       "สร้าง .claude/skills/orchestrator/SKILL.md พร้อมตารางระยะ")

    block = re.search(r"\| stage \|.*?\n\n", orch.read_text(encoding="utf-8"), re.S)
    if not block:
        return missing("AGT-02", "SKILL.md ของ orchestrator ไม่มีตารางระยะให้อ่าน", str(orch),
                       "ตารางต้องขึ้นต้นด้วยหัวคอลัมน์ `| stage |`")

    WRITE = ("Edit", "Write", "NotebookEdit")
    bad, pairs = [], 0
    for row in re.finditer(r"^\| `[a-z]+` \| ([^|]+) \| ([^|]+) \|", block.group(0), re.M):
        roles = re.findall(r"[a-z][a-z-]{3,}", row.group(1))
        # ของส่งมอบคือรหัสเอกสารตัวใหญ่ในคอลัมน์เงื่อนไขเลื่อน
        docs = re.findall(r"\b([A-Z]{3})\b", row.group(2))
        if not docs:
            continue
        for role in roles:
            f = agents / f"{role}.md"
            if not f.exists():
                continue
            pairs += 1
            src = f.read_text(encoding="utf-8")
            tools = re.search(r"^tools: (.+)$", src.split("---")[1], re.M)
            can_write = tools and any(re.search(rf"\b{w}\b", tools.group(1)) for w in WRITE)
            names_writer = "ถอดความ" in src or "ผู้เขียนแทน" in src or "document-control" in src
            if not can_write and not names_writer:
                bad.append(f"{role} ต้องส่งมอบ {'/'.join(docs)} แต่เขียนไฟล์ไม่ได้ และนิยามไม่บอกว่าใครเขียนให้")

    return [Claim(
        id="AGT-02",
        text=(f"ทุกบทบาทที่เป็นเจ้าของของส่งมอบ ({pairs} คู่บทบาท-ของส่งมอบ) ผลิตมันได้ "
              f"หรือระบุไว้ว่าใครผลิตให้" if not bad else " · ".join(bad)),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        evidence="เทียบตารางระยะกับ allowlist ของแต่ละ agent",
        checked=pairs if not bad else None,
    )]


def check_metrics_measurable() -> list[Claim]:
    """ตัวชี้วัดที่ PRD ประกาศ ต้องคำนวณได้จากเหตุการณ์ที่ระบบเก็บจริง

    ตัวชี้วัดที่วัดไม่ได้ ไม่ใช่ตัวชี้วัด แต่เป็นความตั้งใจ
    และมันอันตรายกว่าการไม่มีตัวชี้วัด เพราะทุกคนคิดว่ามีแล้ว
    """
    prd = _headers()[1].get(cfg.doc("PRD"))
    if not prd:
        return missing("MET-02", f"ไม่พบ {cfg.doc('PRD') or 'PRD ของโครงการนี้'}",
                       f"{PROJECT}/**/*.md",
                       "/doc-new PRD — ตัวชี้วัดที่ต้องวัดได้ ประกาศอยู่ใน PRD")
    rel = cfg.get("domain_rules.metrics_source")
    if not rel:
        return skipped("MET-02", "โครงการนี้ไม่ได้ประกาศว่าตัวชี้วัดถูกคำนวณจากที่ไหน",
                       "domain_rules.metrics_source")
    agg = BUILD / rel
    if not agg.exists():
        return missing("MET-02", f"ประกาศแหล่งคำนวณตัวชี้วัดไว้ แต่ไม่พบ {rel}", str(agg),
                       f"สร้าง {rel} หรือแก้ domain_rules.metrics_source ให้ชี้ถูก")
    src = agg.read_text(encoding="utf-8")
    declared = set(re.findall(r"\|\s*([A-Z]{1,3}-\d{1,3})\s*\|", prd.read_text(encoding="utf-8")))
    if not declared:
        return missing("MET-02", "PRD ไม่ได้ประกาศรหัสตัวชี้วัดในตารางสักตัว", str(prd),
                       "เติมตารางตัวชี้วัดลงใน PRD — ตัวชี้วัดที่วัดไม่ได้ ไม่ใช่ตัวชี้วัด")
    absent = sorted(d for d in declared
                    if d.lower().replace("-", "") not in src.lower().replace("-", ""))
    return [Claim(
        id="MET-02",
        text=(f"ตัวชี้วัดที่ประกาศ {len(declared)} ตัว คำนวณได้จากเหตุการณ์ที่เก็บจริงครบ"
              if not absent else
              f"ตัวชี้วัด {' '.join(absent)} ประกาศไว้ใน PRD แต่ {rel} ไม่ได้รายงาน — "
              f"วัดไม่ได้ด้วยสิ่งที่ระบบเก็บ"),
        level=Level.VERIFIED if not absent else Level.CONTRADICTED,
        checked=len(declared) if not absent else None,
        evidence=f"เทียบรหัสตัวชี้วัดในตารางของ PRD กับ {rel}",
    )]


def check_referenced_files_exist() -> list[Claim]:
    """คอมเมนต์และเอกสารที่ชี้ไปยังไฟล์ ต้องชี้ไปยังไฟล์ที่มีอยู่จริง

    ที่มา — คอมเมนต์ใน src/styles/app.css เขียนว่า
        "ด่านที่ตรวจให้คือ e2e/contrast-states-check.cjs"
    ตอนที่เขียนบรรทัดนั้น ไฟล์นั้นไม่มีอยู่ · ไม่เคยมี
    คนอ่านโค้ดจะเชื่อว่ามีด่านคุ้มกันอยู่ แล้วไม่ไปตรวจซ้ำ
    ซึ่งแย่กว่าการไม่เขียนอะไรเลย เพราะช่องว่างที่มองเห็นมีคนเติม
    แต่การอ้างที่ผิดไม่มีใครเห็น

    ตัวตรวจนี้เก็บเฉพาะเส้นทางที่ดูออกชัดว่าเป็นไฟล์ในโครงการ
    (มีนามสกุลที่เรารู้จัก และอยู่ใต้โฟลเดอร์ที่เรารู้จัก)
    เพื่อไม่ให้ไปจับ URL หรือชื่อแพ็กเกจ

    ข้อยกเว้นที่มีเหตุผล และวิธีประกาศให้เครื่องอ่านออก
        รายงานการทบทวนบันทึกสิ่งที่ตรวจ ณ เวลานั้น · ไฟล์บางไฟล์ถูกลบไปภายหลัง
        การลบข้อความนั้นทิ้ง คือการลบประวัติ ซึ่งผิดกติกาของเอกสารควบคุม
        ใส่ขีดฆ่ารอบเส้นทาง ~~เช่นนี้~~ เพื่อบอกว่า "เคยมี ตอนนี้ไม่มีแล้ว"
        คนอ่านเห็นทันทีว่าไม่ใช่ของปัจจุบัน และตัวตรวจข้ามให้
        คำขอเปลี่ยนแปลง (CR-*) ยกเว้นทั้งฉบับ เพราะทั้งฉบับคือข้อเสนอ ไม่ใช่ข้ออ้างว่ามีอยู่
    """
    # ลำดับในวงเล็บสำคัญ · ตัวยาวต้องมาก่อน ไม่งั้น "App.tsx" ถูกจับเป็น "App.ts"
    # และ "content.json" ถูกจับเป็น "content.js" แล้วรายงานว่าไฟล์ที่มีอยู่จริงหายไป
    # ตัวตรวจที่โกหกเสียเอง อันตรายกว่าไม่มีตัวตรวจ · เรียงตามความยาวจึงเป็นข้อบังคับ
    _EXTS = ["tsx", "cjs", "mjs", "json", "html", "yml", "svg", "css", "ts", "js", "py", "sh", "md"]
    exts = "(?:" + "|".join(sorted(_EXTS, key=len, reverse=True)) + ")"
    pattern = re.compile(
        rf"(?<![\w/.-])((?:e2e|src|tests|scripts|server|tools|public|docs|project|\.claude)/[\w./-]+\.{exts})"
    )
    scan_roots = [BUILD / "src", BUILD / "e2e", BUILD / "scripts", BUILD / "server", PROJECT]
    bad: list[str] = []
    checked = 0

    for root in scan_roots:
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if not f.is_file() or "node_modules" in f.parts or "dist" in f.parts:
                continue
            if f.suffix not in {".ts", ".tsx", ".js", ".mjs", ".cjs", ".css", ".md", ".py", ".json"}:
                continue
            # คำขอเปลี่ยนแปลงพูดถึงสถานะที่ "จะเป็น" หรือ "เคยเป็น" โดยธรรมชาติของมัน
            # CR-WKO-001 ถูกยกเลิก ไฟล์ในนั้นจึงไม่เคยถูกสร้าง
            # CR-WKO-002 บันทึกไฟล์ที่ถูกลบทิ้งตามมติ · ทั้งสองอย่างเป็นประวัติที่ถูกต้อง
            # ตัวตรวจนี้ตรวจ "ข้ออ้างว่าตอนนี้มีอยู่" ไม่ใช่ข้อเสนอหรือบันทึกการลบ
            if f.name.startswith("CR-"):
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            # เส้นทางที่ถูกขีดฆ่าไว้ คือการประกาศว่ามันไม่มีแล้ว ไม่ใช่ข้ออ้างว่ามี
            text = re.sub(r"~~.*?~~", "", text, flags=re.DOTALL)
            for m in set(pattern.findall(text)):
                checked += 1
                # เส้นทางเขียนได้สองแบบ · จากรากที่เก็บงาน หรือจากรากของแอป
                if (ROOT / m).exists() or (BUILD / m).exists():
                    continue
                bad.append(f"{f.relative_to(ROOT)} อ้างถึง {m} ที่ไม่มีอยู่จริง")

    if not checked and not bad:
        return missing("REF-01", "ไม่พบเส้นทางไฟล์ที่ถูกอ้างถึงเลยสักรายการ",
                       "คอมเมนต์และเอกสารใต้ project/ และ 4-build/",
                       "ต้องมีโค้ดหรือเอกสารที่อ้างเส้นทางไฟล์ก่อน จึงจะตรวจได้ว่าอ้างถูก")
    return [Claim(
        id="REF-01",
        text=(f"เส้นทางไฟล์ {checked} รายการที่ถูกอ้างในคอมเมนต์และเอกสาร ชี้ไปยังไฟล์ที่มีอยู่จริงทั้งหมด"
              if not bad else " · ".join(sorted(bad)[:5])),
        level=Level.VERIFIED if not bad else Level.CONTRADICTED,
        checked=checked if not bad else None,
        evidence="กวาดคอมเมนต์และเอกสาร หาเส้นทางที่มีนามสกุลรู้จัก แล้วเทียบกับระบบไฟล์",
        fix=None if not bad else "สร้างไฟล์ที่อ้างถึง หรือลบการอ้างที่ไม่จริงออก",
    )]


def check_mechanisms_have_tests() -> list[Claim]:
    """กลไกความปลอดภัยต้องมีเทสต์ที่แดงเมื่อมันหายไป

    ที่มา — รอบตรวจอิสระลบกลไกแปดอย่างทิ้งทีละอย่าง แล้วชุดเทสต์ยังเขียว 77/77
    โค้ดที่ไม่มีเทสต์ตัวไหนล้มเมื่อมันหายไป คือโค้ดที่รอบหน้าจะถูกเก็บกวาดทิ้งเงียบๆ
    และนั่นคือเหตุผลเดียวกับที่ BR-07 ถูกยกจาก "คำเตือนบนกระดาษ" มาเป็น "กลไก"

    ตัวตรวจนี้ไม่ได้รันการกลายพันธุ์เอง เพราะมันช้าเกินจะอยู่ในทุกรอบตรวจ
    สิ่งที่มันตรวจคือ ทะเบียนยังตรงกับโค้ด — ข้อความในช่อง find ยังอยู่ในไฟล์จริง
    ซึ่งจับกรณีที่กลไกถูกลบไปพร้อมกับเทสต์ของมัน
    การรันจริงอยู่ที่ npm run test:mutation ซึ่งเป็นด่านของมันเอง
    """
    rel = cfg.get("domain_rules.mutation_registry")
    if not rel:
        return skipped("MUT-01", "โครงการนี้ไม่ได้ประกาศทะเบียนกลไกที่ต้องมีเทสต์คุ้มครอง",
                       "domain_rules.mutation_registry")
    registry = BUILD / rel
    if not registry.exists():
        return missing("MUT-01", f"ประกาศทะเบียนกลไกไว้ แต่ไม่พบ {rel}", str(registry),
                       f"สร้าง {rel} หรือถอด domain_rules.mutation_registry ถ้าเลิกใช้แล้ว")
    try:
        mutants = json.loads(registry.read_text(encoding="utf-8"))["mutants"]
    except (json.JSONDecodeError, KeyError, OSError) as exc:
        return [Claim("MUT-01", f"อ่านทะเบียนกลไก {rel} ไม่ได้ — {exc}", Level.CONTRADICTED,
                      evidence=str(registry),
                      fix=f"แก้ {rel} ให้เป็น JSON ที่มีคีย์ mutants เป็นรายการ")]
    if not mutants:
        return missing("MUT-01", "ทะเบียนกลไกไม่มีรายการสักรายการ", str(registry),
                       "ขึ้นทะเบียนกลไกที่ต้องมีเทสต์คุ้มครองอย่างน้อยหนึ่งอย่าง")
    stale = []
    for m in mutants:
        target = BUILD / m["file"]
        if not target.exists():
            stale.append(f"{m['id']} ชี้ไปยัง {m['file']} ที่ไม่มีอยู่")
        elif m["find"] not in target.read_text(encoding="utf-8"):
            stale.append(f"{m['id']} · {m['name']} — โค้ดที่ทะเบียนคุ้มครองไว้หายไปจาก {m['file']}")

    # เดิมอ่าน package.json โดยไม่เช็กว่ามีอยู่ · โครงการที่มีทะเบียนแต่ไม่ใช่ Node
    # จึงโยน FileNotFoundError ขึ้นมาฆ่า verify.py ทั้งตัว
    runner = cfg.get("domain_rules.mutation_command") or "npm run test:mutation"
    pkg_file = BUILD / "package.json"
    if pkg_file.exists():
        try:
            pkg = json.loads(pkg_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pkg = {}
        script = runner.replace("npm run ", "").strip()
        if script and script not in pkg.get("scripts", {}):
            stale.append(f"package.json ไม่มีคำสั่ง {script} — ทะเบียนมีอยู่แต่ไม่มีใครรัน")

    return [Claim(
        id="MUT-01",
        text=(f"กลไกที่ขึ้นทะเบียนไว้ {len(mutants)} อย่าง ยังอยู่ในโค้ดครบ และมีคำสั่งทดสอบการกลายพันธุ์"
              if not stale else " · ".join(stale[:4])),
        level=Level.VERIFIED if not stale else Level.CONTRADICTED,
        evidence=f"เทียบ {rel} กับเนื้อไฟล์จริง และตรวจว่ามีคำสั่งรันการกลายพันธุ์",
        checked=len(mutants) if not stale else None,
        fix=None if not stale else "ปรับทะเบียนให้ตรงกับโค้ด หรือเอากลไกที่หายไปกลับมา",
    )]


def check_verdict_command_runnable() -> list[Claim]:
    """คำสั่งที่ใช้ตัดสิน ต้องรันได้จริงในโหมดที่สายงานอัตโนมัติรันอยู่

    ที่มา — `tools/auto.sh` เรียก `claude -p ... --permission-mode acceptEdits`
    โหมดนั้นอนุมัติ **การแก้ไฟล์** ให้เอง แต่ไม่อนุมัติ Bash
    คำสั่ง Bash ที่ไม่อยู่ใน permissions.allow จึงถูกปฏิเสธ
    และในการรันแบบไม่มีคนนั่งเฝ้า ไม่มีใครกดอนุมัติได้

    ผลคือ orchestrator เดินงานได้ แต่เรียก `verify.py` ไม่ได้เลยสักครั้ง
    ซึ่งเป็นรูปแบบที่แย่ที่สุดของระบบนี้ — ตัวที่ทำงานเดินต่อโดยไม่มีตัวตัดสิน
    แล้วไม่มีอะไรในระบบส่งเสียงว่าการตรวจถูกข้ามไป

    ตัวตรวจนี้ไม่บอกว่า "แก้ได้เอง" เพราะไฟล์ตั้งค่าเป็นไฟล์ที่ตัวแทนแก้ไม่ได้
    ตามการออกแบบ · ต้องมีคนเติมกฎเข้าไปเอง
    """
    settings = ROOT / ".claude" / "settings.json"
    if not settings.exists():
        return []
    try:
        allow = json.loads(settings.read_text(encoding="utf-8"))["permissions"]["allow"]
        prefixes = []
        for rule in allow:
            m = re.match(r"Bash\((.+?)(?::\*)?\)$", str(rule))
            if m:
                prefixes.append(m.group(1))
    except (json.JSONDecodeError, KeyError, TypeError):
        return [Claim(
            id="RUN-01",
            text=".claude/settings.json อ่านรายการ permissions.allow ไม่ได้",
            level=Level.CONTRADICTED,
            evidence="อ่าน permissions.allow ใน .claude/settings.json",
        )]

    needed = ["python3 tools/correcter/verify.py",
              "python3 tools/correcter/fix_references.py"]
    absent = [c for c in needed if not any(c.startswith(p) for p in prefixes)]
    return [Claim(
        id="RUN-01",
        checked=len(needed) if not absent else None,
        text=("คำสั่งของ correcter อยู่ใน permissions.allow · สายงานอัตโนมัติเรียกตัวตัดสินได้"
              if not absent else
              "สายงานอัตโนมัติเรียกตัวตัดสินไม่ได้ — permissions.allow ไม่มีกฎที่ครอบคลุม "
              + " และ ".join(absent)
              + " · เติม \"Bash(python3 tools/correcter/verify.py:*)\" "
                "และ \"Bash(python3 tools/correcter/fix_references.py:*)\" "
                "ใน .claude/settings.json — ไฟล์นี้ตัวแทนแก้เองไม่ได้ตามการออกแบบ"),
        level=Level.VERIFIED if not absent else Level.CONTRADICTED,
        evidence="เทียบคำสั่งที่ skill orchestrator สั่งให้รัน กับกฎใน .claude/settings.json",
    )]


ALL = [
    # ตัวกันประตูเงียบต้องมาก่อน · verify.py หยุดทั้งชุดถ้าตัวนี้ตก เพราะตัวตรวจ
    # ครึ่งหนึ่งหาเอกสารด้วยรหัสโครงการ ถ้าอ่านรหัสไม่ได้มันจะหาไม่เจอแล้วเงียบ
    check_project_code_resolves,
    check_document_consistency,
    check_verdict_command_runnable,
    check_agent_boundaries,
    check_deliverable_ownership,
    check_metrics_measurable,
    check_gate_evidence,
    check_traceability,
    check_content_integrity,
    check_test_suite,
    check_gates_can_fail,
    check_health_notice,
    check_release_gate_enforced,
    check_content_review,
    check_measured_metrics,
    check_no_premature_outcome_claim,
    check_referenced_files_exist,
    check_mechanisms_have_tests,
]
