import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def run_home():
    st.header('-호갱제로-')
    st.subheader('어종별 경락 시세를 예측하는 웹대시보드')
    st.caption("🐟 투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션")
    st.subheader('')
    
    # 메인 설명 캡션 추가
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 14px; opacity: 0.95;">
    🌊 시장에서 가장 활발하게 거래되는 어종입니다. 원하시는 품종과 산지를 선택하여 시세를 확인해보세요.
    </p>
    </div>
    """, unsafe_allow_html=True)
    

    
    df=pd.read_csv('./data/갈치csv/2021/2021-1.csv')
    st.dataframe(df)


    st.header('최종 데이터 가공')
    df1 = pd.read_csv('./data/수산물_통합전처리_3컬럼.csv')
    st.dataframe(df1)


    