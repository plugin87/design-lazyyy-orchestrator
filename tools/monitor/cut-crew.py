"""Cut a lineup sheet into N transparent figures.
import pathlib

Reusable: the eight-character sheet and the three-character sheet are the same
problem, so the counting is derived from the widths rather than hard-coded.
"""
import sys, zlib, struct
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from png import read

SRC, NAMES = sys.argv[1], sys.argv[2].split(',')
ART = '/Users/plug/Development/design-lazyyy/skills/tools/monitor/public/art'
w, h, ch, _, px, _, _ = read(SRC)

def bg(i):
    r, g, b = px[i], px[i+1], px[i+2]
    return max(r,g,b) - min(r,g,b) <= 10 and min(r,g,b) >= 233

mask = bytearray(w*h); q = deque()
for x in range(w):
    for y in (0, h-1):
        p = y*w+x
        if not mask[p] and bg(p*ch): mask[p]=1; q.append(p)
for y in range(h):
    for x in (0, w-1):
        p = y*w+x
        if not mask[p] and bg(p*ch): mask[p]=1; q.append(p)
while q:
    p = q.popleft(); x, y = p%w, p//w
    for nx, ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
        if 0 <= nx < w and 0 <= ny < h:
            n = ny*w+nx
            if not mask[n] and bg(n*ch): mask[n]=1; q.append(n)

col = [any(not mask[y*w+x] for y in range(0,h,2)) for x in range(w)]
runs, st = [], None
for x, on in enumerate(col+[False]):
    if on and st is None: st = x
    elif not on and st is not None:
        if x-st > 40: runs.append((st, x-1))
        st = None
print('runs:', [(a, b-a+1) for a,b in runs])

dens = [sum(0 if mask[y*w+x] else 1 for y in range(0,h,4)) for x in range(w)]
widths = [b-a+1 for a,b in runs]
single = min(widths) if len(runs) >= len(NAMES) else round(sum(widths)/len(NAMES))
cuts = []
for a, b in runs:
    n = max(1, round((b-a+1)/single))
    if n == 1: cuts.append((a,b)); continue
    edges = [a]
    for k in range(1, n):
        g = a + round((b-a+1)*k/n)
        lo, hi = max(a+30, g-60), min(b-30, g+60)
        edges.append(min(range(lo,hi), key=lambda x: dens[x]))
    edges.append(b)
    for i in range(n): cuts.append((edges[i]+(1 if i else 0), edges[i+1]))
print('figures:', len(cuts))
if len(cuts) != len(NAMES): sys.exit(f'!! ได้ {len(cuts)} ตัว ต้องการ {len(NAMES)}')

def write_png(path, W, H, rgba):
    raw = b''.join(b'\x00'+bytes(rgba[y*W*4:(y+1)*W*4]) for y in range(H))
    def c(t,b):
        x = struct.pack('>I',len(b))+t+b
        return x+struct.pack('>I', zlib.crc32(t+b)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+c(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))
        +c(b'IDAT',zlib.compress(raw,9))+c(b'IEND',b''))

floor = max(y for y in range(h) if any(not mask[y*w+x] for x in range(w)))
for name,(x0,x1) in zip(NAMES, cuts):
    ys = [y for y in range(h) if any(not mask[y*w+x] for x in range(x0,x1+1))]
    y0, y1 = max(0,min(ys)-8), min(h-1, floor+4)
    x0p, x1p = max(0,x0-4), min(w-1,x1+4)
    W, H = x1p-x0p+1, y1-y0+1
    buf = bytearray(W*H*4)
    for y in range(H):
        for x in range(W):
            sp=(y0+y)*w+(x0p+x); si=sp*ch; di=(y*W+x)*4
            buf[di:di+3]=px[si:si+3]
            buf[di+3]=0 if mask[sp] else (110 if bg(si) else 255)
    write_png(f'{ART}/crew-{name}.png', W, H, buf)
    print(f'  crew-{name}.png {W}x{H}')
