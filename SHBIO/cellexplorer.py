import math
import streamlit as st

st.set_page_config(page_title="세포 탐색 · 세포소기관", page_icon="🔬", layout="wide")

# ══════════════════════════════════════════════
# SVG 그림 도우미 (그림은 모두 코드로 그려서 별도 이미지 파일이 필요 없어요)
# ══════════════════════════════════════════════
W, H = 720, 400
INK = "#12302c"
FONT = "Noto Sans KR, Malgun Gothic, Apple SD Gothic Neo, sans-serif"
BLUE, ORANGE, RED, TEAL, GREEN, PURPLE, GOLD = "#3b6fb6", "#e07b39", "#c4475a", "#2f9aa8", "#2f9a6a", "#8a5db3", "#c9962a"
GRAY = "#5b6b66"


def _marker(mid, color):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')


MARKERS = _marker("aB", BLUE) + _marker("aO", ORANGE) + _marker("aG", GRAY) + _marker("aR", RED) + _marker("aN", GREEN)


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="{FONT}"><defs>{MARKERS}</defs>'
            f'<rect width="{W}" height="{H}" rx="18" fill="#f3f8f5"/>{body}</svg>')


def T(x, y, s, size=16, fill=INK, anchor="middle", weight=600):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>')


def line(x1, y1, x2, y2, color, w=4, arrow=None, dash=None):
    m = f' marker-end="url(#{arrow})"' if arrow else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{w}" stroke-linecap="round"{d}{m}/>')


def path(d, color, w=4, fill="none", arrow=None):
    m = f' marker-end="url(#{arrow})"' if arrow else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"{m}/>')


def circle(cx, cy, r, fill, stroke="none", sw=2):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def ell(cx, cy, rx, ry, fill, stroke="none", sw=2, rot=0):
    t = f' transform="rotate({rot} {cx} {cy})"' if rot else ""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{t}/>'


def rect(x, y, w, h, fill, stroke="none", sw=2, rx=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def chip(x, y, w, h, fill, s, size=15, stroke="#9db6af"):
    return rect(x, y, w, h, fill, stroke, 2, 14) + T(x + w / 2, y + h / 2 + size * 0.35, s, size)


def lab(x, y, tx, ty, s, size=16, col=INK, anchor=None):
    """설명선: (x,y)의 부분을 (tx,ty)에 있는 글자로 가리킨다."""
    right = tx >= x
    a = anchor or ("start" if right else "end")
    off = 0 if a == "middle" else (8 if a == "start" else -8)
    ty_text = ty + 5 if a != "middle" else ty + (16 if ty > y else -6)
    return line(x, y, tx, ty, GRAY, 2) + circle(x, y, 3.5, GRAY) + T(tx + off, ty_text, s, size, col, a, 600)


def pts(fn, n):
    return " ".join(("M" if i == 0 else "L") + f"{fn(i)[0]:.1f},{fn(i)[1]:.1f}" for i in range(n))


def pat(pid, angle, color, gap=12, w=3):
    return (f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate({angle})"><line x1="0" y1="0" x2="{gap}" y2="0" stroke="{color}" stroke-width="{w}"/></pattern>')


# ══════════════════════════════════════════════
# 소기관 그림
# ══════════════════════════════════════════════
def draw_nucleus():
    cx, cy = 280, 200
    b = circle(cx, cy, 140, "#efe6f8", PURPLE, 4) + circle(cx, cy, 128, "#f6f0fb", PURPLE, 3)
    for d in ("M200,205 q20,-30 40,0 t40,0 t40,0", "M205,245 q20,-25 40,0 t40,0 t30,0", "M215,160 q20,-25 40,0 t40,0"):
        b += path(d, "#b08ad6", 3)
    b += circle(335, 205, 32, "#6b3fa0", "#4a2a73", 2)
    for a in (20, 75, 135, 200, 260, 320):
        x, y = cx + 134 * math.cos(math.radians(a)), cy + 134 * math.sin(math.radians(a))
        b += circle(round(x), round(y), 9, "#ffffff", PURPLE, 3)
    b += lab(370, 93, 470, 55, "핵막 (이중막)") + lab(300, 163, 470, 115, "염색질 (DNA + 단백질)")
    b += lab(355, 195, 470, 175, "인 (rRNA 합성)") + lab(406, 246, 470, 250, "핵공 (물질 통로)")
    b += T(470, 330, "DNA를 보호하고 세포 활동을 지휘해요", 15, GRAY, "start", 500)
    return svg(b)


def draw_ribosome():
    b = ell(320, 262, 95, 62, "#b58be0", "#6b3fa0", 3) + ell(320, 148, 72, 40, "#d9c2f0", "#6b3fa0", 3)
    b += line(60, 194, 600, 194, "#f2b84b", 7)
    for x in range(80, 590, 26):
        b += line(x, 189, x, 199, "#a8791a", 2)
    for i in range(8):
        t = i / 7
        b += circle(round(330 + t * 150), round(325 + 38 * math.sin(t * 2.4)), 11, [ORANGE, "#f1a56b"][i % 2], "#ffffff", 2)
    b += lab(395, 135, 470, 75, "작은 소단위체") + lab(410, 270, 490, 250, "큰 소단위체")
    b += lab(560, 194, 590, 150, "mRNA", anchor="middle") + lab(480, 360, 520, 385, "폴리펩타이드 (단백질)", 15, anchor="start")
    b += T(170, 360, "막이 없는 알갱이 (rRNA + 단백질)", 15, GRAY, "middle", 500)
    return svg(b)


def draw_rer():
    b = '<path d="M0,40 L60,40 Q170,200 60,360 L0,360 Z" fill="#efe6f8" stroke="#8a5db3" stroke-width="4"/>'
    b += T(28, 205, "핵", 18, PURPLE)
    for y in (95, 155, 215, 275):
        b += rect(150, y, 300, 34, "#cfe3f7", BLUE, 3, 17)
        for x in range(165, 440, 24):
            b += circle(x, y, 5, PURPLE) + circle(x, y + 34, 5, PURPLE)
    b += circle(525, 292, 20, "#e5f0fb", BLUE, 3) + line(452, 292, 495, 292, BLUE, 4, "aB")
    b += lab(341, 95, 500, 45, "라이보솜 (표면에 붙어 있어요)") + lab(450, 155, 500, 100, "소포체 막")
    b += lab(300, 172, 500, 150, "소포체 내부 공간", anchor="start") + T(525, 335, "수송 소포 → 골지체로", 15, BLUE)
    return svg(b)


def draw_ser():
    def tube(d):
        return path(d, "#6fb78f", 26) + path(d, "#d9f0e3", 18)
    b = ""
    for d in ("M100,110 C200,60 260,170 360,120 S520,90 620,130", "M100,255 C180,315 260,225 340,265 S500,315 620,255",
              "M240,125 C255,175 220,205 250,245", "M450,108 C470,170 430,220 460,290", "M360,121 C372,170 340,225 340,266"):
        b += tube(d)
    for x, y in ((150, 92), (330, 140), (520, 105), (200, 280), (400, 285), (560, 275)):
        b += circle(x, y, 6, "#f2b84b", "#a8791a", 1.5)
    b += lab(560, 275, 600, 190, "Ca²⁺ 저장", 15, anchor="start") + lab(120, 108, 90, 50, "관(튜브) 모양 그물", anchor="start")
    b += chip(70, 335, 170, 44, "#e8f1d9", "🧈 지질 합성", 16) + chip(275, 335, 170, 44, "#e8f1d9", "🧪 독성 물질 해독", 16)
    b += chip(480, 335, 170, 44, "#e8f1d9", "⚡ 칼슘 이온 저장", 16)
    b += T(360, 30, "라이보솜이 없어서 표면이 매끈해요", 16, GRAY, "middle", 500)
    return svg(b)


def draw_golgi():
    b = ""
    for i in range(5):
        x = 250 + i * 34
        d = f"M{x},95 Q{x - 45},200 {x},305"
        b += path(d, "#d99a2b", 17) + path(d, "#f6cf6e", 11)
    for y in (160, 240):
        b += circle(135, y, 15, "#cfe3f7", BLUE, 3) + line(155, y + 4, 215, 200, BLUE, 3, "aB")
    for x, y in ((470, 140), (490, 220), (460, 295)):
        b += circle(x, y, 17, "#fff3d6", ORANGE, 3) + line(395, 200 + (y - 200) * 0.3, x - 22, y, ORANGE, 3, "aO")
    b += lab(228, 105, 60, 45, "시스면 (받는 쪽)", anchor="start") + lab(386, 105, 470, 45, "트랜스면 (내보내는 쪽)", anchor="start")
    b += lab(300, 200, 330, 345, "낭 (납작한 주머니)", anchor="middle")
    b += T(135, 292, "소포체에서 온 소포", 14, BLUE, "middle", 500) + T(590, 200, "가공·포장된 소포", 14, ORANGE, "middle", 500)
    return svg(b)


def draw_lysosome():
    b = circle(105, 200, 58, "#ffe9c7", "#e0a04b", 4)
    for x, y in ((85, 180), (118, 190), (100, 222), (130, 225), (80, 215)):
        b += circle(x, y, 8, "#a8791a")
    b += line(170, 200, 225, 200, GRAY, 4, "aG") + T(198, 180, "합쳐져요", 14, GRAY, "middle", 500)
    b += circle(330, 200, 95, "#fbd9dc", RED, 4)
    for x, y in ((290, 160), (340, 150), (375, 190), (300, 210), (350, 235), (310, 250), (270, 195), (385, 225), (330, 190)):
        b += circle(x, y, 7, RED, "#ffffff", 1.5)
    for y in (160, 200, 240):
        b += line(430, y, 500, y, GREEN, 3, "aN") + circle(520, y, 7, "#7fc297", GREEN, 2)
    b += T(580, 195, "작은 분해 산물", 15, GREEN, "start") + T(580, 220, "→ 세포가 재사용", 15, GREEN, "start")
    b += lab(262, 140, 200, 60, "단일막", anchor="middle") + lab(340, 150, 440, 70, "가수분해 효소", anchor="start")
    b += T(105, 285, "삼킨 음식물·세균", 14, "#a8791a", "middle", 500) + T(330, 335, "산성 환경에서 효소가 작동해요", 15, GRAY, "middle", 500)
    return svg(b)


def draw_mito():
    b = ell(360, 200, 220, 105, "#fbe0d2", ORANGE, 4) + ell(360, 200, 203, 90, "#fff1e8", "#c4642a", 3)
    for x in (255, 315, 375, 435, 495):
        b += path(f"M{x},112 C{x + 20},140 {x - 20},165 {x},192", "#c4642a", 5)
        b += path(f"M{x + 30},288 C{x + 10},262 {x + 50},238 {x + 30},208", "#c4642a", 5)
    b += path("M285,222 a14,14 0 1,1 28,0 a14,14 0 1,1 -28,0", PURPLE, 3)
    b += circle(420, 238, 4, PURPLE) + circle(445, 245, 4, PURPLE)
    b += lab(528, 133, 600, 80, "외막") + lab(553, 169, 620, 130, "내막") + lab(435, 150, 620, 190, "크리스타", anchor="start")
    b += lab(480, 205, 620, 250, "기질 (매트릭스)", anchor="start") + lab(300, 224, 130, 340, "자체 DNA·리보솜", anchor="start")
    b += T(500, 345, "세포호흡 → ATP 생산", 17, RED, "start")
    return svg(b)


def draw_chloroplast():
    b = ell(360, 200, 230, 130, "#e3f3d6", GREEN, 4) + ell(360, 200, 216, 116, "#eef9e4", "#6fb78f", 3)
    stacks = [(250, 170), (365, 225), (480, 170), (320, 150)]
    b += line(284, 178, 335, 222, "#7fc297", 4) + line(398, 222, 450, 178, "#7fc297", 4) + line(284, 168, 300, 160, "#7fc297", 3)
    for cx, cy in stacks:
        for k in range(5):
            b += rect(cx - 34, cy - 30 + k * 14, 68, 11, "#3a9d5d", "#1f6b3c", 1.5, 5)
    b += path("M230,265 a12,12 0 1,1 24,0 a12,12 0 1,1 -24,0", PURPLE, 3)
    b += lab(585, 140, 620, 85, "외막 · 내막", anchor="start") + lab(514, 170, 620, 150, "그라나", anchor="start")
    b += lab(371, 218, 620, 215, "틸라코이드", anchor="start") + lab(420, 258, 620, 280, "스트로마", anchor="start")
    b += lab(242, 266, 130, 350, "자체 DNA", anchor="start")
    b += T(360, 385, "틸라코이드 막의 엽록소가 빛을 흡수해요", 16, GREEN, "middle")
    return svg(b)


def draw_vacuole():
    b = rect(40, 50, 520, 300, "#d8ecc6", "#6aa84f", 14, 40) + rect(54, 64, 492, 272, "#eef7e4", "#9cc47f", 3, 30)
    b += ell(300, 200, 175, 105, "#cfe8f7", BLUE, 4)
    b += circle(90, 200, 28, "#efe6f8", PURPLE, 3) + circle(98, 205, 9, "#6b3fa0")
    for x in (210, 300, 390):
        b += ell(x, 80, 24, 10, "#7fc297", "#1f6b3c", 2)
    for x, y in ((230, 170), (300, 150), (370, 175), (260, 240), (340, 245)):
        b += circle(x, y, 7, "#ffffff", BLUE, 2)
    b += T(300, 205, "물 · 양분 · 노폐물 저장", 17, BLUE) + T(300, 232, "중심액포", 15, GRAY, "middle", 500)
    b += lab(552, 110, 585, 70, "세포벽", anchor="start") + lab(546, 150, 585, 125, "세포막", anchor="start")
    b += lab(472, 215, 585, 235, "액포막", anchor="start") + lab(300, 70, 300, 30, "엽록체", anchor="middle")
    b += lab(90, 232, 90, 322, "핵", anchor="middle")
    b += T(585, 290, "물이 가득 차면", 14, GRAY, "start", 500) + T(585, 312, "팽압으로 세포가", 14, GRAY, "start", 500) + T(585, 334, "단단해져요", 14, GRAY, "start", 500)
    return svg(b)


def draw_membrane():
    b = T(20, 55, "세포 밖", 15, GRAY, "start") + T(20, 360, "세포 안 (세포질)", 15, GRAY, "start")
    xs = [x for x in range(50, 480, 30) if not (170 < x < 215 or 315 < x < 355)]
    for x in xs:
        b += line(x - 4, 130, x - 4, 190, "#c9a13a", 3) + line(x + 4, 130, x + 4, 190, "#c9a13a", 3)
        b += line(x - 4, 270, x - 4, 210, "#c9a13a", 3) + line(x + 4, 270, x + 4, 210, "#c9a13a", 3)
        b += circle(x, 120, 11, "#f2b84b", "#a8791a", 2) + circle(x, 280, 11, "#f2b84b", "#a8791a", 2)
    b += ell(192, 200, 30, 106, "#8fb8e8", BLUE, 3) + rect(326, 98, 20, 204, "#e58f8f", RED, 2, 6) + rect(352, 98, 20, 204, "#e58f8f", RED, 2, 6)
    for y in (140, 200, 260):
        b += circle(349, y, 5, "#ffd166", "#a8791a", 1.5)
    b += ell(262, 322, 38, 17, "#cdb4e6", PURPLE, 2)
    b += line(110, 108, 110, 70, GREEN, 3) + line(110, 85, 92, 66, GREEN, 3) + line(110, 85, 128, 66, GREEN, 3)
    for x, y in ((110, 66), (92, 62), (128, 62)):
        b += circle(x, y, 6, "#f1a56b", ORANGE, 1.5)
    for x, y in ((400, 170), (440, 235), (95, 235)):
        b += ell(x, y, 7, 14, "#ffb703", "#a8791a", 1.5)
    b += lab(95, 62, 505, 40, "당 사슬 (세포 인식)", 15) + lab(440, 120, 505, 85, "인지질 머리 (친수성)", 15)
    b += lab(430, 160, 505, 140, "꼬리 (소수성)", 15) + lab(372, 170, 505, 195, "통로 단백질", 15)
    b += lab(440, 235, 505, 260, "콜레스테롤", 15) + lab(192, 304, 192, 350, "막관통 단백질", 15, anchor="middle")
    b += lab(262, 340, 330, 378, "표면 단백질", 15, anchor="middle")
    return svg(b)


def draw_primary_wall():
    d = "<defs>" + pat("m1", 25, "#8fbf6f") + pat("m2", -55, "#a9cf8c") + "</defs>"
    b = d + rect(30, 60, 190, 280, "#eef7e4") + rect(374, 60, 190, 280, "#eef7e4")
    for x in (220, 314):
        b += rect(x, 60, 60, 280, "#cfe6bd") + rect(x, 60, 60, 280, "url(#m1)") + rect(x, 60, 60, 280, "url(#m2)")
    b += rect(280, 60, 34, 280, "#f3e4a8") + line(220, 60, 220, 340, "#7a9c63", 5) + line(374, 60, 374, 340, "#7a9c63", 5)
    b += T(125, 205, "세포 A", 18, GRAY) + T(469, 205, "세포 B", 18, GRAY)
    b += lab(220, 100, 110, 30, "세포막", anchor="middle") + lab(250, 130, 250, 30, "1차 세포벽", anchor="middle")
    b += lab(297, 100, 400, 30, "중간층 (펙틴)", anchor="middle") + lab(340, 300, 340, 372, "셀룰로스 미세섬유", anchor="middle")
    b += T(600, 150, "얇고 유연해요", 16, GREEN, "middle") + T(600, 178, "세포가 자라는 동안", 15, GRAY, "middle", 500) + T(600, 202, "늘어날 수 있어요", 15, GRAY, "middle", 500)
    return svg(b)


def draw_secondary_wall():
    d = "<defs>" + pat("s3", 70, "#6fa05a", 9, 4) + pat("s2", 8, "#4f8a45", 9, 4) + pat("s1", -60, "#6fa05a", 9, 4)
    d += pat("m1", 25, "#8fbf6f") + pat("m2", -55, "#a9cf8c") + "</defs>"
    b = d + rect(30, 70, 110, 260, "#eef7e4")
    layers = [(140, 70, "#d9ecc8", "s3"), (210, 150, "#d0e6bc", "s2"), (360, 70, "#d9ecc8", "s1"), (430, 50, "#cfe6bd", "m1")]
    for x, w, f, p in layers:
        b += rect(x, 70, w, 260, f) + rect(x, 70, w, 260, f"url(#{p})")
    b += rect(430, 70, 50, 260, "url(#m2)") + rect(480, 70, 30, 260, "#f3e4a8") + rect(510, 70, 50, 260, "#cfe6bd") + rect(510, 70, 50, 260, "url(#m1)")
    b += rect(560, 70, 130, 260, "#eef7e4") + line(140, 70, 140, 330, "#7a9c63", 5) + line(560, 70, 560, 330, "#7a9c63", 5)
    b += T(85, 205, "세포 내부", 17, GRAY) + T(625, 205, "이웃 세포", 17, GRAY)
    b += line(140, 50, 430, 50, GREEN, 4) + T(285, 35, "2차 세포벽 (생장이 끝난 뒤 안쪽에 덧붙여요)", 16, GREEN)
    b += lab(140, 330, 140, 355, "세포막", 15, anchor="middle") + lab(175, 330, 175, 383, "S3층", 15, anchor="middle")
    b += lab(285, 330, 285, 355, "S2층 (가장 두꺼움)", 15, anchor="middle") + lab(395, 330, 395, 383, "S1층", 15, anchor="middle")
    b += lab(455, 330, 455, 355, "1차벽", 15, anchor="middle") + lab(495, 330, 495, 383, "중간층", 15, anchor="middle")
    return svg(b)


def draw_microtubule():
    b = ""
    for i in range(13):
        a = i / 13 * 2 * math.pi
        b += circle(round(150 + 62 * math.cos(a)), round(200 + 62 * math.sin(a)), 14, ["#7aa8e8", BLUE][i % 2], "#ffffff", 2)
    b += T(150, 130, "단면", 16, GRAY, "middle", 500) + T(150, 305, "속이 빈 관", 16, BLUE) + T(150, 330, "지름 약 25nm", 15, GRAY, "middle", 500)
    b += rect(290, 150, 400, 100, "#eaf1fb", BLUE, 3, 50)
    for c in range(14):
        for y in (172, 200, 228):
            b += circle(318 + c * 26, y, 9, [BLUE, "#8fb8e8"][c % 2], "#ffffff", 1.5)
    b += line(470, 105, 455, 152, GRAY, 3) + line(470, 105, 488, 152, GRAY, 3) + line(470, 105, 470, 88, GRAY, 3) + circle(470, 62, 26, "#ffe3d3", ORANGE, 3)
    b += lab(496, 62, 560, 40, "수송 소포", 15) + lab(486, 120, 560, 100, "모터 단백질", 15)
    b += lab(404, 228, 404, 290, "튜불린 (α·β 이량체)", 15, anchor="middle")
    b += T(300, 275, "(−)끝", 15, GRAY, "middle") + T(680, 275, "(+)끝", 15, GRAY, "middle") + line(540, 278, 640, 278, GRAY, 2, "aG")
    return svg(b)


def draw_microfilament():
    b = ""
    for i in range(34):
        x = 250 + i * 13
        s = 28 * math.sin(i * 0.55)
        b += circle(x, round(200 + s), 8, ORANGE, "#ffffff", 1.5) + circle(x, round(200 - s), 8, "#f1a56b", "#ffffff", 1.5)
    for x, y in ((80, 150), (115, 235), (65, 215)):
        b += circle(x, y, 13, "#f1a56b", ORANGE, 2)
    b += line(150, 195, 235, 195, ORANGE, 4, "aO")
    b += lab(80, 150, 120, 95, "액틴 단량체", anchor="start") + lab(470, 172, 470, 110, "액틴 필라멘트 (지름 약 7nm)", anchor="middle")
    b += chip(90, 310, 160, 44, "#fdebdc", "💪 근육 수축", 16, "#e9a47c") + chip(280, 310, 160, 44, "#fdebdc", "🔄 세포 이동", 16, "#e9a47c")
    b += chip(470, 310, 190, 44, "#fdebdc", "✂️ 세포질 분열", 16, "#e9a47c") + T(360, 30, "가장 가는 섬유 · 액틴이 꼬여 있어요", 16, GRAY, "middle", 500)
    return svg(b)


def draw_intermediate():
    b = ""
    cols = ["#2f9a6a", "#5bbf8e", "#7fd1a8"]
    b += rect(40, 185, 90, 14, "#2f9a6a", "none", 0, 7)
    for k in range(2):
        b += path(pts(lambda i, k=k: (190 + i * 7, 192 + 8 * math.sin(i * 0.5 + k * math.pi)), 14), cols[k], 7)
    for r in range(2):
        for k in range(2):
            b += path(pts(lambda i, k=k, r=r: (330 + i * 5 + r * 14, 160 + r * 60 + 7 * math.sin(i * 0.6 + k * math.pi)), 14), cols[k], 6)
    for k in range(3):
        b += path(pts(lambda i, k=k: (470 + i * 9, 200 + 18 * math.sin(i * 0.4 + k * 2.1)), 28), cols[k], 12)
    for x1, x2 in ((135, 185), (290, 325), (410, 465)):
        b += line(x1, 192, x2, 192, GRAY, 3, "aG")
    for x, s in ((85, "단량체"), (230, "이량체 (꼬임)"), (365, "사량체"), (590, "중간섬유 (밧줄 모양)")):
        b += T(x, 300, s, 15, INK)
    b += T(360, 60, "섬유 단백질이 밧줄처럼 꼬여서 튼튼해져요", 17, GREEN) + T(360, 345, "지름 약 8~12nm · 케라틴 등", 15, GRAY, "middle", 500)
    return svg(b)


def draw_cyto_overview():
    b = ell(340, 205, 280, 170, "#fff7ea", "#e0a04b", 5) + circle(330, 215, 52, "#efe6f8", PURPLE, 4) + circle(338, 220, 14, "#6b3fa0")
    for a in range(0, 360, 36):
        x, y = 330 + 300 * math.cos(math.radians(a)), 215 + 300 * math.sin(math.radians(a))
        b += line(330 + 60 * math.cos(math.radians(a)), 215 + 60 * math.sin(math.radians(a)), round(330 + 150 * math.cos(math.radians(a))), round(215 + 120 * math.sin(math.radians(a))), BLUE, 6)
    for a in range(10, 360, 22):
        b += line(round(340 + 262 * math.cos(math.radians(a))), round(205 + 156 * math.sin(math.radians(a))), round(340 + 238 * math.cos(math.radians(a + 10))), round(205 + 142 * math.sin(math.radians(a + 10))), ORANGE, 4)
    b += circle(330, 215, 66, "none", GREEN, 4) + circle(330, 215, 72, "none", "#5bbf8e", 4)
    b += rect(590, 60, 22, 8, BLUE, "none", 0, 4) + T(622, 70, "미세소관", 15, BLUE, "start") + rect(590, 90, 22, 5, ORANGE, "none", 0, 3) + T(622, 98, "미세섬유", 15, ORANGE, "start")
    b += rect(590, 120, 22, 8, GREEN, "none", 0, 4) + T(622, 130, "중간섬유", 15, GREEN, "start")
    return svg(b)


def _cell_dots(pts_):
    return "".join(circle(x, y, 3, PURPLE) for x, y in pts_)


def draw_animal_map():
    b = ell(340, 200, 215, 165, "#fff1e0", "#e0a04b", 5)
    b += circle(225, 195, 55, "#efe6f8", PURPLE, 4) + circle(235, 203, 14, "#6b3fa0")
    for i in range(4):
        y = 150 + i * 24
        b += rect(300, y, 90, 14, "#cfe3f7", BLUE, 2, 7) + _cell_dots([(x, y) for x in range(310, 385, 18)])
    b += path("M360,285 q30,-25 60,0 t60,0", "#6fb78f", 14) + path("M360,285 q30,-25 60,0 t60,0", "#d9f0e3", 8)
    for i in range(4):
        x = 410 + i * 12
        b += path(f"M{x},95 Q{x - 18},118 {x},141", "#f2b84b", 6)
    b += circle(330, 92, 13, "#fbd9dc", RED, 3)
    for x, y, r in ((470, 218, -15), (265, 305, 20)):
        b += ell(x, y, 36, 17, "#fbe0d2", ORANGE, 3, r) + path(f"M{x - 20},{y} q10,-10 20,0 t20,0", "#c4642a", 2)
    b += _cell_dots([(400, 320), (420, 310), (180, 120), (150, 270), (330, 250), (200, 90)])
    b += lab(505, 94, 585, 38, "세포막") + lab(343, 92, 585, 78, "라이소솜") + lab(440, 118, 585, 118, "골지체")
    b += lab(390, 170, 585, 160, "거친면 소포체") + lab(500, 215, 585, 200, "마이토콘드리아") + lab(470, 283, 585, 245, "매끈면 소포체")
    b += lab(420, 310, 585, 290, "라이보솜") + lab(170, 195, 100, 195, "핵")
    b += T(340, 385, "동물 세포 : 세포벽·엽록체가 없고, 큰 중심액포도 없어요", 15, GRAY, "middle", 500)
    return svg(b)


def draw_plant_map():
    b = rect(40, 50, 520, 300, "#d8ecc6", "#6aa84f", 14, 40) + rect(54, 64, 492, 272, "#f6fbef", "#9cc47f", 3, 30)
    b += ell(300, 200, 165, 100, "#cfe8f7", BLUE, 4) + T(300, 205, "액포", 20, BLUE)
    b += circle(100, 200, 30, "#efe6f8", PURPLE, 3) + circle(108, 205, 9, "#6b3fa0")
    for x, y in ((210, 82), (300, 78), (390, 82)):
        b += ell(x, y, 25, 11, "#7fc297", "#1f6b3c", 2)
    b += ell(510, 170, 12, 28, "#7fc297", "#1f6b3c", 2) + ell(215, 320, 30, 13, "#fbe0d2", ORANGE, 3) + ell(430, 315, 30, 13, "#fbe0d2", ORANGE, 3, -10)
    for i in range(3):
        b += rect(110, 255 + i * 12, 50, 8, "#cfe3f7", BLUE, 2, 4)
    for i in range(4):
        x = 498 + i * 9
        b += path(f"M{x},235 Q{x - 12},255 {x},275", "#f2b84b", 5)
    b += _cell_dots([(120, 255), (140, 255), (300, 330), (350, 322)])
    b += lab(552, 110, 590, 40, "세포벽") + lab(546, 150, 590, 80, "세포막") + lab(450, 170, 590, 120, "액포")
    b += lab(510, 160, 590, 160, "엽록체") + lab(515, 255, 590, 215, "골지체") + lab(430, 315, 590, 270, "마이토콘드리아")
    b += lab(135, 262, 135, 364, "소포체", anchor="middle") + lab(100, 170, 40, 130, "핵", anchor="end")
    b += T(360, 392, "식물 세포 : 세포벽, 엽록체, 큰 중심액포가 특징이에요", 15, GRAY, "middle", 500)
    return svg(b)


# ══════════════════════════════════════════════
# 설명 자료
# ══════════════════════════════════════════════
CAT1 = "① 정보 저장과 단백질 합성"
CAT2 = "② 에너지 · 분해 · 저장"
CAT3 = "③ 세포의 경계와 지지"
ALL = "전체 보기"
CATS = [CAT1, CAT2, CAT3]

ITEMS = [
    dict(key="핵", cat=CAT1, icon="🧬", color=PURPLE, where="동물 · 식물 세포 모두",
         summary="세포의 본부예요. 유전 물질인 DNA를 보호하고, 세포의 활동을 지휘해요.",
         easy="DNA는 '설계도 원본'이에요. 원본은 도서관(핵)에 안전하게 보관하고, 필요한 부분만 복사본(mRNA)으로 내보내요.",
         parts=[dict(name="핵", draw=draw_nucleus,
                     structure=["**핵막** : 이중막으로 DNA를 감싸 보호해요.", "**핵공** : 핵막의 구멍. mRNA와 단백질이 드나드는 통로예요.",
                                "**염색질** : DNA가 단백질과 함께 실처럼 풀려 있는 상태예요. 세포가 분열할 때는 염색체로 뭉쳐요.",
                                "**인** : rRNA를 만들고 리보솜의 소단위체를 조립하는 곳이에요."],
                     role=["유전 정보(DNA)를 저장하고 복제해요.", "DNA 정보를 mRNA로 옮겨 적어(전사) 단백질 합성을 지휘해요.", "세포의 생장과 분열 등 활동을 조절해요."])]),
    dict(key="라이보솜", cat=CAT1, icon="⚙️", color=PURPLE, where="모든 세포 (원핵세포에도 있어요)",
         summary="아미노산을 이어 붙여 단백질을 만드는 '단백질 조립 기계'예요.",
         easy="레시피(mRNA)를 읽으면서 재료(아미노산)를 하나씩 이어 붙여 요리(단백질)를 완성해요.",
         parts=[dict(name="라이보솜", draw=draw_ribosome,
                     structure=["rRNA와 단백질로 이루어진 아주 작은 알갱이예요. **막이 없어요.**", "크기가 다른 두 개의 소단위체(큰 것, 작은 것)로 되어 있어요.",
                                "세포질에 떠 있는 것과 거친면 소포체에 붙어 있는 것이 있어요."],
                     role=["mRNA의 정보를 읽어 아미노산을 연결해 단백질을 합성해요(번역).", "떠 있는 라이보솜은 세포 안에서 쓰일 단백질을, 소포체에 붙은 라이보솜은 분비·막 단백질을 주로 만들어요."])]),
    dict(key="소포체", cat=CAT1, icon="🏭", color=BLUE, where="동물 · 식물 세포 모두 (진핵세포)",
         summary="막으로 된 납작한 주머니와 관이 그물처럼 퍼진 구조예요. 핵막과 이어져 있고, 물질을 만들고 운반해요.",
         easy="공장 단지의 생산 라인이에요. 거친면은 단백질 조립 라인, 매끈면은 지방 · 해독 작업장이에요.",
         parts=[dict(name="거친면 소포체", draw=draw_rer,
                     structure=["납작한 주머니가 층층이 쌓인 모양이에요.", "막 바깥에 **라이보솜**이 붙어 있어 표면이 거칠어 보여요.", "핵막과 이어져 있어요."],
                     role=["붙어 있는 라이보솜이 만든 단백질(분비 단백질, 막 단백질)이 소포체 안으로 들어와 접히고 다듬어져요.", "다듬어진 단백질을 수송 소포에 담아 골지체로 보내요."]),
                dict(name="매끈면 소포체", draw=draw_ser,
                     structure=["관(튜브)이 그물처럼 이어진 모양이에요.", "**라이보솜이 없어서** 표면이 매끈해요."],
                     role=["지질(인지질, 스테로이드 등)을 합성해요.", "간세포 등에서 독성 물질을 해독해요.", "칼슘 이온을 저장해요. (근육 세포의 근소포체가 대표적이에요.)"])],
         table=("구분", ["거친면 소포체", "매끈면 소포체"],
                [("모양", "납작한 주머니", "관(튜브) 모양"), ("라이보솜", "붙어 있음", "없음"),
                 ("주요 기능", "단백질 가공 · 운반", "지질 합성, 해독, 칼슘 저장"), ("발달한 세포", "단백질을 많이 분비하는 세포", "지질 대사가 활발한 세포 (간, 근육 등)")])),
    dict(key="골지체", cat=CAT1, icon="📦", color=GOLD, where="동물 · 식물 세포 모두",
         summary="소포체에서 온 단백질과 지질을 가공 · 분류 · 포장해서 목적지로 보내는 '택배 분류 센터'예요.",
         easy="물건(단백질)이 도착하면 포장을 다듬고(가공), 배송지별로 나누어(분류), 상자(소포)에 담아 내보내요.",
         parts=[dict(name="골지체", draw=draw_golgi,
                     structure=["납작한 주머니(낭)가 겹겹이 쌓인 구조예요.", "소포체에서 소포를 받는 쪽(**시스면**)과 내보내는 쪽(**트랜스면**)이 구분돼요."],
                     role=["단백질에 당 사슬을 붙이는 등 물질을 가공해요.", "목적지별로 분류해 소포에 포장하고, 세포막 · 라이소솜 · 세포 밖(분비)으로 보내요.",
                           "식물 세포에서는 세포벽을 이루는 다당류 일부를 만들어요."])]),
    dict(key="라이소솜", cat=CAT2, icon="♻️", color=RED, where="주로 동물 세포 (식물에서는 액포가 비슷한 일을 해요)",
         summary="여러 가수분해 효소가 들어 있는 작은 주머니예요. 세포 안의 '소화 · 재활용' 담당이에요.",
         easy="재활용 센터예요. 낡은 부품과 삼킨 음식물을 잘게 분해해서 다시 쓸 수 있게 만들어요.",
         parts=[dict(name="라이소솜", draw=draw_lysosome,
                     structure=["단일막으로 둘러싸인 작은 주머니예요.", "산성 환경에서 잘 작동하는 **가수분해 효소**가 들어 있어요.", "골지체에서 만들어진 소포로부터 생겨요."],
                     role=["세포가 삼킨 세균과 음식물을 분해해요.", "낡거나 손상된 소기관을 분해하고 재활용해요.", "효소를 막 안에 가두어 두어서 세포 자신을 분해하지 않도록 보호해요."])]),
    dict(key="마이토콘드리아", cat=CAT2, icon="🔋", color=ORANGE, where="동물 · 식물 세포 모두",
         summary="세포호흡으로 영양소를 분해해 ATP(세포의 에너지 화폐)를 만드는 '발전소'예요.",
         easy="연료(포도당)를 태워 전기(ATP)를 만드는 발전소예요. 에너지가 많이 필요한 근육세포에 특히 많아요.",
         parts=[dict(name="마이토콘드리아", draw=draw_mito,
                     structure=["**외막**과 안쪽으로 접힌 **내막**의 이중막이에요.", "**크리스타** : 내막의 주름. 표면적이 넓어져 ATP를 많이 만들 수 있어요.",
                                "**기질(매트릭스)** : 내막 안쪽 공간으로 효소가 많아요.", "자체 DNA와 리보솜이 있어 일부 단백질은 스스로 합성해요."],
                     role=["세포호흡을 통해 포도당 등을 분해하고 ATP를 만들어요.", "세포가 활동하는 데 필요한 에너지를 공급해요."])]),
    dict(key="엽록체", cat=CAT2, icon="🌿", color=GREEN, where="식물 세포 (조류 포함) · 동물 세포에는 없어요",
         summary="빛에너지를 화학 에너지로 바꾸는 광합성의 현장이에요. 식물의 '태양광 발전소'예요.",
         easy="햇빛, 물, 이산화탄소로 포도당(양식)을 만드는 공장이에요. 만드는 김에 산소도 내보내요.",
         parts=[dict(name="엽록체", draw=draw_chloroplast,
                     structure=["**외막 · 내막**의 이중막이에요.", "**틸라코이드** : 납작한 주머니. 쌓여 있는 더미를 **그라나**라고 해요. 막에 엽록소(초록 색소)가 있어요.",
                                "**스트로마** : 틸라코이드 바깥의 액체로, 포도당을 만드는 효소가 있어요.", "자체 DNA와 리보솜이 있어요."],
                     role=["광합성 : 빛, 물, 이산화탄소로 포도당을 만들고 산소를 내보내요.", "빛을 흡수하는 반응은 틸라코이드에서, 포도당을 만드는 반응은 스트로마에서 일어나요."])]),
    dict(key="액포", cat=CAT2, icon="💧", color=BLUE, where="식물 세포에서 특히 크게 발달 (동물 세포에는 작은 액포만)",
         summary="물 · 양분 · 노폐물 등을 저장하는 주머니예요. 식물의 성숙한 세포에는 크고 발달한 중심액포가 있어요.",
         easy="물탱크 겸 창고예요. 물이 가득 차면 풍선처럼 빵빵해져서 식물 세포의 모양을 지켜 줘요.",
         parts=[dict(name="액포", draw=draw_vacuole,
                     structure=["**액포막(토노플라스트)** 으로 둘러싸인 주머니예요.", "식물의 성숙한 세포에서는 세포 부피의 대부분을 차지하고, 세포질은 가장자리로 밀려나요.", "동물 세포에는 작은 액포만 있어요."],
                     role=["물, 양분, 무기염류, 노폐물을 저장해요.", "물이 차면 팽압이 생겨 세포를 단단하게 지탱해요. (물이 부족하면 식물이 시들어요.)",
                           "꽃과 열매의 색소(안토사이아닌 등)를 저장하기도 해요."])]),
    dict(key="세포막", cat=CAT3, icon="🧱", color=GOLD, where="모든 세포",
         summary="세포를 둘러싼 얇은 막이에요. 필요한 물질만 골라 통과시키는 '출입 관리소'예요.",
         easy="경계선에 있는 검문소예요. 들어와도 되는 물질은 통과시키고, 안 되는 물질은 막아요.",
         parts=[dict(name="세포막", draw=draw_membrane,
                     structure=["**인지질 이중층** : 물을 좋아하는 머리(친수성)가 바깥쪽, 물을 싫어하는 꼬리(소수성)가 안쪽을 향해요.",
                                "**막단백질** : 물질이 드나드는 통로, 운반체, 신호를 받는 수용체 역할을 해요.", "**당 사슬** : 세포 표면에 붙어 세포를 알아보는 표지가 돼요.",
                                "**콜레스테롤** : 동물 세포막의 유동성을 조절해요."],
                     role=["**선택적 투과성**으로 물질의 출입을 조절해요.", "호르몬 같은 세포 밖의 신호를 받아들여 전달해요.", "세포를 알아보고 이웃 세포와 정보를 주고받아요.",
                           "막의 구성 성분이 움직이는 모습을 설명한 것이 **유동 모자이크 모형**이에요."])]),
    dict(key="세포벽", cat=CAT3, icon="🏰", color=GREEN, where="식물 세포 (동물 세포에는 없어요)",
         summary="세포막 바깥을 둘러싼 단단한 층이에요. 식물 세포를 보호하고 모양을 지켜 줘요. 주성분은 셀룰로스예요.",
         easy="세포막이 속옷이라면 세포벽은 두꺼운 외투예요. 1차벽은 자랄 때 입는 신축성 있는 옷, 2차벽은 다 자란 뒤 덧입는 갑옷이에요.",
         parts=[dict(name="1차 세포벽", draw=draw_primary_wall,
                     structure=["세포가 자라는 동안 만들어지는 **얇고 유연한** 벽이에요.", "셀룰로스 미세섬유가 펙틴 등과 엮인 그물 모양이에요.", "이웃 세포와는 펙틴이 많은 **중간층**으로 붙어 있어요."],
                     role=["세포가 자랄 수 있도록 늘어나는 성질을 유지해요.", "세포를 보호하고 모양을 유지해요."]),
                dict(name="2차 세포벽", draw=draw_secondary_wall,
                     structure=["세포 생장이 끝난 뒤 1차벽 **안쪽(세포막 쪽)** 에 덧붙여져요.", "**두껍고 단단**하며, 셀룰로스 섬유가 방향을 바꿔 가며 여러 층(S1, S2, S3)으로 쌓여요.",
                                "리그닌이 쌓여 더욱 단단해지기도 해요. (목질화)"],
                     role=["강한 지지와 보호를 해요. (나무줄기, 물관 등)", "모든 세포에 있는 것은 아니고, 지지 · 수송 조직의 세포에서 발달해요."])],
         table=("구분", ["1차 세포벽", "2차 세포벽"],
                [("만들어지는 때", "세포가 자라는 동안", "세포 생장이 끝난 뒤"), ("두께 · 성질", "얇고 유연", "두껍고 단단"),
                 ("위치", "바깥쪽 (중간층 바로 안쪽)", "1차벽의 안쪽 (세포막 쪽)"), ("특징", "셀룰로스 + 펙틴 그물", "셀룰로스 여러 층 + 리그닌"),
                 ("있는 세포", "식물 세포 대부분", "지지 · 수송 조직의 세포")])),
    dict(key="세포골격", cat=CAT3, icon="🕸️", color=TEAL, where="모든 진핵세포",
         summary="세포 속에 그물처럼 퍼진 단백질 섬유예요. 세포의 뼈대이자, 물질이 오가는 도로 역할을 해요.",
         easy="건물의 철골(모양 유지)이면서 도로(운반 길)이기도 해요. 굵기가 다른 세 가지 섬유가 역할을 나눠 맡아요.",
         parts=[dict(name="한눈에 보기", draw=draw_cyto_overview,
                     structure=["**미세소관**(가장 굵음) : 핵 근처에서 바깥으로 뻗어 나가는 길이에요.", "**미세섬유**(가장 가늚) : 세포막 안쪽에 많아요.", "**중간섬유**(중간 굵기) : 핵 주변 등을 질기게 받쳐 줘요."],
                     role=["세포의 모양을 유지하고 소기관을 제자리에 고정해요.", "세포가 움직이고 분열할 때 힘을 써요.", "소포와 소기관이 이동하는 길이 돼요."]),
                dict(name="미세소관", draw=draw_microtubule,
                     structure=["**튜불린** 단백질이 이어진 속이 빈 관이에요.", "지름 약 25nm로 세 가지 중 가장 굵어요.", "동물 세포에서는 중심체 근처에서 뻗어 나와요."],
                     role=["소포와 소기관이 이동하는 길이 돼요. (모터 단백질이 걸어 다녀요.)", "세포 분열 때 **방추사**를 이루어 염색체를 끌어당겨요.", "섬모와 편모의 움직임에 관여해요."]),
                dict(name="미세섬유", draw=draw_microfilament,
                     structure=["**액틴** 단백질이 두 가닥으로 꼬인 가는 실이에요.", "지름 약 7nm로 세 가지 중 가장 가늘어요.", "세포막 바로 안쪽에 많이 분포해요."],
                     role=["근육 수축에 관여해요. (미오신과 함께 작용)", "세포의 이동(위족)과 모양 변화를 도와요.", "동물 세포의 세포질 분열 때 잘록하게 조여 주는 고리를 만들어요."]),
                dict(name="중간섬유", draw=draw_intermediate,
                     structure=["케라틴 등 여러 **섬유 단백질**이 밧줄처럼 꼬인 구조예요.", "지름 약 8~12nm로 중간 굵기예요.", "한 번 만들어지면 비교적 안정적이고 질겨요."],
                     role=["세포가 받는 물리적인 힘을 견디게 해 줘요. (기계적 강도)", "핵을 제자리에 고정하고 핵막 안쪽을 받쳐 줘요.", "세포의 모양을 유지해요."])],
         table=("구분", ["미세소관", "미세섬유", "중간섬유"],
                [("구성 단백질", "튜불린", "액틴", "케라틴 등 섬유 단백질"), ("지름", "약 25nm (가장 굵음)", "약 7nm (가장 가늘음)", "약 8~12nm"),
                 ("모양", "속이 빈 관", "두 가닥이 꼬인 실", "밧줄 모양"), ("주요 기능", "물질 이동 길, 방추사, 섬모·편모", "근육 수축, 세포 이동, 세포질 분열", "기계적 강도, 핵 고정")])),
]
BY_KEY = {i["key"]: i for i in ITEMS}

# ══════════════════════════════════════════════
# 스타일
# ══════════════════════════════════════════════
st.markdown(
    """
<style>
.block-container{max-width:1180px;padding-top:2rem;}
.badge{display:inline-block;padding:3px 12px;border-radius:999px;font-size:.85rem;font-weight:600;
  color:var(--c);border:1.5px solid var(--c);margin-right:6px;}
.where{display:inline-block;padding:3px 12px;border-radius:999px;font-size:.85rem;
  background:rgba(128,128,128,.14);}
.pos{text-align:center;opacity:.75;padding-top:.45rem;}
</style>
""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════
# 상태 / 이동
# ══════════════════════════════════════════════
ss = st.session_state


def names_in(cat):
    return [i["key"] for i in ITEMS if cat == ALL or i["cat"] == cat]


ss.setdefault("cat", ALL)
ss.setdefault("item", names_in(ALL)[0])


def on_cat():
    ss.item = names_in(ss.cat)[0]


def step(delta):
    names = names_in(ss.cat)
    ss.item = names[(names.index(ss.item) + delta) % len(names)]


def nav_row(suffix):
    names = names_in(ss.cat)
    p, mid, nx = st.columns([1, 2, 1])
    p.button("◀ 이전", key=f"prev_{suffix}", on_click=step, args=(-1,), use_container_width=True)
    mid.markdown(f'<div class="pos">{names.index(ss.item) + 1} / {len(names)}</div>', unsafe_allow_html=True)
    nx.button("다음 ▶", key=f"next_{suffix}", on_click=step, args=(1,), use_container_width=True)


def show_part(part, multi):
    left, right = st.columns([1.25, 1], vertical_alignment="center")
    left.image(part["draw"]())
    with right:
        if multi:
            st.markdown(f"### {part['name']}")
        st.markdown("**🔎 구조**")
        for s in part["structure"]:
            st.markdown(f"- {s}")
        st.markdown("**⚙️ 하는 일**")
        for s in part["role"]:
            st.markdown(f"- {s}")


# ══════════════════════════════════════════════
# 화면
# ══════════════════════════════════════════════
st.title("🔬 세포 탐색 · 세포소기관")
st.write("세포 속 소기관과 구조물이 어떻게 생겼고 무슨 일을 하는지 그림과 함께 살펴보세요. "
         "분류와 소기관을 고르거나 **이전 / 다음** 버튼으로 하나씩 넘겨 볼 수 있어요.")

with st.expander("🗺️ 세포 지도 : 소기관이 세포 안 어디에 있을까요?"):
    kind = st.radio("세포 종류", ["동물 세포", "식물 세포"], horizontal=True, key="map_kind")
    st.image(draw_animal_map() if kind == "동물 세포" else draw_plant_map())

st.selectbox("🔎 분류", [ALL] + CATS, key="cat", on_change=on_cat)
st.radio("소기관 · 구조", names_in(ss.cat), key="item", horizontal=True)
nav_row("top")

it = BY_KEY[ss.item]
st.divider()
st.markdown(f'<span class="badge" style="--c:{it["color"]}">{it["cat"]}</span><span class="where">📍 {it["where"]}</span>',
            unsafe_allow_html=True)
st.markdown(f"## {it['icon']} {it['key']}")
st.write(it["summary"])
st.info(f"💡 **쉽게 이해하기**  \n{it['easy']}")

parts = it["parts"]
if len(parts) > 1:
    for tab, part in zip(st.tabs([p["name"] for p in parts]), parts):
        with tab:
            show_part(part, True)
else:
    show_part(parts[0], False)

if "table" in it:
    head, cols, rows = it["table"]
    with st.expander("📊 한눈에 비교하기", expanded=True):
        md = "| " + head + " | " + " | ".join(cols) + " |\n|" + "---|" * (len(cols) + 1) + "\n"
        md += "\n".join("| " + " | ".join(r) + " |" for r in rows)
        st.markdown(md)

nav_row("bottom")
