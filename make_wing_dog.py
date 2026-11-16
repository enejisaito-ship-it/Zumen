# -*- coding: utf-8 -*-
"""冷間蝶ボルト (OPG・ウィット) W3/8 のねじ先を棒先にしたものの図面を、株式会社カネコの A4 図面書式で PDF に出力する。

頭部の寸法は弊社の規格表 (冷間蝶ボルト OPG ウィット、C00G12) の W3/8 の値を使う。
D 羽根の幅 (36±1.5)、H 頭部の高さ (19.1±1.5)、C 胴の高さ (10±1.0)、φA つばの径 (16±1.5)、G 羽根の厚さ (5.5)。
規格表のねじ先は標準でヘッダポイントだが、この図面では写真のような棒先 (先が細い円筒で、端の角を丸めた形) にする。
棒先の径と長さは規格表に無いので、JIS B 1117 (棒先の六角穴付き止めねじ) の M10 の値に合わせて仮に決めた。
羽根と胴の輪郭は規格表の図から読み取った略図で、寸法を入れていない部分は形だけ。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, arrow, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402

THICK, THIN = 6, 1
S = 2.0                     # 尺度 2/1
W = {
    "D": 36.0, "D_tol": "±1.5",    # 羽根の幅
    "H": 19.1, "H_tol": "±1.5",    # 頭部の高さ (羽根の端から座面まで)
    "C": 10.0, "C_tol": "±1.0",    # 胴の高さ (胴の頭から座面まで)
    "A": 16.0, "A_tol": "±1.5",    # つばの径
    "G": 5.5,                      # 羽根の厚さ
    "tc": 2.0,                     # つばの厚さ (図の形だけ)
    "d": 9.525,                    # W3/8 の外径 (3/8 インチ)
    "d1": 7.493,                   # W3/8 の谷の径 (図の線用。寸法は入れない)
    "thread": "W3/8",
    "L": 45.0,                     # 呼び長さ (座面からねじ先まで)
    "dp": 7.0,                     # 棒先の径 (仮。JIS B 1117 M10 に合わせる)
    "z": 5.0,                      # 棒先の長さ (仮。同上)
    "rr": 1.0,                     # 棒先の端の角の丸み (仮)
}
TITLE = {"品番": "", "図番": "", "得意先": "", "尺度": "2/1", "材質": "", "表面処理": ""}
NAME = "冷間蝶ボルト 棒先 W3/8×45"
FILE = "冷間蝶ボルト_棒先_W3-8x45.pdf"


def fmt(v):
    return f"{v:g}"


def bezier(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def poly(sh, pts, pen=THICK, style=1):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        sh.line(x1, y1, x2, y2, pen, style)


def notes(sh, lines, y0=0.0, size=3.5):
    """注記。書式の訂正欄 (y = -54 より下) にかからないよう、図と表題欄の間の左側に書く。"""
    sh.text(-130.0, y0, "注記", 4.0)
    y = y0 - 7.0
    for s in lines:
        sh.text(-126.0, y, s, size)
        y -= size + 2.0


def draw(sh, w=W):
    rA, rd, r1, rp = w["A"] / 2, w["d"] / 2, w["d1"] / 2, w["dp"] / 2
    L, z, rr, tc = w["L"], w["z"], w["rr"], w["tc"]
    half = w["D"] / 2
    Y0 = 40.0
    gap = 34.0
    left = -(2 * S * rA + gap + S * (w["H"] + L)) / 2
    HX = left + S * rA                    # 頭部側から見た図の中心
    X0 = HX + S * rA + gap + S * w["H"]   # 正面図の座面の位置

    # 正面図の座標: u は座面から頭部側への距離、t は座面からねじ先側への距離
    def U(u, y):
        return X0 - S * u, Y0 + S * y

    def T(t, y):
        return X0 + S * t, Y0 + S * y

    # ---- 正面図 頭部 (羽根の輪郭は規格表の図から読み取った略図)
    tipc, tipr = (w["H"] - 4.2, half - 4.2), 4.2        # 羽根の先の丸み: 上端が D/2、頭側の端が H
    a_out, a_in = 110.0, -60.0                           # 羽根の外側と内側の線が丸みから離れる角度
    collar_y = 7.3                                       # 羽根の外側の線がつばに付く高さ
    dome_u, dome_y = w["C"] - 0.8, 4.5                   # 羽根の内側の線が胴の頭に付く点
    Rd = (0.8 ** 2 + dome_y ** 2) / (2 * 0.8)            # 胴の頭の丸み (u = C で軸と交わる)

    def tp(a):
        return tipc[0] + tipr * math.cos(math.radians(a)), tipc[1] + tipr * math.sin(math.radians(a))

    for sg in (1, -1):
        def M(pts):
            return [U(u, sg * y) for u, y in pts]
        p_out, p_in = tp(a_out), tp(a_in)
        arc = [tp(a_out + (a_in - a_out) * i / 60) for i in range(61)]
        poly(sh, M(arc))                                                       # 羽根の先
        poly(sh, M(bezier(p_out, (8.0, 15.8), (tc, collar_y))))                # 羽根の外側
        poly(sh, M(bezier(p_in, (13.5, 8.0), (dome_u, dome_y))))               # 羽根の内側
        poly(sh, M([(tc + (dome_u - tc) * i / 20, 6.5 - 2.0 * (i / 20) ** 0.7)
                    for i in range(21)]))                                      # 胴の外周
        sh.line(*U(tc, sg * collar_y), *U(tc, sg * rA), THICK)                 # つばの裏
        sh.line(*U(0, sg * rA), *U(tc, sg * rA), THICK)                        # つばの外周
        an = math.degrees(math.asin(dome_y / Rd))
        dome = [(w["C"] - Rd + Rd * math.cos(math.radians(an * i / 20)), Rd * math.sin(math.radians(an * i / 20)))
                for i in range(21)]
        poly(sh, M(dome))                                                      # 胴の頭
    sh.line(*U(0, -rA), *U(0, rA), THICK)                                      # 座面

    # ---- 正面図 ねじ部と棒先
    tz = L - z                       # 棒先の始まり
    t1 = tz - (rd - rp)              # ねじの終わり (45° でしぼる)
    for sg in (1, -1):
        sh.line(*T(0, sg * rd), *T(t1, sg * rd), THICK)                        # ねじの山の径
        sh.line(*T(1.6, sg * r1), *T(t1, sg * r1), THIN)                       # ねじの谷の径 (細線)
        sh.line(*T(t1, sg * rd), *T(tz, sg * rp), THICK)                       # しぼり
        sh.line(*T(tz, sg * rp), *T(L - rr, sg * rp), THICK)                   # 棒先
    sh.line(*T(t1, -rd), *T(t1, rd), THICK)
    sh.line(*T(tz, -rp), *T(tz, rp), THICK)
    sh.line(*T(L, -(rp - rr)), *T(L, rp - rr), THICK)                          # 先端面
    cx = T(L - rr, 0)[0]
    sh.arc(cx, T(0, rp - rr)[1], S * rr, 0, 90, THICK)                         # 先端の角の丸み
    sh.arc(cx, T(0, -(rp - rr))[1], S * rr, 270, 360, THICK)
    sh.line(*U(w["C"] + 1.0, 0), *T(L + 1.5, 0), THIN, 6)                      # 中心線

    # ---- 頭部側から見た図 (第三角法: 左に置く)
    g = w["G"] / 2
    gx = S * g
    hub_r = 6.5
    for r in (rA, hub_r):                                                      # つばと胴の外周 (羽根の後ろは切る)
        a = math.degrees(math.asin(g / r))
        sh.arc(HX, Y0, S * r, -90 + a, 90 - a, THICK)
        sh.arc(HX, Y0, S * r, 90 + a, 270 - a, THICK)
    sh.circle(HX, Y0, S * dome_y, THICK)                                       # 胴の頭
    for sg in (1, -1):
        y0 = math.sqrt(dome_y ** 2 - g ** 2)
        for sx in (1, -1):
            sh.line(HX + sx * gx, Y0 + sg * S * y0, HX + sx * gx, Y0 + sg * S * (half - g), THICK)
        a0, a1 = (0, 180) if sg > 0 else (180, 360)
        sh.arc(HX, Y0 + sg * S * (half - g), gx, a0, a1, THICK)                # 羽根の端
    sh.line(HX - S * half - 3, Y0, HX + S * half + 3, Y0, THIN, 6)
    sh.line(HX, Y0 - S * half - 3, HX, Y0 + S * half + 3, THIN, 6)

    # ---- 寸法
    top = Y0 + S * half + 7.0
    hdim(sh, U(w["H"], 0)[0], X0, top, U(0, tipc[1])[1], Y0 + S * rA,
         f"{fmt(w['H'])}{w['H_tol']}")
    ztop = Y0 + S * rd + 8.0
    hdim(sh, T(tz, 0)[0], T(L, 0)[0], ztop, T(0, rp)[1], T(0, rp)[1], fmt(z))
    bot = Y0 - S * half - 7.0
    hdim(sh, U(w["C"], 0)[0], X0, bot, Y0, Y0 - S * rA, f"{fmt(w['C'])}{w['C_tol']}", outside=True)
    hdim(sh, X0, T(L, 0)[0], bot, Y0 - S * rA, T(0, -(rp - rr))[1], fmt(L))
    vdim(sh, U(0, -half)[1], U(0, half)[1], U(w["H"], 0)[0] - 8.0,
         U(tipc[0], 0)[0], U(tipc[0], 0)[0], f"{fmt(w['D'])}{w['D_tol']}")
    hdim(sh, HX - gx, HX + gx, Y0 - S * half - 7.0, Y0 - S * (half - g), Y0 - S * (half - g),
         fmt(w["G"]), outside=True)
    # つばの径: 座面のすぐ右に寸法線を引き、数値は上の寸法補助線の外に置く
    xa = X0 + 6.0
    ya1, ya2 = Y0 - S * rA, Y0 + S * rA
    for yy in (ya1, ya2):
        sh.line(X0 + 1.0, yy, xa + 1.5, yy)
    lab = f"φ{fmt(w['A'])}{w['A_tol']}"
    sh.line(xa, ya1, xa, ya2 + 3.0 + 16.0)
    arrow(sh, xa, ya1, 0, -1)
    arrow(sh, xa, ya2, 0, 1)
    sh.text(xa - 1.0, ya2 + 2.0, lab, 4.0, ang=90)
    # 棒先の径: 棒先の中に寸法線を引く
    xm = T(tz + z * 0.45, 0)[0]
    y1, y2 = Y0 - S * rp, Y0 + S * rp
    sh.line(xm, y1, xm, y2, THIN)
    arrow(sh, xm, y1, 0, -1)
    arrow(sh, xm, y2, 0, 1)
    sh.text(xm - 1.0, Y0 - S * rp * 0.5, f"φ{fmt(w['dp'])}", 4.0, ang=90, align="C")
    # 先端の丸み
    a = math.radians(45)
    leader(sh, cx + S * rr * math.cos(a), T(0, -(rp - rr))[1] - S * rr * math.sin(a),
           T(L, 0)[0] + 6.0, Y0 - S * rp - 8.0, f"R{fmt(rr)}")
    # ねじの呼び
    leader(sh, *T(t1 * 0.6, rd), T(t1 * 0.4, 0)[0], ztop + 2.0, w["thread"])


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, dict(TITLE, 品名=NAME))
    draw(sh)
    notes(sh, ["普通公差は JIS B 0405-m とする。"], y0=-14.0)
    render(sh, os.path.join(out, FILE), NAME)
    print("ok", FILE)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
