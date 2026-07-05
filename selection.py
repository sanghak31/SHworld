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
DEFAULT_DISPLAY_COUNT = 10         # 표시할 유전자형 수 기본값
DEFAULT_MAX_POPULATION = 1000      # 최대 개체수 기본값
DEFAULT_MUTATION_RATE = 0          # 돌연변이 확률 기본값 (%)

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


def apply_max_population_cap(population: dict, max_population: int):
    """전체 개체수가 최대 개체수를 초과하면, 초과한 수만큼 무작위로 개체를 제거.
    (새로 태어난 개체와 기존 개체 구분 없이 전체 개체 중에서 무작위로 제거)
    """
    total = sum(population.values())
    if total <= max_population:
        return population, 0

    excess = total - max_population

    individuals = []
    for genotype, count in population.items():
        individuals.extend([genotype] * count)

    removed = random.sample(individuals, excess)

    new_population = dict(population)
    for genotype in removed:
        new_population[genotype] -= 1

    return new_population, excess


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


def apply_mutation(mated_population: dict, offspring_counts: dict, current_num_genes: int):
    """확률에 당첨된 경우, 교배로 새로 태어난 개체 중 하나를 골라 새로운 대립유전자를 부여.
    - 새로운 대립유전자는 GENE_LETTERS 순서상 다음 글자를 사용 (예: A,B 사용 중이면 C)
    - 선택된 돌연변이 개체는 새 유전자에 대해 이형접합(대문자+소문자, 예: Cc)을 가짐
    - 그 외 기존/신생 개체는 모두 새 유전자에 대해 동형접합 소문자(예: cc)를 가짐
    - 이미 최대 유전자 수(MAX_GENES)에 도달했거나, 이번 세대에 태어난 개체가 없으면
      돌연변이가 발생하지 않음 (population은 그대로, mutant_genotype은 None으로 반환)
    """
    if current_num_genes >= MAX_GENES:
        return mated_population, current_num_genes, None

    offspring_individuals = []
    for genotype, count in offspring_counts.items():
        offspring_individuals.extend([genotype] * count)

    if not offspring_individuals:
        return mated_population, current_num_genes, None

    mutant_base_genotype = random.choice(offspring_individuals)

    new_letter = GENE_LETTERS[current_num_genes]
    normal_suffix = new_letter.lower() * 2                              # 예: "cc"
    mutant_suffix = "".join(sorted([new_letter, new_letter.lower()]))    # 예: "Cc"

    # 1. 돌연변이가 될 개체 하나를 기존 개체수에서 제외
    working_population = dict(mated_population)
    working_population[mutant_base_genotype] -= 1

    # 2. 나머지 모든 개체(기존 + 신생)는 새 유전자 자리에 동형접합 소문자쌍을 부여
    new_population = {}
    for genotype, count in working_population.items():
        if count <= 0:
            continue
        extended_genotype = genotype + normal_suffix
        new_population[extended_genotype] = new_population.get(extended_genotype, 0) + count

    # 3. 돌연변이 개체를 이형접합(대문자+소문자)으로 추가
    mutant_genotype = mutant_base_genotype + mutant_suffix
    new_population[mutant_genotype] = new_population.get(mutant_genotype, 0) + 1

    new_num_genes = current_num_genes + 1
    return new_population, new_num_genes, mutant_genotype


def next_generation(population: dict, reproduction_rate: float, num_genes: int):
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
        child = mate(parent1, parent2, num_genes)
        offspring_counts[child] = offspring_counts.get(child, 0) + 1

    # 5. 기존 개체군에 자손을 더함 (부모 개체는 그대로 유지)
    new_population = dict(population)
    for genotype, count in offspring_counts.items():
        new_population[genotype] = new_population.get(genotype, 0) + count

    return new_population, offspring_counts, len(selected)


def compute_allele_frequencies(population: dict, num_genes: int) -> list:
    """유전자별로 전체 대립유전자 중 우성(대문자)/열성(소문자) 비율을 계산.
    반환값: [(글자, 우성비율%, 열성비율%), ...]
    """
    letters = get_gene_letters(num_genes)
    total_individuals = sum(population.values())
    total_alleles = total_individuals * 2  # 개체당 대립유전자 2개(이배체)

    frequencies = []
    for i, letter in enumerate(letters):
        upper_count = 0
        lower_count = 0
        for genotype, count in population.items():
            pair = genotype[i * 2: i * 2 + 2]
            upper_count += pair.count(letter) * count
            lower_count += pair.count(letter.lower()) * count

        upper_pct = (upper_count / total_alleles * 100) if total_alleles > 0 else 0
        lower_pct = (lower_count / total_alleles * 100) if total_alleles > 0 else 0
        frequencies.append((letter, upper_pct, lower_pct))
    return frequencies


# ------------------------------------------------------------
# 세션 상태 초기화
# ------------------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.generation = 0
    st.session_state.population = {}
    st.session_state.logs = []
    st.session_state.num_genes = DEFAULT_NUM_GENES


# ------------------------------------------------------------
# 상단: 옵션 설정
# ------------------------------------------------------------
st.title("🧬 자연선택 개체군 시뮬레이터")

st.header("⚙️ 옵션 설정")

opt_row1_col1, opt_row1_col2, opt_row1_col3 = st.columns(3)

with opt_row1_col1:
    num_genes_input = st.number_input(
        "대립유전자의 수",
        min_value=MIN_GENES,
        max_value=MAX_GENES,
        value=DEFAULT_NUM_GENES,
        step=1,
        disabled=st.session_state.started,
        help=f"사용할 유전자 쌍의 개수입니다 (1~{MAX_GENES}). 예: 4 -> A/a, B/b, C/c, D/d 사용.",
    )
    used_letters = ", ".join(
        f"{l}/{l.lower()}" for l in get_gene_letters(num_genes_input)
    )
    st.caption(f"사용되는 대립유전자: {used_letters}")

with opt_row1_col2:
    initial_population_input = st.number_input(
        "시초 개체수",
        min_value=1,
        max_value=100000,
        value=DEFAULT_INITIAL_POPULATION,
        step=1,
        disabled=st.session_state.started,
        help="시뮬레이션 시작 시 전체 개체수입니다. 시작 후에는 변경할 수 없습니다.",
    )

with opt_row1_col3:
    # 시작 전에는 옵션에서 설정한 유전자 수를, 시작 후에는(돌연변이로 늘어날 수 있으므로)
    # 실제 진행 중인 유전자 수를 기준으로 최대 표시 개수를 계산
    effective_num_genes = st.session_state.num_genes if st.session_state.started else num_genes_input
    max_display = 3 ** effective_num_genes
    display_count_input = st.number_input(
        "표시할 유전자형의 수",
        min_value=1,
        max_value=max_display,
        value=min(DEFAULT_DISPLAY_COUNT, max_display),
        step=1,
        help="개체수 비율이 높은 순서대로 상위 몇 개의 유전자형을 표시할지 정합니다.",
    )

opt_row2_col1, opt_row2_col2, opt_row2_col3 = st.columns(3)

with opt_row2_col1:
    reproduction_rate_input = st.slider(
        "자손 생성율 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_REPRODUCTION_RATE,
        step=1,
        help="매 세대마다 전체 개체 중 교배에 참여할 개체의 비율입니다.",
    )

with opt_row2_col2:
    death_rate_input = st.slider(
        "사망 비율 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_DEATH_RATE,
        step=1,
        help="매 세대 교배가 끝난 후, 전체 개체 중 무작위로 사망하는 비율입니다.",
    )

with opt_row2_col3:
    max_population_input = st.number_input(
        "최대 개체수",
        min_value=1,
        max_value=1000000,
        value=DEFAULT_MAX_POPULATION,
        step=1,
        help="전체 개체수의 상한선입니다. 교배로 인해 이를 초과하면, 초과한 수만큼 전체 개체 중 무작위로 개체가 죽습니다.",
    )

opt_row3_col1, _, _ = st.columns(3)

with opt_row3_col1:
    mutation_rate_input = st.slider(
        "돌연변이 확률 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_MUTATION_RATE,
        step=1,
        help="'다음 세대' 진행 시, 이 확률로 새로 태어난 개체 중 하나가 새로운 대립유전자를 갖고 등장합니다.",
    )

if st.session_state.started:
    st.caption("※ 대립유전자의 수와 시초 개체수는 시작 전에만 변경할 수 있고, 자손 생성율·사망 비율은 다음 세대부터 즉시 적용됩니다.")

st.divider()

# ------------------------------------------------------------
# 중간: 시뮬레이션
# ------------------------------------------------------------
st.header("🔬 시뮬레이션")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    if st.button("시뮬레이터 시작하기"):
        st.session_state.num_genes = num_genes_input
        st.session_state.population = init_population(initial_population_input, num_genes_input)
        st.session_state.generation = 1
        st.session_state.started = True
        used_letters_log = ", ".join(
            f"{l}/{l.lower()}" for l in get_gene_letters(num_genes_input)
        )
        st.session_state.logs.append(
            f"[시작] 대립유전자 {num_genes_input}쌍({used_letters_log}), "
            f"시초 개체수 {initial_population_input}마리로 시뮬레이션을 시작했습니다. (1세대)"
        )

with col2:
    if st.button("다음 세대", disabled=not st.session_state.started):
        # 1. 교배 진행 (자손 생성)
        mated_population, offspring_counts, num_mated = next_generation(
            st.session_state.population, reproduction_rate_input / 100, st.session_state.num_genes
        )
        num_offspring = sum(offspring_counts.values())

        # 2. 돌연변이 확률 판정
        mutation_log = ""
        if random.random() < mutation_rate_input / 100:
            mutated_population, new_num_genes, mutant_genotype = apply_mutation(
                mated_population, offspring_counts, st.session_state.num_genes
            )
            if mutant_genotype is not None:
                mated_population = mutated_population
                st.session_state.num_genes = new_num_genes
                mutation_log = f" / 돌연변이 발생! {mutant_genotype} 개체 등장"
            elif st.session_state.num_genes >= MAX_GENES:
                mutation_log = " / 돌연변이 시도됐으나 최대 대립유전자 수에 도달하여 무산"

        # 3. 최대 개체수를 초과하면, 초과한 수만큼 전체 개체 중 무작위로 제거
        capped_population, num_capped = apply_max_population_cap(
            mated_population, max_population_input
        )

        # 4. 사망 비율만큼 무작위 제거
        final_population, num_death = apply_death(
            capped_population, death_rate_input / 100
        )

        st.session_state.population = final_population
        st.session_state.generation += 1
        cap_log = f" / 최대 개체수({max_population_input}) 초과로 {num_capped}마리 사망" if num_capped > 0 else ""
        st.session_state.logs.append(
            f"[{st.session_state.generation}세대] 자손 생성율 {reproduction_rate_input}% 적용 - "
            f"{num_mated}마리가 교배하여 {num_offspring}마리 탄생{mutation_log}{cap_log} / "
            f"사망 비율 {death_rate_input}% 적용 - {num_death}마리 사망"
        )

with col3:
    if st.session_state.started:
        st.markdown(f"### {st.session_state.generation}세대")

st.write("")

# 가장 최근 로그를 버튼과 결과 표시 사이에 표시
if st.session_state.logs:
    st.info(st.session_state.logs[-1])

# 시뮬레이션 결과 표시 (시작 전에는 표시하지 않음)
if st.session_state.started:
    total = sum(st.session_state.population.values())
    sorted_items = sorted(
        st.session_state.population.items(), key=lambda x: x[1], reverse=True
    )[:display_count_input]

    for i in range(0, len(sorted_items), 2):
        row = st.columns(2)
        for j in range(2):
            if i + j < len(sorted_items):
                genotype, count = sorted_items[i + j]
                ratio = (count / total * 100) if total > 0 else 0
                row[j].markdown(f"**{genotype}** : {count} / {ratio:.1f}%")

    st.caption(f"전체 개체수: {total}마리")

    allele_frequencies = compute_allele_frequencies(
        st.session_state.population, st.session_state.num_genes
    )
    for letter, upper_pct, lower_pct in allele_frequencies:
        upper_str = "멸종" if upper_pct == 0 else f"{upper_pct:.1f}%"
        lower_str = "멸종" if lower_pct == 0 else f"{lower_pct:.1f}%"
        st.caption(f"{letter}/{letter.lower()} 대립유전자 비율 : {letter} {upper_str} / {letter.lower()} {lower_str}")
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
