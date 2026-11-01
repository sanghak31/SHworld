import streamlit as st

st.set_page_config(page_title="계통수 탐색 · 동물과 식물", page_icon="🌳", layout="wide")

# ══════════════════════════════════════════════
# 계통수 자료
#   N(이름, 아이콘, 한 줄 설명, [이 계통에서 새로 생긴 특징], 대표 생물, 가지 표시, [자식 계통])
# ══════════════════════════════════════════════
def N(name, icon, summary, new, eg="", tag="", kids=()):
    return dict(name=name, icon=icon, summary=summary, new=list(new), eg=eg, tag=tag, kids=list(kids))


ANIMAL = N("동물", "🐾", "다른 생물을 먹고 사는 다세포 생물이에요.",
           ["다세포 생물이에요.", "스스로 양분을 만들지 못하고 다른 생물을 먹어요 (종속 영양).", "세포벽이 없어요.", "대부분 몸을 움직여 이동해요. (일부는 한곳에 붙어 살아요.)"],
           "모든 동물", "", [
    N("해면동물", "🧽", "조직이 없는 가장 단순한 동물이에요.",
      ["조직과 기관이 분화되지 않았어요.", "깃세포(동공세포)가 물을 걸러 먹이를 먹어요.", "몸에 입수공과 출수공(구멍)이 있어요.", "어른은 바위 등에 붙어 살아요 (고착 생활)."],
      "해면, 목욕해면, 컵해면"),
    N("진정후생동물", "🧬", "세포가 모여 조직을 이루는 동물이에요.",
      ["세포가 모여 조직을 만들어요.", "신경 조직과 근육 조직이 생겼어요.", "소화를 위한 공간(소화관)이 생겼어요."],
      "자포동물에서 사람까지", "조직", [
        N("자포동물", "🪼", "독침 세포로 먹이를 잡는 방사 대칭 동물이에요.",
          ["몸이 방사 대칭이에요.", "배엽이 2개(외배엽, 내배엽)예요.", "독침이 있는 자포 세포로 먹이를 잡아요.", "입과 항문의 구분이 없는 소화 순환강(강장)이 있어요."],
          "히드라, 해파리, 말미잘, 산호"),
        N("좌우대칭동물", "⚖️", "몸이 좌우대칭이고 머리가 생긴 동물이에요.",
          ["몸이 좌우대칭이에요.", "배엽이 3개(외배엽, 중배엽, 내배엽)예요.", "머리가 생기고 감각 기관이 머리에 모여요.", "방향을 정해 이동하기에 유리해요."],
          "자포동물을 뺀 거의 모든 동물", "좌우대칭", [
            N("선구동물", "🧩", "발생 때 원구(첫 구멍)가 입이 되는 동물이에요.",
              ["배아 발생 때 원구가 입이 돼요.", "항문은 나중에 새로 생겨요."],
              "연체동물, 환형동물, 절지동물 등", "원구→입", [
                N("촉수담륜동물", "🐚", "촉수관 또는 담륜자 유생을 가진 무리가 많아요.",
                  ["촉수관이나 담륜자(트로코포라)라는 구조를 가진 무리가 많아요.", "허물을 벗지 않고 자라요."],
                  "편형동물, 환형동물, 연체동물", "허물 안 벗음", [
                    N("편형동물", "🐛", "몸이 납작하고 항문이 없는 동물이에요.",
                      ["몸이 납작해요.", "체강이 없어요 (무체강).", "항문이 없어 입으로 노폐물을 내보내요.", "몸에 체절이 없어요."],
                      "플라나리아, 촌충, 간흡충"),
                    N("환형동물", "🪱", "몸이 고리 모양 체절로 나뉜 동물이에요.",
                      ["몸이 고리 모양의 체절로 이루어져 있어요.", "체강(진체강)이 발달했어요.", "혈액이 혈관 속으로만 흐르는 폐쇄 혈관계가 있어요.", "입과 항문이 구분된 완전한 소화관이 있어요."],
                      "지렁이, 거머리, 갯지렁이"),
                    N("연체동물", "🐌", "몸이 부드럽고 외투막과 근육질 발이 있어요.",
                      ["몸이 부드럽고 외투막으로 덮여 있어요.", "근육질의 발이 있어요.", "많은 종이 석회질 껍데기를 가져요. (일부는 퇴화했어요.)", "몸에 체절이 없어요."],
                      "달팽이, 조개, 오징어, 문어"),
                ]),
                N("탈피동물", "🦐", "단단한 외피를 벗으며 자라는 동물이에요.",
                  ["단단한 큐티클(외피)을 가지고, 성장하면서 허물을 벗어요 (탈피)."],
                  "선형동물, 절지동물", "탈피", [
                    N("선형동물", "🧵", "가늘고 긴 원통형 몸을 가진 동물이에요.",
                      ["몸이 가늘고 긴 원통형이에요.", "체강이 불완전한 의체강이에요.", "입과 항문이 구분된 소화관이 있어요.", "몸이 큐티클로 덮여 있어요."],
                      "회충, 요충, 예쁜꼬마선충"),
                    N("절지동물", "🦋", "마디가 있는 다리와 외골격을 가진, 가장 종류가 많은 동물이에요.",
                      ["몸이 체절로 나뉘고, 마디가 있는 부속지(다리 등)를 가져요.", "키틴질 외골격으로 몸을 보호해요.", "성장하려면 허물을 벗어요 (탈피).", "혈액이 혈관 밖으로 흐르는 개방 혈관계예요."],
                      "곤충(다리 3쌍), 거미(다리 4쌍), 게, 새우"),
                ]),
            ]),
            N("후구동물", "🔁", "발생 때 원구가 항문이 되는 동물이에요.",
              ["배아 발생 때 원구가 항문이 돼요.", "입은 나중에 새로 생겨요."],
              "극피동물, 척삭동물", "원구→항문", [
                N("극피동물", "⭐", "오각 방사 대칭의 몸과 가시 있는 피부를 가진 동물이에요.",
                  ["성체의 몸이 오각 방사 대칭이에요. (유생은 좌우대칭이에요.)", "석회질 골편으로 된 내골격과 가시가 있어요.", "수관계와 관족(관 모양 발)으로 움직여요."],
                  "불가사리, 성게, 해삼, 갯고사리"),
                N("척삭동물", "🧠", "일생 중 척삭과 등쪽 신경관을 가지는 동물이에요.",
                  ["척삭이 있어요 (발생 시기에라도).", "속이 빈 등쪽 신경관이 있어요.", "인두 틈이 있어요.", "항문 뒤쪽으로 뻗은 꼬리가 있어요."],
                  "창고기, 멍게, 척추동물 (이 계통수에서는 창고기·멍게를 생략했어요.)", "척삭", [
                    N("척추동물", "🦴", "척추뼈와 두개골을 가진 척삭동물이에요.",
                      ["척삭이 척추뼈로 대체돼 척추가 생겨요.", "두개골이 뇌를 보호해요.", "심장이 발달한 폐쇄 혈관계가 있어요.", "신경계와 감각 기관이 발달했어요."],
                      "어류, 양서류, 파충류, 조류, 포유류", "척추", [
                        N("어류", "🐟", "아가미로 호흡하며 물속에서 사는 척추동물이에요.",
                          ["아가미로 호흡해요.", "지느러미로 헤엄쳐요.", "몸이 비늘로 덮인 경우가 많아요.", "체온이 주변 온도에 따라 변하는 변온 동물이에요.", "대부분 물속에 알을 낳아요 (체외 수정)."],
                          "붕어, 상어, 연어, 가오리"),
                        N("양서류", "🐸", "변태를 하며 물과 육지를 오가는 척추동물이에요.",
                          ["유생은 아가미, 성체는 폐와 피부로 호흡해요 (변태).", "껍데기가 없는 알을 물속에 낳아요.", "피부가 얇고 축축해요.", "변온 동물이에요.", "네 다리(사지)로 육지를 걸어요."],
                          "개구리, 도롱뇽, 두꺼비"),
                        N("양막동물", "🥚", "양막으로 싸인 알로 육지에서 번식하는 무리예요.",
                          ["양막으로 싸인 알(또는 배)로 건조한 육지에서도 번식할 수 있어요.", "폐로 호흡해요.", "피부가 마르지 않도록 비늘, 털, 깃털 등이 있어요."],
                          "파충류, 조류, 포유류", "양막", [
                            N("파충류", "🦎", "단단한 비늘과 양막란을 가진 변온 동물이에요.",
                              ["피부가 단단한 비늘로 덮여 있어요.", "껍데기가 있는 알(양막란)을 육지에 낳아요.", "폐로 호흡해요.", "변온 동물이에요."],
                              "뱀, 도마뱀, 거북, 악어"),
                            N("조류", "🐦", "깃털과 날개를 가진 항온 동물이에요.",
                              ["깃털과 날개가 있어요.", "체온이 일정한 항온 동물이에요.", "속이 빈 뼈와 부리가 있어 몸이 가벼워요.", "껍데기가 단단한 알을 낳아요. (파충류, 특히 공룡과 가까운 친척이에요.)"],
                              "참새, 닭, 펭귄, 독수리"),
                            N("포유류", "🐘", "젖을 먹여 새끼를 키우는 털 있는 항온 동물이에요.",
                              ["젖샘이 있어서 새끼에게 젖을 먹여요.", "몸에 털이 있어요.", "체온이 일정한 항온 동물이에요.", "대부분 새끼를 낳아요 (태생).", "가로막(횡격막)이 있어 호흡을 도와요."],
                              "사람, 고래, 박쥐, 캥거루"),
                        ]),
                    ]),
                ]),
            ]),
        ]),
    ]),
])

PLANT = N("녹색식물", "🌿", "엽록체로 광합성을 하는 식물과 그 친척이에요.",
          ["엽록소 a와 b가 있는 엽록체로 광합성을 해요.", "세포벽이 셀룰로스로 되어 있어요.", "녹말을 저장해요."],
          "녹조류와 모든 육상식물", "", [
    N("녹조류", "🌊", "물속에서 사는, 식물의 가장 가까운 조상 무리예요.",
      ["대부분 물속이나 습한 곳에서 살아요.", "몸이 단순해서 뿌리, 줄기, 잎이 구분되지 않아요.", "단세포부터 다세포까지 다양해요.", "그중 윤조류(차축조류)가 육상식물과 가장 가까운 친척이에요."],
      "클로렐라, 파래, 청각, 차축조류"),
    N("육상식물", "🌱", "물에서 육지로 올라온 식물이에요.",
      ["어린 식물(배)을 어미 몸 안에서 보호하며 키워요.", "몸 표면에 큐티클층이 있어 수분이 증발하는 것을 막아요.", "배우체 세대와 포자체 세대가 번갈아 나타나요 (세대 교번).", "포자의 벽이 단단해 건조한 곳에서도 견뎌요."],
      "이끼부터 장미까지", "배·큐티클", [
        N("선태식물", "🍃", "관다발이 없는 작은 식물이에요.",
          ["관다발(물관·체관)이 없어요.", "뿌리, 줄기, 잎의 구분이 없고 헛뿌리(가근)가 있어요.", "우리가 보는 식물체가 배우체예요 (배우체 우세).", "정자가 물속을 헤엄쳐 수정하므로 습한 곳에서 살아요.", "키가 작아요."],
          "이끼, 우산이끼, 솔이끼"),
        N("관속식물", "🌴", "물관과 체관(관다발)이 있는 식물이에요.",
          ["물관과 체관으로 된 관다발이 있어 물과 양분을 멀리 보내요.", "진짜 뿌리와 줄기가 있어요.", "포자체 세대가 우세해요 (우리가 보는 식물체가 포자체예요).", "리그닌으로 몸을 지탱해 키가 크게 자랄 수 있어요."],
          "석송류, 양치식물, 종자식물", "관다발", [
            N("석송류", "🪴", "작은 잎을 가진 씨 없는 관속식물이에요.",
              ["작은 잎(소엽)이에요. (잎맥이 하나예요.)", "씨가 없고 포자로 번식해요.", "포자낭이삭에 포자가 들어 있어요.", "정자가 물이 있어야 수정해요."],
              "석송, 부처손, 물부추"),
            N("큰잎 식물", "🍂", "잎맥이 갈라진 큰 잎을 가진 무리예요.",
              ["잎맥이 여러 갈래로 갈라진 큰 잎(대엽)이 생겼어요.", "광합성을 많이 할 수 있어 몸이 커져요."],
              "양치식물, 종자식물", "큰 잎", [
                N("양치식물", "🌿", "씨 없이 포자로 번식하는 큰잎 식물이에요.",
                  ["씨가 없고 포자로 번식해요.", "배우체(전엽체)가 작지만 독립해서 살아요.", "정자가 물속에서 헤엄쳐 수정하므로 습한 곳에서 살아요.", "어린잎이 돌돌 말려 있어요 (고사리순)."],
                  "고사리, 고비, 쇠뜨기, 관중"),
                N("종자식물", "🌰", "씨(종자)로 번식하는 식물이에요.",
                  ["씨(종자)로 번식해요 (배, 저장 양분, 씨껍질).", "꽃가루가 정자를 운반해 물 없이도 수정해요.", "배우체가 아주 작아져 포자체 안에서 자라요.", "씨가 단단한 껍질에 싸여 건조한 곳에서도 퍼질 수 있어요."],
                  "겉씨식물, 속씨식물", "씨", [
                    N("겉씨식물", "🌲", "밑씨가 겉으로 드러나 있는 종자식물이에요.",
                      ["밑씨가 씨방에 싸이지 않고 겉으로 드러나 있어요.", "꽃이 없고 구과(방울열매)에 씨가 달려요.", "꽃가루가 주로 바람에 날려 옮겨져요.", "중복 수정을 하지 않아요."],
                      "소나무, 잣나무, 은행나무, 소철"),
                    N("속씨식물", "🌸", "꽃과 열매를 가진, 가장 번성한 식물이에요.",
                      ["꽃이라는 생식 기관이 있어요.", "밑씨가 씨방 속에 들어 있어요.", "중복 수정을 해서 배젖이 만들어져요.", "씨방이 자라 열매가 되어 씨를 보호하고 퍼뜨려요.", "육상식물 중 가장 종류가 많아요."],
                      "장미, 벼, 사과, 민들레", "꽃·열매", [
                        N("외떡잎식물", "🌾", "떡잎이 1장인 속씨식물이에요.",
                          ["떡잎이 1장이에요.", "잎맥이 나란히맥이에요.", "수염뿌리가 있어요.", "관다발이 줄기에 흩어져 있어요.", "꽃잎이 3의 배수인 경우가 많아요."],
                          "벼, 옥수수, 보리, 백합, 난초"),
                        N("쌍떡잎식물", "🌻", "떡잎이 2장인 속씨식물이에요.",
                          ["떡잎이 2장이에요.", "잎맥이 그물맥이에요.", "원뿌리와 곁뿌리가 있어요.", "관다발이 고리 모양으로 배열되고 부름켜가 있어 줄기가 굵어져요.", "꽃잎이 4 또는 5의 배수인 경우가 많아요."],
                          "장미, 콩, 해바라기, 감나무"),
                    ]),
                ]),
            ]),
        ]),
    ]),
])


class Tree:
    def __init__(self, root, color):
        self.root, self.color = root, color
        self.node, self.parent, self.depth, self.order = {}, {}, {}, []
        self._walk(root, None, 0)
        self.leaves = [n for n in self.order if not self.node[n]["kids"]]

    def _walk(self, n, p, d):
        nm = n["name"]
        self.node[nm], self.parent[nm], self.depth[nm] = n, p, d
        self.order.append(nm)
        for k in n["kids"]:
            self._walk(k, nm, d + 1)

    def path(self, name):                      # 뿌리 → name
        out = []
        while name:
            out.append(name)
            name = self.parent[name]
        return out[::-1]

    def descendants(self, name):
        out = []
        for k in self.node[name]["kids"]:
            out += [k["name"]] + self.descendants(k["name"])
        return out

    def mrca(self, a, b):
        pa, pb, last = self.path(a), self.path(b), None
        for x, y in zip(pa, pb):
            if x != y:
                break
            last = x
        return last


TREES = {"🐾 동물": Tree(ANIMAL, "#c4475a"), "🌿 식물": Tree(PLANT, "#2f9a6a")}

# ══════════════════════════════════════════════
# 계통수 그리기 (SVG)
# ══════════════════════════════════════════════
INK, GRAY, GOLD = "#12302c", "#9aa5a1", "#e0a31b"
BLUE, ORANGE = "#3b6fb6", "#e07b39"
X0, DX, ROW, Y0, PH = 70, 112, 36, 44, 26
FONT = "Noto Sans KR, Malgun Gothic, Apple SD Gothic Neo, sans-serif"


def tw(s, size=13):
    return sum(size * 0.6 if ord(c) < 128 else size for c in s) + 24


def layout(t):
    maxd = max(t.depth[n] for n in t.order if t.node[n]["kids"])
    xl = X0 + (maxd + 1) * DX
    pos = {}
    for i, n in enumerate(t.leaves):
        pos[n] = [xl, Y0 + i * ROW]

    def rec(nm):
        kids = [k["name"] for k in t.node[nm]["kids"]]
        if not kids:
            return
        for k in kids:
            rec(k)
        pos[nm] = [X0 + t.depth[nm] * DX, (pos[kids[0]][1] + pos[kids[-1]][1]) / 2]

    rec(t.root["name"])
    return pos, xl, Y0 + len(t.leaves) * ROW + 16


def tint(hex_, a=0.18):
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(int(255 * (1 - a) + c * a) for c in (r, g, b))


def draw_tree(t, mode, show_tags=True):
    """mode : {'sel': 이름}  또는  {'a': 이름, 'b': 이름}"""
    pos, xl, height = layout(t)
    W = int(xl + 150)
    nodes = {n: dict(fill="#ffffff", stroke=GRAY, txt=INK, label=None) for n in t.order}
    edges = {n: (GRAY, 3.0) for n in t.order if t.parent[n]}   # 부모에서 n으로 가는 가지

    if "sel" in mode:
        sel = mode["sel"]
        path, sub = t.path(sel), t.descendants(sel)
        for n in sub:
            nodes[n].update(stroke=t.color, fill=tint(t.color, 0.07))
            edges[n] = (tint(t.color, 0.55), 4.0)
        for n in path:
            nodes[n].update(stroke=t.color, fill=tint(t.color, 0.22))
            if n in edges:
                edges[n] = (t.color, 5.5)
        nodes[sel].update(fill=t.color, stroke=INK, txt="#ffffff")
    else:
        a, b = mode["a"], mode["b"]
        m = t.mrca(a, b)
        for n in t.path(m):
            nodes[n].update(stroke="#2f9a6a", fill=tint("#2f9a6a", 0.2))
            if n in edges:
                edges[n] = ("#2f9a6a", 5.5)
        for who, col in ((a, BLUE), (b, ORANGE)):
            for n in t.path(who)[t.path(who).index(m) + 1:]:
                nodes[n].update(stroke=col, fill=tint(col, 0.2))
                edges[n] = (col, 5.5)
        nodes[a].update(fill=BLUE, stroke=INK, txt="#ffffff")
        nodes[b].update(fill=ORANGE, stroke=INK, txt="#ffffff")
        nodes[m].update(fill=GOLD, stroke=INK, txt="#ffffff", label="★ " + m)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" font-family="{FONT}">',
           f'<rect width="{W}" height="{height}" rx="18" fill="#f3f8f5"/>']
    for n in sorted(edges, key=lambda k: edges[k][1]):                   # 굵은 가지를 위에 그려요
        p, c = t.parent[n], n
        col, w = edges[n]
        (xp, yp), (xc, yc) = pos[p], pos[c]
        out.append(f'<path d="M{xp:.1f},{yp:.1f} L{xp:.1f},{yc:.1f} L{xc:.1f},{yc:.1f}" fill="none" stroke="{col}" '
                   f'stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    for n in t.order:
        x, y = pos[n]
        st_ = nodes[n]
        leaf = not t.node[n]["kids"]
        text = st_["label"] or (t.node[n]["icon"] + " " + n if leaf else n)
        w = tw(text) + (6 if leaf else 0)
        left = x if leaf else x - w / 2
        out.append(f'<rect x="{left:.1f}" y="{y - PH / 2:.1f}" width="{w:.1f}" height="{PH}" rx="13" fill="{st_["fill"]}" '
                   f'stroke="{st_["stroke"]}" stroke-width="2.5"/>')
        out.append(f'<text x="{left + w / 2:.1f}" y="{y + 4.5:.1f}" font-size="13" font-weight="700" fill="{st_["txt"]}" '
                   f'text-anchor="middle">{text}</text>')
        tag = t.node[n]["tag"]
        if show_tags and tag and not leaf:
            out.append(f'<text x="{x:.1f}" y="{y + PH / 2 + 13:.1f}" font-size="11.5" font-weight="600" fill="#7a5a00" text-anchor="middle" '
                       f'paint-order="stroke" stroke="#f3f8f5" stroke-width="4">◆ {tag}</text>')
    out.append("</svg>")
    return "".join(out)


# ══════════════════════════════════════════════
# 상태
# ══════════════════════════════════════════════
ss = st.session_state
ss.setdefault("tree", "🐾 동물")
ss.setdefault("node", ANIMAL["name"])
ss.setdefault("show_tags", True)


def on_tree():
    t = TREES[ss.tree]
    ss.node = t.root["name"]
    ss.cmpA, ss.cmpB = t.leaves[0], t.leaves[-1]


def step(d):
    names = TREES[ss.tree].order
    ss.node = names[(names.index(ss.node) + d) % len(names)]


# ══════════════════════════════════════════════
# 화면
# ══════════════════════════════════════════════
st.markdown("""
<style>
.block-container{max-width:1180px;padding-top:2rem;}
.crumb{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:.2rem 0 .6rem;}
.crumb span{padding:3px 11px;border-radius:999px;background:rgba(128,128,128,.14);font-size:.9rem;}
.crumb b{padding:3px 12px;border-radius:999px;color:#fff;font-size:.9rem;}
</style>""", unsafe_allow_html=True)

st.title("🌳 계통수 탐색 · 동물과 식물")
st.write("**계통수**는 생물들이 어떤 공통 조상에서 갈라져 나왔는지를 나뭇가지 모양으로 나타낸 그림이에요. "
         "가지가 갈라지는 곳(마디)은 **공통 조상**이고, 어떤 가지에서 새로 생겨 그 아래 후손들이 물려받는 특징을 **파생 형질**이라고 해요.")

top1, top2 = st.columns([2, 1], vertical_alignment="center")
top1.radio("계통수 종류", list(TREES), horizontal=True, key="tree", on_change=on_tree)
top2.toggle("가지에 파생 형질 표시 (◆)", key="show_tags")

tree = TREES[ss.tree]
names = tree.order
if ss.node not in names:
    ss.node = tree.root["name"]
ss.setdefault("cmpA", tree.leaves[0])
ss.setdefault("cmpB", tree.leaves[-1])
if ss.cmpA not in names or ss.cmpB not in names:
    ss.cmpA, ss.cmpB = tree.leaves[0], tree.leaves[-1]


def fmt(n):
    return "　" * tree.depth[n] + ("└ " if tree.depth[n] else "") + tree.node[n]["icon"] + " " + n


tab1, tab2, tab3 = st.tabs(["🌳 계통 탐색", "🔎 공통 조상 찾기", "📋 한눈에 비교"])

# ── 1. 계통 탐색 ─────────────────────────────
with tab1:
    n1, n2, n3 = st.columns([1, 4, 1], vertical_alignment="bottom")
    n1.button("◀ 이전", on_click=step, args=(-1,), key="prev", use_container_width=True)
    n2.selectbox("살펴볼 계통", names, format_func=fmt, key="node")
    n3.button("다음 ▶", on_click=step, args=(1,), key="next", use_container_width=True)
    st.image(draw_tree(tree, {"sel": ss.node}, ss.show_tags))

    nd = tree.node[ss.node]
    path = tree.path(ss.node)
    crumbs = " → ".join(f"<span>{p}</span>" if p != ss.node else f'<b style="background:{tree.color}">{p}</b>' for p in path)
    st.markdown(f'<div class="crumb">{crumbs}</div>', unsafe_allow_html=True)
    st.markdown(f"## {nd['icon']} {nd['name']}")
    st.write(nd["summary"])
    if nd["eg"]:
        st.markdown(f"**대표 생물** · {nd['eg']}")
    sub = [tree.node[x]["name"] for x in tree.descendants(ss.node) if not tree.node[x]["kids"]]
    if nd["kids"]:
        st.markdown("**이 계통에 속한 무리** · " + ", ".join(sub))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### 🆕 {nd['name']}에서 새로 생긴 특징")
        for s in nd["new"]:
            st.markdown(f"- {s}")
    with c2:
        st.markdown("#### 🧬 조상에게서 물려받은 특징")
        anc = path[:-1]
        if not anc:
            st.caption("가장 처음 갈라진 공통 조상이에요.")
        for a in anc:
            with st.expander(f"{tree.node[a]['icon']} {a} 에서 생긴 특징", expanded=False):
                for s in tree.node[a]["new"]:
                    st.markdown(f"- {s}")

# ── 2. 공통 조상 찾기 ────────────────────────
with tab2:
    st.write("두 계통을 골라 보세요. 두 계통이 갈라져 나온 **가장 가까운 공통 조상**을 찾아 드려요.")
    q1, q2 = st.columns(2)
    q1.selectbox("🔵 계통 A", names, format_func=fmt, key="cmpA")
    q2.selectbox("🟠 계통 B", names, format_func=fmt, key="cmpB")
    a, b = ss.cmpA, ss.cmpB
    if a == b:
        st.warning("서로 다른 계통을 골라 주세요.")
    else:
        m = tree.mrca(a, b)
        st.image(draw_tree(tree, {"a": a, "b": b}, ss.show_tags))
        if m in (a, b):
            other = b if m == a else a
            st.success(f"**{m}** 은(는) **{other}** 의 조상 계통이에요. {other}은(는) {m}에서 갈라져 나온 무리 가운데 하나예요.")
        else:
            st.success(f"**{a}** 와(과) **{b}** 의 가장 가까운 공통 조상은 **★ {m}** 이에요.")
        pa = tree.path(a)[tree.path(a).index(m) + 1:] if m != a else []
        pb = tree.path(b)[tree.path(b).index(m) + 1:] if m != b else []
        shared = tree.path(m)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 🟢 둘이 함께 가진 특징")
            for n in shared:
                for s in tree.node[n]["new"][:2]:
                    st.markdown(f"- {s}")
            st.caption(f"{tree.path(m)[0]}에서 {m}까지 물려받은 특징 중 일부예요.")
        with c2:
            st.markdown(f"#### 🔵 {a}만의 특징")
            for n in pa:
                st.markdown(f"**{n}**")
                for s in tree.node[n]["new"][:3]:
                    st.markdown(f"- {s}")
            if not pa:
                st.caption("공통 조상 그대로예요.")
        with c3:
            st.markdown(f"#### 🟠 {b}만의 특징")
            for n in pb:
                st.markdown(f"**{n}**")
                for s in tree.node[n]["new"][:3]:
                    st.markdown(f"- {s}")
            if not pb:
                st.caption("공통 조상 그대로예요.")

# ── 3. 한눈에 비교 ───────────────────────────
with tab3:
    rows = ["| 계통 | 대표 생물 | 핵심 특징 |", "|---|---|---|"]
    for n in tree.leaves:
        nd = tree.node[n]
        rows.append(f"| {nd['icon']} **{n}** | {nd['eg']} | {nd['new'][0]} {nd['new'][1] if len(nd['new']) > 1 else ''} |")
    st.markdown("\n".join(rows))
    st.markdown("#### 🌳 계통수에서 알아 둘 점")
    st.markdown(
        "- 가로선이 갈라지는 **마디**는 공통 조상이에요. 마디에서 가까이 갈라진 두 계통일수록 서로 더 가까운 친척이에요.\n"
        "- 가지 끝이 가지런히 정렬되어 있어도, 오른쪽에 있다고 해서 더 '진화한' 생물은 아니에요.\n"
        "- 같은 가지 아래 있는 무리는 그 가지에서 생긴 **파생 형질을 모두 물려받아요**."
    )
