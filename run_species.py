# ============================================================
# 🐟 수산물 경락가 통합 분석 대시보드 (Streamlit)
# ------------------------------------------------------------
# 작성 목적:
#   - 어종별 경락가 변동 추이, 파일어종별 비교, 해양데이터 연계 시각화 제공
# 개발 언어:
#   - Python (pandas, matplotlib, streamlit)
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from koreanize_matplotlib import koreanize  # 한글 폰트 깨짐 방지

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

def load_and_preprocess_data(path):
    """CSV 파일 로딩 및 전처리"""
    df = pd.read_csv(path)

    # 문자열 → 숫자 변환 및 반올림(정수)
    price_cols = ['낙찰고가', '낙찰저가', '평균가']
    for col in price_cols:
        df[col] = df[col].astype(str).str.replace(',', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round(0).astype(int)

    # 날짜 처리
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    return df


def filter_by_species(df, species_col, species_name, min_count=100):
    """특정 어종 기준 필터링 후 평균가 계산 (정수 변환)"""
    filtered = df[df[species_col] == species_name]
    if len(filtered) <= min_count:
        return None
    grouped = filtered.groupby('date')[['낙찰고가', '낙찰저가', '평균가']].mean().round(0).astype(int)
    return grouped


# ============================================================
# 가격 시각화 함수
# ============================================================

def plot_metrics(df, metrics, title, step=DATE_TICK_STEP):
    """날짜별 가격 변화를 선 그래프로 시각화"""
    if df is None or df.empty:
        st.warning("시각화할 데이터가 없습니다.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = {'평균가': 'tab:blue', '낙찰고가': 'tab:orange', '낙찰저가': 'tab:green'}

    for metric in metrics:
        if metric in df.columns:
            ax.plot(df.index, df[metric], label=metric, color=colors.get(metric),
                    marker='o', linewidth=2)

    ax.set_title(title)
    ax.set_xlabel('날짜')
    ax.set_ylabel('가격 (원)')
    ax.legend()

    # X축 날짜 간격 설정
    x_vals = list(df.index)
    step = max(1, step)
    ax.set_xticks(x_vals[::step])
    ax.set_xticklabels([x.strftime('%Y-%m') for x in x_vals[::step]], rotation=45)

    st.pyplot(fig)


# ============================================================
# 해양데이터 연계 시각화 함수
# ============================================================

def plot_ocean_metrics(merged, ocean_vars, selected_market, selected_file_species, step=DATE_TICK_STEP):
    """월별 평균가 vs 해양데이터 (이중 축 시각화)"""
    merged[['평균가'] + ocean_vars] = merged[['평균가'] + ocean_vars].round(0).astype(int)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    x_ticks = list(range(len(merged['연월'])))
    labels = merged['연월']

    # 평균가 (왼쪽 축)
    ax1.plot(x_ticks, merged['평균가'], color='tab:blue', marker='o', label='평균가')
    ax1.set_xlabel('연-월')
    ax1.set_ylabel('평균가 (원)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # X축 라벨 간격
    step = max(1, step)
    ax1.set_xticks(x_ticks[::step])
    ax1.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=45)

    # 해양데이터 (오른쪽 축)
    ax2 = ax1.twinx()
    colors = {'수온 평균': 'tab:red', '기온 평균': 'tab:orange', '풍속 평균': 'tab:green'}
    for v in ocean_vars:
        ax2.plot(x_ticks, merged[v], marker='s', linestyle='--', linewidth=2,
                 color=colors.get(v, 'gray'), label=v)
    ax2.set_ylabel('해양 데이터 지표')
    ax2.tick_params(axis='y')

    # 범례 통합
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title(f"{selected_market} / {selected_file_species} 월별 평균가 vs 해양데이터")
    fig.tight_layout()
    st.pyplot(fig)


# ============================================================
# 메인 Streamlit 앱 (이 부분은 수정 금지)
# ============================================================

def species_price():
    """
    Streamlit 기반 어종별 가격 분석 대시보드 메인 함수
    -------------------------------------------------------
    3개의 주요 섹션으로 구성:
      ① 어종별 일별 경락가 추이
      ② 어종 그룹별 낙찰가 비교
      ③ 해양데이터(수온, 기온, 풍속) 연계분석
    """
    st.title('🐟 어종별 경락가 통합 분석 대시보드')

    # 1️⃣ CSV 데이터 로드 및 전처리
    df = load_and_preprocess_data('./data/수산물_통합전처리_3컬럼.csv')

    # 2️⃣ 세션 상태 초기화
    for key in ['section1_show', 'section2_show', 'section3_show']:
        if key not in st.session_state:
            st.session_state[key] = False

    # -------------------------------------------------
    # ① 어종별 일별 경락가 변동 추이
    # -------------------------------------------------
    st.subheader("① 어종별 일별 경락가 변동 추이")
    species = st.selectbox("어종을 선택하세요", sorted(df['파일어종'].unique()))

    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.section1_show:
            if st.button("시세 보기", key="btn_show_section1"):
                st.session_state.section1_show = True
    with col2:
        if st.button("초기화", key="btn_reset_section1"):
            st.session_state.section1_show = False
            st.experimental_rerun()

    if st.session_state.section1_show:
        result = filter_by_species(df, '파일어종', species)
        if result is not None:
            st.dataframe(result.head(20))
            selected_metrics = st.multiselect(
                "보고 싶은 가격 항목 선택", ['평균가', '낙찰고가', '낙찰저가'], default=['평균가'])
            plot_metrics(result, selected_metrics, f"{species} 가격 추이")
        else:
            st.warning("해당 어종 데이터가 100개 이하입니다.")

        if st.button("닫기", key="btn_close_section1"):
            st.session_state.section1_show = False
            st.experimental_rerun()

    st.markdown("---")

    # -------------------------------------------------
    # ② 파일어종 및 세부 어종별 낙찰가 비교
    # -------------------------------------------------
    st.subheader("② 파일어종 및 하위 어종별 낙찰가 비교")
    file_species = st.selectbox(
        "파일어종을 선택하세요", sorted(df.groupby('파일어종').size()[lambda x: x > 100].index))

    col3, col4 = st.columns(2)
    with col3:
        if not st.session_state.section2_show:
            if st.button("비교 보기", key="btn_show_section2"):
                st.session_state.section2_show = True
    with col4:
        if st.button("초기화", key="btn_reset_section2"):
            st.session_state.section2_show = False
            st.experimental_rerun()

    if st.session_state.section2_show:
        subset = df[df['파일어종'] == file_species]
        valid_species = subset.groupby('어종').size()[lambda x: x > 100].index.tolist()
        species = st.selectbox("세부 어종을 선택하세요", sorted(valid_species))
        if species:
            result = filter_by_species(subset, '어종', species)
            if result is not None:
                st.dataframe(result.head(20))
                plot_metrics(result, ['평균가', '낙찰고가', '낙찰저가'], f"{species} 낙찰가 시계열")
            else:
                st.warning("데이터가 부족합니다.")
        if st.button("닫기", key="btn_close_section2"):
            st.session_state.section2_show = False
            st.experimental_rerun()

    st.markdown("---")

    # -------------------------------------------------
    # ③ 해양데이터 연계 분석
    # -------------------------------------------------
    st.subheader("③ 해양데이터 (수온 · 기온 · 풍속) 연계 분석")

    col5, col6 = st.columns(2)
    with col5:
        if not st.session_state.section3_show:
            if st.button("분석 보기", key="btn_show_section3"):
                st.session_state.section3_show = True
    with col6:
        if st.button("초기화", key="btn_reset_section3"):
            st.session_state.section3_show = False
            st.experimental_rerun()

    if st.session_state.section3_show:
        try:
            ocean_path = './data/해양정보_추출/산지별_2021_2024_해양데이터.csv'
            ocean_df = pd.read_csv(ocean_path)
            ocean_df[['year', 'month']] = ocean_df[['year', 'month']].astype(int)
        except FileNotFoundError:
            st.error("해양데이터 파일을 찾을 수 없습니다.")
            st.stop()

        market_list = sorted(ocean_df['산지'].unique())
        selected_market = st.selectbox("산지를 선택하세요", market_list)
        selected_file_species = st.selectbox("어종(파일어종)을 선택하세요", sorted(df['파일어종'].unique()))

        species_monthly = (
            df[df['파일어종'] == selected_file_species]
            .groupby(['year', 'month'])[['평균가']]
            .mean()
            .round(0)
            .reset_index()
        )

        ocean_cols = ['기온 평균', '수온 평균', '풍속 평균']
        ocean_selected = ocean_df[ocean_df['산지'] == selected_market][['year', 'month'] + ocean_cols]
        merged = pd.merge(species_monthly, ocean_selected, on=['year', 'month'], how='inner')

        if merged.empty:
            st.warning("선택한 산지와 어종의 결합 데이터가 없습니다.")
        else:
            merged['연월'] = merged['year'].astype(str) + '-' + merged['month'].astype(str).str.zfill(2)
            st.write(f"결합된 데이터 수: {len(merged)}")
            st.dataframe(merged, height=400)

            ocean_vars = st.multiselect("비교할 해양 변수 선택", ocean_cols, default=['수온 평균'])
            if not ocean_vars:
                st.warning("비교할 변수를 선택해주세요.")
            else:
                plot_ocean_metrics(merged, ocean_vars, selected_market, selected_file_species)

        if st.button("닫기", key="btn_close_section3"):
            st.session_state.section3_show = False
            st.experimental_rerun()


# ============================================================
# 실행부
# ============================================================

if __name__ == "__main__":
    species_price()
