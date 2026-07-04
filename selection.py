import streamlit as st
import random

st.set_page_config(page_title="자연선택 개체군 시뮬레이터", layout="centered")

# ------------------------------------------------------------
# 기본값 설정 (옵션 설정에서 조절 가능)
# ------------------------------------------------------------
DEFAULT_INITIAL_POPULATION = 90   # 시초 개체수 기본값
DEFAULT_REPRODUCTION_RATE = 50    # 자손 생성율 기본값 (%)
DEFAULT_DEATH_RATE = 0            # 사망 비율 기본값 (%)
DEFAULT_NUM_GENES = 2             # 대립유전자 수 기본값

GENE_LETTERS = "ABCDEFGHIJ"        # 대립유전자 표시 순서 (최대 10개)
MAX_GENES = 10
MIN_GENES = 1


def get_gene_letters(num_genes: int) -> list:
    """유전자 개수에 따라 사용할 알파벳 리스트 반환 (예: 3 -> ['A','B','C'])"""
    return list(GENE_LETTERS[:num_genes])


def generate_all_genotypes(num_genes: int) -> list:
    """유전자 개수에 따라 가능한 모든 유전자형 조합 생성.
    각 유전자는 대문자쌍(AA)/이형(Aa)/소문자쌍(aa) 3가지 상태를 가지며,
    유전자형 문자열은 각 유전자의 2글자 쌍을 순서대로 이어붙인 형태입니다.
    (예: 유전자 3개 -> 'AABbCc' 처럼 6글자)
    """
    letters = get_gene_letters(num_genes)
    gene_options = [[letter + letter, letter + letter.lower(), letter.lower() + letter.lower()]
                     for letter in letters]

    genotypes = [""]
    for options in gene_options:
        genotypes = [prefix + option for prefix in genotypes for option in options]
    return genotypes


# ------------------------------------------------------------
# 시뮬레이션 로직 함수
# ------------------------------------------------------------
def init_population(total: int, num_genes: int) -> dict:
    """시초 개체수를 모든 유전자형에 분배.
    - 균등하게 나눠 떨어지는 몫(base)은 모든 유전자형에 동일하게 배분
    - 나머지(remainder)는 서로 다른 유전자형에 최대 1마리씩만 무작위로 추가 배분
      (remainder는 항상 유전자형 개수보다 작으므로, 특정 유전자형이
       다른 유전자형보다 2마리 이상 더 많이 받는 일은 발생하지 않음)
    """
    all_genotypes = generate_all_genotypes(num_genes)
    n = len(all_genotypes)
    base = total // n
    remainder = total % n

    pop = {g: base for g in all_genotypes}
    if remainder > 0:
        lucky_genotypes = random.sample(all_genotypes, remainder)
        for g in lucky_genotypes:
            pop[g] += 1
    return pop


def gamete(allele_pair: str) -> str:
    """유전자쌍(예: 'Aa')에서 배우자 하나를 무작위로 선택"""
    return random.choice(allele_pair)


def mate(parent1: str, parent2: str, num_genes: int) -> str:
    """두 개체를 교배시켜 자손 유전자형 하나를 생성 (멘델 유전 법칙).
    유전자형 문자열은 유전자별로 2글자씩 순서대로 이어져 있다고 가정합니다.
    """
    child_parts = []
    for i in range(num_genes):
        p1_pair = parent1[i * 2: i * 2 + 2]
        p2_pair = parent2[i * 2: i * 2 + 2]
        child_pair = "".join(sorted([gamete(p1_pair), gamete(p2_pair)]))
        child_parts.append(child_pair)
    return "".join(child_parts)


def apply_death(population: dict, death_rate: float):
    """교배 후의 전체 개체군에서 사망 비율만큼 무작위로 개체를 제거"""
    individuals = []
    for genotype, count in population.items():
        individuals.extend([genotype] * count)

    total = len(individuals)
    num_death = round(total * death_rate)
    num_death = min(num_death, total)

    dead = random.sample(individuals, num_death)

    new_population = dict(population)
    for genotype in dead:
        new_population[genotype] -= 1

    return new_population, num_death


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
st.caption("현재 대립유전자는 A/a, B/b 두 쌍만 지원됩니다. (추가 대립유전자 옵션은 추후 구현 예정)")

opt_col1, opt_col2, opt_col3 = st.columns(3)

with opt_col1:
    initial_population_input = st.number_input(
        "시초 개체수",
        min_value=1,
        max_value=100000,
        value=DEFAULT_INITIAL_POPULATION,
        step=1,
        disabled=st.session_state.started,
        help="시뮬레이션 시작 시 전체 개체수입니다. 시작 후에는 변경할 수 없습니다.",
    )

with opt_col2:
    reproduction_rate_input = st.slider(
        "자손 생성율 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_REPRODUCTION_RATE,
        step=1,
        help="매 세대마다 전체 개체 중 교배에 참여할 개체의 비율입니다.",
    )

with opt_col3:
    death_rate_input = st.slider(
        "사망 비율 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_DEATH_RATE,
        step=1,
        help="매 세대 교배가 끝난 후, 전체 개체 중 무작위로 사망하는 비율입니다.",
    )

if st.session_state.started:
    st.caption("※ 시초 개체수는 시작 전에만 변경할 수 있고, 자손 생성율은 다음 세대부터 즉시 적용됩니다.")

st.divider()

# ------------------------------------------------------------
# 중간: 시뮬레이션
# ------------------------------------------------------------
st.header("🔬 시뮬레이션")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("시뮬레이터 시작하기"):
        st.session_state.population = init_population(initial_population_input)
        st.session_state.generation = 1
        st.session_state.started = True
        st.session_state.logs.append(
            f"[시작] 시초 개체수 {initial_population_input}마리로 시뮬레이션을 시작했습니다. (1세대)"
        )

with col2:
    if st.button("다음 세대", disabled=not st.session_state.started):
        # 1. 교배 진행 (자손 생성)
        mated_population, offspring_counts, num_mated = next_generation(
            st.session_state.population, reproduction_rate_input / 100
        )
        num_offspring = sum(offspring_counts.values())

        # 2. 교배 후 전체 개체군에서 사망 비율만큼 무작위 제거
        final_population, num_death = apply_death(
            mated_population, death_rate_input / 100
        )

        st.session_state.population = final_population
        st.session_state.generation += 1
        st.session_state.logs.append(
            f"[{st.session_state.generation}세대] 자손 생성율 {reproduction_rate_input}% 적용 - "
            f"{num_mated}마리가 교배하여 {num_offspring}마리 탄생 / "
            f"사망 비율 {death_rate_input}% 적용 - {num_death}마리 사망"
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
