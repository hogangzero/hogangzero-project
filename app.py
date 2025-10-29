import streamlit as st

from app_home import run_home
from app_ml import run_ml
from app_species import species_price
from app_source import source, source_species, source_price
from app_llm import run_llm
from app_ml2 import run_ml2

def main():

    menu = ['홈', '시세 알아보기', '시세 예측하기', '챗봇']
    sub_menu = ['어종별 경락가', '산지별 경락가']
    ml_menu = ['날짜별 예측하기','상세 예측하기']


    st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #667eea; margin: 0; font-size: 50px;'>호갱제로</h1>
        <p style='color: #666; font-size: 16px; margin-top: 6px;'>
            투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션
        </p>
    </div>
    """, unsafe_allow_html=True)


    
    st.sidebar.title("")    
    choice = st.sidebar.selectbox('메뉴', menu)
    
    

    if choice == menu[0]:
        run_home()
    elif choice == menu[1]:
        sub_choice = st.sidebar.selectbox('경락가', sub_menu)
        if sub_choice == sub_menu[0] :
            species_price() # 어종별 경락가
        elif sub_choice == sub_menu[1] :
            source_price()
            source() # 산지별 경락가
            source_species()
        
    elif choice == menu[2]:
        ml_choice = st.sidebar.selectbox('예측 방법', ml_menu)
        if ml_choice == ml_menu[0]:
            run_ml()
        elif ml_choice == ml_menu[1]:
            run_ml2()
    elif choice == menu[3]:
        run_llm()

    
if __name__ == '__main__':
    main()