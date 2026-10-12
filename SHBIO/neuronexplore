import streamlit as st

st.set_page_config(page_title="뉴런 탐색 · 신경의 종류", page_icon="🧠", layout="wide")

# ══════════════════════════════════════════════
# SVG 그림 도우미 (그림은 모두 코드로 그려서 별도 이미지 파일이 필요 없어요)
# ══════════════════════════════════════════════
W, H = 720, 400
INK = "#12302c"
FONT = "Noto Sans KR, Malgun Gothic, Apple SD Gothic Neo, sans-serif"
BLUE, ORANGE, RED, TEAL, GREEN, PURPLE = "#3b6fb6", "#e07b39", "#c4475a", "#2f9aa8", "#2f9a6a", "#8a5db3"


def _marker(mid, color):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')


MARKERS = (_marker("aB", BLUE) + _marker("aO", ORANGE) + _marker("aG", "#5b6b66")
           + _marker("aR", RED) + _marker("aV", TEAL))


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="{FONT}"><defs>{MARKERS}</defs>'
            f'<rect width="{W}" height="{H}" rx="18" fill="#f3f8f5"/>{body}</svg>')


def T(x, y, s, size=16, fill=INK, anchor="middle", weight=600):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>')


def box(x, y, w, h, fill, lines, size=16, stroke="#9db6af", color=INK):
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    start = y + h / 2 - (len(lines) - 1) * size * 0.7 + size * 0.35
    for i, s in enumerate(lines):
        out += T(x + w / 2, start + i * size * 1.4, s, size, color)
    return out


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


def pulse(d, color="#ff9f1c", dur="2.6s"):
    """신경 신호를 나타내는 움직이는 점"""
    return (f'<circle r="9" fill="{color}" stroke="#ffffff" stroke-width="2">'
            f'<animateMotion dur="{dur}" repeatCount="indefinite" path="{d}"/></circle>')


def soma(cx, cy, color, light):
    return circle(cx, cy, 24, light, color, 3) + circle(cx, cy, 8, color)


def axon(x1, x2, y, color, light):
    out = line(x1, y, x2, y, color, 5)
    for i in range(int((x2 - x1) // 50)):
        out += (f'<rect x="{x1 + 12 + i * 50}" y="{y - 10}" width="34" height="20" rx="10" '
                f'fill="{light}" stroke="{color}" stroke-width="2"/>')
    return out


# ══════════════════════════════════════════════
# 신경별 그림
# ══════════════════════════════════════════════
def draw_sensory():
    c, l = BLUE, "#cfe0f7"
    b = box(25, 135, 155, 130, "#ffe3d3", ["🔥", "뜨거워!", "피부 · 감각기관"], stroke="#e9a47c")
    b += line(180, 175, 280, 192, c) + line(180, 200, 276, 200, c) + line(180, 225, 280, 208, c)
    b += soma(300, 200, c, l) + axon(324, 520, 200, c, l)
    b += box(520, 125, 175, 150, "#fde2ea", ["중추신경계", "뇌 · 척수"], stroke="#d98aa0")
    b += T(300, 252, "감각신경세포", 14, c)
    b += T(360, 100, "감각신경 (구심성 신경)", 20, c)
    b += line(230, 320, 500, 320, c, 5, "aB") + T(365, 357, "몸 → 뇌와 척수", 18, c)
    return svg(b + pulse("M180,200 L520,200"))


def draw_motor():
    c, l = ORANGE, "#fde0c8"
    b = box(20, 125, 175, 150, "#fde2ea", ["중추신경계", "뇌 · 척수"], stroke="#d98aa0")
    b += line(195, 185, 233, 193, c) + line(195, 200, 231, 200, c) + line(195, 215, 233, 207, c)
    b += soma(255, 200, c, l) + axon(279, 520, 200, c, l)
    b += '<ellipse cx="610" cy="200" rx="90" ry="52" fill="#e76f51" stroke="#b5482a" stroke-width="3"/>'
    for dy in (-26, -9, 9, 26):
        b += path(f"M545,{200 + dy} Q610,{200 + dy - 8} 675,{200 + dy}", "#f6b8a5", 3)
    b += T(610, 206, "근육 · 기관", 17, "#ffffff") + T(610, 290, "수축!", 18, "#b5482a")
    b += T(255, 252, "운동신경세포", 14, c)
    b += T(360, 100, "운동신경 (원심성 신경)", 20, c)
    b += line(230, 320, 500, 320, c, 5, "aO") + T(365, 357, "뇌와 척수 → 근육과 기관", 18, c)
    return svg(b + pulse("M255,200 L525,200"))


def draw_mixed():
    b = box(20, 125, 160, 150, "#ffe3d3", ["몸", "피부 · 근육"], stroke="#e9a47c")
    b += box(540, 125, 160, 150, "#fde2ea", ["중추신경계", "척수"], stroke="#d98aa0")
    b += '<rect x="180" y="140" width="360" height="120" rx="40" fill="#f1e6c8" stroke="#c9b27a" stroke-width="3"/>'
    b += T(360, 120, "혼합신경 (신경다발)", 20, "#8a6d1f")
    b += line(200, 185, 520, 185, BLUE, 5, "aB") + line(520, 225, 200, 225, ORANGE, 5, "aO")
    b += T(360, 298, "🔵 감각 섬유 : 몸 → 중추신경계", 17, BLUE)
    b += T(360, 328, "🟠 운동 섬유 : 중추신경계 → 몸", 17, ORANGE)
    b += T(360, 366, "하나의 신경 속에 두 종류의 섬유가 함께 있어요", 15, "#5b6b66", weight=500)
    return svg(b + pulse("M200,185 L520,185", "#6fa8ff", "2.6s") + pulse("M520,225 L200,225", "#ff9f1c", "2.6s"))


def draw_somatic():
    b = T(360, 62, "운동 : 내가 마음먹고 움직여요", 18, ORANGE)
    b += box(30, 90, 170, 80, "#fde2ea", ["대뇌", "의식적 판단"], stroke="#d98aa0")
    b += box(275, 90, 170, 80, "#fff1c9", ["척수"], stroke="#d9b64a")
    b += box(520, 90, 170, 80, "#ffd9c2", ["골격근", "(수의근)"], stroke="#e9a47c")
    b += line(205, 130, 270, 130, ORANGE, 5, "aO") + line(450, 130, 515, 130, ORANGE, 5, "aO")
    b += T(360, 218, "감각 : 느낀 것은 위로 전달돼요", 18, BLUE)
    b += box(30, 230, 170, 80, "#fde2ea", ["대뇌", "감각 인식"], stroke="#d98aa0")
    b += box(275, 230, 170, 80, "#fff1c9", ["척수"], stroke="#d9b64a")
    b += box(520, 230, 170, 80, "#ffe3d3", ["피부", "촉각 · 통증"], stroke="#e9a47c")
    b += line(515, 270, 450, 270, BLUE, 5, "aB") + line(270, 270, 205, 270, BLUE, 5, "aB")
    b += T(360, 352, "걷기 · 글쓰기 · 물건 잡기  /  피부의 촉각과 통증 감지", 16, INK)
    return svg(b)


def draw_autonomic():
    b = box(260, 12, 200, 52, "#fde2ea", ["뇌 · 척수"], stroke="#d98aa0")
    b += line(320, 66, 200, 116, RED, 4, "aR") + line(400, 66, 520, 116, TEAL, 4, "aV")
    b += box(60, 120, 280, 56, "#fbd5db", ["교감신경", "긴장하거나 위급할 때"], 15, RED)
    b += box(380, 120, 280, 56, "#d5ecf0", ["부교감신경", "휴식과 소화"], 15, TEAL)
    b += box(60, 192, 280, 44, "#ffffff", ["❤️ 심박수를 높여요"], 15, RED)
    b += box(380, 192, 280, 44, "#ffffff", ["❤️ 심박수를 낮춰 안정시켜요"], 15, TEAL)
    b += box(60, 246, 280, 44, "#ffffff", ["🍽️ 소화 활동은 잠시 줄여요"], 15, RED)
    b += box(380, 246, 280, 44, "#ffffff", ["🍽️ 소화를 돕고 에너지를 아껴요"], 15, TEAL)
    b += line(200, 292, 290, 316, "#5b6b66", 3, "aG", "6 5") + line(520, 292, 430, 316, "#5b6b66", 3, "aG", "6 5")
    b += box(110, 316, 500, 62, "#e8f1d9", ["장신경계 : 소화관의 운동과 분비를 조절하는 신경망", "자율신경계와 긴밀하게 상호작용해요"], 15, "#8fb35a")
    return svg(b)


def draw_cns():
    b = '<ellipse cx="360" cy="105" rx="125" ry="66" fill="#f6b8c6" stroke="#c4475a" stroke-width="3"/>'
    b += path("M270,100 q20,-30 45,-8 q20,-25 45,0 q25,-25 45,5 q22,-15 40,10", RED, 3)
    b += path("M285,128 q25,20 50,0 q25,18 50,-2 q25,15 45,-5", RED, 3)
    b += '<ellipse cx="440" cy="160" rx="38" ry="18" fill="#efa0b3" stroke="#c4475a" stroke-width="3"/>'
    for i in range(8):
        b += f'<rect x="325" y="{182 + i * 24}" width="70" height="16" rx="8" fill="#dfe8e4" stroke="#9db6af" stroke-width="2"/>'
    b += '<rect x="349" y="165" width="22" height="215" rx="11" fill="#ffd9a0" stroke="#d9822b" stroke-width="3"/>'
    b += line(250, 100, 160, 100, "#5b6b66", 2, dash="5 4") + T(130, 106, "뇌", 22, RED)
    b += line(372, 280, 560, 280, "#5b6b66", 2, dash="5 4") + T(590, 286, "척수", 22, "#d9822b")
    b += T(150, 205, "감각 정보를 처리하고", 16, INK, "middle", 500) + T(150, 230, "신체의 반응을 조절하는", 16, INK, "middle", 500)
    b += T(150, 255, "중심 역할을 해요", 16, INK, "middle", 500)
    b += T(360, 392, "중추신경계 = 뇌 + 척수", 16, "#5b6b66")
    return svg(b)


def draw_peripheral():
    b = '<rect x="305" y="88" width="110" height="165" rx="40" fill="#e6efeb" stroke="#cddbd5" stroke-width="2"/>'
    b += circle(360, 55, 30, "#ffffff", "#9db6af", 2) + '<ellipse cx="360" cy="50" rx="20" ry="14" fill="#f6b8c6" stroke="#c4475a" stroke-width="2"/>'
    b += line(360, 82, 360, 245, "#e9a0b3", 10)
    for y in (125, 155, 185, 215):
        b += line(360, y, 300, y + 12, GREEN, 3) + line(360, y, 420, y + 12, GREEN, 3)
    b += path("M360,118 Q300,122 255,170 L228,262", GREEN, 5) + path("M360,118 Q420,122 465,170 L492,262", GREEN, 5)
    b += path("M360,245 Q330,300 326,372", GREEN, 5) + path("M360,245 Q390,300 394,372", GREEN, 5)
    b += line(344, 66, 316, 88, GREEN, 4) + line(376, 66, 404, 88, GREEN, 4)
    for x, y in ((228, 262), (492, 262), (326, 372), (394, 372), (316, 88), (404, 88)):
        b += circle(x, y, 6, GREEN)
    b += line(200, 110, 290, 110, "#5b6b66", 2, dash="5 4") + T(190, 106, "뇌신경", 17, GREEN, "end") + T(190, 128, "(머리·얼굴 등)", 14, "#5b6b66", "end", 500)
    b += line(200, 235, 285, 235, "#5b6b66", 2, dash="5 4") + T(190, 231, "척수신경", 17, GREEN, "end") + T(190, 253, "(몸통·팔다리)", 14, "#5b6b66", "end", 500)
    b += circle(540, 100, 8, "#e9a0b3") + T(560, 106, "중추신경계 (뇌 · 척수)", 16, RED, "start")
    b += circle(540, 140, 8, GREEN) + T(560, 146, "말초신경계", 16, GREEN, "start")
    b += T(560, 190, "뇌와 척수에서 뻗어 나와", 15, INK, "start", 500) + T(560, 214, "몸의 각 부위와 중추신경계를", 15, INK, "start", 500)
    b += T(560, 238, "연결해 줘요", 15, INK, "start", 500)
    return svg(b)


def draw_cranial():
    b = circle(250, 195, 150, "#ffffff", "#9db6af", 3)
    b += '<ellipse cx="250" cy="120" rx="95" ry="55" fill="#f6b8c6" stroke="#c4475a" stroke-width="3"/>'
    b += path("M175,115 q20,-26 40,-6 q22,-22 42,0 q22,-22 40,4 q18,-10 30,8", RED, 3)
    b += '<rect x="240" y="170" width="20" height="55" rx="9" fill="#e9a0b3" stroke="#c4475a" stroke-width="2"/>'
    b += circle(205, 215, 13, "#ffffff", INK, 2) + circle(205, 215, 6, INK) + circle(295, 215, 13, "#ffffff", INK, 2) + circle(295, 215, 6, INK)
    b += path("M250,225 L242,255 L258,255", INK, 2) + path("M222,288 q28,20 56,0", INK, 3)
    b += '<ellipse cx="100" cy="215" rx="14" ry="26" fill="#ffe3d3" stroke="#9db6af" stroke-width="2"/>'
    b += path("M250,222 L205,215", BLUE, 3) + path("M250,222 L295,215", BLUE, 3) + path("M250,225 L250,250", GREEN, 3)
    b += path("M244,225 L118,215", PURPLE, 3) + path("M256,225 L330,290 L345,300", ORANGE, 3)
    b += path("M250,230 Q250,330 440,360", RED, 4, arrow="aR")
    b += T(580, 60, "12쌍", 40, GREEN) + T(580, 90, "주로 머리와 얼굴을 담당", 15, INK, "middle", 500)
    items = [(BLUE, "시각신경 : 눈 · 보는 감각"), (GREEN, "후각신경 : 코 · 냄새"), (PURPLE, "청신경 : 귀 · 청각과 평형"),
             (ORANGE, "안면신경 : 얼굴 표정 근육"), (RED, "미주신경 : 심장 · 소화기관 등")]
    for i, (col, s) in enumerate(items):
        b += circle(450, 140 + i * 38, 7, col) + T(468, 146 + i * 38, s, 16, INK, "start", 500)
    b += T(560, 372, "심장 · 소화기관", 15, RED, "start")
    return svg(b)


def draw_spinal():
    groups = [("경신경", 8, BLUE, "목 · 팔"), ("흉신경", 12, GREEN, "가슴 · 등 · 배"),
              ("요신경", 5, ORANGE, "허리 · 다리"), ("천골신경", 5, PURPLE, "엉덩이 · 다리"), ("미골신경", 1, "#8c8c8c", "꼬리뼈 부근")]
    b, y = "", 22
    for name, n, col, region in groups:
        top = y
        for _ in range(n):
            b += f'<rect x="272" y="{y}" width="56" height="9" rx="4" fill="{col}" opacity="0.9"/>'
            b += line(272, y + 4, 238, y + 4, col, 3) + line(328, y + 4, 362, y + 4, col, 3)
            b += circle(238, y + 4, 3, col) + circle(362, y + 4, 3, col)
            y += 11.5
        mid = (top + y) / 2
        b += line(385, top + 1, 385, y - 3, col, 4) + T(402, mid + 5, f"{name} {n}쌍 · {region}", 16, col, "start")
    b += T(120, 200, "합계", 18, INK) + T(120, 240, "31쌍", 40, GREEN)
    b += T(120, 270, "척수에서 나와", 15, INK, "middle", 500) + T(120, 292, "몸통과 팔다리를 담당", 15, INK, "middle", 500)
    return svg(b)


# ══════════════════════════════════════════════
# 신경 자료 (주어진 자료를 바탕으로 정리)
# ══════════════════════════════════════════════
CAT1 = "① 기능에 따른 신경"
CAT2 = "② 조절하는 기능에 따른 신경"
CAT3 = "③ 위치에 따른 신경"
CAT4 = "④ 뇌신경과 척수신경"
ALL = "전체 보기"
CATS = [CAT1, CAT2, CAT3, CAT4]

NERVES = [
    dict(key="감각신경", cat=CAT1, icon="🖐️", color=BLUE, draw=draw_sensory, aka="구심성 신경",
         flow="몸 → 뇌와 척수",
         summary="피부나 감각기관에서 받아들인 정보를 중추신경계로 전달해요.",
         points=[("예시", "뜨거운 냄비를 만졌을 때 뜨겁다고 느끼는 것"), ("주요 기능", "촉각, 통증, 온도, 압력 등의 감각 전달")],
         easy="감각신경은 몸 곳곳에서 소식을 모아 본부(뇌와 척수)로 알려 주는 '제보자'예요."),
    dict(key="운동신경", cat=CAT1, icon="🏃", color=ORANGE, draw=draw_motor, aka="원심성 신경",
         flow="뇌와 척수 → 근육과 기관",
         summary="중추신경계의 명령을 근육이나 여러 기관에 전달해요.",
         points=[("예시", "손을 움직이거나 다리를 들어 올리는 것"), ("주요 기능", "근육 수축 및 움직임 조절")],
         easy="운동신경은 본부의 작전 명령을 현장(근육)에 전하는 '전령'이에요."),
    dict(key="혼합신경", cat=CAT1, icon="🔀", color="#b8932b", draw=draw_mixed, aka="감각 + 운동",
         flow="한 신경 안에서 양방향으로 전달",
         summary="감각신경 섬유와 운동신경 섬유를 모두 포함해요.",
         points=[("예시", "척수신경 대부분"), ("주요 기능", "감각 정보를 전달하고 운동 명령도 전달")],
         easy="왕복 2차선 도로를 떠올려 보세요. 한쪽은 감각 신호가, 반대쪽은 운동 명령이 달려요."),
    dict(key="체성신경계", cat=CAT2, icon="🚶", color=ORANGE, draw=draw_somatic, aka="의식적으로 조절",
         flow="의식적인 감각과 골격근의 수의적 움직임",
         summary="의식적으로 느끼는 감각과 골격근의 수의적 움직임을 담당해요.",
         points=[("운동", "걷기, 글쓰기, 물건 잡기"), ("감각", "피부의 촉각과 통증 감지")],
         easy="'내가 하자!' 하고 마음먹고 하는 행동과, 내가 느끼는 감각을 맡는 신경이에요."),
    dict(key="자율신경계", cat=CAT2, icon="❤️", color=RED, draw=draw_autonomic, aka="교감 · 부교감 · 장신경계",
         flow="의식하지 않아도 자동으로 조절",
         summary="의식적으로 일일이 명령하지 않아도 심장, 소화기관, 땀샘 등의 기능을 조절해요.",
         points=[("교감신경", "긴장하거나 위급할 때 심박수를 높이고 신체가 대응하도록 도와요."),
                 ("부교감신경", "휴식과 소화를 촉진하고 에너지 보존을 도와요."),
                 ("장신경계", "소화관의 운동과 분비를 조절하는 신경망으로, 자율신경계와 긴밀하게 상호작용해요.")],
         easy="자동 조절 장치예요. 교감신경은 '액셀', 부교감신경은 '브레이크'라고 생각하면 쉬워요."),
    dict(key="중추신경계", cat=CAT3, icon="🧠", color=RED, draw=draw_cns, aka="뇌 + 척수",
         flow="신경계의 중심",
         summary="뇌와 척수로 구성되며, 감각 정보를 처리하고 신체의 반응을 조절하는 중심 역할을 해요.",
         points=[("구성", "뇌, 척수"), ("역할", "감각 정보 처리, 신체 반응 조절")],
         easy="전체 신경계의 '사령부'예요. 정보가 모이고 명령이 나와요."),
    dict(key="말초신경계", cat=CAT3, icon="🕸️", color=GREEN, draw=draw_peripheral, aka="뇌신경 + 척수신경 등",
         flow="중추신경계 ↔ 몸의 각 부위",
         summary="뇌와 척수에서 뻗어 나와 몸의 각 부위와 중추신경계를 연결해요.",
         points=[("포함", "뇌신경, 척수신경 등"), ("역할", "몸과 중추신경계 사이의 연결")],
         easy="사령부와 각 지역을 이어 주는 '도로망'이에요."),
    dict(key="뇌신경", cat=CAT4, icon="👁️", color=GREEN, draw=draw_cranial, aka="12쌍",
         flow="뇌에서 시작되는 말초신경",
         summary="주로 머리와 얼굴의 감각·운동을 담당하며, 일부는 심장과 소화기관 등에도 관여해요.",
         points=[("개수", "12쌍"), ("예시", "시각을 담당하는 시신경은 뇌신경 중 하나예요.")],
         easy="뇌에서 곧바로 나와 머리와 얼굴로 가는 '직통 배선'이에요."),
    dict(key="척수신경", cat=CAT4, icon="🦴", color=PURPLE, draw=draw_spinal, aka="31쌍",
         flow="척수에서 시작되는 말초신경",
         summary="척수에서 나와 몸통과 팔다리의 감각 및 운동을 담당해요.",
         points=[("개수", "31쌍"), ("예시", "팔과 손의 움직임 및 감각에는 여러 척수신경에서 나온 신경들이 관여해요.")],
         easy="척수라는 큰 줄기에서 좌우로 뻗어 나가는 31쌍의 '가지'예요."),
]
BY_KEY = {n["key"]: n for n in NERVES}

CRANIAL = [("1", "후각신경", "냄새를 느껴요"), ("2", "시각신경(시신경)", "빛 자극을 뇌로 전달해 보게 해요"),
           ("3", "동안신경", "눈동자 크기와 안구 움직임"), ("4", "활차신경", "안구를 움직여요"),
           ("5", "삼차신경", "얼굴의 감각, 음식을 씹는 운동"), ("6", "외전신경", "안구를 바깥쪽으로 움직여요"),
           ("7", "안면신경", "얼굴 표정 근육, 혀 앞쪽 맛"), ("8", "청신경", "청각과 평형 감각"),
           ("9", "설인신경", "혀 뒤쪽 맛, 삼키기"), ("10", "미주신경", "심장·소화기관 등 여러 내장 기관 조절"),
           ("11", "부신경", "목과 어깨 근육 운동"), ("12", "설하신경", "혀의 움직임")]
SPINAL = [("경신경", "8쌍", "목 · 팔"), ("흉신경", "12쌍", "가슴 · 등 · 배"), ("요신경", "5쌍", "허리 · 다리"),
          ("천골신경", "5쌍", "엉덩이 · 다리"), ("미골신경", "1쌍", "꼬리뼈 부근")]

# ══════════════════════════════════════════════
# 스타일
# ══════════════════════════════════════════════
st.markdown(
    """
<style>
.block-container{max-width:1180px;padding-top:2rem;}
.badge{display:inline-block;padding:3px 12px;border-radius:999px;font-size:.85rem;font-weight:600;
  color:var(--c);border:1.5px solid var(--c);}
.flow{display:inline-block;margin:.2rem 0 .6rem;padding:6px 14px;border-radius:10px;font-weight:600;
  background:rgba(128,128,128,.12);border-left:5px solid var(--c);}
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
    return [n["key"] for n in NERVES if cat == ALL or n["cat"] == cat]


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


# ══════════════════════════════════════════════
# 화면
# ══════════════════════════════════════════════
st.title("🧠 뉴런 탐색 · 신경의 종류")
st.write("신경은 뇌와 척수의 명령을 전달하고, 외부 자극을 감지하며, 몸의 여러 기관이 제대로 기능하도록 도와요. "
         "분류 기준과 신경을 고르거나 **이전 / 다음** 버튼으로 하나씩 살펴보세요.")

st.selectbox("🔎 분류 기준", [ALL] + CATS, key="cat", on_change=on_cat)
st.radio("신경 종류", names_in(ss.cat), key="item", horizontal=True)
nav_row("top")

n = BY_KEY[ss.item]
st.divider()
left, right = st.columns([1.25, 1], vertical_alignment="center")

with left:
    st.image(n["draw"]())

with right:
    st.markdown(f'<span class="badge" style="--c:{n["color"]}">{n["cat"]}</span>', unsafe_allow_html=True)
    st.markdown(f"## {n['icon']} {n['key']}  \n<small>{n['aka']}</small>", unsafe_allow_html=True)
    st.markdown(f'<div class="flow" style="--c:{n["color"]}">{n["flow"]}</div>', unsafe_allow_html=True)
    st.write(n["summary"])
    for label, text in n["points"]:
        st.markdown(f"- **{label}** : {text}")
    st.info(f"💡 **쉽게 이해하기**  \n{n['easy']}")

if n["key"] == "뇌신경":
    with st.expander("🧾 뇌신경 12쌍 이름과 기능 보기"):
        rows = "| 번호 | 이름 | 주요 기능 |\n|---|---|---|\n" + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in CRANIAL)
        st.markdown(rows)

if n["key"] == "척수신경":
    with st.expander("🧾 척수신경 31쌍의 구성 보기"):
        rows = "| 구분 | 개수 | 담당 부위 |\n|---|---|---|\n" + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in SPINAL)
        st.markdown(rows + "\n\n8 + 12 + 5 + 5 + 1 = **31쌍**")

nav_row("bottom")

with st.expander("📌 한눈에 정리하기", expanded=False):
    st.markdown(
        "- **감각신경** : 자극을 뇌와 척수로 전달해요.\n"
        "- **운동신경** : 명령을 근육과 기관으로 전달해요.\n"
        "- **자율신경** : 심장 박동, 소화, 땀 분비 등을 자동으로 조절해요.\n\n"
        "**핵심** : 감각신경은 정보를 받아들이고, 운동신경은 반응을 전달하며, "
        "자율신경은 몸속 기관의 기능을 자동으로 조절해요."
    )
