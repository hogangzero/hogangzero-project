import streamlit as st
import pandas as pd

def run_home():
    st.caption("🐟 투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션")
    
    df=pd.read_csv('./data/갈치csv/2021/2021-1.csv')
    st.dataframe(df)


    st.header('최종 데이터 가공')
    df1 = pd.read_csv('./data/수산물_통합전처리_3컬럼.csv')
    st.dataframe(df1)