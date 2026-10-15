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


TITLE = {
    "品番": "CRS-001",
    "図番": "",
    "得意先": "有限会社シー・アール・エス",
    "品名": "SUS脱落防止トラス十字ネジM4×12,S=3",
    "尺度": "5/1",
    "材質": "SUS",
}


def main(out, draft=False):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    if draft:
        sh.text(0, 40, "（図はねじの寸法を確認してから描く）", 6.0, align="C")
    render(sh, os.path.join(out, "CRS-001_draft.pdf" if draft else "CRS-001.pdf"),
           "CRS-001 SUS脱落防止トラス十字ネジ M4×12, S=3")
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".", draft=True)
