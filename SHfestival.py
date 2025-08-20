₩import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_game_board():
    """직사각형 게임 보드와 중앙 분할선을 생성합니다."""
    
    # 보드 크기 설정
    board_width = 10
    board_height = 6
    
    # matplotlib figure 생성
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # 직사각형 보드 그리기
    board_rect = patches.Rectangle(
        (0, 0), board_width, board_height,
        linewidth=3, edgecolor='black', facecolor='lightgreen', alpha=0.7
    )
    ax.add_patch(board_rect)
    
    # 중앙을 나누는 세로선 그리기
    center_x = board_width / 2
    ax.plot([center_x, center_x], [0, board_height], 
            color='red', linewidth=2, linestyle='--')
    
    # 축 설정
    ax.set_xlim(-1, board_width + 1)
    ax.set_ylim(-1, board_height + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('게임 보드', fontsize=16, fontweight='bold')
    ax.set_xlabel('가로')
    ax.set_ylabel('세로')
    
    return fig

def main():
    st.title("🎮 스트림릿 게임 보드")
    st.write("직사각형 보드와 중앙 분할선이 있는 게임판입니다.")
    
    # 보드 옵션 설정
    st.sidebar.header("보드 설정")
    
    # 보드 크기 조절 옵션
    board_width = st.sidebar.slider("보드 가로 크기", 6, 20, 10)
    board_height = st.sidebar.slider("보드 세로 크기", 4, 15, 6)
    
    # 분할선 방향 선택
    division_type = st.sidebar.selectbox(
        "분할선 방향",
        ["세로 (왼쪽/오른쪽)", "가로 (위/아래)", "대각선", "십자형"]
    )
    
    # 색상 설정
    board_color = st.sidebar.color_picker("보드 색상", "#90EE90")
    line_color = st.sidebar.color_picker("분할선 색상", "#FF0000")
    
    # 게임 보드 생성 및 표시
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # 직사각형 보드 그리기
    board_rect = patches.Rectangle(
        (0, 0), board_width, board_height,
        linewidth=3, edgecolor='black', facecolor=board_color, alpha=0.7
    )
    ax.add_patch(board_rect)
    
    # 선택된 분할선 타입에 따라 선 그리기
    if division_type == "세로 (왼쪽/오른쪽)":
        center_x = board_width / 2
        ax.plot([center_x, center_x], [0, board_height], 
                color=line_color, linewidth=3, linestyle='-')
        
    elif division_type == "가로 (위/아래)":
        center_y = board_height / 2
        ax.plot([0, board_width], [center_y, center_y], 
                color=line_color, linewidth=3, linestyle='-')
        
    elif division_type == "대각선":
        ax.plot([0, board_width], [0, board_height], 
                color=line_color, linewidth=3, linestyle='-')
        
    elif division_type == "십자형":
        center_x = board_width / 2
        center_y = board_height / 2
        # 세로선
        ax.plot([center_x, center_x], [0, board_height], 
                color=line_color, linewidth=3, linestyle='-')
        # 가로선
        ax.plot([0, board_width], [center_y, center_y], 
                color=line_color, linewidth=3, linestyle='-')
    
    # 축 설정
    ax.set_xlim(-0.5, board_width + 0.5)
    ax.set_ylim(-0.5, board_height + 0.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'게임 보드 ({board_width} x {board_height})', fontsize=16, fontweight='bold')
    ax.set_xlabel('가로')
    ax.set_ylabel('세로')
    
    # 스트림릿에 plot 표시
    st.pyplot(fig)
    
    # 보드 정보 표시
    st.info(f"""
    **보드 정보:**
    - 크기: {board_width} x {board_height}
    - 분할 방식: {division_type}
    - 총 면적: {board_width * board_height} 단위²
    """)
    
    # 게임 규칙 예시
    with st.expander("게임 아이디어 💡"):
        st.write("""
        이 보드로 만들 수 있는 게임들:
        
        1. **팀 대전 게임**: 두 팀이 각각 한쪽 영역을 담당
        2. **퍼즐 게임**: 각 영역에 다른 퍼즐 조각 배치
        3. **전략 게임**: 영역별로 다른 자원이나 특성 부여
        4. **미로 게임**: 중앙선을 장애물로 활용
        5. **카드 게임**: 각 영역이 다른 플레이어의 필드
        """)

if __name__ == "__main__":
    main()
