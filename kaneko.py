# -*- coding: utf-8 -*-
"""株式会社カネコの A4 図面書式 (templates/kaneko_A4_title.jww) で図面を作るための共通部品。

座標は JWW と同じく用紙中心を原点とした用紙上の mm。
使い方: sh = Sheet(); load_template(sh); fill_title(sh, {...}); (図を描く); render(sh, path, title)
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

    def circle(self, cx, cy, r, pen=1, style=1):
        self.arc(cx, cy, r, 0, 360, pen, style)

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


# 表題欄のセル (x 左, x 右, y 下, y 上)。書式の罫線から読んだ値。
XL, XR = 59.67, 139.67            # 右側の欄
VAL = 74.67                       # 右側の欄の項目名と記入欄の境
CELLS = {
    "品番": (XL, VAL, -34.33, -28.33), "品番_値": (VAL, XR, -34.33, -28.33),
    "図番": (XL, VAL, -40.33, -34.33), "図番_値": (VAL, XR, -40.33, -34.33),
    "得意先": (XL, VAL, -52.33, -40.33), "得意先_値": (VAL, XR, -52.33, -40.33),
    "品名": (XL, VAL, -64.33, -52.33), "品名_値": (VAL, XR, -64.33, -52.33),
    "第三角法": (-25.33, 19.67, -60.33, -54.33),
    "尺度": (19.67, 39.67, -60.33, -54.33), "尺度_値": (39.67, XL, -60.33, -54.33),
    "仕様": (-25.33, XL, -66.33, -60.33),
    "材質": (-25.33, -0.33, -72.33, -66.33), "材質_値": (-0.33, XL, -72.33, -66.33),
    "熱処理": (-25.33, -0.33, -78.33, -72.33), "熱処理_値": (-0.33, XL, -78.33, -72.33),
    "表面処理": (-25.33, -0.33, -84.33, -78.33), "表面処理_値": (-0.33, XL, -84.33, -78.33),
}
for _x0, _key in ((79.67, "承認"), (99.67, "検図"), (119.67, "製図")):
    CELLS[_key] = (_x0, _x0 + 20, -70.33, -64.33)
    CELLS[_key + "_日付"] = (_x0, _x0 + 20, -80.33, -70.33)   # 押印欄の上半分
    CELLS[_key + "_値"] = (_x0, _x0 + 20, -90.33, -80.33)     # 押印欄の下半分
TITLE_LABEL_CELLS = [k for k in CELLS if not k.endswith(("_値", "_日付"))]
PAPER_W = 297.0                   # 用紙の幅。原点は用紙中心


def cell_text(sheet, cell, s, size, sp=0.5, margin=1.0):
    """セルの左右・上下の中央に置く。入りきらなければ文字を小さくする。"""
    if not s:
        return
    x1, x2, y1, y2 = cell
    size = fit_size(s, size, sp, x2 - x1 - 2 * margin)
    size = min(size, y2 - y1 - 1.0)       # 上下は 0.5 ずつ空ける
    w = text_width(s, size, sp)
    sheet.text((x1 + x2 - w) / 2, (y1 + y2 - size) / 2, s, size, sp)


def find_cell(x, y):
    for k in TITLE_LABEL_CELLS:
        x1, x2, y1, y2 = CELLS[k]
        if x1 < x < x2 and y1 < y < y2:
            return CELLS[k]
    return None


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
            s, size, sp = e["s"], e["sy"], e["sp"]
            cell = find_cell((e["x1"] + e["x2"]) / 2, e["y1"] + size / 2)
            if cell:                  # 表題欄の項目名はセルの中央へ
                cell_text(sheet, cell, s, size, sp)
            elif "カネコ" in s.replace(" ", ""):  # 社名は用紙の左右中央へ (高さは書式のまま)
                sheet.text(-text_width(s, size, sp) / 2, e["y1"], s, size, sp)
            else:
                sheet.items.append(("text", (e["x1"], e["y1"], s, size, sp, e["ang"]), 1, 1))


def fill_title(sheet, f):
    """表題欄の記入。各セルの中央に置く。"""
    cell_text(sheet, CELLS["品番_値"], f["品番"], 5.0)
    cell_text(sheet, CELLS["図番_値"], f["図番"], 5.0)
    cell_text(sheet, CELLS["得意先_値"], f["得意先"], 4.5, sp=0.3)
    cell_text(sheet, CELLS["品名_値"], f["品名"], 5.0, sp=0.3)
    cell_text(sheet, CELLS["尺度_値"], f["尺度"], 4.0)
    for key in ("材質", "熱処理", "表面処理"):
        cell_text(sheet, CELLS[key + "_値"], f.get(key, ""), 4.5)
    for key in ("承認", "検図", "製図"):
        cell_text(sheet, CELLS[key + "_日付"], f.get(key + "_日付", ""), 3.0)
        cell_text(sheet, CELLS[key + "_値"], f.get(key, ""), 5.0)


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


def leader(sh, tx, ty, ex, ey, label, size=4.0, side="R", sub=None):
    """引出線。(tx, ty) に矢印、(ex, ey) から side 側へ棚を出し、棚の上に label、下に sub を書く。"""
    w = max(text_width(t, size, 0.5) for t in (label, sub) if t)
    x0 = ex if side == "R" else ex - w - 2
    sh.line(tx, ty, ex, ey)
    sh.line(x0, ey, x0 + w + 2, ey)
    arrow(sh, tx, ty, tx - ex, ty - ey)
    sh.text(x0 + 1, ey + 0.8, label, size)
    if sub:
        sh.text(x0 + 1, ey - 0.8 - size, sub, size)
