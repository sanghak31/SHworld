import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="야바위 게임", page_icon="🥤", layout="centered")

# 세션 상태 초기화
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'ball_position' not in st.session_state:
    st.session_state.ball_position = 0
if 'shuffled' not in st.session_state:
    st.session_state.shuffled = False
if 'game_finished' not in st.session_state:
    st.session_state.game_finished = False
if 'player_choice' not in st.session_state:
    st.session_state.player_choice = None

# 타이틀
st.title("🥤 야바위 게임 🟡")
st.markdown("---")

# 게임 설명
with st.expander("게임 방법"):
    st.write("""
    1. **시작** 버튼을 눌러 게임을 시작하세요
    2. 노란색 공이 들어있는 컵을 기억하세요
    3. 컵들이 섞인 후, 공이 들어있다고 생각하는 컵을 선택하세요
    4. 정답을 맞춰보세요!
    """)

# 메인 게임 영역
col1, col2, col3 = st.columns(3)

def show_cups_with_ball():
    """공이 보이는 상태의 컵들을 표시"""
    cols = [col1, col2, col3]
    for i in range(3):
        with cols[i]:
            if i == st.session_state.ball_position:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤<br>🟡
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: orange;'><b>공이 여기에!</b></p>", 
                           unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<p style='text-align: center;'>빈 컵</p>", unsafe_allow_html=True)

def show_shuffled_cups():
    """섞인 후의 컵들을 표시 (공은 숨김)"""
    cols = [col1, col2, col3]
    for i in range(3):
        with cols[i]:
            st.markdown("""
            <div style='text-align: center; font-size: 60px; margin: 20px;'>
                🥤
            </div>
            """, unsafe_allow_html=True)
            
            # 게임이 끝나지 않았다면 선택 버튼 표시
            if not st.session_state.game_finished:
                if st.button(f"컵 {i+1} 선택", key=f"cup_{i}", use_container_width=True):
                    st.session_state.player_choice = i
                    st.session_state.game_finished = True
                    st.rerun()

def show_result_cups():
    """결과를 보여주는 컵들"""
    cols = [col1, col2, col3]
    for i in range(3):
        with cols[i]:
            # 정답 컵과 선택한 컵 표시
            if i == st.session_state.ball_position:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤<br>🟡
                </div>
                """, unsafe_allow_html=True)
                if i == st.session_state.player_choice:
                    st.markdown("<p style='text-align: center; color: green;'><b>✅ 정답!</b></p>", 
                               unsafe_allow_html=True)
                else:
                    st.markdown("<p style='text-align: center; color: orange;'><b>공이 여기에 있었어요!</b></p>", 
                               unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤
                </div>
                """, unsafe_allow_html=True)
                if i == st.session_state.player_choice:
                    st.markdown("<p style='text-align: center; color: red;'><b>❌ 당신의 선택</b></p>", 
                               unsafe_allow_html=True)
                else:
                    st.markdown("<p style='text-align: center;'>빈 컵</p>", unsafe_allow_html=True)

# 게임 로직
if not st.session_state.game_started:
    # 게임 시작 전
    st.markdown("<h3 style='text-align: center;'>🎮 게임을 시작하려면 버튼을 누르세요!</h3>", 
                unsafe_allow_html=True)
    
    if st.button("🚀 게임 시작!", type="primary", use_container_width=True):
        st.session_state.game_started = True
        st.session_state.ball_position = random.randint(0, 2)
        st.session_state.shuffled = False
        st.session_state.game_finished = False
        st.session_state.player_choice = None
        st.rerun()

elif not st.session_state.shuffled:
    # 공 위치 보여주기
    st.markdown("<h3 style='text-align: center;'>🟡 노란색 공의 위치를 기억하세요!</h3>", 
                unsafe_allow_html=True)
    
    show_cups_with_ball()
    
    # 3초 후 자동으로 섞기
    if st.button("🔄 컵 섞기!", type="primary", use_container_width=True):
        with st.spinner("컵을 섞고 있습니다..."):
            time.sleep(2)  # 섞는 애니메이션 효과
        st.session_state.shuffled = True
        st.rerun()

elif not st.session_state.game_finished:
    # 선택 단계
    st.markdown("<h3 style='text-align: center;'>🤔 어느 컵에 공이 들어있을까요?</h3>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>컵을 선택해주세요!</p>", 
                unsafe_allow_html=True)
    
    show_shuffled_cups()

else:
    # 결과 표시
    if st.session_state.player_choice == st.session_state.ball_position:
        st.markdown("<h2 style='text-align: center; color: green;'>🎉 축하합니다! 정답입니다! 🎉</h2>", 
                    unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown("<h2 style='text-align: center; color: red;'>😅 아쉽습니다! 틀렸습니다!</h2>", 
                    unsafe_allow_html=True)
    
    show_result_cups()
    
    # 다시 시작 버튼
    st.markdown("---")
    col_restart1, col_restart2, col_restart3 = st.columns([1, 2, 1])
    with col_restart2:
        if st.button("🔄 다시 시작하기", type="primary", use_container_width=True):
            st.session_state.game_started = False
            st.session_state.shuffled = False
            st.session_state.game_finished = False
            st.session_state.player_choice = None
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with ❤️ using Streamlit</p>", 
            unsafe_allow_html=True)
