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
    div.st-key-custom_chatbot_btn div.stButton > button[kind="secondary"] {
        width: 180px !important;
        height: 60px !important;
        font-size: 20px !important;
        border-radius: 50px !important;
        background: linear-gradient(90deg, #667eea, #5a67d8) !important;
        color: white !important;
        border: none !important;
        cursor: pointer !important;
        transition: background 0.3s ease !important;
        position: fixed;
        right: 1.2rem;
        bottom: 2%;
        z-index: 99999;
    }
    div.st-key-custom_chatbot_btn div.stButton > button[kind="secondary"]:hover {
        background: linear-gradient(90deg, #5a67d8, #556cd6) !important;
    }
    div.st-key-custom_chatbot_btn div.stButton > button[kind="secondary"]:active {
        background: linear-gradient(90deg, #556cd6, #4a57b3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 위치 고정을 위해 float_box를 빈 컨테이너로 띄워 좌표 조정(아래)
    float_box("", right="1.2rem", bottom="0.2rem", width="0px", height="0px")

    # 버튼 생성 (type="secondary" 스타일, key 지정)
    if st.button("챗봇 문의", key="custom_chatbot_btn", type="secondary"):
        toggle()

    # 챗봇 팝업 float_box
    if st.session_state.open:
        float_box(
            """
            <div style='position: relative; width: 100%; height: 100%;'>
                <button onclick="window.parent.postMessage('toggle_chatbot', '*')" 
                    style='position: absolute; top: 10px; right: 0px; font-size: 24px; border: none; background: none; cursor: pointer;'>×</button>
                <iframe src="https://app-gemini.streamlit.app/?embedded=true" width="100%" height="100%" frameborder="0" style="border-radius: 10px;"></iframe>
            </div>
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