import streamlit as st
import joblib
import matplotlib.pyplot as plt
from prophet import Prophet

def run_ml():
    st.header('날짜별 어종 경락가 예측')

    model = joblib.load('./model.pkl')

    future = model.make_future_dataframe(periods=12, freq='M')  # 향후 12개월 예측
    forecast = model.predict(future)
    
    
    model.plot(forecast)
    