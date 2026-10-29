# -*- coding: utf-8 -*-
"""ピン型ヒンジ (日本ゲームカード サンプル) の位置決めピン 2 種を、株式会社カネコの A4 図面書式で PDF に出力する。

元の図面: 外観図-ピン型ヒンジ 上金具 / 下金具 (SAGAWA、手で採寸した外観図)。寸法の文字はフォントが
埋め込まれていないので、MS ゴシックの文字番号から読んだ。
- 上金具用: 頭部 φ10 × 2.2、軸 φ8、頭部の下から先端まで 23。
- 下金具用: つば φ18 × 2.2、軸 φ8、つばの上から先端まで 20。
先端のテーパは元の図面に寸法がないので、図の尺度から読んだ (2 本とも長さ約 5、片側約 15°)。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, load_template, fill_title,  # noqa: E402
                    render, text_width)

PINS = [
    {"品名": "位置決めピン 上金具用", "file": "位置決めピン_上金具用_8x23.pdf",
     "dh": 10.0, "kh": 2.2, "d": 8.0, "l": 23.0, "lt": 5.0, "ang": 30.0},
    {"品名": "位置決めピン 下金具用", "file": "位置決めピン_下金具用_8x20.pdf",
     "dh": 18.0, "kh": 2.2, "d": 8.0, "l": 20.0, "lt": 5.0, "ang": 30.0},
]
# dh, kh: 頭部 (つば) の径と厚さ / d: 軸径 / l: 頭部の下から先端まで / lt: 先端のテーパの長さ / ang: テーパの角度
SCALE = 4.0


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


def vdim_left(sh, y1, y2, x, fx, label, size=4.5):
    """直径の縦の寸法。補助線は fx から寸法線 x まで引き、数値は寸法線の左に縦書き。"""
    for yy in (y1, y2):
        sh.line(fx - 1.0, yy, x - 1.5, yy)
    sh.line(x, y1, x, y2)
    arrow(sh, x, y1, 0, -1)
    arrow(sh, x, y2, 0, 1)
    sh.text(x - 1.0, (y1 + y2) / 2, label, size, ang=90, align="C")


def draw_pin(sh, p):
    S = SCALE
    rh, kh, r, lt = p["dh"] / 2, p["kh"], p["d"] / 2, p["lt"]
    th = math.radians(p["ang"] / 2)
    L = kh + p["l"]                                # 全長
    xt = L - lt                                    # テーパの始まり
    re = r - lt * math.tan(th)                     # 先端の半径
    Y0 = max(25.0, S * rh - 4.0)                   # 下の寸法が表題欄にかからない高さ
    gap = 40.0
    left = -(2 * S * rh + gap + S * L) / 2 - 10.0
    HX = left + S * rh
    X0 = HX + S * rh + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (頭部を左)
    for sg in (1, -1):
        sh.line(*P(0, sg * rh), *P(kh, sg * rh), 6)                # 頭部の外周
        sh.line(*P(kh, sg * rh), *P(kh, sg * r), 6)                # 頭部の下面
        sh.line(*P(kh, sg * r), *P(xt, sg * r), 6)                 # 軸
        sh.line(*P(xt, sg * r), *P(L, sg * re), 6)                 # 先端のテーパ
    sh.line(*P(0, -rh), *P(0, rh), 6)                              # 頭部の上面
    sh.line(*P(xt, -r), *P(xt, r), 6)                              # 軸とテーパの境
    sh.line(*P(L, -re), *P(L, re), 6)                              # 先端面
    sh.line(*P(-1.0, 0), *P(L + 1.0, 0), 1, 6)                     # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rh, 6)
    sh.line(HX - S * rh - 3, Y0, HX + S * rh + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * rh - 3, HX, Y0 + S * rh + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * rh + 8.0
    hdim_fit(sh, P(0, 0)[0], P(kh, 0)[0], top, P(0, rh)[1], P(kh, rh)[1], fmt(kh))
    hdim(sh, P(xt, 0)[0], P(L, 0)[0], Y0 + S * r + 8.0, P(xt, r)[1], P(L, re)[1], fmt(lt))
    bot = Y0 - S * rh - 8.0
    hdim(sh, P(kh, 0)[0], P(L, 0)[0], bot, P(kh, -rh)[1], P(L, -re)[1], fmt(p["l"]))
    hdim(sh, P(0, 0)[0], P(L, 0)[0], bot - 10.0, P(0, -rh)[1], P(L, -re)[1], f"({fmt(L)})")
    vdim_left(sh, P(0, -rh)[1], P(0, rh)[1], P(0, 0)[0] - 8.0, P(0, 0)[0], f"φ{fmt(p['dh'])}")
    xv = P(kh + (xt - kh) / 2, 0)[0]                               # 軸径 (軸の中で寸法線を引く)
    sh.line(xv, P(0, -r)[1], xv, P(0, r)[1])
    arrow(sh, xv, P(0, -r)[1], 0, -1)
    arrow(sh, xv, P(0, r)[1], 0, 1)
    sh.text(xv - 1.0, Y0 + 4.0, f"φ{fmt(p['d'])}", 4.5, ang=90)
    # テーパの角度 (母線を先端の右へ延ばし、頂点を中心に円弧を描く)
    xa = L + re / math.tan(th)                                     # テーパの頂点
    ra = xa - L - 3.0                                              # 円弧の半径 (実寸)
    for sg in (1, -1):
        sh.line(*P(L + 0.3, sg * (re - 0.3 * math.tan(th))),
                *P(xa - (ra - 1.0) * math.cos(th), sg * (ra - 1.0) * math.sin(th)))
    ax, ay = P(xa, 0)
    deg = math.degrees(th)
    sh.arc(ax, ay, S * ra, 180 - deg, 180 + deg)
    for sg in (1, -1):
        px, py = ax - S * ra * math.cos(th), ay + sg * S * ra * math.sin(th)
        arrow(sh, px, py, -math.sin(th), -sg * math.cos(th))
    sh.text(ax - S * ra + 4.0, ay + 1.0, f"{fmt(p['ang'])}°", 4.5)

    # ---- 注記
    sh.text(-130.0, -36.0, "注記", 4.0)
    sh.text(-126.0, -43.0, "1. 普通公差は JIS B 0405-m (中級) とする。", 3.5)


def main(out):
    for p in PINS:
        sh = Sheet()
        load_template(sh)
        fill_title(sh, {"品番": "", "図番": "", "得意先": "", "品名": p["品名"], "尺度": "4/1", "材質": ""})
        draw_pin(sh, p)
        render(sh, os.path.join(out, p["file"]), p["品名"])
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
