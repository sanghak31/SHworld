
import time
import glob

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import streamlit as st

st.set_page_config(page_title="신경 자극 전달 시뮬레이션", page_icon="🧠", layout="wide")


# ------------------------------------------------------------
# 한글 폰트 설정 (Streamlit Cloud 등 리눅스 서버에서 한글 깨짐 방지)
# packages.txt에 'fonts-nanum'을 추가해 나눔고딕이 설치되어 있어야 합니다.
# ------------------------------------------------------------
@st.cache_resource
def set_korean_font():
    candidates = glob.glob("/usr/share/fonts/**/Nanum*.ttf", recursive=True)
    if candidates:
        font_path = candidates[0]
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        plt.rcParams["font.family"] = font_name
    else:
        # 나눔고딕이 없을 경우 시스템에 있는 다른 한글 지원 폰트를 탐색
        for name in ["Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"]:
            if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
                plt.rcParams["font.family"] = name
                break
    plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지


set_korean_font()

st.title("🧠 신경 자극 전달 시뮬레이션")
st.caption("뉴런을 따라 자극(활동전위)이 전달되는 과정을 시뮬레이션합니다.")

# ============================================================
# 1. 옵션
# ============================================================
st.header("⚙️ 옵션")

col1, col2 = st.columns(2)
with col1:
    neuron_length = st.slider(
        "뉴런 총 길이 (cm)",
        min_value=100,
        max_value=3000,
        value=1000,
        step=50,
        help="자극이 세포체에서 축삭 말단까지 이동해야 하는 총 거리입니다.",
    )
with col2:
    signal_speed = st.slider(
        "자극 전달 속도 (cm/ms)",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
        help="자극(활동전위)이 축삭을 따라 이동하는 속도입니다.",
    )

st.divider()

# ============================================================
# 2. 시뮬레이션
# ============================================================
st.header("▶️ 시뮬레이션")

if "result_time" not in st.session_state:
    st.session_state.result_time = None
if "last_length" not in st.session_state:
    st.session_state.last_length = neuron_length
if "last_speed" not in st.session_state:
    st.session_state.last_speed = signal_speed

# 옵션이 바뀌면 이전 결과 초기화
if (
    st.session_state.last_length != neuron_length
    or st.session_state.last_speed != signal_speed
):
    st.session_state.result_time = None
    st.session_state.last_length = neuron_length
    st.session_state.last_speed = signal_speed

stimulate = st.button("⚡ 자극!", type="primary", use_container_width=True)

chart_placeholder = st.empty()
result_placeholder = st.empty()


def draw_neuron(position, length):
    fig, ax = plt.subplots(figsize=(10, 2.2))
    ax.hlines(0, 0, length, color="#999999", linewidth=6, zorder=1)
    ax.scatter([0], [0], color="#1f77b4", s=140, zorder=2, label="시작점 (세포체)")
    ax.scatter([length], [0], color="#2ca02c", s=140, zorder=2, label="끝점 (축삭 말단)")
    ax.scatter([position], [0], color="#d62728", s=220, zorder=3, label="자극 위치")
    ax.set_xlim(-length * 0.03, length * 1.03)
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.set_xlabel("뉴런을 따른 위치 (cm)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.55), ncol=3, frameon=False)
    fig.tight_layout()
    return fig


# 초기 화면 (아직 자극 전)
if not stimulate and st.session_state.result_time is None:
    chart_placeholder.pyplot(draw_neuron(0, neuron_length))
    plt.close("all")

# 자극! 버튼 클릭 시 애니메이션 실행
if stimulate:
    total_time = neuron_length / signal_speed  # ms (실제 계산값)
    frames = 60
    anim_duration = 2.0  # 초 단위, 보기 좋게 압축한 애니메이션 재생 시간

    for i in range(frames + 1):
        frac = i / frames
        position = frac * neuron_length
        chart_placeholder.pyplot(draw_neuron(position, neuron_length))
        plt.close("all")
        time.sleep(anim_duration / frames)

    st.session_state.result_time = total_time

if st.session_state.result_time is not None:
    result_placeholder.success(
        f"✅ 자극이 시작점부터 끝점({neuron_length} cm)까지 도달하는 데 걸린 시간: "
        f"**{st.session_state.result_time:.2f} ms**"
    )
else:
    result_placeholder.info("‘자극!’ 버튼을 누르면 시뮬레이션이 시작됩니다.")

st.divider()

# ============================================================
# 3. 그래프
# ============================================================
st.header("📈 그래프")


def action_potential(t, onset, t_rise=1.0, t_fall=1.5, t_recover=2.5):
    """onset 시점을 기준으로 한 활동전위 파형 (mV). 교과서/모의고사에 나오는
    막전위 변화 그래프와 같은 형태로, onset 이전에는 반드시 휴지 전위를
    그대로 유지하고(음수 구간 변화 없음), onset 이후에만
    탈분극 → 재분극(과분극) → 재분극 완료 순서로 변화합니다."""
    rest = -70.0
    peak = 40.0
    trough = -85.0

    rel = t - onset
    v = np.full_like(t, rest, dtype=float)

    # 1) 탈분극: 휴지 전위 -> 최고점 (부드러운 상승)
    m1 = (rel >= 0) & (rel < t_rise)
    frac1 = rel[m1] / t_rise
    v[m1] = rest + (peak - rest) * np.sin(frac1 * np.pi / 2)

    # 2) 재분극(+ 과분극): 최고점 -> 최저점
    m2 = (rel >= t_rise) & (rel < t_rise + t_fall)
    frac2 = (rel[m2] - t_rise) / t_fall
    v[m2] = peak + (trough - peak) * (1 - np.cos(frac2 * np.pi)) / 2

    # 3) 재분극 완료: 최저점 -> 휴지 전위로 복귀
    m3 = (rel >= t_rise + t_fall) & (rel < t_rise + t_fall + t_recover)
    frac3 = (rel[m3] - (t_rise + t_fall)) / t_recover
    v[m3] = trough + (rest - trough) * (1 - np.cos(frac3 * np.pi)) / 2

    # 그 외 구간(onset 이전 및 회복 완료 이후)은 휴지 전위(-70 mV) 그대로 유지
    return v


if st.session_state.result_time is not None:
    total_time = st.session_state.result_time
    t = np.linspace(0, total_time, 200)
    pos = signal_speed * t

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(t, pos, color="#d62728", linewidth=2.5)
    ax2.set_xlabel("시간 (ms)")
    ax2.set_ylabel("자극 위치 (cm)")
    ax2.set_title("시간에 따른 자극 전달 위치")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close("all")

    c1, c2, c3 = st.columns(3)
    c1.metric("뉴런 길이", f"{neuron_length} cm")
    c2.metric("전달 속도", f"{signal_speed} cm/ms")
    c3.metric("총 걸린 시간", f"{total_time:.2f} ms")

    st.subheader("🧪 시작점 vs 끝점 활동전위")
    st.caption("시작점(파란색)에서 발생한 활동전위가 전달 지연 시간(빨간색)만큼 늦게 끝점에 도달합니다. "
               "(실제 HH 모델이 아닌 단순화된 스파이크 파형입니다.)")

    ap_duration = 1.0 + 1.5 + 2.5  # t_rise + t_fall + t_recover
    t_end = total_time + ap_duration + 1.0  # 끝점 파형이 완전히 끝날 때까지 여유 포함
    t_ap = np.linspace(0, t_end, 500)
    v_start = action_potential(t_ap, onset=0.0)
    v_end = action_potential(t_ap, onset=total_time)

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(t_ap, v_start, color="#1f77b4", linewidth=2.2, label="시작점의 활동전위")
    ax3.plot(t_ap, v_end, color="#d62728", linewidth=2.2, label="끝점의 활동전위")
    ax3.axhline(-70, color="gray", linestyle="--", linewidth=1, alpha=0.6, label="휴지 전위 (-70 mV)")
    ax3.set_xlim(0, t_end)
    ax3.set_xlabel("시간 (ms)")
    ax3.set_ylabel("막전위 (mV)")
    ax3.set_title("시작점과 끝점에서의 활동전위 비교")
    ax3.grid(alpha=0.3)
    ax3.legend(loc="upper right")
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close("all")
else:
    st.info("자극! 버튼을 눌러 시뮬레이션을 실행하면 그래프가 표시됩니다.")
