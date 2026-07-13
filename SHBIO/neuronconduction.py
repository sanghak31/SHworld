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

st.subheader("🔗 시냅스 옵션")

synapse_count = st.slider(
    "시냅스 개수",
    min_value=0,
    max_value=5,
    value=0,
    step=1,
    help="자극 전달 경로에 존재하는 시냅스의 개수입니다.",
)

synapse_positions = []
if synapse_count > 0:
    st.markdown("**시냅스 위치 (cm)**")
    default_gap = neuron_length / (synapse_count + 1)
    pos_cols = st.columns(synapse_count)
    for i in range(synapse_count):
        default_val = int(round(default_gap * (i + 1)))
        default_val = min(max(default_val, 0), int(neuron_length))
        with pos_cols[i]:
            pos = st.number_input(
                f"시냅스 {i + 1}의 위치",
                min_value=0,
                max_value=int(neuron_length),
                value=default_val,
                step=1,
                key=f"synapse_pos_{i}",
            )
        synapse_positions.append(int(pos))

synapse_delay = st.slider(
    "시냅스간 자극 전달 시간 (ms)",
    min_value=1,
    max_value=100,
    value=5,
    step=1,
    help="자극이 시냅스를 만날 때마다 추가로 소요되는 시간입니다. (시냅스 개수가 0이면 적용되지 않습니다)",
)

synapse_positions_sorted = sorted(synapse_positions)

st.divider()

# ============================================================
# 2. 시뮬레이션
# ============================================================
st.header("▶️ 시뮬레이션")


def compute_timeline(length, speed, positions, delay):
    """뉴런 길이/속도/시냅스 위치/시냅스 지연시간을 받아
    (시간, 위치) 경로 좌표들과 총 소요 시간, 시냅스 통과 이벤트를 계산합니다."""
    positions_valid = [p for p in positions if 0 < p < length]
    boundaries = [0] + sorted(positions_valid) + [length]

    t_points = [0.0]
    pos_points = [0.0]
    synapse_events = []  # (통과 시각, 위치)
    current_time = 0.0

    for i in range(len(boundaries) - 1):
        a, b = boundaries[i], boundaries[i + 1]
        seg_time = (b - a) / speed
        current_time += seg_time
        t_points.append(current_time)
        pos_points.append(b)

        is_synapse_boundary = i < len(boundaries) - 2  # 마지막 구간(끝점)이 아니면 시냅스 위치
        if is_synapse_boundary:
            synapse_events.append((current_time, b))
            current_time += delay
            t_points.append(current_time)
            pos_points.append(b)

    return t_points, pos_points, current_time, synapse_events


if "result_time" not in st.session_state:
    st.session_state.result_time = None
if "timeline" not in st.session_state:
    st.session_state.timeline = None
if "last_length" not in st.session_state:
    st.session_state.last_length = neuron_length
if "last_speed" not in st.session_state:
    st.session_state.last_speed = signal_speed
if "last_synapses" not in st.session_state:
    st.session_state.last_synapses = (tuple(synapse_positions_sorted), synapse_count, synapse_delay)

# 옵션이 바뀌면 이전 결과 초기화
current_synapses = (tuple(synapse_positions_sorted), synapse_count, synapse_delay)
if (
    st.session_state.last_length != neuron_length
    or st.session_state.last_speed != signal_speed
    or st.session_state.last_synapses != current_synapses
):
    st.session_state.result_time = None
    st.session_state.timeline = None
    st.session_state.last_length = neuron_length
    st.session_state.last_speed = signal_speed
    st.session_state.last_synapses = current_synapses

stimulate = st.button("⚡ 자극!", type="primary", use_container_width=True)

chart_placeholder = st.empty()
result_placeholder = st.empty()


def draw_neuron(position, length, synapse_positions=None, passing=False):
    fig, ax = plt.subplots(figsize=(10, 2.6))
    ax.hlines(0, 0, length, color="#999999", linewidth=6, zorder=1)
    ax.scatter([0], [0], color="#1f77b4", s=140, zorder=2, label="시작점 (세포체)")
    ax.scatter([length], [0], color="#2ca02c", s=140, zorder=2, label="끝점 (축삭 말단)")

    if synapse_positions:
        ax.scatter(
            synapse_positions,
            [0] * len(synapse_positions),
            color="#9467bd",
            marker="^",
            s=170,
            zorder=2,
            label="시냅스",
        )
        for idx, sp in enumerate(synapse_positions, start=1):
            ax.annotate(
                f"S{idx}", (sp, 0), textcoords="offset points", xytext=(0, 14),
                ha="center", fontsize=9, color="#9467bd",
            )

    marker_color = "#ff7f0e" if passing else "#d62728"
    ax.scatter([position], [0], color=marker_color, s=220, zorder=3, label="자극 위치")
    if passing:
        ax.text(position, 0.55, "시냅스 통과 중...", ha="center", fontsize=10, color="#ff7f0e")

    ax.set_xlim(-length * 0.03, length * 1.03)
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.set_xlabel("뉴런을 따른 위치 (cm)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.62), ncol=4, frameon=False, fontsize=8)
    fig.tight_layout()
    return fig


# 초기 화면 (아직 자극 전)
if not stimulate and st.session_state.result_time is None:
    chart_placeholder.pyplot(draw_neuron(0, neuron_length, synapse_positions_sorted))
    plt.close("all")

# 자극! 버튼 클릭 시 애니메이션 실행
if stimulate:
    delay_value = synapse_delay if synapse_count > 0 else 0
    t_points, pos_points, total_time, synapse_events = compute_timeline(
        neuron_length, signal_speed, synapse_positions_sorted, delay_value
    )

    anim_duration = 2.5  # 초 단위, 보기 좋게 압축한 애니메이션 재생 시간
    frames_total = 70
    total_units = total_time if total_time > 0 else 1

    for seg_idx in range(len(t_points) - 1):
        t_a, t_b = t_points[seg_idx], t_points[seg_idx + 1]
        p_a, p_b = pos_points[seg_idx], pos_points[seg_idx + 1]
        seg_duration = t_b - t_a
        seg_frames = max(1, int(round(frames_total * (seg_duration / total_units))))
        is_pause = (p_a == p_b) and (seg_duration > 0)  # 위치 고정 + 시간 경과 -> 시냅스 통과 중

        for f in range(seg_frames):
            frac = f / seg_frames
            position = p_a + (p_b - p_a) * frac
            chart_placeholder.pyplot(
                draw_neuron(position, neuron_length, synapse_positions_sorted, passing=is_pause)
            )
            plt.close("all")
            time.sleep(anim_duration / frames_total)

    # 최종 위치(끝점) 확실히 표시
    chart_placeholder.pyplot(draw_neuron(neuron_length, neuron_length, synapse_positions_sorted))
    plt.close("all")

    st.session_state.result_time = total_time
    st.session_state.timeline = (t_points, pos_points, synapse_events)

if st.session_state.result_time is not None:
    synapse_note = (
        f" (시냅스 {synapse_count}개 통과 지연 {synapse_count * synapse_delay}ms 포함)"
        if synapse_count > 0
        else ""
    )
    result_placeholder.success(
        f"✅ 자극이 시작점부터 끝점({neuron_length} cm)까지 도달하는 데 걸린 시간: "
        f"**{st.session_state.result_time:.2f} ms**{synapse_note}"
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
    t_points, pos_points, synapse_events = st.session_state.timeline

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(t_points, pos_points, color="#d62728", linewidth=2.5)
    for ev_time, ev_pos in synapse_events:
        ax2.axvline(ev_time, color="#9467bd", linestyle=":", alpha=0.5)
        ax2.axvspan(ev_time, ev_time + synapse_delay, color="#9467bd", alpha=0.08)
    ax2.set_xlabel("시간 (ms)")
    ax2.set_ylabel("자극 위치 (cm)")
    title = "시간에 따른 자극 전달 위치"
    if synapse_events:
        title += " (보라색 구간 = 시냅스 통과 지연)"
    ax2.set_title(title)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close("all")

    c1, c2, c3 = st.columns(3)
    c1.metric("뉴런 길이", f"{neuron_length} cm")
    c2.metric("전달 속도", f"{signal_speed} cm/ms")
    c3.metric("총 걸린 시간", f"{total_time:.2f} ms")
    if synapse_count > 0:
        st.caption(
            f"시냅스 {synapse_count}개 × {synapse_delay}ms = "
            f"총 {synapse_count * synapse_delay}ms의 시냅스 지연이 포함된 값입니다."
        )

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
