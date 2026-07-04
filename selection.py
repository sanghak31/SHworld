import streamlit as st
import random

st.set_page_config(page_title="자연선택 개체군 시뮬레이터", layout="centered")

# ------------------------------------------------------------
# 상수 설정
# ------------------------------------------------------------
INITIAL_POPULATION = 90     # 시초 개체수
REPRODUCTION_RATE = 0.5     # 자손 생성율 (50%)

GENE1_GENOTYPES = ["AA", "Aa", "aa"]
GENE2_GENOTYPES = ["BB", "Bb", "bb"]
ALL_GENOTYPES = [g1 + g2 for g1 in GENE1_GENOTYPES for g2 in GENE2_GENOTYPES]


# ------------------------------------------------------------
# 시뮬레이션 로직 함수
# ------------------------------------------------------------
def init_population(total: int) -> dict:
    """시초 개체수를 9개 유전자형에 균등하게 분배"""
    n = len(ALL_GENOTYPES)
    base = total // n
    remainder = total % n
    pop = {}
    for i, g in enumerate(ALL_GENOTYPES):
        pop[g] = base + (1 if i < remainder else 0)
    return pop


def gamete(allele_pair: str) -> str:
    """유전자쌍(예: 'Aa')에서 배우자 하나를 무작위로 선택"""
    return random.choice(allele_pair)


def mate(parent1: str, parent2: str) -> str:
    """두 개체를 교배시켜 자손 유전자형 하나를 생성 (멘델 유전 법칙)"""
    p1_gene1, p1_gene2 = parent1[0:2], parent1[2:4]
    p2_gene1, p2_gene2 = parent2[0:2], parent2[2:4]

    child_gene1 = "".join(sorted([gamete(p1_gene1), gamete(p2_gene1)]))
    child_gene2 = "".join(sorted([gamete(p1_gene2), gamete(p2_gene2)]))
    return child_gene1 + child_gene2


def next_generation(population: dict, reproduction_rate: float):
    """한 세대를 진행시켜 새로운 개체군을 반환"""
    # 1. 개체 목록 전개 (유전자형별 개체수만큼 리스트에 펼침)
    individuals = []
    for genotype, count in population.items():
        individuals.extend([genotype] * count)

    total = len(individuals)
    num_select = round(total * reproduction_rate)
    num_select = min(num_select, total)

    # 2. 자손 생성율만큼 무작위로 개체 지목
    selected = random.sample(individuals, num_select)

    # 3. 홀수면 하나를 무작위로 제외
    if len(selected) % 2 == 1:
        selected.pop(random.randrange(len(selected)))

    # 4. 무작위로 두 마리씩 짝지어 순차적으로 교배
    random.shuffle(selected)
    offspring_counts = {}
    for i in range(0, len(selected), 2):
        parent1, parent2 = selected[i], selected[i + 1]
        child = mate(parent1, parent2)
        offspring_counts[child] = offspring_counts.get(child, 0) + 1

    # 5. 기존 개체군에 자손을 더함 (부모 개체는 그대로 유지)
    new_population = dict(population)
    for genotype, count in offspring_counts.items():
        new_population[genotype] = new_population.get(genotype, 0) + count

    return new_population, offspring_counts, len(selected)


# ------------------------------------------------------------
# 세션 상태 초기화
# ------------------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.generation = 0
    st.session_state.population = {}
    st.session_state.logs = []


# ------------------------------------------------------------
# 상단: 옵션 설정
# ------------------------------------------------------------
st.title("🧬 자연선택 개체군 시뮬레이터")

st.header("⚙️ 옵션 설정")
st.info("옵션 설정 기능은 추후 구현 예정입니다. (현재: 대립유전자 A/a, B/b · 시초 개체수 90 · 자손 생성율 50%)")

st.divider()

# ------------------------------------------------------------
# 중간: 시뮬레이션
# ------------------------------------------------------------
st.header("🔬 시뮬레이션")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("시뮬레이터 시작하기"):
        st.session_state.population = init_population(INITIAL_POPULATION)
        st.session_state.generation = 1
        st.session_state.started = True
        st.session_state.logs.append(
            f"[시작] 시초 개체수 {INITIAL_POPULATION}마리로 시뮬레이션을 시작했습니다. (1세대)"
        )

with col2:
    if st.button("다음 세대", disabled=not st.session_state.started):
        new_population, offspring_counts, num_mated = next_generation(
            st.session_state.population, REPRODUCTION_RATE
        )
        st.session_state.population = new_population
        st.session_state.generation += 1
        num_offspring = sum(offspring_counts.values())
        st.session_state.logs.append(
            f"[{st.session_state.generation}세대] {num_mated}마리가 교배하여 "
            f"{num_offspring}마리의 새로운 개체가 태어났습니다."
        )

with col3:
    if st.session_state.started:
        st.markdown(f"### {st.session_state.generation}세대")

st.write("")

# 시뮬레이션 결과 표시 (시작 전에는 표시하지 않음)
if st.session_state.started:
    total = sum(st.session_state.population.values())
    sorted_items = sorted(
        st.session_state.population.items(), key=lambda x: x[1], reverse=True
    )[:10]

    for i in range(0, len(sorted_items), 2):
        row = st.columns(2)
        for j in range(2):
            if i + j < len(sorted_items):
                genotype, count = sorted_items[i + j]
                ratio = (count / total * 100) if total > 0 else 0
                row[j].markdown(f"**{genotype}** : {count} / {ratio:.1f}%")

    st.caption(f"전체 개체수: {total}마리")
else:
    st.write("아직 시뮬레이션이 시작되지 않았습니다. '시뮬레이터 시작하기' 버튼을 눌러주세요.")

st.divider()

# ------------------------------------------------------------
# 하단: 로그 출력
# ------------------------------------------------------------
st.header("📋 로그 출력")

if st.session_state.logs:
    for log in reversed(st.session_state.logs):
        st.text(log)
else:
    st.caption("아직 기록된 로그가 없습니다.")
