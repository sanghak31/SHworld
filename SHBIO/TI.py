"""
티록신 항상성 시뮬레이션 (HPT axis negative feedback model)
Streamlit 앱 - GitHub에 올려서 Streamlit Community Cloud로 배포할 수 있습니다.
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------
st.set_page_config(
    page_title="티록신 항상성 시뮬레이션",
    page_icon="🧬",
    layout="wide",
)

TRH_COLOR = "#E8A33D"
TSH_COLOR = "#E8664F"
T4_COLOR = "#4FD1C5"
TARGET_COLOR = "#8C9EFF"

# 다크 클리닉 모니터 톤에 가깝게 살짝 커스텀
st.markdown(
    """
    <style>
    .stApp { background-color: #0D1A1C; }
    section[data-testid="stSidebar"] { background-color: #142629; }
    .metric-card {
        background: #1B3236;
        border: 1px solid #2A4448;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 13px; color: #8FA6A3; }
    .metric-value { font-family: 'Courier New', monospace; font-size: 26px; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div style='font-family:monospace; font-size:12px; letter-spacing:0.14em; "
    "color:#4FD1C5; text-transform:uppercase;'>HPT AXIS · NEGATIVE FEEDBACK MODEL</div>",
    unsafe_allow_html=True,
)
st.title("티록신 항상성 시뮬레이션")
st.caption(
    "시상하부(TRH) → 뇌하수체(TSH) → 갑상선(티록신)으로 이어지는 되먹임 고리를 통해, "
    "시스템이 어떻게 목표 티록신 농도로 수렴하는지 살펴봅니다."
)

st.markdown("#### 되먹임 흐름")
st.markdown(
    "**TRH 분비 ↑ → TSH 분비 ↑ → 티록신 분비 ↑ → (목표치 도달 시) 티록신이 TRH 분비를 "
    "억제하는 음성 되먹임(negative feedback)이 작동하여 균형을 되찾습니다.**"
)

st.divider()


# ---------------------------------------------------------------
# 시뮬레이션 함수
# ---------------------------------------------------------------
def simulate(target_t4, init_trh, init_tsh, init_t4, trh_gain, tsh_gain, t4_gain, steps=60):
    trh, tsh, t4 = init_trh, init_tsh, init_t4
    hist_trh, hist_tsh, hist_t4 = [trh], [tsh], [t4]

    for _ in range(steps):
        error = target_t4 - t4  # 티록신이 목표보다 낮으면 양수 -> TRH 자극
        n_trh = max(0.0, trh + trh_gain * error)
        n_tsh = max(0.0, tsh + tsh_gain * (trh - tsh))
        n_t4 = max(0.0, t4 + t4_gain * (tsh - t4))

        trh, tsh, t4 = n_trh, n_tsh, n_t4
        hist_trh.append(trh)
        hist_tsh.append(tsh)
        hist_t4.append(t4)

    return hist_trh, hist_tsh, hist_t4


# ---------------------------------------------------------------
# 레이아웃: 옵션 | 결과
# ---------------------------------------------------------------
col_opt, col_result = st.columns([1.1, 1], gap="large")

with col_opt:
    st.subheader("옵션")
    st.caption("초기값과 각 단계의 반응 강도(영향력)를 조정하세요.")

    target_t4 = st.slider("목표 티록신 분비량", 20, 200, 100, 1)

    st.markdown("&nbsp;", unsafe_allow_html=True)
    init_trh = st.slider("초기 TRH 분비량", 0, 150, 40, 1)
    init_tsh = st.slider("초기 TSH 분비량", 0, 150, 40, 1)
    init_t4 = st.slider("초기 티록신 분비량", 0, 150, 30, 1)

    st.markdown("&nbsp;", unsafe_allow_html=True)
    trh_gain = st.slider("TRH 영향력", 0.05, 1.0, 0.35, 0.01)
    tsh_gain = st.slider("TSH 영향력", 0.05, 1.0, 0.35, 0.01)
    t4_gain = st.slider("티록신 영향력", 0.05, 1.0, 0.35, 0.01)

    run = st.button("시뮬레이션 시작", type="primary", use_container_width=True)

if run:
    hist_trh, hist_tsh, hist_t4 = simulate(
        target_t4, init_trh, init_tsh, init_t4, trh_gain, tsh_gain, t4_gain
    )
    st.session_state["result"] = {
        "hist_trh": hist_trh,
        "hist_tsh": hist_tsh,
        "hist_t4": hist_t4,
        "target_t4": target_t4,
    }

with col_result:
    st.subheader("시뮬레이션")
    st.caption("60단계 동안의 되먹임 반응 결과입니다.")

    if "result" not in st.session_state:
        st.info("옵션을 조정한 뒤 '시뮬레이션 시작'을 눌러주세요.")
    else:
        r = st.session_state["result"]
        final_trh = r["hist_trh"][-1]
        final_tsh = r["hist_tsh"][-1]
        final_t4 = r["hist_t4"][-1]

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">최종 TRH 분비량</div>
                <div class="metric-value" style="color:{TRH_COLOR}">{final_trh:.1f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">최종 TSH 분비량</div>
                <div class="metric-value" style="color:{TSH_COLOR}">{final_tsh:.1f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">최종 티록신 분비량</div>
                <div class="metric-value" style="color:{T4_COLOR}">{final_t4:.1f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        diff = abs(final_t4 - r["target_t4"])
        if diff < 1:
            st.success("60단계 후 티록신이 목표치 부근에서 안정화되었습니다.")
        elif diff < 10:
            st.warning("60단계 후 티록신이 목표치에 가까워지고 있습니다.")
        else:
            st.error("영향력이 낮거나 진동이 발생해 아직 목표치에 도달하지 못했습니다.")

st.divider()

# ---------------------------------------------------------------
# 그래프
# ---------------------------------------------------------------
st.subheader("TRH · TSH · 티록신 분비량 변화 그래프")
st.caption("시간 단계에 따른 세 호르몬의 변화 추이입니다.")

if "result" not in st.session_state:
    st.markdown(
        "<div style='color:#8FA6A3; text-align:center; padding:40px 10px;'>"
        "시뮬레이션을 시작하면 이곳에 그래프가 표시됩니다.</div>",
        unsafe_allow_html=True,
    )
else:
    r = st.session_state["result"]
    steps = list(range(len(r["hist_trh"])))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_trh"], mode="lines", name="TRH",
        line=dict(color=TRH_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_tsh"], mode="lines", name="TSH",
        line=dict(color=TSH_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=r["hist_t4"], mode="lines", name="티록신",
        line=dict(color=T4_COLOR, width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=steps, y=[r["target_t4"]] * len(steps), mode="lines", name="목표치",
        line=dict(color=TARGET_COLOR, width=1.5, dash="dash"),
    ))

    fig.update_layout(
        plot_bgcolor="#142629",
        paper_bgcolor="#142629",
        font=dict(color="#EDE7DA"),
        xaxis=dict(title="시간 단계", gridcolor="#2A4448"),
        yaxis=dict(title="분비량", gridcolor="#2A4448"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        height=420,
    )

    st.plotly_chart(fig, use_container_width=True)
