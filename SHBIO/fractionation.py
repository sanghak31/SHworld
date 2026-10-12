import streamlit as st

st.set_page_config(page_title="세포 분획법 실험실", page_icon="🧫", layout="wide")

# ==========================
# 세포소기관 정보
#   이름: (이모지, 침전 기준값 = 원심력(g) × 시간(분))
#   기준값 이상으로 원심분리하면 침전물로 가라앉고, 미만이면 상층액에 남습니다.
# ==========================
ORGANELLES = {
    "세포찌꺼기":   ("🧩", 10_000),
    "세포벽":       ("🧱", 10_000),
    "핵":           ("🔵", 10_000),
    "엽록체":       ("🌿", 30_000),
    "마이토콘드리아": ("🔋", 200_000),
    "라이소솜":     ("🧪", 200_000),
    "소포체":       ("🌀", 6_000_000),
    "골지체":       ("📚", 6_000_000),
    "액포":         ("💧", 6_000_000),
    "라이보솜":     ("⚪", 27_000_000),
}

# 균질화된 세포액에 들어 있는 것들
ANIMAL_CONTENTS = ["세포찌꺼기", "핵", "마이토콘드리아", "라이소솜", "소포체", "골지체", "라이보솜"]
PLANT_CONTENTS = ["세포찌꺼기", "세포벽", "핵", "엽록체", "마이토콘드리아", "소포체", "골지체", "액포", "라이보솜"]

# 원심분리 설정 버튼 (원심력 g, 시간 분)
PRESETS = [(1_000, 10), (3_000, 10), (10_000, 20), (100_000, 60), (150_000, 180)]

SLOT_COUNT = 10

# ==========================
# 스타일
# ==========================
st.markdown(
    """
<style>
.chip{display:inline-block;margin:3px 6px 3px 0;padding:6px 12px;border-radius:999px;
  background:rgba(128,128,128,.15);border:1px solid rgba(128,128,128,.3);font-size:1.02rem;}
.tube{width:80px;height:230px;margin:0 auto;border:3px solid rgba(128,128,128,.6);
  border-top:none;border-radius:0 0 40px 40px;overflow:hidden;display:flex;flex-direction:column;}
.tube.sm{width:60px;height:160px;border-radius:0 0 30px 30px;}
.tube .sup{flex:3;background:rgba(90,160,230,.35);display:flex;align-items:center;justify-content:center;font-size:.8rem;}
.tube .pel{flex:1;background:rgba(150,85,45,.75);display:flex;align-items:center;justify-content:center;font-size:.8rem;color:#fff;}
.tube .empty,.tube .gap{flex:1;}
.tube .whole{flex:1;background-color:rgba(120,170,110,.30);
  background-image:radial-gradient(circle,rgba(60,110,50,.6) 2px,transparent 2.5px),radial-gradient(circle,rgba(150,85,45,.55) 3px,transparent 3.5px);
  background-size:14px 14px,22px 22px;background-position:0 0,7px 9px;}
.tube-label{text-align:center;font-size:.85rem;opacity:.75;margin-top:6px;}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================
# 상태 초기화
# ==========================
ss = st.session_state
ss.setdefault("target", None)   # 대상 용액: {"name": str, "organelles": [..]}
ss.setdefault("mode", None)     # None / centrifuge / save / analyze / load
ss.setdefault("split", None)    # 원심분리 결과 (상층액, 침전물)
ss.setdefault("slots", [None] * SLOT_COUNT)


# 용액의 종류: whole(원심분리 전) / sup(상층액) / pel(침전물)
KIND_ICON = {"whole": "🟢", "sup": "🔵", "pel": "🟤"}


def copy_solution(sol):
    return {
        "name": sol["name"],
        "organelles": list(sol["organelles"]),
        "kind": sol.get("kind", "whole"),
    }


def single_tube_html(sol, small=False):
    """용액 종류에 따라 다른 시험관 그림을 만든다."""
    kind = sol.get("kind", "whole")
    if kind == "whole":
        inner = '<div class="whole"></div>'
        text = "아직 원심분리하지 않은 용액"
    elif kind == "sup":
        inner = '<div class="sup" style="flex:1"></div>'
        text = "상층액만 있는 용액"
    else:
        if sol["organelles"]:
            inner = '<div class="gap"></div><div class="pel" style="flex:0 0 26%"></div>'
        else:
            inner = '<div class="empty"></div>'
        text = "침전물만 있는 용액"
    cls = "tube sm" if small else "tube"
    return f'<div class="{cls}">{inner}</div><div class="tube-label">{text}</div>'


def chips(names):
    return "".join(f'<span class="chip">{ORGANELLES[n][0]} {n}</span>' for n in names)


def centrifuge(g, minutes):
    """대상 용액을 원심분리해서 상층액/침전물로 나눈다."""
    power = g * minutes
    org = ss.target["organelles"]
    pellet = [o for o in org if ORGANELLES[o][1] <= power]
    supernatant = [o for o in org if ORGANELLES[o][1] > power]
    base = ss.target["name"]
    label = f"{g:,}g·{minutes}분"
    ss.split = {
        "label": label,
        "sup": {"name": f"{base} → {label} 상층액", "organelles": supernatant, "kind": "sup"},
        "pel": {"name": f"{base} → {label} 침전물", "organelles": pellet, "kind": "pel"},
    }


def set_mode(mode):
    ss.mode = None if ss.mode == mode else mode


# ==========================
# 제목 + 상단 버튼
# ==========================
st.title("🧫 세포 분획법 실험실")
st.write("균질화한 세포액을 원심분리해서 세포소기관을 분리해 보세요. 분리한 용액은 분석하고 저장할 수 있어요.")

c1, c2, c3, c4, c5, c6 = st.columns(6)


def mode_type(m):
    return "primary" if ss.mode == m else "secondary"


if c1.button("🐾 균질화된 동물세포액", use_container_width=True):
    ss.target = {"name": "균질화된 동물세포액", "organelles": list(ANIMAL_CONTENTS), "kind": "whole"}
    ss.split = None
    ss.mode = None
    st.rerun()

if c2.button("🌱 균질화된 식물세포액", use_container_width=True):
    ss.target = {"name": "균질화된 식물세포액", "organelles": list(PLANT_CONTENTS), "kind": "whole"}
    ss.split = None
    ss.mode = None
    st.rerun()

if c3.button("🌀 원심분리", use_container_width=True, type=mode_type("centrifuge")):
    set_mode("centrifuge")
    st.rerun()

if c4.button("💾 저장", use_container_width=True, type=mode_type("save")):
    set_mode("save")
    st.rerun()

if c5.button("📂 불러오기", use_container_width=True, type=mode_type("load")):
    set_mode("load")
    st.rerun()

if c6.button("🔬 분석", use_container_width=True, type=mode_type("analyze")):
    set_mode("analyze")
    st.rerun()

# ==========================
# 현재 대상 용액
# ==========================
st.divider()
st.subheader("🧪 현재 대상 용액")

if ss.target is None:
    st.info("먼저 '균질화된 동물세포액' 또는 '균질화된 식물세포액'을 눌러 대상 용액을 정하세요.")
else:
    tcol, ncol = st.columns([1, 5], vertical_alignment="center")
    tcol.markdown(single_tube_html(ss.target, small=True), unsafe_allow_html=True)
    ncol.markdown(f"### {ss.target['name']}")

# ==========================
# 모드별 패널
# ==========================
if ss.mode == "centrifuge":
    st.markdown("#### 🌀 원심분리 설정 (원심력 · 시간)")
    st.caption("크고 무거운 것일수록 낮은 속도에서도 가라앉아요. 낮은 속도부터 차례로 분리해 보세요.")
    if ss.target is None:
        st.warning("대상 용액이 없어요. 먼저 균질화된 세포액을 선택하세요.")
    else:
        cols = st.columns(len(PRESETS))
        for col, (g, minutes) in zip(cols, PRESETS):
            if col.button(f"{g:,}g · {minutes}분", key=f"spin_{g}_{minutes}", use_container_width=True):
                centrifuge(g, minutes)

elif ss.mode == "save":
    st.markdown("#### 💾 저장")
    if ss.target is None:
        st.warning("저장할 대상 용액이 없어요.")
    elif all(s is not None for s in ss.slots):
        st.warning("비어 있는 슬롯이 없어요. 아래에서 슬롯을 비운 뒤 저장하세요.")
    else:
        st.info("아래 저장 슬롯 중 비어 있는 곳의 '여기에 저장'을 누르세요.")

elif ss.mode == "load":
    st.markdown("#### 📂 불러오기")
    if all(s is None for s in ss.slots):
        st.warning("저장된 용액이 없어요.")
    else:
        st.info("아래 저장 슬롯에서 불러올 용액의 '불러오기'를 누르면 대상 용액이 바뀝니다.")

elif ss.mode == "analyze":
    st.markdown("#### 🔬 분석 결과")
    if ss.target is None:
        st.warning("분석할 대상 용액이 없어요.")
    elif not ss.target["organelles"]:
        st.info("이 용액에는 세포소기관이 들어 있지 않아요.")
    else:
        order = list(ORGANELLES.keys())
        found = [o for o in order if o in ss.target["organelles"]]
        st.markdown(chips(found), unsafe_allow_html=True)
        st.caption(f"세포소기관 {len(found)}종류")

# ==========================
# 원심분리 결과: 대상 용액을 무엇으로 바꿀지 선택
# ==========================
if ss.split is not None:
    st.divider()
    st.subheader(f"🌀 원심분리 결과 ({ss.split['label']})")

    sup_exists = bool(ss.split["sup"]["organelles"])
    pel_exists = bool(ss.split["pel"]["organelles"])

    if sup_exists or pel_exists:
        sup_html = '<div class="sup">상층액</div>' if sup_exists else '<div class="empty"></div>'
        pel_html = '<div class="pel">침전물</div>' if pel_exists else ""
        tube_html = f'<div class="tube">{sup_html}{pel_html}</div>'
    else:
        tube_html = '<div class="tube"><div class="empty"></div></div>'

    left, right = st.columns([1, 3], vertical_alignment="center")
    with left:
        st.markdown(tube_html, unsafe_allow_html=True)
    with right:
        st.write("대상 용액을 무엇으로 바꿀까요?")
        b1, b2, b3 = st.columns(3)
        if b1.button("⬆️ 상층액으로 변경", use_container_width=True):
            ss.target = copy_solution(ss.split["sup"])
            ss.split = None
            st.rerun()
        if b2.button("⬇️ 침전물로 변경", use_container_width=True):
            ss.target = copy_solution(ss.split["pel"])
            ss.split = None
            st.rerun()
        if b3.button("↩️ 변경하지 않음", use_container_width=True):
            ss.split = None
            st.rerun()

# ==========================
# 저장 슬롯
# ==========================
st.divider()
st.subheader("💾 저장 슬롯")

for row in range(2):
    cols = st.columns(5)
    for col, i in zip(cols, range(row * 5, row * 5 + 5)):
        with col.container(border=True):
            st.markdown(f"**슬롯 {i + 1}**")
            slot = ss.slots[i]
            if slot is None:
                st.caption("비어 있음")
                if ss.mode == "save" and ss.target is not None:
                    if st.button("여기에 저장", key=f"save_{i}", use_container_width=True):
                        ss.slots[i] = copy_solution(ss.target)
                        ss.mode = None
                        st.rerun()
            else:
                st.caption(f'{KIND_ICON[slot.get("kind", "whole")]} {slot["name"]}')
                if ss.mode == "load":
                    if st.button("불러오기", key=f"load_{i}", use_container_width=True):
                        ss.target = copy_solution(slot)
                        ss.split = None
                        ss.mode = None
                        st.rerun()
                if st.button("비우기", key=f"clear_{i}", use_container_width=True):
                    ss.slots[i] = None
                    st.rerun()
