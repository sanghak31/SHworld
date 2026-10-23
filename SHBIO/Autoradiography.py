import time

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="자기방사법 시뮬레이션", page_icon="☢️", layout="wide")

# ══════════════════════════════════════════════
# 시뮬레이션 설정
# ══════════════════════════════════════════════
T_MAX = 120            # 관찰 시간 (분)
PULSE = 3.0            # 방사성 아미노산이 공급되는 시간 (분)
K1, K2, K3 = 0.10, 0.05, 0.03   # 이동 속도 : 거친면 소포체→골지체, 골지체→분비소낭, 분비소낭→세포 밖
UNIT = 1000            # 투입량 1 μCi 당 방사능량 (cpm/mg) 의 크기를 정하는 값
MIN_DOSE, MAX_DOSE, DEFAULT_DOSE = 0.5, 10.0, 5.0

NAMES = ["거친면 소포체", "골지체", "분비소낭"]
COLORS = ["#3b6fb6", "#d9a21f", "#c4475a"]


@st.cache_data
def simulate(dose):
    """방사성 아미노산 투입 후 구조별 방사능량(cpm/단백질 1mg)을 계산한다."""
    dt = 0.02
    r = g = v = 0.0
    rows = []
    per_row = int(0.5 / dt)
    for i in range(int(T_MAX / dt) + 1):
        t = i * dt
        if i % per_row == 0:
            rows.append((round(t, 1), r * dose * UNIT, g * dose * UNIT, v * dose * UNIT))
        u = 1 / PULSE if t < PULSE else 0.0          # 처음 몇 분 동안만 공급
        dr, dg, dv = u - K1 * r, K1 * r - K2 * g, K2 * g - K3 * v
        r, g, v = r + dr * dt, g + dg * dt, v + dv * dt
    return pd.DataFrame(rows, columns=["t"] + NAMES)


def make_chart(df, t_now, y_max):
    if df is None:
        long = pd.DataFrame({"t": [], "group": [], "value": []})
    else:
        long = df[df["t"] <= t_now].melt("t", var_name="group", value_name="value")
    lines = alt.Chart(long).mark_line(strokeWidth=3).encode(
        x=alt.X("t:Q", title="시간 (분)", scale=alt.Scale(domain=[0, T_MAX])),
        y=alt.Y("value:Q", title="단백질 1mg당 방사능량 (cpm)", scale=alt.Scale(domain=[0, y_max])),
        color=alt.Color("group:N", title=None, scale=alt.Scale(domain=NAMES, range=COLORS),
                        legend=alt.Legend(orient="top")),
    )
    chart = lines
    if df is not None:
        rule = alt.Chart(pd.DataFrame({"t": [t_now]})).mark_rule(strokeDash=[5, 4], color="gray").encode(x="t:Q")
        chart = lines + rule
    return chart.properties(height=380, width="container")


# ══════════════════════════════════════════════
# 세포 그림 (방사능이 센 구조일수록 붉게 표시)
# ══════════════════════════════════════════════
def heat(f):
    f = max(0.0, min(1.0, f))
    a, b = (223, 232, 228), (255, 59, 48)
    return "#%02x%02x%02x" % tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))


def cell_svg(f, t_now):
    fr, fg, fv = f
    b = '<defs><linearGradient id="hg"><stop offset="0" stop-color="#dfe8e4"/><stop offset="1" stop-color="#ff3b30"/></linearGradient></defs>'
    b += '<rect width="720" height="380" rx="18" fill="#f3f8f5"/>'
    b += '<ellipse cx="360" cy="170" rx="335" ry="140" fill="#fff7ea" stroke="#e0a04b" stroke-width="5"/>'
    b += '<circle cx="110" cy="170" r="58" fill="#efe6f8" stroke="#8a5db3" stroke-width="4"/><circle cx="122" cy="178" r="15" fill="#6b3fa0"/>'
    for i in range(4):
        y = 120 + i * 26
        b += f'<rect x="190" y="{y}" width="115" height="16" rx="8" fill="{heat(fr)}" stroke="#3b6fb6" stroke-width="2.5"/>'
        for x in range(200, 300, 20):
            b += f'<circle cx="{x}" cy="{y}" r="3.5" fill="#8a5db3"/>'
    for i in range(4):
        x = 385 + i * 15
        d = f"M{x},105 Q{x - 24},170 {x},235"
        b += f'<path d="{d}" fill="none" stroke="#b07d12" stroke-width="13" stroke-linecap="round"/>'
        b += f'<path d="{d}" fill="none" stroke="{heat(fg)}" stroke-width="8" stroke-linecap="round"/>'
    for x, y in ((520, 115), (565, 170), (520, 225)):
        b += f'<circle cx="{x}" cy="{y}" r="22" fill="{heat(fv)}" stroke="#c4475a" stroke-width="3"/>'
    b += '<line x1="312" y1="170" x2="360" y2="170" stroke="#5b6b66" stroke-width="3" marker-end="url(#ah)"/>'
    b += '<line x1="452" y1="170" x2="488" y2="170" stroke="#5b6b66" stroke-width="3" marker-end="url(#ah)"/>'
    b = b.replace("<defs>", '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5b6b66"/></marker>', 1)
    b += '<line x1="590" y1="170" x2="622" y2="170" stroke="#c4475a" stroke-width="3" stroke-dasharray="6 5" marker-end="url(#ah)"/>'
    lab = 'font-size="16" font-weight="600" fill="#12302c" text-anchor="middle"'
    b += f'<text x="248" y="278" {lab}>거친면 소포체</text><text x="415" y="278" {lab}>골지체</text><text x="545" y="278" {lab}>분비소낭</text>'
    b += f'<text x="110" y="255" {lab}>핵</text><text x="650" y="150" {lab}>세포 밖</text>'
    b += f'<text x="360" y="68" font-size="17" font-weight="600" fill="#a8791a" text-anchor="middle">⏱ 투입 후 {t_now}분</text>'
    b += '<rect x="230" y="328" width="260" height="14" rx="7" fill="url(#hg)"/>'
    b += '<text x="225" y="340" font-size="13" fill="#5b6b66" text-anchor="end">낮음</text><text x="495" y="340" font-size="13" fill="#5b6b66">높음</text>'
    b += '<text x="360" y="365" font-size="13" fill="#5b6b66" text-anchor="middle">붉을수록 방사능이 강해요 (각 구조의 최댓값 기준)</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 380" width="720" height="380" font-family="Noto Sans KR, Malgun Gothic, Apple SD Gothic Neo, sans-serif">{b}</svg>'


# ══════════════════════════════════════════════
# 상태
# ══════════════════════════════════════════════
ss = st.session_state
ss.setdefault("dose_used", None)   # 투입한 방사성 동위원소의 양 (None이면 아직 투입 전)
ss.setdefault("t_now", T_MAX)
ss.setdefault("play", False)


def inject():
    ss.dose_used = ss.dose
    ss.t_now = T_MAX
    ss.play = True


def reset():
    ss.dose_used = None
    ss.t_now = T_MAX
    ss.play = False


# ══════════════════════════════════════════════
# 화면
# ══════════════════════════════════════════════
st.title("☢️ 자기방사법 시뮬레이션")
st.write("방사성 동위원소가 들어 있는 아미노산을 세포에 넣으면, 분비 단백질이 만들어져 세포 밖으로 나가기까지 "
         "**거친면 소포체 → 골지체 → 분비소낭** 순서로 방사능이 차례로 높아졌다 낮아져요.")

left, right = st.columns([1, 2.3])

with left:
    st.subheader("⚙️ 옵션")
    st.slider("방사성 동위원소의 양 (μCi)", MIN_DOSE, MAX_DOSE, DEFAULT_DOSE, 0.5, key="dose",
              help="아미노산에 표지된 방사성 동위원소의 양이에요. 많을수록 그래프가 높아져요.")
    auto_axis = st.toggle("세로축 자동 맞춤", value=False,
                          help="끄면 세로축이 고정되어 투입량에 따라 그래프 높이가 달라지는 것을 비교할 수 있어요.")
    st.button("💉 방사성 동위원소가 함유된 아미노산 투입", type="primary", on_click=inject, use_container_width=True)
    if ss.dose_used is not None:
        st.button("↩️ 처음으로", on_click=reset, use_container_width=True)
        st.success(f"현재 그래프 : {ss.dose_used:g} μCi 투입")
        if ss.dose != ss.dose_used:
            st.caption("투입량을 바꿨다면 위 버튼을 다시 눌러 투입하세요.")
    else:
        st.info("투입량을 정하고 **투입** 버튼을 눌러 보세요.")

injected = ss.dose_used is not None
df = simulate(ss.dose_used) if injected else None
y_max = (float(df[NAMES].to_numpy().max()) * 1.15) if (injected and auto_axis) else MAX_DOSE * UNIT * 0.95

with right:
    chart_ph = st.empty()
    play_again = False
    if injected:
        c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
        c1.slider("⏱ 경과 시간 (분)", 0, T_MAX, key="t_now")
        play_again = c2.button("▶ 다시 재생")

detail_ph = st.empty()


def draw(t_now):
    chart_ph.altair_chart(make_chart(df, t_now, y_max))
    if df is None:
        detail_ph.empty()
        return
    row = df.iloc[int(round(t_now / 0.5))]
    peaks = [float(df[n].max()) for n in NAMES]
    fr = [row[n] / p if p else 0 for n, p in zip(NAMES, peaks)]
    with detail_ph.container():
        st.divider()
        a, b = st.columns([1.4, 1])
        a.image(cell_svg(fr, t_now))
        with b:
            st.markdown(f"#### ⏱ {t_now}분 일 때의 방사능량")
            for n, color in zip(NAMES, COLORS):
                st.metric(n, f"{row[n]:,.0f} cpm/mg")


if injected:
    if ss.play or play_again:
        ss.play = False
        for tt in range(0, T_MAX + 1, 2):
            draw(tt)
            time.sleep(0.04)
    draw(ss.t_now)
else:
    draw(0)

# ══════════════════════════════════════════════
# 결과 해석
# ══════════════════════════════════════════════
if injected:
    st.divider()
    st.subheader("📊 결과 해석")
    rows = ["| 구조 | 방사능이 가장 높은 시점 | 그때의 방사능량 |", "|---|---|---|"]
    for n in NAMES:
        i = df[n].idxmax()
        rows.append(f"| {n} | 약 {df.loc[i, 't']:g}분 | {df.loc[i, n]:,.0f} cpm/mg |")
    st.markdown("\n".join(rows))
    st.markdown(
        "- 방사성 아미노산은 단백질을 합성하는 **거친면 소포체**에서 가장 먼저 단백질에 들어가요.\n"
        "- 이 단백질이 **골지체**를 거쳐 **분비소낭**으로 이동하면서, 방사능이 높은 구조가 차례로 바뀌어요.\n"
        "- 그래서 방사능이 높아지는 순서(거친면 소포체 → 골지체 → 분비소낭)가 **분비 단백질의 이동 경로**를 알려 줘요.\n"
        "- 투입한 방사성 동위원소의 양을 바꾸면 **그래프의 높이만** 달라지고, 최고점이 나타나는 순서는 그대로예요."
    )

with st.expander("📌 시뮬레이션의 가정"):
    st.markdown(
        f"- 방사성 아미노산은 투입 후 처음 약 {PULSE:g}분 동안만 단백질 합성에 쓰이고, 그 뒤에는 방사성이 없는 아미노산이 쓰인다고 가정했어요.\n"
        "- 단백질은 거친면 소포체 → 골지체 → 분비소낭 → 세포 밖으로만 이동하고, 방사성 동위원소가 붕괴하는 양은 무시했어요.\n"
        "- 방사능량의 단위(cpm/mg)와 수치는 이해를 돕기 위한 예시 값이에요."
    )
