# 원자번호 1~20까지의 원자를 다루는 Python 기반 원자 결합 시뮬레이터

from collections import Counter

# 간단한 원자 정보와 결합 규칙 정의
atoms = {
    'H': {'name': 'Hydrogen', 'valence': 1},
    'He': {'name': 'Helium', 'valence': 0},
    'Li': {'name': 'Lithium', 'valence': 1},
    'Be': {'name': 'Beryllium', 'valence': 2},
    'B': {'name': 'Boron', 'valence': 3},
    'C': {'name': 'Carbon', 'valence': 4},
    'N': {'name': 'Nitrogen', 'valence': 3},
    'O': {'name': 'Oxygen', 'valence': 2},
    'F': {'name': 'Fluorine', 'valence': 1},
    'Ne': {'name': 'Neon', 'valence': 0},
    'Na': {'name': 'Sodium', 'valence': 1},
    'Mg': {'name': 'Magnesium', 'valence': 2},
    'Al': {'name': 'Aluminum', 'valence': 3},
    'Si': {'name': 'Silicon', 'valence': 4},
    'P': {'name': 'Phosphorus', 'valence': 3},
    'S': {'name': 'Sulfur', 'valence': 2},
    'Cl': {'name': 'Chlorine', 'valence': 1},
    'Ar': {'name': 'Argon', 'valence': 0},
    'K': {'name': 'Potassium', 'valence': 1},
    'Ca': {'name': 'Calcium', 'valence': 2},
}

# 예시로 정의된 결합 가능 분자 목록
molecule_library = {
    frozenset({'H': 2, 'O': 1}.items()): {
        'name': 'Water (H2O)',
        'bond_type': 'Covalent',
        'properties': 'Polar molecule, essential for life.',
        'visual': 'H-O-H'
    },
    frozenset({'Na': 1, 'Cl': 1}.items()): {
        'name': 'Sodium Chloride (NaCl)',
        'bond_type': 'Ionic',
        'properties': 'Table salt, crystalline solid.',
        'visual': 'Na+ Cl-'
    },
    frozenset({'C': 1, 'O': 2}.items()): {
        'name': 'Carbon Dioxide (CO2)',
        'bond_type': 'Double Covalent',
        'properties': 'Colorless gas, greenhouse effect.',
        'visual': 'O=C=O'
    },
}

def get_molecule_info(selected_atoms):
    atom_counts = Counter(selected_atoms)
    key = frozenset(atom_counts.items())
    return molecule_library.get(key, None)

# 사용 예시
if __name__ == '__main__':
    print("원자를 선택하세요 (예: H H O):")
    user_input = input().split()
    result = get_molecule_info(user_input)

    if result:
        print("\n[결합 결과]")
        print(f"분자: {result['name']}")
        print(f"결합 종류: {result['bond_type']}")
        print(f"특성: {result['properties']}")
        print(f"형태: {result['visual']}")
    else:
        print("\n이 조합은 아직 지원되지 않거나 결합할 수 없습니다.")
