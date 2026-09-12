#!/usr/bin/env python3
"""ตรวจนิยาม subagent แบบเดียวกับที่ Claude Code อ่านมันตอนเริ่ม session

    python3 tools/correcter/validate_agents.py

มีไว้เพราะ .claude/agents/ ถูกโหลดตอนเริ่ม session เท่านั้น
นิยามที่ผิดจะไม่ถูกจับจนกว่าจะเริ่มใหม่ แล้วถึงตอนนั้นก็สายไปแล้ว
สคริปต์นี้จับความผิดตั้งแต่ตอนเขียน · รหัสออก 1 ถ้าพบปัญหา
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS = ROOT / ".claude" / "agents"
SKILLS = ROOT / ".claude" / "skills"

# ชื่อเครื่องมือที่มีจริง · พิมพ์ผิดหนึ่งตัวทำให้ agent ไม่มีเครื่องมือนั้นเงียบๆ
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "NotebookEdit", "Glob", "Grep", "Bash",
    "Agent", "Skill", "AskUserQuestion", "WebFetch", "WebSearch", "TodoWrite",
}
MUST_NOT_WRITE = {"code-reviewer", "quality-assurance"}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}


def parse(path):
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        return {}, raw, [f"{path.name} ไม่ได้ขึ้นต้นด้วย frontmatter"]
    try:
        _, head, body = raw.split("---", 2)
    except ValueError:
        return {}, raw, [f"{path.name} frontmatter ปิดไม่ครบ"]
    meta, errs = {}, []
    for line in head.strip().splitlines():
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
        elif line.strip() and not line.startswith(" "):
            errs.append(f"{path.name} บรรทัด frontmatter อ่านไม่ออก: {line[:40]}")
    return meta, body, errs


def main():
    if not AGENTS.exists():
        print("ไม่มี .claude/agents/")
        return 1
    skills = {d.name for d in SKILLS.iterdir() if d.is_dir()}
    problems, rows = [], []

    for f in sorted(AGENTS.glob("*.md")):
        meta, body, errs = parse(f)
        problems += errs
        name = meta.get("name", "")

        if name != f.stem:
            problems.append(f"{f.name} name เป็น {name!r} ไม่ตรงชื่อไฟล์")
        d = meta.get("description", "")
        if not d:
            problems.append(f"{f.stem} ไม่มี description")
        elif len(d) < 40:
            problems.append(f"{f.stem} description สั้นเกินกว่าจะบอกได้ว่าเมื่อไหร่ควรใช้")
        elif not re.search(r"[A-Za-z]{4,}", d.split("—")[0]):
            problems.append(f"{f.stem} description ไม่มีภาษาอังกฤษ ขัดกติกาใน CLAUDE.md")

        tools = {t for t in re.findall(r"([A-Za-z]+)(?:\([^)]*\))?", meta.get("tools", ""))}
        unknown = tools - KNOWN_TOOLS
        if unknown:
            problems.append(f"{f.stem} อ้างเครื่องมือที่ไม่มีจริง: {', '.join(sorted(unknown))}")
        if not tools:
            problems.append(f"{f.stem} ไม่ได้ระบุ tools — จะได้เครื่องมือทั้งหมดโดยไม่ตั้งใจ")
        if name in MUST_NOT_WRITE and tools & WRITE_TOOLS:
            problems.append(f"{f.stem} มี {', '.join(sorted(tools & WRITE_TOOLS))} ซึ่งทำลายการแยกบทบาท")

        if name and name not in skills:
            problems.append(f"{f.stem} ไม่มี skill ชื่อเดียวกันใน .claude/skills/")
        if name and f"skills/{name}/SKILL.md" not in body:
            problems.append(f"{f.stem} ตัวเอกสารไม่ได้ชี้ไปที่ skill ของตัวเอง")
        if "ขอบเขต" not in body and "Boundaries" not in body:
            problems.append(f"{f.stem} ไม่มีหัวข้อขอบเขต — ไม่รู้ว่าห้ามทำอะไร")

        rows.append((f.stem, len(tools), "ได้" if tools & WRITE_TOOLS else "ไม่ได้",
                     "✓" if name in skills else "✗"))

    w = max(len(r[0]) for r in rows)
    print(f"  {'บทบาท'.ljust(w)}  เครื่องมือ  เขียนไฟล์  skill")
    for n, tc, wr, s in rows:
        print(f"  {n.ljust(w)}  {str(tc).rjust(6)}      {wr.ljust(6)}  {s}")
    print()
    if problems:
        print(f"พบ {len(problems)} ปัญหา\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"ตรวจ {len(rows)} บทบาท · นิยามถูกต้องทั้งหมด")
    return 0


if __name__ == "__main__":
    sys.exit(main())
