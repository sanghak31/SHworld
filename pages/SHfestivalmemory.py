import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="메모리 카드 게임", page_icon="🎴", layout="centered")

# 이모지 카드 세트
CARD_EMOJIS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐸", "🐵", "🦁", "🐯"]
BOMB_EMOJI = "💣"

def get_level_config(level):
    """레벨별 설정 반환"""
    if level == 1:
        return {
            'grid_rows': 4,
            'grid_cols': 4,
            'pairs': 8,
            'max_failures': 10,
            'has_bomb': False
        }
    elif level == 2:
        return {
            'grid_rows': 4,
            'grid_cols': 4,
            'pairs': 8,
            'max_failures': 8,
            'has_bomb': False
        }
    elif level == 3:
        return {
            'grid_rows': 3,
            'grid_cols': 5,
            'pairs': 7,
            'max_failures': 7,
            'has_bomb': True
        }
    elif level == 4:
        return {
            'grid_rows': 4,
            'grid_cols': 5,
            'pairs': 10,
            'max_failures': 12,
            'has_bomb': False
        }
    elif level == 5:
        return {
            'grid_rows': 3,
            'grid_cols': 7,
            'pairs': 10,
            'max_failures': 10,
            'has_bomb': True
        }
    else:  # level >= 6
        max_failures = max(1, 15 - (level - 6) * 2)
        return {
            'grid_rows': 5,
            'grid_cols': 5,
            'pairs': 12,
            'max_failures': max_failures,
            'has_bomb': True
        }

# 세션 상태 초기화
if 'level' not in st.session_state:
    st.session_state.level = 1

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

if 'is_previewing' not in st.session_state:
    st.session_state.is_previewing = False

if 'show_cards_until' not in st.session_state:
    st.session_state.show_cards_until = None

if 'bomb_indices' not in st.session_state:
    st.session_state.bomb_indices = []

def start_game():
    """게임 시작 및 초기화"""
    config = get_level_config(st.session_state.level)
    grid_rows = config['grid_rows']
    grid_cols = config['grid_cols']
    pairs = config['pairs']
    has_bomb = config['has_bomb']
    
    # 카드 생성
    card_list = CARD_EMOJIS[:pairs] * 2
    
    # 폭탄 카드 추가
    if has_bomb:
        card_list.append(BOMB_EMOJI)
    
    random.shuffle(card_list)
    
    # 폭탄 위치 저장
    bomb_indices = []
    if has_bomb:
        bomb_indices = [i for i, card in enumerate(card_list) if card == BOMB_EMOJI]
    
    total_cards = grid_rows * grid_cols
    st.session_state.cards = card_list
    st.session_state.revealed = [False] * total_cards
    st.session_state.matched = [False] * total_cards
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.failures = 0
    st.session_state.matches_found = 0
    st.session_state.game_started = True
    st.session_state.is_previewing = True
    st.session_state.show_cards_until = None
    st.session_state.bomb_indices = bomb_indices

def stop_preview():
    """미리보기 종료"""
    st.session_state.is_previewing = False

def reset_to_level_1():
    """레벨 1로 리셋"""
    st.session_state.level = 1
    st.session_state.game_started = False
    st.session_state.cards = []
    st.session_state.revealed = []
    st.session_state.matched = []
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.failures = 0
    st.session_state.matches_found = 0
    st.session_state.is_previewing = False
    st.session_state.show_cards_until = None
    st.session_state.bomb_indices = []

def next_level():
    """다음 레벨로 진행"""
    st.session_state.level += 1
    st.session_state.game_started = False
    st.session_state.cards = []
    st.session_state.revealed = []
    st.session_state.matched = []
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.failures = 0
    st.session_state.matches_found = 0
    st.session_state.is_previewing = False
    st.session_state.show_cards_until = None
    st.session_state.bomb_indices = []

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
        
        # 폭탄 카드 체크
        if index in st.session_state.bomb_indices:
            st.session_state.failures += 1
            st.session_state.show_cards_until = time.time() + 1  # 1초간 보여주기
    # 두 번째 카드 선택
    elif st.session_state.second_card is None:
        st.session_state.second_card = index
        st.session_state.revealed[index] = True
        st.session_state.show_cards_until = time.time() + 1  # 1초간 보여주기

# 제목
st.title("🎴 메모리 카드 게임")

# 레벨 정보
config = get_level_config(st.session_state.level)
st.markdown(f"### 🎯 레벨 {st.session_state.level}")

# 게임 시작 전
if not st.session_state.game_started:
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**레벨 {st.session_state.level} 정보**\n\n"
                f"- 카드 크기: {config['grid_rows']}x{config['grid_cols']}\n"
                f"- 찾을 짝: {config['pairs']}개\n"
                f"- 실패 제한: {config['max_failures']}번")
    with col2:
        if config['has_bomb']:
            st.warning("⚠️ **폭탄 카드는 건드릴시 바로 실패합니다.**")
        else:
            st.success("✅ 이 레벨은 폭탄이 없습니다!")
    
    st.markdown("---")
    st.info("🎮 게임을 시작하면 모든 카드를 볼 수 있습니다!")
    
    if st.button("🚀 게임 시작", use_container_width=True, type="primary"):
        start_game()
        st.rerun()
    st.stop()

# 미리보기 중인지 확인
is_preview = st.session_state.is_previewing

# 미리보기 중이면 준비 완료 버튼 표시
if is_preview:
    st.warning("⏱️ 카드 위치를 기억하세요!")
    if st.button("✅ 맞출 준비가 되었습니다!", use_container_width=True, type="primary"):
        stop_preview()
        st.rerun()

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
        
        # 첫 번째 카드가 폭탄인 경우
        if first_idx in st.session_state.bomb_indices:
            st.session_state.revealed[first_idx] = False
            st.session_state.first_card = None
            st.session_state.second_card = None
            st.session_state.show_cards_until = None
            st.rerun()
        # 두 번째 카드 선택이 있는 경우
        elif second_idx is not None:
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
    st.metric("실패 횟수", f"{st.session_state.failures}/{config['max_failures']}")
with col2:
    st.metric("찾은 짝", f"{st.session_state.matches_found}/{config['pairs']}")
with col3:
    if st.button("🔄 레벨 1로"):
        reset_to_level_1()
        st.rerun()

st.markdown("---")

# 게임 정보 표시
if config['has_bomb']:
    st.warning("⚠️ **폭탄 카드는 건드릴시 바로 실패합니다.**")

# 게임 실패 체크
if st.session_state.failures >= config['max_failures']:
    st.error(f"💀 게임 오버! 실패 횟수가 {config['max_failures']}번을 초과했습니다!")
    st.info(f"레벨 1부터 다시 시작합니다.")
    if st.button("🎮 레벨 1부터 다시 시작", type="primary", use_container_width=True):
        reset_to_level_1()
        st.rerun()
    st.stop()

# 카드 그리드
grid_rows = config['grid_rows']
grid_cols = config['grid_cols']
for row in range(grid_rows):
    cols = st.columns(grid_cols)
    for col in range(grid_cols):
        index = row * grid_cols + col
        
        # 인덱스가 카드 범위를 벗어나면 건너뛰기
        if index >= len(st.session_state.cards):
            continue
            
        with cols[col]:
            # 카드를 보여줘야 하는 경우들
            should_show = (
                is_preview or  # 미리보기 중
                st.session_state.matched[index] or  # 매칭된 카드
                st.session_state.revealed[index]  # 현재 공개된 카드
            )
            
            if should_show:
                # 매칭된 카드는 초록색, 폭탄은 빨간색, 나머지는 노란색
                if st.session_state.matched[index]:
                    bg_color = "#90EE90"
                elif index in st.session_state.bomb_indices:
                    bg_color = "#FF6B6B"
                else:
                    bg_color = "#FFD700"
                    
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
if is_showing_cards:
    time.sleep(0.1)
    st.rerun()

# 게임 클리어
if st.session_state.matches_found == config['pairs'] and st.session_state.failures < config['max_failures']:
    st.balloons()
    st.success(f"🎉 레벨 {st.session_state.level} 클리어! 실패 {st.session_state.failures}번으로 모든 짝을 찾았습니다!")
    if st.button("➡️ 다음 레벨로", type="primary", use_container_width=True):
        next_level()
        st.rerun()
