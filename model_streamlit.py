import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import joblib
import platform

mpl.rc('font', family='Malgun Gothic' if platform.system() == 'Windows' else 'AppleGothic')
mpl.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    return pd.read_csv("./model/data.csv", parse_dates=["날짜"])

@st.cache_resource
def load_model():
    return joblib.load("./model/model.pkl")

def predict(model, input_df):
    return model.predict(input_df)

st.set_page_config(layout="wide")
st.title("😷 마스크 수요 예측 대시보드")
st.markdown("날씨, 대기오염, 계절 요인을 고려한 예측 기반 수급 판단 도구입니다.")

# 데이터 및 모델 로딩
data = load_data()
model = load_model()

# 날짜 선택
min_date = data['날짜'].min().date()
max_date = data['날짜'].max().date()
selected_date = st.date_input("📅 예측 날짜 선택", value=max_date, min_value=min_date, max_value=max_date)
row = data[data['날짜'].dt.date == selected_date]

if row.empty:
    st.warning("해당 날짜의 데이터가 없습니다.")
else:
    st.subheader(f"📌 입력 변수 요약 ({selected_date})")
    st.dataframe(row.drop(columns=['Sales Amt']))

    X_input = row.drop(columns=['Sales Amt', '날짜'])
    y_true = row['Sales Amt'].values[0]
    y_pred = predict(model, X_input)[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("예측 판매량 (log)", f"{y_pred:.2f}")

    # 환경 요인 분석
    st.subheader("🌤 환경 요인 분석")
    env_cols = [col for col in row.columns if any(x in col for x in ['PM10', 'PM25', 'O3', 'CO', 'NO2', 'SO2', '습도', '습도(%)'])]
    humidity_val = None
    if '습도' in row.columns:
        humidity_val = row['습도'].values[0]
    elif '습도(%)' in row.columns:
        humidity_val = row['습도(%)'].values[0]

    if env_cols:
        st.dataframe(row[env_cols].T.rename(columns={row.index[0]: '값'}))
    else:
        st.info("환경 요인 정보가 없습니다.")

    # 계절 정보 판단
    season = row['날짜'].dt.month.iloc[0]
    if season in [3, 4, 5]:
        st.info("봄철: 미세먼지 영향 가능성 ↑, 수요 증가 경향")
    elif season in [6, 7, 8]:
        st.info("여름철: 수요 감소 경향 (착용 감소)")
    elif season in [9, 10, 11]:
        st.info("가을철: 수요 회복세")
    else:
        st.info("겨울철: 감기/미세먼지 등 복합 영향으로 수요 증가")

    # 종합 수급 판단
    st.subheader("🧾 수급 필요성 종합 지표")
    if humidity_val is not None:
        if y_pred > y_true and humidity_val < 40:
            st.warning("예측 수요가 높고 습도가 낮음 → 건조한 대기 조건에서 수요 증가 가능성 있음 → 선제적 공급 권장")
        elif y_pred < y_true:
            st.info("예측 수요가 실제보다 낮음 → 공급 과잉 위험 여부 검토 필요")
        else:
            st.success("예측 수요와 실제 수요가 유사 → 현재 공급 수준 유지 가능")
    else:
        if y_pred > y_true:
            st.warning("예측 수요가 실제보다 높음 → 수요 증가 가능성 존재")
        elif y_pred < y_true:
            st.info("예측 수요가 실제보다 낮음 → 공급 과잉 위험 여부 검토 필요")
        else:
            st.success("예측 수요와 실제 수요가 유사 → 현재 공급 수준 유지 가능")