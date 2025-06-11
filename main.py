import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import random

# 여행지 데이터
travel_data = [
    {
        "city": "New York City",
        "location": [40.7128, -74.0060],
        "description": "🗽 타임스퀘어와 센트럴파크, 브로드웨이의 도시!",
        "tips": "🚇 지하철이 발달했지만 도보로도 충분히 즐길 수 있어요!",
        "image": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Lower_Manhattan_from_Jersey_City_November_2014_panorama_3.jpg",
        "itinerary": [
            "1일차: 타임스퀘어 → 브라이언트 파크 → 브로드웨이 뮤지컬",
            "2일차: 센트럴파크 자전거 → 자연사박물관 → 루프탑 바",
            "3일차: 자유의 여신상 → 브루클린 브릿지 산책"
        ]
    },
    {
        "city": "San Francisco",
        "location": [37.7749, -122.4194],
        "description": "🌉 금문교와 히피 문화의 본고장!",
        "tips": "🚋 케이블카 타보기는 필수!",
        "image": "https://upload.wikimedia.org/wikipedia/commons/0/0c/SF_from_Twin_Peaks_December_2021_panorama_3.jpg",
        "itinerary": [
            "1일차: 금문교 → 프레시디오 공원 → 피셔맨스 워프",
            "2일차: 알카트라즈 섬 → 차이나타운 → 트윈 픽스",
            "3일차: 미션 지구 벽화 투어 → 하이트-애쉬버리"
        ]
    },
    # 추가 도시 생략 가능
]

# 페이지 설정
st.set_page_config(page_title="🎒 미국 여행 대모험!", layout="wide")
st.title("🌎 미국 여행 대모험!")
st.markdown("지도에서 도시를 클릭하거나 아래에서 도시를 골라 재미있게 여행해보세요! 🚀")

# 지도 설정
map_center = [39.8283, -98.5795]
folium_map = folium.Map(location=map_center, zoom_start=4)

for place in travel_data:
    folium.Marker(
        location=place["location"],
        tooltip=place["city"],
        popup=place["description"],
        icon=folium.Icon(color="purple", icon="star")
    ).add_to(folium_map)

st_folium(folium_map, height=500)

# 도시 선택 UI
selected_city = st.selectbox("🎯 여행지를 선택하세요!", [place["city"] for place in travel_data])

# 선택된 도시 정보 표시
city_info = next(item for item in travel_data if item["city"] == selected_city)

col1, col2 = st.columns([1, 2])
with col1:
    st.image(city_info["image"], use_column_width=True)
with col2:
    st.subheader(f"📍 {city_info['city']}")
    st.markdown(city_info["description"])
    st.markdown(f"💡 **여행 꿀팁**: {city_info['tips']}")
    st.markdown("🗓️ **추천 일정**")
    for day in city_info["itinerary"]:
        st.markdown(f"- {day}")

# --- 퀴즈 추가 ---
st.divider()
st.subheader("🧠 미국 여행 퀴즈!")

quiz = {
    "question": "자유의 여신상은 어느 도시에 있을까요?",
    "options": ["로스앤젤레스", "뉴욕", "시카고", "마이애미"],
    "answer": "뉴욕"
}

user_answer = st.radio("❓ " + quiz["question"], quiz["options"])
if user_answer:
    if user_answer == quiz["answer"]:
        st.success("정답입니다! 🎉")
    else:
        st.error("앗! 다시 생각해보세요 😅")
