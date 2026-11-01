import math
import random
import time

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="세포 분열 관찰실", page_icon="🔬", layout="wide")

# ══════════════════════════════════════════════
# SVG 그림 도우미
# ══════════════════════════════════════════════
W, H = 720, 400
INK = "#12302c"
GRAY = "#5b6b66"
PURPLE = "#8a5db3"
M_COL, P_COL = "#d64550", "#3b6fb6"       # 어머니 쪽(빨강) / 아버지 쪽(파랑) 염색체
CELL_FILL, CELL_LINE = "#fff7ea", "#e0a04b"
FONT = "Noto Sans KR, Malgun Gothic, Apple SD Gothic Neo, sans-serif"


def T(x, y, s, size=16, fill=INK, anchor="middle", weight=600):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'


def line(x1, y1, x2, y2, color, w=4, dash=None, arrow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#ah)"' if arrow else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{d}{m}/>'


def path(d, color, w=3):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def circle(cx, cy, r, fill, stroke="none", sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def ell(cx, cy, rx, ry, fill, stroke="none", sw=2):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def lab(x, y, tx, ty, s, size=15, anchor="start"):
    off = {"start": 8, "end": -8, "middle": 0}[anchor]
    ty2 = ty + 5 if anchor != "middle" else ty + (16 if ty > y else -6)
    return line(x, y, tx, ty, GRAY, 1.8) + circle(x, y, 3.5, GRAY) + T(tx + off, ty2, s, size, INK, anchor, 600)


# ── 염색체 ──────────────────────────────────
LEN = {"L": 74, "S": 48}   # 긴 염색체 / 짧은 염색체


def col(par):
    return M_COL if par == "M" else P_COL


def other(par):
    return "P" if par == "M" else "M"


def chs(kind, par, cross):
    """복제된 염색체의 두 염색분체 색 (교차가 일어나면 긴 염색체의 한쪽 끝이 서로 바뀌어요)"""
    c, o = col(par), col(other(par))
    return [(c, c), (c, o)] if (kind == "L" and cross) else [(c, c), (c, c)]


def chrom(x, y, kind, cl, rot=0):
    """염색체 하나 : 염색분체가 둘이면 X자, 하나면 막대"""
    L = LEN[kind]
    g = ""
    if len(cl) == 2:
        for k, (top, bot) in enumerate(cl):
            sx = -5 if k == 0 else 5
            g += line(sx, -L / 2, 0, 0, top, 7) + line(0, 0, -sx, L / 2, bot, 7)
    else:
        g += line(0, -L / 2, 0, 0, cl[0][0], 7) + line(0, 0, 0, L / 2, cl[0][1], 7)
    g += circle(0, 0, 4.5, "#ffffff", "#333333", 1.5)
    return f'<g transform="translate({x},{y}) rotate({rot})">{g}</g>'


def chrom_v(x, y, kind, c2, rot=0):
    """극으로 끌려가는 염색분체 : 동원체가 앞장서고 팔이 뒤따르는 V자"""
    L = LEN[kind]
    g = line(0, 0, 18, -L / 2, c2[0], 7) + line(0, 0, 18, L / 2, c2[1], 7) + circle(0, 0, 4.5, "#ffffff", "#333333", 1.5)
    return f'<g transform="translate({x},{y}) rotate({rot})">{g}</g>'


# ── 세포 부품 ───────────────────────────────
def cell_e(cx, cy, rx, ry):
    return ell(cx, cy, rx, ry, CELL_FILL, CELL_LINE, 5)


def nucleus(cx, cy, r, dash=None, fill="#efe6f8"):
    return circle(cx, cy, r, fill, PURPLE, 3.5, dash)


def centrosome(x, y):
    rays = "".join(line(x, y, x + 15 * math.cos(math.radians(a)), y + 15 * math.sin(math.radians(a)), PURPLE, 2) for a in range(0, 360, 45))
    return rays + circle(x, y, 7, "#b08ad6", "#6b3fa0", 2)


def fibers(pole, targets):
    return "".join(line(pole[0], pole[1], tx, ty, "#a9b4b0", 2) for tx, ty in targets)


def peanut(x1, x2, cy, r):
    """세포질 분열 중 : 가운데가 잘록해진 세포"""
    b = circle(x1, cy, r, CELL_FILL, CELL_LINE, 5) + circle(x2, cy, r, CELL_FILL, CELL_LINE, 5)
    return b + circle(x1, cy, r - 2, CELL_FILL) + circle(x2, cy, r - 2, CELL_FILL)


def chromatin(cx, cy, scale=1.0):
    """풀어진 염색사 (간기)"""
    b = ""
    cols = ["#e8a0a6", "#9db8e0", "#e8a0a6", "#9db8e0"]
    for i, c in enumerate(cols):
        x0, y0 = cx - 55 * scale + (i % 2) * 20, cy - 45 * scale + i * 28 * scale
        b += path(f"M{x0:.0f},{y0:.0f} q10,-16 20,0 t20,0 t20,0 t20,0 t20,0", c, 4)
    return b


def equator(x, label=True):
    return line(x, 62, x, 338, "#9aa5a1", 1.8, "6 5") + (T(x, 372, "적도면", 13, GRAY) if label else "")


# ══════════════════════════════════════════════
# 단계별 그림
# ══════════════════════════════════════════════
def interphase(o):
    b = cell_e(360, 200, 190, 150) + nucleus(360, 200, 98) + circle(385, 215, 20, "#6b3fa0") + chromatin(340, 195, 1.0)
    b += centrosome(268, 112) + centrosome(292, 126)
    b += lab(268, 112, 140, 70, "중심체 (복제)", anchor="start") + lab(300, 262, 140, 330, "염색사 (풀어진 DNA)", anchor="start")
    b += lab(452, 160, 560, 100, "핵", anchor="start") + T(560, 330, "DNA 복제 : 2C → 4C", 16, M_COL, "middle")
    return b, "2n = 4 (복제 전)"


def mit_prophase(o):
    b = cell_e(360, 200, 190, 150) + circle(360, 200, 100, "#efe6f833", PURPLE, 3, "7 6")
    b += fibers((250, 135), [(325, 180), (335, 225)]) + fibers((470, 265), [(400, 215), (395, 175)])
    b += centrosome(250, 135) + centrosome(470, 265)
    for x, y, k, p, r in ((322, 172, "L", "M", 35), (402, 178, "L", "P", -25), (335, 240, "S", "M", 70), (400, 245, "S", "P", -50)):
        b += chrom(x, y, k, chs(k, p, False), r)
    b += lab(402, 175, 570, 110, "X자 모양 염색체", anchor="start") + lab(440, 120, 570, 70, "핵막이 사라지는 중", anchor="start")
    return b, "2n = 4 (염색체 4개, 염색분체 8개)"


MIT_ORDER = [("L", "M", 100), ("S", "P", 172), ("S", "M", 228), ("L", "P", 298)]


def mit_metaphase(o):
    b = cell_e(360, 200, 190, 150) + equator(360)
    for _, _, y in MIT_ORDER:
        b += fibers((205, 200), [(360, y)]) + fibers((515, 200), [(360, y)])
    b += centrosome(205, 200) + centrosome(515, 200)
    for k, p, y in MIT_ORDER:
        b += chrom(360, y, k, chs(k, p, False), 0)
    b += lab(360, 100, 570, 80, "염색체가 한 줄로 배열", anchor="start") + lab(300, 200, 130, 120, "방추사", anchor="end")
    return b, "2n = 4 (염색체 4개)"


def mit_anaphase(o):
    b = ell(360, 200, 215, 140, CELL_FILL, CELL_LINE, 5)
    for k, p, y in MIT_ORDER:
        cl = chs(k, p, False)
        b += fibers((180, 200), [(280, y)]) + fibers((540, 200), [(440, y)])
        b += chrom_v(280, y, k, cl[0], 0) + chrom_v(440, y, k, cl[1], 180)
    b += centrosome(180, 200) + centrosome(540, 200)
    b += lab(440, 100, 590, 70, "염색분체가 분리", anchor="start") + T(360, 372, "염색체 수가 일시적으로 2배 (4개 → 8개)", 16, M_COL)
    return b, "염색체 8개 (일시적)"


def mit_telophase(o):
    b = peanut(250, 470, 200, 135)
    for cx, idx in ((250, 0), (470, 1)):
        b += nucleus(cx, 200, 68)
        for dx, k, p in ((-36, "L", "M"), (-12, "S", "P"), (12, "S", "M"), (36, "L", "P")):
            b += chrom(cx + dx, 200, k, chs(k, p, False)[:1], 0)
    b += lab(360, 85, 360, 40, "세포질 분열 (잘록해져요)", anchor="middle") + lab(250, 268, 140, 350, "핵막이 다시 생겨요", anchor="start")
    return b, "세포 1개 → 2개로 나뉘는 중"


def mit_daughters(o):
    b = ""
    for cx in (200, 520):
        b += circle(cx, 200, 125, CELL_FILL, CELL_LINE, 5) + nucleus(cx, 200, 62) + chromatin(cx - 18, 200, 0.7)
    b += T(200, 358, "딸세포 1 (2n = 4)", 17, INK) + T(520, 358, "딸세포 2 (2n = 4)", 17, INK)
    b += T(360, 205, "=", 40, GRAY)
    return b, "딸세포 2개, 각각 2n = 4 (모세포와 같음)"


# ── 감수분열 ────────────────────────────────
def bivalent(x, y, kind, left_par, cross, rot=0, gap=26, mark=True):
    """2가 염색체 : 상동 염색체 한 쌍이 나란히 붙어 있는 모습"""
    g = chrom(-gap / 2, 0, kind, chs(kind, left_par, cross), 0) + chrom(gap / 2, 0, kind, chs(kind, other(left_par), cross), 0)
    if cross and kind == "L" and mark:
        g += circle(0, 12, 8, "none", "#f2a900", 3.5)
    return f'<g transform="translate({x},{y}) rotate({rot})">{g}</g>'


def after_I(o):
    """감수 1분열이 끝났을 때 왼쪽 세포/오른쪽 세포가 가진 염색체의 어버이 쪽"""
    lL = "M" if o["oL"] == 0 else "P"
    lS = "M" if o["oS"] == 0 else "P"
    return (lL, lS), (other(lL), other(lS))


def mei_prophase1(o):
    b = cell_e(360, 200, 190, 150) + circle(360, 200, 100, "#efe6f833", PURPLE, 3, "7 6")
    b += fibers((250, 135), [(335, 170)]) + fibers((470, 265), [(395, 240)]) + centrosome(250, 135) + centrosome(470, 265)
    b += bivalent(335, 168, "L", "M", o["cross"], 25) + bivalent(398, 245, "S", "M", False, -35, 22, False)
    b += lab(338, 135, 575, 70, "2가 염색체", anchor="start")
    if o["cross"]:
        b += lab(340, 183, 575, 130, "교차 (유전 물질 교환)", anchor="start")
    return b, "2n = 4 (2가 염색체 2개)"


def mei_metaphase1(o):
    b = cell_e(360, 200, 190, 150) + equator(360)
    yl, ys = 118, 275
    ordL = "M" if o["oL"] == 0 else "P"
    ordS = "M" if o["oS"] == 0 else "P"
    for y, pL in ((yl, ordL), (ys, ordS)):
        b += fibers((205, 200), [(348, y)]) + fibers((515, 200), [(372, y)])
    b += centrosome(205, 200) + centrosome(515, 200)
    b += bivalent(360, yl, "L", ordL, o["cross"], 0, 24, True) + bivalent(360, ys, "S", ordS, False, 0, 24, False)
    b += lab(372, 150, 580, 80, "2가 염색체가 적도면에 배열", anchor="start") + lab(300, 200, 130, 120, "방추사", anchor="end")
    return b, "2n = 4 (2가 염색체 2개)"


def mei_anaphase1(o):
    (lL, lS), (rL, rS) = after_I(o)
    b = ell(360, 200, 215, 140, CELL_FILL, CELL_LINE, 5)
    for x, pole, pL, pS in ((280, (180, 200), lL, lS), (440, (540, 200), rL, rS)):
        b += fibers(pole, [(x, 118), (x, 275)])
        b += chrom(x, 118, "L", chs("L", pL, o["cross"]), 0) + chrom(x, 275, "S", chs("S", pS, False), 0)
    b += centrosome(180, 200) + centrosome(540, 200)
    b += lab(440, 118, 590, 70, "상동 염색체가 분리", anchor="start") + T(360, 372, "염색분체는 아직 붙어 있어요", 16, M_COL)
    return b, "염색체 4개 (양극에 2개씩)"


def mei_telophase1(o):
    (lL, lS), (rL, rS) = after_I(o)
    b = peanut(250, 470, 200, 135)
    for cx, pL, pS in ((250, lL, lS), (470, rL, rS)):
        b += chrom(cx, 145, "L", chs("L", pL, o["cross"]), 0) + chrom(cx, 255, "S", chs("S", pS, False), 0)
    b += lab(360, 85, 360, 40, "세포질 분열", anchor="middle") + T(250, 362, "n = 2", 17, INK) + T(470, 362, "n = 2", 17, INK)
    return b, "세포 2개 (각각 n = 2, 염색체 수가 절반)"


def _two_cells(o):
    (lL, lS), (rL, rS) = after_I(o)
    return (200, lL, lS), (520, rL, rS)


def mei_prophase2(o):
    b = ""
    for cx, pL, pS in _two_cells(o):
        b += circle(cx, 200, 122, CELL_FILL, CELL_LINE, 5) + centrosome(cx, 98) + centrosome(cx, 302)
        b += fibers((cx, 98), [(cx - 20, 170)]) + fibers((cx, 302), [(cx + 20, 235)])
        b += chrom(cx - 25, 170, "L", chs("L", pL, o["cross"]), 28) + chrom(cx + 30, 238, "S", chs("S", pS, False), -40)
    b += T(360, 372, "DNA 복제 없이 시작", 14, GRAY)
    return b, "세포 2개 (각각 n = 2)"


def mei_metaphase2(o):
    b = ""
    for cx, pL, pS in _two_cells(o):
        b += circle(cx, 200, 122, CELL_FILL, CELL_LINE, 5) + line(cx - 100, 200, cx + 100, 200, "#9aa5a1", 1.8, "6 5")
        for tx in (cx - 48, cx + 48):
            b += fibers((cx, 98), [(tx, 200)]) + fibers((cx, 302), [(tx, 200)])
        b += centrosome(cx, 98) + centrosome(cx, 302)
        b += chrom(cx - 48, 200, "L", chs("L", pL, o["cross"]), 90) + chrom(cx + 48, 200, "S", chs("S", pS, False), 90)
    b += T(360, 372, "방추사 방향이 감수 1분열과 수직", 14, GRAY)
    return b, "세포 2개 (염색체 2개씩 적도면에 배열)"


def mei_anaphase2(o):
    b = ""
    for cx, pL, pS in _two_cells(o):
        b += ell(cx, 200, 122, 150, CELL_FILL, CELL_LINE, 5)
        for tx, k, p in ((cx - 48, "L", pL), (cx + 48, "S", pS)):
            cl = chs(k, p, o["cross"] if k == "L" else False)
            b += fibers((cx, 78), [(tx, 150)]) + fibers((cx, 322), [(tx, 250)])
            b += chrom_v(tx, 150, k, cl[0], 90) + chrom_v(tx, 250, k, cl[1], -90)
        b += centrosome(cx, 78) + centrosome(cx, 322)
    b += T(360, 372, "염색분체가 분리돼요", 14, M_COL)
    return b, "염색체 4개씩 (일시적)"


def mei_telophase2(o):
    b = ""
    for cx, pL, pS in _two_cells(o):
        for i, cy in enumerate((110, 290)):
            b += circle(cx, cy, 82, CELL_FILL, CELL_LINE, 5) + nucleus(cx, cy, 46)
            b += chrom(cx - 14, cy, "L", [chs("L", pL, o["cross"])[i]], 0) + chrom(cx + 16, cy, "S", [chs("S", pS, False)[i]], 0)
    b += T(360, 190, "n = 2", 20, GRAY) + T(360, 216, "× 4개", 16, GRAY)
    b += T(360, 252, "서로 유전적으로", 14, M_COL) + T(360, 272, "달라요", 14, M_COL)
    return b, "세포 4개 (각각 n = 2)"


MITOSIS = [
    ("간기", interphase, "세포가 분열을 준비하는 시기예요. **DNA를 복제**(S기)해서 유전 물질의 양이 2배가 돼요. 염색체는 아직 풀어진 실(염색사) 상태라 막대 모양으로 보이지 않아요. 중심체도 복제돼요.", 4, 4),
    ("전기", mit_prophase, "염색사가 **응축해서 염색체**가 되어 보이기 시작해요. 각 염색체는 복제된 **두 염색분체**가 붙어 있는 X자 모양이에요. 핵막이 사라지기 시작하고 **방추사**가 만들어져요.", 4, 4),
    ("중기", mit_metaphase, "염색체가 세포 가운데(**적도면**)에 한 줄로 늘어서요. 방추사가 각 염색체의 동원체에 붙어요. 염색체를 관찰하기 가장 좋은 시기예요.", 4, 4),
    ("후기", mit_anaphase, "각 염색체의 **염색분체가 둘로 갈라져** 방추사에 끌려 양극으로 이동해요. 갈라진 염색분체가 각각 염색체가 되어 염색체 수가 일시적으로 **2배**가 돼요.", 4, 8),
    ("말기", mit_telophase, "염색체가 양극에 도착해 풀어지기 시작하고 **핵막이 다시 생겨요**. 동시에 **세포질 분열**이 일어나요. 동물 세포는 세포막이 잘록해지고, 식물 세포는 세포판이 생겨요.", 4, 8),
    ("딸세포", mit_daughters, "**유전 정보가 똑같은 딸세포 2개**가 만들어져요. 딸세포의 염색체 수는 모세포와 같은 2n = 4예요. 체세포 분열은 생장과 재생, 상처 회복에 쓰여요.", 2, 4),
]
MEIOSIS = [
    ("간기", interphase, "**DNA를 복제**해요. 이후 연속해서 2번 분열(감수 1분열, 감수 2분열)하지만, DNA 복제는 **한 번만** 일어나요.", 4, 4),
    ("전기 I", mei_prophase1, "**상동 염색체**끼리 짝을 지어 붙어 **2가 염색체**를 만들어요. 이때 상동 염색체의 염색분체 사이에서 **교차**가 일어나 유전 물질 일부가 서로 교환돼요(색이 섞인 부분). 핵막이 사라지고 방추사가 생겨요.", 4, 4),
    ("중기 I", mei_metaphase1, "**2가 염색체**가 적도면에 배열돼요. 상동 염색체의 동원체는 서로 **반대쪽 극**의 방추사에 붙어요. 어느 쪽에 어떤 염색체가 서는지는 무작위예요(**독립적 배열**).", 4, 4),
    ("후기 I", mei_anaphase1, "**상동 염색체가 분리**되어 양극으로 이동해요. 염색분체는 아직 붙어 있어요. 이 분리 때문에 염색체 수가 절반으로 줄어요.", 4, 4),
    ("말기 I", mei_telophase1, "세포질 분열이 일어나 딸세포 2개가 만들어져요. 염색체 수가 **절반(n = 2)** 으로 줄었어요. 이것이 감수 1분열의 핵심이에요. 각 염색체는 아직 두 염색분체로 되어 있어요.", 2, 2),
    ("전기 II", mei_prophase2, "**DNA 복제 없이** 곧바로 감수 2분열이 시작돼요. 염색체가 다시 응축하고 방추사가 만들어져요.", 2, 2),
    ("중기 II", mei_metaphase2, "염색체가 적도면에 한 줄로 배열돼요. 방추사의 방향은 감수 1분열 때와 **수직**이에요.", 2, 2),
    ("후기 II", mei_anaphase2, "**염색분체가 분리**되어 양극으로 이동해요. 체세포 분열의 후기와 비슷해요. 염색체 수가 일시적으로 2배가 돼요.", 2, 4),
    ("말기 II", mei_telophase2, "세포질 분열이 일어나 **염색체 수가 n = 2인 딸세포 4개**(생식세포)가 만들어져요. 교차와 독립적 배열 때문에 4개의 세포는 서로 유전적으로 **달라요**.", 1, 2),
]
KINDS = {"체세포 분열": MITOSIS, "감수분열": MEIOSIS}


def frame_svg(stages, idx, o):
    name, fn = stages[idx][0], stages[idx][1]
    body, plo = fn(o)
    head = f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker></defs>'
    head += f'<rect width="{W}" height="{H}" rx="18" fill="#f3f8f5"/>'
    legend = (line(22, 388, 44, 388, M_COL, 7) + T(52, 393, "어머니 쪽 염색체", 13, GRAY, "start", 500)
              + line(170, 388, 192, 388, P_COL, 7) + T(200, 393, "아버지 쪽 염색체", 13, GRAY, "start", 500)
              + T(330, 393, "· 긴 염색체와 짧은 염색체는 서로 다른 상동 염색체 쌍이에요", 13, GRAY, "start", 500))
    title = T(22, 34, name, 22, "#a8791a", "start", 700) + T(698, 34, plo, 15, GRAY, "end", 600)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">'
            f'{head}{body}{title}{legend}</svg>')


# ══════════════════════════════════════════════
# 그래프
# ══════════════════════════════════════════════
def stage_chart(stages, idx, which, title):
    names = [s[0] for s in stages]
    vals = [s[3] if which == "dna" else s[4] for s in stages]
    df = pd.DataFrame({"stage": names, "v": vals})
    base = alt.Chart(df).encode(
        x=alt.X("stage:O", sort=names, title=None, axis=alt.Axis(labelAngle=-35)),
        y=alt.Y("v:Q", title=title, scale=alt.Scale(domain=[0, 9 if which == "chr" else 5]), axis=alt.Axis(tickMinStep=1)),
    )
    line_ = base.mark_line(interpolate="step-after", strokeWidth=3, color="#3b6fb6" if which == "dna" else "#d9822b")
    pts = base.mark_point(filled=True, size=70, color="#3b6fb6" if which == "dna" else "#d9822b")
    cur = alt.Chart(pd.DataFrame({"stage": [names[idx]], "v": [vals[idx]]})).mark_point(
        filled=True, size=260, color="#d64550").encode(x=alt.X("stage:O", sort=names), y="v:Q")
    return (line_ + pts + cur).properties(height=210, width="container")


# ══════════════════════════════════════════════
# 화면
# ══════════════════════════════════════════════
ss = st.session_state
ss.setdefault("kind", "체세포 분열")
ss.setdefault("stage", MITOSIS[0][0])
ss.setdefault("oL", 0)
ss.setdefault("oS", 0)
ss.setdefault("playing", False)


def on_kind():
    ss.stage = KINDS[ss.kind][0][0]


def step(d):
    names = [s[0] for s in KINDS[ss.kind]]
    ss.stage = names[min(max(names.index(ss.stage) + d, 0), len(names) - 1)]


def reroll():
    ss.oL, ss.oS = random.randint(0, 1), random.randint(0, 1)


def play():
    ss.playing = True


st.title("🔬 세포 분열 관찰실")
st.write("체세포 분열과 감수분열을 단계별로 직접 살펴보세요. 단계를 넘기거나 **자동 재생**으로 분열 과정을 따라가 볼 수 있어요. "
         "이 관찰실의 세포는 염색체가 4개(2n = 4)인 가상의 세포예요.")

st.radio("관찰할 분열", list(KINDS), horizontal=True, key="kind", on_change=on_kind)
stages = KINDS[ss.kind]
names = [s[0] for s in stages]

opts = {"cross": True, "oL": ss.oL, "oS": ss.oS}
if ss.kind == "감수분열":
    o1, o2 = st.columns([1, 1], vertical_alignment="center")
    opts["cross"] = o1.checkbox("교차 일어나게 하기", value=True, key="cross",
                                help="끄면 상동 염색체 사이에 유전 물질 교환이 일어나지 않아요.")
    o2.button("🎲 염색체 배열 다시 뽑기 (독립적 배열)", on_click=reroll,
              help="중기 I에서 상동 염색체가 어느 극 쪽에 서는지가 무작위로 바뀌어요.")

c_diagram = st.container()
c_controls = st.container()
c_detail = st.container()
ph_diagram = c_diagram.empty()
ph_detail = c_detail.empty()


def render(idx):
    name, _, desc, dna, chrn = stages[idx]
    ph_diagram.image(frame_svg(stages, idx, opts))
    with ph_detail.container():
        st.markdown(f"### {idx + 1} / {len(stages)} · {name}")
        st.markdown(desc)
        m1, m2 = st.columns(2)
        m1.metric("세포 1개당 DNA 양 (G₁기 = 2C)", f"{dna}C")
        m2.metric("세포 1개당 염색체 수", f"{chrn}개")


# 자동 재생 (슬라이더를 만들기 전에 실행해야 마지막 단계로 맞출 수 있어요)
if ss.playing:
    ss.playing = False
    for i in range(len(stages)):
        render(i)
        time.sleep(1.4)
    ss.stage = names[-1]

idx = names.index(ss.stage)
with c_controls:
    b1, b2, b3, b4 = st.columns([1, 1, 5, 1.6], vertical_alignment="bottom")
    b1.button("◀ 이전", on_click=step, args=(-1,), disabled=idx == 0, use_container_width=True)
    b2.button("다음 ▶", on_click=step, args=(1,), disabled=idx == len(stages) - 1, use_container_width=True)
    b3.select_slider("단계", options=names, key="stage")
    b4.button("▶ 자동 재생", on_click=play, use_container_width=True)

idx = names.index(ss.stage)
render(idx)

st.divider()
g1, g2 = st.columns(2)
with g1:
    st.markdown("#### 🧬 DNA 양의 변화")
    st.altair_chart(stage_chart(stages, idx, "dna", "세포 1개당 DNA 양 (C)"))
with g2:
    st.markdown("#### 🧵 염색체 수의 변화")
    st.altair_chart(stage_chart(stages, idx, "chr", "세포 1개당 염색체 수 (개)"))
st.caption("후기에는 염색분체가 갈라져 염색체 수가 일시적으로 2배가 되고, 세포질 분열이 끝나면 세포 1개당 값이 줄어요. "
           "분열 중인 세포는 그림의 세포 한 개를 기준으로 했어요.")

with st.expander("📊 체세포 분열과 감수분열 비교하기", expanded=False):
    st.markdown(
        "| 구분 | 체세포 분열 | 감수분열 |\n|---|---|---|\n"
        "| 일어나는 곳 | 몸을 이루는 체세포 | 생식 기관의 생식세포 형성 과정 |\n"
        "| 분열 횟수 | 1회 | 연속 2회 (감수 1분열, 감수 2분열) |\n"
        "| DNA 복제 | 1회 | 1회 (분열 전 간기에만) |\n"
        "| 딸세포 수 | 2개 | 4개 |\n"
        "| 염색체 수 | 모세포와 같음 (2n → 2n) | 절반으로 줄어듦 (2n → n) |\n"
        "| 2가 염색체, 교차 | 없음 | 감수 1분열 전기에 형성, 교차 일어남 |\n"
        "| 유전적으로 | 딸세포끼리 같음 | 딸세포끼리 서로 다름 |\n"
        "| 하는 일 | 생장, 재생, 상처 회복 | 생식세포 형성, 유전적 다양성 |"
    )
