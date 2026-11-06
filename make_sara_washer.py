# -*- coding: utf-8 -*-
"""真鍮の皿ワッシャー (外径 φ13、厚さ 2.3、内径 φ4 / φ5) の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

元の資料: 依頼者の指定 (材質 真鍮、外径 φ13、厚さ 2.3、内径 φ4・φ5) と現物の写真 2 枚。
写真から読んだ形 (寸法の指定がないので、写真の比率から決めた値。要確認):
- 表側: 皿もみ (円すい形のくぼみ) が穴の縁まで続き、外周には細い平らな縁が残る。皿もみの径は写真の比率で約 φ12。
  厚さ 2.3 のうちに φ4 の穴まで届かせるには 90° では足りないので、120° とし、皿もみの径を φ11.5 とした。
- 裏側: 平らな面に穴が開き、外周の角に面取りがある。写真の比率で片側約 0.7 なので C0.8 とした。
- 正面図は全断面。皿もみ側 (ねじの頭が入る側) を左に置き、その側から見た図を左に置く。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width)

PARTS = [{"d": 4.0}, {"d": 5.0}]   # d: 内径
D = 13.0              # 外径
T = 2.3               # 厚さ
DC = 11.5             # 皿もみの径 (表側の面で)
ANG = 120.0           # 皿もみの角度
C = 0.8               # 裏側の外周の面取り (45°)
SCALE = 5.0
COMMON = {"品番": "", "図番": "", "得意先": "", "尺度": "5/1", "材質": "真鍮"}


def fmt(v):
    return f"{v:g}"


def hatch(sh, poly, pitch=1.5):
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


def dim_v(sh, y1, y2, x, fx, label, size=4.5):
    """直径の縦の寸法。補助線は fx から寸法線 x まで引き、数値は寸法線の左に縦書き。"""
    s = 1 if x > fx else -1
    for yy in (y1, y2):
        sh.line(fx + s * 1.0, yy, x + s * 1.5, yy)
    sh.line(x, y1, x, y2)
    arrow(sh, x, y1, 0, -1)
    arrow(sh, x, y2, 0, 1)
    sh.text(x - 1.0, (y1 + y2) / 2, label, size, ang=90, align="C")


def draw(sh, d):
    S = SCALE
    R, RC, r = D / 2, DC / 2, d / 2
    th = math.radians(ANG / 2)
    h = (RC - r) / math.tan(th)                    # 皿もみの深さ
    if h >= T:
        raise ValueError(f"皿もみが裏面まで抜ける (d={d}, 深さ {h:.3f})")
    Y0 = 40.0
    HX = -70.0                                     # 皿もみ側から見た図の中心
    X0 = 8.0                                       # 正面図の皿もみ側の面

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (全断面。皿もみ側を左)
    for sg in (1, -1):
        prof = [(0, RC), (0, R), (T - C, R), (T, R - C), (T, r), (h, r)]
        poly = [P(x, sg * y) for x, y in prof]
        hatch(sh, poly if sg > 0 else poly[::-1])
        for p, q in zip(poly, poly[1:] + poly[:1]):
            sh.line(*p, *q, 6)
    # 断面の奥に見える稜線 (穴の縁)
    sh.line(*P(0, -RC), *P(0, RC), 6)              # 皿もみの縁
    sh.line(*P(h, -r), *P(h, r), 6)                # 皿もみと穴の境
    sh.line(*P(T, -r), *P(T, r), 6)                # 裏側の穴の縁
    sh.line(*P(-0.6, 0), *P(T + 0.6, 0), 1, 6)     # 中心線

    # ---- 皿もみ側から見た図 (第三角法: 左側面図を左に置く)
    for rr in (R, RC, r):
        sh.circle(HX, Y0, S * rr, 6)
    sh.line(HX - S * R - 3, Y0, HX + S * R + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * R - 3, HX, Y0 + S * R + 3, 1, 6)

    # ---- 寸法
    xr = P(T, 0)[0]
    dim_v(sh, P(0, -r)[1], P(0, r)[1], xr + 9.0, xr, f"φ{fmt(d)}")
    dim_v(sh, P(0, -R)[1], P(0, R)[1], xr + 19.0, P(T - C, 0)[0], f"φ{fmt(D)}")
    dim_v(sh, P(0, -RC)[1], P(0, RC)[1], X0 - 26.0, X0, f"φ{fmt(DC)}")
    hdim(sh, X0, xr, Y0 - S * R - 9.0, P(0, -R)[1], P(T, -(R - C))[1], fmt(T))
    # 皿もみの角度 (円すいの頂点を中心に、くぼみの中に円弧)
    xa = RC / math.tan(th)                         # 頂点の位置
    rho = 5.0
    ax, ay = P(xa, 0)
    deg = math.degrees(th)
    sh.arc(ax, ay, S * rho, 180 - deg, 180 + deg)
    for sg in (1, -1):
        phi = math.radians(180 - sg * deg)
        px, py = ax + S * rho * math.cos(phi), ay + S * rho * math.sin(phi)
        arrow(sh, px, py, sg * math.sin(phi), -sg * math.cos(phi))
    sh.text(ax - S * rho - 1.5, Y0 + 1.5, f"{fmt(ANG)}°", 4.5, align="R")
    # 裏側の面取り
    cx, cy = P(T - C / 2, R - C / 2)
    leader(sh, cx, cy, xr + 6.0, Y0 + S * R + 8.0, f"C{fmt(C)}")

    # ---- 注記
    sh.text(-130.0, -30.0, "注記", 4.0)
    notes = [
        "1. 普通公差は JIS B 0405-m (中級) とする。",
        "2. 指示のない角はバリを取り、糸面取りとする。",
    ]
    for i, s_ in enumerate(notes):
        sh.text(-126.0, -37.0 - 6.0 * i, s_, 3.5)
    return h


def main(out):
    for p in PARTS:
        d = p["d"]
        name = f"皿ワッシャー φ{fmt(d)}×φ{fmt(D)}×{fmt(T)}"
        sh = Sheet()
        load_template(sh)
        fill_title(sh, dict(COMMON, 品名=name))
        h = draw(sh, d)
        path = os.path.join(out, f"皿ワッシャー_{fmt(d)}x{fmt(D)}x{fmt(T)}.pdf")
        render(sh, path, name)
        print(path, f"皿もみ深さ {h:.3f}, 穴の円筒部 {T - h:.3f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
