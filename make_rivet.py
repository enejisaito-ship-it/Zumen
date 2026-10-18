# -*- coding: utf-8 -*-
"""薄平リベット (d1.4 × L14, SUS) の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

形は ㈱カネコ 図面／規格【薄平リベット】(E00012) の図に合わせる。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, hdim, load_template, fill_title, render, text_width, vdim  # noqa: E402

RIVET = {
    "d": 1.4,          # 軸径
    "dk": 2.8,         # 頭部直径
    "k": 0.5,          # 頭部高さ
    "L": 14.0,         # 首下長さ (マイナス公差)
    "L_up": "0",       # L の上の許容差
    "L_lo": "-0.3",    # L の下の許容差 (値の指定がないので仮に -0.3)
    "rf": 0.1,         # 首下の丸み (図の形だけ。寸法は入れない)
}
SCALE = 10.0
TITLE = {"品番": "", "図番": "", "得意先": "", "品名": "薄平リベット 1.4×14",
         "尺度": "10/1", "材質": "SUS"}
FILE = "薄平リベット_1.4x14.pdf"


def fmt(v):
    return f"{v:g}"


def draw_rivet(sh, r=RIVET):
    S = SCALE
    d, dk, k, L, rf = r["d"], r["dk"], r["k"], r["L"], r["rf"]
    rd, rD, rk = d / 2, dk / 2, k / 2                # rk: 頭部外周の丸み (厚さの半分)
    T = k + L                                       # 全長
    Y0 = 32.0                                       # 中心線の高さ
    gap = 30.0                                      # 側面図と正面図の間
    left = -(S * dk + gap + S * T + 25.0) / 2       # 図の並びを用紙の左右中央に
    HX = left + S * rD                              # 頭部側から見た図の中心
    X0 = HX + S * rD + gap                          # 正面図の頭部上面

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 外形 (頭部を左、軸を右)
    sh.line(*P(0, -(rD - rk)), *P(0, rD - rk), 6)                   # 頭部上面
    for sg in (1, -1):
        sh.line(*P(k, sg * (rd + rf)), *P(k, sg * (rD - rk)), 6)    # 頭部の座面
        sh.line(*P(k + rf, sg * rd), *P(T, sg * rd), 6)             # 軸
    cx, cy = P(rk, rD - rk)
    sh.arc(cx, cy, S * rk, 0, 180, 6)                               # 頭部外周の丸み
    cx, cy = P(rk, -(rD - rk))
    sh.arc(cx, cy, S * rk, 180, 360, 6)
    cx, cy = P(k + rf, rd + rf)
    sh.arc(cx, cy, S * rf, 180, 270, 6)                             # 首下の丸み
    cx, cy = P(k + rf, -(rd + rf))
    sh.arc(cx, cy, S * rf, 90, 180, 6)
    sh.line(*P(T, -rd), *P(T, rd), 6)                               # 先端面
    sh.line(*P(-0.3, 0), *P(T + 0.3, 0), 1, 6)                      # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rD, 6)
    sh.circle(HX, Y0, S * rd, 1, 2)                                 # 軸 (かくれ線)
    sh.line(HX - S * rD - 3, Y0, HX + S * rD + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * rD - 3, HX, Y0 + S * rD + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * rD + 8.0
    bot = Y0 - S * rD - 10.0
    hdim(sh, P(0, 0)[0], P(k, 0)[0], top, P(0, rD - rk)[1], P(k, rD - rk)[1], fmt(k), outside=True)
    x1, x2 = P(k, 0)[0], P(T, 0)[0]
    hdim(sh, x1, x2, bot, P(k, -(rD - rk))[1], P(T, -rd)[1], "")
    main = fmt(L)                                   # L: 数値の右に上下の許容差
    w = text_width(main, 4.5, 0.5)
    xm = (x1 + x2) / 2 - w / 2
    sh.text(xm, bot + 1.0, main, 4.5)
    sh.text(xm + w + 0.8, bot + 4.0, r["L_up"], 3.0)
    sh.text(xm + w + 0.8, bot + 0.6, r["L_lo"], 3.0)
    vdim(sh, P(0, -rD)[1], P(0, rD)[1], X0 - 8.0, P(rk, -rD)[0], P(rk, rD)[0], f"φ{fmt(dk)}")
    vdim(sh, P(0, -rd)[1], P(0, rd)[1], P(T, 0)[0] + 12.0, P(T, 0)[0], P(T, 0)[0],
         f"φ{fmt(d)}")

    # ---- 注記
    notes = ["注記",
             "1. 指示のない角はバリなきこと。"]
    y = -30.0
    for i, s in enumerate(notes):
        sh.text(-135.0, y, s, 4.0 if i == 0 else 3.5, sp=0.3)
        y -= 6.0


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw_rivet(sh)
    render(sh, os.path.join(out, FILE), f'{TITLE["品名"]}')
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
