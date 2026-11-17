# -*- coding: utf-8 -*-
"""ポールピースねじ (エレキギターのピックアップ用) の仕様案1「金属ショートネジ」#5-40 UNC×8.5 の図面を、
株式会社カネコの A4 図面書式で PDF に出力する。

元の資料: お問合せメール (TEMP-BEXSNU) の「仕様案1: 金属ショートネジ仕様」と「基本スペック」。
- 頭部: マイナス溝付きフィリスター頭、外径 約5.0。厚みは仕様案2の頭部の値 (約2.5) を使う。
- ねじ: #5-40 UNC。長さ 8.5 (依頼者の指定。メールの「全長 約8.0〜8.5」の上限)。先端は面取り。
- 材質: S10C相当材 (依頼者の指定)。磁性が必要なのでステンレスは不可。
- 表面処理: ニッケルめっき または 金めっき (両方の可能性がある)。
こちらで決めた値 (要確認):
- 8.5 は首下長さ (座面から先端まで) とした。頭部を含めた全長は 11.0 (参考寸法)。
- 頭部の形は make_polepiece.py の金属頭部と同じ (上面 R8、すりわり 幅 0.8 × 深さ 1.0、座面側の角 C0.2)。
- ねじの等級は 2A。首下まで全ねじとし、首下の不完全ねじ部は 2 山以下。
- 先端の面取りは C0.4 (谷の径 φ2.40 付近まで)。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, arrow, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402
from make_polepiece import (DK, KH, RC, N, T, CH, D, D1, P_, THICK, THIN,  # noqa: E402
                            crown_x, fmt, head_view, notes, pl)

LN = 8.5            # 首下長さ
CT = 0.4            # 先端の面取り
LI = 2 * P_         # 首下の不完全ねじ部 (2 山)
L = KH + LN         # 全長 (参考)
S = 10.0            # 尺度 10/1

TITLE = {"品番": "", "図番": "", "得意先": "", "品名": "ポールピースねじ #5-40 UNC×8.5",
         "尺度": "10/1", "材質": "S10C相当材", "表面処理": "ニッケルめっき または 金めっき"}
FILE = "ポールピースねじ_No5-40UNCx8.5.pdf"


def draw(sh):
    R, r, r1, hn = DK / 2, D / 2, D1 / 2, N / 2
    Y0 = 40.0
    gap = 32.0
    left = -(S * DK + gap + S * L) / 2 - 5.0
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (外形図。すりわりは紙面に垂直)
    xe = crown_x(R)
    crown = [(crown_x(hn + (R - hn) * i / 40), hn + (R - hn) * i / 40) for i in range(41)]
    for sg in (1, -1):
        pl(sh, P, crown + [(KH - CH, R), (KH, R - CH), (KH, r), (L - CT, r), (L, r - CT)], sg)
        pl(sh, P, [(crown_x(hn), hn), (T, hn)], sg)          # すりわりの側面
        pl(sh, P, [(xe, hn), (xe, R)], sg)                   # 上面の丸みと外周の境
        pl(sh, P, [(KH + LI, r1), (L, r1)], sg, THIN)        # ねじの谷の径 (細線)
    pl(sh, P, [(T, -hn), (T, hn)])                           # すりわりの底
    pl(sh, P, [(KH - CH, -R), (KH - CH, R)])                 # 座面側の面取りの境
    pl(sh, P, [(KH + LI, -r), (KH + LI, r)])                 # 完全ねじ部の境
    pl(sh, P, [(L, -(r - CT)), (L, r - CT)])                 # 先端面
    pl(sh, P, [(L - CT, -r), (L - CT, r)])                   # 先端の面取りの境
    sh.line(*P(-0.3, 0), *P(L + 0.3, 0), THIN, 6)

    # ---- 頭部側から見た図
    head_view(sh, HX, Y0, S)

    # ---- 寸法 (上: すりわりの深さと頭部の高さ、下: 首下長さと全長)
    top = Y0 + S * R + 8.0
    yt = P(0, hn)[1]
    hdim(sh, P(0, 0)[0], P(T, 0)[0], top, yt, yt, fmt(T))
    hdim(sh, P(0, 0)[0], P(KH, 0)[0], top + 10.0, yt, P(KH, R - CH)[1], fmt(KH))
    yb = P(0, -hn)[1]
    hdim(sh, P(KH, 0)[0], P(L, 0)[0], Y0 - S * R - 8.0, P(KH, -R + CH)[1], P(L, -(r - CT))[1], fmt(LN))
    hdim(sh, P(0, 0)[0], P(L, 0)[0], Y0 - S * R - 18.0, yb, P(L, -(r - CT))[1], f"({fmt(L)})")
    # 上面の丸み R8 (矢印を外側から当てる)
    ya = 1.8
    xa = crown_x(ya)
    ux, uy = xa - RC, ya
    n = math.hypot(ux, uy)
    tx, ty = P(xa, ya)
    leader(sh, tx, ty, tx + ux / n * 12.0, ty + uy / n * 12.0, f"R{fmt(RC)}", side="L")
    # ねじの呼びと先端の面取り
    leader(sh, *P(KH + 4.5, r), P(KH + 4.5, 0)[0] + 8.0, Y0 + S * r + 10.0, "#5-40 UNC-2A")
    leader(sh, *P(L - CT / 2, r - CT / 2), P(L, 0)[0] + 6.0, Y0 + S * r + 6.0, f"C{fmt(CT)}", size=3.5)
    # 頭部側から見た図: 外径 (左) とすりわりの幅 (右、矢印を外側から当てる)
    vdim(sh, Y0 - S * R, Y0 + S * R, HX - S * R - 8.0, HX - 1.0, HX - 1.0, f"φ{fmt(DK)}")
    xs = math.sqrt(R * R - hn * hn)
    xn = HX + S * R + 7.0
    for sg in (1, -1):
        sh.line(HX + S * xs + 1.0, Y0 + sg * S * hn, xn + 1.5, Y0 + sg * S * hn)
    sh.line(xn, Y0 - S * hn - 5.0, xn, Y0 + S * hn + 13.0)
    arrow(sh, xn, Y0 - S * hn, 0, 1)
    arrow(sh, xn, Y0 + S * hn, 0, -1)
    sh.text(xn - 1.0, Y0 + S * hn + 7.5, fmt(N), 4.5, ang=90, align="C")

    notes(sh, [
        "1. ねじはユニファイ並目ねじ #5-40 UNC-2A とし、首下まで\n切る。首下の不完全ねじ部は 2 山以下とする。",
        "2. 普通公差は JIS B 0405-m (中級) とする。",
        "3. 指示のない面取りは C0.2、首下の隅は R0.2 以下とする。",
        "4. 表面処理はニッケルめっき または 金めっきとし、\n注文ごとに指定する。",
        "5. めっき後に #5-40 UNC のめねじにはまること。",
        "6. 磁性が必要なので、ステンレスに替えないこと。",
    ], y0=-4.0)


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
