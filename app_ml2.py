import os
import io
import joblib
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def _load_or_train_pipe(data_path, pipe_path):
    # Try load
    if os.path.exists(pipe_path):
        try:
            pipe = joblib.load(pipe_path)
            return pipe, 'loaded'
        except Exception:
            pass

    # Fallback: build and train a simple pipeline
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
        ('onehot', OneHotEncoder(handle_unknown='ignore'), [0,1,2,3]),
        ('scaler', MinMaxScaler(), [4,5])
    ])
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
    st.set_page_config(page_title='피처 기반 예측 (Designer UI)', layout='wide')

    # Header
    st.markdown("""
    <div style='text-align:center'>
    <h1 style='margin:6px 0'>상세 가격 예측</h1>
    <p style='color:gray;margin:0'>어종, 산지, 규격, 포장, 수량, 중량을 입력하면 상세한 평균 가격을 예측합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    data_path = os.path.join('data', 'ai데이터가공.csv')
    pipe_path = os.path.join('.', 'pipe.pkl')

    if not os.path.exists(data_path):
        st.error(f'데이터 파일이 없습니다: {data_path}')
        return

    # Load data (for dropdown lists) but keep minimal memory
    df = pd.read_csv(data_path, usecols=['파일어종','산지_그룹화','규격_등급','포장_분류','수량','중량','평균가'])

    # Load or train pipeline
    with st.spinner('모델 준비 중... (있으면 로드, 없으면 학습)'):
        try:
            pipe, status = _load_or_train_pipe(data_path, pipe_path)
        except Exception as e:
            st.error(f'모델 준비 실패: {e}')
            return

    # Sidebar inputs
    st.sidebar.header('상세 선택')
    files = sorted(df['파일어종'].dropna().unique())
    areas = sorted(df['산지_그룹화'].dropna().unique())
    sizes = sorted(df['규격_등급'].dropna().unique())
    packages = sorted(df['포장_분류'].dropna().unique())

    sel_file = st.sidebar.selectbox('어종', files, index=0)
    sel_area = st.sidebar.selectbox('원산지', areas, index=0)
    sel_size = st.sidebar.selectbox('규격 등급', sizes, index=0)
    sel_pack = st.sidebar.selectbox('포장 상태', packages, index=0)
    qty = st.sidebar.number_input('수량', min_value=0.0, value=1.0, step=1.0)
    weight = st.sidebar.number_input('중량(kg)', min_value=0.0, value=1.0, step=0.1)

    # Main area: predict button and results
    st.header('')
    st.markdown('---')
    
    left, right = st.columns([2,1])

    with left:
        st.subheader('설정 목록')
        st.write(f'- 어종: **{sel_file}**')
        st.write(f'- 산지 그룹: **{sel_area}**')
        st.write(f'- 규격 등급: **{sel_size}**')
        st.write(f'- 포장: **{sel_pack}**')
        st.write(f'- 수량: **{qty}**')
        st.write(f'- 중량: **{weight} kg**')
        st.markdown('')

        if st.button('예측하기', key='predict'):
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

                # Confidence via tree ensemble percentiles if possible
                model = None
                try:
                    # get last estimator in pipeline
                    if hasattr(pipe, 'named_steps'):
                        last_key = list(pipe.named_steps.keys())[-1]
                        model = pipe.named_steps[last_key]
                    else:
                        model = pipe.steps[-1][1]
                except Exception:
                    model = None

                lower, median, upper = (None, pred, None)
                if model is not None and hasattr(model, 'estimators_'):
                    preds = np.array([est.predict(pipe.named_steps['pre'].transform(Xnew)) if ('pre' in pipe.named_steps and hasattr(pipe.named_steps['pre'], 'transform')) else est.predict(Xnew) for est in model.estimators_])
                    # preds shape (n_estimators, 1)
                    preds = preds.reshape(len(preds), -1)
                    lower = np.percentile(preds, 5)
                    median = np.percentile(preds, 50)
                    upper = np.percentile(preds, 95)

                # Designer card
                st.markdown(f"""
                <div style='background:linear-gradient(90deg,#fff,#f3f9ff);padding:18px;border-radius:12px;box-shadow:0 8px 24px rgba(15,15,15,0.06)'>
                <h2 style='margin:0 0 6px 0'>{sel_file} 예측 평균가</h2>
                <p style='font-size:28px;margin:4px 0'><b>{pred:,.0f} 원</b></p>
                <p style='color:gray;margin:0'>추정중앙값: {median:,.0f}원</p>
                </div>
                """, unsafe_allow_html=True)

                if lower is not None:
                    st.write(f'신뢰구간 (5%~95%): {lower:,.0f}원 ~ {upper:,.0f}원')

                # Download as CSV
                out_df = Xnew.copy()
                out_df['pred'] = pred
                if lower is not None:
                    out_df['lower_5pct'] = lower
                    out_df['upper_95pct'] = upper
                csv_buf = io.StringIO()
                out_df.to_csv(csv_buf, index=False)
                st.download_button('예측 결과 다운로드 (CSV)', csv_buf.getvalue(), file_name=f'prediction_{sel_file}.csv', mime='text/csv')

            except Exception as e:
                st.error(f'예측 실패: {e}')

    with right:
        st.subheader('모델 정보')
        st.write(f'- 상태: **{status}**')
        st.write(f'- 저장된 파이프: `{pipe_path}`')

        # Feature importances
        try:
            last_key = list(pipe.named_steps.keys())[-1]
            model = pipe.named_steps[last_key]
            if hasattr(model, 'feature_importances_'):
                fi = model.feature_importances_
                # try to build feature names
                feat_names = None
                try:
                    pre = pipe.named_steps.get('pre') or pipe.named_steps.get('preprocessing')
                    if pre is not None and hasattr(pre, 'named_transformers_'):
                        ohe = pre.named_transformers_.get('onehot')
                        if ohe is not None and hasattr(ohe, 'categories_'):
                            cat_names = []
                            cols = ['파일어종','산지_그룹화','규격_등급','포장_분류']
                            for col_idx, cats in enumerate(ohe.categories_):
                                for c in cats:
                                    cat_names.append(f"{cols[col_idx]}={c}")
                            feat_names = cat_names + ['수량','중량']
                except Exception:
                    feat_names = None

                if feat_names is None or len(feat_names) != len(fi):
                    feat_names = [f'f{i}' for i in range(len(fi))]

                fi_series = pd.Series(fi, index=feat_names).sort_values(ascending=False).head(10)
                fig, ax = plt.subplots(figsize=(6,3))
                fi_series.plot(kind='barh', ax=ax, color='#2b8cbe')
                ax.invert_yaxis()
                ax.set_title('Top feature importances')
                st.pyplot(fig)
            else:
                st.info('모델에 feature_importances_가 없습니다.')
        except Exception as e:
            st.info('피쳐 중요도 표시 실패')

    st.markdown('---')
    st.markdown('작동 환경: scikit-learn, pandas, joblib 필요. 파이프가 없으면 샘플로 학습하여 `pipe.pkl`을 생성합니다.')
