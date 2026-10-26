# -*- coding: utf-8 -*-
"""CAP 皿頭加工 M12×25 の切削図を、株式会社カネコの A4 図面書式で PDF に出力する。

素材の六角穴付きボルト M12×15 全ねじ (JIS B 1176、表の基準寸法: 頭部径 18、頭部高さ 12、六角穴 10) を
得意先図面 (サンコーインダストリー(株) 「CAP皿頭加工」 M12X25) の形に削る。加工前の外形を二点鎖線、
完成品の外形を太線で重ねて描き、削る部分を灰色で塗る。
完成品: 頭部は φ15.65 から φ10 まで長さ 10.5 の円すい (30°)、首下 φ10 × 3、ねじ部 M12 × 11.5、全長 25。
素材の全長 27 (12 + 15) との差 2 は頭頂面で削る (ねじ先は素材のまま) と解釈した。
ねじ部の首側の面取りは図面に「C面」とだけあるので、山の径から首下 φ10 までの 45° (C1) とした。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import (Sheet, arrow, hdim, leader, load_template, fill_title,  # noqa: E402
                    render, text_width)

# 素材: 六角穴付きボルト M12×15 全ねじ (JIS B 1176 の基準寸法)
SRC = {
    "dk": 18.0,      # 頭部径
    "k": 12.0,       # 頭部高さ
    "l": 15.0,       # 呼び長さ
    "s": 10.0,       # 六角穴の二面幅
    "t": 6.0,        # 六角穴の深さ (表の最小値。図の線用)
    "v": 0.8,        # 頭部上面の角の面取り (図の線用)
    "ce": 1.0,       # ねじ先の面取り (図の線用)
}
# 完成品 (得意先図面)
B = {
    "cut": 2.0,      # 頭頂面の削り代 (素材の全長 27 - 完成品の全長 25)
    "dt": 15.65,     # 皿頭の上面の径
    "hc": 10.5,      # 皿頭の長さ
    "ang": 30.0,     # 皿頭の角度 (参考)
    "dn": 10.0,      # 首下の径
    "ln": 3.0,       # 首下の長さ
    "lt": 11.5,      # ねじ部の長さ
    "d": 12.0,       # ねじの呼び径
    "d1": 10.106,    # おねじの谷の径 (図の線用)
    "cn": 1.0,       # ねじ部の首側の面取り
}
TITLE = {"品番": "", "図番": "", "得意先": "サンコーインダストリー(株)", "品名": "CAP皿頭加工 M12×25",
         "尺度": "3/1", "材質": "SCM", "表面処理": "生地"}
FILE = "CAP皿頭加工_M12x25.pdf"
SCALE = 3.0


def fmt(v):
    return f"{v:g}"


def hdim_fit(sh, x1, x2, y, f1, f2, label, size=4.5):
    """hdim と同じ。数値が寸法線の間に収まらないときは、矢印を外側から当て、数値を左の外側に書く。"""
    w = text_width(label, size, 0.5)
    if w + 2.0 <= x2 - x1:
        hdim(sh, x1, x2, y, f1, f2, label, size)
        return
    hdim(sh, x1, x2, y, f1, f2, "", size, outside=True)
    sh.line(x1 - w - 2.0, y, x1, y)
    sh.text(x1 - 1.5, y + 1.0, label, size, align="R")


def vdim_left(sh, y1, y2, x, fx, label, size=4.5):
    """直径の縦の寸法。寸法線は x、補助線は fx から引き、数値は寸法線の左に縦書き。"""
    for yy in (y1, y2):
        sh.line(fx - 1.0, yy, x - 1.5, yy)
    sh.line(x, y1, x, y2)
    arrow(sh, x, y1, 0, -1)
    arrow(sh, x, y2, 0, 1)
    sh.text(x - 1.0, (y1 + y2) / 2, label, size, ang=90, align="C")


def draw(sh):
    S = SCALE
    c = B["cut"]
    L0 = SRC["k"] + SRC["l"]                       # 素材の全長 27
    x_n = c + B["hc"]                              # 皿頭の終わり (首下の始まり)
    x_t = x_n + B["ln"]                            # 首下の終わり (ねじ部の始まり)
    L = x_t + B["lt"]                              # 完成品の先端 (素材の頭頂面から)
    rt, rn, rd, r1 = B["dt"] / 2, B["dn"] / 2, B["d"] / 2, B["d1"] / 2
    rk, k, v, ce, cn = SRC["dk"] / 2, SRC["k"], SRC["v"], SRC["ce"], B["cn"]
    e = SRC["s"] / math.cos(math.radians(30))      # 六角穴の対角距離
    Y0 = 30.0
    gap = 45.0
    left = -(S * SRC["dk"] + gap + S * L0) / 2 - 5.0
    HX = left + S * rk
    X0 = HX + S * rk + gap

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 削る部分 (素材の外形を灰色で塗り、完成品の外形を白で塗り戻す)
    up0 = [(0, rk - v), (v, rk), (k, rk), (k, rd), (L0 - ce, rd), (L0, rd - ce)]
    up1 = [(c, rt), (x_n, rn), (x_t, rn), (x_t + cn, rd), (L - ce, rd), (L, rd - ce)]
    for pts, g in ((up0, 0.82), (up1, 1.0)):
        poly = [P(x, y) for x, y in pts] + [P(x, -y) for x, y in reversed(pts)]
        sh.fill(poly, g)

    # ---- 素材の外形 (二点鎖線。完成品と重なる部分は完成品の太線で描く)
    for sg in (1, -1):
        sh.line(*P(0, sg * (rk - v)), *P(v, sg * rk), 1, 7)
        sh.line(*P(v, sg * rk), *P(k, sg * rk), 1, 7)               # 頭部の外周
        sh.line(*P(k, sg * rk), *P(k, sg * rd), 1, 7)               # 座面
        sh.line(*P(k, sg * rd), *P(x_t + cn, sg * rd), 1, 7)        # 首下側のねじ山
        if L < L0:
            sh.line(*P(L - ce, sg * rd), *P(L0 - ce, sg * rd), 1, 7)
            sh.line(*P(L0 - ce, sg * rd), *P(L0, sg * (rd - ce)), 1, 7)
    sh.line(*P(0, -(rk - v)), *P(0, rk - v), 1, 7)                  # 頭頂面
    if L < L0:
        sh.line(*P(L0, -(rd - ce)), *P(L0, rd - ce), 1, 7)

    # ---- 完成品の外形 (太線)
    for sg in (1, -1):
        sh.line(*P(c, sg * rt), *P(x_n, sg * rn), 6)                # 皿頭の円すい
        sh.line(*P(x_n, sg * rn), *P(x_t, sg * rn), 6)              # 首下
        sh.line(*P(x_t, sg * rn), *P(x_t + cn, sg * rd), 6)         # ねじ部の首側の面取り
        sh.line(*P(x_t + cn, sg * rd), *P(L - ce, sg * rd), 6)      # ねじの山の径
        sh.line(*P(L - ce, sg * rd), *P(L, sg * (rd - ce)), 6)      # ねじ先の面取り
        sh.line(*P(x_t + cn, sg * r1), *P(L, sg * r1), 1)           # ねじの谷の径 (細線)
    sh.line(*P(c, -rt), *P(c, rt), 6)                                # 頭頂面 (削ったあと)
    sh.line(*P(x_n, -rn), *P(x_n, rn), 6)                            # 皿頭と首下の境
    sh.line(*P(x_t + cn, -rd), *P(x_t + cn, rd), 6)                  # 面取りとねじ山の境
    sh.line(*P(L - ce, -rd), *P(L - ce, rd), 6)
    sh.line(*P(L, -(rd - ce)), *P(L, rd - ce), 6)                    # 先端面
    # 六角穴 (素材のまま。かくれ線)
    tp = SRC["t"] + (e / 2) / math.tan(math.radians(59))            # ドリル先 118°
    for yy in (e / 2, e / 4, -e / 4, -e / 2):
        sh.line(*P(c, yy), *P(SRC["t"], yy), 1, 2)
        sh.line(*P(SRC["t"], yy), *P(tp, 0), 1, 2)
    sh.line(*P(-1.0, 0), *P(L0 + 1.0, 0), 1, 6)                      # 中心線

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * rk, 1, 7)                                  # 素材の頭部
    sh.circle(HX, Y0, S * rt, 6)                                     # 削ったあとの頭頂面
    R6 = S * e / 2
    pts = [(HX + R6 * math.cos(math.radians(90 + 60 * i)), Y0 + R6 * math.sin(math.radians(90 + 60 * i)))
           for i in range(7)]
    for p, q in zip(pts, pts[1:]):
        sh.line(*p, *q, 6)
    sh.line(HX - S * rk - 3, Y0, HX + S * rk + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * rk - 3, HX, Y0 + S * rk + 3, 1, 6)
    xs = S * SRC["s"] / 2
    hdim(sh, HX - xs, HX + xs, Y0 - S * rk - 8.0, Y0 - S * e / 4, Y0 - S * e / 4, fmt(SRC["s"]))
    a = math.radians(135)
    leader(sh, HX + S * rk * math.cos(a), Y0 + S * rk * math.sin(a), HX - S * rk + 2.0,
           Y0 + S * rk + 6.0, f"(φ{fmt(SRC['dk'])})", side="L")

    # ---- 寸法 (完成品は下、素材は上に括弧付きで)
    bot = Y0 - S * rk - 7.0
    hdim(sh, P(c, 0)[0], P(x_n, 0)[0], bot, P(c, -rt)[1], P(x_n, -rn)[1], fmt(B["hc"]))
    hdim_fit(sh, P(x_n, 0)[0], P(x_t, 0)[0], bot, P(x_n, -rn)[1], P(x_t, -rn)[1], fmt(B["ln"]))
    hdim(sh, P(x_t, 0)[0], P(L, 0)[0], bot, P(x_t, -rn)[1], P(L, -(rd - ce))[1], fmt(B["lt"]))
    hdim(sh, P(c, 0)[0], P(L, 0)[0], bot - 10.0, P(c, -rt)[1], P(L, -(rd - ce))[1], fmt(L - c))
    top = Y0 + S * rk + 7.0
    hdim_fit(sh, P(0, 0)[0], P(c, 0)[0], top, P(0, rk - v)[1], P(c, rt)[1], fmt(c))
    hdim(sh, P(0, 0)[0], P(k, 0)[0], top + 9.0, P(0, rk - v)[1], P(k, rk)[1], f"({fmt(k)})")
    hdim(sh, P(k, 0)[0], P(L0, 0)[0], top + 9.0, P(k, rk)[1], P(L0, rd - ce)[1], f"({fmt(SRC['l'])})")
    hdim(sh, P(0, 0)[0], P(L0, 0)[0], top + 18.0, P(0, rk - v)[1], P(L0, rd - ce)[1], f"({fmt(L0)})")
    # 皿頭の上面の径
    vdim_left(sh, P(0, -rt)[1], P(0, rt)[1], P(0, 0)[0] - 17.0, P(c, 0)[0], f"φ{fmt(B['dt'])}")
    # 皿頭の角度 (円すいの母線を左へ延ばし、頂点を中心に円弧を描く)
    th = math.atan((rt - rn) / B["hc"])
    xa = x_n + rn / math.tan(th)                                     # 円すいの頂点
    ra = xa + 3.0                                                    # 円弧の半径 (実寸)
    for sg in (1, -1):
        sh.line(*P(c - 1.0, sg * (rt + math.tan(th) * 1.0)),
                *P(xa - (ra + 1.0) * math.cos(th), sg * (ra + 1.0) * math.sin(th)))
    ax, ay = P(xa, 0)
    deg = math.degrees(th)
    sh.arc(ax, ay, S * ra, 180 - deg, 180 + deg)
    for sg in (1, -1):
        px, py = ax - S * ra * math.cos(th), ay + sg * S * ra * math.sin(th)
        arrow(sh, px, py, -math.sin(th), -sg * math.cos(th))
    sh.text(ax - S * ra - 1.5, ay, f"({fmt(B['ang'])}°)", 4.5, ang=90, align="C")
    # 首下の径、ねじ、面取り
    leader(sh, *P((x_n + x_t) / 2, rn), P(x_n, 0)[0] + 2.0, Y0 + S * rk + 2.0, f"φ{fmt(B['dn'])}", side="L")
    leader(sh, *P(L - 5.0, rd), P(L, 0)[0] - 4.0, Y0 + S * rk + 2.0, f"M{fmt(B['d'])}", sub="(素材のまま)")
    leader(sh, *P(x_t + cn / 2, -(rn + cn / 2)), P(x_t + cn, 0)[0] + 3.0, Y0 - S * rd - 5.0, f"C{fmt(cn)}")

    # ---- 凡例
    lx, ly = 95.0, -8.0
    sh.fill([(lx, ly), (lx + 14, ly), (lx + 14, ly + 4), (lx, ly + 4)], 0.82)
    sh.text(lx + 16, ly + 0.4, "削る部分", 3.5)
    sh.line(lx, ly - 5, lx + 14, ly - 5, 1, 7)
    sh.text(lx + 16, ly - 6.6, "素材の外形", 3.5)
    sh.line(lx, ly - 11, lx + 14, ly - 11, 6)
    sh.text(lx + 16, ly - 12.6, "完成品の外形", 3.5)

    # ---- 注記
    sh.text(-130.0, -22.0, "注記", 4.0)
    notes = [
        "1. 素材は六角穴付きボルト M12×15 全ねじ (JIS B 1176)。",
        "   二点鎖線と ( ) 内の寸法は素材の基準寸法 (参考)。",
        f"2. 頭頂面を {fmt(c)} 削り、頭部を皿頭 (円すい)、首下を φ{fmt(B['dn'])} に削る。ねじ先と六角穴は素材のまま。",
        "3. 切削加工部の指定外公差は JIS B 0405 中級とする。",
        "4. 各角稜部の有害なバリは除去のこと (糸面取り可)。",
    ]
    for i, s in enumerate(notes):
        sh.text(-126.0, -28.0 - 5.5 * i, s, 3.3)


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw(sh)
    render(sh, os.path.join(out, FILE), TITLE["品名"])
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
