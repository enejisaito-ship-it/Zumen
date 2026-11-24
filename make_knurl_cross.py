# -*- coding: utf-8 -*-
"""十字穴付きローレットねじ M2.5×10 の図面を、株式会社カネコの A4 図面書式で PDF に出力する。

元の資料:
- 依頼メール (管理番号 TEMP-XYX759): 摂津金属工業のビスセット BP「FRP-2510BS-BP」の
  パネル固定用ビス 2.5B を元に、頭部のすりわりを十字穴に替えたい。材質は鉄または黄銅、
  表面処理はニッケルクロムめっき。
- 同社カタログ PDF (www.settsu.co.jp/products/pdf/8578 の 20 ページ「外観寸法図」):
  頭部 φ7、頭部の長さ (ローレット部 + 段) 7.5、ねじのない軸部 4、ねじ部 6、M2.5、すりわり幅 1。
- 依頼者の回答: 先端はとがり先 90°、ねじのない軸部は転造前の径、段の外径・高さの指定なし、
  ナイロンワッシャー不要、首下は 11〜12 程度でもよい、頭部径は φ6 でもよい。
カタログ図 (立体図) から読んだ値 (寸法の記入がないので要確認):
- ローレット部の長さ 5.5、段の長さ 2、段の外径 φ5.5。ローレット部の両端の角は C0.3。
- 十字穴の番号は No.1 (M2.5 のなべ小ねじと同じとした。JIS 本文は未確認)。形状は略図。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, hdim, leader, load_template, fill_title, render, vdim  # noqa: E402
from make_knurl_screw import fmt, hatch  # noqa: E402
from make_polepiece import notes  # noqa: E402

DK = 7.0        # 頭部 (ローレット部) の径
LK = 5.5        # ローレット部の長さ (カタログ図から読んだ値)
CK = 0.3        # ローレット部の両端の面取り
DC = 5.5        # 段の外径 (指定なし。カタログ図から読んだ値)
LH = 7.5        # 頭部の長さ (ローレット部 + 段)
DS = 2.2        # ねじのない軸部の径 (転造前の径。参考)
LS = 4.0        # ねじのない軸部の長さ
D = 2.5         # ねじの呼び径
D1 = 2.013      # おねじの谷の径 (図の線用)
LT = 6.0        # ねじ部の長さ (とがり先を含む)
L = LH + LS + LT
S = 5.0         # 尺度 5/1
TITLE = {"品番": "", "図番": "", "得意先": "", "品名": "十字穴付きローレットねじ M2.5×10",
         "尺度": "5/1", "材質": "鉄 または 黄銅", "表面処理": "ニッケルクロムめっき"}
FILE = "十字穴付きローレットねじ_M2.5x10.pdf"


def draw(sh):
    R, rc, rs, rd, r1 = DK / 2, DC / 2, DS / 2, D / 2, D1 / 2
    Y0 = 40.0
    gap = 30.0
    left = -(S * DK + gap + S * L) / 2 + 5.0
    HX = left + S * R
    X0 = HX + S * R + gap
    xt = L - rd                      # とがり先の円すいの始まり (90° なので長さは半径と同じ)

    def P(x, y):
        return X0 + S * x, Y0 + S * y

    # ---- 正面図 (頭部を左)
    sh.line(*P(0, -(R - CK)), *P(0, R - CK), 6)                       # 頭の端面
    for sg in (1, -1):
        sh.line(*P(0, sg * (R - CK)), *P(CK, sg * R), 6)               # 端面側の面取り
        sh.line(*P(CK, sg * R), *P(LK - CK, sg * R), 6)                # ローレット部の外周
        sh.line(*P(LK - CK, sg * R), *P(LK, sg * (R - CK)), 6)         # 段側の面取り
        sh.line(*P(LK, sg * (R - CK)), *P(LK, sg * rc), 6)             # ローレット部の座面
        sh.line(*P(LK, sg * rc), *P(LH, sg * rc), 6)                   # 段の外周
        sh.line(*P(LH, sg * rc), *P(LH, sg * rs), 6)                   # 段の座面
        sh.line(*P(LH, sg * rs), *P(LH + LS, sg * rs), 6)              # ねじのない軸部
        sh.line(*P(LH + LS, sg * rs), *P(LH + LS, sg * rd), 6)         # ねじの始まり
        sh.line(*P(LH + LS, sg * rd), *P(xt, sg * rd), 6)              # ねじの山の径
        sh.line(*P(xt, sg * rd), *P(L, 0), 6)                          # とがり先 90°
        sh.line(*P(LH + LS, sg * r1), *P(L - r1, sg * r1), 1)          # ねじの谷の径 (細線)
    sh.line(*P(CK, -R), *P(CK, R), 6)                                 # 面取りの境
    sh.line(*P(LK - CK, -R), *P(LK - CK, R), 6)
    sh.line(*P(xt, -rd), *P(xt, rd), 6)                               # 円すいの境
    sh.line(*P(-1.0, 0), *P(L + 1.0, 0), 1, 6)                        # 中心線
    box = [P(CK, -R), P(LK - CK, -R), P(LK - CK, R), P(CK, R)]       # ローレット (綾目)
    hatch(sh, box, 30, 2.5)
    hatch(sh, box, -30, 2.5)

    # ---- 頭部側から見た図 (第三角法: 左側面図を左に置く)
    sh.circle(HX, Y0, S * R, 6)
    sh.circle(HX, Y0, S * (R - CK), 6)                                # 面取りの境
    aw, al = 0.3 * S, 1.35 * S
    cross = [(aw, al), (-aw, al), (-aw, aw), (-al, aw), (-al, -aw), (-aw, -aw),
             (-aw, -al), (aw, -al), (aw, -aw), (al, -aw), (al, aw), (aw, aw)]
    for p, q in zip(cross, cross[1:] + cross[:1]):
        sh.line(HX + p[0], Y0 + p[1], HX + q[0], Y0 + q[1], 6)
    sh.line(HX - S * R - 3, Y0, HX + S * R + 3, Y0, 1, 6)
    sh.line(HX, Y0 - S * R - 3, HX, Y0 + S * R + 3, 1, 6)

    # ---- 寸法
    top = Y0 + S * R + 8.0
    hdim(sh, P(0, 0)[0], P(LH, 0)[0], top, P(0, R - CK)[1], P(LH, rc)[1], fmt(LH))
    hdim(sh, P(LH, 0)[0], P(LH + LS, 0)[0], top, P(LH, rc)[1], P(LH + LS, rd)[1], fmt(LS))
    hdim(sh, P(LH + LS, 0)[0], P(L, 0)[0], top, P(LH + LS, rd)[1], P(L, 0)[1], fmt(LT))
    top2 = top + 9.0
    hdim(sh, P(0, 0)[0], P(LK, 0)[0], top2, top + 1.5, P(LK, R - CK)[1], f"({fmt(LK)})")
    bot = Y0 - S * R - 16.0
    hdim(sh, P(0, 0)[0], P(L, 0)[0], bot, P(0, -(R - CK))[1], P(L, 0)[1], f"({fmt(L)})")
    vdim(sh, P(0, -R)[1], P(0, R)[1], X0 - 10.0, P(CK, -R)[0], P(CK, R)[0], f"φ{fmt(DK)}")
    low = Y0 - S * R - 6.0
    leader(sh, *P(CK / 2, -(R - CK / 2)), X0 - 4.0, low, f"C{fmt(CK)}", size=3.5, side="L")
    leader(sh, *P(LK - CK / 2, -(R - CK / 2)), P(LK, 0)[0] - 4.0, low - 8.0, f"C{fmt(CK)}",
           size=3.5, side="L")
    leader(sh, *P((LK + LH) / 2, -rc), P(LH, 0)[0] + 4.0, low - 1.0, f"段 (φ{fmt(DC)})", size=3.5)
    leader(sh, *P(LH + LS / 2, -rs), P(LH + LS, 0)[0] + 6.0, Y0 - S * R + 4.0,
           f"(φ{fmt(DS)})", size=3.5, sub="転造前の径")
    leader(sh, *P(LH + LS + 2.5, rd), P(LH + LS + 2.5, 0)[0] + 6.0, Y0 + S * R - 2.0,
           f"M{fmt(D)}")
    leader(sh, *P(L - 0.5, -0.5), P(L, 0)[0] + 4.0, Y0 - S * rd - 8.0, "とがり先 90°", size=3.5)
    leader(sh, *P(2.0, R), X0 - 6.0, top2 + 4.0, "ローレット 綾目", size=3.5, side="L")
    leader(sh, HX + aw + 0.5, Y0 + al * 0.6, HX + S * R + 2.0, Y0 + S * R + 6.0,
           "十字穴 No.1", size=3.5)

    # ---- 注記
    notes(sh, [
        "1. 普通公差は JIS B 0405-m (中級) とする。",
        "2. ねじはメートル並目ねじ (ピッチ 0.45) とし、転造とする。",
        "3. ねじのない軸部 (長さ 4) は転造前の径とする。",
        "4. 段の外径 φ5.5、ローレット部の長さ 5.5 は指定なし。製作の都合で変えてよい。",
        "5. 頭部の径は φ6 でもよい。首下の長さは 11〜12 程度でもよい (依頼者の回答)。",
        "6. 十字穴の形状は略図。",
        "7. 指示のない角はバリを取ること。",
    ], y0=-6.0)


def main(out):
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw(sh)
    path = os.path.join(out, FILE)
    render(sh, path, TITLE["品名"])
    print(path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
