import streamlit as st
from streamlit_float import float_init, float_box
import time

def chatbot_popup():
    float_init()

    if "open" not in st.session_state:
        st.session_state.open = False
    if "closing" not in st.session_state:
        st.session_state.closing = False

    def toggle():
        if st.session_state.open and not st.session_state.closing:
            # 닫기 클릭 시 닫기 애니메이션 활성화
            st.session_state.closing = True
            # rerun 없이 상태만 변경해 애니메이션 재생 대기
        elif not st.session_state.open:
            st.session_state.open = True

    # 버튼 스타일 CSS (기존 코드 유지)
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

    # 버튼 생성
    button_label = "챗봇 닫기" if st.session_state.open and not st.session_state.closing else "챗봇 문의"
    if st.button(button_label, key="custom_chatbot_btn", on_click=toggle, type="secondary"):
        pass

    # 팝업 float_box 호출 (열림 또는 닫힘 중 상태에서 계속 표시)
    if st.session_state.open or st.session_state.closing:
        animation_class = "close" if st.session_state.closing else "open"
        float_box(
            f"""
            <div class="fake_floating {animation_class}">
                <div class="custom-iframe-container">
                    <iframe src="https://app-gemini.streamlit.app/?embedded=true" width="100%" height="100%" frameborder="0" style="border-radius: 10px;"></iframe>
                </div>
            </div>
            <style>
            div.floating{{
                box-shadow: unset;
                padding: 0;
                right: var(--chatbot_right);
                height: var(--chatbot_height);
                top: calc(100% - var(--chatbot_height) - 4.8rem);
            }}
            div.floating > div.fake_floating {{
                width: inherit;
                height: inherit;
                position: inherit;
                animation-fill-mode: forwards;
                transform-origin: bottom center;
            }}
            div.fake_floating.open {{
                animation: growUp 0.4s ease-out forwards;
            }}
            div.fake_floating.close {{
                animation: shrinkDown 0.4s ease-in forwards;
            }}
            .custom-iframe-container {{
                width: inherit;
                height: inherit;
                overflow: hidden;
                border-radius: 10px;
                box-shadow: #434343 0px 0px 6px;
                background-color: #ccc;
            }}

            @keyframes growUp {{
                0% {{
                    transform: scale(0);
                    opacity: 0;
                    transform-origin: bottom right;
                }}
                100% {{
                    transform: scale(1);
                    opacity: 1;
                }}
            }}
            @keyframes shrinkDown {{
                0% {{
                    transform: scale(1);
                    opacity: 1;
                }}
                100% {{
                    transform: scale(0);
                    opacity: 0;
                    transform-origin: bottom right;
                }}
            }}
            </style>
            """,
            width="400px",
            height="600px",
            right="1.2rem",
            bottom="5.5rem",
            shadow=20,
        )

        # 닫힘 애니메이션 재생 대기 후 상태 초기화
        if st.session_state.closing:
            time.sleep(0.4)  # 애니메이션 지속 시간과 맞춰 조절
            st.session_state.open = False
            st.session_state.closing = False
