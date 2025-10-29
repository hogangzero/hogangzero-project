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

def extract_state_and_species(species_name):
    """상태와 품종을 분리"""
    import re
    # (상태)품종 형식에서 상태와 품종을 분리
    match = re.match(r'\((활|선|냉)\)(.+)', species_name)
    if match:
        return match.group(1), match.group(2)  # 상태, 품종
    return '', species_name  # 상태 구분이 없는 경우

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
    st.header('')
    st.header('🐟 어종별 시세 분석 대시보드')
    st.header('')


    # 1️⃣ CSV 데이터 로드 및 전처리
    df = load_and_preprocess_data('./data/수산물_통합전처리_3컬럼.csv')

    # 2️⃣ 세션 상태 초기화
    for key in ['section1_show', 'section2_show', 'section3_show']:
        if key not in st.session_state:
            st.session_state[key] = False

    # -------------------------------------------------
    # ① 어종별 일별 경락가 변동 추이
    # -------------------------------------------------
    st.subheader("①  어종별 경락가 변동 ")
    species = st.selectbox(" 어종을 선택하세요 ", sorted(df['파일어종'].unique()))

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
            # 표시용 데이터프레임 생성
            display_df = result.reset_index()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.rename(columns={'date': '기준날짜'})
            # 인덱스 리셋 후 표시
            display_df = display_df.reset_index(drop=True)
            st.dataframe(display_df)
            selected_metrics = st.multiselect(
                "가격 항목을 선택하세요 ~", ['평균가', '낙찰고가', '낙찰저가'], default=['평균가'])
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
    st.subheader("② 품종 및 상태별 경락가 ")
    file_species = st.selectbox(
        "어종을 선택하세요 .", sorted(df.groupby('파일어종').size()[lambda x: x > 100].index))
    
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
        
        # 어종별로 품종과 상태 분리하여 정리하고 데이터가 100개 이상인 경우만 포함
        species_info = {}
        for species_name in subset['어종'].unique():
            state, pure_species = extract_state_and_species(species_name)
            if state:  # 상태 정보가 있는 경우
                # 해당 상태와 품종의 데이터 수 확인
                species_count = len(subset[subset['어종'] == species_name])
                if species_count >= 100:  # 데이터가 100개 이상인 경우만 저장
                    if pure_species not in species_info:
                        species_info[pure_species] = set()
                    species_info[pure_species].add(state)
        
        # 순수 품종 목록 (상태 제외)
        pure_species_list = sorted(species_info.keys())
        
        if pure_species_list:
            # compact 품종 + 상태 layout: 품종 selectbox (narrow) + 상태 radio
            col_species, col_state = st.columns([2.5, 1.5])
            with col_species:
                selected_pure_species = st.selectbox(
                    "품종 선택",
                    pure_species_list,
                    key="pure_species_select",
                    label_visibility="collapsed",
                )
            # 해당 품종의 가능한 상태 표시
            available_states = sorted(species_info[selected_pure_species])
            # 상태가 1개인 경우 바로 선택, 2개 이상인 경우만 라디오 버튼 표시
            if len(available_states) == 1:
                selected_state = available_states[0]
                st.info(f"이 품종은 '{selected_state}' 상태의 데이터만 있습니다.")
            else: 
                selected_state = st.radio( "상태를 선택하세요", available_states, horizontal=True, key="radio_state_section2")

            
            # 선택된 품종과 상태로 완성된 이름 생성
            species = f"({selected_state}){selected_pure_species}"
        else:
            st.warning("분류 가능한 품종이 없습니다.")
            st.stop()
                
        if species:
            result = filter_by_species(subset, '어종', species)
            if result is not None:
                # 표시용 데이터프레임 생성
                display_df = result.reset_index()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                display_df = display_df.rename(columns={'date': '기준날짜'})
                # 인덱스 리셋 후 표시
                display_df = display_df.reset_index(drop=True)
                st.dataframe(display_df)
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
    # 메인 설명 캡션 추가
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 14px; opacity: 0.95;">
    🌊 해양 환경 데이터(수온, 기온, 풍속)와 경매가의 상관관계를 분석하였습니다.
    </p>
    </div>
    """, unsafe_allow_html=True)

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
        # compact: market selectbox + section reset next to it, then species selectbox
        col_m, col_m_reset, col_s = st.columns([2.5, 0.8, 2.5])
        with col_m:
            selected_market = st.selectbox(
                "산지 선택",
                market_list,
                key="market_section3",
                label_visibility="collapsed",
            )
        
        with col_s:
            selected_file_species = st.selectbox(
                "어종(파일어종) 선택",
                sorted(df['파일어종'].unique()),
                key="btn_reset_section3_market",
                label_visibility="collapsed",
            )

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

            # compact ocean variable selector
            col_vars, col_vars_spacer = st.columns([2.5, 1])
            with col_vars:
                ocean_vars = st.multiselect(
                    "해양 변수",
                    ocean_cols,
                    default=['수온 평균'],
                    key="ocean_vars_select",
                    label_visibility="collapsed",
                )
            if not ocean_vars:
                st.warning("비교할 변수를 선택해주세요.")
            else:
                plot_ocean_metrics(merged, ocean_vars, selected_market, selected_file_species)

        

            st.text('데이터 출처')
            # ==================== 메트릭 카드 섹션 (맨 아래로 이동) ====================
        st.markdown("---")
        st.markdown("### 📊 주요 지표")
        
        # 계산
        avg_price = merged['평균가'].mean()
        max_price = merged['평균가'].max()
        min_price = merged['평균가'].min()
        avg_temp = merged['수온 평균'].mean()
        
        # 가격 변동성 계산
        price_volatility = (merged['평균가'].std() / avg_price * 100)
        
        # 상관계수 계산
        corr_temp = merged['평균가'].corr(merged['수온 평균'])
        corr_air = merged['평균가'].corr(merged['기온 평균'])
        corr_wind = merged['평균가'].corr(merged['풍속 평균'])
        
        # 4개 메트릭 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="평균 경매가",
                value=f"{avg_price:,.0f}원",
                delta=f"변동성 {price_volatility:.1f}%"
            )
        
        with col2:
            st.metric(
                label="가격 범위",
                value=f"{max_price:,.0f}원",
                delta=f"최저 {min_price:,.0f}원",
                delta_color="off"
            )
        
        with col3:
            st.metric(
                label="평균 수온",
                value=f"{avg_temp:.1f}°C",
                delta=f"상관계수 {corr_temp:.2f}"
            )
        
        with col4:
            # 가장 강한 상관관계 찾기
            correlations = {
                '수온': abs(corr_temp),
                '기온': abs(corr_air),
                '풍속': abs(corr_wind)
            }
            strongest = max(correlations, key=correlations.get)
            strongest_val = correlations[strongest]
            
            st.metric(
                label="주요 영향 요인",
                value=strongest,
                delta=f"상관도 {strongest_val:.2f}"
            )
        
        # ==================== 인사이트 카드 섹션 ====================
        st.markdown("### 💡 데이터 인사이트")
        
        col_i1, col_i2, col_i3 = st.columns(3)
        
        with col_i1:
            # 수온 영향 분석
            if corr_temp < -0.3:
                temp_insight = "수온이 높을수록 가격이 <b>하락</b>하는 역상관 관계"
                temp_emoji = "📉"
            elif corr_temp > 0.3:
                temp_insight = "수온이 높을수록 가격이 <b>상승</b>하는 양의 상관관계"
                temp_emoji = "📈"
            else:
                temp_insight = "수온과 가격 간 <b>약한 상관관계</b>"
                temp_emoji = "➡️"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 15px; border-radius: 10px; color: white; height: 150px;">
                <h4>{temp_emoji} 수온 영향</h4>
                <p style="font-size: 13px; line-height: 1.5;">
                {temp_insight}
                </p>
                <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                상관계수: {corr_temp:.3f}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_i2:
            # 계절별 가격 패턴
            merged['season'] = merged['month'].apply(
                lambda x: '겨울' if x in [12, 1, 2] 
                else '봄' if x in [3, 4, 5]
                else '여름' if x in [6, 7, 8]
                else '가을'
            )
            season_avg = merged.groupby('season')['평균가'].mean()
            highest_season = season_avg.idxmax()
            lowest_season = season_avg.idxmin()
            season_diff = ((season_avg.max() - season_avg.min()) / season_avg.mean() * 100)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 15px; border-radius: 10px; color: white; height: 150px;">
                <h4>🗓️ 계절별 패턴</h4>
                <p style="font-size: 13px; line-height: 1.5;">
                <b>{highest_season}</b>에 최고가<br/>
                <b>{lowest_season}</b>에 최저가 기록
                </p>
                <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                계절 간 가격차: {season_diff:.1f}%
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_i3:
            # 풍속 영향
            if abs(corr_wind) > 0.3:
                wind_impact = "높음"
                wind_color = "#e74c3c"
            elif abs(corr_wind) > 0.15:
                wind_impact = "중간"
                wind_color = "#f39c12"
            else:
                wind_impact = "낮음"
                wind_color = "#2ecc71"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 15px; border-radius: 10px; color: white; height: 150px;">
                <h4>💨 풍속 영향도</h4>
                <p style="font-size: 13px; line-height: 1.5;">
                풍속의 가격 영향력:<br/>
                <b style="color: {wind_color};">{wind_impact}</b>
                </p>
                <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                상관계수: {corr_wind:.3f}<br/>
                평균 풍속: {merged['풍속 평균'].mean():.1f}m/s
                </p>
            </div>
            """, unsafe_allow_html=True)

    if st.button("닫기", key="btn_close_section3"):
        st.session_state.section3_show = False
        st.rerun()

st.markdown("---")
st.caption("📍 데이터 출처: 수산물유통정보시스템(FIPS) | 해양환경정보시스템")


# ============================================================
# 실행부
# ============================================================

if __name__ == "__main__":
    species_price()
