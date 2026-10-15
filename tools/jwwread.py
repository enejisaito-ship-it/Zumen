"""JWW (Jw_cad) ファイルの図形 (線・文字・円弧・点・ソリッド・寸法) を読み出す。

使い方: python3 -I jwwread.py <file.jww> <out.json>
"""
import json
import struct
import sys


class R:
    def __init__(self, d, pos):
        self.d, self.p = d, pos

    def u8(self):
        v = self.d[self.p]; self.p += 1; return v

    def u16(self):
        v = struct.unpack_from('<H', self.d, self.p)[0]; self.p += 2; return v

    def u32(self):
        v = struct.unpack_from('<I', self.d, self.p)[0]; self.p += 4; return v

    def f64(self):
        v = struct.unpack_from('<d', self.d, self.p)[0]; self.p += 8; return v

    def cstr(self):
        n = self.u8()
        if n == 0xFF:
            n = self.u16()
            if n == 0xFFFF:
                n = self.u32()
        s = self.d[self.p:self.p + n]; self.p += n
        return s.decode('cp932', errors='replace')


def base(r, ver):
    g = r.u32(); style = r.u8(); color = r.u16()
    width = r.u16() if ver >= 351 else 0
    layer = r.u16(); glayer = r.u16(); flg = r.u16()
    return dict(group=g, style=style, color=color, width=width, layer=layer, glayer=glayer, flg=flg)


def sen(r, ver):
    b = base(r, ver)
    b.update(type='line', x1=r.f64(), y1=r.f64(), x2=r.f64(), y2=r.f64())
    return b


def moji(r, ver):
    b = base(r, ver)
    b.update(type='text', x1=r.f64(), y1=r.f64(), x2=r.f64(), y2=r.f64(), kind=r.u32(),
             sx=r.f64(), sy=r.f64(), sp=r.f64(), ang=r.f64(), font=r.cstr(), s=r.cstr())
    return b


def enko(r, ver):
    b = base(r, ver)
    b.update(type='arc', cx=r.f64(), cy=r.f64(), r=r.f64(), a0=r.f64(), da=r.f64(),
             tilt=r.f64(), flat=r.f64(), full=r.u32())
    return b


def ten(r, ver):
    b = base(r, ver)
    b.update(type='point', x=r.f64(), y=r.f64(), kari=r.u32())
    if b['style'] == 100:
        b.update(code=r.u32(), rot=r.f64(), scale=r.f64())
    return b


def solid(r, ver):
    b = base(r, ver)
    b.update(type='solid', pts=[r.f64() for _ in range(8)])
    if b['color'] == 10:
        b['rgb'] = r.u32()
    return b


def sunpou(r, ver):
    b = base(r, ver)
    b['type'] = 'dim'
    b['line'] = sen(r, ver)
    b['text'] = moji(r, ver)
    if ver >= 420:
        b['sxf'] = r.u16()
        b['ho'] = [sen(r, ver), sen(r, ver)]
        b['pts'] = [ten(r, ver) for _ in range(6)]
    return b


def block(r, ver):
    b = base(r, ver)
    b.update(type='block', x=r.f64(), y=r.f64(), sx=r.f64(), sy=r.f64(), ang=r.f64(), num=r.u32())
    return b


READERS = {'CDataSen': sen, 'CDataMoji': moji, 'CDataEnko': enko, 'CDataTen': ten,
           'CDataSolid': solid, 'CDataSunpou': sunpou, 'CDataBlock': block}


def read_list(r, ver):
    n = r.u16()
    if n == 0xFFFF:
        n = r.u32()
    cmap = {}
    count = 1
    out = []
    for _ in range(n):
        tag = r.u16()
        if tag == 0xFFFF:
            r.u16()  # schema
            ln = r.u16()
            name = r.d[r.p:r.p + ln].decode('ascii'); r.p += ln
            cmap[count] = name; count += 1
        elif tag & 0x8000:
            name = cmap[tag & 0x7FFF]
        else:
            raise ValueError(f'unexpected tag {tag:#x} at {r.p}')
        out.append(READERS[name](r, ver))
        count += 1
    return out


def main(src, dst):
    d = open(src, 'rb').read()
    ver = struct.unpack_from('<I', d, 8)[0]
    i = d.find(b'\xff\xff', 0)
    # 図形リストの先頭: 最初の新規クラスタグ (FFFF + schema + 名前長 + "CData")
    j = d.find(b'CData')
    start = j - 6 - 2
    r = R(d, start)
    ents = read_list(r, ver)
    json.dump({'version': ver, 'start': start, 'end': r.p, 'size': len(d), 'entities': ents},
              open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('version', ver, 'entities', len(ents), 'end', r.p, 'of', len(d))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
