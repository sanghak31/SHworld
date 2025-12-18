import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="메모리 카드 게임", page_icon="🎴", layout="centered")

# 이모지 카드 세트
CARD_EMOJIS = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐸", "🐵", "🦁", "🐯"]
BOMB_EMOJI = "💣"
ICE_EMOJI = "❄️"
LIGHT_EMOJI = "✨"
WITCH_EMOJI = "🧙"
LOCK_EMOJI = "🔒"

def get_level_config(level):
    """레벨별 설정 반환"""
    if level == 1:
        return {
            'grid_rows': 2,
            'grid_cols': 2,
            'pairs': 2,
            'max_failures': 5,
            'bombs': 0,
            'has_ice': False,
            'has_light': False,
            'has_witch': False,
            'has_lock': False
        }
    elif level == 2:
        return {
            'grid_rows': 3,
            'grid_cols': 3,
            'pairs': 4,
            'max_failures': 8,
            'bombs': 1,
            'has_ice': False,
            'has_light': False,
            'has_witch': False,
            'has_lock': False
        }
    elif level == 3:
        return {
            'grid_rows': 4,
            'grid_cols': 4,
            'pairs': 7,
            'max_failures': 8,
            'bombs': 2,
            'has_ice': True,
            'has_light': False,
            'has_witch': False,
            'has_lock': False
        }
    elif level == 4:
        return {
            'grid_rows': 4,
            'grid_cols': 5,
            'pairs': 8,
            'max_failures': 8,
            'bombs': 4,
            'has_ice': True,
            'has_light': True,
            'has_witch': False,
            'has_lock': False
        }
    elif level == 5:
        return {
            'grid_rows': 3,
            'grid_cols': 7,
            'pairs': 9,
            'max_failures': 7,
            'bombs': 3,
            'has_ice': True,
            'has_light': True,
            'has_witch': True,
            'has_lock': False
        }
    elif level == 6:
        return {
            'grid_rows': 5,
            'grid_cols': 5,
            'pairs': 11,
            'max_failures': 8,
            'bombs': 3,
            'has_ice': False,
            'has_light': True,
            'has_witch': True,
            'has_lock': True
        }
    else:  # level >= 7
        max_failures = max(1, 8 - (level - 6) * 2)
        return {
            'grid_rows': 5,
            'grid_cols': 5,
            'pairs': 11,
            'max_failures': max_failures,
            'bombs': 3,
            'has_ice': False,
            'has_light': True,
            'has_witch': True,
            'has_lock': True
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

if 'ice_indices' not in st.session_state:
    st.session_state.ice_indices = []

if 'light_indices' not in st.session_state:
    st.session_state.light_indices = []

if 'lock_indices' not in st.session_state:
    st.session_state.lock_indices = []

if 'witch_indices' not in st.session_state:
    st.session_state.witch_indices = []

if 'bombs_revealed' not in st.session_state:
    st.session_state.bombs_revealed = False

if 'lock_opened' not in st.session_state:
    st.session_state.lock_opened = False

if 'witch_defeated' not in st.session_state:
    st.session_state.witch_defeated = False

if 'edge_indices' not in st.session_state:
    st.session_state.edge_indices = []

if 'auto_reveal_bombs' not in st.session_state:
    st.session_state.auto_reveal_bombs = False

def start_game():
    """게임 시작 및 초기화"""
    config = get_level_config(st.session_state.level)
    grid_rows = config['grid_rows']
    grid_cols = config['grid_cols']
    pairs = config['pairs']
    bombs = config['bombs']
    has_ice = config['has_ice']
    has_light = config['has_light']
    has_witch = config['has_witch']
    has_lock = config['has_lock']
    
    # 카드 생성
    card_list = []
    
    # 특수 카드 개수 계산
    special_pairs = 0
    if has_ice:
        special_pairs += 1
    if has_light:
        special_pairs += 1
    if has_witch:
        special_pairs += 1
    if has_lock:
        special_pairs += 1
    
    actual_pairs = pairs - special_pairs
    card_list = CARD_EMOJIS[:actual_pairs] * 2
    
    # 특수 카드 추가
    if has_ice:
        card_list.extend([ICE_EMOJI, ICE_EMOJI])
    if has_light:
        card_list.extend([LIGHT_EMOJI, LIGHT_EMOJI])
    if has_witch:
        card_list.extend([WITCH_EMOJI, WITCH_EMOJI])
    if has_lock:
        card_list.extend([LOCK_EMOJI, LOCK_EMOJI])
    
    # 폭탄 카드 추가
    for _ in range(bombs):
        card_list.append(BOMB_EMOJI)
    
    # 카드 섞기
    random.shuffle(card_list)
    
    # 자물쇠 카드가 가장자리에 있으면 다시 섞기
    if has_lock:
        max_attempts = 100
        for _ in range(max_attempts):
            lock_indices_temp = [i for i, card in enumerate(card_list) if card == LOCK_EMOJI]
            edge_indices_temp = []
            
            # 가장자리 인덱스 계산
            for i in range(len(card_list)):
                row = i // grid_cols
                col = i % grid_cols
                if row == 0 or row == grid_rows - 1 or col == 0 or col == grid_cols - 1:
                    edge_indices_temp.append(i)
            
            # 자물쇠가 가장자리에 있는지 확인
            lock_on_edge = any(idx in edge_indices_temp for idx in lock_indices_temp)
            if not lock_on_edge:
                break
            random.shuffle(card_list)
    
    # 특수 카드 위치 저장
    bomb_indices = [i for i, card in enumerate(card_list) if card == BOMB_EMOJI]
    ice_indices = [i for i, card in enumerate(card_list) if card == ICE_EMOJI]
    light_indices = [i for i, card in enumerate(card_list) if card == LIGHT_EMOJI]
    witch_indices = [i for i, card in enumerate(card_list) if card == WITCH_EMOJI]
    lock_indices = [i for i, card in enumerate(card_list) if card == LOCK_EMOJI]
    
    # 가장자리 인덱스 저장
    edge_indices = []
    for i in range(len(card_list)):
        row = i // grid_cols
        col = i % grid_cols
        if row == 0 or row == grid_rows - 1 or col == 0 or col == grid_cols - 1:
            edge_indices.append(i)
    
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
    st.session_state.ice_indices = ice_indices
    st.session_state.light_indices = light_indices
    st.session_state.witch_indices = witch_indices
    st.session_state.lock_indices = lock_indices
    st.session_state.edge_indices = edge_indices
    st.session_state.bombs_revealed = False
    st.session_state.lock_opened = False
    st.session_state.witch_defeated = False
    st.session_state.auto_reveal_bombs = False

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
    st.session_state.ice_indices = []
    st.session_state.light_indices = []
    st.session_state.witch_indices = []
    st.session_state.lock_indices = []
    st.session_state.edge_indices = []
    st.session_state.bombs_revealed = False
    st.session_state.lock_opened = False
    st.session_state.witch_defeated = False
    st.session_state.auto_reveal_bombs = False
    st.session_state.auto_reveal_bombs = False

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
    st.session_state.ice_indices = []
    st.session_state.light_indices = []
    st.session_state.witch_indices = []
    st.session_state.lock_indices = []
    st.session_state.edge_indices = []
    st.session_state.bombs_revealed = False
    st.session_state.lock_opened = False
    st.session_state.witch_defeated = False

def card_clicked(index):
    """카드 클릭 처리"""
    # 이미 매칭되었거나 선택된 카드면 무시
    if st.session_state.matched[index]:
        return
    if st.session_state.first_card == index:
        return
    
    # 폭탄이 공개된 상태면 폭탄 클릭 무시
    if st.session_state.bombs_revealed and index in st.session_state.bomb_indices:
        return
    
    # 자물쇠 카드가 있고, 열리지 않았고, 가장자리 카드면 클릭 무시 (단, 자물쇠 카드는 예외)
    if (len(st.session_state.lock_indices) > 0 and 
        not st.session_state.lock_opened and 
        index in st.session_state.edge_indices and
        index not in st.session_state.lock_indices):
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
        info_text = f"**레벨 {st.session_state.level} 정보**\n\n"
        info_text += f"- 카드 크기: {config['grid_rows']}x{config['grid_cols']}\n"
        info_text += f"- 찾을 짝: {config['pairs']}개\n"
        info_text += f"- 실패 제한: {config['max_failures']}번\n"
        if config['bombs'] > 0:
            info_text += f"- 폭탄: {config['bombs']}개\n"
        if config['has_ice']:
            info_text += f"- 얼음 카드: 1쌍\n"
        if config['has_light']:
            info_text += f"- 빛 카드: 1쌍\n"
        if config['has_witch']:
            info_text += f"- 마녀 카드: 1쌍\n"
        if config['has_lock']:
            info_text += f"- 자물쇠 카드: 1쌍"
        st.info(info_text)
    with col2:
        if st.session_state.level == 2 and config['bombs'] > 0:
            st.warning("⚠️ **폭탄 카드는 건드릴시 바로 실패합니다.**")
        if st.session_state.level == 3 and config['has_ice']:
            st.success("❄️ **얼음 카드 쌍을 맞추면 폭탄 위치가 공개됩니다!**")
        if st.session_state.level == 4 and config['has_light']:
            st.success("✨ **빛 카드 쌍을 맞추면 다른 카드 1쌍이 자동으로 맞춰집니다!**")
        if st.session_state.level == 5 and config['has_witch']:
            st.warning("🧙 **마녀 카드를 먼저 처치해야 특수 카드 효과가 발동됩니다!**")
        if st.session_state.level == 6 and config['has_lock']:
            st.warning("🔒 **자물쇠 카드를 열기 전까지 가장자리 카드를 선택할 수 없습니다!**")
    
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
                
                # 마녀 카드를 매칭한 경우
                if first_idx in st.session_state.witch_indices:
                    st.session_state.witch_defeated = True
                
                # 자물쇠 카드를 매칭한 경우
                if first_idx in st.session_state.lock_indices:
                    st.session_state.lock_opened = True
                
                # 마녀가 처치되었거나 마녀가 없는 경우에만 특수 효과 발동
                if st.session_state.witch_defeated or len(st.session_state.witch_indices) == 0:
                    # 얼음 카드를 매칭한 경우 폭탄 공개
                    if first_idx in st.session_state.ice_indices:
                        st.session_state.bombs_revealed = True
                        st.session_state.auto_reveal_bombs = False  # 수동 공개
                    
                    # 빛 카드를 매칭한 경우 다른 카드 1쌍 자동 매칭
                    if first_idx in st.session_state.light_indices:
                        # 아직 매칭되지 않은 일반 카드 찾기
                        unmatched_cards = {}
                        for i, card in enumerate(st.session_state.cards):
                            if (not st.session_state.matched[i] and 
                                i not in st.session_state.bomb_indices and
                                i not in st.session_state.ice_indices and
                                i not in st.session_state.light_indices and
                                i not in st.session_state.witch_indices and
                                i not in st.session_state.lock_indices):
                                if card not in unmatched_cards:
                                    unmatched_cards[card] = []
                                unmatched_cards[card].append(i)
                        
                        # 쌍이 있는 카드 자동 매칭
                        for card, indices in unmatched_cards.items():
                            if len(indices) >= 2:
                                st.session_state.matched[indices[0]] = True
                                st.session_state.matched[indices[1]] = True
                                st.session_state.matches_found += 1
                                break
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
status_messages = []

if config['has_witch']:
    if st.session_state.witch_defeated:
        status_messages.append(("success", "🧙 **마녀를 처치했습니다! 이제 특수 카드 효과가 발동됩니다!**"))
    else:
        status_messages.append(("warning", "🧙 **마녀 카드를 먼저 처치해야 특수 카드 효과가 발동됩니다!**"))

if config['has_lock']:
    if st.session_state.lock_opened:
        status_messages.append(("success", "🔓 **자물쇠가 열렸습니다! 이제 가장자리 카드를 선택할 수 있습니다!**"))
    else:
        status_messages.append(("warning", "🔒 **자물쇠 카드를 열기 전까지 가장자리 카드를 선택할 수 없습니다!**"))

if config['bombs'] > 0 and st.session_state.bombs_revealed and not st.session_state.auto_reveal_bombs:
    status_messages.append(("success", "❄️ **얼음 카드 효과 발동! 폭탄 위치가 공개되었습니다!**"))

for msg_type, msg in status_messages:
    if msg_type == "success":
        st.success(msg)
    elif msg_type == "info":
        st.info(msg)
    else:
        st.warning(msg)

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
                # 매칭된 카드는 초록색
                # 폭탄은 빨간색 (공개되었거나 미리보기 중일 때)
                # 얼음은 하늘색
                # 빛은 연한 노란색
                # 마녀는 보라색
                # 자물쇠는 회색
                # 나머지는 노란색
                if st.session_state.matched[index]:
                    bg_color = "#90EE90"
                elif index in st.session_state.bomb_indices and (is_preview or st.session_state.bombs_revealed):
                    bg_color = "#FF6B6B"
                elif index in st.session_state.ice_indices:
                    bg_color = "#87CEEB"
                elif index in st.session_state.light_indices:
                    bg_color = "#FFFFE0"
                elif index in st.session_state.witch_indices:
                    bg_color = "#9370DB"
                elif index in st.session_state.lock_indices:
                    bg_color = "#D3D3D3"
                else:
                    bg_color = "#FFD700"
                    
                st.markdown(
                    f"<div style='background-color: {bg_color}; padding: 30px; text-align: center; "
                    f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                    f"display: flex; align-items: center; justify-content: center;'>"
                    f"{st.session_state.cards[index]}</div>",
                    unsafe_allow_html=True
                )
                # 매칭된 카드 아래에 비활성화된 버튼 추가 (클릭해도 아무 일 없음)
                if st.session_state.matched[index]:
                    st.button("", key=f"card_{index}", use_container_width=True, disabled=True)
            else:
                # 폭탄이 공개된 경우 폭탄 위치에 경고 표시
                if st.session_state.bombs_revealed and index in st.session_state.bomb_indices:
                    st.markdown(
                        f"<div style='background-color: #FF6B6B; padding: 30px; text-align: center; "
                        f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                        f"display: flex; align-items: center; justify-content: center; opacity: 0.7;'>"
                        f"💣</div>",
                        unsafe_allow_html=True
                    )
                    # 폭탄 아래에 비활성화된 버튼 추가
                    st.button("", key=f"card_{index}", use_container_width=True, disabled=True)
                else:
                    # 뒤집힌 카드
                    # 자물쇠 카드가 있고, 열리지 않았고, 가장자리이며, 자물쇠 카드가 아닌 경우 비활성화
                    is_locked_edge = (len(st.session_state.lock_indices) > 0 and
                                     not st.session_state.lock_opened and 
                                     index in st.session_state.edge_indices and 
                                     index not in st.session_state.lock_indices)
                    
                    disabled = is_preview or is_showing_cards or st.session_state.second_card is not None or is_locked_edge
                    
                    # 잠긴 가장자리 카드는 회색으로 표시
                    if is_locked_edge:
                        st.markdown(
                            f"<div style='background-color: #E0E0E0; padding: 30px; text-align: center; "
                            f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                            f"display: flex; align-items: center; justify-content: center; opacity: 0.5;'>"
                            f"❓</div>",
                            unsafe_allow_html=True
                        )
                        st.button("", key=f"card_{index}", use_container_width=True, disabled=True)
                    else:
                        # 일반 뒤집힌 카드 - 무색 배경에 ? 이모지
                        st.markdown(
                            f"<div style='background-color: #F5F5F5; padding: 30px; text-align: center; "
                            f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                            f"display: flex; align-items: center; justify-content: center; "
                            f"border: 2px solid #CCCCCC;'>"
                            f"❓</div>",
                            unsafe_allow_html=True
                        )
                        if st.button("카드 선택", key=f"card_{index}", use_container_width=True, disabled=disabled):
                            card_clicked(index)
                            st.rerun()

# 미리보기나 카드 보여주기 중이면 자동 새로고침
if is_showing_cards:
    time.sleep(0.1)
    st.rerun()

# 게임 클리어
if st.session_state.matches_found == config['pairs'] and st.session_state.failures < config['max_failures']:
    # 모든 짝을 찾았으면 폭탄도 공개
    if not st.session_state.bombs_revealed and len(st.session_state.bomb_indices) > 0:
        st.session_state.bombs_revealed = True
        st.rerun()
    
    st.balloons()
    st.success(f"🎉 레벨 {st.session_state.level} 클리어! 실패 {st.session_state.failures}번으로 모든 짝을 찾았습니다!")
    if st.button("➡️ 다음 레벨로", type="primary", use_container_width=True):
        next_level()
        st.rerun()
