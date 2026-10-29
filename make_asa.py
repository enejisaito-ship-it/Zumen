# -*- coding: utf-8 -*-
"""ASA-002 / ASA-003 (A1070 スラグ φ5.2×4.3 / φ5.2×5.6) の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

元の資料: アジヤアルミ 蔵持様のメール「お見積り依頼の件」(2026/07/08) と添付の「260707_φ5.2スラグ図面」、
社内の検討表 ASA-002K / ASA-003K-701-001-04。
形状は添付図 (t4.3) のとおり: 外径 φ5.20±0.05、片側の端を φ3 まで (0.5) 落とす。角の R は出来なり。
厚さと面取りの長さは添付図で括弧付き (参考寸法) なので、そのまま括弧付きで書く。
ASA-003 (t5.6) は添付図がないので、厚さだけ変えて同じ形とした。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, load_template, fill_title,  # noqa: E402
                    render, text_width)

PARTS = [
    {"品番": "ASA-002", "品名": "A1070スラグ φ5.2×4.3", "t": 4.3},
    {"品番": "ASA-003", "品名": "A1070スラグ φ5.2×5.6", "t": 5.6},
]
D = 5.2               # 外径
D_TOL = "±0.05"
DE = 3.0              # 面取りした端面の径
C = 0.5               # 面取りの長さ (軸方向)
SCALE = 10.0
COMMON = {"図番": "", "得意先": "アジヤアルミ株式会社", "尺度": "10/1", "材質": "A1070"}


def fmt(v):
    return f"{v:g}"


def hdim_fit(sh, x1, x2, y, f1, f2, label, size=4.5):
    """hdim と同じ。数値が寸法線の間に収まらないときは、矢印を外側から当て、数値を右の外側に書く。"""
    w = text_width(label, size, 0.5)
    if w + 2.0 <= x2 - x1:
        hdim(sh, x1, x2, y, f1, f2, label, size)
        return
    hdim(sh, x1, x2, y, f1, f2, "", size, outside=True)
    sh.line(x2, y, x2 + w + 8.0, y)
    sh.text(x2 + 7.0, y + 1.0, label, size)


def vdim_side(sh, y1, y2, x, fx, label, size=4.5):
    """縦の寸法。補助線は fx から寸法線 x まで引き、数値は寸法線の左に縦書き。"""
    s = 1 if x > fx else -1
    for yy in (y1, y2):
        sh.line(fx + s * 1.0, yy, x + s * 1.5, yy)
    sh.line(x, y1, x, y2)
    arrow(sh, x, y1, 0, -1)
    arrow(sh, x, y2, 0, 1)
    sh.text(x - 1.0, (y1 + y2) / 2, label, size, ang=90, align="C")


def hatch(sh, poly, pitch=2.0):
    """凸多角形 poly (用紙座標) の中に 45° のハッチングを細線で引く。"""
    xs = [x - y for x, y in poly]                  # 45° の線は x - y = 一定
    k = min(xs) + pitch / 2
    while k < max(xs):
        pts = []
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            a, b = x1 - y1 - k, x2 - y2 - k
            if a == b or a * b > 0:
                continue
            u = a / (a - b)
            pts.append((x1 + (x2 - x1) * u, y1 + (y2 - y1) * u))
        if len(pts) >= 2:
            pts.sort()
            sh.line(*pts[0], *pts[-1])
        k += pitch


def draw_slug(sh, t):
    S = SCALE
    R, RE = D / 2, DE / 2
    Y0 = 28.0
    gap = 35.0
    left = -(S * D + gap + S * t) / 2 - 15.0
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (上半分は外形、下半分は断面。平らな端面を左、面取り側を右)
    hatch(sh, [P(0, 0), P(0, -R), P(t - C, -R), P(t, -RE), P(t, 0)])
    for sg in (1, -1):
        sh.line(*P(0, sg * R), *P(t - C, sg * R), 6)               # 外周
        sh.line(*P(t - C, sg * R), *P(t, sg * RE), 6)              # 面取り
    sh.line(*P(0, -R), *P(0, R), 6)                                # 左の端面
    sh.line(*P(t, -RE), *P(t, RE), 6)                              # 右の端面
    sh.line(*P(t - C, 0), *P(t - C, R), 6)                         # 面取りの始まり (外形側だけ)
    sh.line(*P(-0.3, 0), *P(t + 0.3, 0), 1, 6)                     # 中心線

    # ---- 左側面図 (平らな端面側から見た図)
    sh.circle(HX, Y0, S * R, 6)
    sh.line(HX - S * R - 3, Y0, HX + S * R + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * R - 3, HX, Y0 + S * R + 3, 1, 6)
    vdim_side(sh, Y0 - S * R, Y0 + S * R, HX - S * R - 10.0, HX, f"φ{D:.2f}{D_TOL}")

    # ---- 寸法
    bot = Y0 - S * R - 9.0
    hdim_fit(sh, P(t - C, 0)[0], P(t, 0)[0], bot, P(t - C, -R)[1], P(t, -RE)[1], f"({fmt(C)})")
    hdim(sh, P(0, 0)[0], P(t, 0)[0], bot - 10.0, P(0, -R)[1], P(t, -RE)[1], f"({fmt(t)})")
    vdim_side(sh, P(0, -RE)[1], P(0, RE)[1], P(t, 0)[0] + 10.0, P(t, 0)[0], f"φ{fmt(DE)}")
    # 角の R (出来なり)。棚から 2 か所の角へ線を引く
    ex, ey = P(t, 0)[0] + 6.0, Y0 + S * R + 9.0
    label, sub = "R仕上がり", "出来なり"
    w = max(text_width(s, 4.0, 0.5) for s in (label, sub))
    sh.line(ex, ey, ex + w + 2, ey)
    sh.text(ex + 1, ey + 0.8, label, 4.0)
    sh.text(ex + 1, ey - 4.8, sub, 4.0)
    for cx, cy in (P(t - C, R), P(t, RE)):
        sh.line(cx, cy, ex, ey)
        arrow(sh, cx, cy, cx - ex, cy - ey)

    # ---- 注記
    sh.text(-130.0, -30.0, "注記", 4.0)
    notes = [
        "1. ( ) 内の寸法は参考寸法とする。",
        "2. 後工程で焼鈍するため、出荷前に洗浄すること (完全脱脂でなくても可)。",
    ]
    for i, s in enumerate(notes):
        sh.text(-126.0, -37.0 - 6.0 * i, s, 3.5)


def main(out):
    for p in PARTS:
        sh = Sheet()
        load_template(sh)
        fill_title(sh, dict(COMMON, 品番=p["品番"], 品名=p["品名"]))
        draw_slug(sh, p["t"])
        render(sh, os.path.join(out, p["品番"] + ".pdf"), p["品名"])
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
