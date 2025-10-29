import os
import re
import io
import joblib
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from prophet import Prophet


def _clean_price_series(s):
    # 문자열로 된 가격에서 쉼표와 따옴표 제거 후 float 변환
    if s.dtype == object:
        return s.fillna('0').astype(str).str.replace(r"[^0-9.-]", "", regex=True).replace('', '0').astype(float)
    return s.astype(float)


def run_ml():
    """Streamlit app: 어종별 월별 경락가를 Prophet으로 학습/예측합니다.

    사용법(간단):
    - 좌측에서 어종을 선택
    - 예측할 연수(예: 3년)를 선택하면 월 단위로 (연수*12)개월을 예측

    데이터: 프로젝트의 `data/수산물_통합_전처리.csv` 파일을 사용합니다.
    컬럼: 'date' (YYYY-MM-DD), '공통어종' (어종 그룹), '평균가' (숫자, 쉼표 포함) 가 필요합니다.
    """
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

    species_list = sorted(df['파일어종'].dropna().unique())
    species = st.sidebar.selectbox('어종 선택', species_list)

    
    years_to_forecast = st.sidebar.slider('예측 기간 (년)', min_value=1, max_value=10, value=3)
    retrain = st.sidebar.checkbox('모델 재학습 (강제)', value=False)
    months = years_to_forecast * 12

    # 주요 월을 사용자가 선택할 수 있도록 함 (디자이너처럼 기본은 3,6,9,12)
    
    months_with_label = [f"{m}월" for m in range(1, 13)]

    months_to_show = st.sidebar.multiselect('주요 월 선택', options=months_with_label,default=["3월", "6월", "9월", "12월"])
    # 모델 관련 정보와 도움말
    st.sidebar.markdown('---')
    st.sidebar.markdown('Tip: 주요 월을 선택하여 각 연도의 핵심 시점을 빠르게 확인하세요.')

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

    model = None
    if os.path.exists(model_file) and (not retrain):
        try:
            model = joblib.load(model_file)
            st.info('저장된 모델을 불러왔습니다.')
        except Exception as e:
            st.warning(f'저장된 모델 로드 실패: {e}. 재학습을 진행합니다.')
            model = None

    if model is None:
        with st.spinner('Prophet 모델 학습 중...'):
            model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            # Prophet 기본으로도 월별 패턴을 잡지만 필요시 커스텀 시즌 추가 가능
            try:
                model.fit(monthly)
                joblib.dump(model, model_file)
                st.success('모델 학습 완료 및 저장되었습니다.')
            except Exception as e:
                st.error(f'모델 학습 실패: {e}')
                return

    # 예측
    future = model.make_future_dataframe(periods=months, freq='M')
    forecast = model.predict(future)

    st.subheader('예측 결과')
    # matplotlib figure 출력
    fig = model.plot(forecast)
    st.pyplot(fig)

    # 예측값 테이블 (월별) 제공
    forecast_monthly = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_monthly['ds'] = pd.to_datetime(forecast_monthly['ds']).dt.to_period('M').dt.to_timestamp()
    
    # 연도/주요월(3,6,9,12)별 예측 결과를 텍스트로 표시
    st.subheader("연도별 주요 월(3,6,9,12) 예측 가격")
    last_training_date = monthly['ds'].max()
    future_forecasts = forecast_monthly[forecast_monthly['ds'] > last_training_date]

    # 디자이너 스타일: 연도별로 행을 만들고, 주요 월을 칼럼으로 정렬하여 metric 카드 형태로 표현
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

    # 테이블로도 전체 데이터 표시
    st.subheader("예측 결과 테이블")
    st.dataframe(forecast_monthly.tail(months + 6))

    # CSV 다운로드
    csv_buf = io.StringIO()
    forecast_monthly.to_csv(csv_buf, index=False)
    csv_bytes = csv_buf.getvalue().encode('utf-8')
    st.download_button(label='예측 결과 다운로드 (CSV)', data=csv_bytes, file_name=f'forecast_{species}.csv', mime='text/csv')

    # 그래프 PNG로 다운로드 (디자이너용 보고서 첨부 가능)
    try:
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format='png', bbox_inches='tight')
        img_buf.seek(0)
        st.download_button(label='그래프 다운로드 (PNG)', data=img_buf, file_name=f'forecast_{species}.png', mime='image/png')
    except Exception:
        # fig가 없거나 저장 불가 시 무시
        pass

    st.markdown('---')
    st.markdown('### 노트')
    st.markdown('- 데이터는 `data/수산물_통합_전처리.csv`의 `공통어종` 및 `평균가`를 사용하여 월별 평균을 계산합니다.')


        