# -*- coding: utf-8 -*-
"""CRS-001（SUS脱落防止トラス十字ネジ M4×12, S=3）の図面を、株式会社カネコの A4 図面書式 (JWW) に合わせて PDF で出力する。

書式 (枠・表題欄) は templates/kaneko_A4_title.jww から読み込む。
座標は JWW と同じく用紙中心を原点とした用紙上の mm。
"""
import math
import os
import sys

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
import jwwread  # noqa: E402

FONT = "IPAGothic"
pdfmetrics.registerFont(TTFont(FONT, "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "kaneko_A4_title.jww")

# Jw_cad の線色 -> 印刷時の線幅 (mm)。書式では 1 が細線、6 が外形線。
PEN_WIDTH = {1: 0.25, 6: 0.5}
# Jw_cad の線種 -> 破線パターン (mm)
PEN_DASH = {1: None, 2: [1, 1], 5: [10, 1.5, 1, 1.5], 6: [10, 1.5, 1, 1.5], 7: [10, 1.5, 1, 1, 1, 1.5]}

# 表題欄に元から入っている記入例 (差し替える文字)
TEMPLATE_CONTENT = {"SUS", "T型ねじ（SUS）", "2024.9.26", "斎藤", "清水"}


# ---------------------------------------------------------------- 図形の記録 (JWW と同じ用紙座標)
class Sheet:
    def __init__(self):
        self.items = []

    def line(self, x1, y1, x2, y2, pen=1, style=1):
        self.items.append(("line", (x1, y1, x2, y2), pen, style))

    def arc(self, cx, cy, r, a0, a1, pen=1, style=1):
        """a0 から a1 まで反時計回り (度)。"""
        self.items.append(("arc", (cx, cy, r, a0, a1), pen, style))

    def solid(self, pts):
        self.items.append(("solid", pts, 1, 1))

    def text(self, x, y, s, size=5.0, sp=0.5, ang=0.0, align="L"):
        """JWW と同じく (x, y) は文字列の左下。align=C/R は (x, y) を中央/右下とみなす。"""
        w = text_width(s, size, sp)
        a = math.radians(ang)
        if align == "C":
            x, y = x - math.cos(a) * w / 2, y - math.sin(a) * w / 2
        elif align == "R":
            x, y = x - math.cos(a) * w, y - math.sin(a) * w
        self.items.append(("text", (x, y, s, size, sp, ang), 1, 1))


def is_full(ch):
    """Jw_cad と同じく Shift_JIS で 2 バイトになる文字を全角とみなす。"""
    try:
        return len(ch.encode("cp932")) == 2
    except UnicodeEncodeError:
        return True


def fit_size(s, size, sp, width):
    """width (mm) に収まるまで文字の大きさを小さくする。"""
    while size > 2.0 and text_width(s, size, sp) > width:
        size -= 0.1
    return size


def text_width(s, size, sp):
    """Jw_cad の文字幅: 全角 = size、半角 = size/2、文字間隔は全角 sp、半角 sp/2。"""
    w = 0.0
    for i, ch in enumerate(s):
        w += size if is_full(ch) else size / 2
        if i < len(s) - 1:
            w += sp if is_full(ch) else sp / 2
    return w


def load_template(sheet):
    d = open(TEMPLATE, "rb").read()
    ver = int.from_bytes(d[8:12], "little")
    start = d.find(b"CData") - 8
    ents = jwwread.read_list(jwwread.R(d, start), ver)
    for e in ents:
        if e["glayer"] != 1:          # レイヤグループ 1 が枠と表題欄。2 は元の図なので使わない
            continue
        if e["type"] == "line":
            sheet.line(e["x1"], e["y1"], e["x2"], e["y2"], e["color"], e["style"])
        elif e["type"] == "text" and e["s"] not in TEMPLATE_CONTENT:
            sheet.items.append(("text", (e["x1"], e["y1"], e["s"], e["sy"], e["sp"], e["ang"]), 1, 1))


def fill_title(sheet, f):
    """表題欄の記入。セル位置は書式の罫線から読んだ値。"""
    t = sheet.text
    t(77.0, -33.93, f["品番"], 5.0)
    t(77.0, -39.92, f["図番"], 5.0)
    t(77.0, -48.68, f["得意先"], fit_size(f["得意先"], 4.5, 0.3, 61.0), sp=0.3)
    t(107.17, -61.12, f["品名"], fit_size(f["品名"], 5.0, 0.3, 63.0), sp=0.3, align="C")
    t(49.67, -59.87, f["尺度"], 4.0, align="C")
    t(-0.33 + 39.67 / 2 + 19.5, -65.92, f.get("仕様", ""), 4.0, align="C")
    t(19.67, -72.16, f["材質"], 4.5, align="C")
    t(19.67, -78.08, f.get("熱処理", ""), 4.5, align="C")
    t(19.67, -83.95, f.get("表面処理", ""), 4.5, align="C")
    for x0, key in ((79.67, "承認"), (99.67, "検図"), (119.67, "製図")):
        if f.get(key + "_日付"):
            t(x0 + 10, -77.9, f[key + "_日付"], 3.0, align="C")
        if f.get(key):
            t(x0 + 10, -85.8, f[key], 5.0, align="C")


# ---------------------------------------------------------------- PDF 出力
def render(sheet, path, title):
    c = canvas.Canvas(path, pagesize=landscape(A4))
    c.setTitle(title)
    c.scale(mm, mm)
    c.translate(297 / 2, 210 / 2)      # JWW の原点 = 用紙中心
    c.setLineCap(0)
    c.setLineJoin(1)
    for kind, data, pen, style in sheet.items:
        c.setStrokeColorRGB(0, 0, 0)
        c.setFillColorRGB(0, 0, 0)
        if kind == "text":
            x, y, s, size, sp, ang = data
            c.saveState()
            c.translate(x, y)
            c.rotate(ang)
            c.setFont(FONT, size)
            u = 0.0
            for i, ch in enumerate(s):
                c.drawString(u, size * 0.12, ch)
                u += (size if is_full(ch) else size / 2) + (sp if is_full(ch) else sp / 2)
            c.restoreState()
            continue
        if kind == "solid":
            p = c.beginPath()
            p.moveTo(*data[0])
            for q in data[1:]:
                p.lineTo(*q)
            p.close()
            c.drawPath(p, stroke=0, fill=1)
            continue
        c.setLineWidth(PEN_WIDTH.get(pen, 0.25))
        c.setDash(PEN_DASH.get(style) or [])
        if kind == "line":
            c.line(*data)
        elif kind == "arc":
            cx, cy, r, a0, a1 = data
            c.arc(cx - r, cy - r, cx + r, cy + r, startAng=a0, extent=a1 - a0)
    c.showPage()
    c.save()


# ---------------------------------------------------------------- 寸法記入 (書式と同じ開いた矢印: 長さ 2、開き 15°)
ARROW = 2.0


def arrow(sh, tx, ty, dx, dy):
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    for s in (1, -1):
        a = math.radians(15) * s
        rx = dx * math.cos(a) - dy * math.sin(a)
        ry = dx * math.sin(a) + dy * math.cos(a)
        sh.line(tx, ty, tx - rx * ARROW, ty - ry * ARROW)


def hdim(sh, x1, x2, y, f1, f2, label, size=4.5, outside=False):
    for x, f in ((x1, f1), (x2, f2)):
        s = 1 if y > f else -1
        sh.line(x, f + s * 1.0, x, y + s * 1.5)
    if outside:
        sh.line(x1 - 6, y, x2 + 6, y)
        arrow(sh, x1, y, 1, 0)
        arrow(sh, x2, y, -1, 0)
    else:
        sh.line(x1, y, x2, y)
        arrow(sh, x1, y, -1, 0)
        arrow(sh, x2, y, 1, 0)
    sh.text((x1 + x2) / 2, y + 1.0, label, size, align="C")


def vdim(sh, y1, y2, x, f1, f2, label, size=4.5):
    for yy, f in ((y1, f1), (y2, f2)):
        s = 1 if x > f else -1
        sh.line(f + s * 1.0, yy, x + s * 1.5, yy)
    sh.line(x, y1, x, y2)
    arrow(sh, x, y1, 0, -1)
    arrow(sh, x, y2, 0, 1)
    sh.text(x - 1.0, (y1 + y2) / 2, label, size, ang=90, align="C")


def tol_text(sh, x, y, main, upper, lower, size=4.5, tsize=3.0):
    """縦向き (90°) の寸法数値に上下の許容差を添える。(x, y) は数値の下端の書き出し位置。"""
    w = text_width(main, size, 0.5)
    sh.text(x, y, main, size, ang=90)
    sh.text(x, y + w + 0.8, lower, tsize, ang=90)
    sh.text(x - tsize - 0.6, y + w + 0.8, upper, tsize, ang=90)


def leader(sh, tx, ty, ex, ey, label, size=4.0):
    w = text_width(label, size, 0.5)
    sh.line(tx, ty, ex, ey)
    sh.line(ex, ey, ex + w + 2, ey)
    arrow(sh, tx, ty, tx - ex, ty - ey)
    sh.text(ex + 1, ey + 0.8, label, size)


# ---------------------------------------------------------------- ねじの寸法 (実寸 mm)
SCREW = {
    "L": 12.0,        # 呼び長さ (座面から先端)
    "S": 3.0,         # ねじ部長さ (先端側)
    "d": 4.0,         # M4
    "d1": 3.242,      # M4 並目 谷の径 (基準寸法)
    "ds": 3.0,        # 首下の軸径 d (ミスミ規格表: 3 0/-0.3)
    "dk": 9.4,        # 頭部の径 A (ミスミ規格表)
    "k": 2.5,         # 頭部の高さ E (ミスミ規格表)
    "rim": 0.0,       # 頭部外周の立ち上がり (ミスミの図に合わせてなし。角は r0.3)
}
SCALE = 5.0


def draw_screw(sh, sc=SCREW):
    S_ = SCALE
    X0, Y0 = -10.0, 25.0          # 正面図: 座面と中心線
    HX = -80.0                    # 頭部側から見た図の中心 x

    def P(x, r):
        return X0 + S_ * x, Y0 + S_ * r

    L, Sl, k = sc["L"], sc["S"], sc["k"]
    rd, rd1, rs, rk, rim = sc["d"] / 2, sc["d1"] / 2, sc["ds"] / 2, sc["dk"] / 2, sc["rim"]
    ch = rd - rd1                 # 先端の面取り (谷の径まで)

    # ---- 正面図 外形 (線色 6 = 太線)
    for sg in (1, -1):
        if rim > 0:
            sh.line(*P(0, sg * rk), *P(-rim, sg * rk), 6)             # 頭部外周の立ち上がり
        sh.line(*P(0, sg * rs), *P(L - Sl, sg * rs), 6)              # 首下の細い軸
        sh.line(*P(L - Sl, sg * rd), *P(L - ch, sg * rd), 6)         # ねじ外径
        sh.line(*P(L - ch, sg * rd), *P(L, sg * rd1), 6)             # 先端の面取り
        sh.line(*P(L - Sl, sg * rd1), *P(L - ch, sg * rd1), 1)       # ねじ谷径 (細線)
    sh.line(*P(0, -rk), *P(0, rk), 6)                                # 座面
    sh.line(*P(L - Sl, -rd), *P(L - Sl, rd), 6)                      # 軸とねじ部の段
    sh.line(*P(L, -rd1), *P(L, rd1), 6)                              # 先端面
    # 頭部の丸み: 外周 (rim, rk) と頂点 (k, 0) を通る円弧
    h = k - rim
    R = (rk ** 2 + h ** 2) / (2 * h)
    cx, _ = P(-k + R, 0)
    a = math.degrees(math.atan2(rk, -(R - h)))
    sh.arc(cx, Y0, S_ * R, a, 360 - a, 6)
    # 十字穴 (かくれ線、略図)
    for sg in (1, -1):
        sh.line(*P(-k + 0.15, sg * 1.1), *P(-k + 1.9, sg * 0.25), 1, 2)
        sh.line(*P(-k + 1.9, sg * 0.25), *P(-k + 2.1, 0), 1, 2)
    sh.line(*P(-k - 0.7, 0), *P(L + 0.7, 0), 1, 6)                   # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.arc(HX, Y0, S_ * rk, 0, 360, 6)
    aw, al = 0.55 * S_, 2.2 * S_
    cross = [(aw, al), (-aw, al), (-aw, aw), (-al, aw), (-al, -aw), (-aw, -aw),
             (-aw, -al), (aw, -al), (aw, -aw), (al, -aw), (al, aw), (aw, aw)]
    for p, q in zip(cross, cross[1:] + cross[:1]):
        sh.line(HX + p[0], Y0 + p[1], HX + q[0], Y0 + q[1], 6)
    sh.line(HX - S_ * rk - 3, Y0, HX + S_ * rk + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S_ * rk - 3, HX, Y0 + S_ * rk + 3, 1, 6)

    # ---- 寸法
    xb, xt = P(0, 0)[0], P(L, 0)[0]
    hdim(sh, xb, xt, -10.0, P(0, -rk)[1], P(L, -rd1)[1], "12")
    hdim(sh, P(L - Sl, 0)[0], xt, 45.0, P(L - Sl, rd)[1], P(L, rd1)[1], "3")
    hdim(sh, P(-k, 0)[0], xb, 57.0, Y0, P(0, rk)[1], "2.5")
    vdim(sh, P(0, -rk)[1], P(0, rk)[1], -32.0, P(-rim, -rk)[0], P(-rim, rk)[0], "φ9.4")
    # 首下の軸径: 矢印を外側から当て、数値は上へ
    xs = P(5.0, 0)[0]
    ys1, ys2 = P(0, -rs)[1], P(0, rs)[1]
    sh.line(xs, ys1 - 5, xs, ys2 + 15)
    arrow(sh, xs, ys1, 0, 1)
    arrow(sh, xs, ys2, 0, -1)
    tol_text(sh, xs - 1.0, ys2 + 4.0, "φ3", "0", "-0.3")
    leader(sh, *P(-0.25, rk - 0.35), -6.0, 60.0, "r0.3")
    leader(sh, *P(L - Sl / 2 - 0.4, rd), 62.0, 60.0, "M4（並目）")
    leader(sh, HX + aw + 0.5, Y0 + al * 0.6, -62.0, 60.0, "十字穴 No.2")

    # ---- 注記
    notes = ["注記",
             "1. ねじはメートル並目、ねじ部は先端側の長さ 3、先端は平先。",
             "2. 首下の軸 φ3 はねじの谷の径より細く、脱落防止とする。",
             "3. 指示のない角はバリなきこと。"]
    y = -22.0
    for i, s in enumerate(notes):
        sh.text(-135.0, y, s, 4.0 if i == 0 else 3.5, sp=0.3)
        y -= 6.0


TITLE = {
    "品番": "CRS-001",
    "図番": "",
    "得意先": "有限会社シー・アール・エス",
    "品名": "SUS脱落防止トラス十字ネジM4×12,S=3",
    "尺度": "5/1",
    "材質": "SUS304相当",
    "表面処理": "なし",
}


def main(out, draft=False):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    if draft:
        sh.text(0, 40, "（図はねじの寸法を確認してから描く）", 6.0, align="C")
    else:
        draw_screw(sh)
    render(sh, os.path.join(out, "CRS-001_draft.pdf" if draft else "CRS-001.pdf"),
           "CRS-001 SUS脱落防止トラス十字ネジ M4×12, S=3")
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
