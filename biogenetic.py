import streamlit as st

st.set_page_config(page_title="DNA 염기서열 변환기", page_icon="🧬")

st.title("🧬 DNA 염기서열 변환기")

st.write("DNA 염기서열(A, C, G, T)만 입력하세요.")

# 입력창
dna = st.text_input("DNA 염기서열 입력").upper()

# 입력이 있을 때만 실행
if dna:

    # 올바른 문자만 있는지 검사
    valid = {"A", "C", "G", "T"}

    if all(base in valid for base in dna):

        # 상보적 DNA
        dna_dict = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C"
        }

        opposite_dna = "".join(dna_dict[base] for base in dna)

        # RNA (전사)
        rna = opposite_dna.replace("T", "U")

        st.success(f'반대쪽 DNA의 염기서열은 "{opposite_dna}" 입니다.')
        st.success(f'RNA의 염기서열은 "{rna}" 입니다.')

    else:
        st.error("제대로 입력하세요! (A, C, G, T만 입력 가능합니다.)")
