"""
면역 반응 시뮬레이션
- 하루 단위로 진행하는 인터랙티브 시뮬레이션입니다.
- "시뮬레이션 시작"을 누르면 1일차부터 시작하고, "다음 일차"를 눌러야 하루씩 진행됩니다.
- 바이러스 A/B/C 주입 버튼은 on/off 토글이며, on 상태에서 "다음 일차"를 누르면
  그 날 해당 바이러스가 체내로 침입한 뒤 자동으로 off로 돌아갑니다.
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------
st.set_page_config(
    page_title="면역 반응 시뮬레이션",
    page_icon="🦠",
    layout="wide",
)

T_COLOR = "#4FD1C5"       # 보조 T림프구 - 청록
VA_COLOR = "#E8664F"      # 바이러스 A - 빨강
VB_COLOR = "#E8A33D"      # 바이러스 B - 주황
VC_COLOR = "#B084E8"      # 바이러스 C - 보라

st.markdown(
    """
    <style>
    .stApp { background-color: #0D1A1C; color: #EDE7DA; }
    section[data-testid="stSidebar"] { background-color: #142629; }
    .status-box {
        background: #1B3236;
        border: 1px solid #2A4448;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 6px;
        font-family: 'Courier New', monospace;
        font-size: 13.5px;
        line-height: 1.9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div style='font-family:monospace; font-size:12px; letter-spacing:0.14em; "
    "color:#4FD1C5; text-transform:uppercase;'>ADAPTIVE IMMUNITY · DAY-BY-DAY MODEL</div>",
    unsafe_allow_html=True,
)
st.title("면역 반응 시뮬레이션")
st.caption(
    "바이러스가 침입하면 보조 T림프구의 도움으로 각 바이러스에 대한 항체가 만들어지고, "
    "항체 농도가 오르면 해당 바이러스가 억제됩니다. 후천성 면역 결핍증(AIDS) 상태에서는 "
    "보조 T림프구가 점점 파괴되어 이 반응이 제대로 작동하지 않습니다."
)

st.divider()

# ---------------------------------------------------------------
# 내부 모델 상수 (고정값)
# ---------------------------------------------------------------
INOCULATION_DOSE = 60.0
CARRYING_CAPACITY = 1000.0
VIRUS_GROWTH_RATE = 0.35
CLEARANCE_COEF = 0.0035
AB_PROD_COEF = 0.025
AB_DECAY = 0.06
T_REGEN_RATE = 0.05
T_CONSUMPTION_COEF = 0.01
AIDS_DECLINE_RATE = 0.04
AIDS_EXTRA_DECLINE_COEF = 0.00003


def next_day_state(state, inject_a, inject_b, inject_c, immunity_factor, aids_on, t_baseline):
    T = state["T"]
    Va, Vb, Vc = state["Va"], state["Vb"], state["Vc"]
    Aa, Ab, Ac = state["Aa"], state["Ab"], state["Ac"]

    # 1. 바이러스 주입 (해당 토글이 켜져 있으면 이 날 침입)
    if inject_a:
        Va += INOCULATION_DOSE
    if inject_b:
        Vb += INOCULATION_DOSE
    if inject_c:
        Vc += INOCULATION_DOSE

    t_ref = max(1.0, t_baseline)

    def grow_virus(V, A):
        growth = VIRUS_GROWTH_RATE * V * (1 - V / CARRYING_CAPACITY)
        clearance = CLEARANCE_COEF * A * V * immunity_factor
        return min(CARRYING_CAPACITY * 1.05, max(0.0, V + growth - clearance))

    def grow_antibody(A, V):
        production = AB_PROD_COEF * V * (T / t_ref) * immunity_factor
        return max(0.0, A + production - AB_DECAY * A)

    n_Aa = grow_antibody(Aa, Va)
    n_Ab = grow_antibody(Ab, Vb)
    n_Ac = grow_antibody(Ac, Vc)

    n_Va = grow_virus(Va, Aa)
    n_Vb = grow_virus(Vb, Ab)
    n_Vc = grow_virus(Vc, Ac)

    total_virus = Va + Vb + Vc
    if aids_on:
        n_T = max(0.0, T - AIDS_DECLINE_RATE * T - AIDS_EXTRA_DECLINE_COEF * total_virus * T)
    else:
        n_T = max(0.0, T + T_REGEN_RATE * (t_baseline - T) - T_CONSUMPTION_COEF * total_virus)

    return {"T": n_T, "Va": n_Va, "Vb": n_Vb, "Vc": n_Vc, "Aa": n_Aa, "Ab": n_Ab, "Ac": n_Ac}


# ---------------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
if "day" not in st.session_state:
    st.session_state.day = 0
if "history" not in st.session_state:
    st.session_state.history = None
if "state" not in st.session_state:
    st.session_state.state = None

# 토글 초기값(강제 리셋) 처리 - 위젯이 인스턴스화되기 전에 수행해야 함
if st.session_state.get("reset_toggles", False):
    st.session_state["inject_a"] = False
    st.session_state["inject_b"] = False
    st.session_state["inject_c"] = False
    st.session_state["reset_toggles"] = False

# ---------------------------------------------------------------
# 옵션
# ---------------------------------------------------------------
st.subheader("옵션")
st.caption("시뮬레이션 시작 시점의 값으로 적용됩니다.")

opt1, opt2, opt3 = st.columns(3)
with opt1:
    immunity = st.slider("면역력", 0, 200, 100, 1, disabled=st.session_state.started)
with opt2:
    init_t = st.slider("초기 보조 T림프구 수", 1, 1000, 500, 1, disabled=st.session_state.started)
with opt3:
    aids_on = st.checkbox("후천성 면역 결핍증(AIDS)", value=False, disabled=st.session_state.started)

st.divider()

# ---------------------------------------------------------------
# 시뮬레이션 - 버튼 5개를 한 줄에 배치
# ---------------------------------------------------------------
st.subheader("시뮬레이션")

b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
with b1:
    start_clicked = st.button("시뮬레이션 시작", type="primary", use_container_width=True)
with b2:
    next_clicked = st.button(
        "다음 일차", use_container_width=True, disabled=not st.session_state.started
    )
with b3:
    skip10_clicked = st.button(
        "10일 넘기기", use_container_width=True, disabled=not st.session_state.started
    )
with b4:
    skip30_clicked = st.button(
        "30일 넘기기", use_container_width=True, disabled=not st.session_state.started
    )
with b5:
    inject_a = st.toggle(
        "바이러스 A 주입", key="inject_a", disabled=not st.session_state.started
    )
with b6:
    inject_b = st.toggle(
        "바이러스 B 주입", key="inject_b", disabled=not st.session_state.started
    )
with b7:
    inject_c = st.toggle(
        "바이러스 C 주입", key="inject_c", disabled=not st.session_state.started
    )

# ---- 시뮬레이션 시작 처리 ----
if start_clicked:
    init_state = {"T": float(init_t), "Va": 0.0, "Vb": 0.0, "Vc": 0.0, "Aa": 0.0, "Ab": 0.0, "Ac": 0.0}
    st.session_state.started = True
    st.session_state.day = 1
    st.session_state.state = init_state
    st.session_state.immunity_factor = immunity / 100.0
    st.session_state.aids_on = aids_on
    st.session_state.t_baseline = float(init_t)
    st.session_state.history = {
        "day": [1],
        "T": [init_state["T"]],
        "Va": [0.0], "Vb": [0.0], "Vc": [0.0],
        "Aa": [0.0], "Ab": [0.0], "Ac": [0.0],
    }
    st.session_state.reset_toggles = True
    st.rerun()


def advance_days(n_days, inj_a, inj_b, inj_c):
    """n_days만큼 하루씩 진행하며 매일의 기록을 history에 쌓는다.
    바이러스 주입은 이 구간의 첫째 날에만 적용되고, 이후 날짜에는 적용되지 않는다."""
    state = st.session_state.state
    h = st.session_state.history
    for i in range(n_days):
        ia = inj_a if i == 0 else False
        ib = inj_b if i == 0 else False
        ic = inj_c if i == 0 else False
        state = next_day_state(
            state, ia, ib, ic,
            st.session_state.immunity_factor,
            st.session_state.aids_on,
            st.session_state.t_baseline,
        )
        st.session_state.day += 1
        h["day"].append(st.session_state.day)
        h["T"].append(state["T"])
        h["Va"].append(state["Va"])
        h["Vb"].append(state["Vb"])
        h["Vc"].append(state["Vc"])
        h["Aa"].append(state["Aa"])
        h["Ab"].append(state["Ab"])
        h["Ac"].append(state["Ac"])
    st.session_state.state = state


# ---- 다음 일차 / 10일 넘기기 / 30일 넘기기 처리 ----
if st.session_state.started:
    if next_clicked:
        advance_days(1, inject_a, inject_b, inject_c)
        st.session_state.reset_toggles = True
        st.rerun()
    elif skip10_clicked:
        advance_days(10, inject_a, inject_b, inject_c)
        st.session_state.reset_toggles = True
        st.rerun()
    elif skip30_clicked:
        advance_days(30, inject_a, inject_b, inject_c)
        st.session_state.reset_toggles = True
        st.rerun()

# ---- 현재 상태 요약 ----
if st.session_state.started:
    s = st.session_state.state
    st.markdown(
        f"""
        <div class="status-box">
        현재 <b>{st.session_state.day}일차</b> · 후천성 면역 결핍증: {"ON" if st.session_state.aids_on else "OFF"}<br>
        보조 T림프구 수&nbsp;: <span style="color:{T_COLOR}">{s['T']:.1f}</span><br>
        바이러스 A&nbsp;/&nbsp;항체 A&nbsp;: <span style="color:{VA_COLOR}">{s['Va']:.1f}</span> / {s['Aa']:.1f}<br>
        바이러스 B&nbsp;/&nbsp;항체 B&nbsp;: <span style="color:{VB_COLOR}">{s['Vb']:.1f}</span> / {s['Ab']:.1f}<br>
        바이러스 C&nbsp;/&nbsp;항체 C&nbsp;: <span style="color:{VC_COLOR}">{s['Vc']:.1f}</span> / {s['Ac']:.1f}
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("옵션을 설정한 뒤 '시뮬레이션 시작'을 누르면 1일차부터 진행할 수 있습니다.")

st.divider()

# ---------------------------------------------------------------
# 그래프
# ---------------------------------------------------------------
st.subheader("일차에 따른 변화 그래프")
st.caption("보조 T림프구 수, 바이러스 A·B·C의 수, 바이러스 A·B·C에 대한 항체 농도")

if not st.session_state.started or st.session_state.history is None:
    st.markdown(
        "<div style='color:#8FA6A3; text-align:center; padding:40px 10px;'>"
        "시뮬레이션을 시작하면 이곳에 그래프가 표시됩니다.</div>",
        unsafe_allow_html=True,
    )
else:
    h = st.session_state.history
    days = h["day"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=h["T"], mode="lines+markers", name="보조 T림프구 수",
                              line=dict(color=T_COLOR, width=2.5)))

    fig.add_trace(go.Scatter(x=days, y=h["Va"], mode="lines+markers", name="바이러스 A 수",
                              line=dict(color=VA_COLOR, width=2.5)))
    fig.add_trace(go.Scatter(x=days, y=h["Vb"], mode="lines+markers", name="바이러스 B 수",
                              line=dict(color=VB_COLOR, width=2.5)))
    fig.add_trace(go.Scatter(x=days, y=h["Vc"], mode="lines+markers", name="바이러스 C 수",
                              line=dict(color=VC_COLOR, width=2.5)))

    fig.add_trace(go.Scatter(x=days, y=h["Aa"], mode="lines", name="바이러스 A 항체 농도",
                              line=dict(color=VA_COLOR, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=days, y=h["Ab"], mode="lines", name="바이러스 B 항체 농도",
                              line=dict(color=VB_COLOR, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=days, y=h["Ac"], mode="lines", name="바이러스 C 항체 농도",
                              line=dict(color=VC_COLOR, width=2, dash="dash")))

    fig.update_layout(
        plot_bgcolor="#142629",
        paper_bgcolor="#142629",
        font=dict(color="#EDE7DA"),
        xaxis=dict(title="일차", gridcolor="#2A4448", dtick=1),
        yaxis=dict(title="수치", gridcolor="#2A4448"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        height=480,
    )

    st.plotly_chart(fig, use_container_width=True)
