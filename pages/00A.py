import streamlit as st
import random

# 단어 목록 (6글자 단어)
WORDS = [
    "planet", "border", "submit", "wallet", "danger", "silent",
    "charge", "flight", "master", "castle", "rescue", "bucket",
    "animal", "beauty", "circle", "damage", "effort", "fabric",
    "galaxy", "hunger", "injury", "jungle", "kitten", "legend",
    "moment", "number", "object", "people", "quartz", "result",
    "singer", "ticket", "update", "valley", "window", "yellow",
    "zephyr", "chance", "decent", "famous", "garden", "horror",
    "island", "leader", "manual", "nation", "option", "prince",
    "random", "school", "temple", "unique", "vision", "winner"
]

# 초기 상태 설정
if 'answer' not in st.session_state:
    st.session_state.answer = random.choice(WORDS)
    st.session_state.guesses = []
    st.session_state.game_over = False

ANSWER = st.session_state.answer

st.title("🟩 6-Letter Wordle Game")
st.markdown("Guess the **6-letter English word**. You have 6 attempts. Only valid words are accepted.")

# 피드백 계산
def get_feedback(guess, answer):
    result = ['gray'] * 6
    answer_chars = list(answer)

    # 초록: 위치도 같고 글자도 같음
    for i in range(6):
        if guess[i] == answer[i]:
            result[i] = 'green'
            answer_chars[i] = None

    # 노랑: 글자는 있으나 위치는 다름
    for i in range(6):
        if result[i] == 'gray' and guess[i] in answer_chars:
            result[i] = 'yellow'
            answer_chars[answer_chars.index(guess[i])] = None

    return result

# 입력 폼 처리
if not st.session_state.game_over:
    with st.form("guess_form"):
        guess = st.text_input("Enter a valid 6-letter word:", max_chars=6).lower()
        submitted = st.form_submit_button("Submit")
        if submitted:
            guess = guess.strip()
            if len(guess) != 6 or not guess.isalpha():
                st.warning("Please enter exactly 6 English letters.")
            elif guess not in WORDS:
                st.warning("This word is not in the word list.")
            else:
                st.session_state.guesses.append((guess, get_feedback(guess, ANSWER)))
                if guess == ANSWER:
                    st.success("🎉 Correct! You guessed the word!")
                    st.session_state.game_over = True
                elif len(st.session_state.guesses) >= 6:
                    st.error(f"❌ Game Over! The word was **{ANSWER.upper()}**.")
                    st.session_state.game_over = True

# 시도 결과 표시
for idx, (guess, feedback) in enumerate(st.session_state.guesses):
    st.markdown(f"**Attempt {idx + 1}:**")
    cols = st.columns(6)
    for i in range(6):
        with cols[i]:
            st.markdown(
                f"<div style='background-color:{feedback[i]};"
                f"color:white;padding:8px;text-align:center;font-size:20px;border-radius:5px'>"
                f"{guess[i].upper()}</div>", unsafe_allow_html=True
            )

# 재시작 버튼
if st.session_state.game_over:
    if st.button("🔄 Restart Game"):
        st.session_state.answer = random.choice(WORDS)
        st.session_state.guesses = []
        st.session_state.game_over = False
