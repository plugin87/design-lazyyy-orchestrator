"""Cut a lineup sheet into transparent figures, one PNG per role.

    python3 tools/monitor/cut-crew.py <sheet.png> name1,name2,…  [out_dir]

Names are given in reading order — left to right along the top row, then left to
right along the row beneath it — and become `crew-<name>.png`.

Why the background is found by flooding rather than by keying white
    A sheet that looks like it has a transparent background usually does not;
    it is opaque white, or a checkerboard baked into the pixels. Keying every
    white pixel is still wrong, because the characters are white in places —
    white fur, a white shirt, the whites of the eyes — and keying punches holes
    straight through them.

    Only white that is *connected to the edge of the sheet* is background, so the
    fill starts at the border and spreads inward. White enclosed by a character
    is never reached, and survives.

Rows
    A sheet is not always one row. Bands of background that run the full width
    separate the rows, so the figures are found band by band and only then
    column by column inside each band. Each band keeps its own floor line, so a
    short row does not get padded down to the tallest row's feet.
"""
import pathlib
import sys
import struct
import zlib
from collections import deque

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from png import read  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent

# The art lives beside the page that loads it. An absolute path baked in here
# once pointed at a different checkout, so this script wrote eleven files that
# the room it belongs to never read.
SRC = sys.argv[1]
NAMES = sys.argv[2].split(',')
ART = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / 'public' / 'art'

MIN_FIGURE_W = 40      # narrower than this is a stray mark, not a character
MIN_BAND_H = 60        # shorter than this is a caption, not a row

# A row of figures is separated from the next by paper, but rarely by *clean*
# paper: one tail, cape or whisker reaching down leaves a handful of pixels in
# the gap. Counting "is there any ink at all" welds the two rows into one, so a
# line has to carry more than a wisp before it counts as occupied.
ROW_INK_MIN = 12
COL_INK_MIN = 3

w, h, ch, _, px, _, _ = read(SRC)


def bg(i):
    """Near-white and near-grey — the sheet's paper, whatever its exact value."""
    r, g, b = px[i], px[i + 1], px[i + 2]
    return max(r, g, b) - min(r, g, b) <= 10 and min(r, g, b) >= 233


# ── flood the paper inward from every edge ────────────────────────────────────
mask = bytearray(w * h)
q = deque()


def seed(p):
    if not mask[p] and bg(p * ch):
        mask[p] = 1
        q.append(p)


for x in range(w):
    seed(x)                      # top edge
    seed((h - 1) * w + x)        # bottom edge
for y in range(h):
    seed(y * w)                  # left edge
    seed(y * w + w - 1)          # right edge

while q:
    p = q.popleft()
    x, y = p % w, p // w
    if x:         seed(p - 1)
    if x < w - 1: seed(p + 1)
    if y:         seed(p - w)
    if y < h - 1: seed(p + w)


def runs_of(flags, minimum):
    """Contiguous True stretches, discarding any shorter than `minimum`."""
    out, start = [], None
    for i, on in enumerate(list(flags) + [False]):
        if on and start is None:
            start = i
        elif not on and start is not None:
            if i - start >= minimum:
                out.append((start, i - 1))
            start = None
    return out


ink_row = [sum(0 if mask[y * w + x] else 1 for x in range(0, w, 2)) > ROW_INK_MIN
           for y in range(h)]
bands = runs_of(ink_row, MIN_BAND_H)
print(f'rows: {len(bands)} → {[(a, b - a + 1) for a, b in bands]}')


# ── figures, band by band ─────────────────────────────────────────────────────
figures = []   # (x0, x1, y_top, y_floor)
for top, bot in bands:
    ink_col = [sum(0 if mask[y * w + x] else 1 for y in range(top, bot + 1, 2)) > COL_INK_MIN
               for x in range(w)]
    cols = runs_of(ink_col, MIN_FIGURE_W)

    # Touching characters share one run. Split it on the thinnest seam rather
    # than in the middle, so the cut misses the bodies and lands in the gap.
    dens = [sum(0 if mask[y * w + x] else 1 for y in range(top, bot + 1, 4)) for x in range(w)]
    widths = [b - a + 1 for a, b in cols]
    single = min(widths) if widths else 0

    for a, b in cols:
        n = max(1, round((b - a + 1) / single)) if single else 1
        if n == 1:
            figures.append((a, b, top, bot))
            continue
        edges = [a]
        for k in range(1, n):
            guess = a + round((b - a + 1) * k / n)
            lo, hi = max(a + 30, guess - 60), min(b - 30, guess + 60)
            edges.append(min(range(lo, hi), key=lambda x: dens[x]) if lo < hi else guess)
        edges.append(b)
        for i in range(n):
            figures.append((edges[i] + (1 if i else 0), edges[i + 1], top, bot))

print(f'figures: {len(figures)}')
if len(figures) != len(NAMES):
    sys.exit(f'!! found {len(figures)} figures but was given {len(NAMES)} names')


def write_png(path, W, H, rgba):
    raw = b''.join(b'\x00' + bytes(rgba[y * W * 4:(y + 1) * W * 4]) for y in range(H))

    def chunk(tag, body):
        return (struct.pack('>I', len(body)) + tag + body
                + struct.pack('>I', zlib.crc32(tag + body) & 0xffffffff))

    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw, 9))
        + chunk(b'IEND', b''))


ART.mkdir(parents=True, exist_ok=True)
for name, (x0, x1, top, bot) in zip(NAMES, figures):
    # Every figure in a row is cut to that row's floor, so they stand on one
    # line when the room places them by their feet.
    floor = max(y for y in range(top, bot + 1)
                if any(not mask[y * w + x] for x in range(w)))
    ys = [y for y in range(top, bot + 1)
          if any(not mask[y * w + x] for x in range(x0, x1 + 1))]
    if not ys:
        sys.exit(f'!! {name}: nothing inside its column')

    y0, y1 = max(top, min(ys) - 8), min(bot, floor + 4)
    xa, xb = max(0, x0 - 4), min(w - 1, x1 + 4)
    W, H = xb - xa + 1, y1 - y0 + 1

    # Figures that touch are separated on a density valley, and a valley is a
    # narrow place, not an empty one — so each cut carries a sliver of whoever
    # stood next to it. In the room that sliver reads as a scrap floating beside
    # the character. Keeping only the largest connected blob drops it, because a
    # figure is one body and a sliver is not attached to it.
    keep = bytearray(W * H)
    best, seen = [], bytearray(W * H)
    for start in range(W * H):
        if seen[start] or mask[(y0 + start // W) * w + (xa + start % W)]:
            continue
        blob, stack, seen[start] = [], [start], 1
        while stack:
            c = stack.pop()
            blob.append(c)
            cx, cy = c % W, c // W
            for nx in range(max(0, cx - 1), min(W, cx + 2)):
                for ny in range(max(0, cy - 1), min(H, cy + 2)):
                    n = ny * W + nx
                    if not seen[n] and not mask[(y0 + ny) * w + (xa + nx)]:
                        seen[n] = 1
                        stack.append(n)
        if len(blob) > len(best):
            best = blob
    for c in best:
        keep[c] = 1

    buf = bytearray(W * H * 4)
    for y in range(H):
        for x in range(W):
            sp = (y0 + y) * w + (xa + x)
            si, di = sp * ch, (y * W + x) * 4
            buf[di:di + 3] = px[si:si + 3]
            # Paper reached by the flood goes fully clear. Paper-coloured pixels
            # the flood never reached are inside the figure, so they stay —
            # dimmed only enough to soften the cut edge.
            buf[di + 3] = 0 if not keep[y * W + x] else (110 if bg(si) else 255)

    # Trim the window back to what survived, so the figure's box is its own.
    cols_on = [x for x in range(W) if any(keep[y * W + x] for y in range(H))]
    rows_on = [y for y in range(H) if any(keep[y * W + x] for x in range(W))]
    if cols_on and rows_on and (len(cols_on) < W or len(rows_on) < H):
        cx0, cx1, cy0, cy1 = cols_on[0], cols_on[-1], rows_on[0], rows_on[-1]
        nW, nH = cx1 - cx0 + 1, cy1 - cy0 + 1
        trimmed = bytearray(nW * nH * 4)
        for y in range(nH):
            src = ((cy0 + y) * W + cx0) * 4
            trimmed[y * nW * 4:(y + 1) * nW * 4] = buf[src:src + nW * 4]
        buf, W, H = trimmed, nW, nH

    write_png(ART / f'crew-{name}.png', W, H, buf)
    print(f'  crew-{name}.png  {W}x{H}')
