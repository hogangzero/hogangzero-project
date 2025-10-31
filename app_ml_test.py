import os
import re
import io
import joblib
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from prophet import Prophet
import seaborn as sns


def _clean_price_series(s):
    # 문자열로 된 가격에서 쉼표와 따옴표 제거 후 float 변환
    if s.dtype == object:
        return s.fillna('0').astype(str).str.replace(r"[^0-9.-]", "", regex=True).replace('', '0').astype(float)
    return s.astype(float)


def run_ml():
    """수산물 경매가 예측 시스템

    수산물 도매 거래를 위한 가격 동향 분석 및 예측 도구입니다.
    시장 가격 예측을 통해 효율적인 구매 계획을 수립할 수 있습니다.
    """
    
    # 페이지 기본 설정
    st.set_page_config(
        page_title="수산물 경매가 예측 시스템",
        page_icon="🐟",
        layout="wide"
    )
    # 간단한 스타일링: 가운데 정렬된 제목과 서브타이틀
    st.markdown(
        "<div style='text-align:center; padding:6px 0 0 0'>"
        "<h1 style='margin:0'>날짜별 가격 예측</h1>"
        "<p style='color:gray; margin:0'>Prophet 모델을 이용한 월별 예측</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.header('')

    st.markdown('---')
    
    
    


    data_path = os.path.join('data', '수산물_통합전처리_3컬럼.csv')
    if not os.path.exists(data_path):
        st.error(f'데이터 파일이 없습니다: {data_path}')
        return

    # 데이터 로드
    df = pd.read_csv(data_path)

    # 예상되는 컬럼 확인
    needed = ['date', '파일어종', '평균가']
    if not all(c in df.columns for c in needed):
        st.error(f'데이터에 필요한 컬럼이 없습니다. 필요: {needed}. 현재 컬럼: {list(df.columns)}')
        return

    # 전처리: 날짜 파싱, 평균가 정리
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['평균가'] = _clean_price_series(df['평균가'])

    # 사이드바 설정
    with st.sidebar:
        st.markdown("""
            <div style='background-color:#f0f8ff; padding:15px; border-radius:10px'>
            <h2 style='color:#1e3d59; margin:0'>🎯 거래 설정</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # 어종 선택
        st.markdown("### 🐟 어종 선택")
        species_list = sorted(df['파일어종'].dropna().unique())
        species = st.selectbox(
            '분석할 어종을 선택하세요',
            species_list,
            help="가격을 예측하고 싶은 어종을 선택하세요"
        )
        
        st.markdown("### 📅 기간 설정")
        years_to_forecast = st.slider(
            '예측 기간',
            min_value=1,
            max_value=5,
            value=2,
            help="향후 몇 년간의 가격을 예측할지 선택하세요"
        )
        months = years_to_forecast * 12
        
        st.markdown("### 📊 분석 옵션")
        months_with_label = [f"{m}월" for m in range(1, 13)]
        months_to_show = st.multiselect(
            '주요 거래월 선택',
            options=months_with_label,
            default=["3월", "6월", "9월", "12월"],
            help="중점적으로 보고 싶은 월을 선택하세요"
        )
        
        # 거래 팁 제공
        st.markdown("---")
        with st.expander("💡 거래 전략 팁"):
            st.markdown("""
            - **분기별 가격 변동**: 3,6,9,12월의 가격 변화를 주목하세요
            - **계절성 고려**: 어종별 성수기/비수기를 참고하세요
            - **신뢰구간 활용**: 가격 변동 범위를 고려해 거래하세요
            - **장기 트렌드**: 연간 가격 추세를 파악하세요
            """)

    # 모델 디렉터리
    model_dir = os.path.join('.', 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_file = os.path.join(model_dir, f'model_{re.sub(r"[^0-9a-zA-Z가-힣_]","_", species)}.pkl')

    # 선택한 어종 데이터 월 단위 집계 (평균)
    # 파일에서 사용자가 선택한 어종은 '파일어종' 컬럼에서 선택하므로 동일 컬럼으로 필터링합니다.
    df_sp = df[df['파일어종'] == species].copy()
    if df_sp.empty:
        st.warning('선택한 어종에 대한 데이터가 없습니다.')
        return

    df_sp.set_index('date', inplace=True)
    monthly = df_sp['평균가'].resample('M').mean().reset_index()
    monthly = monthly.dropna()
    monthly = monthly.rename(columns={'date': 'ds', '평균가': 'y'})

    st.subheader(f'{species} - 학습 데이터 (월별 평균, 관측치 수: {len(monthly)})')
    st.dataframe(monthly.tail(12))

    # 모델 로드 또는 학습
    model = None
    if os.path.exists(model_file):
        try:
            model = joblib.load(model_file)
            st.info('✅ 가격 예측 준비가 완료되었습니다')
        except Exception as e:
            model = None
            st.warning('시스템을 초기화하고 있습니다. 잠시만 기다려주세요.')

    if model is None:
        with st.spinner('🔄 시장 데이터 분석 중...'):
            model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            try:
                model.fit(monthly)
                joblib.dump(model, model_file)
                st.success('✨ 데이터 분석이 완료되었습니다!')
            except Exception as e:
                st.error('😓 분석 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.')
                return

    # 가격 예측 수행
    future = model.make_future_dataframe(periods=months, freq='M')
    forecast = model.predict(future)

    # 예측 결과 시각화
    st.markdown("""
        <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; margin:20px 0'>
        <h2 style='color:#1e3d59; margin:0'>📈 가격 동향 분석</h2>
        <p style='color:#666; margin:10px 0'>파란색 선: 예측 가격 | 파란색 영역: 예측 가격 변동 범위</p>
        </div>
    """, unsafe_allow_html=True)

    # 그래프 스타일링 개선
    fig = model.plot(forecast)
    sns.set_theme(style="whitegrid")
    plt.title(f'{species} 경매가 동향 및 예측', pad=20, fontsize=14)
    plt.xlabel('거래 시기', fontsize=12)
    plt.ylabel('예상 경매가 (원)', fontsize=12)
    st.pyplot(fig)

    # 예측 데이터 준비
    forecast_monthly = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_monthly['ds'] = pd.to_datetime(forecast_monthly['ds']).dt.to_period('M').dt.to_timestamp()
    
    # 주요 거래월 예측 결과
    st.markdown("""
        <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; margin:20px 0'>
        <h2 style='color:#1e3d59; margin:0'>💰 예상 거래 가격</h2>
        <p style='color:#666; margin:10px 0'>선택하신 주요 거래월의 예상 경매가와 변동 범위입니다</p>
        </div>
    """, unsafe_allow_html=True)
    
    last_training_date = monthly['ds'].max()
    future_forecasts = forecast_monthly[forecast_monthly['ds'] > last_training_date]

    # 디자이너 스타일: 연도별로 행을 만들고, 주요 달을 칼럼으로 정렬하여 metric 카드 형태로 표현
    years = sorted(future_forecasts['ds'].dt.year.unique())
    for year in years:
        year_data = future_forecasts[future_forecasts['ds'].dt.year == year]
        if year_data.empty:
            continue
        st.markdown(f"### {year}년")

        cols = st.columns(len(months_to_show))
        for col, m in zip(cols, months_to_show):
            with col:
                row = year_data[year_data['ds'].dt.month == m]
                if row.empty:
                    st.metric(label=f"{m}월", value="데이터 없음")
                    st.caption('예측 범위에 없음')
                    continue
                r = row.iloc[0]
                predicted_price = r['yhat']
                lower_bound = r['yhat_lower']
                upper_bound = r['yhat_upper']
                # 메트릭 카드로 출력 (숫자 형식: 천단위 콤마)
                st.metric(label=f"{m}월", value=f"{predicted_price:,.0f}원")
                st.caption(f"신뢰구간: {lower_bound:,.0f}원 ~ {upper_bound:,.0f}원")
        st.markdown("---")

    # 상세 데이터 및 다운로드 섹션
    st.markdown("""
        <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; margin:20px 0'>
        <h2 style='color:#1e3d59; margin:0'>📊 상세 데이터</h2>
        <p style='color:#666; margin:10px 0'>월별 예측 가격 상세 정보와 데이터 다운로드</p>
        </div>
    """, unsafe_allow_html=True)

    # 데이터 테이블 표시
    with st.expander("📋 월별 상세 예측 데이터"):
        formatted_data = forecast_monthly.tail(months + 6).copy()
        formatted_data['ds'] = formatted_data['ds'].dt.strftime('%Y년 %m월')
        formatted_data.columns = ['거래월', '예측가격', '최소예상가격', '최대예상가격']
        formatted_data['예측가격'] = formatted_data['예측가격'].apply(lambda x: f'{x:,.0f}원')
        formatted_data['최소예상가격'] = formatted_data['최소예상가격'].apply(lambda x: f'{x:,.0f}원')
        formatted_data['최대예상가격'] = formatted_data['최대예상가격'].apply(lambda x: f'{x:,.0f}원')
        st.dataframe(formatted_data, hide_index=True)

    # 다운로드 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        # 엑셀 다운로드
        csv_buf = io.StringIO()
        forecast_monthly.to_csv(csv_buf, index=False)
        csv_bytes = csv_buf.getvalue().encode('utf-8')
        st.download_button(
            label='📥 예측 데이터 다운로드 (Excel)',
            data=csv_bytes,
            file_name=f'{species}_가격예측_{years_to_forecast}년.csv',
            mime='text/csv',
            help='월별 예측 가격을 엑셀 파일로 저장합니다'
        )

    with col2:
        # 그래프 이미지 다운로드
        try:
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
            img_buf.seek(0)
            st.download_button(
                label='📥 가격 동향 그래프 (이미지)',
                data=img_buf,
                file_name=f'{species}_가격동향_{years_to_forecast}년.png',
                mime='image/png',
                help='가격 동향 그래프를 고품질 이미지로 저장합니다'
            )
        except Exception:
            st.warning("그래프 저장 중 문제가 발생했습니다")

    # 참고 사항
    st.markdown('---')
    with st.expander("ℹ️ 데이터 신뢰도 안내"):
        st.markdown("""
        **예측 정확도 관련 참고사항**
        
        - 이 예측은 과거 실제 거래 데이터를 기반으로 한 통계적 분석 결과입니다
        - 실제 시장 가격은 날씨, 수급 상황 등 다양한 요인에 의해 변동될 수 있습니다
        - 신뢰구간은 예상되는 가격의 변동 범위를 나타냅니다
        - 가까운 미래일수록 예측의 정확도가 높습니다
        
        **활용 방법**
        
        - 구매 계획 수립 시 참고 자료로 활용하세요
        - 계절성과 장기 트렌드를 고려한 의사결정에 활용하세요
        - 정기적으로 예측을 확인하여 시장 동향을 파악하세요
        """)


        