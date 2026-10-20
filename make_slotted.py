# -*- coding: utf-8 -*-
"""すりわり付き (マイナス溝) の小ねじ M3 × 首下 6 の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

カネコの規格表「(+) トラス小ねじ」「(+-) ナベ小ねじ」の M3 の寸法を使い、十字穴をすりわりに替えた。
トラスとなべを 1 品 1 ファイルで出す。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width, tol_text, vdim)

COMMON = {
    "d": 3.0,      # ねじの呼び径 M3
    "p": 0.5,      # ピッチ (並目)
    "d1": 2.39,    # おねじの谷の径 (図の線用)
    "l": 6.0,      # 首下長さ
    "c": 0.3,      # ねじ先の面取り (谷の径まで)
    "n": 0.8,      # すりわりの幅
}
PARTS = [
    {   # 規格表「(+) トラス小ねじ」M3: dk 6.9 0/-0.5、k 1.9±0.15。すりわりの寸法は表にないので参考値
        "head": "truss", "dk": 6.9, "dk_tol": ("0", "-0.5"), "k": 1.9, "k_tol": "±0.15",
        "t": 0.95,     # すりわりの深さ (規格表になし。参考値)
        "e": 0.27,     # 頭部外周の平らな部分の厚さ (規格表の図から読み取り)
        "title": {"品番": "", "図番": "", "得意先": "",
                  "品名": "すりわり付きトラス小ねじ M3×6", "尺度": "10/1", "材質": ""},
        "file": "すりわり付きトラス小ねじ_M3x6.pdf",
    },
    {   # 規格表「(+-) ナベ小ねじ」M3: dk 5.5 0/-0.5、k 2±0.15、n 0.80、t 1.10
        "head": "pan", "dk": 5.5, "dk_tol": ("0", "-0.5"), "k": 2.0, "k_tol": "±0.15",
        "t": 1.1,      # すりわりの深さ (規格表の t)
        "title": {"品番": "", "図番": "", "得意先": "",
                  "品名": "すりわり付きなべ小ねじ M3×6", "尺度": "10/1", "材質": ""},
        "file": "すりわり付きなべ小ねじ_M3x6.pdf",
    },
]
SCALE = 10.0


def fmt(v):
    return f"{v:g}"


def hdim_fit(sh, x1, x2, y, f1, f2, label, size=4.5):
    """hdim と同じ。数値が寸法線の間に収まらないときは、寸法線を左へ延ばして左の外側に書く。"""
    w = text_width(label, size, 0.5)
    if w + 2.0 <= x2 - x1:
        hdim(sh, x1, x2, y, f1, f2, label, size)
        return
    hdim(sh, x1, x2, y, f1, f2, "", size)
    sh.line(x1 - w - 2.0, y, x1, y)
    sh.text(x1 - 1.5, y + 1.0, label, size, align="R")


def head_profile(s):
    """頭部の上側の外形 (x: 頭部上面から軸方向、y: 中心から) を点列で返す。y はすりわりの縁から外周まで。"""
    rD, k, hn = s["dk"] / 2, s["k"], COMMON["n"] / 2
    pts = []
    if s["head"] == "truss":
        h = k - s["e"]                                  # 丸い部分の高さ
        R = (h * h + rD * rD) / (2 * h)                 # 丸い部分の半径 (中心は軸上 x=R)
        a0, a1 = math.asin(hn / R), math.asin(rD / R)
        for i in range(61):
            a = a0 + (a1 - a0) * i / 60
            pts.append((R - R * math.cos(a), R * math.sin(a)))
        pts.append((k, rD))
    else:
        xs, yf = 0.5 * k, 0.45 * rD                     # 側面の始まりと上面の平らな範囲 (図の形だけ)
        pts.append((0.0, hn))
        for i in range(61):
            f = math.pi / 2 * i / 60
            pts.append((xs - xs * math.cos(f), yf + (rD - yf) * math.sin(f)))
        pts.append((k, rD))
    return pts


def draw_screw(sh, s):
    S = SCALE
    c0 = COMMON
    rD, rd, r1, hn = s["dk"] / 2, c0["d"] / 2, c0["d1"] / 2, c0["n"] / 2
    k, t, c = s["k"], s["t"], c0["c"]
    L = k + c0["l"]                                         # 全長 (頭部上面からねじ先まで)
    Y0 = 24.0
    gap = 34.0
    left = -(S * s["dk"] + gap + S * L + 25.0) / 2
    HX = left + S * rD
    X0 = HX + S * rD + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (頭部を左、ねじ先を右。すりわりは紙面に垂直)
    prof = head_profile(s)
    for sg in (1, -1):
        for (x1, y1), (x2, y2) in zip(prof, prof[1:]):
            sh.line(*P(x1, sg * y1), *P(x2, sg * y2), 6)        # 頭部の外形
        sh.line(*P(k, sg * rD), *P(k, sg * rd), 6)              # 座面
        sh.line(*P(prof[0][0], sg * hn), *P(t, sg * hn), 6)     # すりわりの側面
        sh.line(*P(k, sg * rd), *P(L - c, sg * rd), 6)          # ねじの山の径
        sh.line(*P(L - c, sg * rd), *P(L, sg * (rd - c)), 6)    # ねじ先の面取り
        sh.line(*P(k, sg * r1), *P(L, sg * r1), 1)              # ねじの谷の径 (細線)
    sh.line(*P(t, -hn), *P(t, hn), 6)                           # すりわりの底
    if s["head"] == "truss":
        sh.line(*P(k - s["e"], -rD), *P(k - s["e"], rD), 6)     # 丸い部分と外周の平らな部分の境
    sh.line(*P(L, -(rd - c)), *P(L, rd - c), 6)                 # 先端面
    sh.line(*P(-0.3, 0), *P(L + 0.3, 0), 1, 6)                  # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rD, 6)
    xe = math.sqrt(rD * rD - hn * hn)
    for sg in (1, -1):
        sh.line(HX - S * xe, Y0 + sg * S * hn, HX + S * xe, Y0 + sg * S * hn, 6)   # すりわり
    sh.line(HX - S * rD - 3, Y0, HX + S * rD + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * rD - 3, HX, Y0 + S * rD + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * rD + 8.0
    yt = P(0, hn)[1]
    hdim_fit(sh, P(0, 0)[0], P(t, 0)[0], top, prof[0][1] * S + Y0, yt, fmt(t))
    hdim_fit(sh, P(0, 0)[0], P(k, 0)[0], top + 10.0, prof[0][1] * S + Y0, P(k, rD)[1],
         f"{fmt(k)}{s['k_tol']}")
    bot = Y0 - S * rD - 8.0
    hdim(sh, P(k, 0)[0], P(L, 0)[0], bot, P(k, -rD)[1], P(L, -(rd - c))[1], fmt(c0["l"]))
    # 頭部の径 (許容差付き)
    xv = X0 - 8.0
    vdim(sh, P(0, -rD)[1], P(0, rD)[1], xv, P(k, -rD)[0], P(k, rD)[0], "")
    main = f"φ{fmt(s['dk'])}"
    tol_text(sh, xv - 1.0, Y0 - 5.0, main, *s["dk_tol"])
    # すりわりの幅 (頭部側から見た図。矢印を外側から当てる)
    xn = HX + S * rD + 6.0
    for sg in (1, -1):
        sh.line(HX + S * xe + 1.0, Y0 + sg * S * hn, xn + 1.5, Y0 + sg * S * hn)
    sh.line(xn, Y0 - S * hn - 5.0, xn, Y0 + S * hn + 13.0)
    arrow(sh, xn, Y0 - S * hn, 0, 1)
    arrow(sh, xn, Y0 + S * hn, 0, -1)
    sh.text(xn - 1.0, Y0 + S * hn + 7.0, fmt(c0["n"]), 4.5, ang=90, align="C")
    leader(sh, *P(L - 1.2, rd), P(L, 0)[0] + 6.0, Y0 + S * rd + 12.0,
           f"M{fmt(c0['d'])}×{fmt(c0['p'])}")


def main(out):
    for s in PARTS:
        sh = Sheet()
        load_template(sh)
        fill_title(sh, s["title"])
        draw_screw(sh, s)
        render(sh, os.path.join(out, s["file"]), s["title"]["品名"])
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
