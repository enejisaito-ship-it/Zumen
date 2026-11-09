# -*- coding: utf-8 -*-
"""金属頭部と樹脂ねじ軸を圧入して一体にするポールピースねじ (エレキギターのピックアップ用) の図面を、
株式会社カネコの A4 図面書式で PDF に出力する。組立図、金属頭部、樹脂ねじ軸の 3 枚を 1 本のスクリプトで出す。

元の資料: 池田様からのお問合せメールの「仕様案2: 金属 (頭部) × 樹脂 (ネジ軸部) の一体型ハイブリッド仕様」。
メールの値:
- 頭部: マイナス溝付きフィリスター頭、外径 約5.0、厚み 約2.5。材質 1010 スチール相当 (S10C / SWCH10)。
  表面処理 ニッケルめっき または 金めっき。磁性が必要なのでステンレスは不可。
- 先端結合ピン: φ1.5 × 長さ 2.0〜2.5。金属部単体の全長 約4.5〜5.0。回り止めにローレットか D カットの提案を希望。
- ねじ軸: POM (デルリン) または PEEK。#5-40 または M3。ねじ部長さ 約13.5〜15.5。組立後の全長 約16.0〜18.0。
メールの範囲の中から、こちらで決めた値 (要確認):
- ねじは M3 (並目 0.5) とした。ねじ軸の長さ 14.5、組立後の全長 17.0。樹脂は POM とした。
- ピンは φ1.5 × 2.5 (金属部の全長 5.0)。回り止めは平目ローレットとし、ピンを丸穴へ圧入する。
- 樹脂の穴は φ1.4 (圧入しろ 0.1)、深さ 3.0 (ピンより 0.5 深くして、底に空気と削りくずの逃げを取る)。
- フィリスター頭の上面は R8 の丸み (中央の高さ 0.4)、すりわりは幅 0.8 × 深さ 1.0。規格値は確かめていない。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width, vdim)

# ---- 金属頭部 (部品 1)
DK = 5.0        # 頭部の外径
KH = 2.5        # 頭部の厚さ (上面の丸みの頂点から座面まで)
RC = 8.0        # 頭部上面の丸みの半径
N = 0.8         # すりわりの幅
T = 1.0         # すりわりの深さ
CH = 0.2        # 頭部の座面側の角の面取り
DP = 1.5        # ピンの径 (ローレット前)
LP = 2.5        # ピンの長さ
CP = 0.2        # ピン先の面取り
KN0 = 0.3       # ローレットを掛けない座面側の長さ
# ---- 樹脂ねじ軸 (部品 2)
D = 3.0         # ねじの呼び径 M3
P_ = 0.5        # ピッチ (並目)
D1 = 2.39       # おねじの谷の径 (図の線用)
LR = 14.5       # ねじ軸の長さ
CR = 0.3        # 両端の面取り (谷の径まで)
DH = 1.4        # ピンを圧入する穴の径
HD = 3.0        # 穴の深さ (円筒部)
CH2 = 0.2       # 穴の入口の面取り
CZ = (DH / 2) / math.tan(math.radians(59))   # きりの先端 (118°) の長さ

CUSTOMER = "池田様"
SHEETS = {
    "assy": {"title": {"品番": "", "図番": "", "得意先": CUSTOMER, "品名": "ポールピースねじ組立 M3×17",
                       "尺度": "5/1", "材質": ""},
             "file": "ポールピースねじ組立_M3x17.pdf"},
    "metal": {"title": {"品番": "", "図番": "", "得意先": CUSTOMER, "品名": "ポールピースねじ 金属頭部",
                        "尺度": "10/1", "材質": "S10C", "表面処理": "ニッケルめっき"},
              "file": "ポールピースねじ_金属頭部_φ5x5.pdf"},
    "resin": {"title": {"品番": "", "図番": "", "得意先": CUSTOMER, "品名": "ポールピースねじ 樹脂ねじ軸 M3×14.5",
                        "尺度": "10/1", "材質": "POM"},
              "file": "ポールピースねじ_樹脂ねじ軸_M3x14.5.pdf"},
}
THICK, THIN = 6, 1


def fmt(v):
    return f"{v:g}"


def crown_x(y):
    """頭部上面の丸みの、軸方向の位置 (頂点が 0)。"""
    return RC - math.sqrt(RC * RC - y * y)


def pl(sh, P, pts, sg=1, pen=THICK, style=1):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        sh.line(*P(x1, sg * y1), *P(x2, sg * y2), pen, style)


def hatch(sh, poly, ang, pitch):
    """凸多角形 poly (用紙座標) の中に、水平から ang 度の細線を間隔 pitch で引く。
    線の位置は用紙全体で揃えるので、隣り合う多角形に分けても線がつながる。"""
    a = math.radians(ang)
    nx, ny = -math.sin(a), math.cos(a)
    ks = [x * nx + y * ny for x, y in poly]
    k = (math.floor(min(ks) / pitch) + 0.5) * pitch
    if k <= min(ks):
        k += pitch
    while k < max(ks):
        pts = []
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            u1, u2 = x1 * nx + y1 * ny - k, x2 * nx + y2 * ny - k
            if u1 == u2 or u1 * u2 > 0:
                continue
            t = u1 / (u1 - u2)
            pts.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        if len(pts) >= 2:
            pts.sort()
            sh.line(*pts[0], *pts[-1])
        k += pitch


def hatch_both(sh, P, poly, ang, pitch):
    """中心線の上下に、局所座標の多角形を写してハッチングする。"""
    for sg in (1, -1):
        hatch(sh, [P(x, sg * y) for x, y in poly], ang, pitch)


def center_lines(sh, cx, cy, r):
    sh.line(cx - r - 3, cy, cx + r + 3, cy, THIN, 6)
    sh.line(cx, cy - r - 3, cx, cy + r + 3, THIN, 6)


def notes(sh, lines, y0=0.0, size=3.5):
    """注記。書式の訂正欄 (y = -54 より下) にかからないよう、図と表題欄の間の左側に書く。"""
    sh.text(-130.0, y0, "注記", 4.0)
    y = y0 - 7.0
    for s in lines:
        for j, part in enumerate(s.split("\n")):
            sh.text(-126.0 + (4.0 if j else 0.0), y, part, size)
            y -= size + 2.0


# ---------------------------------------------------------------- 部品の形
def metal_profile():
    """金属頭部の上半分の外形 (すりわりの縁から外周、座面、ピン先まで)。"""
    R, rp, hn = DK / 2, DP / 2, N / 2
    pts = [(crown_x(hn + (R - hn) * i / 40), hn + (R - hn) * i / 40) for i in range(41)]
    pts += [(KH - CH, R), (KH, R - CH), (KH, rp), (KH + LP - CP, rp), (KH + LP, rp - CP)]
    return pts


def draw_metal(sh, P, section):
    R, rp, hn = DK / 2, DP / 2, N / 2
    prof = metal_profile()
    for sg in (1, -1):
        pl(sh, P, prof, sg)
        pl(sh, P, [(crown_x(hn), hn), (T, hn)], sg)                  # すりわりの側面
    pl(sh, P, [(T, -hn), (T, hn)])                                    # すりわりの底
    pl(sh, P, [(KH + LP, -(rp - CP)), (KH + LP, rp - CP)])            # ピンの先端面
    if section:
        return
    xe = crown_x(R)
    for sg in (1, -1):
        pl(sh, P, [(xe, hn), (xe, R)], sg)                            # 上面の丸みと外周の境
    pl(sh, P, [(KH - CH, -R), (KH - CH, R)])                          # 座面側の面取りの境
    # 平目ローレット (軸に平行な細線)
    for y in (-0.6, -0.4, -0.2, 0.2, 0.4, 0.6):
        pl(sh, P, [(KH + KN0, y), (KH + LP - CP, y)], pen=THIN)


def metal_hatch_polys():
    R, rp, hn = DK / 2, DP / 2, N / 2
    head = [(crown_x(hn + (R - hn) * i / 40), hn + (R - hn) * i / 40) for i in range(41)]
    head += [(KH - CH, R), (KH, R - CH), (KH, hn)]
    under_slot = [(T, 0), (KH, 0), (KH, hn), (T, hn)]
    pin = [(KH, 0), (KH + LP, 0), (KH + LP, rp - CP), (KH + LP - CP, rp), (KH, rp)]
    return [head, under_slot, pin]


def head_view(sh, cx, cy, S):
    """頭部側から見た図 (すりわりは横向き)。"""
    R, hn = DK / 2, N / 2
    sh.circle(cx, cy, S * R, THICK)
    xe = math.sqrt(R * R - hn * hn)
    for sg in (1, -1):
        sh.line(cx - S * xe, cy + sg * S * hn, cx + S * xe, cy + sg * S * hn, THICK)
    center_lines(sh, cx, cy, S * R)


# ---------------------------------------------------------------- 組立図
def draw_assy(sh):
    S = 5.0
    R, rp, r, r1 = DK / 2, DP / 2, D / 2, D1 / 2
    L = KH + LR
    Y0 = 42.0
    gap = 30.0
    left = -(S * DK + gap + S * L + 20.0) / 2
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    def Q(u, y):                     # 樹脂ねじ軸の局所座標 (座面からの距離)
        return P(KH + u, y)

    # ---- 正面図 (中心を通る面で切った全断面。すりわりは紙面に垂直)
    draw_metal(sh, P, section=True)
    for sg in (1, -1):
        pl(sh, Q, [(0, 1.2), (CR, r), (LR - CR, r), (LR, r - CR)], sg)         # 外形 (ねじの山の径)
        pl(sh, Q, [(0, r1), (LR, r1)], sg, THIN)                                # ねじの谷の径 (細線)
        pl(sh, Q, [(0, DH / 2 + CH2), (CH2 - 0.05, rp)], sg)                    # 穴の入口の面取り
        pl(sh, Q, [(LP - CP, rp), (LP - CP, DH / 2), (HD, DH / 2), (HD + CZ, 0)], sg)  # 穴の残り (空間)
    pl(sh, Q, [(LR, -(r - CR)), (LR, r - CR)])                                  # 先端面
    sh.line(*P(-1.0, 0), *P(L + 1.0, 0), THIN, 6)
    # ハッチング: 金属は 45°、樹脂は -45° で間隔を変える
    for poly in metal_hatch_polys():
        hatch_both(sh, P, poly, 45, 1.2)
    resin = [
        [(0, DH / 2 + CH2), (CH2 - 0.05, rp), (LP - CP, rp), (LP - CP, r), (CR, r), (0, 1.2)],
        [(LP - CP, DH / 2), (HD, DH / 2), (HD, r), (LP - CP, r)],
        [(HD, DH / 2), (HD + CZ, 0), (LR, 0), (LR, r - CR), (LR - CR, r), (HD, r)],
    ]
    for poly in resin:
        hatch_both(sh, Q, poly, -45, 2.0)

    # ---- 頭部側から見た図
    head_view(sh, HX, Y0, S)

    # ---- 寸法
    b1 = Y0 - S * R - 8.0
    hdim(sh, P(0, 0)[0], P(KH, 0)[0], b1, P(0, -N / 2)[1], P(KH, -R + CH)[1], fmt(KH))
    hdim(sh, P(KH, 0)[0], P(L, 0)[0], b1, P(KH, -R + CH)[1], P(L, -(r - CR))[1], fmt(LR))
    hdim(sh, P(0, 0)[0], P(L, 0)[0], b1 - 10.0, P(0, -N / 2)[1], P(L, -(r - CR))[1], fmt(L))
    vdim(sh, Y0 - S * R, Y0 + S * R, HX - S * R - 8.0, HX - 1.0, HX - 1.0, f"φ{fmt(DK)}")
    leader(sh, *Q(12.0, r), Q(12.0, 0)[0] + 7.0, Y0 + S * r + 10.0, f"M{fmt(D)}")

    # ---- 部品番号 (風船)
    def balloon(tx, ty, bx, by, num):
        rb = 4.0
        dx, dy = tx - bx, ty - by
        n = math.hypot(dx, dy)
        sh.line(bx + dx / n * rb, by + dy / n * rb, tx, ty)
        sh.solid([(tx + 0.6 * math.cos(a * math.pi / 6), ty + 0.6 * math.sin(a * math.pi / 6))
                  for a in range(12)])
        sh.circle(bx, by, rb)
        sh.text(bx, by - 2.0, num, 4.0, align="C")

    balloon(*P(1.7, 1.4), P(0, 0)[0] - 6.0, Y0 + S * R + 12.0, "1")
    balloon(*Q(7.0, 1.0), Q(5.0, 0)[0], Y0 + S * R + 12.0, "2")

    # ---- 部品欄 (表題欄の上。下から 見出し、1、2 の順)
    cols = [("番号", 12), ("品名", 38), ("材質", 30), ("数量", 12), ("備考", 73)]
    rows = [
        ["番号", "品名", "材質", "数量", "備考"],
        ["1", "金属頭部", "S10C", "1", "ニッケルめっき (または金めっき)"],
        ["2", "樹脂ねじ軸 M3×14.5", "POM", "1", "PEEK にする場合は別途指示"],
    ]
    x0, y0, h = -25.0, -28.0, 7.0
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

    notes(sh, [
        "1. 部品1のピンを部品2の穴に圧入して一体とする。",
        "2. 部品1をマイナスドライバーで回したとき、部品2が\n共回りし、空回りしないこと。",
        "3. 圧入しろと保持トルクは試作で確かめて決める。",
        "4. 接着剤を併用するかは試作の結果で決める\n(POM は接着しにくい)。",
        "5. 普通公差は JIS B 0405-m (中級) とする。",
    ])


# ---------------------------------------------------------------- 金属頭部
def draw_metal_sheet(sh):
    S = 10.0
    R, rp, hn = DK / 2, DP / 2, N / 2
    L = KH + LP
    Y0 = 41.0
    gap = 32.0
    left = -(S * DK + gap + S * L + 30.0) / 2 + 8.0
    HX = left + S * R
    X0 = HX + S * R + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    draw_metal(sh, P, section=False)
    sh.line(*P(-0.3, 0), *P(L + 0.3, 0), THIN, 6)
    head_view(sh, HX, Y0, S)

    # ---- 寸法
    top = Y0 + S * R + 8.0
    yt = P(0, hn)[1]
    hdim(sh, P(0, 0)[0], P(T, 0)[0], top, yt, yt, fmt(T))
    hdim(sh, P(0, 0)[0], P(KH, 0)[0], top + 10.0, yt, P(KH, R - CH)[1], fmt(KH))
    yb = P(0, -hn)[1]
    hdim(sh, P(KH, 0)[0], P(L, 0)[0], Y0 - S * rp - 9.0, P(KH, -rp)[1], P(L, -(rp - CP))[1], fmt(LP))
    hdim(sh, P(0, 0)[0], P(L, 0)[0], Y0 - S * R - 12.0, yb, P(L, -(rp - CP))[1], fmt(L))
    vdim(sh, P(0, -rp)[1], P(0, rp)[1], P(L, 0)[0] + 10.0, P(L - CP, 0)[0], P(L - CP, 0)[0],
         f"φ{fmt(DP)}")
    # 上面の丸み R8 (矢印を外側から当てる)
    ya = 1.8
    xa = crown_x(ya)
    ux, uy = xa - RC, ya
    n = math.hypot(ux, uy)
    tx, ty = P(xa, ya)
    leader(sh, tx, ty, tx + ux / n * 12.0, ty + uy / n * 12.0, f"R{fmt(RC)}", side="L")
    leader(sh, *P(KH + 1.2, rp), P(L, 0)[0] - 2.0, Y0 + S * rp + 9.0, "平目ローレット", size=3.5)
    # 頭部側から見た図: 外径 (左) とすりわりの幅 (右、矢印を外側から当てる)
    vdim(sh, Y0 - S * R, Y0 + S * R, HX - S * R - 8.0, HX - 1.0, HX - 1.0, f"φ{fmt(DK)}")
    xe = math.sqrt(R * R - hn * hn)
    xn = HX + S * R + 7.0
    for sg in (1, -1):
        sh.line(HX + S * xe + 1.0, Y0 + sg * S * hn, xn + 1.5, Y0 + sg * S * hn)
    sh.line(xn, Y0 - S * hn - 5.0, xn, Y0 + S * hn + 13.0)
    arrow(sh, xn, Y0 - S * hn, 0, 1)
    arrow(sh, xn, Y0 + S * hn, 0, -1)
    sh.text(xn - 1.0, Y0 + S * hn + 7.5, fmt(N), 4.5, ang=90, align="C")

    notes(sh, [
        "1. 普通公差は JIS B 0405-m (中級) とする。",
        "2. 指示のない面取りは C0.2 とする。",
        "3. ピンの根元の隅は R0.1 以下とする\n(座面を部品2の端面に密着させるため)。",
        f"4. ピンは座面から {fmt(KN0)} を除き、先端まで\n平目ローレットとする。ローレット後の外径は\n試作で決める。",
        "5. 金めっきにする場合は別途指示する。",
        "6. 磁性が必要なので、ステンレスに替えないこと。",
    ])


# ---------------------------------------------------------------- 樹脂ねじ軸
def draw_resin_sheet(sh):
    S = 10.0
    r, r1, rh = D / 2, D1 / 2, DH / 2
    Y0 = 40.0
    gap = 30.0
    left = -(S * D + gap + S * LR + 20.0) / 2
    HX = left + S * r
    X0 = HX + S * r + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (上半分を断面、下半分を外形で示す片側断面。左端が頭部側)
    pl(sh, P, [(0, r - CR), (0, rh + CH2), (CH2, rh), (HD, rh), (HD + CZ, 0)])     # 上: 断面の外形
    pl(sh, P, [(CH2, 0), (CH2, rh)])                                               # 穴の中に見える稜線
    pl(sh, P, [(HD, 0), (HD, rh)])
    pl(sh, P, [(0, 0), (0, -(r - CR))])                                            # 下: 端面
    for sg in (1, -1):
        pl(sh, P, [(0, r - CR), (CR, r), (LR - CR, r), (LR, r - CR)], sg)
        pl(sh, P, [(0, r1), (LR, r1)], sg, THIN)
    pl(sh, P, [(LR, -(r - CR)), (LR, r - CR)])
    sh.line(*P(-0.5, 0), *P(LR + 0.5, 0), THIN, 6)
    for poly in ([(0, rh + CH2), (CH2, rh), (HD, rh), (HD, r), (CR, r), (0, r - CR)],
                 [(HD, rh), (HD + CZ, 0), (LR, 0), (LR, r - CR), (LR - CR, r), (HD, r)]):
        hatch(sh, [P(x, y) for x, y in poly], -45, 2.0)

    # ---- 頭部側 (左端) から見た図
    sh.circle(HX, Y0, S * r, THICK)
    sh.arc(HX, Y0, S * r1, 90, 360, THIN)            # ねじの谷 (3/4 の円)
    sh.circle(HX, Y0, S * (rh + CH2), THICK)
    sh.circle(HX, Y0, S * rh, THICK)
    center_lines(sh, HX, Y0, S * r)

    # ---- 寸法
    top = Y0 + S * r + 8.0
    hdim(sh, P(0, 0)[0], P(HD, 0)[0], top, P(0, r - CR)[1], P(HD, rh)[1], fmt(HD))
    bot = Y0 - S * r - 16.0
    hdim(sh, P(0, 0)[0], P(LR, 0)[0], bot, P(0, -(r - CR))[1], P(LR, -(r - CR))[1], fmt(LR))
    low = Y0 - S * r - 6.0
    leader(sh, *P(CR / 2, -(r - CR / 2)), P(0, 0)[0] - 4.0, low, f"C{fmt(CR)}", size=3.5, side="L")
    leader(sh, *P(LR - CR / 2, -(r - CR / 2)), P(LR, 0)[0] + 4.0, low, f"C{fmt(CR)}", size=3.5)
    leader(sh, *P(CH2 / 2, rh + CH2 / 2), P(0, 0)[0] - 6.0, top + 4.0, f"C{fmt(CH2)}", size=3.5, side="L")
    leader(sh, *P(9.0, -r), P(9.0, 0)[0] + 8.0, low, f"M{fmt(D)}")
    a = math.radians(135)
    leader(sh, HX + S * rh * math.cos(a), Y0 + S * rh * math.sin(a),
           HX - S * r - 2.0, Y0 + S * r + 8.0, f"φ{fmt(DH)}", side="L", sub="+0.05/0")

    notes(sh, [
        "1. ねじはメートル並目ねじ M3×0.5 とし、全長に切る。",
        "2. φ1.4 の穴は部品1のピン (φ1.5、平目ローレット)\nを圧入する穴。穴径は試作で調整する。",
        "3. 穴の底はきり先 (118°) のままでよい。",
        "4. 普通公差は JIS B 0405-m (中級) とする。",
        "5. ねじ山と穴にバリ、削りくずを残さないこと。",
    ])


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
