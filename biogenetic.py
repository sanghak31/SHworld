import streamlit as st

st.set_page_config(page_title="DNA 염기서열 변환기", page_icon="🧬")

st.title("🧬 DNA 염기서열 변환기")

st.write("DNA 염기서열(A, C, G, T)만 입력하세요.")

# 입력창 (소문자 입력 가능)
dna = st.text_input("DNA 염기서열 입력")

# 색상 지정
colors = {
    "A": "#2ecc71",  # 초록
    "T": "#e74c3c",  # 빨강
    "G": "#f39c12",  # 주황
    "C": "#3498db",  # 파랑
    "U": "#9b59b6"   # 보라
}


def color_sequence(seq):
    """염기서열을 색깔 있는 HTML 문자열로 변환"""
    result = ""
    for base in seq:
        color = colors.get(base, "black")
        result += (
            f'<span style="color:{color};'
            f'font-size:28px;font-weight:bold;">{base}</span>'
        )
    return result


if dna:

    # 자동으로 대문자로 변환
    dna = dna.upper()

    # 입력 검사
    valid = {"A", "C", "G", "T"}

    if all(base in valid for base in dna):

        dna_dict = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C"
        }

        opposite = "".join(dna_dict[b] for b in dna)

        rna = opposite.replace("T", "U")

        st.success("변환 완료!")

        st.write("### 입력한 DNA")
        st.markdown(color_sequence(dna), unsafe_allow_html=True)

        st.write("### 반대쪽 DNA")
        st.markdown(color_sequence(opposite), unsafe_allow_html=True)

        st.write("### RNA")
        st.markdown(color_sequence(rna), unsafe_allow_html=True)

        st.write("")
        st.write(f'반대쪽 DNA의 염기서열은 **"{opposite}"** 입니다.')
        st.write(f'RNA의 염기서열은 **"{rna}"** 입니다.')

    else:
        st.error("❌ 제대로 입력하세요! (A, C, G, T만 입력 가능합니다.)")
