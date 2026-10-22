# -*- coding: utf-8 -*-
"""六角リーマボルト M8 × 首下 47 の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

得意先の現品測定値 (Excel) から起こした。測定値: 全長 52.63、二面幅 13 (スパナ)、頭部高さ 5.8、
首下 46.89、胴径 9.8〜9.9、胴長さ 26 (スケール)、ねじ山径 7.74、ねじ長さ 18.5 (スケール)、
胴の両端に斜めのくびれ (長さは 1〜2 の推定)。
胴 φ9.9 の両端は C2 の面取りとし、ねじ部は元資料の通り先端から 18.5 で、ねじ側の面取りの斜面上に終わるとした。
ピッチは測定がないので並目 1.25 とした。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width, tol_text)

B = {
    "s": 13.0,       # 二面幅
    "k": 5.8,        # 頭部高さ
    "d": 8.0,        # ねじの呼び径 M8
    "p": 1.25,       # ピッチ (並目と仮定)
    "d1": 6.647,     # おねじの谷の径 (図の線用)
    "ds": 9.9,       # 胴径
    "ds_tol": ("0", "-0.05"),
    "cs": 2.0,       # 胴の両端の面取り (C2)
    "lth": 18.5,     # ねじ部の長さ (先端から。ねじ側の面取りの斜面上で終わる)
    "lb": 26.0,      # 胴の円筒部の長さ
    "l": 47.0,       # 首下長さ
    "ce": 0.8,       # ねじ先の面取り
}
TITLE = {"品番": "", "図番": "", "得意先": "", "品名": "リーマボルト M8×47", "尺度": "3/1", "材質": ""}
FILE = "リーマボルト_M8x47.pdf"
SCALE = 3.0


def fmt(v):
    return f"{v:g}"


def hdim_fit(sh, x1, x2, y, f1, f2, label, size=4.5):
    """hdim と同じ。数値が寸法線の間に収まらないときは、矢印を外側から当て、数値を左の外側に書く。"""
    w = text_width(label, size, 0.5)
    if w + 2.0 <= x2 - x1:
        hdim(sh, x1, x2, y, f1, f2, label, size)
        return
    hdim(sh, x1, x2, y, f1, f2, "", size, outside=True)
    sh.line(x1 - w - 2.0, y, x1, y)
    sh.text(x1 - 1.5, y + 1.0, label, size, align="R")


def curve3(sh, P, a, b, c, n=16):
    """3 点 a, b, c (b は y が中央) を通る x = f(y) の 2 次曲線を太線で描く。面取りの線の近似。"""
    (xa, ya), (xb, yb), (xc, yc) = a, b, c
    pts = []
    for i in range(n + 1):
        y = ya + (yc - ya) * i / n
        la = (y - yb) * (y - yc) / ((ya - yb) * (ya - yc))
        lb = (y - ya) * (y - yc) / ((yb - ya) * (yb - yc))
        lc = (y - ya) * (y - yb) / ((yc - ya) * (yc - yb))
        pts.append(P(xa * la + xb * lb + xc * lc, y))
    for p, q in zip(pts, pts[1:]):
        sh.line(*p, *q, 6)


def draw_bolt(sh):
    S = SCALE
    s, k = B["s"], B["k"]
    e = s / math.cos(math.radians(30))                 # 対角距離 (図の線用)
    rd, r1, rs, cs = B["d"] / 2, B["d1"] / 2, B["ds"] / 2, B["cs"]
    rn = rs - cs                                       # 首下側の面取りの座面での半径
    ch = (e / 2 - s / 2) * math.tan(math.radians(30))  # 頭部上面の 30° 面取りの角での深さ
    x1 = k + cs                                        # 胴の円筒部の始まり
    x2 = x1 + B["lb"]                                  # 胴の円筒部の終わり
    x3 = x2 + (rs - rd)                                # ねじ側の面取り (45°) が山の径と交わる位置
    L = k + B["l"]                                     # 全長
    xt = L - B["lth"]                                  # ねじ部の終わり (ねじ側の面取りの斜面上)
    assert x2 < xt < x3
    rt = rs - (xt - x2)                                # ねじ部の終わりでの面取りの半径
    ce = B["ce"]
    Y0 = 25.0
    gap = 30.0
    left = -(S * e + gap + S * L) / 2
    HX = left + S * e / 2
    X0 = HX + S * e / 2 + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (頭部を左、ねじ先を右。六角は角を上下に向ける)
    for sg in (1, -1):
        sh.line(*P(0, sg * s / 2), *P(ch, sg * e / 2), 6)          # 面取りの外形
        sh.line(*P(ch, sg * e / 2), *P(k, sg * e / 2), 6)          # 頭部の外形 (角)
        sh.line(*P(ch, sg * e / 4), *P(k, sg * e / 4), 6)          # 六角の稜線
        curve3(sh, P, (ch, sg * e / 4), (0, sg * s / 2 * math.sin(math.radians(60))), (ch, sg * e / 2))
        sh.line(*P(k, sg * e / 2), *P(k, sg * rn), 6)              # 座面
        sh.line(*P(k, sg * rn), *P(x1, sg * rs), 6)                # 首下側の C2 面取り
        sh.line(*P(x1, sg * rs), *P(x2, sg * rs), 6)               # 胴
        sh.line(*P(x2, sg * rs), *P(x3, sg * rd), 6)               # ねじ側の C2 面取り
        sh.line(*P(x3, sg * rd), *P(L - ce, sg * rd), 6)           # ねじの山の径
        sh.line(*P(L - ce, sg * rd), *P(L, sg * (rd - ce)), 6)     # ねじ先の面取り
        sh.line(*P(xt, sg * r1), *P(L, sg * r1), 1)                # ねじの谷の径 (細線)
    sh.line(*P(0, -s / 2), *P(0, s / 2), 6)                        # 頭部上面
    curve3(sh, P, (ch, -e / 4), (0, 0), (ch, e / 4))
    for x in (x1, x2):
        sh.line(*P(x, -rs), *P(x, rs), 6)                          # 面取りと胴の境
    sh.line(*P(xt, -rt), *P(xt, rt), 6)                            # ねじ部の終わり (面取りの斜面上)
    sh.line(*P(L, -(rd - ce)), *P(L, rd - ce), 6)                  # 先端面
    sh.line(*P(-0.5, 0), *P(L + 0.5, 0), 1, 6)                     # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    R = S * e / 2
    pts = [(HX + R * math.cos(math.radians(90 + 60 * i)), Y0 + R * math.sin(math.radians(90 + 60 * i)))
           for i in range(7)]
    for p, q in zip(pts, pts[1:]):
        sh.line(*p, *q, 6)
    sh.circle(HX, Y0, S * s / 2, 6)                                # 面取りの円
    sh.line(HX - R - 3, Y0, HX + R + 3, Y0, 1, 6)
    sh.line(HX, Y0 - R - 3, HX, Y0 + R + 3, 1, 6)
    hdim(sh, HX - S * s / 2, HX + S * s / 2, Y0 - R - 8.0, Y0 - S * e / 4, Y0 - S * e / 4, fmt(s))

    # ---- 寸法
    top = Y0 + R + 8.0
    hdim(sh, P(0, 0)[0], P(k, 0)[0], top, P(0, s / 2)[1], P(k, e / 2)[1], fmt(k))
    bot = Y0 - R - 8.0
    hdim(sh, P(x1, 0)[0], P(x2, 0)[0], bot, P(x1, -rs)[1], P(x2, -rs)[1], fmt(B["lb"]))
    hdim(sh, P(xt, 0)[0], P(L, 0)[0], bot, P(xt, -rt)[1], P(L, -(rd - ce))[1], fmt(B["lth"]))
    hdim(sh, P(k, 0)[0], P(L, 0)[0], bot - 10.0, P(k, -e / 2)[1], P(L, -(rd - ce))[1], fmt(B["l"]))
    # 胴径 (許容差付き。胴の中で寸法線を引く)
    xv = P(x1 + 9.0, 0)[0]
    sh.line(xv, P(0, -rs)[1], xv, P(0, rs)[1])
    arrow(sh, xv, P(0, -rs)[1], 0, -1)
    arrow(sh, xv, P(0, rs)[1], 0, 1)
    tol_text(sh, xv - 1.0, Y0 - 7.0, f"φ{fmt(B['ds'])}", *B["ds_tol"])
    # 胴の両端の面取り
    leader(sh, *P(k + cs / 2, rn + cs / 2), P(k, 0)[0] + 12.0, Y0 + R + 4.0, f"C{fmt(cs)}")
    leader(sh, *P(x2 + 0.25, rs - 0.25), P(x2, 0)[0] - 10.0, Y0 + R + 4.0, f"C{fmt(cs)}", side="L")
    # ねじ
    leader(sh, *P(L - 4.0, rd), P(L, 0)[0] - 6.0, Y0 + R + 2.0, f"M{fmt(B['d'])}×{fmt(B['p'])}-6g")
    leader(sh, *P(L - ce / 2, -(rd - ce / 2)), P(L, 0)[0] + 4.0, Y0 - S * rd - 8.0, f"C{fmt(ce)}")

    # ---- 注記
    sh.text(-130.0, -40.0, "注記", 4.0)
    sh.text(-126.0, -47.0, "1. 普通公差は JIS B 0405-m (中級) とする。", 3.5)


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw_bolt(sh)
    render(sh, os.path.join(out, FILE), TITLE["品名"])
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
