from pathlib import Path
import streamlit as st
import app_llm
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from koreanize_matplotlib import koreanize
import datetime
from matplotlib import font_manager
import matplotlib as mpl



# ============================================================
# 전역 설정
# ============================================================
def configure_matplotlib_font():
    candidates = [
        # ✅ 레포에 폰트 포함한 경우(가장 추천)
        Path(__file__).resolve().parent / "assets" / "fonts" / "NanumGothic.ttf",
        # ✅ 리눅스에 패키지로 설치된 경우(packages.txt)
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        # ✅ Ubuntu/Debian 시스템 폰트
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf"),
    ]

    font_loaded = False
    for p in candidates:
        try:
            if p.exists():
                font_manager.fontManager.addfont(str(p))
                font_name = font_manager.FontProperties(fname=str(p)).get_name()
                mpl.rcParams["font.family"] = font_name
                mpl.rcParams["axes.unicode_minus"] = False
                font_loaded = True
                break
        except Exception as e:
            continue

    # ✅ 폰트가 없더라도 앱이 죽지 않게 fallback
    if not font_loaded:
        try:
            mpl.rcParams["font.family"] = "DejaVu Sans"
        except:
            pass
    
    mpl.rcParams["axes.unicode_minus"] = False

configure_matplotlib_font()

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
    # ============================================================
    # 메인 헤더 - 파도 패턴 배경
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 60px 40px; border-radius: 20px; margin-bottom: 40px;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
                position: relative; overflow: hidden;'>
        <!-- 파도 패턴 SVG -->
        <svg style='position: absolute; bottom: 0; left: 0; width: 100%; height: 100px; opacity: 0.3;' 
            xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
            <path fill="#ffffff" fill-opacity="1" 
                d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z">
            </path>
        </svg>
        <svg style='position: absolute; bottom: -20px; left: 0; width: 100%; height: 120px; opacity: 0.2;' 
            xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
            <path fill="#ffffff" fill-opacity="1" 
                d="M0,192L48,197.3C96,203,192,213,288,192C384,171,480,117,576,112C672,107,768,149,864,154.7C960,160,1056,128,1152,133.3C1248,139,1344,181,1392,202.7L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z">
            </path>
        </svg>
        <div style='text-align: center; position: relative; z-index: 1;'>
            <h1 style='color: white; margin: 0; font-size: 3.9em; font-weight: 800; 
                    letter-spacing: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                호갱제로
            </h1>
            <div style=
                        border-radius: 2px; opacity: 0.8;'></div>
            <p style='color: rgba(255,255,255,0.95); font-size: 1.4em; margin: 10px 0 0 0;
                    font-weight: 500; letter-spacing: 2.5px;'>
                투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 주요 기능 안내 카드
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2em;">어종별 실시간 시세</h3>
            <p style="color: #666; margin-top: 10px; font-size: 0.9em; line-height: 1.5;">
            활어·냉동·선어 상태별<br/>
            가격 비교로 최적 구매시기 파악
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2em;">산지별 가격 비교</h3>
            <p style="color: #666; margin-top: 10px; font-size: 0.9em; line-height: 1.5;">
            전국 산지 간 가격 차이로<br/>
            합리적인 거래처 선정 지원
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2em;">AI 가격 예측</h3>
            <p style="color: #666; margin-top: 10px; font-size: 0.9em; line-height: 1.5;">
            머신러닝 기반 미래 시세 예측과<br/>
            24시간 실시간 상담 서비스
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 사용 방법 안내 (접을 수 있는 형태)
    with st.expander("💡 호갱제로 사용 가이드"):
        st.markdown("""
        ###  이렇게 활용하세요
        ####
        
        **1️⃣ 어종별 시세 분석**
        - 관심 어종을 선택하여 일별 가격 변동 추이를 확인할 수 있습니다.
        - 평균가, 최고가, 최저가를 비교하여 거래 시기를 결정해 보세요.
        - 품종 및 상태별(활어/냉동/선어) 가격 차이 분석이 가능합니다.
        
        **2️⃣ 산지별 시세 비교**
        - 특정 산지의 전체 어종 평균 가격 조회 할 수 있습니다.
        - 거래량 Top 10 어종의 산지별 가격을 알아볼 수 있습니다.
        - 월별 가격 추이를 확인하여 최적의 거래처를 선정해보세요.
        
        **3️⃣ AI 챗봇 활용**
        - Google API 기반 실시간 시세 조회를 이용해 보세요.
        - RAG 기반 챗봇을 통해 저희 호갱제로 사용법을 쉽게 알아보세요.
        - 24시간 언제든지 궁금한 사항 문의해주세요.
        
        **4️⃣ 제철 어종 확인**
        - 월별 가격이 가장 저렴한 제철 어종을 추천해드립니다.
        - 계절별 최적의 구매 시기를 파악해 보세요.
        
        ---
        
         **데이터 출처**: 수산물유통정보시스템(FIPS) | 해양환경정보시스템  
         **사용된 데이터 기간**: 2021년 ~ 2024년
        """)
    
    st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 데이터 로드
    df = load_data()
    if df is None:
        st.error("데이터를 불러올 수 없습니다.")
        return
    
    # ============================================================
    # AI 챗봇 섹션 - 통일된 헤더 스타일
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 16px; border-radius: 40px; margin-bottom: 40px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                width: 600px; 
                margin-left: auto; margin-right: auto;'>
        <h2 style='color: #2c3e50; margin: 0; font-size: 2.2em;
                font-weight: 900; text-align: center;'>
            AI 안내 챗봇
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col_chat1, col_chat2 = st.columns([0.01, 0.99])  # 0 대신 아주 작은 양수를 줌

    col_chat2 = st.columns(1)[0]  # 단일 컬럼 생성 후 사용

    with col_chat2:
        st.markdown("""
        <div style='background: white; padding: 20px; border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                    border-left: 4px solid #764ba2;
                    width: 100%; max-width: 700px; margin: auto; height: 24vh; max-height: 184px;'>
            <h3 style='color: #764ba2; margin: 0 0 10px 0; font-size: 1.1em; font-weight: 600;'>
                호갱제로 안내 상담  Chatbot
            </h3>
            <p style='color: #666; font-size: 0.85em; line-height: 1.5; margin-bottom: 12px;'>
                이용 중 모르시는 부분은 챗봇에게 물어보세요!
            </p>
        </div>
        """, unsafe_allow_html=True)

        app_llm.rag_llm_inner_ui()

        # rag_llm_inner_ui 위치 변경 css
        st.markdown("""
        <style>
            .stVerticalBlock{
                    position: relative;
                    }
            .st-key-rag_question{
                    position: absolute;
                    top: 7.4rem;
                    width: calc(100% - 40px);
                    max-width: 660px;
                    transform: translateX(-50%);
                    left: 50%;
                    }
            .stTextInput > label{
                    display: none;
                    }
            

        </style>
        """, unsafe_allow_html=True)
    st.markdown('---')
    
    # ============================================================
    # 1. KPI 카드 섹션 - 통일된 헤더 + 가로형 카드
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 16px; border-radius: 40px; margin-bottom: 40px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                width: 600px; 
                margin-left: auto; margin-right: auto;'>
        <h2 style='color: #2c3e50; margin: 0; font-size: 2.2em;
                font-weight: 900; text-align: center;'>
            주요 지표
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI 계산
    today = df['date'].max()
    today_data = df[df['date'] == today]
    
    total_species = df['파일어종'].nunique()
    total_sources = df['산지'].nunique()
    
    # KPI 카드 2개 - 가로형 디자인
    col_space1, col1, col2, col_space2 = st.columns([0.5, 2, 2, 0.5])
    
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px 30px; border-radius: 15px; 
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);
                    display: flex; justify-content: space-between; align-items: center;'>
            <div style='text-align: left;'>
                <p style='color: rgba(255,255,255,0.9); font-size: 1.1em; 
                        margin: 0; font-weight: 500;'>등록 어종</p>
                <p style='color: rgba(255,255,255,0.7); font-size: 0.9em; margin: 5px 0 0 0;'>
                    등록된 전체 어종 수
                </p>
            </div>
            <div style='text-align: right;'>
                <h2 style='color: white; margin: 0; font-size: 2.8em; font-weight: 700;'>
                    {total_species:,}
                </h2>
                <p style='color: rgba(255,255,255,0.8); font-size: 1em; margin: 5px 0 0 0;'>종</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px 30px; border-radius: 15px; 
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);
                    display: flex; justify-content: space-between; align-items: center;'>
            <div style='text-align: left;'>
                <p style='color: rgba(255,255,255,0.9); font-size: 1.1em; 
                        margin: 0; font-weight: 500;'>거래 산지</p>
                <p style='color: rgba(255,255,255,0.7); font-size: 0.9em; margin: 5px 0 0 0;'>
                    전국 거래 산지 수
                </p>
            </div>
            <div style='text-align: right;'>
                <h2 style='color: white; margin: 0; font-size: 2.8em; font-weight: 700;'>
                    {total_sources:,}
                </h2>
                <p style='color: rgba(255,255,255,0.8); font-size: 1em; margin: 5px 0 0 0;'>곳</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # 2. 오늘의 시세 - 통일된 헤더
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 16px; border-radius: 40px; margin-bottom: 40px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                width: 600px; 
                margin-left: auto; margin-right: auto;'>
        <h2 style='color: #2c3e50; margin: 0; font-size: 2.2em;
                font-weight: 900; text-align: center;'>
            최근 가격 추이
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 최근 7일간 거래량이 많은 어종 추출
    recent_7days = df[df['date'] >= (today - pd.Timedelta(days=7))]
    top_species = recent_7days['파일어종'].value_counts().head(6).index.tolist()
    last_30days = df[df['date'] >= (today - pd.Timedelta(days=30))]
    
    # 2x3 그리드
    cols = st.columns(3)
    
    for idx, species in enumerate(top_species):
        species_data = last_30days[last_30days['파일어종'] == species].groupby('date')['평균가'].mean().reset_index()
        
        if len(species_data) > 0:
            col_idx = idx % 3
            
            with cols[col_idx]:
                # 미니 차트 생성
                fig, ax = plt.subplots(figsize=(4, 2.8))
                
                ax.plot(species_data['date'], species_data['평균가'], 
                    color='#667eea', linewidth=3, marker='o', markersize=4)
                ax.fill_between(species_data['date'], species_data['평균가'], 
                            alpha=0.2, color='#667eea')
                
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.set_title(f'{species}', fontsize=15, fontweight='bold', 
                        pad=12, color='#2c3e50')
                ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
                ax.tick_params(axis='x', rotation=45, labelsize=9)
                ax.tick_params(axis='y', labelsize=10)
                
                ax.set_facecolor('#f8f9fa')
                fig.patch.set_facecolor('white')
                
                # 최신 가격 표시
                if len(species_data) > 0:
                    latest_price = species_data.iloc[-1]['평균가']
                    
                    if len(species_data) > 1:
                        prev_price = species_data.iloc[-2]['평균가']
                        change_pct = ((latest_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                        change_color = '#e74c3c' if change_pct > 0 else '#2ecc71' if change_pct < 0 else '#95a5a6'
                        change_symbol = '▲' if change_pct > 0 else '▼' if change_pct < 0 else '—'
                    else:
                        change_pct = 0
                        change_color = '#95a5a6'
                        change_symbol = '—'
                    
                    ax.text(0.98, 0.98, f'{latest_price:,.0f}원', 
                        transform=ax.transAxes, fontsize=14, fontweight='bold',
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round,pad=0.6', facecolor='white', 
                                edgecolor='#667eea', linewidth=2.5, alpha=0.95))
                    
                    ax.text(0.02, 0.98, f'{change_symbol} {abs(change_pct):.1f}%', 
                        transform=ax.transAxes, fontsize=11, fontweight='bold',
                        verticalalignment='top', horizontalalignment='left',
                        color=change_color,
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                                edgecolor=change_color, linewidth=2, alpha=0.9))
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
                
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # 3. 제철 어종 - 통일된 헤더
    # ============================================================
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 16px; border-radius: 40px; margin-bottom: 40px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                width: 600px; 
                margin-left: auto; margin-right: auto;'>
        <h2 style='color: #2c3e50; margin: 0; font-size: 2.2em;
                   font-weight: 900; text-align: center;'>
            제철 어종 추천
        </h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 30px;
                background: #f8f9fa; padding: 15px; border-radius: 10px;'>
        <p style='margin: 0; font-size: 1.05em; line-height: 1.6;'>
            현재 시점을 기준으로 저번 달, 이번 달, 다음 달의 제철 어종을 추천합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 월별 계산
    today_dt = datetime.datetime.today()
    this_month = today_dt.month
    prev_month = 12 if this_month == 1 else this_month - 1
    next_month = 1 if this_month == 12 else this_month + 1
    target_months = [prev_month, this_month, next_month]

    months_korean = {
        1:'1월', 2:'2월', 3:'3월', 4:'4월', 5:'5월', 6:'6월',
        7:'7월', 8:'8월', 9:'9월', 10:'10월', 11:'11월', 12:'12월'
    }

    # 어종별 최저가 기준 제철 판단
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

    # 월별 추천 카드 표시
    cols = st.columns(3)

    for i, month in enumerate(target_months):
        with cols[i]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 18px 0; border-radius: 12px; margin-bottom: 15px;
                        text-align: center; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);'>
                <h4 style='color: white; margin: 0; font-size: 1.4em; font-weight: 600;
                           text-align: center;'>
                    {months_korean[month]}
                </h4>
            </div>
            """, unsafe_allow_html=True)

            month_species = seasonal_df[seasonal_df['best_month'] == month].sort_values('avg_price').head(6)

            if len(month_species) > 0:
                for _, row in month_species.iterrows():
                    st.markdown(f"""
                    <div style='background: white;
                                padding: 16px 22px; margin: 8px 0;
                                border-radius: 10px; border-left: 4px solid #667eea;
                                box-shadow: 0 2px 6px rgba(0,0,0,0.06);
                                display: flex; justify-content: space-between;
                                align-items: center;'>
                        <span style='font-size: 1em; color: #2c3e50; font-weight: 500;'>
                            {row['species']}
                        </span>
                        <span style='font-size: 1.05em; font-weight: 700; color: #667eea;'>
                            {row['avg_price']:,.0f}원
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background: #f8f9fa; padding: 15px;
                            border-radius: 10px; text-align: center;
                            color: #999; font-size: 0.95em;'>
                    추천 어종이 없습니다.
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ============================================================
    # 4. 푸터
    # ============================================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #999; padding: 30px 0;
                background: #f8f9fa; border-radius: 10px; margin-top: 40px;'>
        <p style='margin: 0; font-size: 0.95em;'>
            데이터 출처:수산물유통정보시스템(FIPS) | 해양환경정보시스템<br>
                        노량진수산물도매시장  | 통계자료
        </p>
        <p style='margin: 10px 0 0 0; font-size: 0.85em; color: #bbb;'>
            © 2025 호갱제로 - 투명한 수산 시장을 위한 AI 솔루션
        </p>
    </div>
    """, unsafe_allow_html=True)