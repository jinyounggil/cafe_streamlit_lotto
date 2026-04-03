import streamlit as st
import random
import time
import datetime
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="Cafe Lucky Event", page_icon="🎰", layout="centered")

# 스타일 설정
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    .ball { 
        display: inline-block; width: 50px; height: 50px; line-height: 50px; 
        border-radius: 50%; text-align: center; font-weight: bold; font-size: 20px;
        margin: 5px; color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎰 Cafe Lucky Event - 행운의 추첨기")

# 배경 이미지 표시 (파일이 있을 경우)
if os.path.exists("background.png"):
    st.image("background.png", use_container_width=True)

st.write("카페 방문 고객님을 위한 특별한 추첨 이벤트!")

# 1. 번호 선택 (멀티셀렉트)
all_nums = list(range(1, 46))
selected_nums = st.multiselect("추첨기에 넣을 번호를 선택하세요 (기본: 전체)", all_nums, default=all_nums)

target_count = st.number_input("뽑을 공의 개수", min_value=1, max_value=len(selected_nums), value=min(6, len(selected_nums)))

if st.button("추첨 시작!"):
    if len(selected_nums) < target_count:
        st.error("선택된 번호보다 더 많은 수를 뽑을 수 없습니다.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        ball_display = st.empty()
        
        # 애니메이션 효과 시뮬레이션
        drawn = []
        temp_nums = list(selected_nums)
        
        for i in range(target_count):
            # 섞이는 느낌을 주기 위한 지연
            for _ in range(5):
                status_text.text(f"공을 섞는 중... {random.choice(temp_nums)}")
                time.sleep(0.1)
            
            pick = random.choice(temp_nums)
            temp_nums.remove(pick)
            drawn.append(pick)
            
            # 진행률 업데이트
            progress_bar.progress((i + 1) / target_count)
            
            # 뽑힌 공 표시
            balls_html = ""
            for n in sorted(drawn):
                color = "#fbc400" if n <= 10 else "#69c8f2" if n <= 20 else "#ff7272" if n <= 30 else "#aaaaaa" if n <= 40 else "#b0d840"
                balls_html += f'<div class="ball" style="background-color: {color};">{n}</div>'
            ball_display.markdown(balls_html, unsafe_allow_html=True)

        status_text.success(f"🎊 추첨이 완료되었습니다! (총 {target_count}개)")
        st.balloons()
        
        # 결과 저장 기록 (히스토리)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_str = ", ".join(map(str, sorted(drawn)))
        
        # 세션 스테이트를 이용한 간이 로그 표시
        if 'history' not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({"시간": now, "결과": result_str})

st.divider()
st.subheader("📜 최근 추첨 이력")

# 기존 파일(lotto_history.txt)에서 이력 불러오기 시도
if 'history' not in st.session_state:
    st.session_state.history = []
    if os.path.exists("lotto_history.txt"):
        try:
            with open("lotto_history.txt", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if "]" in line:
                        time_part, num_part = line.split("]")
                        st.session_state.history.append({
                            "시간": time_part.replace("[", ""),
                            "결과": num_part.strip()
                        })
        except:
            pass

if 'history' in st.session_state:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df.iloc[::-1], use_container_width=True) # 최신순 표시
else:
    st.write("아직 추첨 이력이 없습니다.")