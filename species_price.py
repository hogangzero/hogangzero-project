import streamlit as st
import pandas as pd

def species_price() :
    # 데이터 로드
    df = pd.read_csv('./data/수산물_통합전처리_3컬럼.csv')
    st.info('어종별 2021 ~ 2024 월별 평균가 선그래프')

    ## 수산물의 모든 데이터 확인
    show_data = st.checkbox('모든 데이터 보기')  # 체크박스 생성
    if show_data:
        st.dataframe(df)

    

    # 어종 리스트 가져오기
    # species_list = df['파일어종'].unique()
    # selected_species = st.selectbox('어종 선택', species_list)

    # st.text(df[(df['파일어종'] == selected_species) & (df['평균가'])])

    # if selected_species:
    #     text = f"선택하신 어종은 {selected_species}의 평균가는 "
    #     st.info(text)


    # date 컬럼 datetime 변환
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 어종 리스트 만들기
    species_list = df['파일어종'].unique()
    selected_species = st.selectbox('어종 선택', species_list)

    # 선택한 어종 데이터 필터링
    filtered = df[df['파일어종'] == selected_species]

    # 날짜기준 정렬
    filtered = filtered.sort_values('date')

    # 선그래프에 표시할 데이터 정리
    chart_data = filtered.set_index('date')[['낙찰고가', '낙찰저가', '평균가']]

    # 선그래프 출력 (st.line_chart는 인덱스를 x축으로 사용)
    st.line_chart(chart_data)