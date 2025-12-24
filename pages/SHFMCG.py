import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="카드 메모리 게임", page_icon="🎴", layout="centered")

# 이모지 카드 세트
CARD_EMOJIS = ["🐶", "🐱", "🦐", "🐬", "🐰", "🦊", "🐻", "🐼", "🐸", "🐙", "🦁", "🐯", "🦄", "🐢", "🦉"]
BOMB_EMOJI = "💣"
LIGHT_EMOJI = "✨"
LOCK_EMOJI = "🔒"
BALL_EMOJI = "💃"

def get_level_config(level):
    """레벨별 설정 반환"""
    configs = {
        1: {'grid_rows': 2, 'grid_cols': 2, 'pairs': 2, 'max_failures': 4, 'bombs': 0,
            'has_light': False, 'has_lock': False, 'has_ball': False},
        2: {'grid_rows': 3, 'grid_cols': 3, 'pairs': 4, 'max_failures': 5, 'bombs': 1,
            'has_light': True, 'has_lock': False, 'has_ball': False},
        3: {'grid_rows': 4, 'grid_cols': 4, 'pairs': 7, 'max_failures': 8, 'bombs': 2,
            'has_light': True, 'has_lock': True, 'has_ball': False},
        4: {'grid_rows': 4, 'grid_cols': 4, 'pairs': 7, 'max_failures': 7, 'bombs': 2,
            'has_light': True, 'has_lock': False, 'has_ball': True},
        5: {'grid_rows': 5, 'grid_cols': 5, 'pairs': 11, 'max_failures': 8, 'bombs': 3,
            'has_light': True, 'has_lock': True, 'has_ball': True},
    }
    return configs.get(level)

# 세션 상태 초기화
for key in ['level', 'game_started', 'cards', 'revealed', 'matched', 'first_card', 'second_card', 
            'failures', 'matches_found', 'is_previewing', 'show_cards_until', 'bomb_indices',
            'light_indices', 'lock_indices', 'ball_indices', 'edge_indices',
            'bombs_revealed', 'lock_opened', 'auto_reveal_bombs', 'ball_positions', 'preview_start_time',
            'bomb_hit', 'shown_tutorials']:
    if key not in st.session_state:
        if key == 'level':
            st.session_state[key] = 1
        elif key in ['game_started', 'is_previewing', 'bombs_revealed', 'lock_opened', 'auto_reveal_bombs', 'bomb_hit']:
            st.session_state[key] = False
        elif key in ['first_card', 'second_card', 'show_cards_until', 'preview_start_time']:
            st.session_state[key] = None
        elif key in ['failures', 'matches_found']:
            st.session_state[key] = 0
        elif key == 'shown_tutorials':
            st.session_state[key] = set()
        else:
            st.session_state[key] = []

def get_edge_indices(rows, cols):
    """가장자리 인덱스 반환 (시계방향 순서)"""
    edges = []
    # 상단 (왼쪽에서 오른쪽)
    for c in range(cols):
        edges.append(c)
    # 오른쪽 (위에서 아래, 모서리 제외)
    for r in range(1, rows):
        edges.append(r * cols + (cols - 1))
    # 하단 (오른쪽에서 왼쪽, 모서리 제외)
    if rows > 1:
        for c in range(cols - 2, -1, -1):
            edges.append((rows - 1) * cols + c)
    # 왼쪽 (아래에서 위, 모서리 제외)
    if cols > 1:
        for r in range(rows - 2, 0, -1):
            edges.append(r * cols)
    return edges

def move_ball_clockwise(ball_idx, rows, cols):
    """무도회 카드를 시계방향으로 1칸 이동"""
    edges = get_edge_indices(rows, cols)
    if ball_idx not in edges:
        return ball_idx
    current_pos = edges.index(ball_idx)
    next_pos = (current_pos + 1) % len(edges)
    return edges[next_pos]

def start_game():
    """게임 시작 및 초기화"""
    config = get_level_config(st.session_state.level)
    rows, cols = config['grid_rows'], config['grid_cols']
    
    # 특수 카드 개수 계산
    special_count = sum([config['has_light'], config['has_lock'], config['has_ball']])
    actual_pairs = config['pairs'] - special_count
    
    # 카드 생성
    card_list = CARD_EMOJIS[:actual_pairs] * 2
    if config['has_light']:
        card_list.extend([LIGHT_EMOJI, LIGHT_EMOJI])
    if config['has_lock']:
        card_list.extend([LOCK_EMOJI, LOCK_EMOJI])
    if config['has_ball']:
        card_list.extend([BALL_EMOJI, BALL_EMOJI])
    
    # 폭탄 추가
    for _ in range(config['bombs']):
        card_list.append(BOMB_EMOJI)
    
    # 카드 섞기 (특수 배치 조건 확인)
    edge_indices = get_edge_indices(rows, cols)
    max_attempts = 500
    
    for _ in range(max_attempts):
        random.shuffle(card_list)
        
        # 자물쇠는 가장자리에 없어야 함
        lock_indices = [i for i, c in enumerate(card_list) if c == LOCK_EMOJI]
        if config['has_lock'] and any(i in edge_indices for i in lock_indices):
            continue
        
        # 무도회는 가장자리에만 있어야 함
        ball_indices = [i for i, c in enumerate(card_list) if c == BALL_EMOJI]
        if config['has_ball'] and not all(i in edge_indices for i in ball_indices):
            continue
        
        break
    
    # 상태 초기화
    st.session_state.cards = card_list
    st.session_state.revealed = [False] * len(card_list)
    st.session_state.matched = [False] * len(card_list)
    st.session_state.bomb_indices = [i for i, c in enumerate(card_list) if c == BOMB_EMOJI]
    st.session_state.light_indices = [i for i, c in enumerate(card_list) if c == LIGHT_EMOJI]
    st.session_state.lock_indices = [i for i, c in enumerate(card_list) if c == LOCK_EMOJI]
    st.session_state.ball_indices = [i for i, c in enumerate(card_list) if c == BALL_EMOJI]
    st.session_state.edge_indices = edge_indices
    st.session_state.ball_positions = {i: i for i in st.session_state.ball_indices}
    st.session_state.first_card = None
    st.session_state.second_card = None
    st.session_state.failures = 0
    st.session_state.matches_found = 0
    st.session_state.game_started = True
    st.session_state.is_previewing = True
    st.session_state.show_cards_until = None
    st.session_state.bombs_revealed = False
    st.session_state.lock_opened = False
    st.session_state.auto_reveal_bombs = False
    st.session_state.preview_start_time = time.time()
    st.session_state.bomb_hit = False

def reset_to_level_1():
    """레벨 1로 리셋"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.level = 1

def next_level():
    """다음 레벨로 진행"""
    st.session_state.level += 1
    st.session_state.game_started = False

def stop_preview():
    """미리보기 종료"""
    st.session_state.is_previewing = False
    st.session_state.preview_start_time = None

def card_clicked(index):
    """카드 클릭 처리"""
    config = get_level_config(st.session_state.level)
    
    if st.session_state.matched[index] or st.session_state.first_card == index:
        return
    if st.session_state.bombs_revealed and index in st.session_state.bomb_indices:
        return
    
    # 자물쇠 잠금
    if (len(st.session_state.lock_indices) > 0 and not st.session_state.lock_opened and
        index in st.session_state.edge_indices and index not in st.session_state.lock_indices):
        return
    
    # 첫 번째 카드
    if st.session_state.first_card is None:
        # 폭탄 체크 - 즉시 게임 오버
        if index in st.session_state.bomb_indices:
            st.session_state.first_card = index
            st.session_state.revealed[index] = True
            st.session_state.failures = config['max_failures']  # 즉시 게임 오버
            st.session_state.bomb_hit = True  # 폭탄 터짐 플래그
            st.session_state.show_cards_until = time.time() + 1
            return
        
        # 일반 첫 번째 선택
        st.session_state.first_card = index
        st.session_state.revealed[index] = True
    # 두 번째 카드
    elif st.session_state.second_card is None:
        # 폭탄 체크 - 즉시 게임 오버
        if index in st.session_state.bomb_indices:
            st.session_state.second_card = index
            st.session_state.revealed[index] = True
            st.session_state.failures = config['max_failures']  # 즉시 게임 오버
            st.session_state.bomb_hit = True  # 폭탄 터짐 플래그
            st.session_state.show_cards_until = time.time() + 1
            return
        
        st.session_state.second_card = index
        st.session_state.revealed[index] = True
        st.session_state.show_cards_until = time.time() + 1

# 제목
st.title("🎴 카드 메모리 게임")
st.markdown(f"### 🎯 레벨 {st.session_state.level}")

config = get_level_config(st.session_state.level)

if config is None:
    st.balloons()
    st.success("🎊🎉 축하합니다! 모든 레벨을 클리어했습니다! 🎉🎊")
    st.markdown("### 🏆 게임 완전 클리어! 🏆")
    st.markdown("당신은 진정한 카드 메모리 마스터입니다!")
    if st.button("🔄 처음부터 다시 시작", use_container_width=True):
        reset_to_level_1()
        st.rerun()
    st.stop()

# 게임 시작 전
if not st.session_state.game_started:
    col1, col2 = st.columns(2)
    with col1:
        info = f"**레벨 {st.session_state.level} 정보**\n\n"
        info += f"- 카드: {config['grid_rows']}x{config['grid_cols']}\n- 찾을 짝: {config['pairs']}개\n- 실패 제한: {config['max_failures']}번\n"
        if config['bombs'] > 0:
            info += f"- 폭탄: {config['bombs']}개\n"
        for name, has, emoji in [('빛', 'has_light', '✨'), ('자물쇠', 'has_lock', '🔒'), ('무도회', 'has_ball', '💃')]:
            if config[has]:
                info += f"- {name} 카드: 1쌍\n"
        st.info(info)
    with col2:
        if st.session_state.level == 2 and config['bombs'] > 0:
            st.warning("⚠️ **폭탄 카드를 건드리면 즉시 게임 오버입니다!**")
        if st.session_state.level == 2 and config['has_light']:
            st.success("✨ **빛 카드 쌍을 맞추면 다른 카드 1쌍이 자동으로 맞춰집니다!**")
        if st.session_state.level == 3 and config['has_lock']:
            st.warning("🔒 **자물쇠 카드를 열기 전까지 가장자리 카드를 선택할 수 없습니다!**")
        if st.session_state.level == 4 and config['has_ball']:
            st.info("💃 **무도회 카드는 매 시도마다 시계방향으로 이동합니다!**")
    
    st.markdown("---")
    st.info("🎮 게임을 시작하면 5초 동안 모든 카드를 볼 수 있습니다!")
    if st.button("🚀 게임 시작", use_container_width=True, type="primary"):
        start_game()
        st.rerun()
    st.stop()

# 미리보기
is_preview = st.session_state.is_previewing
if is_preview:
    elapsed = time.time() - st.session_state.preview_start_time
    remaining = max(0, 5 - int(elapsed))
    
    if remaining > 0:
        st.warning(f"⏱️ 카드 위치를 기억하세요! {remaining}초 남음...")
        if st.button("✅ 맞을 준비가 되었습니다!", use_container_width=True, type="primary"):
            stop_preview()
            st.rerun()
    else:
        # 5초 경과 시 자동으로 시작
        stop_preview()
        st.rerun()

# 두 카드 비교
is_showing_cards = False
if st.session_state.show_cards_until:
    if time.time() < st.session_state.show_cards_until:
        is_showing_cards = True
    else:
        first_idx = st.session_state.first_card
        second_idx = st.session_state.second_card
        
        if first_idx in st.session_state.bomb_indices or second_idx in st.session_state.bomb_indices:
            # 폭탄을 선택한 경우 두 카드 모두 다시 숨김
            st.session_state.revealed[first_idx] = False
            if second_idx is not None:
                st.session_state.revealed[second_idx] = False
        elif second_idx is not None:
            match_success = False
            if st.session_state.cards[first_idx] == st.session_state.cards[second_idx]:
                st.session_state.matched[first_idx] = True
                st.session_state.matched[second_idx] = True
                st.session_state.matches_found += 1
                match_success = True
                
                if first_idx in st.session_state.lock_indices:
                    st.session_state.lock_opened = True
                
                # 빛 카드 효과
                if first_idx in st.session_state.light_indices:
                    unmatched = {}
                    for i, c in enumerate(st.session_state.cards):
                        if (not st.session_state.matched[i] and i not in st.session_state.bomb_indices and
                            i not in st.session_state.light_indices and
                            i not in st.session_state.lock_indices and
                            i not in st.session_state.ball_indices):
                            unmatched.setdefault(c, []).append(i)
                    for indices in unmatched.values():
                        if len(indices) >= 2:
                            st.session_state.matched[indices[0]] = True
                            st.session_state.matched[indices[1]] = True
                            st.session_state.matches_found += 1
                            break
            else:
                st.session_state.failures += 1
                st.session_state.revealed[first_idx] = False
                st.session_state.revealed[second_idx] = False
        
        # 무도회 카드 이동 (매칭 결과와 무관하게)
        if config['has_ball']:
            for original_ball_idx in list(st.session_state.ball_indices):
                current_pos = st.session_state.ball_positions[original_ball_idx]
                new_pos = move_ball_clockwise(current_pos, config['grid_rows'], config['grid_cols'])
                
                if current_pos != new_pos:
                    # 두 위치의 카드 교환
                    st.session_state.cards[current_pos], st.session_state.cards[new_pos] = st.session_state.cards[new_pos], st.session_state.cards[current_pos]
                    st.session_state.revealed[current_pos], st.session_state.revealed[new_pos] = st.session_state.revealed[new_pos], st.session_state.revealed[current_pos]
                    st.session_state.matched[current_pos], st.session_state.matched[new_pos] = st.session_state.matched[new_pos], st.session_state.matched[current_pos]
                    
                    # 특수 카드 인덱스 업데이트
                    if current_pos in st.session_state.bomb_indices:
                        st.session_state.bomb_indices.remove(current_pos)
                        st.session_state.bomb_indices.append(new_pos)
                    elif new_pos in st.session_state.bomb_indices:
                        st.session_state.bomb_indices.remove(new_pos)
                        st.session_state.bomb_indices.append(current_pos)
                    
                    if current_pos in st.session_state.light_indices:
                        st.session_state.light_indices.remove(current_pos)
                        st.session_state.light_indices.append(new_pos)
                    elif new_pos in st.session_state.light_indices:
                        st.session_state.light_indices.remove(new_pos)
                        st.session_state.light_indices.append(current_pos)
                    
                    if current_pos in st.session_state.lock_indices:
                        st.session_state.lock_indices.remove(current_pos)
                        st.session_state.lock_indices.append(new_pos)
                    elif new_pos in st.session_state.lock_indices:
                        st.session_state.lock_indices.remove(new_pos)
                        st.session_state.lock_indices.append(current_pos)
                    
                    st.session_state.ball_positions[original_ball_idx] = new_pos
        
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

# 특수 카드 튜토리얼 메시지 (게임 중 계속 표시)
if st.session_state.game_started:
    # 폭탄 카드 튜토리얼 (레벨 2에서 처음 등장)
    if st.session_state.level == 2 and config['bombs'] > 0:
        st.warning("💣 **폭탄을 건드리면 바로 패배합니다. 조심하세요!**")
    
    # 빛 카드 튜토리얼 (레벨 2에서 처음 등장)
    if st.session_state.level == 2 and config['has_light']:
        st.success("✨ **빛 카드의 쌍을 맞추면 다른 카드 쌍 하나를 찾아줍니다!**")
    
    # 자물쇠 카드 튜토리얼 (레벨 3에서 처음 등장)
    if st.session_state.level == 3 and config['has_lock']:
        if st.session_state.lock_opened:
            st.success("🔓 **자물쇠가 열렸습니다! 이제 가장자리 카드를 선택할 수 있습니다!**")
        else:
            st.warning("🔒 **자물쇠 카드를 열기 전까지 가장자리 카드를 선택할 수 없습니다!**")
    
    # 무도회 카드 튜토리얼 (레벨 4에서 처음 등장)
    if st.session_state.level == 4 and config['has_ball']:
        st.info("💃 **무도회 카드는 매 턴 가장자리를 따라 시계 방향으로 움직입니다!**")

# 게임 오버
if st.session_state.failures >= config['max_failures']:
    if st.session_state.bomb_hit:
        st.error("💀 게임 오버! 폭탄을 건드렸습니다!")
    else:
        st.error(f"💀 게임 오버! 실패 횟수가 {config['max_failures']}번을 초과했습니다!")
    st.info("레벨 1부터 다시 시작합니다.")
    if st.button("🎮 레벨 1부터 다시 시작", type="primary", use_container_width=True):
        reset_to_level_1()
        st.rerun()
    st.stop()

# 카드 그리드
for row in range(config['grid_rows']):
    cols = st.columns(config['grid_cols'])
    for col in range(config['grid_cols']):
        idx = row * config['grid_cols'] + col
        if idx >= len(st.session_state.cards):
            continue
        
        with cols[col]:
            should_show = is_preview or st.session_state.matched[idx] or st.session_state.revealed[idx]
            
            if should_show:
                color_map = {
                    BOMB_EMOJI: "#FF6B6B", LIGHT_EMOJI: "#FFFFE0",
                    LOCK_EMOJI: "#D3D3D3", BALL_EMOJI: "#FFB6C6"
                }
                bg = "#90EE90" if st.session_state.matched[idx] else color_map.get(st.session_state.cards[idx], "#FFD700")
                if idx in st.session_state.bomb_indices and (is_preview or st.session_state.bombs_revealed):
                    bg = "#FF6B6B"
                
                st.markdown(f"<div style='background-color: {bg}; padding: 30px; text-align: center; "
                           f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                           f"display: flex; align-items: center; justify-content: center;'>"
                           f"{st.session_state.cards[idx]}</div>", unsafe_allow_html=True)
                if st.session_state.matched[idx]:
                    st.button("", key=f"card_{idx}", disabled=True)
            else:
                if st.session_state.bombs_revealed and idx in st.session_state.bomb_indices:
                    st.markdown(f"<div style='background-color: #FF6B6B; padding: 30px; text-align: center; "
                               f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                               f"display: flex; align-items: center; justify-content: center; opacity: 0.7;'>💣</div>",
                               unsafe_allow_html=True)
                    st.button("", key=f"card_{idx}", disabled=True)
                else:
                    is_locked = (len(st.session_state.lock_indices) > 0 and not st.session_state.lock_opened and
                                idx in st.session_state.edge_indices and idx not in st.session_state.lock_indices)
                    disabled = is_preview or is_showing_cards or st.session_state.second_card is not None or is_locked
                    
                    if is_locked:
                        st.markdown(f"<div style='background-color: #E0E0E0; padding: 30px; text-align: center; "
                                   f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                                   f"display: flex; align-items: center; justify-content: center; opacity: 0.5;'>❓</div>",
                                   unsafe_allow_html=True)
                        st.button("", key=f"card_{idx}", disabled=True)
                    else:
                        st.markdown(f"<div style='background-color: #F5F5F5; padding: 30px; text-align: center; "
                                   f"border-radius: 10px; font-size: 40px; margin: 5px; height: 80px; "
                                   f"display: flex; align-items: center; justify-content: center; border: 2px solid #CCC;'>❓</div>",
                                   unsafe_allow_html=True)
                        button_text = "카드 선택" if st.session_state.level <= 3 else ""
                        if st.button(button_text, key=f"card_{idx}", use_container_width=True, disabled=disabled):
                            card_clicked(idx)
                            st.rerun()

if is_preview or is_showing_cards:
    time.sleep(0.1)
    st.rerun()

# 게임 클리어
if st.session_state.matches_found >= config['pairs'] and st.session_state.failures < config['max_failures']:
    if not st.session_state.bombs_revealed and len(st.session_state.bomb_indices) > 0:
        st.session_state.bombs_revealed = True
        st.session_state.auto_reveal_bombs = True
        st.rerun()
    
    st.balloons()
    st.success(f"🎉 레벨 {st.session_state.level} 클리어! 실패 {st.session_state.failures}번으로 모든 짝을 찾았습니다!")
    
    if st.session_state.level < 5:
        if st.button("➡️ 다음 레벨로", type="primary", use_container_width=True):
            next_level()
            st.rerun()
    else:
        st.markdown("### 🏆 모든 레벨을 완료했습니다! 🏆")
        if st.button("🔄 처음부터 다시 시작", use_container_width=True):
            reset_to_level_1()
            st.rerun()
