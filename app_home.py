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

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from koreanize_matplotlib import koreanize
import datetime

# ============================================================
# 전역 설정
# ============================================================
try:
    font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    font_name = font_manager.FontProperties(fname=font_path).get_name()
except:
    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')
koreanize()

# ============================================================
# 데이터 로딩
# ============================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/수산물_통합전처리_3컬럼.csv')
        price_cols = ['낙찰고가', '낙찰저가', '평균가']
        for col in price_cols:
            df[col] = df[col].astype(str).str.replace(',', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round(0).astype(int)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

# ============================================================
# 메인 홈 화면
# ============================================================
def run_home():
    # 헤더 섹션
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #667eea; margin: 0; font-size: 80px;'>호갱제로</h1>
        <p style='color: #666; font-size: 25px; margin-top: 21px;'>
            투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 데이터 로드
    df = load_data()
    if df is None:
        st.error("데이터를 불러올 수 없습니다.")
        return
    
    # ============================================================
    # 1. KPI 카드 섹션
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 10px 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h3 style='color: white; margin: 0;'> 주요 지표</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI 계산
    today = df['date'].max()
    today_data = df[df['date'] == today]
    yesterday = today - pd.Timedelta(days=1)
    yesterday_data = df[df['date'] == yesterday]
    
    total_species = df['파일어종'].nunique()
    total_sources = df['산지'].nunique()
    avg_price_today = today_data['평균가'].mean()
    avg_price_yesterday = yesterday_data['평균가'].mean() if len(yesterday_data) > 0 else avg_price_today
    price_change = ((avg_price_today - avg_price_yesterday) / avg_price_yesterday * 100) if avg_price_yesterday > 0 else 0
    
    # 거래량 (데이터 건수로 대체)
    today_trades = len(today_data)
    
    # KPI 카드 4개 - 균일한 크기
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; height: 100px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <p style='color: #667eea; font-size: 24px; margin: 0 0 1px 0;'>등록 어종</p>
            <h2 style='color: #333; margin: 0; font-size: 36px;'>{total_species:,} <span style='font-size: 16px; color: #999;'>종</span></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 25px; border-radius: 10px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; height: 100px;
                    display: flex; flex-direction: column; justify-content: center;'>
            <p style='color: #764ba2; font-size: 24px; margin: 0 0 1px 0;'>거래 산지</p>
            <h2 style='color: #333; margin: 0; font-size: 36px;'>{total_sources:,} <span style='font-size: 16px; color: #999;'>곳</span></h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # 2. 오늘의 시세 (인기 어종 Top 6) - 깔끔한 카드형
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 10px 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h3 style='color: white; margin: 0;'> 오늘의 시세 (인기 어종 6종)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 최근 7일간 거래량이 많은 어종 추출 (6개로 줄임)
    recent_7days = df[df['date'] >= (today - pd.Timedelta(days=7))]
    top_species = recent_7days['파일어종'].value_counts().head(6).index.tolist()
    
    # 상위 어종의 최근 30일 추이를 카드형으로 표시
    last_30days = df[df['date'] >= (today - pd.Timedelta(days=30))]
    
    # 2x3 그리드로 변경
    cols = st.columns(3)
    
    for idx, species in enumerate(top_species):
        species_data = last_30days[last_30days['파일어종'] == species].groupby('date')['평균가'].mean().reset_index()
        
        if len(species_data) > 0:
            col_idx = idx % 3
            
            with cols[col_idx]:
                # 미니 차트 생성
                fig, ax = plt.subplots(figsize=(4, 2.5))
                
                # 라인 차트 - 심플하게
                ax.plot(species_data['date'], species_data['평균가'], 
                    color='#667eea', linewidth=2.5, marker='o', markersize=3)
                ax.fill_between(species_data['date'], species_data['평균가'], 
                            alpha=0.2, color='#667eea')
                
                # 축 레이블 제거, 테두리만 유지
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.set_title(f'{species}', fontsize=14, fontweight='bold', pad=10, color='#333')
                ax.grid(True, alpha=0.2, linestyle='--')
                ax.tick_params(axis='x', rotation=45, labelsize=8)
                ax.tick_params(axis='y', labelsize=9)
                
                # 배경색 설정
                ax.set_facecolor('#f8f9fa')
                fig.patch.set_facecolor('white')
                
                # 최신 가격을 큰 글씨로 표시
                if len(species_data) > 0:
                    latest_price = species_data.iloc[-1]['평균가']
                    
                    # 가격 변동 계산
                    if len(species_data) > 1:
                        prev_price = species_data.iloc[-2]['평균가']
                        change_pct = ((latest_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                        change_color = '#e74c3c' if change_pct > 0 else '#2ecc71' if change_pct < 0 else '#95a5a6'
                        change_symbol = '▲' if change_pct > 0 else '▼' if change_pct < 0 else '—'
                    else:
                        change_pct = 0
                        change_color = '#95a5a6'
                        change_symbol = '—'
                    
                    # 텍스트 박스로 가격 표시
                    ax.text(0.98, 0.98, f'{latest_price:,.0f}원', 
                        transform=ax.transAxes, fontsize=13, fontweight='bold',
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                                edgecolor='#667eea', linewidth=2, alpha=0.95))
                    
                    # 변동률 표시
                    ax.text(0.02, 0.98, f'{change_symbol} {abs(change_pct):.1f}%', 
                        transform=ax.transAxes, fontsize=10, fontweight='bold',
                        verticalalignment='top', horizontalalignment='left',
                        color=change_color,
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                                edgecolor=change_color, linewidth=1.5, alpha=0.9))
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
        # ============================================================
    # 3. 제철 어종 (이번달 / 저번달 / 다음달 기준)
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 12px 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h3 style='color: white; margin: 0;'>제철 어종 추천!</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 25px;'>
        <p style='margin: 0; font-size: 14px;'>현재 시점을 기준으로 저번 달, 이번 달, 다음 달의 제철 어종을 추천합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # ======= 이번 달 / 저번 달 / 다음 달 계산 =======
    today = datetime.datetime.today()
    this_month = today.month
    prev_month = 12 if this_month == 1 else this_month - 1
    next_month = 1 if this_month == 12 else this_month + 1
    target_months = [prev_month, this_month, next_month]

    months_korean = {
        1:'1월', 2:'2월', 3:'3월', 4:'4월', 5:'5월', 6:'6월',
        7:'7월', 8:'8월', 9:'9월', 10:'10월', 11:'11월', 12:'12월'
    }

    # ======= 어종별 최저가 기준 제철 판단 =======
    species_list = df['파일어종'].unique()
    seasonal_data = []

    for species in species_list:
        species_df = df[df['파일어종'] == species]
        monthly_avg = species_df.groupby('month').agg({'평균가': 'mean', 'date': 'count'}).reset_index()
        monthly_avg.columns = ['month', 'avg_price', 'count']
        monthly_avg = monthly_avg[monthly_avg['count'] >= 10]
        if len(monthly_avg) > 0:
            best_month = monthly_avg.loc[monthly_avg['avg_price'].idxmin()]
            seasonal_data.append({
                'species': species,
                'best_month': int(best_month['month']),
                'avg_price': int(best_month['avg_price'])
            })

    seasonal_df = pd.DataFrame(seasonal_data)

    # ======= 월별 추천 카드 표시 =======
    cols = st.columns(3)
    gradients = {
        'winter': "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        'spring': "linear-gradient(135deg, #56ab2f 0%, #a8e063 100%)",
        'summer': "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        'fall':   "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
    }

    for i, month in enumerate(target_months):
        # 계절감에 따라 색상 설정
        if month in [12, 1, 2]:
            gradient = gradients['winter']
            border_color = "#a3b3f8"
        elif month in [3, 4, 5]:
            gradient = gradients['spring']
            border_color = "#fa73c6"
        elif month in [6, 7, 8]:
            gradient = gradients['summer']
            border_color = "#48cf36"
        else:
            gradient = gradients['fall']
            border_color = "#fcae08"

        with cols[i]:
            st.markdown(f"""
            <div style='background: {gradient};
                        padding: 10px 0; border-radius: 10px; margin-bottom: 10px;
                        text-align: center;'>
                <h4 style='color: white; margin: 0; font-size: 18px;'>{months_korean[month]}</h4>
            </div>
            """, unsafe_allow_html=True)

            month_species = seasonal_df[seasonal_df['best_month'] == month].sort_values('avg_price').head(6)

            if len(month_species) > 0:
                for _, row in month_species.iterrows():
                    st.markdown(f"""
                    <div style='background: white;
                                padding: 20px 40px; margin: 6px 0;
                                border-radius: 8px; border-left: 4px solid {border_color};
                                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                                display: flex; justify-content: space-between;
                                align-items: center; height: 45px;'>
                        <span style='font-size: 20px; color: #333;'>{row['species']}</span>
                        <span style='font-size: 20px; font-weight: bold; color: #667eea;'>{row['avg_price']:,.0f}원</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background: #f8f9fa; padding: 10px;
                            border-radius: 8px; text-align: center;
                            color: #999; font-size: 13px;'>
                    재철 어종이 없습니다!
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    
    # ============================================================
    # 4. 푸터
    # ============================================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #999; padding: 20px 0;'>
        <p style='margin: 0;'> 데이터 출처: 수산물유통정보시스템(FIPS) | 해양환경정보시스템</p>
        <p style='margin: 5px 0 0 0; font-size: 12px;'>
            © 2025 호갱제로 - 투명한 수산 시장을 위한 AI 솔루션
        </p>
    </div>
    """, unsafe_allow_html=True)




