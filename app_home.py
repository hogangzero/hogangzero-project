import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from koreanize_matplotlib import koreanize  # 한글 폰트 깨짐 방지
import datetime


# ============================================================
# 전역 설정(Global Settings)
# ============================================================

# 한글 폰트 설정 (OS 자동 인식)
try:
    font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # macOS
    font_name = font_manager.FontProperties(fname=font_path).get_name()
except:
    font_path = "C:/Windows/Fonts/malgun.ttf"  # Windows
    font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['legend.fontsize'] = 10
koreanize()  # 보조 폰트 지정

DATE_TICK_STEP = 3  # 날짜 라벨 표시 간격

# ============================================================
# 데이터 로딩 및 전처리 함수
# ============================================================

@st.cache_data # 캐싱 데코레이터


def load_data():

    try:
        df = pd.read_csv('data/수산물_통합전처리_3컬럼.csv')
        
        # 문자열 → 숫자 변환 및 반올림(정수)
        price_cols = ['낙찰고가', '낙찰저가', '평균가']
        for col in price_cols:
            df[col] = df[col].astype(str).str.replace(',', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round(0).astype(int)


        # 날짜 처리
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

# 데이터 로드
df = load_data()

if df is None:
    st.error("데이터를 불러올 수 없습니다. 파일 경로를 확인해주세요.")
    st.stop()


def filter_by_species(df, species_col, species_name, min_count=100):
    """특정 어종 기준 필터링 후 평균가 계산 (정수 변환)"""
    filtered = df[df[species_col] == species_name]
    if len(filtered) <= min_count:
        return None
    grouped = filtered.groupby('date')[['낙찰고가', '낙찰저가', '평균가']].mean().round(0).astype(int)
    return grouped

# ------------------------------------------------------------
# 화면 구성
"""
1. 타이틀
2. KPI 
3. 실시간 어종별 시세
4. 최근 제철 어종 (저번달, 이번달, 다음달) 
 """
#------------------------------------------------------------
def run_home():
    # 메인 설명 캡션 추가
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 14px; opacity: 0.95;">
    🐟 투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션.
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("")
    st.subheader("")
# 2. KPI ----------------------------------------------------
# 3. 시각적 차트 - 오늘의 시세(선형그래프) ---------------------
    st.subheader(" ① 오늘의 시세 ")
    
    
# 4.  최근 제철 어종 (저번달, 이번달, 다음달) ------------------
    st.subheader(" ②  제철 어종 ")





