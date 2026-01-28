# ============================================================
# 🐟 수산물 경매가 통합 분석 대시보드 (Streamlit)
# ------------------------------------------------------------
# 작성 목적:
#   - 어종별 경매가 변동 추이, 파일어종별 비교, 해양데이터 연계 시각화 제공
# 개발 언어:
#   - Python (pandas, matplotlib, streamlit)
# ============================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rc
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 전역 설정(Global Settings)
# ============================================================

# 한글 폰트 설정
def setup_font():
    try:
        from koreanize_matplotlib import koreanize
        koreanize()
        return
    except:
        pass
    
    mpl.rcParams["font.sans-serif"] = [
        "DejaVu Sans", "Noto Sans CJK JP", "Noto Sans CJK SC",
        "Noto Sans CJK TC", "Noto Sans CJK KR", "Arial"
    ]
    mpl.rcParams['axes.unicode_minus'] = False

setup_font()
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['legend.fontsize'] = 10

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

def plot_metrics(dfs, metrics, titles, step=DATE_TICK_STEP):
    """날짜별 가격 변화를 선 그래프로 시각화 (여러 데이터프레임 비교)"""
    if not isinstance(dfs, list):
        dfs = [dfs]
        titles = [titles]

    if any(df is None or df.empty for df in dfs):
        st.warning("시각화할 데이터가 없습니다.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = {'평균가': ['tab:blue', 'tab:red'], '낙찰고가': ['tab:orange', 'darkred'], '낙찰저가': ['tab:green', 'darkgreen']}
    line_styles = ['-', '--']  # 서로 다른 품종을 구분하기 위한 선 스타일

    # 모든 데이터프레임의 날짜 범위를 통합
    all_dates = sorted(set().union(*[df.index for df in dfs]))
    
    for df_idx, (df, title) in enumerate(zip(dfs, titles)):
        for metric in metrics:
            if metric in df.columns:
                ax.plot(df.index, df[metric], 
                       label=f"{title} - {metric}",
                       color=colors[metric][df_idx % len(colors[metric])],
                       linestyle=line_styles[df_idx % len(line_styles)],
                       marker='o' if df_idx == 0 else 's',
                       linewidth=2)

    ax.set_title("품종별 가격 비교" if len(dfs) > 1 else titles[0])
    ax.set_xlabel('날짜')
    ax.set_ylabel('가격 (원)')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # X축 날짜 간격 설정
    step = max(1, step)
    ax.set_xticks(all_dates[::step])
    ax.set_xticklabels([d.strftime('%Y-%m') for d in all_dates[::step]], rotation=45)

    plt.tight_layout()
    st.pyplot(fig)


# ============================================================
# 해양데이터 연계 시각화 함수
# ============================================================

def calculate_species_correlations(df, ocean_df, market):
    """모든 어종에 대한 환경 변수와의 상관관계 계산"""
    correlations = {}
    ocean_selected = ocean_df[ocean_df['산지'] == market]
    
    for species in df['파일어종'].unique():
        species_monthly = (
            df[df['파일어종'] == species]
            .groupby(['year', 'month'])[['평균가']]
            .mean()
            .round(0)
            .reset_index()
        )
        
        merged = pd.merge(species_monthly, ocean_selected[['year', 'month', '기온 평균', '수온 평균', '풍속 평균']], 
                         on=['year', 'month'], how='inner')
        
        if len(merged) > 0:
            correlations[species] = {
                '수온': merged['평균가'].corr(merged['수온 평균']),
                '기온': merged['평균가'].corr(merged['기온 평균']),
                '풍속': merged['평균가'].corr(merged['풍속 평균'])
            }
    
    return correlations

def get_most_affected_species(correlations):
    """각 환경 변수별로 가장 영향을 많이 받는 어종 찾기"""
    most_affected = {
        '수온': {'species': '', 'correlation': 0},
        '기온': {'species': '', 'correlation': 0},
        '풍속': {'species': '', 'correlation': 0}
    }
    
    for species, corr_values in correlations.items():
        for var in ['수온', '기온', '풍속']:
            if abs(corr_values[var]) > abs(most_affected[var]['correlation']):
                most_affected[var] = {
                    'species': species,
                    'correlation': corr_values[var]
                }
    
    return most_affected

def plot_ocean_metrics(merged, ocean_vars, selected_market, selected_file_species, step=DATE_TICK_STEP):
    """월별 평균가 vs 해양데이터 (이중 축 시각화)"""
    merged[['평균가'] + ocean_vars] = merged[['평균가'] + ocean_vars].round(0).astype(int)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    x_ticks = list(range(len(merged['연월'])))
    labels = merged['연월']

    # 평균가 (왼쪽 축)
    ax1.plot(x_ticks, merged['평균가'], color='tab:blue', marker='o', label='평균가')
    ax1.set_xlabel('연/월')
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
    ① 어종별 일별 경매가 추이
    ② 어종 그룹별 낙찰가 비교
    ③ 해양데이터(수온, 기온, 풍속) 연계분석
    """

    # ============================================================

    # 메인 타이틀과 설명
    st.markdown("""
    <div style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: 700;">
            어종별 시세 분석 대시보드
        </h1>
        <p style="color: rgba(255,255,255,0.95); margin-top: 15px; font-size: 1.15em; line-height: 0.7;">
            실시간 어종별 경매가 추이와 해양환경 데이터를 한눈에 확인하세요
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 주요 기능 안내 카드
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2em;"> 어종별 시세</h3>
            <p style="color: #666; margin-top: 10px; font-size: 0.9em; line-height: 1.5;">
            다양한 어종의 일별 경매가<br/>
            추이를 실시간으로 분석
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2em;"> 품종별 비교</h3>
            <p style="color: #666; margin-top: 10px; font-size: 0.9em; line-height: 1.5;">
            활어·냉동·선어 등<br/>
            상태별 가격 비교 분석
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); height: 150px;">
            <h3 style="color: #667eea; margin: 0; font-size: 1.2em;"> 해양데이터</h3>
            <p style="color: #666; margin-top: 10px; font-size: 0.9em; line-height: 1.5;">
            수온·기온·풍속과<br/>
            시세의 상관관계 분석
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 사용 방법 안내 (접을 수 있는 형태)
    with st.expander("💡 대시보드 사용 가이드"):
        st.markdown("""

        ### 이렇게 활용하세요
        ######
        
        
        **1️⃣ 어종별 시세 분석**
        - 관심 어종을 선택하여 일별 가격 변동 추이를 확인
        - 평균가, 최고가, 최저가를 비교하여 거래 시기 결정
        
        **2️⃣ 품종 및 상태별 비교**
        - 동일 어종의 활어/냉동/선어 상태별 가격 차이 분석
        - 계절별 최적 거래 시기 파악
        
        **3️⃣ 해양환경 연계 분석**
        - 수온, 기온, 풍속 등 해양 데이터가 가격에 미치는 영향 분석
        - 산지별 환경 요인과 시세의 상관관계 확인
        
        ---  
         **사용된 데이터 기간** : 2021년 ~ 2024년
    """)
    st.markdown("---")



    



    # 1️⃣ CSV 데이터 로드 및 전처리
    df = load_and_preprocess_data('./data/수산물_통합전처리_3컬럼.csv')

    # 2️⃣ 세션 상태 초기화
    for key in ['section1_show', 'section2_show', 'section3_show']:
        if key not in st.session_state:
            st.session_state[key] = False

    # -------------------------------------------------
    # ① 어종별 일별 경매가 변동 추이
    # -------------------------------------------------
    st.subheader("① 어종별 평균 경매가 ")
    # 설명 캡션 추가
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 14px; opacity: 1;"> 
    💡어종별 시세를 한눈에 알아보세요.
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('---')

    species = st.selectbox(" 어종을 선택하세요 ", sorted(df['파일어종'].unique()))

    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.section1_show:
            if st.button("시세 보기", key="btn_show_section1"):
                st.session_state.section1_show = True
    with col2:
        if st.button("초기화", key="btn_reset_section1"):
            st.session_state.section1_show = False
            st.rerun()

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
            st.markdown('---')
            selected_metrics = st.multiselect(
                "가격 항목을 선택하세요 ~", ['평균가', '낙찰고가', '낙찰저가'], default=['평균가'])
            if selected_metrics is None or len(selected_metrics) == 0:
                st.warning("하나 이상의 가격 항목을 선택해주세요.")
            else:
                plot_metrics(result, selected_metrics, f"{species} 가격 추이")
                # ==================== 메트릭 카드 섹션 ====================
                st.markdown("---")
                

                # 계산
                avg_price = result['평균가'].mean()
                max_price = result['낙찰고가'].max()
                min_price = result['낙찰저가'].min()
                price_range = max_price - min_price
                price_volatility = (result['평균가'].std() / avg_price * 100)
                
                # 데이터 기간
                date_range = (result.index.max() - result.index.min()).days
                
                # 최근 트렌드 (최근 30일 vs 이전 30일)
                if len(result) > 60:
                    recent_30 = result.tail(30)['평균가'].mean()
                    previous_30 = result.iloc[-60:-30]['평균가'].mean()
                    trend_change = ((recent_30 - previous_30) / previous_30 * 100)
                elif len(result) > 30:
                    recent_30 = result.tail(30)['평균가'].mean()
                    trend_change = ((recent_30 - avg_price) / avg_price * 100)
                else:
                    recent_30 = avg_price
                    trend_change = 0
                
                # 4개 메트릭 카드
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="평균 경매가",
                        value=f"{avg_price:,.0f}원",
                        delta=f"{trend_change:+.1f}% (최근 추세)"
                    )
                
                with col2:
                    st.metric(
                        label="최고 낙찰가",
                        value=f"{max_price:,.0f}원",
                        delta=f"+{((max_price - avg_price) / avg_price * 100):.1f}%",
                        delta_color="off"
                    )
                
                with col3:
                    st.metric(
                        label="최저 낙찰가",
                        value=f"{min_price:,.0f}원",
                        delta=f"{((min_price - avg_price) / avg_price * 100):.1f}%",
                        delta_color="off"
                    )
                
                with col4:
                    st.metric(
                        label="가격 변동폭",
                        value=f"{price_range:,.0f}원",
                        delta=f"변동률 {price_volatility:.1f}%"
                    )

                st.markdown('')
                st.markdown('')
                st.markdown('')
                st.markdown('')
                
                # ==================== 인사이트 카드 섹션 ====================
                
                col_i1, col_i2, col_i3 = st.columns(3)
                
                with col_i1:
                    # 가격 트렌드 분석
                    if trend_change > 5:
                        trend_text = "강한 상승세"
                        trend_emoji = ""
                        trend_desc = "가격이 지속적으로 상승 중입니다"
                        trend_color = "#e74c3c"
                    elif trend_change > 2:
                        trend_text = "완만한 상승"
                        trend_emoji = ""
                        trend_desc = "가격이 소폭 상승하고 있습니다"
                        trend_color = "#e67e22"
                    elif trend_change < -5:
                        trend_text = "급격한 하락"
                        trend_emoji = ""
                        trend_desc = "가격이 빠르게 하락하고 있습니다"
                        trend_color = "#2ecc71"
                    elif trend_change < -2:
                        trend_text = "완만한 하락"
                        trend_emoji = ""
                        trend_desc = "가격이 소폭 하락하고 있습니다"
                        trend_color = "#27ae60"
                    else:
                        trend_text = "안정 유지"
                        trend_emoji = ""
                        trend_desc = "가격이 안정적으로 유지되고 있습니다"
                        trend_color = "#3498db"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 10px; border-radius: 10px; color: white; height: 180px;">
                    <p style="margin: 0; font-size: 15px; opacity: 0.95;"> 
                        <h4>{trend_emoji} 가격 추세</h4>
                        <p style="font-size: 12px; line-height: 1.5;">
                        <b style="color: {trend_color};">{trend_text}</b><br/>
                        {trend_desc}
                        </p>
                        <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                        변화율: {abs(trend_change):.1f}%<br/>
                        최근 평균: {recent_30:,.0f}원
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_i2:
                    # 변동성 및 안정성 분석
                    if price_volatility > 25:
                        volatility_level = "매우 높음"
                        volatility_desc = "가격 예측이 어려운 고위험 구간"
                        vol_emoji = ""
                        vol_color = "#e74c3c"
                    elif price_volatility > 15:
                        volatility_level = "높음"
                        volatility_desc = "변동이 크므로 거래 타이밍 중요"
                        vol_emoji = ""
                        vol_color = "#f39c12"
                    elif price_volatility > 8:
                        volatility_level = "보통"
                        volatility_desc = "적정 수준의 가격 변동"
                        vol_emoji = ""
                        vol_color = "#3498db"
                    else:
                        volatility_level = "낮음"
                        volatility_desc = "안정적인 가격 형성"
                        vol_emoji = ""
                        vol_color = "#2ecc71"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 10px; border-radius: 10px; color: white; height: 180px;">
                        <h4>{vol_emoji} 가격 변동성</h4>
                        <p style="font-size: 12px; line-height: 1.5;">
                        변동성: <b style="color: {vol_color};">{volatility_level}</b><br/>
                        {volatility_desc}
                        </p>
                        <p style="font-size: 12px; margin-top: 1px; opacity: 1.5;">
                        변동계수: {price_volatility:.1f}%<br/>
                        가격 범위: {price_range:,.0f}원
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

    
                    

    # -------------------------------------------------
    # ② 파일어종 및 세부 어종별 낙찰가 비교
    # -------------------------------------------------
    st.markdown('---')

    st.subheader("② 품종 및 상태별 어종 경매가 ")
    # 설명 캡션 추가
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 14px; opacity: 1;"> 
    💡 품종별, 상태별 시세를 비교하여 최적의 거래 시기를 파악해보세요.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
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
            st.rerun()

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


                    # 상태명 매핑 (줄임말 → 풀네임)
        state_fullname_map = { "활": "활어", "냉": "냉동", "선": "선어(냉장)" }
        # 역매핑 (풀네임 → 줄임말)
        state_shortname_map = {v: k for k, v in state_fullname_map.items()}

        # 품종 및 상태 선택 섹션

        if pure_species_list:
            st.markdown('품종을 선택해주세요')
            col_species, col_state = st.columns([2.5, 1.5])

            with col_species:
                selected_pure_species_list = st.multiselect(
                    "품종 선택 (최대 2개)", pure_species_list,
                    key="pure_species_select", 
                    max_selections=2,
                    label_visibility="collapsed"
                )
            
            if not selected_pure_species_list:
                st.warning("하나 이상의 품종을 선택해주세요.")
    
            species_list = []
            for selected_pure_species in selected_pure_species_list:
                available_states = sorted(species_info[selected_pure_species])
                available_states_full = [state_fullname_map.get(s, s) for s in available_states]

                # 품종별로 상태 선택
                st.markdown(f"**{selected_pure_species}** 상태 선택:")
                if len(available_states) == 1:
                    selected_state_full = available_states_full[0]
                    st.info(f"'{selected_pure_species}'는 '{selected_state_full}' 상태의 데이터만 있습니다.")
                else:
                    selected_state_full = st.radio(
                        f"{selected_pure_species}의 상태를 선택하세요",
                        available_states_full,
                        horizontal=True,
                        key=f"radio_state_section2_{selected_pure_species}"
                    )

                selected_state = state_shortname_map.get(selected_state_full, selected_state_full)
                species_list.append(f"({selected_state}){selected_pure_species}")

            species = species_list

        else:
            st.warning("분류 가능한 품종이 없습니다.")
            st.stop()

                
        show_analysis = True
        if not selected_pure_species_list:
            show_analysis = False
        
        if show_analysis and species_list:
            results = []
            display_dfs = []
            
            for species_name in species_list:
                result = filter_by_species(subset, '어종', species_name)
                if result is not None:
                    results.append(result)
                    # 표시용 데이터프레임 생성
                    display_df = result.reset_index()
                    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                    display_df = display_df.rename(columns={'date': '기준날짜'})
                    display_df['품종'] = species_name  # 품종 정보 추가
                    display_dfs.append(display_df)
            
            if display_dfs:
                # 모든 데이터프레임 통합하여 표시
                combined_df = pd.concat(display_dfs, ignore_index=True)
                st.dataframe(combined_df)
                
                # 그래프 표시
                # 여러 품종을 비교할 때는 가독성 문제로 평균가만 표시
                if len(results) > 1:
                    metrics_to_plot = ['평균가']
                    st.info("여러 품종을 비교할 때는 '평균가'만 표시됩니다.")
                else:
                    metrics_to_plot = ['평균가', '낙찰고가', '낙찰저가']

                plot_metrics(results, metrics_to_plot, species_list)

            st.markdown("---")

            # 선택된 품종이 한 개일 때만 상세 메트릭 및 인사이트를 표시
            if len(species_list) == 1 and results:
                single_result = results[0]

                # 계산
                avg_price = single_result['평균가'].mean()
                max_price = single_result['낙찰고가'].max()
                min_price = single_result['낙찰저가'].min()
                price_range = max_price - min_price
                price_volatility = (single_result['평균가'].std() / avg_price * 100)
                
                # 최근 트렌드 (최근 30일 vs 전체 평균)
                if len(single_result) > 30:
                    recent_avg = single_result.tail(30)['평균가'].mean()
                    trend_change = ((recent_avg - avg_price) / avg_price * 100)
                else:
                    recent_avg = avg_price
                    trend_change = 0
                
                # 4개 메트릭 카드
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="평균 경매가",
                        value=f"{avg_price:,.0f}원",
                        delta=f"{trend_change:+.1f}% (최근 30일)"
                    )
                
                with col2:
                    st.metric(
                        label="최고 낙찰가",
                        value=f"{max_price:,.0f}원",
                        delta=f"+{((max_price - avg_price) / avg_price * 100):.1f}%",
                        delta_color="off"
                    )
                
                with col3:
                    st.metric(
                        label="최저 낙찰가",
                        value=f"{min_price:,.0f}원",
                        delta=f"{((min_price - avg_price) / avg_price * 100):.1f}%",
                        delta_color="off"
                    )
                
                with col4:
                    st.metric(
                        label="가격 변동폭",
                        value=f"{price_volatility:.1f}%",
                        delta=f"범위 {price_range:,.0f}원"
                    )

                st.markdown('---')
                
                # ==================== 인사이트 카드 섹션 ====================
                col_i1, col_i2, col_i3 = st.columns(3)
                
                with col_i1:
                    # 가격 트렌드 분석
                    if trend_change > 5:
                        trend_text = "상승 추세"
                        trend_emoji = ""
                        trend_color = "#e74c3c"
                    elif trend_change < -5:
                        trend_text = "하락 추세"
                        trend_emoji = ""
                        trend_color = "#2ecc71"
                    else:
                        trend_text = "안정 추세"
                        trend_emoji = ""
                        trend_color = "#3498db"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 9px; border-radius: 10px; color: white; height: 180px;">
                        <h4>{trend_emoji} 최근 가격 동향</h4>
                        <p style="font-size: 12px; line-height: 1.5;">
                        최근 30일 평균가가<br/>
                        전체 평균 대비 <b>{abs(trend_change):.1f}%</b><br/>
                        <b style="color: {trend_color};">{trend_text}</b>
                        </p>
                        <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                        최근 평균: {recent_avg:,.0f}원
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_i2:
                    # 변동성 분석
                    if price_volatility > 20:
                        volatility_level = "높음"
                        volatility_desc = "가격 변동이 크므로 거래 시점 신중 선택 필요"
                        vol_color = "#e74c3c"
                    elif price_volatility > 10:
                        volatility_level = "중간"
                        volatility_desc = "적당한 가격 변동으로 예측 가능성 양호"
                        vol_color = "#f39c12"
                    else:
                        volatility_level = "낮음"
                        volatility_desc = "안정적인 가격으로 예측 가능성 높음"
                        vol_color = "#2ecc71"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 9px; border-radius: 10px; color: white; height: 180px;">
                        <h4> 가격 변동성</h4>
                        <p style="font-size: 12px; line-height: 1.5;">
                        변동성: <b style="color: {vol_color};">{volatility_level}</b><br/>
                        {volatility_desc}
                        </p>
                        <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                        변동계수: {price_volatility:.1f}%
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_i3:
                    # 최적 거래 시기 (월별 평균)
                    if 'date' in single_result.columns:
                        result_with_month = single_result.copy()
                        result_with_month['month'] = pd.to_datetime(result_with_month['date']).dt.month
                        monthly_avg = result_with_month.groupby('month')['평균가'].mean()
                        best_month = monthly_avg.idxmin()
                        worst_month = monthly_avg.idxmax()
                        price_diff = ((monthly_avg.max() - monthly_avg.min()) / monthly_avg.mean() * 100)
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  
                                    padding: 15px; border-radius: 10px; color: white; height: 150px;">
                            <h4> 최적 거래 시기</h4>
                            <p style="font-size: 13px; line-height: 1.5;">
                            <b>{best_month}월</b>에 가장 저렴<br/>
                            <b>{worst_month}월</b>에 가장 비쌈
                            </p>
                            <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                            월별 가격차: {price_diff:.1f}%
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  
                                    padding: 10px; border-radius: 10px; color: white; height: 180px;">
                            <h4> 거래 정보</h4>
                            <p style="font-size: 15px; line-height: 1.8;">
                            선택한 품종과 상태의<br/>
                            데이터를 분석 중입니다.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                # 여러 품종 선택 또는 품종 미선택 시 상세 카드는 표시하지 않음
                if not selected_pure_species_list:
                    st.info("품종을 선택하면 상세 정보가 표시됩니다.")
                else:
                    st.info("여러 품종을 선택하셨습니다. 상세 메트릭과 인사이트는 품종을 하나만 선택했을 때 표시됩니다.")
            

    st.markdown("---")

    # -------------------------------------------------
    # ③ 해양데이터 연계 분석
    # -------------------------------------------------
    st.subheader("③ 해양데이터 (수온 · 기온 · 풍속) 관계 분석")
    # 메인 설명 캡션 추가
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            padding: 8px; border-radius: 10px; color: white; margin-bottom: 10px;">
    <p style="margin: 0; font-size: 14px; opacity: 1;"> 
    💡 해양 환경 데이터(수온, 기온, 풍속)와 시세의 상관관계를 알아보세요.
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('---')

    col5, col6 = st.columns(2)
    with col5:
        if not st.session_state.section3_show:
            if st.button("분석 보기", key="btn_show_section3"):
                st.session_state.section3_show = True
    with col6:
        if st.button("초기화", key="btn_reset_section3"):
            st.session_state.section3_show = False
            st.rerun()

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
        
        ocean_df.dropna(inplace=True)
    

        col_m, col_m_reset, col_s = st.columns([2.5, 0.8, 2.5])
        with col_m:
            st.markdown("산지를 선택하세요")
            selected_market = st.selectbox(
                "산지 선택",
                market_list,
                key="market_section3",
                label_visibility="collapsed",
            )
        
        with col_s:
            st.markdown("어종을 선택하세요.")
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

            st.markdown('---')

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

        
            # ==================== 메트릭 카드 섹션 (맨 아래로 이동) ====================
        st.markdown("---")

        # 모든 어종에 대한 상관관계 계산
        species_correlations = calculate_species_correlations(df, ocean_df, selected_market)
        most_affected = get_most_affected_species(species_correlations)
        
        # 현재 선택된 어종에 대한 계산
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

        st.markdown("---")

        # 환경 변수별 가장 영향받는 어종 표시
        st.subheader(f" {selected_market}의 환경별 관계 1순위 어종")

        st.markdown('')
    
        
        env_col1, env_col2, env_col3 = st.columns(3)
        
        highlight_color = "#cdeff3"  # 연두색과 초록색 중간 느낌 색상

        with env_col1:
            temp_species = most_affected['수온']['species']
            temp_corr = most_affected['수온']['correlation']
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        padding: 15px; border-radius: 10px; color: white;">
                <h4> 수온 영향 1위</h4>
                <p style="font-size: 20px; line-height: 1.5;">
                    <b style="color: {highlight_color};">{temp_species}</b>
                </p>
                <p style="font-size: 12px; opacity: 0.9;">
                    상관계수: {temp_corr:.3f}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with env_col2:
            air_species = most_affected['기온']['species']
            air_corr = most_affected['기온']['correlation']
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        padding: 15px; border-radius: 10px; color: white;">
                <h4> 기온 영향 1위</h4>
                <p style="font-size: 20px; line-height: 1.5;">
                    <b style="color: {highlight_color};">{air_species}</b>
                </p>
                <p style="font-size: 12px; opacity: 0.9;">
                    상관계수: {air_corr:.3f}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with env_col3:
            wind_species = most_affected['풍속']['species']
            wind_corr = most_affected['풍속']['correlation']
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        padding: 15px; border-radius: 10px; color: white;">
                <h4> 풍속 영향 1위</h4>
                <p style="font-size: 20px; line-height: 1.5;">
                    <b style="color: {highlight_color};">{wind_species}</b>
                </p>
                <p style="font-size: 12px; opacity: 0.9;">
                    상관계수: {wind_corr:.3f}
                </p>
            </div>
            """, unsafe_allow_html=True)


        st.markdown("---")
        
        col_i1, col_i2, col_i3 = st.columns(3)
        
        with col_i1:
            if corr_temp < -0.3:
                temp_insight = "수온이 높을수록 가격이 <b><span style='color: #fa4e3b;'>하락</span></b>하는 역상관 관계"  
                temp_emoji = ""
            elif corr_temp > 0.3:
                temp_insight = "수온이 높을수록 가격이 <b><span style='color: #f39c12;'>상승</span></b>하는 양의 상관관계"  
                temp_emoji = ""
            else:
                temp_insight = "수온과 가격 간 <span style='color: #fa4e3b;'><b>약한 상관관계</b></span>"
                temp_emoji = ""


            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 15px; border-radius: 10px; color: white; height: 180px;">
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
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 15px; border-radius: 10px; color: white; height: 180px;">
                    <h4> 계절별 시세</h4>
                    <p style="font-size: 13px; line-height: 1.5;">
                        <b>{highest_season}</b>에<b style="color: #fa4e3b;"> 최고가</b><br/>
                        <b>{lowest_season}</b>에<b style="color: #2ecc71;"> 최저가</b>기록</b>
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
                wind_color = "#fa4e3b"
            elif abs(corr_wind) > 0.15:
                wind_impact = "중간"
                wind_color = "#f39c12"
            else:
                wind_impact = "낮음"
                wind_color = "#2ecc71"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 15px; border-radius: 10px; color: white; height: 180px;">
                <h4> 풍속 영향도</h4>
                <p style="font-size: 13px; line-height: 1;">
                풍속의 가격 영향력:<br/>
                <b style="color: {wind_color};">{wind_impact}</b>
                </p>
                <p style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                상관계수: {corr_wind:.3f}<br/>
                평균 풍속: {merged['풍속 평균'].mean():.1f}m/s
                </p>
            </div>
            """, unsafe_allow_html=True)

def show_source():
    st.markdown("---")
    st.caption("📍 데이터 출처: 수산물유통정보시스템(FIPS) | 해양환경정보시스템")

# 앱 마지막에 호출
show_source()


# ============================================================
# 실행부
# ============================================================

if __name__ == "__main__":
    species_price()
