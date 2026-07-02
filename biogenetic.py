import streamlit as st
import random
import math

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
# 돌연변이 함수
# ==========================
def mutate_dna(sequence, mutation_count):

    dna_list = list(sequence)

    # 중복 없이 위치 선택
    positions = random.sample(range(len(dna_list)), mutation_count)

    for pos in positions:

        current = dna_list[pos]

        # 현재 염기를 제외한 나머지 중 하나 선택
        candidates = ["A", "T", "G", "C"]
        candidates.remove(current)

        dna_list[pos] = random.choice(candidates)

    return "".join(dna_list)
    
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

INS_DNA = "ATGGCCCTGTGGATGCGCCTCCTGCCCCTG"

COLLAGEN_DNA = "ATGGTGCTGCTGGCCCTGCTGGCCCTGCTG"

SICKLE_HBB_DNA = "ATGGTGCACCTGACTCCTGTGGAGAAGTCT"

# 초기 상태일 때만 프리셋 버튼 표시

col1, col2, col3, col4= st.columns(4)

with col1:
    if st.button("🩸 헤모글로빈(HBB)"):
        st.session_state.dna_input = HBB_DNA
        st.rerun()

with col2:
    if st.button("💉 인슐린(INS)"):
        st.session_state.dna_input = INS_DNA
        st.rerun()
with col3:
    if st.button("🦴 콜라겐(COL1A1)"):
        st.session_state.dna_input = COLLAGEN_DNA
        st.rerun()

with col4:
    if st.button("🩸 낫모양 적혈구 빈혈"):
        st.session_state.dna_input = SICKLE_HBB_DNA
        st.session_state.converted = False
        st.rerun()



# ==========================
# 입력창
# ==========================
dna = st.text_input(
    "DNA 염기서열 입력",
    value=st.session_state.dna_input
)

st.session_state.dna_input = dna


# ==========================
# 변환 버튼
# ==========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    convert = st.button("🧬 염기서열 변환")

with col2:
    small_mutation = st.button("🟢 돌연변이(소)")

with col3:
    medium_mutation = st.button("🟡 돌연변이(중)")

with col4:
    large_mutation = st.button("🔴 돌연변이(대)")


# ==========================
# 돌연변이 처리
# ==========================
if small_mutation or medium_mutation or large_mutation:

    dna = st.session_state.dna_input.upper()

    valid = {"A", "C", "G", "T"}

    if len(dna) < 6:
        st.error("최소 6개의 염기가 입력되어 있어야 합니다.")

    elif not all(base in valid for base in dna):
        st.error("A, C, G, T만 입력 가능합니다.")

    else:

        if small_mutation:
            mutation_count = 1

        elif medium_mutation:
            mutation_count = max(2, math.ceil(len(dna) * 0.1))

        else:
            mutation_count = max(3, math.ceil(len(dna) / 3))

        st.session_state.dna_input = mutate_dna(
            dna,
            mutation_count
        )

        st.session_state.converted = False

        st.rerun()


# ==========================
# 변환
# ==========================
if convert:

    dna = st.session_state.dna_input.upper()

    valid = {"A", "C", "G", "T"}

    if dna == "":
        st.error("DNA를 입력하세요.")

    elif not all(base in valid for base in dna):
        st.error("❌ 제대로 입력하세요! (A, C, G, T만 입력 가능합니다.)")

    else:

        st.session_state.converted = True

        opposite_dna = "".join(dna_pair[b] for b in dna)

        rna = opposite_dna.replace("T", "U")

        amino_list = []

        for i in range(0, len(rna), 3):

            codon = rna[i:i+3]

            if len(codon) == 3:
                amino_list.append(codon_table.get(codon, "알수없음"))
            else:
                amino_list.append("알수없음")

        amino_result = " - ".join(amino_list)

        st.session_state.opposite = opposite_dna
        st.session_state.rna = rna
        st.session_state.amino = amino_result

        # -------------------
        # 상보적 DNA
        # -------------------
        opposite_dna = "".join(dna_pair[b] for b in dna)

        # -------------------
        #  염기 개수 통계
        # -------------------
        count_A = dna.count("A")
        count_T = dna.count("T")
        count_G = dna.count("G")
        count_C = dna.count("C")
        
        total = len(dna)

        # -------------------
        # GC 함량
        # -------------------
        gc_content = ((count_G + count_C) / total) * 100

        # -------------------
        # RNA
        # -------------------
        rna = opposite_dna.replace("T", "U")

        # -------------------
    # 시작/종결 코돈 분석
    # -------------------
    start_exists = "AUG" in rna
    
    stop_codons = []

    if "UAA" in rna:
        stop_codons.append("UAA")

    if "UAG" in rna:
        stop_codons.append("UAG")

    if "UGA" in rna:
        stop_codons.append("UGA")

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
        st.session_state.start_exists = start_exists
        st.session_state.stop_codons = stop_codons


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

    st.write("### 염기 개수 통계")

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("🟢 A", st.session_state.count_A)
    col2.metric("🔴 T", st.session_state.count_T)
    col3.metric("🟡 G", st.session_state.count_G)
    col4.metric("🔵 C", st.session_state.count_C)

    st.write("### GC 함량")

    st.metric(
        label="GC 함량",
        value=f"{st.session_state.gc_content:.1f}%"
    )

    if st.session_state.gc_content >= 60:
        st.info("GC 함량이 높은 DNA입니다.\n일반적으로 GC 결합이 많을수록 이중가닥이 더 안정적인 경향이 있습니다.")

    elif st.session_state.gc_content >= 40:
        st.info("GC 함량이 평균적인 수준입니다.\n일반적으로 GC 결합이 많을수록 이중가닥이 더 안정적인 경향이 있습니다.")

    else:
        st.info("GC 함량이 비교적 낮은 DNA입니다.\n일반적으로 GC 결합이 많을수록 이중가닥이 더 안정적인 경향이 있습니다.")

    st.write("## 시작 / 종결 코돈 분석")

    if st.session_state.start_exists:
        st.success("🟢 시작 코돈(AUG) 발견")
    else:
        st.warning("🟡 시작 코돈(AUG)을 찾지 못했습니다.")

    if len(st.session_state.stop_codons) == 0:
        st.warning("🟡 종결 코돈(UAA, UAG, UGA)을 찾지 못했습니다.")

    else:
        st.success(
            "🔴 종결 코돈 발견 : "
            + ", ".join(st.session_state.stop_codons)
        )

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
