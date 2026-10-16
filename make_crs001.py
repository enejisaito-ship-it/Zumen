# -*- coding: utf-8 -*-
"""CRS-001（SUS脱落防止トラス十字ネジ M4×12, S=3）の図面を、株式会社カネコの A4 図面書式 (JWW) に合わせて PDF で出力する。

書式 (枠・表題欄) は templates/kaneko_A4_title.jww から読み込む。
座標は JWW と同じく用紙中心を原点とした用紙上の mm。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, tol_text, vdim)


# ---------------------------------------------------------------- ねじの寸法 (実寸 mm)
SCREW = {
    "L": 12.0,        # 呼び長さ (座面から先端)
    "S": 3.0,         # ねじ部長さ (先端側)
    "d": 4.0,         # M4
    "d1": 3.242,      # M4 並目 谷の径 (基準寸法)
    "ds": 3.0,        # 首下の軸径 d (ミスミ規格表: 3 0/-0.3)
    "dk": 9.4,        # 頭部の径 A (ミスミ規格表)
    "k": 2.5,         # 頭部の高さ E (ミスミ規格表)
    "rim": 0.0,       # 頭部外周の立ち上がり (ミスミの図に合わせてなし。角は r0.3)
}
SCALE = 5.0


def draw_screw(sh, sc=SCREW):
    S_ = SCALE
    X0, Y0 = -10.0, 25.0          # 正面図: 座面と中心線
    HX = -80.0                    # 頭部側から見た図の中心 x

    def P(x, r):
        return X0 + S_ * x, Y0 + S_ * r

    L, Sl, k = sc["L"], sc["S"], sc["k"]
    rd, rd1, rs, rk, rim = sc["d"] / 2, sc["d1"] / 2, sc["ds"] / 2, sc["dk"] / 2, sc["rim"]
    ch = rd - rd1                 # 先端の面取り (谷の径まで)

    # ---- 正面図 外形 (線色 6 = 太線)
    for sg in (1, -1):
        if rim > 0:
            sh.line(*P(0, sg * rk), *P(-rim, sg * rk), 6)             # 頭部外周の立ち上がり
        sh.line(*P(0, sg * rs), *P(L - Sl, sg * rs), 6)              # 首下の細い軸
        sh.line(*P(L - Sl, sg * rd), *P(L - ch, sg * rd), 6)         # ねじ外径
        sh.line(*P(L - ch, sg * rd), *P(L, sg * rd1), 6)             # 先端の面取り
        sh.line(*P(L - Sl, sg * rd1), *P(L - ch, sg * rd1), 1)       # ねじ谷径 (細線)
    sh.line(*P(0, -rk), *P(0, rk), 6)                                # 座面
    sh.line(*P(L - Sl, -rd), *P(L - Sl, rd), 6)                      # 軸とねじ部の段
    sh.line(*P(L, -rd1), *P(L, rd1), 6)                              # 先端面
    # 頭部の丸み: 外周 (rim, rk) と頂点 (k, 0) を通る円弧
    h = k - rim
    R = (rk ** 2 + h ** 2) / (2 * h)
    cx, _ = P(-k + R, 0)
    a = math.degrees(math.atan2(rk, -(R - h)))
    sh.arc(cx, Y0, S_ * R, a, 360 - a, 6)
    # 十字穴 (かくれ線、略図)
    for sg in (1, -1):
        sh.line(*P(-k + 0.15, sg * 1.1), *P(-k + 1.9, sg * 0.25), 1, 2)
        sh.line(*P(-k + 1.9, sg * 0.25), *P(-k + 2.1, 0), 1, 2)
    sh.line(*P(-k - 0.7, 0), *P(L + 0.7, 0), 1, 6)                   # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.arc(HX, Y0, S_ * rk, 0, 360, 6)
    aw, al = 0.55 * S_, 2.2 * S_
    cross = [(aw, al), (-aw, al), (-aw, aw), (-al, aw), (-al, -aw), (-aw, -aw),
             (-aw, -al), (aw, -al), (aw, -aw), (al, -aw), (al, aw), (aw, aw)]
    for p, q in zip(cross, cross[1:] + cross[:1]):
        sh.line(HX + p[0], Y0 + p[1], HX + q[0], Y0 + q[1], 6)
    sh.line(HX - S_ * rk - 3, Y0, HX + S_ * rk + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S_ * rk - 3, HX, Y0 + S_ * rk + 3, 1, 6)

    # ---- 寸法
    xb, xt = P(0, 0)[0], P(L, 0)[0]
    hdim(sh, xb, xt, -10.0, P(0, -rk)[1], P(L, -rd1)[1], "12")
    hdim(sh, P(L - Sl, 0)[0], xt, 45.0, P(L - Sl, rd)[1], P(L, rd1)[1], "3")
    hdim(sh, P(-k, 0)[0], xb, 57.0, Y0, P(0, rk)[1], "2.5")
    vdim(sh, P(0, -rk)[1], P(0, rk)[1], -32.0, P(-rim, -rk)[0], P(-rim, rk)[0], "φ9.4")
    # 首下の軸径: 矢印を外側から当て、数値は上へ
    xs = P(5.0, 0)[0]
    ys1, ys2 = P(0, -rs)[1], P(0, rs)[1]
    sh.line(xs, ys1 - 5, xs, ys2 + 15)
    arrow(sh, xs, ys1, 0, 1)
    arrow(sh, xs, ys2, 0, -1)
    tol_text(sh, xs - 1.0, ys2 + 4.0, "φ3", "0", "-0.3")
    leader(sh, *P(-0.25, rk - 0.35), -6.0, 60.0, "r0.3")
    leader(sh, *P(L - Sl / 2 - 0.4, rd), 62.0, 60.0, "M4（並目）")
    leader(sh, HX + aw + 0.5, Y0 + al * 0.6, -62.0, 60.0, "十字穴 No.2")

    # ---- 注記
    notes = ["注記",
             "1. ねじはメートル並目、ねじ部は先端側の長さ 3、先端は平先。",
             "2. 首下の軸 φ3 はねじの谷の径より細く、脱落防止とする。",
             "3. 指示のない角はバリなきこと。"]
    y = -22.0
    for i, s in enumerate(notes):
        sh.text(-135.0, y, s, 4.0 if i == 0 else 3.5, sp=0.3)
        y -= 6.0


TITLE = {
    "品番": "CRS-001",
    "図番": "",
    "得意先": "有限会社シー・アール・エス",
    "品名": "SUS脱落防止トラス十字ネジM4×12,S=3",
    "尺度": "5/1",
    "材質": "SUS304相当",
    "表面処理": "なし",
}


def main(out, draft=False):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    if draft:
        sh.text(0, 40, "（図はねじの寸法を確認してから描く）", 6.0, align="C")
    else:
        draw_screw(sh)
    render(sh, os.path.join(out, "CRS-001_draft.pdf" if draft else "CRS-001.pdf"),
           "CRS-001 SUS脱落防止トラス十字ネジ M4×12, S=3")
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
