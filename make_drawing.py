# -*- coding: utf-8 -*-
"""(+)皿小ねじ 小頭 M6x15 先端φ4.5追加工品の図面を PDF と DXF で出力する。

座標はすべて用紙上の mm (A4 横 297x210)。部品は尺度 5:1 で描く。
"""
import math
import sys

import ezdxf
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
FONT = "IPAGothic"
pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))

# ---------------------------------------------------------------- 部品寸法 (実寸 mm)
L_TOTAL = 15.0      # 全長 ℓ
DK = 10.0           # 頭部径 dk
K = 2.4             # 頭部高さ k
C = 0.3             # 頭部円筒部 c (約)
D = 6.0             # ねじの呼び径
D1 = 4.917          # M6x1 谷の径 (基準寸法)
D_CUT = 4.5         # 切削後の径
L_CUT = 5.0         # 先端からの切削長さ
L_THREAD = L_TOTAL - K - L_CUT  # 頭の下からの残りねじ部長さ (参考)

S = 5.0             # 尺度 5:1
CY = 125.0          # 中心線の高さ (用紙)
X0 = 105.0          # 正面図 頭部上面の位置 (用紙)
HX = 50.0           # 頭部側から見た図の中心 x
TX = 235.0          # 先端側から見た図の中心 x


def px(x):
    return X0 + S * x


def pr(r):
    return S * r


# ---------------------------------------------------------------- 図形の記録
# 線の種類: (PDF の線幅 mm, 破線パターン mm, DXF 画層, DXF 線種)
STYLES = {
    "OUTLINE": (0.5, None, "OUTLINE", "CONTINUOUS"),
    "THIN": (0.25, None, "THIN", "CONTINUOUS"),
    "CENTER": (0.25, [8, 1.2, 1, 1.2], "CENTER", "CENTER"),
    "HIDDEN": (0.35, [2.5, 1], "HIDDEN", "HIDDEN"),
    "DIM": (0.25, None, "DIM", "CONTINUOUS"),
    "FRAME": (0.7, None, "FRAME", "CONTINUOUS"),
    "TITLE": (0.35, None, "FRAME", "CONTINUOUS"),
}

prims = []


def line(style, x1, y1, x2, y2):
    prims.append(("line", style, x1, y1, x2, y2))


def poly(style, pts, closed=False):
    pts = list(pts)
    if closed:
        pts.append(pts[0])
    for a, b in zip(pts, pts[1:]):
        line(style, a[0], a[1], b[0], b[1])


def circle(style, cx, cy, r):
    prims.append(("circle", style, cx, cy, r))


def arc(style, cx, cy, r, a1, a2):
    prims.append(("arc", style, cx, cy, r, a1, a2))


def solid(pts):
    prims.append(("solid", "DIM", pts))


def text(x, y, s, h=3.5, rot=0.0, align="L", layer="TEXT"):
    """x, y は基準点。align は L/C/R (水平方向)。y は文字の下端 (ベースライン)。"""
    prims.append(("text", layer, x, y, s, h, rot, align))


def text_width(s, h):
    return pdfmetrics.stringWidth(s, FONT, h / 0.88)


# ---------------------------------------------------------------- 寸法記入
ARROW_L = 3.0
ARROW_W = ARROW_L * math.tan(math.radians(15))
EXT_GAP = 1.0     # 外形と寸法補助線のすき間
EXT_OVER = 2.0    # 寸法線から寸法補助線を出す長さ
TXT_H = 3.5
TOL_H = 2.5


def arrow(tx, ty, dx, dy):
    """先端 (tx, ty)、向き (dx, dy) の塗りつぶし矢印。"""
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    bx, by = tx - dx * ARROW_L, ty - dy * ARROW_L
    nx, ny = -dy * ARROW_W, dx * ARROW_W
    solid([(tx, ty), (bx + nx, by + ny), (bx - nx, by - ny)])


def dim_text(cx, cy, rot, value, tol=None):
    """寸法数値 (必要なら上下の許容差を添える) を、(cx, cy) を下端中央として置く。"""
    if not value:
        return
    w_main = text_width(value, TXT_H)
    w_tol = 0.0
    if tol:
        w_tol = max(text_width(t, TOL_H) for t in tol) + 0.8
    total = w_main + w_tol
    a = math.radians(rot)
    ux, uy = math.cos(a), math.sin(a)        # 文字の進む向き
    vx, vy = -math.sin(a), math.cos(a)       # 文字の上向き

    def at(u, v):
        return cx + ux * u + vx * v, cy + uy * u + vy * v

    x, y = at(-total / 2, 0)
    text(x, y, value, TXT_H, rot, "L")
    if tol:
        upper, lower = tol
        x, y = at(-total / 2 + w_main + 0.8, 0)
        text(x, y, lower, TOL_H, rot, "L")
        x, y = at(-total / 2 + w_main + 0.8, TOL_H + 0.4)
        text(x, y, upper, TOL_H, rot, "L")


def hdim(x1, x2, y, from1, from2, value, tol=None, outside=False,
         text_at=None, ext1=True, ext2=True):
    """水平寸法。from1/from2 は寸法補助線を引き出す外形の y。"""
    for x, f, use in ((x1, from1, ext1), (x2, from2, ext2)):
        if not use:
            continue
        sgn = 1 if y > f else -1
        line("DIM", x, f + sgn * EXT_GAP, x, y + sgn * EXT_OVER)
    if outside:
        line("DIM", x1 - ARROW_L - 3, y, x2 + ARROW_L + 3, y)
        arrow(x1, y, 1, 0)
        arrow(x2, y, -1, 0)
    else:
        line("DIM", x1, y, x2, y)
        arrow(x1, y, -1, 0)
        arrow(x2, y, 1, 0)
    if text_at is None:
        dim_text((x1 + x2) / 2, y + 1.0, 0, value, tol)
    else:
        tx, align = text_at
        w = text_width(value, TXT_H)
        if align == "R":
            tx -= w
        text(tx, y + 1.0, value, TXT_H, 0, "L")


def vdim(y1, y2, x, from1, from2, value, tol=None):
    """垂直寸法。from1/from2 は寸法補助線を引き出す外形の x。数値は寸法線の左に縦書き方向(90°)で置く。"""
    for yy, f in ((y1, from1), (y2, from2)):
        sgn = 1 if x > f else -1
        line("DIM", f + sgn * EXT_GAP, yy, x + sgn * EXT_OVER, yy)
    line("DIM", x, y1, x, y2)
    arrow(x, y1, 0, -1)
    arrow(x, y2, 0, 1)
    dim_text(x - 1.0, (y1 + y2) / 2, 90, value, tol)


def leader(pts, label, h=TXT_H):
    """先端に矢印の付いた引出線。最後の水平線の上に文字を置く。"""
    poly("DIM", pts)
    (x0, y0), (x1, y1) = pts[0], pts[1]
    arrow(x0, y0, x0 - x1, y0 - y1)
    xa, ya = pts[-2]
    xb, yb = pts[-1]
    text(min(xa, xb) + 1.0, ya + 1.0, label, h, 0, "L")


# ================================================================ 図形本体
# ---------------- 正面図
r_head, r_d, r_d1, r_cut = pr(DK / 2), pr(D / 2), pr(D1 / 2), pr(D_CUT / 2)
x_face, x_c, x_k = px(0), px(C), px(K)
x_step, x_tip = px(L_TOTAL - L_CUT), px(L_TOTAL)

for sgn in (1, -1):
    line("OUTLINE", x_face, CY + sgn * r_head, x_c, CY + sgn * r_head)     # 頭部円筒部
    line("OUTLINE", x_c, CY + sgn * r_head, x_k, CY + sgn * r_d)           # 皿部
    line("OUTLINE", x_k, CY + sgn * r_d, x_step, CY + sgn * r_d)           # ねじ外径
    line("THIN", x_k, CY + sgn * r_d1, x_step, CY + sgn * r_d1)            # ねじ谷径
    line("OUTLINE", x_step, CY + sgn * r_cut, x_tip, CY + sgn * r_cut)     # 切削部
line("OUTLINE", x_face, CY - r_head, x_face, CY + r_head)   # 頭部上面
line("OUTLINE", x_c, CY - r_head, x_c, CY + r_head)         # 円筒部と皿部の境目
line("OUTLINE", x_k, CY - r_d, x_k, CY + r_d)               # 頭部と軸の境目
line("OUTLINE", x_step, CY - r_d, x_step, CY + r_d)         # 切削の段
line("OUTLINE", x_tip, CY - r_cut, x_tip, CY + r_cut)       # 先端面
line("CENTER", x_face - 5, CY, x_tip + 5, CY)

# 十字穴 (かくれ線、形状は略図)
for sgn in (1, -1):
    poly("HIDDEN", [(x_face, CY + sgn * 13), (x_face + 10.5, CY + sgn * 3),
                    (x_face + 13, CY)])

# ---------------- 頭部側から見た図 (左側面図)
circle("OUTLINE", HX, CY, r_head)
a, l = 3.0, 13.0
cross = [(a, l), (-a, l), (-a, a), (-l, a), (-l, -a), (-a, -a),
         (-a, -l), (a, -l), (a, -a), (l, -a), (l, a), (a, a)]
poly("OUTLINE", [(HX + x, CY + y) for x, y in cross], closed=True)
line("CENTER", HX - r_head - 3, CY, HX + r_head + 3, CY)
line("CENTER", HX, CY - r_head - 3, HX, CY + r_head + 3)

# ---------------- 先端側から見た図 (右側面図)
circle("OUTLINE", TX, CY, r_head)      # 頭部座面の外周
circle("OUTLINE", TX, CY, r_d)         # ねじ外径
arc("THIN", TX, CY, r_d1, 100, 350)    # ねじ谷径 (約3/4の細線)
circle("OUTLINE", TX, CY, r_cut)       # 切削部 φ4.5
line("CENTER", TX - r_head - 3, CY, TX + r_head + 3, CY)
line("CENTER", TX, CY - r_head - 3, TX, CY + r_head + 3)

# ================================================================ 寸法
# φdk
vdim(CY - r_head, CY + r_head, 93.0, x_face, x_face, "φ10", ("0", "-0.6"))
# c (約0.3)
hdim(x_face, x_c, 90.0, CY - r_head, CY - r_head, "約0.3", outside=True,
     text_at=(x_face - ARROW_L - 4, "R"))
# k, (残りねじ部), 切削長さ
# k は寸法の間隔が狭いので、寸法線を左へ延ばして数値を外側に置く
hdim(x_face, x_k, 80.0, CY - r_head, CY - r_d, "", ext1=False)
line("DIM", x_face - 15, 80.0, x_face, 80.0)
dim_text(x_face - 7.5, 81.0, 0, "2.4", ("0", "-0.3"))
hdim(x_k, x_step, 80.0, CY - r_d, CY - r_d, f"({L_THREAD:.1f})", ext1=False)
hdim(x_step, x_tip, 80.0, CY - r_d, CY - r_cut, "5")
# 全長 ℓ
hdim(x_face, x_tip, 70.0, CY - r_head, CY - r_cut, "15")
# φ4.5
vdim(CY - r_cut, CY + r_cut, 192.0, x_tip, x_tip, "φ4.5")
# ねじの呼び
leader([(x_k + 21, CY + r_d), (x_k + 29, CY + 33), (x_k + 43, CY + 33)], "M6")
# 十字穴
leader([(HX + a, CY + 9), (HX + 16, CY + 35), (HX + 46, CY + 35)], "十字穴の番号 2")

# ================================================================ 図枠・表題欄・注記
line("FRAME", 10, 10, 287, 10)
line("FRAME", 287, 10, 287, 200)
line("FRAME", 287, 200, 10, 200)
line("FRAME", 10, 200, 10, 10)

text(15, 191, "（＋）皿小ねじ　小頭　M6×15　先端 φ4.5 追加工品", 5.0)

# 表題欄 x:167-287, y:10-45 (5行 x 7mm)
TB_X0, TB_X1, TB_Y0 = 167.0, 287.0, 10.0
ROW = 7.0
rows = 5
line("TITLE", TB_X0, TB_Y0, TB_X0, TB_Y0 + ROW * rows)
line("TITLE", TB_X0, TB_Y0 + ROW * rows, TB_X1, TB_Y0 + ROW * rows)
for i in range(1, rows):
    line("TITLE", TB_X0, TB_Y0 + ROW * i, TB_X1, TB_Y0 + ROW * i)


def cell_text(x, row, s, h=2.8):
    """row は上から 0 始まり。"""
    y = TB_Y0 + ROW * (rows - 1 - row) + (ROW - h) / 2 + 0.3
    text(x, y, s, h)


def vsep(x, row_from, row_to):
    y_top = TB_Y0 + ROW * (rows - row_from)
    y_bot = TB_Y0 + ROW * (rows - row_to - 1)
    line("TITLE", x, y_bot, x, y_top)


LBL = TB_X0 + 18
vsep(LBL, 0, 4)
cell_text(TB_X0 + 2, 0, "品名")
cell_text(LBL + 2, 0, "（＋）皿小ねじ 小頭 M6×15 先端追加工")
cell_text(TB_X0 + 2, 1, "尺度")
cell_text(LBL + 2, 1, "5 : 1")
vsep(LBL + 22, 1, 1)
cell_text(LBL + 24, 1, "単位　mm")
vsep(LBL + 50, 1, 1)
cell_text(LBL + 52, 1, "第三角法")
cell_text(TB_X0 + 2, 2, "材質")
cell_text(LBL + 2, 2, "元品のとおり（指定なし）")
cell_text(TB_X0 + 2, 3, "元品")
cell_text(LBL + 2, 3, "ねじの呼び M6　全長 15　ピッチ 1.0")
cell_text(TB_X0 + 2, 4, "作成日")
cell_text(LBL + 2, 4, "2026/10/09")

# 第三角法の記号 (円錐台: 正面形の細い側に円の図を置く)
sx, sy = LBL + 77, TB_Y0 + ROW * 3 + ROW / 2
poly("THIN", [(sx, sy + 2.2), (sx + 5, sy + 1.2), (sx + 5, sy - 1.2), (sx, sy - 2.2)],
     closed=True)
circle("THIN", sx + 9.5, sy, 2.2)
circle("THIN", sx + 9.5, sy, 1.2)

# 注記
notes = [
    "注記",
    "1. 元品：（＋）皿小ねじ 小頭 M6×15（頭部寸法は元図面 M6 の値）。",
    "2. 追加工：ねじ先端から長さ 5 の範囲を外径 φ4.5 に切削する。",
    "    φ4.5 は M6 の谷の径（基準寸法 4.917）より小さいため、",
    "    切削部にねじ山は残らない。",
    "3. 十字穴の番号：2（ステンレス製は 3）。十字穴の形状は略図。",
    "4. （　）内の寸法は参考寸法。",
    "5. φ4.5 と長さ 5 の許容差は指定なし（必要なら追記すること）。",
    "6. 指示のない角は糸面取りとする。",
]
y = 50.0
for i, s in enumerate(notes):
    text(15, y, s, 3.0 if i == 0 else 2.8)
    y -= 4.8


# ================================================================ PDF 出力
def write_pdf(path):
    w, h = landscape(A4)
    c = canvas.Canvas(path, pagesize=(w, h))
    c.setTitle("皿小ねじ M6x15 先端φ4.5追加工 図面")
    c.scale(mm, mm)
    c.setLineCap(0)
    c.setLineJoin(1)
    for p in prims:
        kind = p[0]
        if kind == "text":
            _, _, x, y, s, hgt, rot, align = p
            c.saveState()
            c.setFillColorRGB(0, 0, 0)
            c.translate(x, y)
            c.rotate(rot)
            c.setFont(FONT, hgt / 0.88)  # 文字高さ ≒ フォントサイズ x 0.88 (漢字の字面)
            fs = hgt / 0.88
            wdt = pdfmetrics.stringWidth(s, FONT, fs)
            dx = {"L": 0, "C": -wdt / 2, "R": -wdt}[align]
            c.drawString(dx, 0, s)
            c.restoreState()
            continue
        if kind == "solid":
            pts = p[2]
            c.setFillColorRGB(0, 0, 0)
            path_ = c.beginPath()
            path_.moveTo(*pts[0])
            for q in pts[1:]:
                path_.lineTo(*q)
            path_.close()
            c.drawPath(path_, stroke=0, fill=1)
            continue
        width, dash, _, _ = STYLES[p[1]]
        c.setLineWidth(width)
        c.setDash(dash if dash else [])
        if kind == "line":
            c.line(*p[2:6])
        elif kind == "circle":
            c.circle(p[2], p[3], p[4], stroke=1, fill=0)
        elif kind == "arc":
            _, _, cx, cy, r, a1, a2 = p
            c.arc(cx - r, cy - r, cx + r, cy + r, startAng=a1, extent=a2 - a1)
    c.showPage()
    c.save()


# ================================================================ DXF 出力 (R12, Shift_JIS)
def write_dxf(path):
    doc = ezdxf.new("R12", setup=True)
    doc.encoding = "cp932"  # $DWGCODEPAGE = ANSI_932
    colors = {"OUTLINE": 7, "THIN": 3, "CENTER": 1, "HIDDEN": 4, "DIM": 2,
              "FRAME": 7, "TEXT": 7}
    ltypes = {"CENTER": "CENTER", "HIDDEN": "HIDDEN"}
    for name, col in colors.items():
        doc.layers.add(name, color=col, linetype=ltypes.get(name, "CONTINUOUS"))
    msp = doc.modelspace()
    for p in prims:
        kind = p[0]
        if kind == "text":
            _, layer, x, y, s, hgt, rot, align = p
            if align != "L":
                wdt = text_width(s, hgt)
                a = math.radians(rot)
                off = wdt / 2 if align == "C" else wdt
                x -= math.cos(a) * off
                y -= math.sin(a) * off
            msp.add_text(s, dxfattribs={"layer": layer, "height": hgt,
                                        "rotation": rot, "insert": (x, y)})
            continue
        if kind == "solid":
            msp.add_solid(p[2], dxfattribs={"layer": "DIM"})
            continue
        layer = STYLES[p[1]][2]
        attrs = {"layer": layer}
        if kind == "line":
            msp.add_line(p[2:4], p[4:6], dxfattribs=attrs)
        elif kind == "circle":
            msp.add_circle((p[2], p[3]), p[4], dxfattribs=attrs)
        elif kind == "arc":
            msp.add_arc((p[2], p[3]), p[4], p[5], p[6], dxfattribs=attrs)
    doc.header["$LTSCALE"] = 1.0
    doc.saveas(path, encoding="cp932")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    write_pdf(f"{out}/M6x15_tip_phi4.5.pdf")
    write_dxf(f"{out}/M6x15_tip_phi4.5.dxf")
    print("ok")
