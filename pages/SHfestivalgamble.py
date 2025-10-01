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
if 'shuffle_moves' not in st.session_state:
    st.session_state.shuffle_moves = []
if 'current_positions' not in st.session_state:
    st.session_state.current_positions = [0, 1, 2]  # 각 컵의 현재 위치
if 'stage' not in st.session_state:
    st.session_state.stage = 1  # 현재 단계
if 'shuffle_count' not in st.session_state:
    st.session_state.shuffle_count = 5  # 섞는 횟수
if 'wait_time' not in st.session_state:
    st.session_state.wait_time = 2.5  # 대기 시간

# 타이틀
st.title("🥤 야바위 게임 🟡")

# 단계 정보 표시
col_stage1, col_stage2, col_stage3 = st.columns([1, 2, 1])
with col_stage2:
    st.markdown(f"""
    <div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;'>
        <h2 style='margin: 0;'>⭐ 단계 {st.session_state.stage} ⭐</h2>
        <p style='margin: 5px 0 0 0; font-size: 14px;'>
            섞는 횟수: {st.session_state.shuffle_count}회 | 관찰 시간: {st.session_state.wait_time}초
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 게임 설명
with st.expander("게임 방법"):
    st.write("""
    1. **시작** 버튼을 눌러 게임을 시작하세요
    2. 노란색 공이 들어있는 컵을 기억하세요
    3. 컵들이 섞이는 과정을 주의 깊게 지켜보세요
    4. 컵들이 섞인 후, 공이 들어있다고 생각하는 컵을 선택하세요
    5. 정답을 맞춰보세요!
    """)

def generate_shuffle_moves():
    """현재 단계에 맞는 섞기 동작들을 생성"""
    moves = []
    num_moves = st.session_state.shuffle_count  # 현재 단계의 섞는 횟수
    
    for _ in range(num_moves):
        pos1 = random.randint(0, 2)
        pos2 = random.randint(0, 2)
        while pos2 == pos1:
            pos2 = random.randint(0, 2)
        moves.append((pos1, pos2))
    
    return moves

def apply_shuffle_move(positions, move):
    """섞기 동작을 적용하고 새로운 위치 반환"""
    new_positions = positions.copy()
    pos1, pos2 = move
    new_positions[pos1], new_positions[pos2] = new_positions[pos2], new_positions[pos1]
    return new_positions

def show_cups_with_ball(positions=None):
    """공이 보이는 상태의 컵들을 표시"""
    if positions is None:
        positions = [0, 1, 2]
    
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    # 현재 공이 있는 위치 찾기
    ball_current_pos = None
    for i, original_pos in enumerate(positions):
        if original_pos == st.session_state.ball_position:
            ball_current_pos = i
            break
    
    for i in range(3):
        with cols[i]:
            if i == ball_current_pos:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤<br>🟡
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: orange;'><b>컵 {positions[i]+1}번 (공!)</b></p>", 
                           unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>컵 {positions[i]+1}번</p>", unsafe_allow_html=True)

def execute_shuffle_animation():
    """같은 위치에서 섞기 애니메이션을 실행"""
    # 카운트다운
    countdown_container = st.empty()
    
    for i in range(3, 0, -1):
        countdown_container.markdown(f"""
        <div style='text-align: center; font-size: 80px; color: red; font-weight: bold; margin: 30px;'>
            {i}
        </div>
        <h3 style='text-align: center;'>초 후에 섞기 시작!</h3>
        """, unsafe_allow_html=True)
        time.sleep(1)
    
    countdown_container.markdown("""
    <div style='text-align: center; font-size: 60px; color: green; font-weight: bold; margin: 30px;'>
        시작! 🔄
    </div>
    """, unsafe_allow_html=True)
    time.sleep(0.5)
    countdown_container.empty()
    
    # 섞기 상태 표시
    status_container = st.empty()
    status_container.markdown("<h3 style='text-align: center;'>🔄 컵을 섞고 있습니다...</h3>", 
                unsafe_allow_html=True)
    
    # 초기 위치
    current_positions = [0, 1, 2]
    moves = st.session_state.shuffle_moves
    
    # 각 스텝별로 애니메이션 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 컵 표시 영역
    animation_container = st.empty()
    
    for step, move in enumerate(moves):
        pos1, pos2 = move
        
        # 현재 상태 표시 (공은 숨김)
        with animation_container.container():
            st.markdown(f"**{step + 1}/{len(moves)} 단계: 컵 {pos1+1}번 ↔ 컵 {pos2+1}번 교환**")
            
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            
            for i in range(3):
                with cols[i]:
                    # 교환되는 컵들 강조
                    border_color = "red" if i in [pos1, pos2] else "gray"
                    
                    # 모든 컵에서 공을 숨김
                    st.markdown(f"""
                    <div style='text-align: center; font-size: 50px; margin: 15px; 
                               border: 3px solid {border_color}; border-radius: 10px; padding: 10px;'>
                        🥤
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center;'>컵 {current_positions[i]+1}번</p>", 
                               unsafe_allow_html=True)
        
        # 교환 실행
        current_positions = apply_shuffle_move(current_positions, move)
        
        # 진행률 업데이트
        progress_bar.progress((step + 1) / len(moves))
        status_text.text(f"교환 완료: {step + 1}/{len(moves)}")
        
        time.sleep(st.session_state.wait_time)  # 현재 단계의 대기 시간
    
    # 최종 위치 저장
    st.session_state.current_positions = current_positions
    
    # 완료 메시지
    progress_bar.progress(1.0)
    status_text.text("섞기 완료!")
    time.sleep(1)

def show_shuffled_cups():
    """섞인 후의 컵들을 표시 (공은 숨김)"""
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i in range(3):
        with cols[i]:
            st.markdown("""
            <div style='text-align: center; font-size: 60px; margin: 20px;'>
                🥤
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>위치 {i+1}</p>", unsafe_allow_html=True)
            
            # 게임이 끝나지 않았다면 선택 버튼 표시
            if not st.session_state.game_finished:
                if st.button(f"위치 {i+1} 선택", key=f"cup_{i}", use_container_width=True):
                    st.session_state.player_choice = i
                    st.session_state.game_finished = True
                    st.rerun()

def show_result_cups():
    """결과를 보여주는 컵들"""
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    # 현재 공이 있는 실제 위치 찾기
    ball_actual_pos = None
    for i, original_pos in enumerate(st.session_state.current_positions):
        if original_pos == st.session_state.ball_position:
            ball_actual_pos = i
            break
    
    for i in range(3):
        with cols[i]:
            # 정답 위치와 선택한 위치 표시
            if i == ball_actual_pos:
                st.markdown("""
                <div style='text-align: center; font-size: 60px; margin: 20px;'>
                    🥤<br>🟡
                </div>
                """, unsafe_allow_html=True)
                if i == st.session_state.player_choice:
                    st.markdown("<p style='text-align: center; color: green;'><b>✅ 정답!</b></p>", 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='text-align: center; color: orange;'><b>공이 여기에! (원래 컵 {st.session_state.ball_position+1}번)</b></p>", 
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
                    original_cup = st.session_state.current_positions[i]
                    st.markdown(f"<p style='text-align: center;'>빈 컵 (원래 컵 {original_cup+1}번)</p>", 
                               unsafe_allow_html=True)

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
        st.session_state.stage = 1
        st.session_state.shuffle_count = 5
        st.session_state.wait_time = 2.5
        st.session_state.shuffle_moves = generate_shuffle_moves()
        st.session_state.current_positions = [0, 1, 2]
        st.rerun()

elif not st.session_state.shuffled:
    # 공 위치 보여주기 및 섞기 과정
    st.markdown("<h3 style='text-align: center;'>🟡 노란색 공의 위치를 기억하세요!</h3>", 
                unsafe_allow_html=True)
    
    # 컵 섞기 버튼
    if st.button("🔄 컵 섞기 시작!", type="primary", use_container_width=True):
        # 섞기 애니메이션 바로 실행 (컵 표시 생략)
        execute_shuffle_animation()
        st.session_state.shuffled = True
        st.rerun()
    else:
        # 버튼을 누르기 전에는 공 위치만 보여줌
        show_cups_with_ball()
        st.markdown(f"<p style='text-align: center; color: blue;'><b>공은 현재 컵 {st.session_state.ball_position + 1}번에 있습니다!</b></p>", 
                    unsafe_allow_html=True)

elif not st.session_state.game_finished:
    # 선택 단계
    st.markdown("<h3 style='text-align: center;'>🤔 어느 위치에 공이 들어있을까요?</h3>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>위치를 선택해주세요!</p>", 
                unsafe_allow_html=True)
    
    show_shuffled_cups()

else:
    # 결과 표시
    ball_final_pos = None
    for i, original_pos in enumerate(st.session_state.current_positions):
        if original_pos == st.session_state.ball_position:
            ball_final_pos = i
            break
            
    if st.session_state.player_choice == ball_final_pos:
        # 정답! 다음 단계로
        st.markdown("<h2 style='text-align: center; color: green;'>🎉 축하합니다! 정답입니다! 🎉</h2>", 
                    unsafe_allow_html=True)
        st.balloons()
        
        # 다음 단계 정보
        next_stage = st.session_state.stage + 1
        next_shuffle_count = st.session_state.shuffle_count + 1
        next_wait_time = max(0.2, st.session_state.wait_time - 0.1)
        
        st.markdown(f"""
        <div style='text-align: center; background-color: #d4edda; padding: 20px; 
                    border-radius: 10px; margin: 20px 0;'>
            <h3 style='color: #155724; margin: 0;'>다음 단계 정보</h3>
            <p style='color: #155724; margin: 10px 0 0 0; font-size: 16px;'>
                단계: {st.session_state.stage} → <b>{next_stage}</b><br>
                섞는 횟수: {st.session_state.shuffle_count}회 → <b>{next_shuffle_count}회</b><br>
                관찰 시간: {st.session_state.wait_time}초 → <b>{next_wait_time}초</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # 오답! 단계 1로 초기화
        st.markdown("<h2 style='text-align: center; color: red;'>😅 아쉽습니다! 틀렸습니다!</h2>", 
                    unsafe_allow_html=True)
        
        if st.session_state.stage > 1:
            st.markdown(f"""
            <div style='text-align: center; background-color: #f8d7da; padding: 20px; 
                        border-radius: 10px; margin: 20px 0;'>
                <h3 style='color: #721c24; margin: 0;'>단계 초기화</h3>
                <p style='color: #721c24; margin: 10px 0 0 0; font-size: 16px;'>
                    단계 {st.session_state.stage}에서 실패했습니다.<br>
                    다시 <b>단계 1</b>부터 시작합니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    show_result_cups()
    
    # 계속하기 또는 다시 시작 버튼
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.session_state.player_choice == ball_final_pos:
            # 정답 시 - 다음 단계로
            if st.button("🎯 다음 단계로!", type="primary", use_container_width=True):
                st.session_state.stage += 1
                st.session_state.shuffle_count += 1
                st.session_state.wait_time = max(0.2, st.session_state.wait_time - 0.1)
                st.session_state.ball_position = random.randint(0, 2)
                st.session_state.shuffled = False
                st.session_state.game_finished = False
                st.session_state.player_choice = None
                st.session_state.shuffle_moves = generate_shuffle_moves()
                st.session_state.current_positions = [0, 1, 2]
                st.rerun()
        else:
            # 오답 시 - 단계 1로 초기화
            if st.button("🔄 처음부터 다시 시작!", type="primary", use_container_width=True):
                st.session_state.stage = 1
                st.session_state.shuffle_count = 5
                st.session_state.wait_time = 2.5
                st.session_state.ball_position = random.randint(0, 2)
                st.session_state.shuffled = False
                st.session_state.game_finished = False
                st.session_state.player_choice = None
                st.session_state.shuffle_moves = generate_shuffle_moves()
                st.session_state.current_positions = [0, 1, 2]
                st.rerun()

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with ❤️ using Streamlit</p>", 
            unsafe_allow_html=True)
