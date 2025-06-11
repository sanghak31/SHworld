import streamlit as st
import folium
from streamlit_folium import st_folium

# 주요 여행지 데이터
travel_data = [
    {
        "city": "New York City",
        "location": [40.7128, -74.0060],
        "description": "🗽 뉴욕은 타임스퀘어, 센트럴 파크, 브로드웨이, 메트로폴리탄 미술관 등 세계적으로 유명한 명소가 많은 도시입니다."
    },
    {
        "city": "San Francisco",
        "location": [37.7749, -122.4194],
        "description": "🌉 샌프란시스코는 금문교, 알카트라즈 섬, 피셔맨스 워프로 유명하며, 힙하고 자유로운 분위기가 특징입니다."
    },
    {
        "city": "Las Vegas",
        "location": [36.1699, -115.1398],
        "description": "🎰 라스베이거스는 카지노, 공연, 고급 호텔로 유명한 엔터테인먼트 도시입니다."
    },
    {
        "city": "Chicago",
        "location": [41.8781, -87.6298],
        "description": "🌆 시카고는 밀레니엄 파크, 시카고 강 유람선, 건축 투어 등으로 유명합니다."
    },
    {
        "city": "Miami",
        "location": [25.7617, -80.1918],
        "description": "🏖️ 마이애미는 해변, 아트 데코 지구, 라틴 문화가 살아있는 도시입니다."
    }
]

# Streamlit 앱 UI
st.set_page_config(page_title="미국 여행 가이드", layout="wide")
st.title("🇺🇸 미국 여행지 가이드")
st.markdown("아래 지도에서 미국 주요 여행지를 선택하면 자세한 설명을 확인할 수 있습니다.")

# Folium 지도 생성
map_center = [39.8283, -98.5795]  # 미국 중심 좌표
folium_map = folium.Map(location=map_center, zoom_start=4)

# 마커 추가 및 마커 클릭 시 정보 제공
for place in travel_data:
    folium.Marker(
        location=place["location"],
        popup=folium.Popup(f"<b>{place['city']}</b><br>{place['description']}", max_width=300),
        tooltip=place["city"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(folium_map)

# 지도 출력
st_folium(folium_map, width=800, height=500)

# 선택된 도시 정보 출력
st.subheader("📝 주요 여행지 요약")
for place in travel_data:
    with st.expander(place["city"]):
        st.write(place["description"])
