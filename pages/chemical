import streamlit as st

# 원소 데이터 정의
elements_data = {
    '칼륨': {'reactivity': 1, 'atomic_weight': 39.1, 'charge': 1},
    '칼슘': {'reactivity': 2, 'atomic_weight': 40.1, 'charge': 2},
    '나트륨': {'reactivity': 3, 'atomic_weight': 23.0, 'charge': 1},
    '마그네슘': {'reactivity': 4, 'atomic_weight': 24.3, 'charge': 2},
    '알루미늄': {'reactivity': 5, 'atomic_weight': 27.0, 'charge': 3},
    '아연': {'reactivity': 6, 'atomic_weight': 65.4, 'charge': 2},
    '철': {'reactivity': 7, 'atomic_weight': 55.8, 'charge': 2},
    '니켈': {'reactivity': 8, 'atomic_weight': 58.7, 'charge': 2},
    '주석': {'reactivity': 9, 'atomic_weight': 118.7, 'charge': 2},
    '납': {'reactivity': 10, 'atomic_weight': 207.2, 'charge': 2},
    '수소': {'reactivity': 11, 'atomic_weight': 1.0, 'charge': 1},
    '구리': {'reactivity': 12, 'atomic_weight': 63.5, 'charge': 2},
    '수은': {'reactivity': 13, 'atomic_weight': 200.6, 'charge': 2},
    '은': {'reactivity': 14, 'atomic_weight': 107.9, 'charge': 1},
    '백금': {'reactivity': 15, 'atomic_weight': 195.1, 'charge': 2},
    '금': {'reactivity': 16, 'atomic_weight': 197.0, 'charge': 3}
}

def analyze_redox_reaction(solution_element, metal_element):
    """산화환원 반응을 분석하는 함수"""
    
    solution_data = elements_data[solution_element]
    metal_data = elements_data[metal_element]
    
    # 1. 산화환원 반응 발생 여부 확인
    reaction_occurs = metal_data['reactivity'] < solution_data['reactivity']
    
    if not reaction_occurs:
        return {
            'reaction_occurs': False,
            'cation_change': '변함 없음',
            'solution_mass_change': '변함 없음',
            'explanation': f"{metal_element}의 반응성이 {solution_element}보다 크지 않아 반응이 일어나지 않습니다."
        }
    
    # 2. 양이온 개수 변화 분석
    solution_charge = solution_data['charge']
    metal_charge = metal_data['charge']
    
    if solution_charge > metal_charge:
        cation_change = '증가'
    elif solution_charge == metal_charge:
        cation_change = '변함 없음'
    else:
        cation_change = '감소'
    
    # 3. 수용액 질량 변화 분석
    solution_weight = solution_data['atomic_weight']
    metal_weight = metal_data['atomic_weight']
    
    if solution_weight > metal_weight:
        mass_change = '감소'
    elif solution_weight == metal_weight:
        mass_change = '변함 없음'
    else:
        mass_change = '증가'
    
    # 반응식 설명
    explanation = f"""
    반응이 일어납니다:
    - {solution_element} 이온이 환원되어 {solution_element} 금속으로 석출됩니다.
    - {metal_element} 금속이 산화되어 {metal_element} 이온이 되어 수용액에 녹습니다.
    """
    
    return {
        'reaction_occurs': True,
        'cation_change': cation_change,
        'solution_mass_change': mass_change,
        'explanation': explanation
    }

def main():
    st.title("🧪 산화환원 반응 분석기")
    st.markdown("---")
    
    # 반응성 순서 표시
    st.subheader("📊 반응성 순서")
    st.write("칼륨 > 칼슘 > 나트륨 > 마그네슘 > 알루미늄 > 아연 > 철 > 니켈 > 주석 > 납 > (수소) > 구리 > 수은 > 은 > 백금 > 금")
    st.markdown("---")
    
    # 사용자 입력
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 수용액의 원소 (이온 상태)")
        solution_elements = [elem for elem in elements_data.keys() if elem != '수소']
        solution_element = st.selectbox(
            "수용액에 있는 이온을 선택하세요:",
            solution_elements
        )
    
    with col2:
        st.subheader("🔩 금속 원소 (고체 상태)")
        metal_elements = [elem for elem in elements_data.keys() if elem != '수소']
        metal_element = st.selectbox(
            "금속 원소를 선택하세요:",
            metal_elements
        )
    
    if st.button("🔍 반응 분석하기", type="primary"):
        if solution_element and metal_element:
            result = analyze_redox_reaction(solution_element, metal_element)
            
            st.markdown("---")
            st.subheader("📋 분석 결과")
            
            # 결과 표시
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="🔄 산화환원 반응 발생",
                    value="발생" if result['reaction_occurs'] else "발생하지 않음"
                )
            
            with col2:
                st.metric(
                    label="⚡ 양이온 개수",
                    value=result['cation_change']
                )
            
            with col3:
                st.metric(
                    label="⚖️ 수용액 질량",
                    value=result['solution_mass_change']
                )
            
            # 상세 설명
            st.subheader("📝 상세 설명")
            if result['reaction_occurs']:
                st.success(result['explanation'])
                
                # 추가 정보 표시
                st.info(f"""
                **반응 조건:**
                - {metal_element}의 반응성: {elements_data[metal_element]['reactivity']}
                - {solution_element} 이온의 반응성: {elements_data[solution_element]['reactivity']}
                
                **전하량 비교:**
                - {solution_element} 이온의 전하: +{elements_data[solution_element]['charge']}
                - {metal_element} 이온의 전하: +{elements_data[metal_element]['charge']}
                
                **원자량 비교:**
                - {solution_element}: {elements_data[solution_element]['atomic_weight']} g/mol
                - {metal_element}: {elements_data[metal_element]['atomic_weight']} g/mol
                """)
            else:
                st.warning(result['explanation'])
                st.info(f"""
                **반응하지 않는 이유:**
                - {metal_element}의 반응성: {elements_data[metal_element]['reactivity']}
                - {solution_element} 이온의 반응성: {elements_data[solution_element]['reactivity']}
                
                반응성이 큰 금속이 작은 금속의 이온을 환원시킬 수 있습니다.
                """)

    # 사용법 안내
    st.markdown("---")
    st.subheader("📖 사용법")
    st.write("""
    1. **수용액의 원소**: 이온 상태로 수용액에 녹아있는 원소를 선택합니다.
    2. **금속 원소**: 고체 상태의 금속 원소를 선택합니다.
    3. **분석하기 버튼**: 클릭하여 산화환원 반응을 분석합니다.
    
    **분석 항목:**
    - 🔄 **산화환원 반응 발생 여부**: 금속의 반응성이 수용액 이온보다 큰지 확인
    - ⚡ **양이온 개수 변화**: 전하량 차이에 따른 양이온 개수 변화
    - ⚖️ **수용액 질량 변화**: 원자량 차이에 따른 수용액 질량 변화
    """)

if __name__ == "__main__":
    main()
