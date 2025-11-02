import os
import re
import io
import joblib
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import pandas as pd
from prophet import Prophet
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from koreanize_matplotlib import koreanize

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
    
    # 메인 타이틀 - 통일된 그라데이션 스타일
    st.markdown(
        "<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        "padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>"
        "<h1 style='color: white; margin: 0;'>날짜별 가격 예측</h1>"
        "<p style='color: white; margin: 5px 0; opacity: 0.95;'>AI 기반 수산물 거래 가격 예측 시스템</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    st.markdown('---')

    # 안내 메시지
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 7px;
                background: #f8f9fa; padding: 15px; border-radius: 10px;'>
        <p style='margin: 0; font-size: 1.4em; line-height: 1.5;'>
            좌측 사이드바에서 어종과 예측 기간을 설정하세요
        </p>
    </div>
    """, unsafe_allow_html=True)
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

        st.divider()
        st.sidebar.header('상세 검색하기')
        
        # 어종 선택
        st.markdown("## 어종 선택")
        species_list = sorted(df['파일어종'].dropna().unique())
        species = st.selectbox(
            '분석할 어종을 선택하세요',
            species_list,
            help="가격을 예측하고 싶은 어종을 선택하세요"
        )
        
        st.markdown("## 기간 설정")
        years_to_forecast = st.slider(
            '예측 연도를 설정하세요',
            min_value=1,
            max_value=5,
            value=2,
            help="향후 몇 년간의 가격을 예측할지 선택하세요"
        )
        months = years_to_forecast * 12

        months_with_label = [f"{m}월" for m in range(1, 13)]
        months_to_show = st.multiselect(
            '주요 거래월을 선택하세요',
            options=months_with_label,
            default=["3월", "6월", "9월", "12월"],
            help="중점적으로 보고 싶은 월을 선택하세요"
        )
        if not months_to_show:
            st.warning('최소 한 개 이상의 거래월을 선택해주세요.')
            return
        
        # 문자열 "N월"을 숫자로 변환
        selected_months_num = [int(m.replace("월", "")) for m in months_to_show]
            
        # 거래 팁 제공
        st.markdown("---")
        with st.expander("💡  거래 전략 팁"):
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
    df_sp = df[df['파일어종'] == species].copy()
    if df_sp.empty:
        st.warning('선택한 어종에 대한 데이터가 없습니다.')
        return
        

    df_sp.set_index('date', inplace=True)
    monthly = df_sp['평균가'].resample('M').mean().reset_index()
    monthly = monthly.dropna()
    monthly = monthly.rename(columns={'date': 'ds', '평균가': 'y'})


    # 최근 시장 동향 표시 - 스타일 변경
    st.subheader('① 최근 시장 경매가')
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.95;'>
                💡  {species}의 최근 12개월 거래 데이터 분석입니다.
            </p>
        </div>
    """, unsafe_allow_html=True)


    # 최근 12개월 데이터를 보기 좋게 표시
    with st.expander("최근 12개월 시세 보기"):
        recent_data = monthly.tail(12).copy()
        recent_data['ds'] = recent_data['ds'].dt.strftime('%Y년 %m월')
        recent_data = recent_data.rename(columns={'ds': '거래월', 'y': '평균 경매가(원)'})
        recent_data['평균 경매가(원)'] = recent_data['평균 경매가(원)'].apply(lambda x: f'{x:,.0f}')
        st.dataframe(recent_data, hide_index=True)



    # 모델 로드 또는 학습
    model = None
    if os.path.exists(model_file):
        try:
            model = joblib.load(model_file)
        except Exception as e:
            model = None
            st.warning('시스템을 초기화하고 있습니다. 잠시만 기다려주세요.')

    if model is None:
        with st.spinner('🔄 시장 데이터 분석 중...'):
            model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            try:
                model.fit(monthly)
                joblib.dump(model, model_file)
                st.success(' 데이터 분석이 완료되었습니다!')
            except Exception as e:
                st.error(' 분석 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.')
                return

    st.markdown('---')

    # 상세 데이터 및 다운로드 섹션 - 스타일 변경
    st.subheader('② 경매가 예측하기')
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.95;'>
                💡  월별 경매 시세 예측을 확인하세요.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 가격 예측 수행
    future = model.make_future_dataframe(periods=months, freq='M')
    forecast = model.predict(future)

    # 예측 데이터 준비
    forecast_monthly = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_monthly['ds'] = pd.to_datetime(forecast_monthly['ds']).dt.to_period('M').dt.to_timestamp()

    # 데이터 테이블 표시
    with st.expander("월별 예측 시세 보기"):
        formatted_data = forecast_monthly.tail(months).copy()
        formatted_data['ds'] = formatted_data['ds'].dt.strftime('%Y년 %m월')
        formatted_data.columns = ['거래월', '예측가격', '최소예상가격', '최대예상가격']
        formatted_data['예측가격'] = formatted_data['예측가격'].apply(lambda x: f'{x:,.0f}원')
        formatted_data['최소예상가격'] = formatted_data['최소예상가격'].apply(lambda x: f'{x:,.0f}원')
        formatted_data['최대예상가격'] = formatted_data['최대예상가격'].apply(lambda x: f'{x:,.0f}원')
        st.dataframe(formatted_data, hide_index=True)

    st.markdown('')
    st.markdown('---')

    # 예측 결과 시각화 - Plotly 인터랙티브 차트
    st.subheader('② 예측 시세 그래프 보기')
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.95;'>
                💡  (실제 거래가 , 예측 가격 , 신뢰 구간) 상세 정보를 확인하세요.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Plotly 인터랙티브 차트 생성
    forecast_display = forecast.copy()
    forecast_display['ds'] = pd.to_datetime(forecast_display['ds'])
    
    # 실제 데이터와 예측 데이터 분리
    actual_data = monthly.copy()
    future_data = forecast_display[forecast_display['ds'] > actual_data['ds'].max()]
    
    # Figure 생성
    fig_plotly = go.Figure()
    
    # 1. 신뢰구간 (하한)
    fig_plotly.add_trace(go.Scatter(
        x=forecast_display['ds'],
        y=forecast_display['yhat_lower'],
        fill=None,
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 2. 신뢰구간 (상한) - 하한과 상한 사이 영역 채우기
    fig_plotly.add_trace(go.Scatter(
        x=forecast_display['ds'],
        y=forecast_display['yhat_upper'],
        fill='tonexty',
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(99, 110, 250, 0.2)',
        name='신뢰구간',
        hovertemplate='<b>신뢰구간</b><br>날짜: %{x|%Y년 %m월}<br>최대: %{y:,.0f}원<extra></extra>'
    ))
    
    # 3. 예측선
    fig_plotly.add_trace(go.Scatter(
        x=forecast_display['ds'],
        y=forecast_display['yhat'],
        mode='lines',
        name='예측 가격',
        line=dict(color='rgb(99, 110, 250)', width=3, dash='dot'),
        hovertemplate='<b>예측 가격</b><br>날짜: %{x|%Y년 %m월}<br>가격: %{y:,.0f}원<extra></extra>'
    ))
    
    # 4. 실제 데이터 (점과 선)
    fig_plotly.add_trace(go.Scatter(
        x=actual_data['ds'],
        y=actual_data['y'],
        mode='lines+markers',
        name='실제 거래가',
        line=dict(color='rgb(0, 204, 150)', width=3),
        marker=dict(size=6, color='rgb(0, 204, 150)', 
                line=dict(width=2, color='white')),
        hovertemplate='<b>실제 거래가</b><br>날짜: %{x|%Y년 %m월}<br>가격: %{y:,.0f}원<extra></extra>'
    ))
    
    # 5. 미래 예측 구간 강조
    if not future_data.empty:
        fig_plotly.add_vrect(
            x0=future_data['ds'].min(),
            x1=future_data['ds'].max(),
            fillcolor="rgba(255, 200, 0, 0.1)",
            layer="below",
            line_width=0,
            annotation_text="예측 구간",
            annotation_position="top left",
            annotation=dict(font_size=11, font_color="gray")
        )
    
    # 레이아웃 설정 - 가독성 개선 (모든 글씨 검정색)
    fig_plotly.update_layout(
    title={
        'text': f'<b>{species}</b> 경매가 동향 및 예측',
        'font': {'size': 22, 'color': '#000000', 'family': 'Arial Black'},  # 검정색
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis=dict(
        title='거래 시기',
        showgrid=True,
        gridcolor='rgba(150, 150, 150, 0.3)',
        gridwidth=1,
        dtick="M3",  # 3개월 간격
        tickformat='%Y년 %m월',
        tickfont=dict(size=12, color='#000000'),  # 검정색
        linecolor='#2c3e50',
        linewidth=2
    ),
    yaxis=dict(
        title='경매가 (원)',
        showgrid=True,
        gridcolor='rgba(150, 150, 150, 0.3)',
        gridwidth=1,
        tickformat=',',
        separatethousands=True,
        tickfont=dict(size=12, color='#000000'),  # 검정색
        linecolor='#2c3e50',
        linewidth=2
    ),
    hovermode='x unified',
    plot_bgcolor='#f8f9fa',  # 연한 회색 배경
    paper_bgcolor='white',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=13, color='#000000', family='Arial'),  # 검정색
        bgcolor='rgba(255, 255, 255, 0.9)',
        bordercolor='#dee2e6',
        borderwidth=1
    ),
    height=500,
    margin=dict(t=80, b=50, l=50, r=50)
    )

    # x축, y축 타이틀 폰트 스타일 별도 지정
    fig_plotly.update_xaxes(title_font=dict(size=15, color='#000000', family='Arial'))
    fig_plotly.update_yaxes(title_font=dict(size=15, color='#000000', family='Arial'))

    
    # Streamlit에 표시
    st.plotly_chart(fig_plotly, use_container_width=True)

    st.markdown('')
    st.markdown('---')

    # 주요 거래월 예측 결과 - 스타일 변경
    st.subheader('③ 주요 거래월 예상 경매가')
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <p style='margin: 5px 0 0 0; font-size: 14px; opacity: 0.95;'>
                💡선택하신 주요 거래월의 예상 경매가와 변동 범위입니다.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    last_training_date = monthly['ds'].max()
    future_forecasts = forecast_monthly[forecast_monthly['ds'] > last_training_date]

    # 연도별로 행을 만들고, 주요 달을 칼럼으로 정렬하여 metric 카드 형태로 표현
    years = sorted(future_forecasts['ds'].dt.year.unique())
    
    for year in years:
        year_data = future_forecasts[future_forecasts['ds'].dt.year == year]
        if year_data.empty:
            continue
        
        # 연도 헤더 - 도매상 친화적 디자인
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 10px 20px; border-radius: 8px; margin: 30px 0 10px 0;'>
                <h4 style='color: white; margin: 0; font-weight: 600;'>
                    {year}년 예상 경매가
                </h4>
            </div>
        """, unsafe_allow_html=True)

        # 선택한 월들에 대한 컬럼 생성
        cols = st.columns(len(selected_months_num))
        
        for col, month_num in zip(cols, selected_months_num):
            with col:
                row = year_data[year_data['ds'].dt.month == month_num]
                
                if row.empty:
                    # 데이터 없을 때 스타일
                    st.markdown(f"""
                        <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; 
                                    border-left: 4px solid #dee2e6; text-align: center;'>
                            <div style='color: #6c757d; font-size: 14px; font-weight: 600;'>
                                {month_num}월
                            </div>
                            <div style='color: #adb5bd; font-size: 12px; margin-top: 5px;'>
                                예측 범위 외
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    r = row.iloc[0]
                    predicted_price = r['yhat']
                    lower_bound = r['yhat_lower']
                    upper_bound = r['yhat_upper']
                    
                    # 가격 변동 추세 계산 (이전 월 대비)
                    prev_month_data = year_data[year_data['ds'].dt.month == month_num - 1]
                    if not prev_month_data.empty:
                        prev_price = prev_month_data.iloc[0]['yhat']
                        price_change = predicted_price - prev_price
                        change_pct = (price_change / prev_price) * 100
                        
                        if price_change > 0:
                            trend_color = "#dc3545"  # 빨강 (상승)
                            trend_icon = "📈"
                            trend_text = f"+{change_pct:.1f}%"
                        else:
                            trend_color = "#28a745"  # 초록 (하락)
                            trend_icon = "📉"
                            trend_text = f"{change_pct:.1f}%"
                    else:
                        trend_color = "#6c757d"
                        trend_icon = "➖"
                        trend_text = "-"
                    
                    # 도매상 친화적 카드 디자인
                    st.markdown(f"""
                        <div style='background: white; padding: 15px; border-radius: 8px;
                                    border: 2px solid #e9ecef; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                            <div style='color: #495057; font-size: 14px; font-weight: 600; margin-bottom: 8px;'>
                                {month_num}월 {trend_icon}
                            </div>
                            <div style='color: #212529; font-size: 20px; font-weight: 700; margin-bottom: 8px;'>
                                {predicted_price:,.0f}원
                            </div>
                            <div style='color: {trend_color}; font-size: 12px; font-weight: 600; margin-bottom: 8px;'>
                                {trend_text}
                            </div>
                            <div style='background: #f8f9fa; padding: 6px; border-radius: 4px; font-size: 11px;'>
                                <div style='color: #6c757d;'>변동 범위</div>
                                <div style='color: #495057; font-weight: 500;'>
                                    {lower_bound:,.0f}원<br>~ {upper_bound:,.0f}원
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    # 참고 사항
    st.markdown('---')
    with st.expander("ℹ데이터 신뢰도 안내"):
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


if __name__ == "__main__":
    run_ml()