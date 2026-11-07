# -*- coding: utf-8 -*-
"""ローレットつまみねじ (ローレット部 φ10 × 高さ 15、ねじ M5 × 25) の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

元の資料: 依頼者の指定 (ローレット部 高さ 15・直径 φ10、ねじ M5×25) と現物の写真 2 枚。
写真から読んだ形 (寸法の指定がないので、写真から決めた値。要確認):
- ローレットは綾目 (斜めに交差した目)。ローレット部の両端の角に面取りがあり、C0.5 とした。
- 頭の端面は平ら (穴やすりわりはない)。
- ねじは座面のきわまで切ってあり、首下の逃げ溝は見えない。ピッチは山の数から並目 0.8 と読んだ。
- ねじ先は面取りしてある。谷の径より少し内側までとして C0.5 とした。
- 正面図は軸を横向きにし、頭部 (ローレット部) を左に置く。頭部側から見た図を左に置く。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402

DK = 10.0       # ローレット部の径
K = 15.0        # ローレット部の高さ
CK = 0.5        # ローレット部の両端の面取り (写真から仮定)
D = 5.0         # ねじの呼び径 M5
P_ = 0.8        # ピッチ (並目)
D1 = 4.134      # おねじの谷の径 (図の線用)
LS = 25.0       # ねじ部の長さ (首下長さ)
CT = 0.5        # ねじ先の面取り
SCALE = 3.0
TITLE = {"品番": "", "図番": "", "得意先": "",
         "品名": "ローレットつまみねじ M5×25", "尺度": "3/1", "材質": ""}
FILE = "ローレットつまみねじ_M5x25.pdf"


def fmt(v):
    return f"{v:g}"


def hatch(sh, poly, ang, pitch):
    """凸多角形 poly の中に、水平から ang 度の細線を間隔 pitch で引く。"""
    a = math.radians(ang)
    nx, ny = -math.sin(a), math.cos(a)              # 線に垂直な向き
    ks = [x * nx + y * ny for x, y in poly]
    k = min(ks) + pitch / 2
    while k < max(ks):
        pts = []
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            u1, u2 = x1 * nx + y1 * ny - k, x2 * nx + y2 * ny - k
            if u1 == u2 or u1 * u2 > 0:
                continue
            t = u1 / (u1 - u2)
            pts.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        if len(pts) >= 2:
            pts.sort()
            sh.line(*pts[0], *pts[-1])
        k += pitch


def draw(sh):
    S = SCALE
    R, rd, r1 = DK / 2, D / 2, D1 / 2
    L = K + LS
    Y0 = 40.0
    gap = 30.0
    left = -(S * DK + gap + S * L + 30.0) / 2
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (頭部を左)
    sh.line(*P(0, -(R - CK)), *P(0, R - CK), 6)                     # 頭の端面
    for sg in (1, -1):
        sh.line(*P(0, sg * (R - CK)), *P(CK, sg * R), 6)             # 端面側の面取り
        sh.line(*P(CK, sg * R), *P(K - CK, sg * R), 6)               # ローレット部の外周
        sh.line(*P(K - CK, sg * R), *P(K, sg * (R - CK)), 6)         # 座面側の面取り
        sh.line(*P(K, sg * (R - CK)), *P(K, sg * rd), 6)             # 座面
        sh.line(*P(K, sg * rd), *P(L - CT, sg * rd), 6)              # ねじの山の径
        sh.line(*P(L - CT, sg * rd), *P(L, sg * (rd - CT)), 6)       # ねじ先の面取り
        sh.line(*P(K, sg * r1), *P(L, sg * r1), 1)                   # ねじの谷の径 (細線)
    sh.line(*P(CK, -R), *P(CK, R), 6)                               # 面取りの境
    sh.line(*P(K - CK, -R), *P(K - CK, R), 6)
    sh.line(*P(L, -(rd - CT)), *P(L, rd - CT), 6)                   # ねじ先の端面
    sh.line(*P(-1.0, 0), *P(L + 1.0, 0), 1, 6)                      # 中心線
    # ローレット (綾目) を細線で示す
    box = [P(CK, -R), P(K - CK, -R), P(K - CK, R), P(CK, R)]
    hatch(sh, box, 30, 3.0)
    hatch(sh, box, -30, 3.0)

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * R, 6)
    sh.circle(HX, Y0, S * (R - CK), 6)                              # 面取りの境
    sh.line(HX - S * R - 3, Y0, HX + S * R + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * R - 3, HX, Y0 + S * R + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * R + 8.0
    hdim(sh, P(0, 0)[0], P(K, 0)[0], top, P(0, R - CK)[1], P(K, R - CK)[1], fmt(K))
    hdim(sh, P(K, 0)[0], P(L, 0)[0], top, P(K, R - CK)[1], P(L, rd - CT)[1], fmt(LS))
    bot = Y0 - S * R - 16.0
    hdim(sh, P(0, 0)[0], P(L, 0)[0], bot, P(0, -(R - CK))[1], P(L, -(rd - CT))[1], f"({fmt(L)})")
    vdim(sh, P(0, -R)[1], P(0, R)[1], X0 - 10.0, P(CK, -R)[0], P(CK, R)[0], f"φ{fmt(DK)}")
    low = Y0 - S * R - 6.0
    leader(sh, *P(CK / 2, -(R - CK / 2)), X0 - 6.0, low, f"C{fmt(CK)}", size=3.5, side="L")
    leader(sh, *P(K - CK / 2, -(R - CK / 2)), P(K, 0)[0] + 6.0, low, f"C{fmt(CK)}", size=3.5)
    leader(sh, *P(L - CT / 2, -(rd - CT / 2)), P(L, 0)[0] + 5.0, Y0 - S * rd - 6.0,
           f"C{fmt(CT)}", size=3.5)
    leader(sh, *P(K + 8.0, rd), P(K + 8.0, 0)[0] + 10.0, Y0 + S * R, f"M{fmt(D)}")
    leader(sh, *P(3.0, R), X0 - 6.0, top + 10.0, "ローレット 綾目", size=3.5, side="L")

    # ---- 注記
    sh.text(-130.0, -30.0, "注記", 4.0)
    notes = [
        "1. 普通公差は JIS B 0405-m (中級) とする。",
        "2. ねじはメートル並目ねじ (ピッチ 0.8) とする。",
        "3. 指示のない角はバリを取り、糸面取りとする。",
    ]
    for i, s_ in enumerate(notes):
        sh.text(-126.0, -37.0 - 6.0 * i, s_, 3.5)


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw(sh)
    path = os.path.join(out, FILE)
    render(sh, path, TITLE["品名"])
    print(path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
