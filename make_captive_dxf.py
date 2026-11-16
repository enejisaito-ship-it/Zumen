# -*- coding: utf-8 -*-
"""脱落防止ねじ M2×7.2 (TEMP-7D6H73 の案件) の図面を DXF で出力する。

図は make_captive.py と同じ。10/19 にお送りした注記付きの PDF に合わせて注記 1〜5 を入れる。
得意先は CLAUDE.md の決まりにより空欄。
座標は用紙の左下を原点とした用紙上の mm で、部品は尺度 10/1 のまま描いている (CAD で測った長さの 1/10 が実寸)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaneko import Sheet, load_template, fill_title, render, render_dxf  # noqa: E402
from make_captive import SCREW, TITLE, draw_screw, fmt  # noqa: E402

FILE = "脱落防止ねじ_M2x7.2.dxf"
NOTES = ["注記",
         "1. 寸法はお客様の推定値と写真から読み取った",
         "   仮の値。サンプル測定後に確定する。",
         "2. 材質は鉄またはステンレス (未定)。",
         f"3. 首部はM{fmt(SCREW['d'])}めねじの内径より細くし、",
         "   ねじ込み後に脱落しないこと。",
         "4. 駆動穴の形と深さはサンプルに合わせる。",
         "5. 指示のない角はバリなきこと。"]


def build():
    sh = Sheet()
    load_template(sh)
    fill_title(sh, TITLE)
    draw_screw(sh)
    y = -14.0
    for i, t in enumerate(NOTES):
        sh.text(-135.0, y, t, 4.0 if i == 0 else 3.5, sp=0.3)
        y -= 6.0 if i == 0 else 5.2
    return sh


def main(out, preview=None):
    sh = build()
    render_dxf(sh, os.path.join(out, FILE))
    if preview:                       # 確認用の PDF (同じ図形をそのまま PDF にしたもの)
        render(sh, preview, TITLE["品名"])
    print("ok", FILE)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".", sys.argv[2] if len(sys.argv) > 2 else None)
