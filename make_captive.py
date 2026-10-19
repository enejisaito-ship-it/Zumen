# -*- coding: utf-8 -*-
"""脱落防止ねじ (M2 × 全長 7.2、平頭、ヘクサロビュラ T8) の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

株式会社ビーエヌテクノロジー様のお問合せ (管理番号 TEMP-7D6H73) の推定寸法と添付写真から起こした仮の図面。
首部をねじ部の谷の径より細くし、相手のめねじを通り抜けたあとに抜け落ちない形とする。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402

SCREW = {
    "dk": 5.2,     # 頭部の径 (お客様推定)
    "k": 2.0,      # 頭部の厚さ (お客様推定)
    "ch": 0.2,     # 頭部上面の角の面取り (写真から仮定)
    "d": 2.0,      # ねじの呼び径 M2 (写真から推定。山の径 約1.9)
    "p": 0.4,      # ピッチ (並目。写真から推定)
    "d1": 1.57,    # ねじの谷の径 (図の線用)
    "L": 7.2,      # 全長 (お客様推定)
    "ln": 3.0,     # 首部の長さ = 抜け止め部分 (お客様推定。写真では約2.9)
    "dn": 1.3,     # 首部の径 (写真から推定。M2 めねじの内径より細く)
    "c": 0.2,      # ねじ先の面取り
    "ta": 2.4,     # T8 穴の山の径 (図の形だけ)
    "tb": 1.75,    # T8 穴の谷の径 (図の形だけ)
    "td": 0.8,     # T8 穴の深さ (図の形だけ。寸法は入れない)
}
SCALE = 10.0
TITLE = {"品番": "", "図番": "", "得意先": "株式会社ビーエヌテクノロジー",
         "品名": "脱落防止ねじ M2×7.2", "尺度": "10/1", "材質": ""}
FILE = "脱落防止ねじ_M2x7.2.pdf"


def fmt(v):
    return f"{v:g}"


def draw_screw(sh, s=SCREW):
    S = SCALE
    rD, rd, r1, rn = s["dk"] / 2, s["d"] / 2, s["d1"] / 2, s["dn"] / 2
    k, L, ch, c = s["k"], s["L"], s["ch"], s["c"]
    xb = k + s["ln"]                                        # ねじ部の始まり
    cb = rd - rn                                            # ねじ部の首側の面取り (45°)
    Y0 = 40.0
    gap = 30.0
    left = -(S * s["dk"] + gap + S * L + 25.0) / 2
    HX = left + S * rD
    X0 = HX + S * rD + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 外形 (頭部を左、ねじ先を右)
    sh.line(*P(0, -(rD - ch)), *P(0, rD - ch), 6)                   # 頭部上面
    for sg in (1, -1):
        sh.line(*P(0, sg * (rD - ch)), *P(ch, sg * rD), 6)          # 頭部上面の面取り
        sh.line(*P(ch, sg * rD), *P(k, sg * rD), 6)                 # 頭部の外周
        sh.line(*P(k, sg * rD), *P(k, sg * rn), 6)                  # 座面
        sh.line(*P(k, sg * rn), *P(xb, sg * rn), 6)                 # 首部
        sh.line(*P(xb, sg * rn), *P(xb + cb, sg * rd), 6)           # ねじ部 首側の面取り
        sh.line(*P(xb + cb, sg * rd), *P(L - c, sg * rd), 6)        # ねじの山の径
        sh.line(*P(L - c, sg * rd), *P(L, sg * (rd - c)), 6)        # ねじ先の面取り
        sh.line(*P(xb + cb, sg * r1), *P(L, sg * r1), 1)            # ねじの谷の径 (細線)
        sh.line(*P(0, sg * s["ta"] / 2), *P(s["td"], sg * s["ta"] / 2), 1, 2)   # T8 穴 (かくれ線)
    sh.line(*P(ch, -rD), *P(ch, rD), 6)                             # 面取りの境
    sh.line(*P(L, -(rd - c)), *P(L, rd - c), 6)                     # 先端面
    sh.line(*P(s["td"], -s["ta"] / 2), *P(s["td"], s["ta"] / 2), 1, 2)
    sh.line(*P(-0.3, 0), *P(L + 0.3, 0), 1, 6)                      # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rD, 6)
    sh.circle(HX, Y0, S * (rD - ch), 6)                             # 面取りの境
    ra, rb = s["ta"] / 2, s["tb"] / 2                               # T8 穴 (6 つの山の略図)
    n = 120
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        r = (ra + rb) / 2 + (ra - rb) / 2 * math.cos(6 * t)
        pts.append((HX + S * r * math.cos(t), Y0 + S * r * math.sin(t)))
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        sh.line(x1, y1, x2, y2, 6)
    sh.line(HX - S * rD - 3, Y0, HX + S * rD + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * rD - 3, HX, Y0 + S * rD + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * rD + 8.0
    hdim(sh, P(0, 0)[0], P(k, 0)[0], top, P(0, rD - ch)[1], P(k, rD)[1], fmt(k))
    hdim(sh, P(k, 0)[0], P(xb, 0)[0], top, P(k, rD)[1], P(xb, rn)[1], fmt(s["ln"]))
    bot1 = Y0 - S * rD - 8.0
    bot2 = bot1 - 10.0
    hdim(sh, P(xb, 0)[0], P(L, 0)[0], bot1, P(xb, -rn)[1], P(L, -(rd - c))[1], f"({fmt(L - xb)})")
    hdim(sh, P(0, 0)[0], P(L, 0)[0], bot2, P(0, -(rD - ch))[1], P(L, -(rd - c))[1], fmt(L))
    vdim(sh, P(0, -rD)[1], P(0, rD)[1], X0 - 8.0, P(ch, -rD)[0], P(ch, rD)[0], f"φ{fmt(s['dk'])}")
    leader(sh, *P(ch / 2, rD - ch / 2), X0 - 6.0, top + 8.0, f"C{fmt(ch)}", side="L")
    leader(sh, *P(k + 1.0, rn), P(k, 0)[0] + 6.0, Y0 + S * rD - 6.0,
           f"首部 φ{fmt(s['dn'])}", size=3.5)
    leader(sh, *P(L - 0.8, rd), P(L, 0)[0] + 6.0, Y0 + S * rD - 4.0,
           f"M{fmt(s['d'])}×{fmt(s['p'])}")
    leader(sh, HX + S * ra * math.cos(math.radians(30)), Y0 - S * ra * math.sin(math.radians(30)) * 0.4,
           HX + S * rD - 2.0, Y0 - S * rD - 10.0, "ヘクサロビュラ T8", size=3.5)

    # ---- 注記
    notes = ["注記",
             "1. 寸法はお客様の推定値と写真から読み取った",
             "   仮の値。サンプル測定後に確定する。",
             "2. 材質は鉄またはステンレス (未定)。",
             f"3. 首部はM{fmt(s['d'])}めねじの内径より細くし、",
             "   ねじ込み後に脱落しないこと。",
             "4. 駆動穴の形と深さはサンプルに合わせる。",
             "5. 指示のない角はバリなきこと。"]
    y = -14.0
    for i, t in enumerate(notes):
        sh.text(-135.0, y, t, 4.0 if i == 0 else 3.5, sp=0.3)
        y -= 6.0 if i == 0 else 5.2


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw_screw(sh)
    render(sh, os.path.join(out, FILE), f'{TITLE["品名"]}')
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
