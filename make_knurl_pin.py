# -*- coding: utf-8 -*-
"""ローレットピン φ1×5 の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

元の資料: 依頼者の指定 (ローレットのない軸部 φ1、全長 5) と写真 2 枚 (現物と「Φ1×5mm ローレットピン」のカタログ)。
写真から読んだ形 (寸法の指定がないので、写真から決めた値。要確認):
- ローレット部の長さは 1.5 (写真では全長の 3 割前後)。ローレットは綾目 (斜めに交差した目)。
- ローレット後の外径は φ1.1 (参考)。ローレットで盛り上がった分を見込んだ値で、加工後に決まる。
- ローレット側の端面は平らで、角は C0.1。
- 反対側の先端は C0.2 の面取り。依頼者の指示で粗先 (面取りなしで切ったまま) でもよい。
- 正面図は軸を横向きにし、ローレット側を左に置く。ローレット側から見た図を左に置く。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402
from make_knurl_screw import fmt, hatch  # noqa: E402
from make_polepiece import notes  # noqa: E402

D = 1.0         # 軸部の径
DK = 1.1        # ローレット後の外径 (参考)
L = 5.0         # 全長
LK = 1.5        # ローレット部の長さ
CK = 0.1        # ローレット側の端面の面取り
CT = 0.2        # 反対側の先端の面取り
S = 20.0        # 尺度 20/1
TITLE = {"品番": "", "図番": "", "得意先": "", "品名": "ローレットピン φ1×5",
         "尺度": "20/1", "材質": "", "表面処理": ""}
FILE = "ローレットピン_φ1x5.pdf"


def draw(sh):
    R, r = DK / 2, D / 2
    Y0 = 38.0
    gap = 34.0
    left = -(S * DK + gap + S * L) / 2 - 8.0
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (ローレット側を左)
    sh.line(*P(0, -(R - CK)), *P(0, R - CK), 6)                  # ローレット側の端面
    for sg in (1, -1):
        sh.line(*P(0, sg * (R - CK)), *P(CK, sg * R), 6)          # 端面の面取り
        sh.line(*P(CK, sg * R), *P(LK, sg * R), 6)                # ローレット部の外周
        sh.line(*P(LK, sg * R), *P(LK, sg * r), 6)                # ローレット部と軸部の段
        sh.line(*P(LK, sg * r), *P(L - CT, sg * r), 6)            # 軸部
        sh.line(*P(L - CT, sg * r), *P(L, sg * (r - CT)), 6)      # 先端の面取り
    sh.line(*P(CK, -R), *P(CK, R), 6)                            # 面取りの境
    sh.line(*P(L - CT, -r), *P(L - CT, r), 6)
    sh.line(*P(L, -(r - CT)), *P(L, r - CT), 6)                  # 先端面
    sh.line(*P(-0.1, 0), *P(L + 0.1, 0), 1, 6)                   # 中心線
    box = [P(CK, -R), P(LK, -R), P(LK, R), P(CK, R)]             # ローレット (綾目) を細線で示す
    hatch(sh, box, 30, 2.5)
    hatch(sh, box, -30, 2.5)

    # ---- ローレット側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * R, 6)
    sh.circle(HX, Y0, S * (R - CK), 6)                           # 面取りの境
    sh.line(HX - S * R - 3, Y0, HX + S * R + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * R - 3, HX, Y0 + S * R + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * R + 9.0
    hdim(sh, P(0, 0)[0], P(LK, 0)[0], top, P(0, R - CK)[1], P(LK, R)[1], fmt(LK))
    bot = Y0 - S * R - 12.0
    hdim(sh, P(0, 0)[0], P(L, 0)[0], bot, P(0, -(R - CK))[1], P(L, -(r - CT))[1], fmt(L))
    vdim(sh, P(0, -R)[1], P(0, R)[1], X0 - 10.0, P(CK, -R)[0], P(CK, R)[0], f"(φ{fmt(DK)})")
    vdim(sh, P(0, -r)[1], P(0, r)[1], P(L, 0)[0] + 10.0, P(L - CT, -r)[0], P(L - CT, r)[0], f"φ{fmt(D)}")
    leader(sh, *P(CK / 2, -(R - CK / 2)), X0 - 4.0, Y0 - S * R - 4.0, f"C{fmt(CK)}", size=3.5, side="L")
    leader(sh, *P(L - CT / 2, r - CT / 2), P(L, 0)[0] + 3.0, Y0 + S * R + 6.0, f"C{fmt(CT)}", size=3.5)
    leader(sh, *P(LK * 0.6, R), P(LK, 0)[0] + 12.0, top + 4.0, "ローレット 綾目", size=3.5)

    notes(sh, [
        "1. 普通公差は JIS B 0405-m (中級) とする。",
        f"2. ローレット後の外径 φ{fmt(DK)} は参考寸法とする。",
        f"3. ローレットと反対側の先端は C{fmt(CT)} とするが、\n粗先 (面取りなし) でもよい。",
        "4. 指示のない角はバリを取ること。",
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
