#!/usr/bin/env python3
"""Draw the project Gantt chart as SVG and PNG.

Accompanies the project schedule document, SCH-XXX-001.

Usage
    python3 tools/gen-gantt.py

Edit only the "Schedule data" section below; the rest is drawing code.

A note on size
    Keep the image under roughly 950 pixels wide. The content area of an A4 page
    is 160mm, about 605 pixels — an image wider than that gets scaled down until
    the labels are unreadable in print. The script warns when the resulting type
    size would fall below 10pt.
"""

from datetime import date, timedelta
import pathlib
import subprocess
import sys

# ─────────────────────────────────────────────────────────────
# Schedule data · edit only this section
# ─────────────────────────────────────────────────────────────

# Project start date. Must be a Monday, and must match SCH-XXX-001.
START = date(2026, 8, 31)

# Axis range, set slightly wider than the work itself so the chart breathes.
# Keep AXIS_TO at least two weeks past the last milestone, or its label is
# clipped at the right edge of the canvas.
AXIS_FROM = date(2026, 8, 24)
AXIS_TO = date(2026, 12, 4)

# Work packages · (short label, start week, end week) — weeks counted from START
# Keep labels short; the label column is only 300 pixels wide.
# Full names belong in the work breakdown table of WBS-XXX-001.
#
# Replace the example below with the project's real work.
TASKS = [
    ("1 ข้อกำหนดและแบบระบบ", 1, 3),
    ("2 ระบบออกแบบ", 2, 4),
    ("3 ค้นหาและเรียกดู", 3, 6),
    ("4 หน้ารายละเอียดท่า", 5, 7),
    ("5 ผลิตเนื้อหา 30 ท่า", 3, 7),
    ("6 สถิติและหน้าดูสถิติ", 7, 8),
    ("7 ทดสอบและแก้", 8, 10),
    ("8 โค้ชตรวจรับรอง", 7, 11),
    ("9 วัดค่าฐานจากผู้ใช้", 8, 11),
    ("10 ตรวจคุณภาพและปล่อย", 11, 12),
]

# Milestones · (id, week, is it a decision point)
# Decision points are drawn in the accent colour.
#
# Two milestones in the same week draw their labels on top of each other and
# neither is readable. Put them in different weeks, or merge them into one.
MILESTONES = [
    ("G1", 1, True),
    ("G2", 2, True),
    ("G3", 4, False),
    ("G4", 10, False),
    ("G5", 11, False),
    ("G6", 12, True),
]

# ─────────────────────────────────────────────────────────────
# Drawing constants · rarely need changing
# ─────────────────────────────────────────────────────────────

LABEL_W, CHART_W = 300, 600      # label column width, chart area width
PAD_L, PAD_T = 14, 12
HEAD_H, ROW_H, MS_H = 46, 48, 62
FONT_LABEL, FONT_MONTH = 21, 18

COL_BAR = "#0E6B75"              # work bar
COL_CRIT = "#A33528"             # decision-point milestone
COL_MS = "#3A4247"               # ordinary milestone
COL_TEXT = "#15191A"
COL_GRID = "#DCE0E1"
COL_STRIPE = "#F3F5F5"

PAGE_W_PX = 605                  # A4 content-area width in pixels
MIN_PT = 10                      # smallest type size acceptable in print

# Rendered into the image itself, which goes into a Thai document — keep Thai
TH_MONTH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
            "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]

ROOT = pathlib.Path(__file__).resolve().parent.parent
SVG_OUT = ROOT / "project" / "assets" / "gantt.svg"
PNG_OUT = ROOT / "project" / "assets" / "gantt.png"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def round_start(n):
    return START + timedelta(weeks=n - 1)


def round_end(n):
    return START + timedelta(weeks=n - 1, days=4)


def build_svg():
    span = (AXIS_TO - AXIS_FROM).days
    width = PAD_L * 2 + LABEL_W + CHART_W
    height = PAD_T + HEAD_H + ROW_H * len(TASKS) + MS_H

    def x_of(d):
        return PAD_L + LABEL_W + (d - AXIS_FROM).days / span * CHART_W

    months, y, m = [], AXIS_FROM.year, AXIS_FROM.month
    while (y, m) <= (AXIS_TO.year, AXIS_TO.month):
        months.append(date(y, m, 1))
        m += 1
        if m == 13:
            y, m = y + 1, 1

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
         f'viewBox="0 0 {width} {height}" font-family="Sarabun, sans-serif">',
         f'<rect width="{width}" height="{height}" fill="#ffffff"/>']

    top = PAD_T + HEAD_H
    bottom = top + ROW_H * len(TASKS)

    for i, mm in enumerate(months):
        mx = x_of(mm)
        o.append(f'<line x1="{mx:.1f}" y1="{PAD_T + 26}" x2="{mx:.1f}" y2="{bottom + 30}" '
                 f'stroke="{COL_GRID}" stroke-width="1"/>')
        if i + 1 < len(months):
            cx = (mx + x_of(months[i + 1])) / 2
            year_suffix = f' {mm.year + 543 - 2500:02d}' if mm.month in (1, 7) else ''
            o.append(f'<text x="{cx:.1f}" y="{PAD_T + 20}" font-size="{FONT_MONTH}" '
                     f'fill="{COL_MS}" text-anchor="middle">{TH_MONTH[mm.month - 1]}{year_suffix}</text>')

    o.append(f'<line x1="{PAD_L + LABEL_W}" y1="{top - 8}" x2="{PAD_L + LABEL_W + CHART_W}" '
             f'y2="{top - 8}" stroke="{COL_TEXT}" stroke-width="2"/>')

    for i, (label, a, b) in enumerate(TASKS):
        ry = top + i * ROW_H
        if i % 2 == 0:
            o.append(f'<rect x="{PAD_L}" y="{ry}" width="{LABEL_W + CHART_W}" '
                     f'height="{ROW_H}" fill="{COL_STRIPE}"/>')
        o.append(f'<text x="{PAD_L + 2}" y="{ry + ROW_H / 2 + 7}" font-size="{FONT_LABEL}" '
                 f'fill="{COL_TEXT}">{label}</text>')
        x1, x2 = x_of(round_start(a)), x_of(round_end(b))
        o.append(f'<rect x="{x1:.1f}" y="{ry + 11}" width="{max(x2 - x1, 4):.1f}" '
                 f'height="{ROW_H - 22}" fill="{COL_BAR}"/>')

    my = bottom + 26
    o.append(f'<line x1="{PAD_L + LABEL_W}" y1="{bottom + 3}" x2="{PAD_L + LABEL_W + CHART_W}" '
             f'y2="{bottom + 3}" stroke="#C6CCCD" stroke-width="1"/>')
    o.append(f'<text x="{PAD_L + 2}" y="{my + 7}" font-size="{FONT_LABEL}" fill="{COL_MS}">หลักหมาย</text>')
    for code, n, is_crit in MILESTONES:
        mx = x_of(round_end(n))
        col = COL_CRIT if is_crit else COL_MS
        o.append(f'<polygon points="{mx:.1f},{my - 10} {mx + 8:.1f},{my} {mx:.1f},{my + 10} '
                 f'{mx - 8:.1f},{my}" fill="{col}"/>')
        o.append(f'<text x="{mx:.1f}" y="{my + 30}" font-size="{FONT_MONTH - 1}" fill="{col}" '
                 f'text-anchor="middle" font-weight="700">{code}</text>')

    o.append('</svg>')
    return "\n".join(o), width, height


def main():
    svg, width, height = build_svg()
    SVG_OUT.parent.mkdir(parents=True, exist_ok=True)
    SVG_OUT.write_text(svg)

    printed_pt = FONT_LABEL * PAGE_W_PX / width * 0.75
    print(f"image {width} x {height} px")
    print(f"label type size when printed: {printed_pt:.1f}pt")
    if printed_pt < MIN_PT:
        print(f"\nwarning: below {MIN_PT}pt, labels are hard to read in print")
        print("fix by narrowing the image, shortening the labels, or raising FONT_LABEL")

    html = pathlib.Path("/tmp/gantt-render.html")
    html.write_text('<!doctype html><meta charset="utf-8">'
                    '<style>html,body{margin:0;padding:0;background:#fff}</style>' + svg)

    if not pathlib.Path(CHROME).exists():
        print(f"\nChrome not found at {CHROME} — wrote the SVG only")
        sys.exit(1)

    subprocess.run([CHROME, "--headless", "--disable-gpu",
                    "--force-device-scale-factor=3", "--hide-scrollbars",
                    f"--window-size={width},{height + 18}",
                    f"--screenshot={PNG_OUT}", str(html)],
                   capture_output=True)

    print(f"\nwrote\n  {SVG_OUT.relative_to(ROOT)}\n  {PNG_OUT.relative_to(ROOT)}")
    print("\nnext: rebuild the documents with  bash tools/build-docs.sh")


if __name__ == "__main__":
    main()
