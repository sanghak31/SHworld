import streamlit as st

st.set_page_config(page_title="DNA 염기서열 변환기", page_icon="🧬")

st.title("🧬 DNA → RNA → 아미노산 변환기")
st.write("DNA 염기서열(A, C, G, T)만 입력하세요.")

# ==========================
# 색상 설정
# ==========================
colors = {
    "A": "#2ecc71",   # 초록
    "T": "#e74c3c",   # 빨강
    "G": "#f39c12",   # 주황
    "C": "#3498db",   # 파랑
    "U": "#9b59b6"    # 보라
}


def color_sequence(seq):
    html = ""
    for base in seq:
        color = colors.get(base, "black")
        html += f'<span style="color:{color}; font-size:30px; font-weight:bold;">{base}</span>'
    return html


# ==========================
# 상보적 DNA
# ==========================
dna_pair = {
    "A": "T",
    "T": "A",
    "C": "G",
    "G": "C"
}

# ==========================
# 코돈표
# ==========================
codon_table = {

    "UUU":"페닐알라닌","UUC":"페닐알라닌",

    "UUA":"류신","UUG":"류신",
    "CUU":"류신","CUC":"류신","CUA":"류신","CUG":"류신",

    "AUU":"아이소류신","AUC":"아이소류신","AUA":"아이소류신",

    "AUG":"메티오닌",

    "GUU":"발린","GUC":"발린","GUA":"발린","GUG":"발린",

    "UCU":"세린","UCC":"세린","UCA":"세린","UCG":"세린",
    "AGU":"세린","AGC":"세린",

    "CCU":"프롤린","CCC":"프롤린","CCA":"프롤린","CCG":"프롤린",

    "ACU":"트레오닌","ACC":"트레오닌","ACA":"트레오닌","ACG":"트레오닌",

    "GCU":"알라닌","GCC":"알라닌","GCA":"알라닌","GCG":"알라닌",

    "UAU":"티로신","UAC":"티로신",

    "CAU":"히스티딘","CAC":"히스티딘",

    "CAA":"글루타민","CAG":"글루타민",

    "AAU":"아스파라긴","AAC":"아스파라긴",

    "AAA":"라이신","AAG":"라이신",

    "GAU":"아스파트산","GAC":"아스파트산",

    "GAA":"글루탐산","GAG":"글루탐산",

    "UGU":"시스테인","UGC":"시스테인",

    "UGG":"트립토판",

    "CGU":"아르지닌","CGC":"아르지닌","CGA":"아르지닌","CGG":"아르지닌",
    "AGA":"아르지닌","AGG":"아르지닌",

    "GGU":"글라이신","GGC":"글라이신","GGA":"글라이신","GGG":"글라이신",

    "UAA":"종결","UAG":"종결","UGA":"종결"
}
# ==========================
# Session State 초기화
# ==========================
if "dna_input" not in st.session_state:
    st.session_state.dna_input = ""

if "converted" not in st.session_state:
    st.session_state.converted = False


# ==========================
# 프리셋
# ==========================
HBB_DNA = "ATGGTGCACCTGACTCCTGAGGAGAAGTCT"

# 초기 상태일 때만 프리셋 버튼 표시
if not st.session_state.converted:

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🩸 헤모글로빈(HBB)"):
            st.session_state.dna_input = HBB_DNA
            st.rerun()

    with col2:
        st.button("백혈구(준비중)", disabled=True)


# ==========================
# 입력창
# ==========================
dna = st.text_input(
    "DNA 염기서열 입력",
    key="dna_input"
)


# ==========================
# 변환 버튼
# ==========================
if st.button("🧬 염기서열 변환"):

    dna = st.session_state.dna_input.upper()

    valid = {"A", "C", "G", "T"}

    if dna == "":
        st.error("DNA를 입력하세요.")

    elif not all(base in valid for base in dna):
        st.error("❌ 제대로 입력하세요! (A, C, G, T만 입력 가능합니다.)")

    else:

        st.session_state.converted = True

        # -------------------
        # 상보적 DNA
        # -------------------
        opposite_dna = "".join(dna_pair[b] for b in dna)

        # -------------------
        # RNA
        # -------------------
        rna = opposite_dna.replace("T", "U")

        # -------------------
        # 아미노산
        # -------------------
        amino_list = []

        for i in range(0, len(rna), 3):

            codon = rna[i:i+3]

            if len(codon) == 3:
                amino_list.append(codon_table.get(codon, "알수없음"))
            else:
                amino_list.append("알수없음")

        amino_result = " - ".join(amino_list)

        # 결과 저장
        st.session_state.opposite = opposite_dna
        st.session_state.rna = rna
        st.session_state.amino = amino_result


# ==========================
# 결과 출력
# ==========================
if st.session_state.converted:

    st.success("변환 완료!")

    st.write("## 입력한 DNA")
    st.markdown(color_sequence(st.session_state.dna_input.upper()),
                unsafe_allow_html=True)

    st.write("## 반대쪽 DNA")
    st.markdown(color_sequence(st.session_state.opposite),
                unsafe_allow_html=True)

    st.write("## RNA")
    st.markdown(color_sequence(st.session_state.rna),
                unsafe_allow_html=True)

    st.write("## 아미노산")
    st.success(st.session_state.amino)

    st.divider()

    st.write(
        f'**반대쪽 DNA의 염기서열은 "{st.session_state.opposite}" 입니다.**'
    )

    st.write(
        f'**RNA의 염기서열은 "{st.session_state.rna}" 입니다.**'
    )

    st.write(
        f'**아미노산 : {st.session_state.amino}**'
    )

    # -------------------
    # 초기화 버튼
    # -------------------
    if st.button("🔄 초기화"):

        st.session_state.dna_input = ""
        st.session_state.converted = False

        # 결과 삭제
        for key in ["opposite", "rna", "amino"]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()
