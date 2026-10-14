# -*- coding: utf-8 -*-
"""PLUG M8x0.75 追加工指示図 (第2案) を PDF で出力する。

元品: 図番 1546996 P54 (添付 1ページ目)  ->  完成品: 図番 21341250 01 (添付 2ページ目)
加工: 下端面を 0.25 削り、M8 外径の下側を φ6.8 まで削って段 (溝位置) を上へ移す。上端面は削らない。

座標は用紙上の mm (A4 横 297x210)。部品の座標は (r, y) = (中心からの半径方向, 完成品の下端面からの高さ) の実寸 mm。
"""
import math
import sys

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT = "IPAGothic"
pdfmetrics.registerFont(TTFont(FONT, "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))
FS = 1 / 0.88          # 文字高さ -> フォントサイズ

BLACK = (0, 0, 0)
RED = (0.85, 0.0, 0.0)
GRAY = (0.35, 0.35, 0.35)
PHANTOM = [5, 0.8, 0.8, 0.8, 0.8, 0.8]    # 二点鎖線
CHAIN = [6, 1, 1, 1]                      # 一点鎖線

# ---------------------------------------------------------------- 寸法 (実寸 mm)
T = 5.75            # 完成品の全長 (上端面は元品のまま)
H_LOW = 2.1         # 完成品: 溝位置から下端面まで
CUT_BOT = 0.25      # 下端面の削り量
A_TOTAL, A_LOW = 6.0, 2.2                 # 元品の基準寸法
A_BOT = -CUT_BOT                          # 元品の下端面の位置
A_GROOVE = A_BOT + A_LOW                  # 元品の溝位置 (1.95)
SHIFT = H_LOW - A_GROOVE                  # 段を上へ移す量 (0.15)

R_THR = 4.0
R_THR_MINOR = (8 - 1.082532 * 0.75) / 2   # M8x0.75 谷の径/2 (基準寸法)
CH_TOP = 0.75
R_COL = 3.4
R_BOT = 2.9
CH_BOT = R_COL - R_BOT                    # 0.5
STEP = R_THR - R_COL                      # 段の45°面取りの高さ (0.6)
R_GROOVE = 0.4
SOCK_HALF = 1.5
SOCK_DEPTH = 3.8    # 作図上の穴深さ (指示は 4 MAX)
SOCK_R = 1.0
SOCK_Y = T - SOCK_DEPTH


def arc_pts(cx, cy, r, a1, a2, n=8):
    return [(cx + r * math.cos(math.radians(a1 + (a2 - a1) * i / n)),
             cy + r * math.sin(math.radians(a1 + (a2 - a1) * i / n))) for i in range(n + 1)]


def groove_arc(yg):
    """段の入隅 R0.4 (上から下へ)。yg は面取りと φ6.8 の交点の高さ。"""
    return arc_pts(R_COL + R_GROOVE, yg - R_GROOVE * math.tan(math.radians(22.5)), R_GROOVE, 135, 180, 6)


def right_profile(yb, yg, yt=T):
    """右半分の外形 (上端面の穴縁から下端中心の手前まで、上から順)。"""
    return ([(SOCK_HALF, yt), (R_THR - CH_TOP, yt), (R_THR, yt - CH_TOP), (R_THR, yg + STEP)]
            + groove_arc(yg) + [(R_COL, yb + CH_BOT), (R_BOT, yb)])


def socket_pts():
    return ([(-SOCK_HALF, T)] + arc_pts(-SOCK_HALF + SOCK_R, SOCK_Y + SOCK_R, SOCK_R, 180, 270, 6)
            + arc_pts(SOCK_HALF - SOCK_R, SOCK_Y + SOCK_R, SOCK_R, 270, 360, 6) + [(SOCK_HALF, T)])


# ---------------------------------------------------------------- 描画の記録
prims = []


def line(x1, y1, x2, y2, w=0.25, color=BLACK, dash=None):
    prims.append(("line", (x1, y1, x2, y2), w, color, dash))


def polyline(pts, w=0.25, color=BLACK, dash=None, closed=False):
    pts = list(pts)
    if closed:
        pts.append(pts[0])
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], w, color, dash)


def circle(cx, cy, r, w=0.25, color=BLACK):
    prims.append(("circle", (cx, cy, r), w, color, None))


def solid(pts, color=BLACK):
    prims.append(("solid", pts, 0, color, None))


def text(x, y, s, h=3.0, rot=0.0, align="L", color=BLACK):
    prims.append(("text", (x, y, s, h, rot, align), 0, color, None))


def hatch(poly_pts, pitch=2.0, w=0.18, color=BLACK):
    prims.append(("hatch", (poly_pts, pitch), w, color, None))


def tw(s, h):
    return pdfmetrics.stringWidth(s, FONT, h * FS)


ARROW_L = 2.5
ARROW_W = ARROW_L * math.tan(math.radians(15))


def arrow(tx, ty, dx, dy, color=BLACK):
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    bx, by = tx - dx * ARROW_L, ty - dy * ARROW_L
    nx, ny = -dy * ARROW_W, dx * ARROW_W
    solid([(tx, ty), (bx + nx, by + ny), (bx - nx, by - ny)], color)


def hdim(x1, x2, y, f1, f2, label, color=BLACK, h=3.0, ext_right=0.0):
    for x, f in ((x1, f1), (x2, f2)):
        s = 1 if y > f else -1
        line(x, f + s * 1.0, x, y + s * 2.0, color=color)
    line(x1, y, x2 + ext_right, y, color=color)
    arrow(x1, y, -1, 0, color)
    arrow(x2, y, 1, 0, color)
    text((x1 + x2) / 2, y + 1.0, label, h, 0, "C", color)


def ext_h(y, x_from, x_to, color=BLACK):
    """水平の寸法補助線 (外形から 1mm 離して、寸法線の 2mm 先まで)。"""
    s = 1 if x_to > x_from else -1
    line(x_from + s * 1.0, y, x_to + s * 2.0, y, color=color)


def vdim_line(y1, y2, x, label, color=BLACK, h=3.0, small=False, text_side=None):
    """垂直の寸法線と数値。small=True は矢印を外側から当て、数値を横書きで右に置く。"""
    if small:
        line(x, y1 - ARROW_L - 2.5, x, y2 + ARROW_L + 2.5, color=color)
        arrow(x, y1, 0, 1, color)
        arrow(x, y2, 0, -1, color)
        ty = text_side if text_side is not None else (y1 + y2) / 2 - h / 2
        text(x + 1.5, ty, label, h, 0, "L", color)
    else:
        line(x, y1, x, y2, color=color)
        arrow(x, y1, 0, -1, color)
        arrow(x, y2, 0, 1, color)
        text(x - 1.0, (y1 + y2) / 2, label, h, 90, "C", color)


def vdim(y1, y2, x, f1, f2, label, color=BLACK, h=3.0):
    ext_h(y1, f1, x, color)
    ext_h(y2, f2, x, color)
    vdim_line(y1, y2, x, label, color, h)


def balloon_note(bx, by, num, target, lines_, color=RED, h=3.0):
    r = 3.2
    circle(bx, by, r, 0.35, color)
    text(bx, by - 1.3, str(num), 2.8, 0, "C", color)
    tx, ty = target
    d = math.hypot(tx - bx, ty - by)
    sx, sy = bx + (tx - bx) / d * r, by + (ty - by) / d * r
    line(sx, sy, tx, ty, 0.25, color)
    arrow(tx, ty, tx - sx, ty - sy, color)
    for i, s in enumerate(lines_):
        text(bx + r + 2.0, by - 1.2 - i * (h + 1.6), s, h, 0, "L", color)


def note_leader(target, elbow, s, color=BLACK, h=2.8, left=False):
    tx, ty = target
    ex, ey = elbow
    w = tw(s, h)
    line(tx, ty, ex, ey, color=color)
    if left:
        line(ex - w - 2, ey, ex, ey, color=color)
        text(ex - w - 1, ey + 0.8, s, h, 0, "L", color)
    else:
        line(ex, ey, ex + w + 2, ey, color=color)
        text(ex + 1, ey + 0.8, s, h, 0, "L", color)
    arrow(tx, ty, tx - ex, ty - ey, color)


def frame():
    polyline([(10, 10), (287, 10), (287, 200), (10, 200)], 0.7, closed=True)


def wrap(s, width, h):
    """幅 width (mm) に収まるように 1 文字ずつ折り返す。"""
    out, cur = [], ""
    for ch in s:
        if tw(cur + ch, h) > width and cur:
            out.append(cur)
            cur = ch.lstrip() if ch == " " else ch
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out or [""]


def legend(y_top=186):
    line(196, y_top, 210, y_top, 0.7, RED)
    text(212, y_top - 1, "加工する部分", 3.0, color=RED)
    line(196, y_top - 7, 210, y_top - 7, 0.25, GRAY, PHANTOM)
    text(212, y_top - 8, "加工前の外形（元品が基準寸法の場合）", 3.0, color=GRAY)


# ================================================================ 1枚目: 全体の加工指示図 (10:1)
def page_main():
    prims.clear()
    SC, CX, Y0 = 10.0, 100.0, 75.0

    def P(r, y):
        return CX + SC * r, Y0 + SC * y

    right = right_profile(0.0, H_LOW)
    left = [(-r, y) for r, y in reversed(right)]
    hatch([P(r, y) for r, y in socket_pts() + right + left], 1.6)

    g = groove_arc(H_LOW)
    for sgn in (1, -1):
        def Q(r, y):
            return P(sgn * r, y)
        polyline([Q(SOCK_HALF, T), Q(R_THR - CH_TOP, T), Q(R_THR, T - CH_TOP), Q(R_THR, H_LOW + STEP)], 0.5)
        # 加工する部分 (赤): 段の面取り、溝、φ6.8 の上部、下端の面取り
        polyline([Q(R_THR, H_LOW + STEP)] + [Q(r, y) for r, y in g], 0.7, RED)
        line(*Q(R_COL, g[-1][1]), *Q(R_COL, A_GROOVE - 0.25), 0.7, RED)
        line(*Q(R_COL, A_GROOVE - 0.25), *Q(R_COL, CH_BOT), 0.5)
        line(*Q(R_COL, CH_BOT), *Q(R_BOT, 0), 0.7, RED)
        # ねじ谷径 (細線)
        line(*Q(R_THR_MINOR, H_LOW + STEP - (R_THR - R_THR_MINOR)),
             *Q(R_THR_MINOR, T - (R_THR_MINOR - (R_THR - CH_TOP))), 0.25)
        # 加工前の外形 (二点鎖線)
        polyline([Q(R_COL, A_GROOVE), Q(R_THR, A_GROOVE + STEP), Q(R_THR, H_LOW + STEP)], 0.25, GRAY, PHANTOM)
        polyline([Q(R_COL, CH_BOT), Q(R_COL, A_BOT + CH_BOT), Q(R_BOT, A_BOT)], 0.25, GRAY, PHANTOM)
    line(*P(-R_BOT, 0), *P(R_BOT, 0), 0.7, RED)
    line(*P(-R_BOT, A_BOT), *P(R_BOT, A_BOT), 0.25, GRAY, PHANTOM)
    polyline([P(r, y) for r, y in socket_pts()], 0.5)
    line(*P(0, -0.6), *P(0, T + 1.0), 0.25, BLACK, CHAIN)

    # ---------------- 寸法
    vdim(Y0, Y0 + SC * T, 30.0, P(-R_BOT, 0)[0], P(-(R_THR - CH_TOP), T)[0], "5.75±0.25", RED)
    vdim(Y0, Y0 + SC * H_LOW, 44.0, P(-R_BOT, 0)[0], P(-R_COL, H_LOW)[0], "2.1±0.1", RED)
    x1, yt = P(-R_THR, T - CH_TOP)
    x2, _ = P(R_THR, T - CH_TOP)
    hdim(x1, x2, 147.0, yt, yt, "M8×0.75-6g")
    # データム A (M8 ねじ部)
    line(x1 - 12, 147.0, x1 - 2.6, 147.0)
    solid([(x1, 145.6), (x1, 148.4), (x1 - 2.6, 147.0)])
    polyline([(x1 - 18, 144), (x1 - 12, 144), (x1 - 12, 150), (x1 - 18, 150)], 0.35, closed=True)
    text(x1 - 15, 145.6, "A", 3.0, 0, "C")
    text(x1 - 19, 152.5, "データム A", 2.5, 0, "L")

    xb1, yb = P(-R_BOT, A_BOT)
    xb2, _ = P(R_BOT, A_BOT)
    hdim(xb1, xb2, 63.0, yb, yb, "φ5.8±0.2 [3]", RED)
    xc1, yc = P(-R_COL, CH_BOT)
    xc2, _ = P(R_COL, CH_BOT)
    hdim(xc1, xc2, 54.0, yc, yc, "φ6.8±0.1 [3]", ext_right=6.0)
    # 同軸度の枠 (φ6.8 の寸法線につなぐ)
    fx, fy, fh = xc2 + 6.0, 54.0 - 3.0, 6.0
    cells = [("◎", 7), ("φ0.2(M)", 17), ("A(M)", 11)]
    x = fx
    for s, w in cells:
        polyline([(x, fy), (x + w, fy), (x + w, fy + fh), (x, fy + fh)], 0.35, closed=True)
        text(x + w / 2, fy + 1.6, s, 2.8, 0, "C")
        x += w
    text(x + 2, fy + 1.6, "MP1 [3]", 2.8)
    text(fx, fy - 4.5, "同軸度 φ0.2（最大実体）、データム A、測定原理 1、要求クラス 3", 2.4)

    note_leader(P(R_THR - CH_TOP / 2, T - CH_TOP / 2), (150, 141), "0.75×45° の面取り（変更なし）")
    note_leader(P(0.9, SOCK_Y + 0.12), (150, 131), "M4 六角穴・穴深さ 最大4・穴底 R1 MAX（変更なし）")

    # ---------------- 加工箇所
    balloon_note(200, 116, 4, P(R_COL + STEP / 2 + 0.05, H_LOW + STEP / 2 - 0.05),
                 ["段の面取り 45°（+5°/0）と", "溝 R0.4±0.2 を付け直す"])
    balloon_note(200, 98, 3, P(R_COL, (A_GROOVE + H_LOW) / 2 - 0.05),
                 ["M8 外径の下側を φ6.8±0.1 まで削り、", "段を上へ 0.15 移す（溝位置から 2.1±0.1）"])
    balloon_note(200, 80, 2, P(R_COL - CH_BOT / 2, CH_BOT / 2),
                 ["下端の面取りを付け直す", "45°（+5°/0）、端面 φ5.8±0.2"])
    balloon_note(200, 64, 1, P(1.8, 0), ["下端面を 0.25 削る", "全長 6.0 → 5.75±0.25"])

    text(15, 192, "PLUG M8×0.75　追加工指示図（1ページ目の品物 → 2ページ目の品物）", 5.0)
    text(15, 184, "断面図（2ページ目の A-A と同じ向き）　尺度 10:1　［ ］内の数字は要求クラス", 3.0)
    legend()

    notes = [
        "注記",
        "1. 加工は赤線の部分だけ。上端面、上端の面取り、ねじ、六角穴は変更しない。",
        "2. 加工順：① → ② → ③ → ④。拡大図と削る量の決め方は 2枚目。",
        "3. 二点鎖線は元品が基準寸法（全長 6.0、溝位置から下端 2.2）の場合の外形。",
        "4. 寸法の比較と英語注記の和訳は 3枚目以降。",
    ]
    y = 34.0
    for i, s in enumerate(notes):
        text(15, y, s, 3.0 if i == 0 else 2.6)
        y -= 4.6

    x0, x1_, y0, rh = 177.0, 287.0, 10.0, 6.0
    rows = [("品名", "PLUG M8×0.75　追加工（下端側）"),
            ("元品", "図番 1546996　P54（添付 1ページ目）"),
            ("完成品", "図番 21341250　01（添付 2ページ目）"),
            ("材質", "11SMnPb30+C（変更なし）"),
            ("尺度", "10 : 1　　単位 mm　　作成日 2026/10/14")]
    n = len(rows)
    polyline([(x0, y0), (x0, y0 + rh * n), (x1_, y0 + rh * n)], 0.35)
    for i in range(1, n):
        line(x0, y0 + rh * i, x1_, y0 + rh * i, 0.35)
    line(x0 + 15, y0, x0 + 15, y0 + rh * n, 0.35)
    for i, (k, v) in enumerate(rows):
        yy = y0 + rh * (n - 1 - i) + 1.8
        text(x0 + 2, yy, k, 2.6)
        text(x0 + 17, yy, v, 2.6)
    frame()
    return list(prims)


# ================================================================ 2枚目: 拡大図 (20:1) と削る量
def page_detail():
    prims.clear()
    SC, CX, Y0 = 20.0, 40.0, 97.0
    Y_TOP = 3.3          # 拡大範囲の上端 (破断線)

    def P(r, y):
        return CX + SC * r, Y0 + SC * y

    # 右半分の断面 (上は破断)
    g = groove_arc(H_LOW)
    body = ([(SOCK_HALF, Y_TOP), (R_THR, Y_TOP), (R_THR, H_LOW + STEP)] + g
            + [(R_COL, CH_BOT), (R_BOT, 0.0), (0.0, 0.0), (0.0, SOCK_Y)]
            + arc_pts(SOCK_HALF - SOCK_R, SOCK_Y + SOCK_R, SOCK_R, 270, 360, 6)
            + [(SOCK_HALF, Y_TOP)])
    hatch([P(r, y) for r, y in body], 2.2)
    polyline([P(R_THR, Y_TOP), P(R_THR, H_LOW + STEP)], 0.5)
    polyline([P(R_THR, H_LOW + STEP)] + [P(r, y) for r, y in g], 0.7, RED)
    line(*P(R_COL, g[-1][1]), *P(R_COL, A_GROOVE - 0.25), 0.7, RED)
    line(*P(R_COL, A_GROOVE - 0.25), *P(R_COL, CH_BOT), 0.5)
    line(*P(R_COL, CH_BOT), *P(R_BOT, 0), 0.7, RED)
    line(*P(R_BOT, 0), *P(0, 0), 0.7, RED)
    polyline([P(0, SOCK_Y)] + [P(r, y) for r, y in arc_pts(SOCK_HALF - SOCK_R, SOCK_Y + SOCK_R, SOCK_R, 270, 360, 6)]
             + [P(SOCK_HALF, Y_TOP)], 0.5)
    line(*P(R_THR_MINOR, H_LOW + STEP - (R_THR - R_THR_MINOR)), *P(R_THR_MINOR, Y_TOP), 0.25)
    # 破断線 (波線)
    pts = []
    for i in range(41):
        r = SOCK_HALF + (R_THR + 0.15 - SOCK_HALF) * i / 40
        pts.append(P(r, Y_TOP + 0.05 * math.sin(i / 40 * 2 * math.pi * 2)))
    polyline(pts, 0.25)
    line(*P(0, -0.6), *P(0, Y_TOP + 0.3), 0.25, BLACK, CHAIN)

    # 加工前の外形 (二点鎖線)
    polyline([P(R_COL, A_GROOVE), P(R_THR, A_GROOVE + STEP), P(R_THR, H_LOW + STEP)], 0.25, GRAY, PHANTOM)
    polyline([P(R_COL, CH_BOT), P(R_COL, A_BOT + CH_BOT), P(R_BOT, A_BOT), P(0, A_BOT)], 0.25, GRAY, PHANTOM)

    # ---------------- 寸法 (右側)
    XA, XB, XC = 183.0, 200.0, 216.0
    xo_bot = P(R_BOT, 0)[0]
    xo_abot = P(R_BOT, A_BOT)[0]
    xo_col = P(R_COL, 0)[0]
    y_bot, y_abot = P(0, 0)[1], P(0, A_BOT)[1]
    y_grv, y_agrv = P(0, H_LOW)[1], P(0, A_GROOVE)[1]
    ext_h(y_abot, xo_abot, XC, GRAY)
    ext_h(y_bot, xo_bot, XB, RED)
    ext_h(y_agrv, xo_col, XC, GRAY)
    ext_h(y_grv, xo_col, XB, RED)
    vdim_line(y_abot, y_bot, XA, "0.25", RED, 3.0, small=True, text_side=y_abot + 0.8)
    vdim_line(y_agrv, y_grv, XA, "0.15", RED, 3.0, small=True, text_side=y_grv + 3.2)
    vdim_line(y_bot, y_grv, XB, "2.1±0.1", RED)
    vdim_line(y_abot, y_agrv, XC, "（元品 2.2）", GRAY)

    # ---------------- 加工箇所の説明
    note_leader(P(R_COL + 0.3, H_LOW + 0.3), (132, 178), "④ 段の面取り 45°（+5°/0）[3] を付け直す", RED)
    note_leader(P(R_COL + 0.04, H_LOW - 0.06), (132, 168), "④ 溝 R0.4±0.2 を付け直す", RED)
    note_leader(P(R_COL, A_GROOVE + 0.03), (128, 124),
                "③ φ6.8±0.1 まで削る（段を 0.15 上へ）", RED)
    note_leader(P(R_COL - CH_BOT / 2, CH_BOT / 2), (128, 108),
                "② 面取り 45°（+5°/0）、端面 φ5.8±0.2", RED)
    note_leader(P(1.2, 0), (60, 86), "① 下端面を 0.25 削る", RED)

    text(15, 192, "拡大図（右半分、上側は省略）　尺度 20:1", 5.0)
    legend(66)

    # ---------------- 加工手順と削る量
    steps = [
        "加工手順",
        "1. 元品の全長と、溝位置から下端面までの長さを測る。",
        "2. ① 下端面を 0.25 削る（全長 6.0 → 5.75）。",
        "3. ② 下端の面取り 45°（+5°/0）を付け直し、端面を φ5.8±0.2 にする。",
        "4. ③ M8 外径の下側を φ6.8±0.1 まで削り、溝位置を下端面から 2.1±0.1 にする。",
        "5. ④ 段の面取り 45°（+5°/0）と溝 R0.4±0.2 を付け直し、ねじ端のバリを取る。",
        "6. 全長 5.75±0.25、溝位置から下端 2.1±0.1、φ6.8±0.1、φ5.8±0.2 を測って確認する。",
    ]
    y = 79.0
    for i, s in enumerate(steps):
        text(15, y, s, 3.2 if i == 0 else 2.6)
        y -= 4.6
    text(15, y - 1.5, "③で削る長さ ＝ 2.1 －（元品の溝位置から下端の実測値 － 0.25）　0 以下なら③は不要", 2.6, color=RED)

    rows = [("元品の全長", "元品の溝から下端", "③で削る長さ", "加工後の全長", "加工後の溝から下端", "判定"),
            ("6.0", "2.2", "0.15", "5.75", "2.1", "可"),
            ("6.0", "2.3", "0.05", "5.75", "2.1", "可"),
            ("6.0", "2.4", "0（不要）", "5.75", "2.15", "可"),
            ("6.25", "2.2", "0.15", "6.0", "2.1", "可（全長が上限）"),
            ("6.5", "2.2", "0.15", "6.25", "2.1", "不可（全長が 6.0 を超える）")]
    simple_table(15, 41, [27, 32, 27, 27, 35, 50], rows, rh=4.2, h=2.4,
                 row_colors={5: RED})
    text(220, 41.5, "全長が 6.25 を超える元品は、", 2.5)
    text(220, 37.5, "0.25 では全長が公差に入らない。", 2.5)
    text(220, 33.5, "下端の削り量を（全長 － 5.75）に増やし、", 2.5)
    text(220, 29.5, "③で削る長さもそのぶん増やす。", 2.5)
    frame()
    return list(prims)


def simple_table(x0, y_top, widths, rows, rh=5.0, h=2.6, row_colors=None):
    xs = [x0]
    for w in widths:
        xs.append(xs[-1] + w)
    n = len(rows)
    for i in range(n + 1):
        line(xs[0], y_top - rh * i, xs[-1], y_top - rh * i, 0.5 if i in (0, 1, n) else 0.25)
    for x in xs:
        line(x, y_top, x, y_top - rh * n, 0.5 if x in (xs[0], xs[-1]) else 0.25)
    for i, row in enumerate(rows):
        col = (row_colors or {}).get(i, BLACK)
        for j, cell in enumerate(row):
            text(xs[j] + 1.5, y_top - rh * i - rh / 2 - h / 2 + 0.25, cell, h, 0, "L", col)
    return y_top - rh * n


# ================================================================ 3枚目以降: 寸法比較と英語注記の和訳
class Flow:
    """表を上から順に流し込み、下まで来たら次のページへ送る。"""

    def __init__(self):
        self.pages = []
        self.new_page()

    def new_page(self):
        if self.pages or prims:
            pass
        prims.clear()
        self.cur = []
        self.pages.append(self.cur)
        self.y = 194.0

    def flush(self):
        self.cur[:] = list(prims)

    def heading(self, s, h=4.0, gap=4.0):
        if self.y - h - gap < 25:
            self.flush()
            self.new_page()
        text(15, self.y - h, s, h)
        self.y -= h + gap

    def table(self, widths, header, rows, h=2.4, pad=0.9, colors=None):
        x0 = 15.0
        xs = [x0]
        for w in widths:
            xs.append(xs[-1] + w)

        def draw_row(cells, color=BLACK, bold=False):
            wrapped = [wrap(c, widths[j] - 3.0, h) for j, c in enumerate(cells)]
            nl = max(len(wl) for wl in wrapped)
            rh = nl * (h + 1.1) + pad * 2 - 1.1
            if self.y - rh < 12:
                self.flush()
                self.new_page()
                draw_row(header, BLACK, True)
            top = self.y
            line(xs[0], top - rh, xs[-1], top - rh, 0.5 if bold else 0.25)
            if bold:
                line(xs[0], top, xs[-1], top, 0.5)
            for x in xs:
                line(x, top, x, top - rh, 0.5 if x in (xs[0], xs[-1]) else 0.25)
            for j, wl in enumerate(wrapped):
                for k, s in enumerate(wl):
                    text(xs[j] + 1.5, top - pad - h - k * (h + 1.1) + 0.2, s, h, 0, "L", color)
            self.y = top - rh

        draw_row(header, BLACK, True)
        for i, r in enumerate(rows):
            draw_row(r, (colors or {}).get(i, BLACK))
        self.y -= 6

    def finish(self):
        self.flush()
        return self.pages


COMPARE = [
    ("全長", "6 +0.5/0（6.0～6.5）", "5.75±0.25（5.5～6.0）", "① 下端面を 0.25 削る"),
    ("溝位置から下端面まで", "2.2 +0.2/0（2.2～2.4）", "2.1±0.1（2.0～2.2）", "③ 段を上へ移す"),
    ("下端の面取り", "45° +5°/0、端面 φ5.8±0.2", "同じ", "② ①の後に付け直す"),
    ("段の面取り・溝", "45° +5°/0、R0.4±0.2", "同じ", "④ ③の後に付け直す"),
    ("ねじ", "M8×0.75-6g", "同じ", "なし（ねじ長さは 0.15 短くなる）"),
    ("段部の径", "φ6.8±0.1", "同じ", "③で上側に延びる"),
    ("上端の面取り", "0.75×45°", "同じ", "なし"),
    ("六角穴・穴深さ・穴底", "M4・4 MAX・R 1 MAX", "M4・4 MAX・R1 MAX", "なし（上端は削らない）"),
    ("同軸度", "◎φ0.2(M) A(M) I [3]", "◎φ0.2(M) A(M) MP1 [3]", "なし"),
    ("材質", "11SMnPb30+C", "同じ", "なし"),
    ("表面粗さ（指示なし面）", "Ra12.5", "Ra12.5", "―"),
    ("角部", "バリなし（STD 5080,341）", "エッジ記号 -0.5", "加工後にバリ取り"),
]

EN_B = [  # 添付 2ページ目 (完成品 21341250 01)
    ("A-A", "A-A 断面（下の図の A-A の線で切った断面図）"),
    ("M8x0,75-6g", "メートル細目ねじ。呼び径 8、ピッチ 0.75、おねじの公差域クラス 6g。小数点はカンマで書かれている"),
    ("[A]（三角記号付きの枠）", "データム A。M8 ねじ部を基準にする"),
    ("0,75x45°", "0.75×45° の面取り"),
    ("4 MAX DRILL DEPTH", "穴深さ 最大 4"),
    ("R1 MAX", "穴底の丸み 最大 R1"),
    ("R0,4±0,2", "丸み R0.4±0.2（段の入隅の溝）"),
    ("2x 45° +5°/0 [3]", "45°（+5°/0）が 2 か所。[3] は要求クラス 3（下の [3] の行）"),
    ("Ø5,8±0,2 [3]　Ø6,8±0,1 [3]", "直径 5.8±0.2、直径 6.8±0.1。どちらも要求クラス 3"),
    ("◎ Ø0,2(M) A(M) MP1 [3]", "同軸度 φ0.2。(M) は最大実体公差方式。データム A にも (M) を適用。MP1 は測定原理 1。要求クラス 3"),
    ("[3]", "要求クラス 3。1ページ目の表題欄に「要求クラスの表示がない特性はクラス 4（STD 5060.4）」とある。クラスごとの中身は STD 5060.4 にあり、未確認"),
    ("M4 HEXAGON SOCKET (SEE DRAWING 1052942)", "M4 用の六角穴（形と寸法は図番 1052942 を参照）"),
    ("Material 11SMnPb30+C", "材質 11SMnPb30+C（鉛入りの快削鋼。+C は冷間引抜き材の記号と判断、未確認）"),
    ("DRAWING SCALE 5:1", "図面の尺度 5:1"),
    ("SURFACE ROUGHNESS UNLESS OTHERWISE STATED √Ra 12,5", "指示のない面の表面粗さは Ra 12.5"),
    ("THREAD TOLERANCES STD 5081,15", "ねじの公差は規格 STD 5081,15 による"),
    ("GEOMETRICAL TOLERANCES STD 4759-1:2000, GRADE A", "幾何公差は STD 4759-1:2000 の等級 A による（ISO 4759-1:2000 は締結部品の公差と部品等級 A・B・C を決めた規格。同じ内容かは未確認）"),
    ("エッジ記号 -0.5 と（ ）内の記号", "指示のない外側の角は 0～0.5 の範囲で取る（面取りか丸み）。（ ）内の記号は、ほかの角すべてに適用する意味と判断。ISO 13715 の記号と判断、未確認"),
    ("SYMBOLS, DESIGNATIONS AND GENERAL DRAWING METHODS STD 101-0005 AND STD 5023,503", "記号、呼び方、一般的な図示方法は STD 101-0005 と STD 5023,503 による"),
    ("10006039/1061676K", "管理番号（意味は未確認）"),
    ("2:1（左上の枠）", "左上の立体図の尺度 2:1"),
    ("Engineering Release Notice (ERN) / Location / Change description A=Added W=Was D=Deleted",
     "技術変更通知 / 位置 / 変更内容（A=追加、W=変更前、D=削除）"),
    ("P/A: 1.1.main　D: 1.3.main", "意味は未確認"),
    ("Document release status RELEASED / Date / Modification count", "文書の状態：発行済み / 日付 / 変更回数"),
    ("The copying, distribution and utilization of this document as well as the communication of its contents to others without expressed authorization is prohibited. Offenders will be held liable for the payment of damages. All rights reserved in the event of the grant of a patent, utility model or ornamental design registration.",
     "明示の許可なく、本書を複製、配布、利用し、内容を第三者に伝えることを禁止する。違反者は損害賠償の責任を負う。特許、実用新案、意匠登録に関する権利はすべて留保する"),
    ("Document title PLUG VCB M8X0,75", "文書名 プラグ M8×0.75（VCB の意味は未確認）"),
    ("Document type / Owner domain:Document prefix", "文書の種類 / 所有部門：文書の接頭記号"),
    ("Volvo Powertrain Corporation", "作成会社名"),
    ("Document No 21341250 / Issue index 01 / Sheet No 1(1)", "図番 21341250 / 版 01 / シート 1（全 1 枚）"),
]

EN_A = [  # 添付 1ページ目 (元品 1546996 P54)
    ("M8x0,75-6g / 0,75x45° / 4MAX DRILL DEPTH / R 0,4±0,2 / Ø5,8±0,2 [3] / Ø6,8±0,1 [3] / 2x 45° +5°/-0° [3]",
     "2ページ目と同じ（3枚目の和訳を参照）"),
    ("6 +0,5/0", "全長 6（+0.5/0）"),
    ("2,2 +0,2/0", "溝位置から下端面まで 2.2（+0.2/0）"),
    ("R 1MAX（図中は R MAX と重なって見える）", "穴底の丸み 最大 R1（変更履歴 D6 で追加）"),
    ("◎ Ø0,2(M) A(M) I [3]", "同軸度 φ0.2(M)、データム A(M)、I は測定原理 I、要求クラス 3"),
    ("M4 HEXAGON SOCKET STD 7124,5 *)", "M4 用の六角穴（規格 STD 7124,5）"),
    ("（手書き）3 +0,08/+0,02 djup = min 2 *)", "二面幅 3（+0.08/+0.02）、深さ 最小 2。djup はスウェーデン語で「深さ」。手書きのため読み取りに自信なし"),
    ("（手書き）Alt STD1052942", "代わりに STD 1052942 でもよい、という意味と判断（未確認）"),
    ("（手書き）6.0～6.5、2.2～2.4", "公差を範囲で書いたメモ"),
    ("√ 12,5 IF UNSPECIFIED", "指示のない面の表面粗さ 12.5（Ra）"),
    ("THREAD TOLERANCES STD 5081,15", "ねじの公差は規格 STD 5081,15 による"),
    ("FREE FROM BURRS STD 5080,341 INCLUDING DOCUMENTS", "バリがないこと（STD 5080,341 とその関連文書による）"),
    ("10005778/1060516", "管理番号（意味は未確認）"),
    ("ISSUE / MICRO-COPIED / DESIGN CHANGE NOTICE / DATE / No / PLAC. / DRAWN / CHECK.",
     "版 / マイクロフィルム複写 / 設計変更通知 / 日付 / 番号 / 図面上の位置 / 作成 / 検図"),
    ("DESIGN CHANGE T=ADDED U=DELETED V=WAS", "設計変更の内容（T=追加、U=削除、V=変更前）"),
    ("V B51（C52）", "B51 から変更（内容は未確認）"),
    ("Ra=12,5 IF UNSPECIFIED T（P53, D4）", "指示のない面の粗さ Ra12.5 を追加"),
    ("MEASURING PRINCIPLE I V II（P53, B5）", "測定原理を I に変更（変更前は II）"),
    ("2,2 +0,2/0 V 2 +0,2/0（P53, C7）", "2.2 +0.2/0 に変更（変更前は 2 +0.2/0）"),
    ("R 1MAX T（P54, D6）", "穴底 R1 MAX を追加"),
    ("4MAX V 3MAX（P54, D5）", "穴深さを 4MAX に変更（変更前は 3MAX）"),
    ("CAD RELEASED", "CAD データとして発行済み"),
    ("DWG NO / ISSUE / CADDS PARTNAME / CADDS DRAWNAME / BASE", "図番 / 版 / CAD（CADDS）上の部品名 / 図面名 / ベース"),
    ("ASSY No / PART No / ISSUE", "組立品の番号 / 部品番号 / 版"),
    ("APPLIES TO PROPERTIES NOT MARKED WITH REQUIREMENT CLASS [4] STD 5060.4", "要求クラスの表示がない特性は要求クラス 4 とする（STD 5060.4）"),
    ("ISO TOLERANCE SYSTEM STD 5061,101", "ISO 公差方式 STD 5061,101"),
    ("TOLERANCE REQUIREMENTS STD 5060,011", "公差の要求事項 STD 5060,011"),
    ("SURFACE ROUGHNESS Ra μm STD 5068,04", "表面粗さ Ra（単位 μm）STD 5068,04"),
    ("MAX MATERIAL PRINCIPLE (M) STD 5063,1", "最大実体公差方式 (M) STD 5063,1"),
    ("GEOMETRICAL TOLERANCES STD 5062,2", "幾何公差 STD 5062,2"),
    ("TECHNICAL REGULATION", "法規・技術規制の対象を示す欄（空欄）"),
    ("SCALE 5:1", "尺度 5:1"),
    ("MATERIAL / DESIGNATION STEEL 1912-04 ** / **11SMnPb30+C", "材料 / 呼び：鋼 1912-04（** の注で 11SMnPb30+C）"),
    ("DOCUMENT STD 1119,12", "材料の規格 STD 1119,12"),
    ("BASIC DIMENSION / REF.", "素材寸法 / 参照（どちらも空欄）"),
    ("NOTICE: THIS DOCUMENT CONTAINS PROPRIETARY INFORMATION AND SHALL NOT BE USED OR REPRODUCED OR ITS CONTENTS DISCLOSED IN WHOLE OR IN PART WITHOUT THE PRIOR WRITTEN CONSENT OF Volvo Truck Corporation or Volvo GM Heavy Truck Corporation",
     "注意：本書は社外秘の情報を含む。Volvo Truck Corporation または Volvo GM Heavy Truck Corporation の書面による事前の同意なく、全部または一部を使用、複製、開示してはならない"),
    ("EUROPEAN PROJECTION METHOD FIRST ANGLE PROJECTION / AMERICAN PROJECTION METHOD THIRD ANGLE PROJECTION",
     "欧州式＝第一角法 / 米国式＝第三角法。第三角法の欄は斜線で消してあり、この図面は第一角法と読める"),
    ("NAME PLUG VEB", "名称 プラグ（VEB の意味は未確認）"),
    ("Volvo Truck Corporation", "作成会社名"),
    ("DEPT / TYPE / GROUP / MASTER No", "部署 / タイプ / グループ / マスター番号"),
    ("SIGN / DATE / DRAWN / APPR. / CHECKED / APPR. PROD.", "署名 / 日付 / 作成 / 承認 / 検図 / 生産承認"),
    ("DRAWING No 1546996 / SHEET / ISSUE P54", "図番 1546996 / シート / 版 P54"),
    ("PPF (1:1)（左上の枠）", "左上の立体図。PPF の意味は未確認、(1:1) は尺度"),
    ("03 FORM", "図面用紙の様式番号"),
]


def pages_tables():
    f = Flow()
    f.heading("寸法の比較（赤字が加工で変わる寸法）")
    f.table([48, 62, 62, 95], ("項目", "1ページ目（元品）1546996 P54", "2ページ目（完成品）21341250 01", "加工"),
            COMPARE, colors={0: RED, 1: RED, 2: RED, 3: RED})
    f.heading("英語注記の和訳：添付 2ページ目（完成品 21341250 01）")
    f.table([105, 162], ("原文", "和訳"), EN_B)
    f.heading("英語注記の和訳：添付 1ページ目（元品 1546996 P54）")
    f.table([105, 162], ("原文", "和訳"), EN_A)
    return f.finish()


# ================================================================ PDF 出力
def draw(c, plist):
    for kind, data, w, color, dash in plist:
        c.setStrokeColorRGB(*color)
        c.setFillColorRGB(*color)
        if kind == "text":
            x, y, s, h, rot, align = data
            fs = h * FS
            wd = pdfmetrics.stringWidth(s, FONT, fs)
            dx = {"L": 0, "C": -wd / 2, "R": -wd}[align]
            c.saveState()
            c.translate(x, y)
            c.rotate(rot)
            c.setFont(FONT, fs)
            c.drawString(dx, 0, s)
            c.restoreState()
        elif kind == "solid":
            p = c.beginPath()
            p.moveTo(*data[0])
            for q in data[1:]:
                p.lineTo(*q)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
        elif kind == "hatch":
            pts, pitch = data
            c.saveState()
            p = c.beginPath()
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
            c.clipPath(p, stroke=0, fill=0)
            c.setLineWidth(w)
            c.setDash([])
            xs = [q[0] for q in pts]
            ys = [q[1] for q in pts]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            k = x0 - (y1 - y0)
            while k < x1:
                c.line(k, y0, k + (y1 - y0), y1)
                k += pitch
            c.restoreState()
        else:
            c.setLineWidth(w)
            c.setDash(dash if dash else [])
            if kind == "line":
                c.line(*data)
            elif kind == "circle":
                c.circle(*data, stroke=1, fill=0)


def main(out):
    pages = [page_main(), page_detail()]
    for pl in pages_tables():
        prims.clear()
        prims.extend(pl)
        frame()
        pages.append(list(prims))
    n = len(pages)
    c = canvas.Canvas(f"{out}/PLUG_M8x0.75_rework_v2.pdf", pagesize=landscape(A4))
    c.setTitle("PLUG M8x0.75 追加工指示図（下端側の加工）")
    for i, pl in enumerate(pages):
        prims.clear()
        text(285, 202, f"{i + 1} / {n}", 2.6, 0, "R")
        c.saveState()
        c.scale(mm, mm)
        c.setLineCap(0)
        c.setLineJoin(1)
        draw(c, pl + list(prims))
        c.restoreState()
        c.showPage()
    c.save()
    print(f"ok {n} pages")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
