import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from koreanize_matplotlib import koreanize


def source_price():
    st.title("산지별 경락가")

    # ============================================================
    # 전역 설정 (Global Settings)
    # ============================================================
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
    @st.cache_data
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
        grouped = (
            filtered.groupby('date')[['낙찰고가', '낙찰저가', '평균가']]
            .mean()
            .round(0)
            .astype(int)
        )
        return grouped

    # ---------------------------------------------------
    # 1. 산지별 어종 평균 경락가
    # ---------------------------------------------------
    st.header("1. 산지별 어종 평균 경락가")

    # 산지 목록 구성
    산지_목록_전체 = df['산지'].unique()
    산지_일반 = sorted([x for x in 산지_목록_전체 if '(원양)' not in str(x)])
    산지_원양 = sorted([x for x in 산지_목록_전체 if '(원양)' in str(x)])
    산지_목록 = 산지_일반 + 산지_원양

    선택_산지_1 = st.selectbox('산지를 선택하세요', 산지_목록)
    선택_산지_1 = st.selectbox('산지를 선택하세요', 산지_목록)

    # 선택한 산지 데이터 필터링
    filtered_df = df[df['산지'] == 선택_산지_1]
    # 선택한 산지 데이터 필터링
    filtered_df = df[df['산지'] == 선택_산지_1]

    # 시각화
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(filtered_df['파일어종'], filtered_df['평균가'],color="#f57d87")
    ax.set_xlabel('어종')
    ax.set_ylabel('평균 경락가')
    ax.set_title(f'{선택_산지_1} 산지 어종별 평균 경락가', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    # ---------------------------------------------------
    # 2. 거래량 상위 10개 품목 및 품목별 상위 5개 산지
    # ---------------------------------------------------
    st.header("2. 거래량 상위 10개 품목 및 품목별 상위 5개 산지")

    #  거래량 계산 (데이터 개수 또는 평균가 합계로 판단)
    # 방법 1: 데이터 개수 기준
    품종별_거래량 = df.groupby('어종').size().reset_index(name='거래량')
    상위_품종 = 품종별_거래량.nlargest(10, '거래량')['어종'].tolist()

    품종_목록 = sorted(상위_품종)

    # 선택 UI
    col1, col2 = st.columns(2)
    with col1:
        선택_품종 = st.selectbox('품종을 선택하세요', 품종_목록, key='품종')

    with col2:
        품종_데이터 = df[df['어종'] == 선택_품종]
        산지별_거래량 = 품종_데이터.groupby('산지').size().reset_index(name='거래량')
        상위_산지 = 산지별_거래량.nlargest(5, '거래량')['산지'].tolist()

        # (원양) 분리 및 정렬
        산지_일반_2 = sorted([x for x in 상위_산지 if '(원양)' not in str(x)])
        산지_원양_2 = sorted([x for x in 상위_산지 if '(원양)' in str(x)])
        산지_목록_2 = 산지_일반_2 + 산지_원양_2
    
        선택_산지_2 = st.selectbox(
            f'산지를 선택하세요 ({선택_품종} 거래량 상위 5개)', 
            산지_목록_2, 
            key='산지2'
        )

    # 필터링
    filtered_df_2 = df[(df['산지'] == 선택_산지_2) & (df['어종'] == 선택_품종)]
    # 필터링
    filtered_df_2 = df[(df['산지'] == 선택_산지_2) & (df['어종'] == 선택_품종)]

    # 시각화
    if len(filtered_df_2) > 0:
        monthly_avg = filtered_df_2.groupby('month')['평균가'].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(monthly_avg['month'], monthly_avg['평균가'], marker='o')
        ax.set_xlabel('월')
        ax.set_ylabel('평균 경락가')
        ax.set_title(f'{선택_산지_2} 산지의 {선택_품종} 월별 평균 경락가', fontsize=14)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("날짜 컬럼이 없거나 데이터가 유효하지 않아 월별 그래프를 그릴 수 없습니다.")
