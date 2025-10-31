import os
import io
import joblib
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def _load_or_train_pipe(data_path, pipe_path):
    if os.path.exists(pipe_path):
        try:
            pipe = joblib.load(pipe_path)
            return pipe, 'loaded'
        except Exception:
            pass

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline

    df = pd.read_csv(data_path)
    required = ['파일어종', '산지_그룹화', '규격_등급', '포장_분류', '수량', '중량', '평균가']
    if not all(c in df.columns for c in required):
        raise RuntimeError(f"데이터에 필요한 컬럼이 없습니다. 필요: {required}. 현재 컬럼: {list(df.columns)}")

    X = df[['파일어종','산지_그룹화','규격_등급','포장_분류','수량','중량']].copy()
    y = df['평균가'].astype(float)

    ct = ColumnTransformer([
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['파일어종','산지_그룹화','규격_등급','포장_분류']),
        ('scaler', MinMaxScaler(), ['수량','중량'])
    ], remainder='drop')
    model = RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=42)
    pipe = Pipeline(steps=[('pre', ct), ('model', model)])

    sample = X.join(y).dropna()
    if len(sample) > 20000:
        sample = sample.sample(20000, random_state=42)
    X_train = sample[['파일어종','산지_그룹화','규격_등급','포장_분류','수량','중량']]
    y_train = sample['평균가']
    pipe.fit(X_train, y_train)
    try:
        joblib.dump(pipe, pipe_path)
    except Exception:
        pass
    return pipe, 'trained'


def run_ml2():
    st.set_page_config(
        page_title="수산물 맞춤형 경매가 예측",
        page_icon="🎯",
        layout="wide"
    )

    # 메인 타이틀
    st.markdown(
        "<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); "
        "padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>"
        "<h1 style='color: white; margin: 0;'>맞춤형 경매가 예측</h1>"
        "<p style='color: white; margin: 5px 0; opacity: 0.95;'>AI 기반 수산물 거래 가격 예측 시스템</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    st.markdown('---')
    
    st.markdown(
        "<div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); "
        "padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;'>"
        "<p style='margin: 0; font-size: 15px; opacity: 0.95;'> "
        "💡 좌측 메뉴에서 어종과 거래 조건을 선택하세요." 
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    data_path = os.path.join('data', 'ai데이터가공.csv')
    pipe_path = os.path.join('.', 'pipe.pkl')

    if not os.path.exists(data_path):
        st.error(f'데이터 파일이 없습니다: {data_path}')
        return

    df = pd.read_csv(data_path, usecols=['파일어종','산지_그룹화','규격_등급','포장_분류','수량','중량','평균가'])

    with st.spinner('모델 준비 중... (있으면 로드, 없으면 학습)'):
        try:
            pipe, status = _load_or_train_pipe(data_path, pipe_path)
        except Exception as e:
            st.error(f'모델 준비 실패: {e}')
            return

    files = sorted(df['파일어종'].dropna().unique())
    areas = sorted(df['산지_그룹화'].dropna().unique())
    sizes = sorted(df['규격_등급'].dropna().unique())
    packages = sorted(df['포장_분류'].dropna().unique())
    with st.sidebar:
        st.markdown('')
        st.markdown('---')

        st.subheader("🛒 거래 조건 설정")
        st.header("기본 정보")
        col1, col2 = st.columns(2)
        with col1:
            sel_file = st.selectbox('어종 선택', files)
            sel_area = st.selectbox('원산지 선택', areas)
        with col2:
            sel_size = st.selectbox('규격 등급 선택', sizes)
            sel_pack = st.selectbox('포장 형태 선택', packages)

        st.header("수량 정보")
        col3, col4 = st.columns(2)
        with col3:
            qty = st.number_input('수량 (단위)', min_value=0.0, value=1.0, step=1.0)
        with col4:
            weight = st.number_input('중량 (kg)', min_value=0.0, value=1.0, step=0.1)
        
        st.markdown('')  # 여백 추가
        st.markdown("""
            <div style='font-size:12px; color:#666;'>
            규격, 수량, 원산지 등을 신중히 선택해 거래 조건에 맞는 가격 예측을 받아보세요.
            </div>
        """, unsafe_allow_html=True)

    # 정보 배너 스타일 통일 적용
    def info_banner(text):
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                        padding: 8px; border-radius: 10px; color: white; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 14px; opacity: 1;">{text}</p>
            </div>
            """, unsafe_allow_html=True)

    with st.container():
        st.subheader('거래 조건 목록')

        # 선택한 거래 조건 표 형식으로 표시
        st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 10px; 
                        border: 2px solid #e9ecef; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        margin-bottom: 20px;'>
                <table style='width: 100%; border-collapse: separate; border-spacing: 0 10px;'>
                    <tr>
                        <td style='width: 30%; background: #f8f9fa; padding: 12px; border-radius: 8px;'>
                            <span style='color: #666;'>어종</span>
                        </td>
                        <td style='padding: 12px; font-weight: 600; color: #1e3d59;'>{sel_file}</td>
                        <td style='width: 30%; background: #f8f9fa; padding: 12px; border-radius: 8px;'>
                            <span style='color: #666;'>규격 등급</span>
                        </td>
                        <td style='padding: 12px; font-weight: 600; color: #1e3d59;'>{sel_size}</td>
                    </tr>
                    <tr>
                        <td style='width: 30%; background: #f8f9fa; padding: 12px; border-radius: 8px;'>
                            <span style='color: #666;'>원산지</span>
                        </td>
                        <td style='padding: 12px; font-weight: 600; color: #1e3d59;'>{sel_area}</td>
                        <td style='width: 30%; background: #f8f9fa; padding: 12px; border-radius: 8px;'>
                            <span style='color: #666;'>포장 형태</span>
                        </td>
                        <td style='padding: 12px; font-weight: 600; color: #1e3d59;'>{sel_pack}</td>
                    </tr>
                    <tr>
                        <td style='width: 30%; background: #f8f9fa; padding: 12px; border-radius: 8px;'>
                            <span style='color: #666;'>수량</span>
                        </td>
                        <td style='padding: 12px; font-weight: 600; color: #1e3d59;'>{qty:.0f} 단위</td>
                        <td style='width: 30%; background: #f8f9fa; padding: 12px; border-radius: 8px;'>
                            <span style='color: #666;'>중량</span>
                        </td>
                        <td style='padding: 12px; font-weight: 600; color: #1e3d59;'>{weight:.1f} kg</td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

        # 예측 버튼 및 결과
        if st.button(' 맞춤 가격 예측하기', key='predict', type='primary'):
            Xnew = pd.DataFrame([{
                '파일어종': sel_file,
                '산지_그룹화': sel_area,
                '규격_등급': sel_size,
                '포장_분류': sel_pack,
                '수량': float(qty),
                '중량': float(weight)
            }])
            try:
                pred = pipe.predict(Xnew)[0]
                model = None
                try:
                    model = pipe.named_steps.get(list(pipe.named_steps.keys())[-1])
                except Exception:
                    model = None
                lower, median, upper = (None, pred, None)
                if model is not None and hasattr(model, 'estimators_'):
                    preds = np.array([est.predict(pipe.named_steps['pre'].transform(Xnew))
                                      for est in model.estimators_])
                    lower = np.percentile(preds, 5)
                    median = np.percentile(preds, 50)
                    upper = np.percentile(preds, 95)
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                                padding: 15px; border-radius: 10px; color: white; margin: 20px 0;'>
                        <h3 style='color: white; margin: 0;'>💰 예측 경매가</h3>
                    </div>
                    <div style='background: white; padding: 25px; border-radius: 12px;
                                border: 2px solid #e9ecef; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
                        <h2 style='color: #1e3d59; margin: 0 0 10px 0;'>{sel_file}</h2>
                        <div style='font-size: 32px; font-weight: 700; color: #2a5298; margin: 15px 0;'>
                            {pred:,.0f}원
                        </div>
                        <div style='background: #f8f9fa; padding: 12px; border-radius: 8px; margin-top: 15px;'>
                            <div style='color: #666; font-size: 14px;'>예측 신뢰 구간 (5% ~ 95%)</div>
                            <div style='color: #1e3d59; font-size: 16px; font-weight: 500; margin-top: 5px;'>
                                {lower:,.0f}원 ~ {upper:,.0f}원
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # 다운로드
                out_df = Xnew.copy()
                out_df['예측가격'] = pred
                if lower is not None:
                    out_df['최소예상가격'] = lower
                    out_df['최대예상가격'] = upper
                csv_buf = io.StringIO()
                out_df.to_csv(csv_buf, index=False)
                st.download_button(
                    label='📥 예측 결과 다운로드 (CSV)',
                    data=csv_buf.getvalue(),
                    file_name=f'{sel_file}_맞춤가격예측.csv',
                    mime='text/csv'
                )
            except Exception as e:
                st.error(f'예측 실패: {e}')

        st.markdown('---')

        # AI 분석 정보 부분도 동일 스타일로
        info_banner("💡 AI 모델이 학습한 가격 영향 요인을 확인하세요.")

        try:
            last_key = list(pipe.named_steps.keys())[-1]
            model = pipe.named_steps[last_key]
            if hasattr(model, 'feature_importances_'):
                fi = model.feature_importances_
                feat_names = None
                try:
                    pre = pipe.named_steps.get('pre')
                    if pre and hasattr(pre, 'named_transformers_'):
                        ohe = pre.named_transformers_.get('onehot')
                        if ohe and hasattr(ohe, 'categories_'):
                            cat_names = []
                            cols = ['파일어종','산지_그룹화','규격_등급','포장_분류']
                            for i, cats in enumerate(ohe.categories_):
                                for c in cats:
                                    cat_names.append(f"{cols[i]}={c}")
                            feat_names = cat_names + ['수량','중량']
                except Exception:
                    feat_names = None
                if feat_names is None or len(feat_names) != len(fi):
                    feat_names = [f'factor_{i}' for i in range(len(fi))]
                fi_series = pd.Series(fi, index=feat_names).sort_values(ascending=False).head(10)
                fig, ax = plt.subplots(figsize=(6,4))
                bars = fi_series.plot(kind='barh', ax=ax,
                                    color='#4facfe',
                                    alpha=0.7)
                ax.invert_yaxis()
                ax.set_title('주요 가격 영향 요인', pad=20, fontsize=12)
                ax.set_xlabel('영향도', fontsize=10)
                ax.grid(True, alpha=0.3)
                for i in ax.patches:
                    width = i.get_width()
                    ax.text(width, i.get_y() + i.get_height()/2,
                           f'{width*100:.1f}%',
                           ha='left', va='center',
                           fontsize=9, color='#666')
                plt.tight_layout()
                st.pyplot(fig)
                st.markdown("""
                    <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px;'>
                        <span style='color: #666; font-size: 13px;'>
                            💡 그래프는 각 요인이 가격 결정에 미치는 영향력을 보여줍니다.
                            높은 퍼센트일수록 영향력이 큽니다.
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info('가격 영향 요인 분석을 사용할 수 없습니다.')
        except Exception:
            st.info('가격 영향 요인 분석을 불러올 수 없습니다.')
