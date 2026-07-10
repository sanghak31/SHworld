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
else:
    st.info("자극! 버튼을 눌러 시뮬레이션을 실행하면 그래프가 표시됩니다.")
