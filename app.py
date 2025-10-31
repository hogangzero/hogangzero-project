import streamlit as st
from streamlit_float import float_init, float_box
from app_home import run_home
from app_ml import run_ml
from app_species import species_price
from app_source import source, source_species, source_price
from app_llm import run_llm
from app_ml2 import run_ml2


def main():

    float_init()

    if "open" not in st.session_state:
        st.session_state.open = False

    def toggle():
        st.session_state.open = not st.session_state.open

    # 버튼 스타일 적용 CSS (key가 custom_chatbot_btn인 버튼 대상으로)
    st.markdown("""
    <style>
    :root{
        --chatbot_right : 1rem;
        --chatbot_height : 78vh;
        
    }
    div.st-key-custom_chatbot_btn div.stButton > button[kind="secondary"] {
        width: 8rem;
        height: 3.2rem; 
        border-radius: 50px;
        background: linear-gradient(90deg, #667eea, #5a67d8) !important;
        color: #fff;
        border: none;
        cursor: pointer !important;
        transition: background 0.3s ease !important;
        position: fixed;
        right: var(--chatbot_right);
        bottom: 2%;
        z-index: 99999;
    }
    div.st-key-custom_chatbot_btn div.stButton > button[kind="secondary"]:hover,
    div.st-key-custom_chatbot_btn div.stButton > button[kind="secondary"]:active {
        background: linear-gradient(90deg, #5a67d8, #556cd6) !important;
    }
    
    </style>
    """, unsafe_allow_html=True)


    # 버튼 생성 (type="secondary" 스타일, key 지정)
    button_label = "챗봇 닫기" if st.session_state.open else "챗봇 문의"
    if st.button(button_label, key="custom_chatbot_btn", on_click=toggle, type="secondary"):
        pass

    # 챗봇 팝업 float_box
    if st.session_state.open:
        float_box(
            """
            <div class="fake_floating">
                <div class="custom-iframe-container">
                    <iframe src="https://app-gemini.streamlit.app/?embedded=true" width="100%" height="100%" frameborder="0" style="border-radius: 10px;"></iframe>
                </div>
            </div>
            <style>
            div.floating{
                box-shadow: unset;
                padding: 0;
                right: var(--chatbot_right);
                height: var(--chatbot_height);
                top: calc(100% - var(--chatbot_height) - 4.8rem);
            }
            div.floating > div.fake_floating {
                width: inherit;
                height: inherit;
                position: inherit;
            }
            .custom-iframe-container {
                width: inherit;
                height: inherit;
                overflow: hidden;
                border-radius: 10px;
                box-shadow: #434343 0px 0px 6px;
                background-color: #ccc;
            }
            </style>
            """,
            width="400px",
            height="600px",
            right="1.2rem",
            bottom="5.5rem",
            shadow=20,
        )








    
    menu = ['홈', '시세 알아보기', '시세 예측하기']
    sub_menu = ['어종별 시세', '산지별 시세']
    ml_menu = ['날짜별 예측','상세 검색 예측']


    st.sidebar.markdown("""
    <div style='text-align: center; padding: 0px 0;'>
        <h1 style='color: #667eea; margin: 0; font-size: 45px;'>호갱제로</h1>
        <p style='color: #666; font-size: 13px; margin-top: 1px;'>
            투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar: 
        st.markdown('---')
    
    st.sidebar.title("")    
    choice = st.sidebar.selectbox('메뉴', menu)
    


    if choice == menu[0]:
        run_home()
    elif choice == menu[1]:
        sub_choice = st.sidebar.selectbox('경매가', sub_menu)
        if sub_choice == sub_menu[0] :
            species_price() # 어종별 경매가
        elif sub_choice == sub_menu[1] :
            source_price()
            source() # 산지별 경매가
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