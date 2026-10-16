# -*- coding: utf-8 -*-
"""株式会社アヴァンティ 見積依頼 (2026/6/2) の照号1〜3 ピン (AVT-001〜003) の図面を、
株式会社カネコの A4 図面書式で 1 点ずつ PDF に出力する。

M4 タップは下穴までとし、ねじ立ては行わない。下穴の深さは M4 タップ有効長 (指定寸法) 以上とする。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, arrow, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402

TAP_DRILL = 3.3        # M4 並目 (P0.7) のタップ下穴径
DRILL_ANGLE = 118.0    # ドリル先端角

# 寸法は依頼書の手書き図から読んだ実寸 (mm)
PINS = [
    {"品番": "AVT-001", "品名": "照号1ﾋﾟﾝ SUS304 φ20X50", "file": "AVT-001.pdf",
     "D": 32.0, "H": 6.0, "C": 2.0,                 # 頭部の径、厚さ、頭部上面の面取り
     "d": 20.0, "L": 50.0, "R": 0.5,                # 軸径、首下長さ、首下の丸み
     "ea": 3.0, "eb": 3.0,                          # 先端の面取り (径方向, 軸方向)
     "hd": 3.5, "hp": 6.5,                          # 横穴の径、先端からの位置
     "td": 15.0,                                    # M4 タップ有効長 (下穴はこれ以上の深さ)
     "scale": 2.0, "尺度": "2/1"},
    {"品番": "AVT-002", "品名": "照号2ﾋﾟﾝ SUS304 φ10X32", "file": "AVT-002.pdf",
     "D": 15.0, "H": 4.0, "C": 1.0,
     "d": 10.0, "L": 32.0, "R": 0.5,
     "ea": 1.5, "eb": 2.0,
     "hd": 3.0, "hp": 4.0,
     "td": 12.0,
     "scale": 3.0, "尺度": "3/1"},
    {"品番": "AVT-003", "品名": "照号3ﾋﾟﾝ SUS304 φ20X55", "file": "AVT-003.pdf",
     "D": 32.0, "H": 6.0, "C": 2.0,
     "d": 20.0, "L": 55.0, "R": 0.5,
     "ea": 3.0, "eb": 3.0,
     "hd": 3.5, "hp": 6.5,
     "td": 15.0,
     "scale": 2.0, "尺度": "2/1"},
]


def fmt(v):
    return f"{v:g}"


def draw_pin(sh, p):
    S = p["scale"]
    D, H, C, d, L, R = p["D"], p["H"], p["C"], p["d"], p["L"], p["R"]
    ea, eb, hd, hp, td = p["ea"], p["eb"], p["hd"], p["hp"], p["td"]
    rD, rd, rt = D / 2, d / 2, TAP_DRILL / 2
    T = H + L                                       # 全長
    Y0 = 32.0                                       # 中心線の高さ
    gap = 30.0                                      # 側面図と正面図の間
    left = -(S * D + gap + S * T + 25.0) / 2        # 図の並びを用紙の左右中央に
    HX = left + S * rD                              # 頭部側から見た図の中心
    X0 = HX + S * rD + gap                          # 正面図の頭部上面

    def P(x, r):
        return X0 + S * x, Y0 + S * r

    # ---- 正面図 外形 (頭部を左、軸を右)
    for sg in (1, -1):
        sh.line(*P(0, sg * (rD - C)), *P(C, sg * rD), 6)            # 頭部上面の面取り
        sh.line(*P(C, sg * rD), *P(H, sg * rD), 6)                  # 頭部外周
        sh.line(*P(H, sg * rD), *P(H, sg * (rd + R)), 6)            # 頭部の首下側の面
        sh.line(*P(H + R, sg * rd), *P(T - eb, sg * rd), 6)         # 軸
        sh.line(*P(T - eb, sg * rd), *P(T, sg * (rd - ea)), 6)      # 先端の面取り
    cx, cy = P(H + R, rd + R)
    sh.arc(cx, cy, S * R, 180, 270, 6)                              # 首下の丸み
    cx, cy = P(H + R, -(rd + R))
    sh.arc(cx, cy, S * R, 90, 180, 6)
    sh.line(*P(0, -(rD - C)), *P(0, rD - C), 6)                     # 頭部上面
    sh.line(*P(C, -rD), *P(C, rD), 6)                               # 面取りの稜線
    sh.line(*P(T - eb, -rd), *P(T - eb, rd), 6)
    sh.line(*P(T, -(rd - ea)), *P(T, rd - ea), 6)                   # 先端面
    # タップ下穴 (かくれ線)
    tip = rt / math.tan(math.radians(DRILL_ANGLE / 2))
    for sg in (1, -1):
        sh.line(*P(0, sg * rt), *P(td, sg * rt), 1, 2)
        sh.line(*P(td, sg * rt), *P(td + tip, 0), 1, 2)
    sh.line(*P(td, -rt), *P(td, rt), 1, 2)
    # 横穴 (紙面に垂直な貫通穴)
    hx, _ = P(T - hp, 0)
    sh.circle(hx, Y0, S * hd / 2, 6)
    sh.line(hx, Y0 - S * hd / 2 - 3, hx, Y0 + S * hd / 2 + 3, 1, 6)
    sh.line(*P(-1.5, 0), *P(T + 1.5, 0), 1, 6)                      # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rD, 6)
    sh.circle(HX, Y0, S * (rD - C), 6)                              # 面取りの稜線
    sh.circle(HX, Y0, S * rd, 1, 2)                                 # 軸 (かくれ線)
    sh.circle(HX, Y0, S * rt, 6)                                    # タップ下穴
    w = math.sqrt(rd ** 2 - (hd / 2) ** 2)
    for sg in (1, -1):                                              # 横穴 (かくれ線)
        sh.line(HX - S * w, Y0 + sg * S * hd / 2, HX + S * w, Y0 + sg * S * hd / 2, 1, 2)
    sh.line(HX - S * rD - 3, Y0, HX + S * rD + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * rD - 3, HX, Y0 + S * rD + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * rD + 8.0
    bot = Y0 - S * rD - 10.0
    hdim(sh, P(0, 0)[0], P(H, 0)[0], top, P(0, rD - C)[1], P(H, rD)[1], fmt(H),
         outside=S * H < 10)
    hdim(sh, hx, P(T, 0)[0], Y0 + S * rd + 8.0, Y0 + S * hd / 2, P(T, rd - ea)[1], fmt(hp),
         outside=S * hp < 10)
    hdim(sh, P(H, 0)[0], P(T, 0)[0], bot, P(H, -rD)[1], P(T, -(rd - ea))[1], fmt(L))
    hdim(sh, P(0, 0)[0], P(T, 0)[0], bot - 8.0, P(0, -(rD - C))[1], P(T, -(rd - ea))[1],
         f"({fmt(T)})")
    vdim(sh, P(0, -rD)[1], P(0, rD)[1], X0 - 8.0, P(C, -rD)[0], P(C, rD)[0], f"φ{fmt(D)}")
    xr = P(T, 0)[0] + 12.0
    vdim(sh, P(0, -rd)[1], P(0, rd)[1], xr, P(T - eb, 0)[0], P(T - eb, 0)[0], f"φ{fmt(d)}")

    # 頭部上面の面取り
    leader(sh, *P(C / 2, rD - C / 2), P(-3, 0)[0] - 4, top + 10.0, f"C{fmt(C)}", side="L")
    # 首下の丸み
    fx, fy = P(H + R * (1 - math.sqrt(0.5)), -(rd + R * (1 - math.sqrt(0.5))))
    leader(sh, fx, fy, fx + 14.0, bot + 5.0, f"R{fmt(R)}")
    # 先端の面取り
    if ea == eb:
        leader(sh, *P(T - eb / 2, -(rd - ea / 2)), P(T, 0)[0] + 6.0, bot + 3.0, f"C{fmt(ea)}")
    else:
        hdim(sh, P(T - eb, 0)[0], P(T, 0)[0], Y0 - S * rd - 6.0, P(T - eb, -rd)[1],
             P(T, -(rd - ea))[1], fmt(eb), outside=S * eb < 10)
        # 径方向は上側の角に記入。外側の補助線は φd の補助線と共用
        xe = P(T, 0)[0] + 7.0
        y_out, y_in = P(0, rd)[1], P(0, rd - ea)[1]
        sh.line(P(T, 0)[0] + 1.0, y_in, xe + 1.5, y_in)
        sh.line(xe, y_in - 6.0, xe, y_out + 6.0)
        arrow(sh, xe, y_in, 0, 1)
        arrow(sh, xe, y_out, 0, -1)
        sh.text(xe - 1.0, y_out + 7.0, fmt(ea), 4.5, ang=90)
    # 横穴
    a = math.radians(45)
    leader(sh, hx - S * hd / 2 * math.cos(a), Y0 + S * hd / 2 * math.sin(a),
           hx - 20.0, top + 4.0, f"φ{fmt(hd)} 貫通", side="L")
    # タップ下穴 (頭部側から見た図)
    leader(sh, HX - S * rt * math.cos(a), Y0 - S * rt * math.sin(a),
           HX - 12.0, Y0 - S * rD - 8.0, f"M4タップ下穴 φ{fmt(TAP_DRILL)} 深さ{fmt(td)}以上",
           size=3.5, sub="(ねじ立てなし)")

    # ---- 注記
    notes = ["注記",
             f"1. M4タップは下穴 φ{fmt(TAP_DRILL)} までとし、ねじ立ては行わない。",
             f"   下穴の深さはM4タップ有効長（{fmt(td)}）以上とする。",
             "2. 指示のない角はバリなきこと。"]
    y = -30.0
    for i, s in enumerate(notes):
        sh.text(-135.0, y, s, 4.0 if i == 0 else 3.5, sp=0.3)
        y -= 6.0


def main(out):
    for p in PINS:
        sh = Sheet()
        load_template(sh)
        fill_title(sh, {"品番": p["品番"], "図番": "", "得意先": "株式会社アヴァンティ",
                        "品名": p["品名"], "尺度": p["尺度"], "材質": "SUS304"})
        draw_pin(sh, p)
        render(sh, os.path.join(out, p["file"]), f'{p["品番"]} {p["品名"]}')
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
