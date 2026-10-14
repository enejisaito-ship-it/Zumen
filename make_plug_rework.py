# -*- coding: utf-8 -*-
"""PLUG M8x0.75 追加工指示図 (図番 1546996 P54 の品物を 図番 21341250 01 の形にする) を PDF で出力する。

座標は用紙上の mm (A4 横 297x210)。部品は尺度 10:1 で描く。
部品の座標は (r, y) = (中心からの半径方向, 下端面からの高さ) の実寸 mm。
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

# ---------------------------------------------------------------- 完成品 (2ページ目) の寸法
T = 5.75            # 全長
H_LOW = 2.1         # 溝位置から下端面まで
R_THR = 4.0         # M8 外径/2
R_THR_MINOR = (8 - 1.082532 * 0.75) / 2   # M8x0.75 谷の径/2 (基準寸法)
CH_TOP = 0.75       # 上端の面取り 0.75x45°
R_COL = 3.4         # φ6.8/2
R_BOT = 2.9         # φ5.8/2
CH_BOT = R_COL - R_BOT   # 下端の45°面取りの長さ (0.5)
R_GROOVE = 0.4
SOCK_HALF = 1.5     # M4 六角穴 二面幅3/2
SOCK_DEPTH = 3.8    # 作図上の穴深さ (指示は 4 MAX)
SOCK_R = 1.0        # 穴底 R1 MAX
Y_CH_LOW = H_LOW + (R_THR - R_COL)  # ねじ部下側の45°面取りが外径に達する高さ

# 元品 (1ページ目) を基準寸法 (全長6.0、下部2.2) とした場合の端面位置
A_TOTAL, A_LOW = 6.0, 2.2
CUT_BOT = A_LOW - H_LOW                 # 0.10
CUT_TOP = A_TOTAL - CUT_BOT - T         # 0.15
Y_A_BOT = -CUT_BOT
Y_A_TOP = T + CUT_TOP

SC = 10.0           # 尺度 10:1
CX, Y0 = 100.0, 70.0


def P(r, y):
    return CX + SC * r, Y0 + SC * y


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


def hdim(x1, x2, y, f1, f2, label, color=BLACK, h=3.0):
    for x, f in ((x1, f1), (x2, f2)):
        s = 1 if y > f else -1
        line(x, f + s * 1.0, x, y + s * 2.0, color=color)
    line(x1, y, x2, y, color=color)
    arrow(x1, y, -1, 0, color)
    arrow(x2, y, 1, 0, color)
    text((x1 + x2) / 2, y + 1.0, label, h, 0, "C", color)


def vdim(y1, y2, x, f1, f2, label, color=BLACK, h=3.0):
    for yy, f in ((y1, f1), (y2, f2)):
        s = 1 if x > f else -1
        line(f + s * 1.0, yy, x + s * 2.0, yy, color=color)
    line(x, y1, x, y2, color=color)
    arrow(x, y1, 0, -1, color)
    arrow(x, y2, 0, 1, color)
    text(x - 1.0, (y1 + y2) / 2, label, h, 90, "C", color)


def balloon_note(bx, by, num, target, lines_, color=RED):
    """番号の丸 (bx, by) から target へ矢印付き引出線。丸の右に説明文。"""
    r = 3.2
    circle(bx, by, r, 0.35, color)
    text(bx, by - 1.3, str(num), 2.8, 0, "C", color)
    tx, ty = target
    d = math.hypot(tx - bx, ty - by)
    sx, sy = bx + (tx - bx) / d * r, by + (ty - by) / d * r
    line(sx, sy, tx, ty, 0.25, color)
    arrow(tx, ty, tx - sx, ty - sy, color)
    for i, s in enumerate(lines_):
        text(bx + r + 2.0, by - 1.2 - i * 4.6, s, 3.0, 0, "L", color)


def note_leader(target, elbow, s, color=BLACK, h=2.8):
    tx, ty = target
    ex, ey = elbow
    w = tw(s, h)
    line(tx, ty, ex, ey, color=color)
    line(ex, ey, ex + w + 2, ey, color=color)
    arrow(tx, ty, tx - ex, ty - ey, color)
    text(ex + 1, ey + 0.8, s, h, 0, "L", color)


def arc_pts(cx, cy, r, a1, a2, n=12):
    return [(cx + r * math.cos(math.radians(a1 + (a2 - a1) * i / n)),
             cy + r * math.sin(math.radians(a1 + (a2 - a1) * i / n))) for i in range(n + 1)]


# ================================================================ 1ページ目: 加工指示図
def page1():
    prims.clear()
    # 溝 R0.4 (ねじ部下側の45°面取りと φ6.8 の入隅)
    gcx = R_COL + R_GROOVE
    gcy = H_LOW - R_GROOVE * math.tan(math.radians(22.5))
    groove_r = arc_pts(gcx, gcy, R_GROOVE, 135, 180, 6)          # 上から下へ
    sock_y = T - SOCK_DEPTH

    # 右半分の外形 (上端面の穴縁から下端中心まで、上から順)
    right = ([(SOCK_HALF, T), (R_THR - CH_TOP, T), (R_THR, T - CH_TOP), (R_THR, Y_CH_LOW)]
             + groove_r + [(R_COL, CH_BOT), (R_BOT, 0.0)])
    left = [(-r, y) for r, y in reversed(right)]
    # 穴 (左壁を下へ -> 穴底 -> 右壁を上へ)
    sock = ([(-SOCK_HALF, T)] + arc_pts(-SOCK_HALF + SOCK_R, sock_y + SOCK_R, SOCK_R, 180, 270, 6)
            + arc_pts(SOCK_HALF - SOCK_R, sock_y + SOCK_R, SOCK_R, 270, 360, 6) + [(SOCK_HALF, T)])
    section = sock + right + left
    sec_pts = [P(r, y) for r, y in section]
    hatch(sec_pts, 1.6)

    # 外形線 (加工する面は赤)
    TH = 0.5
    for sgn in (1, -1):
        def Q(r, y):
            return P(sgn * r, y)
        line(*Q(SOCK_HALF, T), *Q(R_THR - CH_TOP, T), 0.7, RED)               # (1) 上端面
        line(*Q(R_THR - CH_TOP, T), *Q(R_THR, T - CH_TOP), 0.7, RED)          # (2) 上端の面取り
        line(*Q(R_THR, T - CH_TOP), *Q(R_THR, Y_CH_LOW), TH)                  # ねじ外径
        line(*Q(R_THR, Y_CH_LOW), *Q(*groove_r[0]), TH)                       # ねじ部下側の面取り
        polyline([Q(r, y) for r, y in groove_r], TH)                         # 溝 R0.4
        line(*Q(R_COL, groove_r[-1][1]), *Q(R_COL, CH_BOT), TH)               # φ6.8
        line(*Q(R_COL, CH_BOT), *Q(R_BOT, 0), 0.7, RED)                       # (4) 下端の面取り
        line(*Q(R_THR_MINOR, H_LOW + R_THR_MINOR - R_COL), *Q(R_THR_MINOR, T - (R_THR_MINOR - (R_THR - CH_TOP))), 0.25)  # ねじ谷径
    line(*P(-R_BOT, 0), *P(R_BOT, 0), 0.7, RED)                               # (3) 下端面
    polyline([P(r, y) for r, y in sock], TH)                                  # 六角穴
    line(*P(0, -0.5), *P(0, T + 1.2), 0.25, BLACK, [6, 1, 1, 1])              # 中心線

    # 加工前の端面 (二点鎖線)
    PH = [5, 0.8, 0.8, 0.8, 0.8, 0.8]
    for sgn in (1, -1):
        polyline([P(sgn * R_THR, T - CH_TOP), P(sgn * R_THR, Y_A_TOP - CH_TOP),
                  P(sgn * (R_THR - CH_TOP), Y_A_TOP), P(sgn * SOCK_HALF, Y_A_TOP),
                  P(sgn * SOCK_HALF, T)], 0.25, GRAY, PH)
        polyline([P(sgn * R_COL, CH_BOT), P(sgn * R_COL, Y_A_BOT + CH_BOT),
                  P(sgn * R_BOT, Y_A_BOT)], 0.25, GRAY, PH)
    line(*P(-R_BOT, Y_A_BOT), *P(R_BOT, Y_A_BOT), 0.25, GRAY, PH)

    # ---------------- 寸法
    xl_top = P(-(R_THR - CH_TOP), T)[0]
    xl_bot = P(-R_BOT, 0)[0]
    xl_grv = P(-R_COL, H_LOW)[0]
    vdim(Y0, Y0 + SC * T, 35.0, xl_bot, xl_top, "5.75±0.25", RED)
    vdim(Y0, Y0 + SC * H_LOW, 47.0, xl_bot, xl_grv, "2.1±0.1", RED)
    # M8
    xt1, yt = P(-R_THR, T - CH_TOP)
    xt2, _ = P(R_THR, T - CH_TOP)
    hdim(xt1, xt2, 142.0, yt, yt, "M8×0.75-6g")
    # φ5.8 / φ6.8
    xb1, yb = P(-R_BOT, Y_A_BOT)
    xb2, _ = P(R_BOT, Y_A_BOT)
    hdim(xb1, xb2, 58.0, yb, yb, "φ5.8±0.2", RED)
    xc1, yc = P(-R_COL, CH_BOT)
    xc2, _ = P(R_COL, CH_BOT)
    hdim(xc1, xc2, 49.0, yc, yc, "φ6.8±0.1")

    # ---------------- 加工箇所の番号と説明
    balloon_note(160, 150, 1, P(2.4, T), ["上端面を削る", "全長 5.75±0.25 に仕上げる"])
    balloon_note(160, 128, 2, P(R_THR - CH_TOP / 2, T - CH_TOP / 2),
                 ["上端の面取りを付け直す", "0.75×45°"])
    balloon_note(160, 74, 4, P(R_COL - CH_BOT / 2, CH_BOT / 2),
                 ["下端の面取りを付け直す", "45°（+5°/0）、端面 φ5.8±0.2"])
    balloon_note(160, 56, 3, P(1.6, 0), ["下端面を削る", "溝位置から 2.1±0.1 に仕上げる"])
    note_leader(P(R_COL + 0.12, H_LOW + 0.05), (150, 96), "R0.4±0.2（変更なし）")
    note_leader(P(0.9, sock_y + 0.12), (150, 110), "六角穴 M4・穴深さ 4 MAX・穴底 R1 MAX（変更なし）")

    # ---------------- 表題・凡例・注記・図枠
    text(15, 192, "PLUG M8×0.75　追加工指示図（1ページ目の品物 → 2ページ目の品物）", 5.0)
    text(15, 184, "断面図（2ページ目の A-A と同じ向き）　尺度 10:1", 3.0)
    line(200, 186, 214, 186, 0.7, RED)
    text(216, 185, "加工する面", 3.0, color=RED)
    line(200, 179, 214, 179, 0.25, GRAY, PH)
    text(216, 178, "加工前の端面（元品が基準寸法の場合）", 3.0, color=GRAY)

    notes = [
        "注記",
        "1. 加工するのは赤線の 4 か所だけ。ねじ、φ6.8、溝、六角穴は変更しない。",
        "2. 加工順：③ → ④ → ① → ②（下端側で溝位置からの寸法を決めてから全長を合わせる）。",
        "3. 削り代は元品の実測値で決める（次ページの表）。二点鎖線は元品が全長 6.0、",
        "    溝から下端 2.2 の場合で、削り代は上端 約0.15、下端 約0.1。",
        "4. φ6.8 の同軸度 ◎φ0.2(M)、データム A（ねじ）は完成品図のとおり。",
        "5. 指示のない面の表面粗さ Ra12.5、指示のない角は完成品図のエッジ指示（-0.5）による。",
    ]
    y = 40.0
    for i, s in enumerate(notes):
        text(15, y, s, 3.0 if i == 0 else 2.6)
        y -= 4.4

    title_block([
        ("品名", "PLUG M8×0.75　追加工"),
        ("元品", "図番 1546996　P54（添付 1ページ目）"),
        ("完成品", "図番 21341250　01（添付 2ページ目）"),
        ("材質", "11SMnPb30+C（変更なし）"),
        ("尺度", "10 : 1　　単位 mm　　作成日 2026/10/14"),
    ], "1 / 2")
    frame()
    return list(prims)


def frame():
    polyline([(10, 10), (287, 10), (287, 200), (10, 200)], 0.7, closed=True)


def title_block(rows, sheet):
    x0, x1, y0, rh = 177.0, 287.0, 10.0, 6.0
    n = len(rows)
    polyline([(x0, y0), (x0, y0 + rh * n), (x1, y0 + rh * n)], 0.35)
    for i in range(1, n):
        line(x0, y0 + rh * i, x1, y0 + rh * i, 0.35)
    line(x0 + 15, y0, x0 + 15, y0 + rh * n, 0.35)
    for i, (k, v) in enumerate(rows):
        yy = y0 + rh * (n - 1 - i) + 1.8
        text(x0 + 2, yy, k, 2.6)
        text(x0 + 17, yy, v, 2.6)
    text(x1 - 2, y0 + rh * n + 1.5, sheet, 2.6, 0, "R")


# ================================================================ 2ページ目: 寸法の比較と削り代
def table(x0, y_top, widths, rows, rh=6.5, h=2.7, header_fill=True, colors=None):
    xs = [x0]
    for w in widths:
        xs.append(xs[-1] + w)
    n = len(rows)
    for i in range(n + 1):
        line(xs[0], y_top - rh * i, xs[-1], y_top - rh * i, 0.5 if i in (0, 1, n) else 0.25)
    for x in xs:
        line(x, y_top, x, y_top - rh * n, 0.5 if x in (xs[0], xs[-1]) else 0.25)
    for i, row in enumerate(rows):
        col = (colors or {}).get(i, BLACK)
        for j, cell in enumerate(row):
            text(xs[j] + 1.8, y_top - rh * i - rh / 2 - h / 2 + 0.2, cell, h, 0, "L", col)
    return y_top - rh * n


def page2():
    prims.clear()
    text(15, 192, "寸法の比較と削り代の決め方", 5.0)

    text(15, 183, "1. 寸法の比較（赤字が加工で変わる寸法）", 3.4)
    rows = [
        ("項目", "1ページ目（元品）1546996 P54", "2ページ目（完成品）21341250 01", "加工"),
        ("全長", "6 +0.5/0（6.0～6.5）", "5.75±0.25（5.5～6.0）", "① 上端面を削る"),
        ("溝位置から下端面まで", "2.2 +0.2/0（2.2～2.4）", "2.1±0.1（2.0～2.2）", "③ 下端面を削る"),
        ("上端の面取り", "0.75×45°", "0.75×45°", "② ①の後に付け直す"),
        ("下端の面取り", "45° +5°/0、端面 φ5.8±0.2", "同じ", "④ ③の後に付け直す"),
        ("ねじ", "M8×0.75-6g", "同じ", "なし"),
        ("段部の径", "φ6.8±0.1", "同じ", "なし"),
        ("溝", "R0.4±0.2", "同じ", "なし"),
        ("六角穴", "M4（STD 7124,5）", "M4（図番 1052942 参照）", "なし（深さは確認事項1）"),
        ("穴深さ・穴底", "4 MAX・R 1 MAX", "4 MAX・R1 MAX", "なし"),
        ("同軸度", "◎φ0.2(M) A(M)", "同じ", "なし"),
        ("材質", "11SMnPb30+C", "同じ", "なし"),
        ("表面粗さ（指示なし）", "Ra12.5", "Ra12.5", "―"),
        ("角部", "バリなし（STD 5080,341）", "エッジ指示 -0.5", "加工後にバリ取り"),
    ]
    y = table(15, 179, [45, 72, 72, 78], rows, rh=5.4, colors={0: BLACK, 1: RED, 2: RED, 3: RED, 4: RED})

    y -= 8
    text(15, y, "2. 削り代の決め方（元品を 1 個ずつ測ってから決める）", 3.4)
    y -= 7
    for s in [
        "下端の削り量 a ＝（元品の溝位置から下端面までの実測値）－ 2.1",
        "上端の削り量 b ＝（元品の全長の実測値）－ a － 5.75　　b が 0 以下なら上端は削らない",
    ]:
        text(20, y, s, 3.0, color=RED)
        y -= 5.0
    rows2 = [
        ("元品の全長", "元品の溝から下端", "下端の削り量 a", "上端の削り量 b", "加工後の全長", "加工後の溝から下端"),
        ("6.0", "2.2", "0.10", "0.15", "5.75", "2.1"),
        ("6.0", "2.4", "0.30", "0（計算 -0.05）", "5.70", "2.1"),
        ("6.25", "2.3", "0.20", "0.30", "5.75", "2.1"),
        ("6.5", "2.2", "0.10", "0.65", "5.75", "2.1"),
        ("6.5", "2.4", "0.30", "0.45", "5.75", "2.1"),
    ]
    y = table(20, y, [38, 42, 38, 42, 38, 42], rows2, rh=5.2)

    y -= 8
    text(15, y, "3. 確認事項", 3.4)
    y -= 6
    for s in [
        "1) 上端を最大 0.65 削るため、六角穴の深さが減る。1ページ目の手書きメモには「深さ min 2」とある。",
        "    図番 1052942 の深さ指示を満たすか確認する。満たさない場合は全長の狙いを 5.75 より大きく（6.0 以下）して上端の削り量を減らす。",
        "2) 元品が全長 6.0、溝から下端 2.2 ちょうどなら、そのままで完成品の公差内（どちらも上限）。加工するかは使い方で判断する。",
    ]:
        text(20, y, s, 2.7)
        y -= 4.6
    frame()
    return list(prims)


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
    pages = [page1(), page2()]
    c = canvas.Canvas(f"{out}/PLUG_M8x0.75_rework.pdf", pagesize=landscape(A4))
    c.setTitle("PLUG M8x0.75 追加工指示図")
    for pl in pages:
        c.saveState()
        c.scale(mm, mm)
        c.setLineCap(0)
        c.setLineJoin(1)
        draw(c, pl)
        c.restoreState()
        c.showPage()
    c.save()
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
