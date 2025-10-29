import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="메모리 카드 게임", page_icon="🎴", layout="centered")

# 이모지 카드 세트
CARD_EMOJIS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"]

# 세션 상태 초기화
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if 'cards' not in st.session_state:
    st.session_state.cards = []

if 'revealed' not in st.session_state:
    st.session_state.revealed = []

if 'matched' not in st.session_state:
    st.session_state.matched = []

if 'first_card' not in st.session_state:
    st.session_state.first_card = None

if 'second_card' not in st.session_state:
    st.session_state.second_card = None

if 'failures' not in st.session_state:
    st.session_state.failures = 0

if 'matches_found' not in st.session_state:
    st.session_state.matches_found = 0

if 'preview_end_time' not in st.session_state:
    st.session_state.preview_end_time = None

if 'show_cards_until' not in st.session_state:
    st.session_state.show_cards_until = None

def start_game():
    """게임 시작 및 초기화"""
    st.session_state.cards = CARD_EMOJIS * 2
    random.shuffle(st.session_state.cards)
    st.session_state.revealed = [False] * 16
    st.session_state.matched = [False] * 16
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.failures = 0
    st.session_state.matches_found = 0
    st.session_state.game_started = True
    st.session_state.preview_end_time = time.time() + 5  # 5초 후
    st.session_state.show_cards_until = None

def reset_game():
    """게임 리셋"""
    st.session_state.game_started = False
    st.session_state.cards = []
    st.session_state.revealed = []
    st.session_state.matched = []
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.failures = 0
    st.session_state.matches_found = 0
    st.session_state.preview_end_time = None
    st.session_state.show_cards_until = None

def card_clicked(index):
    """카드 클릭 처리"""
    # 이미 매칭되었거나 선택된 카드면 무시
    if st.session_state.matched[index]:
        return
    if st.session_state.first_card == index:
        return
    
    # 첫 번째 카드 선택
    if st.session_state.first_card is None:
        st.session_state.first_card = index
        st.session_state.revealed[index] = True
    # 두 번째 카드 선택
    elif st.session_state.second_card is None:
        st.session_state.second_card = index
        st.session_state.revealed[index] = True
        st.session_state.show_cards_until = time.time() + 1  # 1초간 보여주기

# 제목
st.title("🎴 메모리 카드 게임")
st.markdown("같은 그림의 카드를 찾으세요!")

# 게임 시작 전
if not st.session_state.game_started:
    st.info("🎮 게임을 시작하면 5초 동안 모든 카드를 볼 수 있습니다!")
    if st.button("🚀 게임 시작", use_container_width=True, type="primary"):
        start_game()
        st.rerun()
    st.stop()

# 미리보기 중인지 확인
is_preview = False
if st.session_state.preview_end_time is not None:
    current_time = time.time()
    if current_time < st.session_state.preview_end_time:
        is_preview = True
        remaining = int(st.session_state.preview_end_time - current_time) + 1
        st.warning(f"⏱️ 카드를 기억하세요! {remaining}초 남음...")
    else:
        st.session_state.preview_end_time = None

# 두 카드를 보여주는 중인지 확인
is_showing_cards = False
if st.session_state.show_cards_until is not None:
    current_time = time.time()
    if current_time < st.session_state.show_cards_until:
        is_showing_cards = True
    else:
        # 1초 경과 후 매칭 확인
        first_idx = st.session_state.first_card
        second_idx = st.session_state.second_card
        
        if st.session_state.cards[first_idx] == st.session_state.cards[second_idx]:
            # 매칭 성공 - 실패 횟수 증가 없음
            st.session_state.matched[first_idx] = True
            st.session_state.matched[second_idx] = True
            st.session_state.matches_found += 1
        else:
            # 매칭 실패 - 실패 횟수 증가
            st.session_state.failures += 1
            st.session_state.revealed[first_idx] = False
            st.session_state.revealed[second_idx] = False
        
        st.session_state.first_card = None
        st.session_state.second_card = None
        st.session_state.show_cards_until = None
        st.rerun()

# 게임 정보
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("실패 횟수", f"{st.session_state.failures}/10")
with col2:
    st.metric("찾은 짝", f"{st.session_state.matches_found}/8")
with col3:
    if st.button("🔄 새 게임"):
        reset_game()
        st.rerun()

st.markdown("---")

# 게임 실패 체크
if st.session_state.failures >= 10:
    st.error("💀 게임 오버! 실패 횟수가 10번을 초과했습니다!")
    if st.button("🎮 다시 도전하기", type="primary", use_container_width=True):
        reset_game()
        st.rerun()
    st.stop()

# 카드 그리드 (4x4)
for row in range(4):
    cols = st.columns(4)
    for col in range(4):
        index = row * 4 + col
        with cols[col]:
            # 카드를 보여줘야 하는 경우들
            should_show = (
                is_preview or  # 미리보기 중
                st.session_state.matched[index] or  # 매칭된 카드
                st.session_state.revealed[index]  # 현재 공개된 카드
            )
            
            if should_show:
                # 매칭된 카드는 초록색, 나머지는 노란색
                bg_color = "#90EE90" if st.session_state.matched[index] else "#FFD700"
                st.markdown(
                    f"<div style='background-color: {bg_color}; padding: 30px; text-align: center; "
                    f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                    f"display: flex; align-items: center; justify-content: center;'>"
                    f"{st.session_state.cards[index]}</div>",
                    unsafe_allow_html=True
                )
            else:
                # 뒤집힌 카드 (클릭 가능)
                # 미리보기 중이거나 카드 보여주는 중이면 클릭 비활성화
                disabled = is_preview or is_showing_cards or st.session_state.second_card is not None
                if st.button("❓", key=f"card_{index}", use_container_width=True, disabled=disabled):
                    card_clicked(index)
                    st.rerun()

# 미리보기나 카드 보여주기 중이면 자동 새로고침
if is_preview or is_showing_cards:
    time.sleep(0.1)
    st.rerun()

# 게임 클리어
if st.session_state.matches_found == 8 and st.session_state.failures < 10:
    st.balloons()
    st.success(f"🎉 축하합니다! 실패 {st.session_state.failures}번으로 모든 짝을 찾았습니다!")
    if st.button("🎮 다시 플레이", type="primary"):
        reset_game()
        st.rerun()
