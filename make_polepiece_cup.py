# -*- coding: utf-8 -*-
"""ポールピースねじ (エレキギターのピックアップ用) の、樹脂部品に鉄の円筒を圧入する形の図面を、
株式会社カネコの A4 図面書式で PDF に出力する。組立図、鉄部品、樹脂部品の 3 枚を 1 本のスクリプトで出す。

元の形: make_polepiece.py (仕様案2: 金属頭部のピンを樹脂ねじ軸の穴に圧入する形)。
今回の変更 (依頼者の指示):
- 樹脂を頭部の外径 (φ5) まで伸ばし、頭部も樹脂にする。
- 頭部の上面に穴を開け、S10C の円筒を圧入する。円筒は上面にすりわり、外周にローレット。
仕様案2から引き継いだ値: 頭部の外径 φ5、頭部の高さ 2.5、ねじ #5-40 UNC-2A、ねじ部の長さ 14.5、全長 17.0、
すりわり 幅 0.8 × 深さ 1.0、樹脂は POM または PEEK、鉄は S10C 相当材、ニッケルめっき または 金めっき。
こちらで決めた値 (要確認):
- 円筒は φ3.5 × 1.8 (ローレット前の径)。ローレットは平目 (軸に平行な目) で外周の全長。
- 樹脂の穴は φ3.4 (圧入しろ 0.1、仕様案2のピンと穴の差と同じ) × 深さ 1.8 で底は平ら。
  円筒の上面と樹脂の上面を面一にする。頭部の樹脂の肉厚は 0.8、穴の底から座面までは 0.7。
- 頭部の上面は平ら (仕様案2のような丸みは付けない)。角は C0.2。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width, vdim)
from make_polepiece import (DK, KH, N, T, D, D1, P_, THICK, THIN,  # noqa: E402
                            center_lines, fmt, hatch, hatch_both, notes, pl)

# ---- 鉄部品 (部品 1)
DM = 3.5        # 円筒の径 (ローレット前)
LM = 1.8        # 円筒の長さ
CM = 0.2        # 円筒の両端の面取り
# ---- 樹脂部品 (部品 2)
CH = 0.2        # 頭部の上面と座面側の角の面取り
DB = 3.4        # 円筒を圧入する穴の径
BD = 1.8        # 穴の深さ
CB = 0.2        # 穴の入口の面取り
LR = 14.5       # ねじ部の長さ (座面から先端まで)
CR = 0.3        # ねじ先の面取り
LI = 2 * P_     # 座面側の不完全ねじ部 (2 山)
L = KH + LR     # 全長

SURF = "ニッケルめっき または 金めっき"
SHEETS = {
    "assy": {"title": {"品番": "", "図番": "", "得意先": "", "品名": "ポールピースねじ組立 円筒圧入 #5-40 UNC×17",
                       "尺度": "5/1", "材質": ""},
             "file": "ポールピースねじ組立_円筒圧入_No5-40UNCx17.pdf"},
    "metal": {"title": {"品番": "", "図番": "", "得意先": "", "品名": "ポールピースねじ 鉄部品 φ3.5×1.8",
                        "尺度": "10/1", "材質": "S10C相当材", "表面処理": SURF},
              "file": "ポールピースねじ_鉄部品_φ3.5x1.8.pdf"},
    "resin": {"title": {"品番": "", "図番": "", "得意先": "", "品名": "ポールピースねじ 樹脂部品 #5-40 UNC×17",
                        "尺度": "10/1", "材質": "POMまたはPEEK"},
              "file": "ポールピースねじ_樹脂部品_No5-40UNCx17.pdf"},
}


# ---------------------------------------------------------------- 部品の形 (局所座標: x は上面から軸方向、y は半径方向)
def metal_outline(rm):
    """鉄部品の上半分の外形 (すりわりの縁から外周、下端の中心まで)。"""
    hn = N / 2
    return [(0, hn), (0, rm - CM), (CM, rm), (LM - CM, rm), (LM, rm - CM), (LM, 0)]


def draw_metal(sh, P, rm, section):
    hn = N / 2
    for sg in (1, -1):
        pl(sh, P, metal_outline(rm), sg)
        pl(sh, P, [(0, hn), (T, hn)], sg)                       # すりわりの側面
    pl(sh, P, [(T, -hn), (T, hn)])                               # すりわりの底
    if section:
        return
    for sg in (1, -1):
        pl(sh, P, [(CM, hn), (CM, rm)], sg)                      # 上側の面取りの境 (すりわりで切れる)
    pl(sh, P, [(LM - CM, -rm), (LM - CM, rm)])                   # 下側の面取りの境
    for y in (0.65, 0.95, 1.25, 1.5):                            # 平目ローレット (軸に平行な細線)
        for sg in (1, -1):
            pl(sh, P, [(CM, sg * y), (LM - CM, sg * y)], pen=THIN)


def metal_hatch_polys(rm):
    hn = N / 2
    return [[(0, hn), (0, rm - CM), (CM, rm), (LM - CM, rm), (LM, rm - CM), (LM, hn)],
            [(T, 0), (LM, 0), (LM, hn), (T, hn)]]


def resin_outline():
    """樹脂部品の上半分の外形 (穴の入口から外周、ねじ先まで) と穴。"""
    R, r, rb = DK / 2, D / 2, DB / 2
    outer = [(0, rb + CB), (0, R - CH), (CH, R), (KH - CH, R), (KH, R - CH), (KH, r),
             (L - CR, r), (L, r - CR)]
    bore = [(0, rb + CB), (CB, rb), (BD, rb), (BD, 0)]
    return outer, bore


def resin_hatch_polys():
    R, r, rb = DK / 2, D / 2, DB / 2
    return [[(0, rb + CB), (CB, rb), (BD, rb), (BD, R), (CH, R), (0, R - CH)],
            [(BD, 0), (KH, 0), (KH, R - CH), (KH - CH, R), (BD, R)],
            [(KH, 0), (L, 0), (L, r - CR), (L - CR, r), (KH, r)]]


def draw_thread_lines(sh, P, sgs=(1, -1)):
    r, r1 = D / 2, D1 / 2
    for sg in sgs:
        pl(sh, P, [(KH + LI, r1), (L, r1)], sg, THIN)            # ねじの谷の径 (細線)
    pl(sh, P, [(KH + LI, -r), (KH + LI, r)])                      # 完全ねじ部の境
    pl(sh, P, [(L, -(r - CR)), (L, r - CR)])                      # ねじ先の端面


def slot_view(sh, cx, cy, S, rm):
    """上面から見たすりわり (横向き)。"""
    hn = N / 2
    xe = math.sqrt(rm * rm - hn * hn)
    for sg in (1, -1):
        sh.line(cx - S * xe, cy + sg * S * hn, cx + S * xe, cy + sg * S * hn, THICK)


def slot_width_dim(sh, cx, cy, S, rm, xn):
    """上面から見た図のすりわりの幅 (矢印を外側から当てる)。"""
    hn = N / 2
    xe = math.sqrt(rm * rm - hn * hn)
    for sg in (1, -1):
        sh.line(cx + S * xe + 1.0, cy + sg * S * hn, xn + 1.5, cy + sg * S * hn)
    sh.line(xn, cy - S * hn - 5.0, xn, cy + S * hn + 13.0)
    arrow(sh, xn, cy - S * hn, 0, 1)
    arrow(sh, xn, cy + S * hn, 0, -1)
    sh.text(xn - 1.0, cy + S * hn + 7.5, fmt(N), 4.5, ang=90, align="C")


def parts_table(sh, rows, cols, x0=-25.0, y0=-28.0, h=7.0):
    W = sum(w for _, w in cols)
    for i in range(len(rows) + 1):
        sh.line(x0, y0 + h * i, x0 + W, y0 + h * i, THICK if i in (0, len(rows)) else THIN)
    xs = [x0]
    for _, w in cols:
        xs.append(xs[-1] + w)
    for j, x in enumerate(xs):
        sh.line(x, y0, x, y0 + h * len(rows), THICK if j in (0, len(xs) - 1) else THIN)
    for i, row in enumerate(rows):
        for j, s in enumerate(row):
            size = 3.5
            while text_width(s, size, 0.5) > cols[j][1] - 2 and size > 2.0:
                size -= 0.1
            sh.text((xs[j] + xs[j + 1]) / 2, y0 + h * i + (h - size) / 2, s, size, align="C")


# ---------------------------------------------------------------- 組立図
def draw_assy(sh):
    S = 5.0
    R, r, rb = DK / 2, D / 2, DB / 2
    Y0 = 42.0
    gap = 30.0
    left = -(S * DK + gap + S * L + 20.0) / 2
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (中心を通る面で切った全断面。すりわりは紙面に垂直)
    #      圧入部は 1 本の線で描くので、鉄部品の外周は穴の径 (φ3.4) の位置に描く
    outer, bore = resin_outline()
    for sg in (1, -1):
        pl(sh, P, outer, sg)
        pl(sh, P, bore[:3], sg)
    draw_metal(sh, P, rb, section=True)
    draw_thread_lines(sh, P)
    sh.line(*P(-1.0, 0), *P(L + 1.0, 0), THIN, 6)
    for poly in metal_hatch_polys(rb):
        hatch_both(sh, P, poly, 45, 1.2)
    for poly in resin_hatch_polys():
        hatch_both(sh, P, poly, -45, 2.0)

    # ---- 頭部側から見た図
    for rr in (R, R - CH, rb + CB, rb, rb - CM):
        sh.circle(HX, Y0, S * rr, THICK)
    slot_view(sh, HX, Y0, S, rb)
    center_lines(sh, HX, Y0, S * R)

    # ---- 寸法
    b1 = Y0 - S * R - 8.0
    hdim(sh, P(0, 0)[0], P(KH, 0)[0], b1, P(0, -(R - CH))[1], P(KH, -(R - CH))[1], fmt(KH))
    hdim(sh, P(KH, 0)[0], P(L, 0)[0], b1, P(KH, -(R - CH))[1], P(L, -(r - CR))[1], fmt(LR))
    hdim(sh, P(0, 0)[0], P(L, 0)[0], b1 - 10.0, P(0, -(R - CH))[1], P(L, -(r - CR))[1], fmt(L))
    vdim(sh, Y0 - S * R, Y0 + S * R, HX - S * R - 8.0, HX - 1.0, HX - 1.0, f"φ{fmt(DK)}")
    leader(sh, *P(KH + 10.0, r), P(KH + 10.0, 0)[0] + 7.0, Y0 + S * r + 10.0, "#5-40 UNC")

    # ---- 部品番号 (風船)
    def balloon(tx, ty, bx, by, num):
        rbl = 4.0
        dx, dy = tx - bx, ty - by
        n = math.hypot(dx, dy)
        sh.line(bx + dx / n * rbl, by + dy / n * rbl, tx, ty)
        sh.solid([(tx + 0.6 * math.cos(a * math.pi / 6), ty + 0.6 * math.sin(a * math.pi / 6))
                  for a in range(12)])
        sh.circle(bx, by, rbl)
        sh.text(bx, by - 2.0, num, 4.0, align="C")

    balloon(*P(1.3, 1.0), P(0, 0)[0] - 8.0, Y0 + S * R + 12.0, "1")
    balloon(*P(KH + 5.0, 1.0), P(KH + 3.0, 0)[0], Y0 + S * R + 12.0, "2")

    cols = [("番号", 12), ("品名", 50), ("材質", 30), ("数量", 12), ("備考", 61)]
    parts_table(sh, [
        ["番号", "品名", "材質", "数量", "備考"],
        ["1", "鉄部品 φ3.5×1.8", "S10C相当材", "1", SURF],
        ["2", "樹脂部品 #5-40 UNC×17", "POMまたはPEEK", "1", "穴径は材質ごとに試作で決める"],
    ], cols)

    notes(sh, [
        "1. 部品1を部品2の穴に、上面が面一になるまで\n圧入する。",
        "2. 部品1をマイナスドライバーで回したとき、部品2が\n共回りし、空回りしないこと。",
        "3. 圧入しろと保持トルクは試作で確かめて決める。",
        "4. 接着剤を併用するかは試作の結果で決める\n(POM は接着しにくい)。",
        "5. 普通公差は JIS B 0405-m (中級) とする。",
    ])


# ---------------------------------------------------------------- 鉄部品
def draw_metal_sheet(sh):
    S = 10.0
    rm, hn = DM / 2, N / 2
    Y0 = 40.0
    gap = 40.0
    left = -(S * DM + gap + S * LM) / 2 - 10.0
    HX = left + S * rm
    X0 = HX + S * rm + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    draw_metal(sh, P, rm, section=False)
    sh.line(*P(-0.3, 0), *P(LM + 0.3, 0), THIN, 6)

    # ---- 上面 (すりわり側) から見た図
    sh.circle(HX, Y0, S * rm, THICK)
    sh.circle(HX, Y0, S * (rm - CM), THICK)
    slot_view(sh, HX, Y0, S, rm)
    center_lines(sh, HX, Y0, S * rm)

    # ---- 寸法
    top = Y0 + S * rm + 8.0
    yt = P(0, hn)[1]
    hdim(sh, P(0, 0)[0], P(T, 0)[0], top, yt, yt, fmt(T), outside=True)
    yb = P(0, -(rm - CM))[1]
    hdim(sh, P(0, 0)[0], P(LM, 0)[0], Y0 - S * rm - 8.0, yb, P(LM, -(rm - CM))[1], fmt(LM), outside=True)
    vdim(sh, Y0 - S * rm, Y0 + S * rm, P(LM, 0)[0] + 12.0, P(LM - CM, 0)[0], P(LM - CM, 0)[0],
         f"φ{fmt(DM)}")
    leader(sh, *P(1.1, rm), P(LM, 0)[0] + 4.0, Y0 + S * rm + 14.0, "平目ローレット", size=3.5)
    vdim(sh, Y0 - S * rm, Y0 + S * rm, HX - S * rm - 8.0, HX - 1.0, HX - 1.0, f"φ{fmt(DM)}")
    slot_width_dim(sh, HX, Y0, S, rm, HX + S * rm + 7.0)

    notes(sh, [
        "1. φ3.5 はローレット前の径。外周は全長を平目ローレット\nとし、ローレット後の外径は試作で決める。",
        "2. 指示のない面取りは C0.2 とする。",
        "3. 普通公差は JIS B 0405-m (中級) とする。",
        "4. 表面処理はニッケルめっき または 金めっきとし、\n注文ごとに指定する。",
        "5. めっきは部品2へ圧入する前に行う。",
    ], y0=-4.0)


# ---------------------------------------------------------------- 樹脂部品
def draw_resin_sheet(sh):
    S = 10.0
    R, r, rb = DK / 2, D / 2, DB / 2
    Y0 = 42.0
    gap = 24.0
    left = -(S * DK + gap + S * L) / 2 + 2.0
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (上半分を断面、下半分を外形で示す片側断面。左端が頭部側)
    outer, bore = resin_outline()
    pl(sh, P, outer)
    pl(sh, P, bore)
    pl(sh, P, [(CB, 0), (CB, rb)])                                   # 穴の中に見える面取りの稜線
    pl(sh, P, [(0, 0), (0, -(R - CH))])                               # 下: 上面
    pl(sh, P, outer[1:], -1)
    pl(sh, P, [(CH, -R), (CH, 0)])                                    # 下: 上面側の面取りの境
    pl(sh, P, [(KH - CH, -R), (KH - CH, 0)])                          # 下: 座面側の面取りの境
    pl(sh, P, [(L - CR, -r), (L - CR, 0)])                            # 下: ねじ先の面取りの境
    draw_thread_lines(sh, P)
    sh.line(*P(-0.4, 0), *P(L + 0.4, 0), THIN, 6)
    for poly in resin_hatch_polys():
        hatch(sh, [P(x, y) for x, y in poly], -45, 2.0)

    # ---- 頭部側 (上面) から見た図
    for rr in (R, R - CH, rb + CB, rb):
        sh.circle(HX, Y0, S * rr, THICK)
    center_lines(sh, HX, Y0, S * R)

    # ---- 寸法
    top = Y0 + S * R + 8.0
    hdim(sh, P(0, 0)[0], P(BD, 0)[0], top, P(0, R - CH)[1], P(BD, rb)[1], fmt(BD), outside=True)
    hdim(sh, P(0, 0)[0], P(KH, 0)[0], top + 10.0, P(0, R - CH)[1], P(KH, R - CH)[1], fmt(KH))
    b1 = Y0 - S * R - 8.0
    hdim(sh, P(KH, 0)[0], P(L, 0)[0], b1, P(KH, -(R - CH))[1], P(L, -(r - CR))[1], fmt(LR))
    hdim(sh, P(0, 0)[0], P(L, 0)[0], b1 - 10.0, P(0, -(R - CH))[1], P(L, -(r - CR))[1], fmt(L))
    vdim(sh, Y0 - S * R, Y0 + S * R, HX - S * R - 8.0, HX - 1.0, HX - 1.0, f"φ{fmt(DK)}")
    leader(sh, *P(KH + 9.0, -r), P(KH + 9.0, 0)[0] + 8.0, Y0 - S * r - 10.0 + 4.0, "#5-40 UNC-2A")
    leader(sh, *P(L - CR / 2, r - CR / 2), P(L, 0)[0] - 2.0, Y0 + S * r + 9.0, f"C{fmt(CR)}", size=3.5)
    # 穴の径 (上面から見た図に引出線)
    a = math.radians(45)
    leader(sh, HX + S * rb * math.cos(a), Y0 + S * rb * math.sin(a),
           HX + S * R + 6.0, Y0 + S * R + 8.0, f"φ{fmt(DB)}", sub="+0.05/0")

    notes(sh, [
        "1. ねじはユニファイ並目ねじ #5-40 UNC-2A とし、座面まで\n切る。座面側の不完全ねじ部は 2 山以下とする。",
        "2. φ3.4 の穴は部品1 (φ3.5、平目ローレット) を圧入する\n穴。穴径は材質ごとに試作で調整する。",
        "3. 穴の底は平らとし、隅の丸みは R0.2 以下とする。",
        "4. 指示のない面取りは C0.2 とする。",
        "5. 普通公差は JIS B 0405-m (中級) とする。",
        "6. ねじ山と穴にバリ、削りくずを残さないこと。",
        "7. 材質は POM または PEEK とし、注文ごとに指定する。",
    ], y0=-2.0)


def main(out):
    for key, fn in (("assy", draw_assy), ("metal", draw_metal_sheet), ("resin", draw_resin_sheet)):
        s = SHEETS[key]
        sh = Sheet()
        load_template(sh)
        fill_title(sh, s["title"])
        fn(sh)
        path = os.path.join(out, s["file"])
        render(sh, path, s["title"]["品名"])
        print(path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
