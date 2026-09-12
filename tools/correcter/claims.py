"""การจำแนกข้ออ้าง — หัวใจของ correcter

ทุกข้ออ้างในชุดเอกสารตกอยู่ในสามชั้น และชั้นที่ต่างกันต้องปฏิบัติต่างกัน

    VERIFIED     มีความจริงให้เทียบ และเทียบแล้วตรง
                 เช่น "เทสต์ผ่าน 69 กรณี" เทียบกับผลรัน npm test

    ASSERTED     ยังไม่มีความจริงให้เทียบ
                 เช่น "ค่าฐาน 180 วินาที" ซึ่งไม่เคยวัด
                 ข้ออ้างชั้นนี้ไม่ผิด แต่ห้ามถูกนำเสนอว่าตรวจแล้ว

    CONTRADICTED มีความจริงให้เทียบ และเทียบแล้วไม่ตรง

ข้อบกพร่องที่อันตรายที่สุดของระบบอัตโนมัติ ไม่ใช่การตอบผิด
แต่คือการยกข้ออ้างชั้น ASSERTED ขึ้นเป็น VERIFIED โดยไม่มีใครสังเกต
เพราะมันทำให้ทุกอย่างที่อยู่ปลายน้ำดูน่าเชื่อถือทั้งที่ไม่มีฐานรองรับ
"""
from dataclasses import dataclass, field
from enum import Enum


class Level(str, Enum):
    VERIFIED = "VERIFIED"
    ASSERTED = "ASSERTED"
    CONTRADICTED = "CONTRADICTED"


class Verdict(str, Enum):
    PASS = "PASS"                 # สายงานเดินได้ · เงื่อนไขที่เหลือมีกลไกบังคับของตัวเอง
    CORRECTED = "CORRECTED"       # พบข้อบกพร่องที่แก้ได้เอง แก้แล้ว ต้องตรวจซ้ำ
    BLOCKED = "BLOCKED"           # สายงานเดินต่อไม่ได้


class Blocks(str, Enum):
    """สิ่งที่ข้ออ้างซึ่งยังไม่มีฐาน กำลังกั้นอยู่

    การออกแบบเดิมมีชั้นเดียว — ข้ออ้างที่ยังไม่มีฐานกั้น "ประตู" แล้วทั้งสายงานหยุด
    ซึ่งใช้ไม่ได้กับสิ่งที่มีวงจรชีวิตต่อเนื่อง

    เนื้อหาท่าออกกำลังกายเป็นข้อมูลที่ถูกเพิ่มและแก้ไปเรื่อยๆ
    จะมีท่าที่รอตรวจอยู่เสมอเป็นเรื่องปกติของการใช้งานจริง
    ถ้าท่าหนึ่งท่าที่ยังไม่ถูกตรวจหยุดทั้งสายงานได้
    **สายงานจะไม่มีวันถึง PASS เลย** ซึ่งแปลว่าคำตัดสินนั้นไม่มีความหมาย

    ทางแก้ไม่ใช่เลิกตรวจ แต่คือแยกให้ชัดว่าอะไรกั้นอะไร
    """

    PIPELINE = "pipeline"
    """กั้นสายงาน · ระบบยังไม่ถูกต้อง เดินต่อไม่ได้"""

    PUBLICATION = "publication"
    """กั้นการเผยแพร่เนื้อหาสู่ผู้ใช้จริง · ระบบถูกต้องแล้ว แต่เนื้อหายังไม่พร้อม"""

    OUTCOME_CLAIM = "outcome_claim"
    """กั้นการอ้างว่าโครงการได้ผล · ยังไม่มีข้อมูลวัดจริง
    ระบบและเนื้อหาเดินต่อได้ แต่ห้ามเขียนว่าตัวชี้วัดบรรลุแล้ว"""


@dataclass
class Claim:
    """ข้ออ้างหนึ่งข้อ พร้อมวิธีที่ใช้ตัดสิน"""
    id: str
    text: str
    level: Level
    evidence: str = ""            # คำสั่งหรือไฟล์ที่ใช้ตรวจ · ว่างได้เฉพาะชั้น ASSERTED
    fix: str | None = None        # คำสั่งที่แก้ได้เอง ถ้ามี
    blocks: "Blocks | None" = None   # สิ่งที่ข้ออ้างนี้กั้นอยู่
    blocks_gate: str | None = None   # ประตูที่เกี่ยวข้อง · ใช้ในรายงานเท่านั้น
    enforced_by: str = ""            # กลไกที่บังคับเงื่อนไขนี้อยู่แล้ว

    def __post_init__(self):
        if self.level is Level.VERIFIED and not self.evidence:
            raise ValueError(f"{self.id}: ข้ออ้างชั้น VERIFIED ต้องระบุหลักฐานที่ตรวจซ้ำได้")


@dataclass
class Report:
    claims: list[Claim] = field(default_factory=list)
    corrections: list[str] = field(default_factory=list)

    def add(self, c: Claim) -> None:
        self.claims.append(c)

    @property
    def contradicted(self) -> list[Claim]:
        return [c for c in self.claims if c.level is Level.CONTRADICTED]

    @property
    def asserted(self) -> list[Claim]:
        return [c for c in self.claims if c.level is Level.ASSERTED]

    @property
    def verified(self) -> list[Claim]:
        return [c for c in self.claims if c.level is Level.VERIFIED]

    @property
    def standing(self) -> list[Claim]:
        """เงื่อนไขที่ยังเปิดอยู่ แต่ไม่ได้กั้นสายงาน

        แต่ละข้อ **ต้องมีกลไกบังคับของตัวเองใน `enforced_by`**
        เงื่อนไขที่ไม่มีกลไกบังคับ ไม่ใช่เงื่อนไข แต่เป็นความหวัง
        และความหวังที่ถูกเขียนไว้ในรายงาน คือสิ่งที่ทุกคนอ่านผ่านตั้งแต่ครั้งที่สอง
        """
        return [c for c in self.asserted
                if c.blocks in (Blocks.PUBLICATION, Blocks.OUTCOME_CLAIM)]

    def verdict(self) -> Verdict:
        """ลำดับความสำคัญ

        ขัดแย้งที่แก้ได้เอง                    → CORRECTED
        ขัดแย้งที่แก้เองไม่ได้                  → BLOCKED
        ยังไม่มีฐาน และกั้นสายงาน                → BLOCKED
        ยังไม่มีฐาน กั้นการเผยแพร่ แต่มีกลไกบังคับ → PASS
        ยังไม่มีฐาน กั้นการเผยแพร่ แต่ไม่มีกลไก    → BLOCKED

        แถวสุดท้ายสำคัญที่สุด · การย้ายเงื่อนไขออกจากคำตัดสิน
        ต้องแลกด้วยการมีกลไกอื่นบังคับมันจริง ไม่ใช่แค่ลดระดับความรุนแรง
        """
        if any(c.fix for c in self.contradicted):
            return Verdict.CORRECTED
        if self.contradicted:
            return Verdict.BLOCKED
        if any(c.blocks is Blocks.PIPELINE for c in self.asserted):
            return Verdict.BLOCKED
        if any(c.blocks in (Blocks.PUBLICATION, Blocks.OUTCOME_CLAIM) and not c.enforced_by
               for c in self.asserted):
            return Verdict.BLOCKED
        return Verdict.PASS
