"""
ADH(항이뇨호르몬) 항상성 시뮬레이션
- 혈장 삼투압 상승 / 혈액량 감소 -> ADH 분비 증가 -> 콩팥의 수분 재흡수 증가
  -> 오줌 삼투압 상승(오줌 농축), 수분 배출 감소 -> 혈액량 증가, 혈장 삼투압 하락(희석)
- 수분 섭취량은 매 단계 계속 유입되는 입력값으로 작용하여, 섭취량 수준에 따라
  시스템이 새로운 균형점을 찾아가는 과정을 보여줍니다.
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------
st.set_page_config(
    page_title="ADH 항상성 시뮬레이션",
    page_icon="💧",
    layout="wide",
)

ADH_COLOR = "#4FA8E8"      # 파란 계열 - 뇌하수체 후엽 호르몬
OSM_COLOR = "#E8664F"      # 코랄 - 혈장 삼투압
URINE_COLOR = "#E8C23D"    # 노랑 - 오줌 삼투압
VOL_COLOR = "#4FD1C5"      # 청록 - 혈액량
NORM_COLOR = "#8C9EFF"     # 정상 범위 참조선

st.markdown(
    """
    <style>
    .stApp { background-color: #0D1A1C; }
    section[data-testid="stSidebar"] { background-color: #142629; }
    .summary-box {
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
    "color:#4FA8E8; text-transform:uppercase;'>ADH · RENAL WATER FEEDBACK MODEL</div>",
    unsafe_allow_html=True,
)
st.title("ADH 항상성 시뮬레이션")
st.caption(
    "혈장 삼투압이 오르거나 혈액량이 줄어들면 ADH 분비가 늘어나 콩팥의 수분 재흡수를 촉진합니다. "
    "그 결과 오줌은 진해지고(오줌 삼투압 상승), 몸은 물을 덜 내보내 혈액량이 늘고 혈장은 다시 묽어집니다."
)

st.markdown("#### 되먹임 흐름")
st.markdown(
    "**혈장 삼투압 ↑ / 혈액량 ↓ → ADH 분비 ↑ → 콩팥 수분 재흡수 ↑ → 오줌 삼투압 ↑ (수분 배출 ↓) "
    "→ 혈액량 ↑ · 혈장 삼투압 ↓ (음성 되먹임)**  \n"
    "수분 섭취량은 매 단계 계속 들어오는 입력으로 작용해, 섭취량 수준에 따라 시스템이 새로운 균형점을 찾아갑니다."
)

st.divider()

# ---------------------------------------------------------------
# 내부 생리학적 상수 (정상 범위 및 반응 강도 - 고정값)
# ---------------------------------------------------------------
NORM = 100.0            # 혈장 삼투압 · 혈액량의 정상 기준치 (임의 단위)
ADH_OSM_GAIN = 0.30      # 혈장 삼투압 편차 -> ADH 반응 강도
ADH_VOL_GAIN = 0.15      # 혈액량 편차 -> ADH 반응 강도
URINE_GAIN = 0.35        # ADH -> 오줌 삼투압이 따라가는 속도
EXCRETION_BASE = 60.0    # ADH가 0일 때 기본 수분 배출량
EXCRETION_GAIN = 0.60    # ADH가 수분 배출을 억제하는 정도
INTAKE_GAIN = 0.60       # 수분 섭취량 중 실제로 체내에 반영되는 비율
OSM_GAIN = 0.05          # 순수분(net water)이 혈장 삼투압에 미치는 영향
VOL_GAIN = 0.30          # 순수분(net water)이 혈액량에 미치는 영향
STEPS = 60


def simulate(water_intake, init_adh, init_osm, init_urine, init_vol, steps=STEPS):
    adh, osm, urine, vol = init_adh, init_osm, init_urine, init_vol
    hist_adh, hist_osm, hist_urine, hist_vol = [adh], [osm], [urine], [vol]

    for _ in range(steps):
        excretion = max(0.0, EXCRETION_BASE - EXCRETION_GAIN * adh)
        net_water = INTAKE_GAIN * water_intake - excretion

        n_osm = max(0.0, osm - OSM_GAIN * net_water)
        n_vol = max(0.0, vol + VOL_GAIN * net_water)
        n_adh = max(0.0, adh + ADH_OSM_GAIN * (osm - NORM) + ADH_VOL_GAIN * (NORM - vol))
        n_urine = max(0.0, urine + URINE_GAIN * (adh - urine))

        adh, osm, vol, urine = n_adh, n_osm, n_vol, n_urine
        hist_adh.append(adh)
        hist_osm.append(osm)
        hist_urine.append(urine)
        hist_vol.append(vol)

    return hist_adh, hist_osm, hist_urine, hist_vol


# ---------------------------------------------------------------
# 레이아웃: 옵션 | 안내
# ---------------------------------------------------------------
col_opt, col_info = st.columns([1.1, 1], gap="large")

with col_opt:
    st.subheader("옵션")
    st.caption("수분 섭취량과 각 요소의 초기값을 조정하세요.")

    water_intake = st.slider("수분 섭취량", 0, 150, 80, 1)

    st.markdown("&nbsp;", unsafe_allow_html=True)
    init_adh = st.slider("초기 ADH 분비량", 0, 150, 50, 1)
    init_osm = st.slider("초기 혈장 삼투압", 50, 150, 100, 1)
    init_urine = st.slider("초기 오줌 삼투압", 0, 150, 50, 1)
    init_vol = st.slider("초기 혈액량", 50, 150, 100, 1)

    run = st.button("시뮬레이션 시작", type="primary", use_container_width=True)

if run:
    hist_adh, hist_osm, hist_urine, hist_vol = simulate(
        water_intake, init_adh, init_osm, init_urine, init_vol
    )
    st.session_state["adh_result"] = {
        "hist_adh": hist_adh,
        "hist_osm": hist_osm,
        "hist_urine": hist_urine,
        "hist_vol": hist_vol,
    }

with col_info:
    st.subheader("참고")
    st.markdown(
        f"""
        <div class="summary-box">
        정상 기준치(혈장 삼투압 · 혈액량) &nbsp;≈&nbsp; {NORM:.0f}<br>
        수분 섭취량이 콩팥의 수분 배출 능력보다 많으면, ADH가 억제되어 과도한 저류를 막지만<br>
        혈장 삼투압과 혈액량은 정상치에서 다소 벗어난 새로운 균형점에 머무를 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if "adh_result" in st.session_state:
        r = st.session_state["adh_result"]
        st.markdown(
            f"""
            <div class="summary-box">
            최종 ADH &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span style="color:{ADH_COLOR}">{r['hist_adh'][-1]:.1f}</span><br>
            최종 혈장 삼투압&nbsp;: <span style="color:{OSM_COLOR}">{r['hist_osm'][-1]:.1f}</span><br>
            최종 오줌 삼투압&nbsp;: <span style="color:{URINE_COLOR}">{r['hist_urine'][-1]:.1f}</span><br>
            최종 혈액량&nbsp;&nbsp;&nbsp;&nbsp;: <span style="color:{VOL_COLOR}">{r['hist_vol'][-1]:.1f}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ---------------------------------------------------------------
# 그래프
# ---------------------------------------------------------------
st.subheader("ADH · 혈장삼투압 · 오줌삼투압 · 혈액량 변화 그래프")
st.caption("시간 단계에 따른 네 요소의 변화 추이입니다.")

if "adh_result" not in st.session_state:
    st.markdown(
        "<div style='color:#8FA6A3; text-align:center; padding:40px 10px;'>"
        "시뮬레이션을 시작하면 이곳에 그래프가 표시됩니다.</div>",
        unsafe_allow_html=True,
    )
else:
    r = st.session_state["adh_result"]
    steps = list(range(len(r["hist_adh"])))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_adh"], mode="lines", name="ADH",
        line=dict(color=ADH_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_osm"], mode="lines", name="혈장 삼투압",
        line=dict(color=OSM_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_urine"], mode="lines", name="오줌 삼투압",
        line=dict(color=URINE_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_vol"], mode="lines", name="혈액량",
        line=dict(color=VOL_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=[NORM] * len(steps), mode="lines", name="정상 범위",
        line=dict(color=NORM_COLOR, width=1.5, dash="dash"),
    ))

    fig.update_layout(
        plot_bgcolor="#142629",
        paper_bgcolor="#142629",
        font=dict(color="#EDE7DA"),
        xaxis=dict(title="시간 단계", gridcolor="#2A4448"),
        yaxis=dict(title="수치", gridcolor="#2A4448"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        height=440,
    )

    st.plotly_chart(fig, use_container_width=True)
