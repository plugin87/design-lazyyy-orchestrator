"""Minimal PNG reader — enough to measure the crew sheet without installing anything."""
import zlib, struct, sys

def read(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not a png'
    pos, idat, pal, trns = 8, b'', None, None
    while pos < len(data):
        ln, typ = struct.unpack('>I4s', data[pos:pos+8])
        body = data[pos+8:pos+8+ln]
        if typ == b'IHDR':
            w, h, depth, color, comp, filt, inter = struct.unpack('>IIBBBBB', body)
        elif typ == b'IDAT': idat += body
        elif typ == b'PLTE': pal = body
        elif typ == b'tRNS': trns = body
        elif typ == b'IEND': break
        pos += 12 + ln
    assert depth == 8 and inter == 0, f'depth={depth} interlace={inter} unsupported'
    ch = {0:1, 2:3, 3:1, 4:2, 6:4}[color]
    raw = zlib.decompress(idat)
    stride = w * ch
    out = bytearray(w * h * ch)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if f == 1:
            for i in range(ch, stride): line[i] = (line[i] + line[i-ch]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                b = prev[i]; c = prev[i-ch] if i >= ch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y*stride:(y+1)*stride] = line
        prev = line
    return w, h, ch, color, bytes(out), pal, trns

if __name__ == '__main__':
    w, h, ch, color, px, pal, trns = read(sys.argv[1])
    print(f'{w}x{h} channels={ch} colortype={color} palette={"yes" if pal else "no"} tRNS={"yes" if trns else "no"}')
    def at(x, y):
        i = (y*w + x)*ch
        return tuple(px[i:i+ch])
    print('corners:', at(2,2), at(w-3,2), at(2,h-3), at(w-3,h-3))
    print('between badges (mid gap):', at(w//2, 20), at(375, 250))
