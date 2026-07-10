import streamlit as st
import pandas as pd
import random
import pandas as pd

st.set_page_config(page_title="자연선택 개체군 시뮬레이터", layout="centered")

# ------------------------------------------------------------
# 기본값 설정 (옵션 설정에서 조절 가능)
# ------------------------------------------------------------
DEFAULT_INITIAL_POPULATION = 90   # 시초 개체수 기본값
DEFAULT_REPRODUCTION_RATE = 50    # 자손 생성율 기본값 (%)
DEFAULT_DEATH_RATE = 0            # 사망 비율 기본값 (%)
DEFAULT_ERROR = 0                 # 오차 기본값 (%)
DEFAULT_NUM_GENES = 2             # 대립유전자 수 기본값
DEFAULT_DISPLAY_COUNT = 10         # 표시할 유전자형 수 기본값
DEFAULT_MAX_POPULATION = 1000      # 최대 개체수 기본값
DEFAULT_MUTATION_RATE = 0          # 돌연변이 확률 기본값 (%)
DEFAULT_OFFSPRING_PER_PAIR = 1      # 1회 교배 출산 개체수 기본값
DEFAULT_PROSPERITY = 0              # 번성 기본값
DEFAULT_DECLINE = 0                 # 쇠락 기본값
DEFAULT_EVENT_CHANCE = 0            # 이벤트 발생 확률 기본값 (%)
DEFAULT_EVENT_MAX_COUNT = 3         # 이벤트 최대 개수 기본값

GENE_LETTERS = "ABCDEFGHIJ"        # 대립유전자 표시 순서 (최대 10개)
MAX_GENES = 10
MIN_GENES = 1

# 이벤트 정의: 각 이벤트는 옵션값 자체를 바꾸지 않고, 계산 시점에만 보너스/배율로 적용됨
# - "rolls": 이벤트 발생 시 이 범위(포함) 내에서 정수 하나를 무작위로 뽑아 고정하고,
#            사라지기 전까지 그 값이 계속 유지됨
#   · prosperity_bonus: 번성에 그대로 더해지는 값
#   · decline_bonus: 쇠락에 그대로 더해지는 값
#   · max_population_pct: 최대 개체수 증가율(%) -> 배율 = 1 + 값/100
#   · death_point_add: 사망률에 %p로 그대로 더해지는 값
#   · death_pct: 사망률 상대적 증가율(%) -> 배율 = 1 + 값/100
#   · climate_probability_pct: 기후변화의 개별 사망 확률(%)
#   · predator_pct: 포식자의 진화로 인한 사망 가중치 증가율(%) -> 배율 = 1 + 값/100
EVENTS = {
    "풍족한 먹이": {
        "rolls": {"prosperity_bonus": (10, 50), "max_population_pct": (50, 100)},
        "description_template": "번성이 {prosperity_bonus} 증가하고, 최대 개체수가 {max_population_pct}% 증가합니다.",
    },
    "자연재해": {
        "rolls": {"death_point_add": (10, 25)},
        "description_template": "사망률이 {death_point_add}%p 증가합니다.",
    },
    "먹이 부족": {
        "rolls": {"decline_bonus": (20, 40), "death_pct": (10, 50)},
        "description_template": "쇠락이 {decline_bonus} 증가하고, 사망률이 {death_pct}% 증가합니다.",
    },
    "포식자 증가": {
        "rolls": {"death_pct": (30, 70)},
        "description_template": "사망률이 {death_pct}% 증가합니다.",
    },
    "먹이 경쟁 심화": {
        "rolls": {"decline_bonus": (20, 40)},
        "description_template": "쇠락이 {decline_bonus} 증가합니다.",
    },
    "기후변화": {
        "type": "trait_flat_death",
        "rolls": {"climate_probability_pct": (10, 30)},
        "description_template": "{trait} 성질을 지니지 못한 개체는 {climate_probability_pct}%의 사망 확률이 적용됩니다.",
    },
    "포식자의 진화": {
        "type": "trait_weight_death",
        "rolls": {"predator_pct": (100, 400)},
        "description_template": "{trait} 성질을 지니지 못한 개체는 자연 사망될 확률이 {predator_pct}% 증가합니다.",
    },
    "포식자 감소": {
        "rolls": {"death_pct_decrease": (10, 50)},
        "description_template": "사망률이 {death_pct_decrease}% 감소합니다.",
    },
    "위장": {
        "type": "camouflage",
        "rolls": {"survival_pct": (100, 400)},
        "description_template": "{trait} 대립유전자를 지닌 개체의 생존 확률이 {survival_pct}% 증가합니다.",
    },
}


def roll_event_values(event_def: dict) -> dict:
    """이벤트 정의의 rolls 범위 내에서 값을 무작위로 뽑아 딕셔너리로 반환 (발생 시 한 번만 호출)"""
    rolled = {}
    for key, (low, high) in event_def.get("rolls", {}).items():
        rolled[key] = random.randint(low, high)
    return rolled


def lacks_trait(genotype: str, gene_index: int, trait_type: str) -> bool:
    """개체(genotype)가 특정 유전자 자리(gene_index)의 특정 성질(trait_type)을 지니지 '못했는지' 판정.
    - trait_type == 'dominant' (예: 'A' 성질): 대문자를 하나라도 가지면 그 성질을 지님 (AA, Aa) -> 지니지 못한 건 aa뿐
    - trait_type == 'recessive' (예: 'a' 성질): 동형 소문자(aa)여야만 그 성질을 지님 -> 지니지 못한 건 AA, Aa
    """
    letter = GENE_LETTERS[gene_index]
    pair = genotype[gene_index * 2: gene_index * 2 + 2]
    if trait_type == "dominant":
        has_trait = letter in pair
    else:
        has_trait = pair == letter.lower() * 2
    return not has_trait


def has_specific_allele(genotype: str, gene_index: int, trait_type: str) -> bool:
    """개체(genotype)가 특정 유전자 자리(gene_index)에서 특정 대립유전자(trait_type이 가리키는
    대문자 또는 소문자 한 글자)를 하나라도 지니고 있는지 판정. (표현형이 아니라 대립유전자 자체의 보유 여부)
    """
    letter = GENE_LETTERS[gene_index]
    pair = genotype[gene_index * 2: gene_index * 2 + 2]
    allele_char = letter if trait_type == "dominant" else letter.lower()
    return allele_char in pair


def get_trait_label(gene_index: int, trait_type: str) -> str:
    letter = GENE_LETTERS[gene_index]
    return letter if trait_type == "dominant" else letter.lower()


def get_event_description(event_entry: dict) -> str:
    """이벤트 인스턴스의 실제 설명 문구를 생성 (난수로 뽑힌 값과, 형질 기반 이벤트는 대상 성질을 채워 넣음)"""
    event_def = EVENTS[event_entry["name"]]
    format_values = dict(event_entry.get("rolled", {}))
    if "gene_index" in event_entry:
        format_values["trait"] = get_trait_label(event_entry["gene_index"], event_entry["trait_type"])
    return event_def["description_template"].format(**format_values)


def weighted_sample_without_replacement(items_with_weights: list, k: int) -> list:
    """가중치가 반영된 비복원 무작위 추출 (Efraimidis-Spirakis 방식).
    가중치가 클수록 뽑힐 확률이 높아지되, 총 뽑히는 개수(k)는 그대로 유지됨.
    """
    if k <= 0:
        return []
    keyed = []
    for item, weight in items_with_weights:
        weight = max(weight, 1e-9)
        u = random.random()
        key = u ** (1.0 / weight)
        keyed.append((key, item))
    keyed.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in keyed[:k]]


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


def compute_death_weight(
    genotype: str, predator_weight_events: list = None, camouflage_events: list = None
) -> float:
    """개체 하나가 '죽는 쪽으로 뽑힐' 상대적 가중치를 계산.
    - 포식자의 진화: 대상 성질을 지니지 못한 개체는 가중치가 곱해져 죽을 확률이 높아짐
    - 위장: 대상 대립유전자를 지닌 개체는 가중치가 나눠져 죽을 확률이 낮아짐(생존 확률 증가)
    두 효과 모두 사망률로 인한 자연사망과 최대 개체수 초과로 인한 사망 둘 다에 동일하게 적용됨.
    """
    weight = 1.0
    for gene_index, trait_type, multiplier in (predator_weight_events or []):
        if lacks_trait(genotype, gene_index, trait_type):
            weight *= multiplier
    for gene_index, trait_type, survival_multiplier in (camouflage_events or []):
        if has_specific_allele(genotype, gene_index, trait_type):
            weight /= survival_multiplier
    return weight


def weighted_death_selection(
    individuals: list, num_death: int, predator_weight_events: list = None, camouflage_events: list = None
) -> list:
    """포식자의 진화/위장 효과가 있으면 가중 비복원 추출로, 없으면 균등 무작위 추출로 사망 대상을 선택."""
    if not predator_weight_events and not camouflage_events:
        return random.sample(individuals, num_death)

    weights = [compute_death_weight(g, predator_weight_events, camouflage_events) for g in individuals]
    return weighted_sample_without_replacement(list(zip(individuals, weights)), num_death)


def apply_max_population_cap(
    population: dict, max_population: int, predator_weight_events: list = None, camouflage_events: list = None
):
    """전체 개체수가 최대 개체수를 초과하면, 초과한 수의 '절반'만큼만 개체를 제거해 서서히 맞춰감.
    (새로 태어난 개체와 기존 개체 구분 없이 전체 개체 중에서 선택하며,
     포식자의 진화/위장 효과가 있으면 그 가중치가 반영됨)
    """
    total = sum(population.values())
    if total <= max_population:
        return population, 0

    excess = total - max_population
    num_to_remove = round(excess / 2)
    num_to_remove = min(num_to_remove, total)

    individuals = []
    for genotype, count in population.items():
        individuals.extend([genotype] * count)

    removed = weighted_death_selection(individuals, num_to_remove, predator_weight_events, camouflage_events)

    new_population = dict(population)
    for genotype in removed:
        new_population[genotype] -= 1

    return new_population, num_to_remove


def apply_death(population: dict, death_rate: float, predator_weight_events: list = None, camouflage_events: list = None):
    """교배 후의 전체 개체군에서 사망률만큼 개체를 제거.
    포식자의 진화/위장 효과가 있으면 그 가중치가 반영되며, 전체 사망 개체수 자체는 그대로 유지됨.
    """
    individuals = []
    for genotype, count in population.items():
        individuals.extend([genotype] * count)

    total = len(individuals)
    num_death = round(total * death_rate)
    num_death = min(num_death, total)

    dead = weighted_death_selection(individuals, num_death, predator_weight_events, camouflage_events)

    new_population = dict(population)
    for genotype in dead:
        new_population[genotype] -= 1

    return new_population, num_death


def apply_trait_specific_death(population: dict, climate_events: list):
    """'기후변화' 이벤트 적용: 특정 성질을 지니지 못한 개체 각각에 대해
    독립적으로 확률 판정을 진행해 사망시킴 (전체 사망 비율과 별개로 추가 적용).
    """
    new_population = dict(population)
    total_removed = 0

    for gene_index, trait_type, probability in climate_events:
        for genotype, count in list(new_population.items()):
            if count <= 0:
                continue
            if lacks_trait(genotype, gene_index, trait_type):
                deaths = sum(1 for _ in range(count) if random.random() < probability)
                new_population[genotype] -= deaths
                total_removed += deaths

    return new_population, total_removed


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


def apply_error_margin(base_value_percent: float, error_percent: float) -> float:
    """기준값에 오차 범위를 적용해 무작위 값을 반환.
    오차 범위 = 기준값 * (오차 / 100), 그 범위 내에서 균등 분포로 무작위 선택.
    """
    if error_percent <= 0:
        return base_value_percent
    margin = base_value_percent * (error_percent / 100)
    value = random.uniform(base_value_percent - margin, base_value_percent + margin)
    return max(value, 0)


def compute_effective_participation_rate(
    base_rate_percent: float,
    current_population: int,
    max_population: int,
    prosperity_percent: float,
    decline_percent: float,
) -> float:
    """번성/쇠락 옵션을 반영한 실제 교배 참여율(%)을 계산.
    - 번성: 현재 개체수가 최대 개체수의 절반 미만일 때만 적용.
      증가 비율 = 번성 * (1 - 현재 개체수 / (최대 개체수 / 2))
      1차 참여율 = 기본 교배 참여율 * (1 + 증가 비율 / 100)
    - 쇠락: 현재 개체수가 최대 개체수의 절반 이상일 때만 적용 (절반 미만이면 효과 없음).
      감소 비율 = (현재 개체수 / 최대 개체수) * (쇠락 / 100)
      최종 참여율 = 1차 참여율 * (1 - 감소 비율)   (※ %p 감소가 아니라 % 만큼의 상대적 감소)
    """
    if max_population <= 0:
        return base_rate_percent

    half_max = max_population / 2

    # 1. 번성 효과 (증가) - 절반 미만일 때만 적용
    if current_population < half_max:
        boost_ratio = 1 - (current_population / half_max)
        boost_ratio = max(boost_ratio, 0)
        boost_percent = prosperity_percent * boost_ratio
    else:
        boost_percent = 0

    rate_after_prosperity = base_rate_percent * (1 + boost_percent / 100)

    # 2. 쇠락 효과 (감소, 상대적 비율 감소) - 절반 이상일 때만 적용
    if current_population >= half_max:
        pop_ratio = current_population / max_population
        pop_ratio = min(max(pop_ratio, 0), 1)
        decline_ratio = pop_ratio * (decline_percent / 100)
        decline_ratio = min(decline_ratio, 1)  # 참여율이 음수가 되지 않도록 제한
    else:
        decline_ratio = 0

    rate_after_decline = rate_after_prosperity * (1 - decline_ratio)

    return rate_after_decline


def next_generation(
    population: dict,
    base_participation_rate_percent: float,
    num_genes: int,
    offspring_per_pair: int,
    max_population: int,
    prosperity_percent: float,
    decline_percent: float,
):
    """한 세대를 진행시켜 새로운 개체군을 반환.
    - 번성/쇠락 옵션에 따라 실제 교배 참여율이 기본값보다 높거나 낮아질 수 있음
    - 교배 참여율이 100%를 넘으면, 100%씩 완전히 채운 후 남은 비율만큼 추가로 교배를 진행
      (매 라운드 모두 원래(이번 세대 시작 시점) 개체군에서 무작위로 선택)
    - 교배 한 쌍마다 offspring_per_pair 마리의 자손이 태어남
    """
    current_total = sum(population.values())
    effective_rate_percent = compute_effective_participation_rate(
        base_participation_rate_percent, current_total, max_population, prosperity_percent, decline_percent
    )

    # 이번 세대 시작 시점의 개체 목록 (모든 라운드에서 공통으로 사용하는 원본 풀)
    individuals = []
    for genotype, count in population.items():
        individuals.extend([genotype] * count)
    total = len(individuals)

    offspring_counts = {}
    total_mated = 0
    remaining_percent = effective_rate_percent

    while remaining_percent > 1e-9 and total > 0:
        round_percent = min(remaining_percent, 100)
        num_select = round(total * (round_percent / 100))
        num_select = min(num_select, total)

        if num_select >= 2:
            selected = random.sample(individuals, num_select)
            if len(selected) % 2 == 1:
                selected.pop(random.randrange(len(selected)))
            random.shuffle(selected)

            for i in range(0, len(selected), 2):
                parent1, parent2 = selected[i], selected[i + 1]
                for _ in range(offspring_per_pair):
                    child = mate(parent1, parent2, num_genes)
                    offspring_counts[child] = offspring_counts.get(child, 0) + 1

            total_mated += len(selected)

        remaining_percent -= 100

    # 기존 개체군에 자손을 더함 (부모 개체는 그대로 유지)
    new_population = dict(population)
    for genotype, count in offspring_counts.items():
        new_population[genotype] = new_population.get(genotype, 0) + count

    return new_population, offspring_counts, total_mated, effective_rate_percent


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


def record_history_snapshot():
    """현재 세대의 전체 개체수와 유전자별 우성 대립유전자 비율을 히스토리에 기록 (그래프용)"""
    total_population = sum(st.session_state.population.values())
    entry = {"generation": st.session_state.generation, "population": total_population}

    frequencies = compute_allele_frequencies(st.session_state.population, st.session_state.num_genes)
    for letter, upper_pct, lower_pct in frequencies:
        entry[letter] = upper_pct  # 우성 대립유전자 비율(%) 기준으로 기록 (열성 비율은 100 - 값)

    st.session_state.history.append(entry)


EVENT_QUEUE_LENGTH = 10


def ensure_event_queue_filled():
    """이벤트 예고 큐가 항상 EVENT_QUEUE_LENGTH개를 유지하도록 무작위 이벤트로 채움"""
    event_names = list(EVENTS.keys())
    while len(st.session_state.event_queue) < EVENT_QUEUE_LENGTH:
        st.session_state.event_queue.append(random.choice(event_names))


def get_event_preview_description(event_name: str) -> str:
    """아직 발생하지 않은 예고 이벤트의 설명(구체적인 수치 대신 범위로 표시)"""
    event_def = EVENTS[event_name]
    format_values = {key: f"{low}~{high}" for key, (low, high) in event_def.get("rolls", {}).items()}
    if "{trait}" in event_def["description_template"]:
        format_values["trait"] = "(무작위 대립유전자)"
    return event_def["description_template"].format(**format_values)


def trigger_event(active_events: list, event_chance_percent: float, max_event_count: int, current_num_genes: int):
    """확률에 따라 이벤트 예고 큐의 맨 앞쪽에서 하나를 꺼내 발생시킴 (중복 불가).
    - 큐에서 현재 활성화되지 않은 이벤트 중 가장 앞선 것을 사용하고, 사용한 자리는 새 이벤트로 채워짐
    - 이미 최대 개수에 도달했다면 가장 오래된 활성 이벤트를 제거하고 새 이벤트를 추가
    - 큐 전체가 이미 활성 상태인 이벤트들로만 채워져 있다면 "no_available" 반환
    - 확률에 당첨되지 않으면 (원래 active_events, None) 그대로 반환
    - 형질 기반 이벤트(기후변화/포식자의 진화/위장)는 대상이 될 유전자와 성질(우성/열성)을 이때 무작위로 정함
    """
    if random.random() >= event_chance_percent / 100:
        return list(active_events), None

    ensure_event_queue_filled()
    active_names = [entry["name"] for entry in active_events]

    chosen_index = next(
        (i for i, name in enumerate(st.session_state.event_queue) if name not in active_names), None
    )
    if chosen_index is None:
        return list(active_events), "no_available"

    new_event_name = st.session_state.event_queue.pop(chosen_index)
    ensure_event_queue_filled()

    event_def = EVENTS[new_event_name]
    new_entry = {"name": new_event_name, "rolled": roll_event_values(event_def)}

    if event_def.get("type") in ("trait_flat_death", "trait_weight_death", "camouflage"):
        new_entry["gene_index"] = random.randrange(current_num_genes)
        new_entry["trait_type"] = random.choice(["dominant", "recessive"])

    new_active_events = list(active_events)
    if len(new_active_events) >= max_event_count:
        new_active_events.pop(0)  # 가장 오래된 이벤트 제거
    new_active_events.append(new_entry)
    return new_active_events, new_entry



def compute_event_effects(active_events: list):
    """현재 활성화된 이벤트들의 효과를 종류별로 합산 (각 이벤트에 저장된 rolled 값을 사용).
    반환값: (번성 보너스, 쇠락 보너스, 최대개체수 배율, 사망률 %p 가산, 사망률 배율,
             기후변화 목록[(gene_index, trait_type, 확률)],
             포식자의 진화 목록[(gene_index, trait_type, 배율)],
             위장 목록[(gene_index, trait_type, 생존배율)])
    """
    prosperity_bonus = 0
    decline_bonus = 0
    max_population_mult = 1.0
    death_rate_point_add = 0
    death_rate_mult = 1.0
    climate_events = []
    predator_weight_events = []
    camouflage_events = []

    for entry in active_events:
        rolled = entry.get("rolled", {})

        if "prosperity_bonus" in rolled:
            prosperity_bonus += rolled["prosperity_bonus"]
        if "decline_bonus" in rolled:
            decline_bonus += rolled["decline_bonus"]
        if "max_population_pct" in rolled:
            max_population_mult *= (1 + rolled["max_population_pct"] / 100)
        if "death_point_add" in rolled:
            death_rate_point_add += rolled["death_point_add"]
        if "death_pct" in rolled:
            death_rate_mult *= (1 + rolled["death_pct"] / 100)
        if "death_pct_decrease" in rolled:
            death_rate_mult *= (1 - rolled["death_pct_decrease"] / 100)
        if "climate_probability_pct" in rolled:
            climate_events.append(
                (entry["gene_index"], entry["trait_type"], rolled["climate_probability_pct"] / 100)
            )
        if "predator_pct" in rolled:
            predator_weight_events.append(
                (entry["gene_index"], entry["trait_type"], 1 + rolled["predator_pct"] / 100)
            )
        if "survival_pct" in rolled:
            camouflage_events.append(
                (entry["gene_index"], entry["trait_type"], 1 + rolled["survival_pct"] / 100)
            )

    return (
        prosperity_bonus,
        decline_bonus,
        max_population_mult,
        death_rate_point_add,
        death_rate_mult,
        climate_events,
        predator_weight_events,
        camouflage_events,
    )


# ------------------------------------------------------------
# 세션 상태 초기화
# ------------------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.generation = 0
    st.session_state.population = {}
    st.session_state.logs = []
    st.session_state.num_genes = DEFAULT_NUM_GENES
    st.session_state.active_events = []
    st.session_state.history = []
    st.session_state.event_queue = []
    ensure_event_queue_filled()


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

    # 토글 위젯이 생성되기 전이므로, 이전 렌더링에서의 토글 상태를 세션 상태에서 미리 확인
    show_all_genotypes_prev = st.session_state.get("show_all_genotypes_toggle", False)

    display_count_input = st.number_input(
        "표시할 유전자형의 수",
        min_value=1,
        max_value=max_display,
        value=min(DEFAULT_DISPLAY_COUNT, max_display),
        step=1,
        disabled=show_all_genotypes_prev,
        help="개체수 비율이 높은 순서대로 상위 몇 개의 유전자형을 표시할지 정합니다.",
    )

    show_all_genotypes_input = st.toggle(
        "모든 유전자형 표시하기",
        value=False,
        key="show_all_genotypes_toggle",
        help="켜면 상황에 관계없이 '표시할 유전자형의 수'가 항상 최댓값으로 고정됩니다.",
    )
    if show_all_genotypes_input:
        display_count_input = max_display

opt_row2_col1, opt_row2_col2, opt_row2_col3, opt_row2_col4 = st.columns(4)

with opt_row2_col1:
    reproduction_rate_input = st.slider(
        "교배 참여율 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_REPRODUCTION_RATE,
        step=1,
        help="매 세대마다 전체 개체 중 교배에 참여할 개체의 기본 비율입니다.",
    )

with opt_row2_col2:
    death_rate_input = st.slider(
        "사망률 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_DEATH_RATE,
        step=1,
        help="매 세대 교배가 끝난 후, 전체 개체 중 무작위로 사망하는 비율입니다.",
    )

with opt_row2_col3:
    error_margin_input = st.slider(
        "오차 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_ERROR,
        step=1,
        help="교배 참여율과 사망률에 매 세대 적용되는 오차 범위입니다.",
    )

with opt_row2_col4:
    max_population_input = st.number_input(
        "최대 개체수",
        min_value=1,
        max_value=1000000,
        value=DEFAULT_MAX_POPULATION,
        step=1,
        help="전체 개체수의 상한선입니다. 교배로 인해 이를 초과하면, 초과한 수만큼 전체 개체 중 무작위로 개체가 죽습니다.",
    )

opt_row3_col1, opt_row3_col2, opt_row3_col3, opt_row3_col4 = st.columns(4)

with opt_row3_col1:
    mutation_rate_input = st.slider(
        "돌연변이 확률 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_MUTATION_RATE,
        step=1,
        help="'다음 세대' 진행 시, 이 확률로 새로 태어난 개체 중 하나가 새로운 대립유전자를 갖고 등장합니다.",
    )

with opt_row3_col2:
    offspring_per_pair_input = st.slider(
        "1회 교배 출산 개체수",
        min_value=1,
        max_value=10,
        value=DEFAULT_OFFSPRING_PER_PAIR,
        step=1,
        help="교배 한 쌍이 성사될 때마다 태어나는 자손의 수입니다.",
    )

with opt_row3_col3:
    prosperity_input = st.slider(
        "번성",
        min_value=0,
        max_value=100,
        value=DEFAULT_PROSPERITY,
        step=1,
        help="현재 개체수가 최대 개체수의 절반보다 적을 때, 그 차이만큼 교배 참여율을 추가로 끌어올립니다.",
    )

with opt_row3_col4:
    decline_input = st.slider(
        "쇠락",
        min_value=0,
        max_value=100,
        value=DEFAULT_DECLINE,
        step=1,
        help="현재 개체수가 최대 개체수의 절반 이상일 때, 최대 개체수 대비 현재 개체수 비율만큼 교배 참여율을 상대적으로 감소시킵니다.",
    )

opt_row4_col1, opt_row4_col2 = st.columns(2)

with opt_row4_col1:
    event_chance_input = st.slider(
        "이벤트 발생 확률 (%)",
        min_value=0,
        max_value=100,
        value=DEFAULT_EVENT_CHANCE,
        step=1,
        help="'다음 세대' 진행 시, 이 확률로 새로운 이벤트가 하나 발생합니다. 이벤트는 사라지기 전까지 효과가 계속 적용됩니다.",
    )

with opt_row4_col2:
    event_max_count_input = st.slider(
        "이벤트 최대 개수",
        min_value=1,
        max_value=5,
        value=DEFAULT_EVENT_MAX_COUNT,
        step=1,
        help="동시에 활성화될 수 있는 이벤트의 최대 개수입니다. 초과 시 가장 오래된 이벤트가 사라집니다.",
    )

if st.session_state.started:
    st.caption("※ 대립유전자의 수와 시초 개체수는 시작 전에만 변경할 수 있고, 교배 참여율·사망률·번성 등은 다음 세대부터 즉시 적용됩니다.")

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
        st.session_state.active_events = []
        st.session_state.history = []
        record_history_snapshot()
        used_letters_log = ", ".join(
            f"{l}/{l.lower()}" for l in get_gene_letters(num_genes_input)
        )
        st.session_state.logs.append(
            f"[시작] 대립유전자 {num_genes_input}쌍({used_letters_log}), "
            f"시초 개체수 {initial_population_input}마리로 시뮬레이션을 시작했습니다. (1세대)"
        )

with col2:
    if st.button("다음 세대", disabled=not st.session_state.started):
        # 0. 이벤트 발생 판정
        st.session_state.active_events, triggered_event = trigger_event(
            st.session_state.active_events, event_chance_input, event_max_count_input, st.session_state.num_genes
        )
        event_log = ""
        if triggered_event == "no_available":
            event_log = "이벤트 발생을 시도했으나 모든 이벤트가 이미 활성화되어 있어 무산"
        elif triggered_event:
            event_log = f"새로운 이벤트 발생: {triggered_event['name']} ({get_event_description(triggered_event)})"

        # 활성 이벤트들의 효과 합산 (옵션값 자체는 그대로 두고, 계산에만 반영)
        (
            prosperity_bonus,
            decline_bonus,
            max_pop_mult,
            death_point_add,
            death_mult,
            climate_events,
            predator_weight_events,
            camouflage_events,
        ) = compute_event_effects(st.session_state.active_events)

        effective_prosperity = prosperity_input + prosperity_bonus
        effective_decline = decline_input + decline_bonus
        effective_max_population = max(1, round(max_population_input * max_pop_mult))

        # 오차 적용: 교배 참여율과 사망률의 기준값을 각각 무작위로 흔든 뒤, 이후 효과들을 적용
        randomized_participation_rate = apply_error_margin(reproduction_rate_input, error_margin_input)
        randomized_death_rate = apply_error_margin(death_rate_input, error_margin_input)

        effective_death_rate_percent = min(max((randomized_death_rate + death_point_add) * death_mult, 0), 100)

        # 1. 교배 진행 (오차/번성/쇠락/이벤트 반영, 자손 생성)
        mated_population, offspring_counts, num_mated, effective_rate = next_generation(
            st.session_state.population,
            randomized_participation_rate,
            st.session_state.num_genes,
            offspring_per_pair_input,
            effective_max_population,
            effective_prosperity,
            effective_decline,
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
                mutation_log = f"돌연변이 발생! {mutant_genotype} 개체 등장"
            elif st.session_state.num_genes >= MAX_GENES:
                mutation_log = "돌연변이 시도됐으나 최대 대립유전자 수에 도달하여 무산"

        # 3. 최대 개체수(이벤트 반영)를 초과하면, 초과한 수만큼 개체를 제거
        #    (포식자의 진화/위장 효과가 있으면 그 가중치가 여기에도 반영됨)
        capped_population, num_capped = apply_max_population_cap(
            mated_population, effective_max_population, predator_weight_events, camouflage_events
        )

        # 4. 사망률(이벤트 반영)만큼 개체를 제거
        #    (포식자의 진화/위장 효과가 있으면 그 가중치가 여기에도 반영됨)
        after_death_population, num_death = apply_death(
            capped_population, effective_death_rate_percent / 100, predator_weight_events, camouflage_events
        )

        # 5. 기후변화 이벤트: 특정 성질을 지니지 못한 개체에 추가 사망 판정
        final_population, num_climate_death = apply_trait_specific_death(
            after_death_population, climate_events
        )

        st.session_state.population = final_population
        st.session_state.generation += 1
        record_history_snapshot()

        cap_log = f"최대 개체수({effective_max_population}) 초과로 {num_capped}마리 사망" if num_capped > 0 else ""
        rate_log = (
            f"교배 참여율 {reproduction_rate_input}% (오차 적용 {randomized_participation_rate:.1f}% → "
            f"번성/쇠락 적용 후 {effective_rate:.1f}%) 적용"
            if abs(effective_rate - reproduction_rate_input) > 0.01
            else f"교배 참여율 {reproduction_rate_input}% 적용"
        )
        death_log = (
            f"사망률 {death_rate_input}% (오차 적용 {randomized_death_rate:.1f}% → "
            f"이벤트 적용 후 {effective_death_rate_percent:.1f}%) 적용"
            if abs(effective_death_rate_percent - death_rate_input) > 0.01
            else f"사망률 {death_rate_input}% 적용"
        )
        climate_log = f"기후변화로 추가 {num_climate_death}마리 사망" if num_climate_death > 0 else ""

        log_lines = [f"[{st.session_state.generation}세대] {rate_log}"]
        log_lines.append(f"{num_mated}마리가 교배하여 {num_offspring}마리 탄생")
        if mutation_log:
            log_lines.append(mutation_log)
        if cap_log:
            log_lines.append(cap_log)
        if event_log:
            log_lines.append(event_log)
        log_lines.append(f"{death_log} - {num_death}마리 사망")
        if climate_log:
            log_lines.append(climate_log)

        st.session_state.logs.append("  \n".join(log_lines))

with col3:
    if st.session_state.started:
        st.markdown(f"### {st.session_state.generation}세대")

st.write("")

# 가장 최근 로그를 버튼과 결과 표시 사이에 표시
if st.session_state.logs:
    st.info(st.session_state.logs[-1])

# 현재 활성화된 이벤트 표시 (사라지기 전까지 계속 표시됨)
if st.session_state.started and st.session_state.active_events:
    for event_entry in st.session_state.active_events:
        st.warning(f"⚡ **{event_entry['name']}** : {get_event_description(event_entry)}")

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
# 중간: 그래프
# ------------------------------------------------------------
st.header("📈 그래프")

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history).set_index("generation")

    st.subheader("세대별 개체수 변화")
    st.line_chart(history_df[["population"]].rename(columns={"population": "총 개체수"}))

    trait_columns = [col for col in history_df.columns if col != "population"]
    if trait_columns:
        st.subheader("세대별 대립유전자(우성) 비율 변화 (%)")
        trait_df = history_df[trait_columns].rename(columns={col: f"{col} 비율(%)" for col in trait_columns})
        st.line_chart(trait_df)
        st.caption("각 유전자의 우성 대립유전자(대문자) 비율입니다. 열성 비율은 100%에서 이 값을 뺀 값과 같습니다.")
else:
    st.write("아직 기록된 데이터가 없습니다. '시뮬레이터 시작하기' 버튼을 눌러주세요.")

st.divider()

# ------------------------------------------------------------
# 중간: 이벤트 조작 시스템
# ------------------------------------------------------------
st.header("🎛️ 이벤트 조작")
st.caption(
    "앞으로 발생할 이벤트 10개를 미리 보여줍니다. 순서를 바꾸거나(▲▼) 삭제(✕)할 수 있습니다. "
    "실제 발생 시 구체적인 수치와 대상 대립유전자는 그때 무작위로 정해집니다."
)

ensure_event_queue_filled()
queue_length = len(st.session_state.event_queue)

for i, event_name in enumerate(list(st.session_state.event_queue)):
    col_order, col_desc, col_up, col_down, col_delete = st.columns([0.6, 6, 0.7, 0.7, 0.9])

    col_order.markdown(f"**{i + 1}**")
    col_desc.markdown(f"**{event_name}** : {get_event_preview_description(event_name)}")

    if col_up.button("▲", key=f"event_queue_up_{i}", disabled=(i == 0)):
        st.session_state.event_queue[i - 1], st.session_state.event_queue[i] = (
            st.session_state.event_queue[i],
            st.session_state.event_queue[i - 1],
        )
        st.rerun()

    if col_down.button("▼", key=f"event_queue_down_{i}", disabled=(i == queue_length - 1)):
        st.session_state.event_queue[i + 1], st.session_state.event_queue[i] = (
            st.session_state.event_queue[i],
            st.session_state.event_queue[i + 1],
        )
        st.rerun()

    if col_delete.button("✕", key=f"event_queue_delete_{i}"):
        st.session_state.event_queue.pop(i)
        ensure_event_queue_filled()
        st.rerun()

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
