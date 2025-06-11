import streamlit as st
import random

# 6-letter English word list
WORDS = [
    "planet", "border", "submit", "wallet", "danger", "silent",
    "charge", "flight", "master", "castle", "rescue", "bucket"
]

# Initialize game state
if 'answer' not in st.session_state:
    st.session_state.answer = random.choice(WORDS)
    st.session_state.guesses = []
    st.session_state.game_over = False

ANSWER = st.session_state.answer

st.title("🟩 6-Letter Wordle Game")
st.markdown("Guess the **6-letter English word**. You have 6 attempts.")

# Feedback function
def get_feedback(guess, answer):
    result = ['gray'] * 6
    answer_chars = list(answer)

    # Green: correct letter and position
    for i in range(6):
        if guess[i] == answer[i]:
            result[i] = 'green'
            answer_chars[i] = None  # prevent duplicate matching

    # Yellow: letter exists but in wrong position
    for i in range(6):
        if result[i] == 'gray' and guess[i] in answer_chars:
            result[i] = 'yellow'
            answer_chars[answer_chars.index(guess[i])] = None

    return result

# Guess input
if not st.session_state.game_over:
    with st.form("guess_form"):
        guess = st.text_input("Enter a 6-letter word:", max_chars=6).lower()
        submitted = st.form_submit_button("Submit")
        if submitted:
            guess = guess.strip()
            if len(guess) != 6 or not guess.isalpha():
                st.warning("Please enter exactly 6 English letters.")
            else:
                st.session_state.guesses.append((guess, get_feedback(guess, ANSWER)))
                if guess == ANSWER:
                    st.success("🎉 Correct! You guessed the word!")
                    st.session_state.game_over = True
                elif len(st.session_state.guesses) >= 6:
                    st.error(f"❌ Game Over! The word was **{ANSWER.upper()}**.")
                    st.session_state.game_over = True

# Display guesses
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

# Restart button
if st.session_state.game_over:
    if st.button("🔄 Restart Game"):
        st.session_state.answer = random.choice(WORDS)
        st.session_state.guesses = []
        st.session_state.game_over = False
