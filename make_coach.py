# -*- coding: utf-8 -*-
"""皿頭六角穴付きコーチボルト M8 / M10 / M12 × 150 の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

元の資料: 株式会社建材のサカイ 鈴木様のメール (管理番号 TEMP-XBUP6N) の手書き図と、
規格品の図面「六角コーチ」「皿CAP (アンスコ JIS)」。
- 頭部: 皿頭 90° (皿CAP と同じ)。頭部径は手書き図の M8 16、M10 20、M12 24。頭部高さは 90° から出る参考寸法。
- 六角穴: 皿CAP (JIS B 1194) の二面幅と深さ。M8 は規格表の値、M10 と M12 は規格表にないので JIS の値を記憶から入れた。
- 長さ: 手書き図の「150mm くらい」を 150 とし、皿頭なので頭部の上面から測る。
- ねじ部: 六角コーチと同じく約 2/3 × 長さ。ねじ山は六角コーチ同等の木ねじ形状とし、ピッチ・谷径・先端形状は
  製作先の標準に任せる (手書き図に「打ち込めれば形状は問いません」とある)。図の谷径と先端の長さは線を引くための仮の値。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width)

BOLTS = [
    {"d": 8.0, "dk": 16.0, "s": 5.0, "t": 3.0},
    {"d": 10.0, "dk": 20.0, "s": 6.0, "t": 3.5},
    {"d": 12.0, "dk": 24.0, "s": 8.0, "t": 4.4},
]
# d: 呼び径 (軸径) / dk: 頭部径 / s: 六角穴の二面幅 / t: 六角穴の深さ (最小)
L = 150.0             # 長さ (頭部の上面から先端まで)
ANG = 90.0            # 皿頭の角度
S = 1.0               # 正面図の尺度
SS = 2.0              # 頭部側から見た図の尺度
COMMON = {"品番": "", "図番": "", "得意先": "株式会社建材のサカイ", "尺度": "1/1", "材質": ""}


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
    s = 1 if x > fx else -1
    for yy in (y1, y2):
        sh.line(fx + s * 1.0, yy, x + s * 1.5, yy)
    sh.line(x, y1, x, y2)
    arrow(sh, x, y1, 0, -1)
    arrow(sh, x, y2, 0, 1)
    sh.text(x - 1.0, (y1 + y2) / 2, label, size, ang=90, align="C")


def draw(sh, b):
    d, dk, s, t = b["d"], b["dk"], b["s"], b["t"]
    r, rk = d / 2, dk / 2
    th = math.radians(ANG / 2)
    k = (rk - r) / math.tan(th)                    # 頭部高さ (参考)
    lt = round(L * 2 / 3 / 5) * 5                  # ねじ部の長さ (約 2/3 L)
    xt = L - lt                                    # ねじ部の始まり
    r1 = 0.36 * d                                  # 谷の半径 (線を引くための仮の値)
    lp = 1.2 * d                                   # 先端のテーパの長さ (仮の値)
    e = s / math.cos(math.radians(30))             # 六角穴の対角距離
    Y0 = 30.0
    gap = 32.0
    left = -(SS * dk + gap + S * L) / 2 - 2.0
    HX = left + SS * rk
    X0 = HX + SS * rk + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (頭部を左)
    for sg in (1, -1):
        sh.line(*P(0, sg * rk), *P(k, sg * r), 6)                  # 皿頭
        sh.line(*P(k, sg * r), *P(L - lp, sg * r), 6)              # 軸とねじの山
        sh.line(*P(L - lp, sg * r), *P(L, 0), 6)                   # 先端 (山)
        sh.line(*P(xt, sg * r1), *P(L - lp * (1 - r1 / r), sg * r1), 1)   # ねじの谷 (細線)
        sh.line(*P(L - lp * (1 - r1 / r), sg * r1), *P(L, 0), 1)
    sh.line(*P(0, -rk), *P(0, rk), 6)                              # 頭部の上面
    sh.line(*P(k, -r), *P(k, r), 6)                                # 頭部と軸の境
    sh.line(*P(xt, -r), *P(xt, r), 6)                              # ねじ部の始まり
    tp = t + (e / 2) / math.tan(math.radians(59))                  # 六角穴の底 (ドリル先 118°)
    for yy in (e / 2, e / 4, -e / 4, -e / 2):
        sh.line(*P(0, yy), *P(t, yy), 1, 2)
        sh.line(*P(t, yy), *P(tp, 0), 1, 2)
    sh.line(*P(-1.0, 0), *P(L + 2.0, 0), 1, 6)                     # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く。尺度 2/1)
    sh.circle(HX, Y0, SS * rk, 6)
    R6 = SS * e / 2
    pts = [(HX + R6 * math.cos(math.radians(90 + 60 * i)), Y0 + R6 * math.sin(math.radians(90 + 60 * i)))
           for i in range(7)]
    for p, q in zip(pts, pts[1:]):
        sh.line(*p, *q, 6)
    sh.line(HX - SS * rk - 3, Y0, HX + SS * rk + 3, Y0, 1, 6)
    sh.line(HX, Y0 - SS * rk - 3, HX, Y0 + SS * rk + 3, 1, 6)
    xs = SS * s / 2
    hdim(sh, HX - xs, HX + xs, Y0 - SS * rk - 8.0, Y0 - SS * e / 4, Y0 - SS * e / 4, fmt(s))
    a = math.radians(120)
    leader(sh, HX + R6 * math.cos(a) * 0.9, Y0 + R6 * math.sin(a) * 0.9, HX - SS * rk + 4.0,
           Y0 + SS * rk + 6.0, "六角穴", sub=f"深さ{fmt(t)}以上", side="L")
    sh.text(HX, Y0 - SS * rk - 17.0, f"(尺度 {fmt(SS)}/1)", 3.5, align="C")

    # ---- 寸法
    bot = Y0 - rk - 10.0
    hdim(sh, P(xt, 0)[0], P(L, 0)[0], bot, P(xt, -r)[1], P(L, 0)[1], f"({fmt(lt)})")
    hdim(sh, P(0, 0)[0], P(L, 0)[0], bot - 10.0, P(0, -rk)[1], P(L, 0)[1], fmt(L))
    top = Y0 + rk + 14.0
    hdim_fit(sh, P(0, 0)[0], P(k, 0)[0], top, P(0, rk)[1], P(k, r)[1], f"({fmt(k)})")
    vdim_left(sh, P(0, -r)[1], P(0, r)[1], P((k + xt) / 2, 0)[0], P((k + xt) / 2, 0)[0], "")
    sh.text(P((k + xt) / 2, 0)[0] - 1.0, Y0 + 2.0, f"φ{fmt(d)}", 4.5, ang=90)
    # 頭部径 (頭部の上面から左へ補助線)
    vdim_left(sh, P(0, -rk)[1], P(0, rk)[1], P(0, 0)[0] - 10.0 - rk, P(0, 0)[0], f"φ{fmt(dk)}")
    # 皿頭の角度 (母線を左へ延ばし、頂点を中心に円弧を描く)
    xa = rk / math.tan(th)                                         # 母線が軸と交わる位置
    ra = xa / math.cos(th) + 5.0                                   # 円弧の半径
    for sg in (1, -1):
        sh.line(*P(-0.5 * math.cos(th), sg * (rk + 0.5 * math.sin(th))),
                *P(xa - (ra + 1.5) * math.cos(th), sg * (ra + 1.5) * math.sin(th)))
    ax, ay = P(xa, 0)
    deg = math.degrees(th)
    sh.arc(ax, ay, S * ra, 180 - deg, 180 + deg)
    for sg in (1, -1):
        px, py = ax - S * ra * math.cos(th), ay + sg * S * ra * math.sin(th)
        arrow(sh, px, py, -math.sin(th), -sg * math.cos(th))
    sh.text(ax - S * ra * math.cos(th) - 2.0, ay + S * ra * math.sin(th) + 1.5, f"{fmt(ANG)}°", 4.5,
            align="R")
    # ねじ部
    leader(sh, *P(xt + lt * 0.45, r), P(xt + lt * 0.45, 0)[0] + 8.0, Y0 + rk + 6.0,
           f"コーチねじ φ{fmt(d)}", sub="(六角コーチ同等)")

    # ---- 注記
    sh.text(-130.0, -30.0, "注記", 4.0)
    notes = [
        "1. ねじ部は六角コーチスクリュー同等の木ねじ形状とし、ピッチ・谷径・先端形状は製作先の標準による。",
        "   ねじ部の長さは約 2/3L。",
        "2. ( ) 内の寸法は参考寸法とする。",
    ]
    for i, s_ in enumerate(notes):
        sh.text(-126.0, -37.0 - 6.0 * i, s_, 3.3)


def main(out):
    for b in BOLTS:
        name = f"皿頭六角穴付きコーチボルト M{fmt(b['d'])}×{fmt(L)}"
        sh = Sheet()
        load_template(sh)
        fill_title(sh, dict(COMMON, 品名=name))
        draw(sh, b)
        render(sh, os.path.join(out, f"皿頭六角穴付きコーチボルト_M{fmt(b['d'])}x{fmt(L)}.pdf"), name)
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
