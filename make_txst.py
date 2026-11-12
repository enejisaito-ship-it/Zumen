# -*- coding: utf-8 -*-
"""ヘクサロビュラ穴付き段付きボルト (TX-ST 形) 2 種の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

株式会社ニコン様のお問合せ (管理番号 TEMP-AB12CD) から起こした図面。
- ピン無し M3・L3・F6 (弊社 TX-ST の M3 寸法で、段部の径 D だけ 5 から 4 に変更)
- ピン付き (いじり止め) M3・L2・F8 (同じ頭部と D4 で、穴の中心にピンを立てる)
寸法の記号は TX-ST の寸法表に合わせる: A 頭部の径、E 頭部の高さ、D 段部の径、L 段部の長さ、
F ねじ部の長さ、T 穴の呼び、h1 穴の深さ。
材質は鉄、表面処理は Ni-Cr めっき (お客様のご指定)。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, arrow, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402

THICK, THIN = 6, 1
COMMON = {
    "A": 8.0,      # 頭部の径 (TX-ST M3)
    "E": 2.0,      # 頭部の高さ (TX-ST M3)
    "D": 4.0,      # 段部の径 (お客様のご指定。TX-ST 標準は 5)
    "d": 3.0,      # ねじの呼び径 M3
    "p": 0.5,      # ピッチ (並目)
    "d1": 2.46,    # ねじの谷の径 (図の線用。寸法は入れない)
    "c": 0.3,      # ねじ先の面取り (図の形だけ)
    "T": "T10",    # 穴の呼び (TX-ST M3)
    "h1": 2.0,     # 穴の深さ (TX-ST M3)
    "ta": 2.8,     # T10 穴の山の径 (図の形だけ。ISO 10664 の A)
    "tb": 2.05,    # T10 穴の谷の径 (図の形だけ。ISO 10664 の B)
    "tip": 0.6,    # 穴の底の円すい部 (図の形だけ)
    "dp": 1.0,     # ピンの径 (図の形だけ。寸法は入れない)
    "pt": 0.2,     # ピン先端の頭部上面からの下がり (図の形だけ)
}
SCALE = 5.0
TITLE = {"品番": "", "図番": "", "得意先": "株式会社ニコン", "尺度": "5/1",
         "材質": "鉄", "表面処理": "Ni-Crめっき"}
PARTS = [
    {"L": 3.0, "F": 6.0, "pin": False,
     "品名": "ヘクサロビュラ穴付き段付きボルト M3×L3×F6",
     "file": "ヘクサロビュラ穴付き段付きボルト_M3xL3xF6.pdf"},
    {"L": 2.0, "F": 8.0, "pin": True,
     "品名": "ピン付きヘクサロビュラ穴付き段付きボルト M3×L2×F8",
     "file": "ピン付きヘクサロビュラ穴付き段付きボルト_M3xL2xF8.pdf"},
]


def fmt(v):
    return f"{v:g}"


def notes(sh, lines, y0=0.0, size=3.5):
    """注記。書式の訂正欄 (y = -54 より下) にかからないよう、図と表題欄の間の左側に書く。"""
    sh.text(-130.0, y0, "注記", 4.0)
    y = y0 - 7.0
    for s in lines:
        for j, part in enumerate(s.split("\n")):
            sh.text(-126.0 + (4.0 if j else 0.0), y, part, size)
            y -= size + 2.0


def draw_bolt(sh, part, s=COMMON):
    S = SCALE
    rA, rD, rd, r1 = s["A"] / 2, s["D"] / 2, s["d"] / 2, s["d1"] / 2
    E, L, F, c = s["E"], part["L"], part["F"], s["c"]
    xs, xt = E, E + L                     # 段部の始まり、ねじ部の始まり
    xe = xt + F                           # ねじ先
    Y0 = 42.0
    gap = 32.0
    left = -(S * s["A"] + gap + S * xe) / 2
    HX = left + S * rA
    X0 = HX + S * rA + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 外形 (頭部を左、ねじ先を右)
    sh.line(*P(0, -rA), *P(0, rA), THICK)                           # 頭部上面
    sh.line(*P(E, -rA), *P(E, rA), THICK)                           # 頭部の座面
    sh.line(*P(xt, -rD), *P(xt, rD), THICK)                         # 段部の端面
    sh.line(*P(xe, -(rd - c)), *P(xe, rd - c), THICK)               # 先端面
    for sg in (1, -1):
        sh.line(*P(0, sg * rA), *P(E, sg * rA), THICK)              # 頭部の外周
        sh.line(*P(xs, sg * rD), *P(xt, sg * rD), THICK)            # 段部
        sh.line(*P(xt, sg * rd), *P(xe - c, sg * rd), THICK)        # ねじの山の径
        sh.line(*P(xe - c, sg * rd), *P(xe, sg * (rd - c)), THICK)  # ねじ先の面取り
        sh.line(*P(xt, sg * r1), *P(xe, sg * r1), THIN)             # ねじの谷の径 (細線)

    # ---- 穴 (かくれ線)
    ra, rb, h1 = s["ta"] / 2, s["tb"] / 2, s["h1"]
    for sg in (1, -1):
        sh.line(*P(0, sg * ra), *P(h1, sg * ra), THIN, 2)           # 穴の山
        sh.line(*P(0, sg * rb), *P(h1, sg * rb), THIN, 2)           # 穴の谷
        sh.line(*P(h1, sg * ra), *P(h1 + s["tip"], 0), THIN, 2)     # 穴の底の円すい
    sh.line(*P(h1, -ra), *P(h1, ra), THIN, 2)
    if part["pin"]:
        rp, pt = s["dp"] / 2, s["pt"]
        bot = h1 + s["tip"] * (1 - rp / ra)                         # ピンの根元 = 円すいとの交わり
        sh.line(*P(pt, -rp), *P(pt, rp), THIN, 2)                   # ピンの先端
        for sg in (1, -1):
            sh.line(*P(pt, sg * rp), *P(bot, sg * rp), THIN, 2)
    sh.line(*P(-0.6, 0), *P(xe + 0.6, 0), THIN, 6)                  # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rA, THICK)
    n = 180
    pts = []
    for i in range(n + 1):                                          # T10 穴 (6 つの山の略図)
        t = 2 * math.pi * i / n
        r = (ra + rb) / 2 + (ra - rb) / 2 * math.cos(6 * t)
        pts.append((HX + S * r * math.cos(t), Y0 + S * r * math.sin(t)))
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        sh.line(x1, y1, x2, y2, THICK)
    if part["pin"]:
        sh.circle(HX, Y0, S * s["dp"] / 2, THICK)                   # ピン
    sh.line(HX - S * rA - 3, Y0, HX + S * rA + 3, Y0, THIN, 6)
    sh.line(HX, Y0 - S * rA - 3, HX, Y0 + S * rA + 3, THIN, 6)

    # ---- 寸法
    top = Y0 + S * rA + 8.0
    hdim(sh, P(0, 0)[0], P(E, 0)[0], top, P(0, rA)[1], P(E, rA)[1], fmt(E), outside=True)
    hdim(sh, P(xs, 0)[0], P(xt, 0)[0], top, P(xs, rA)[1], P(xt, rD)[1], fmt(L))
    hdim(sh, P(xt, 0)[0], P(xe, 0)[0], top, P(xt, rD)[1], P(xe, rd - c)[1], fmt(F))
    bot = Y0 - S * rA - 9.0
    hdim(sh, P(0, 0)[0], P(xe, 0)[0], bot, P(0, -rA)[1], P(xe, -(rd - c))[1], f"({fmt(xe)})")
    hdim(sh, HX - S * rA, HX + S * rA, bot, Y0, Y0, f"φ{fmt(s['A'])}")
    # 段部の径: 段部の中に寸法線を引く
    xm = P(xt, 0)[0] - 1.5                                          # 穴のかくれ線をよけて段部の右寄り
    y1, y2 = P(0, -rD)[1], P(0, rD)[1]
    sh.line(xm, y1, xm, y2, THIN)
    arrow(sh, xm, y1, 0, -1)
    arrow(sh, xm, y2, 0, 1)
    sh.text(xm - 1.0, Y0 - S * rD * 0.5, f"φ{fmt(s['D'])}", 4.0, ang=90, align="C")
    # ねじの呼び: 文字を F の寸法補助線 2 本の間に置き、補助線と重ねない
    leader(sh, *P(xt + F * 0.6, rd), P(xt, 0)[0] + 4.0, Y0 + S * rA - 2.0,
           f"M{fmt(s['d'])}×{fmt(s['p'])}")
    label = ("ピン付き" if part["pin"] else "") + f"ヘクサロビュラ {s['T']}"
    ang = math.radians(120)
    leader(sh, HX + S * ra * math.cos(ang) * 0.95, Y0 + S * ra * math.sin(ang) * 0.95,
           HX - S * rA * 0.5, Y0 + S * rA + 6.0, label, size=3.5, side="L", sub=f"深さ {fmt(h1)}")


def note_lines(part):
    return ["普通公差は JIS B 0405-m とする。"]


def main(out):
    for part in PARTS:
        sh = Sheet()
        load_template(sh)
        fill_title(sh, dict(TITLE, 品名=part["品名"]))
        draw_bolt(sh, part)
        notes(sh, note_lines(part))
        render(sh, os.path.join(out, part["file"]), part["品名"])
        print("ok", part["file"])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
