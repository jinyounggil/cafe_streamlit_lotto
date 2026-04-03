# v1.0.1 - 오류 수정 및 이력 로직 개선 반영
import streamlit as st
import random
import time
import datetime
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="Cafe Lucky Event", page_icon="🎰", layout="centered")

# 파일 경로 설정 (현재 스크립트 위치 기준)
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "lotto_history.txt")
def get_history_file_path():
    # 실행 파일명에 상관없이 같은 폴더의 lotto_history.txt를 참조하도록 합니다.
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "lotto_history.txt")

HISTORY_FILE = get_history_file_path()

def get_ball_color(n):
    """번호에 따른 로또 공 색상을 반환합니다."""
    if n <= 10: return "#fbc400"  # 노란색
    if n <= 20: return "#69c8f2"  # 파란색
    if n <= 30: return "#ff7272"  # 빨간색
    if n <= 40: return "#aaaaaa"  # 회색
    return "#b0d840"              # 초록색

def load_history():
    """파일에서 추첨 이력을 불러와 리스트로 반환합니다."""
    history = []
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and "]" in line and "[" in line:
                        time_part, num_part = line.split("]", 1)
                        history.append({
                            "시간": time_part.replace("[", "").strip(),
                            "결과": num_part.strip()
                        })
        except Exception as e:
            st.error(f"이력을 불러오는 중 오류 발생: {e}")
    return history

def save_history_item(time_str, result_str):
    """새로운 추첨 결과를 파일에 추가합니다."""
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time_str}] {result_str}\n")
    except (OSError, IOError) as e:
        st.error(f"기록 저장 중 오류 발생: {e}")

def clear_history():
    """이력 파일과 세션 스테이트를 초기화합니다."""
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0: # 파일이 존재하고 내용이 있을 때만 삭제
        os.remove(HISTORY_FILE) # 파일 삭제
    if 'history' in st.session_state:
        del st.session_state['history'] # 세션 스테이트에서 history 키 삭제
    st.session_state['show_clear_success'] = True # 성공 메시지 표시 플래그 설정
    st.rerun()

# 세션 스테이트 초기화 및 기존 이력 로드
if 'history' not in st.session_state:
    st.session_state.history = load_history()

# 스타일 설정
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    .ball { 
        display: inline-flex; justify-content: center; align-items: center; width: 50px; height: 50px; 
        border-radius: 50%; text-align: center; font-weight: bold; font-size: 20px;
        margin: 5px; color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; white-space: nowrap; font-size: 1.2rem; margin-bottom: 20px;'>🎰 Cafe Lucky Event - 행운의 추첨기</h2>", unsafe_allow_html=True)

# 이력 초기화 성공 메시지 표시
if 'show_clear_success' in st.session_state and st.session_state['show_clear_success']:
    st.success("✅ 추첨 이력이 성공적으로 초기화되었습니다!")
    st.toast("✅ 이력이 성공적으로 초기화되었습니다.")
    del st.session_state['show_clear_success']

# 배경 이미지 표시 (파일이 있을 경우)
if os.path.exists("background.png"):
    st.image("background.png", use_container_width=True)

st.write("카페 방문 고객님을 위한 특별한 추첨 이벤트!")

# 1. 번호 선택 (멀티셀렉트)
all_nums = list(range(1, 46))
selected_nums = st.multiselect("추첨기에 넣을 번호를 선택하세요 (기본: 전체)", all_nums, default=all_nums)

if not selected_nums:
    st.warning("⚠️ 추첨을 위해 번호를 하나 이상 선택해 주세요.")
else:
    # 선택된 번호의 개수에 맞춰 안전하게 입력 범위를 설정합니다.
    # min_value가 1이므로, value와 max_value가 1보다 작아지지 않도록 보장하여 오류를 방지합니다.
    num_selected = len(selected_nums)
    safe_max = max(1, num_selected)
    safe_value = max(1, min(6, num_selected))
    
    target_count = st.number_input("뽑을 공의 개수", min_value=1, max_value=safe_max, value=safe_value)

    if st.button("추첨 시작!"):
        with st.status("행운의 공을 섞는 중...", expanded=True) as status:
            progress_bar = st.progress(0)
            ball_display = st.empty()
            
            drawn = []
            temp_nums = list(selected_nums)
            
            for i in range(target_count):
                # 섞이는 느낌 시뮬레이션
                for _ in range(5):
                    time.sleep(0.05)
                
                pick = random.choice(temp_nums)
                temp_nums.remove(pick)
                drawn.append(pick)
                
                progress_bar.progress((i + 1) / target_count)
                
                balls_html = '<div style="display: flex; flex-wrap: wrap; justify-content: center;">'
                for n in sorted(drawn):
                    balls_html += f'<div class="ball" style="background-color: {get_ball_color(n)};">{n}</div>'
                balls_html += '</div>'
                ball_display.markdown(balls_html, unsafe_allow_html=True)
            
            status.update(label=f"🎊 추첨 완료! (총 {target_count}개)", state="complete", expanded=False)
            
        st.balloons()
        
        # 결과 저장 기록 (히스토리)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_str = ", ".join(map(str, sorted(drawn)))
        
        st.session_state.history.append({"시간": now, "결과": result_str})
        save_history_item(now, result_str)

st.divider()

col_header, col_btn = st.columns([2, 1], vertical_alignment="bottom")
with col_header:
    st.markdown("<h3 style='margin:0; padding-bottom:5px;'>📜 최근 추첨 이력</h3>", unsafe_allow_html=True)
with col_btn:
    if len(st.session_state.history) > 0:
        with st.popover("🗑️ 이력 초기화", use_container_width=True):
            st.write("저장된 모든 추첨 기록을 삭제하시겠습니까?")
            if st.button("🔥 전체 삭제 실행", type="primary", use_container_width=True):
                clear_history()

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    # 이력 테이블과 통계를 탭으로 분리
    tab1, tab2 = st.tabs(["📋 추첨 기록", "📊 출현 빈도 통계"])
    
    with tab1:
        st.dataframe(df.iloc[::-1], use_container_width=True)
        
    with tab2:
        # 모든 결과 숫자를 하나의 리스트로 통합
        all_numbers = []
        for res in df["결과"]:
            all_numbers.extend([int(n.strip()) for n in res.split(",")])
        
        if all_numbers:
            counts = pd.Series(all_numbers).value_counts().sort_index()
            st.bar_chart(counts)
            st.caption("현재까지 저장된 이력을 바탕으로 계산된 번호별 노출 횟수입니다.")

    # CSV 다운로드 기능
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("이력 다운로드 (CSV)", data=csv, file_name="lotto_history.csv", mime="text/csv")
else:
    st.write("아직 추첨 이력이 없습니다.")