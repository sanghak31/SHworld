import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="메모리 카드 게임", page_icon="🎴", layout="centered")

# 이모지 카드 세트
CARD_EMOJIS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"]

# 세션 상태 초기화
if 'cards' not in st.session_state:
    st.session_state.cards = CARD_EMOJIS * 2
    random.shuffle(st.session_state.cards)

if 'revealed' not in st.session_state:
    st.session_state.revealed = [False] * 16

if 'matched' not in st.session_state:
    st.session_state.matched = [False] * 16

if 'first_card' not in st.session_state:
    st.session_state.first_card = None

if 'second_card' not in st.session_state:
    st.session_state.second_card = None

if 'moves' not in st.session_state:
    st.session_state.moves = 0

if 'matches_found' not in st.session_state:
    st.session_state.matches_found = 0

if 'checking' not in st.session_state:
    st.session_state.checking = False

if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if 'preview_time' not in st.session_state:
    st.session_state.preview_time = None

def reset_game():
    st.session_state.cards = CARD_EMOJIS * 2
    random.shuffle(st.session_state.cards)
    st.session_state.revealed = [False] * 16
    st.session_state.matched = [False] * 16
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.moves = 0
    st.session_state.matches_found = 0
    st.session_state.checking = False
    st.session_state.game_started = False
    st.session_state.preview_time = None

def start_game():
    # 게임 초기화
    st.session_state.cards = CARD_EMOJIS * 2
    random.shuffle(st.session_state.cards)
    st.session_state.revealed = [False] * 16
    st.session_state.matched = [False] * 16
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.moves = 0
    st.session_state.matches_found = 0
    st.session_state.checking = False
    st.session_state.game_started = True
    st.session_state.preview_time = time.time()

def card_clicked(index):
    # 이미 매칭되었거나 공개된 카드는 클릭 불가
    if st.session_state.matched[index] or st.session_state.revealed[index]:
        return
    
    # 체크 중이면 클릭 불가
    if st.session_state.checking:
        return
    
    # 카드 공개
    st.session_state.revealed[index] = True
    
    # 첫 번째 카드 선택
    if st.session_state.first_card is None:
        st.session_state.first_card = index
    # 두 번째 카드 선택
    elif st.session_state.second_card is None and index != st.session_state.first_card:
        st.session_state.second_card = index
        st.session_state.moves += 1
        st.session_state.checking = True
        # 두 번째 카드도 즉시 공개
        st.session_state.revealed[index] = True

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

# 미리보기 시간 확인 (5초)
is_preview = False
if st.session_state.preview_time is not None:
    elapsed = time.time() - st.session_state.preview_time
    if elapsed < 5:
        is_preview = True
        remaining = 5 - int(elapsed)
        st.warning(f"⏱️ 카드를 기억하세요! {remaining + 1}초 남음...")
        time.sleep(0.1)
        st.rerun()
    else:
        # 미리보기 종료
        st.session_state.preview_time = None
        st.rerun()

# 게임 정보
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("이동 횟수", st.session_state.moves)
with col2:
    st.metric("찾은 짝", f"{st.session_state.matches_found}/8")
with col3:
    if st.button("🔄 새 게임"):
        reset_game()
        st.rerun()

st.markdown("---")

# 두 카드가 선택되었을 때 매칭 확인
if st.session_state.checking:
    # 두 카드를 먼저 보여주기 위해 화면 갱신
    first_idx = st.session_state.first_card
    second_idx = st.session_state.second_card
    
    # 두 카드 모두 공개 상태로 표시
    st.session_state.revealed[first_idx] = True
    st.session_state.revealed[second_idx] = True
    
    # 매칭 확인
    if st.session_state.cards[first_idx] == st.session_state.cards[second_idx]:
        st.session_state.matched[first_idx] = True
        st.session_state.matched[second_idx] = True
        st.session_state.matches_found += 1
        st.session_state.first_card = None
        st.session_state.second_card = None
        st.session_state.checking = False
    else:
        # 1초간 보여주고 다시 뒤집기
        time.sleep(1)
        st.session_state.revealed[first_idx] = False
        st.session_state.revealed[second_idx] = False
        st.session_state.first_card = None
        st.session_state.second_card = None
        st.session_state.checking = False
    st.rerun()

# 게임 클리어
if st.session_state.matches_found == 8:
    st.balloons()
    st.success(f"🎉 축하합니다! {st.session_state.moves}번 만에 모든 짝을 찾았습니다!")
    if st.button("다시 플레이"):
        reset_game()
        st.rerun()
