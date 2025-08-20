import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 페이지 설정
st.set_page_config(page_title="정사각형 이동 게임", layout="centered")

# 세션 상태 초기화
if 'x' not in st.session_state:
    st.session_state.x = 5  # 정사각형의 x 좌표
if 'y' not in st.session_state:
    st.session_state.y = 5  # 정사각형의 y 좌표

# 게임 설정
BOARD_WIDTH = 10
BOARD_HEIGHT = 10
SQUARE_SIZE = 0.8
MOVE_STEP = 1

st.title("🎮 정사각형 이동 게임")
st.write("버튼을 눌러 정사각형을 이동시키세요!")

# 컨트롤 버튼들
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("⬆️ W (위)", key="up"):
        if st.session_state.y < BOARD_HEIGHT - 1:
            st.session_state.y += MOVE_STEP
        st.rerun()

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col2:
    if st.button("⬅️ A (왼쪽)", key="left"):
        if st.session_state.x > 0:
            st.session_state.x -= MOVE_STEP
        st.rerun()

with col3:
    if st.button("🔄 리셋", key="reset"):
        st.session_state.x = 5
        st.session_state.y = 5
        st.rerun()

with col4:
    if st.button("➡️ D (오른쪽)", key="right"):
        if st.session_state.x < BOARD_WIDTH - 1:
            st.session_state.x += MOVE_STEP
        st.rerun()

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("⬇️ S (아래)", key="down"):
        if st.session_state.y > 0:
            st.session_state.y -= MOVE_STEP
        st.rerun()

# 게임 보드 그리기
def draw_game_board():
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # 배경 직사각형 (게임 보드)
    background = patches.Rectangle(
        (0, 0), BOARD_WIDTH, BOARD_HEIGHT,
        linewidth=3, edgecolor='black', facecolor='lightgray', alpha=0.3
    )
    ax.add_patch(background)
    
    # 격자 그리기
    for i in range(BOARD_WIDTH + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.5)
    for i in range(BOARD_HEIGHT + 1):
        ax.axhline(y=i, color='gray', linestyle='--', alpha=0.5)
    
    # 플레이어 정사각형
    player_square = patches.Rectangle(
        (st.session_state.x + (1-SQUARE_SIZE)/2, st.session_state.y + (1-SQUARE_SIZE)/2), 
        SQUARE_SIZE, SQUARE_SIZE,
        linewidth=2, edgecolor='red', facecolor='blue', alpha=0.8
    )
    ax.add_patch(player_square)
    
    # 축 설정
    ax.set_xlim(-0.5, BOARD_WIDTH + 0.5)
    ax.set_ylim(-0.5, BOARD_HEIGHT + 0.5)
    ax.set_aspect('equal')
    ax.set_title(f'현재 위치: ({st.session_state.x}, {st.session_state.y})', fontsize=14)
    ax.set_xlabel('X 좌표')
    ax.set_ylabel('Y 좌표')
    
    return fig

# 게임 보드 표시
st.pyplot(draw_game_board())

# 현재 위치 정보
st.info(f"🎯 현재 위치: X = {st.session_state.x}, Y = {st.session_state.y}")

# 게임 설명
with st.expander("게임 설명"):
    st.write("""
    - **W (위)**: 정사각형을 위로 이동
    - **A (왼쪽)**: 정사각형을 왼쪽으로 이동  
    - **S (아래)**: 정사각형을 아래로 이동
    - **D (오른쪽)**: 정사각형을 오른쪽으로 이동
    - **리셋**: 정사각형을 중앙으로 이동
    
    정사각형은 회색 직사각형 경계 내에서만 이동할 수 있습니다.
    """)

# 키보드 단축키 안내
st.markdown("""
---
💡 **팁**: 스트림릿에서는 키보드 이벤트를 직접 처리하기 어려워 버튼을 사용했습니다. 
실제 키보드 입력을 원한다면 `streamlit-keyup` 같은 확장 라이브러리를 사용하거나 
다른 웹 프레임워크(Flask, Django 등)를 고려해보세요.
""")
