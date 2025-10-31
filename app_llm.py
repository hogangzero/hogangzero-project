# import os
# import pandas as pd
# import streamlit as st
# from pathlib import Path
# from langchain_core.documents import Document
# from langchain_community.vectorstores import Chroma
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_text_splitters import CharacterTextSplitter

# # ----- ML 예측 챗봇 함수 -----
# def ml_predict_section():
#     st.header("경매가 예측 챗봇")
#     question = st.text_input("질문을 입력하세요 (예: 2025년 1월 제주도산 갈치 평균가를 예측해줘)", key="ml_question")
#     @st.cache_resource
#     def prepare():
#         df = pd.read_csv("./data/rag_df2.csv")
#         feature_cols = ['파일어종', '전처리', '산지', '기온 평균', '수온 평균', '풍속 평균', 'year', 'month']
#         X = df[feature_cols].copy()
#         y = df['평균가']
#         for col in ['파일어종', '전처리', '산지', 'year', 'month']:
#             X[col] = X[col].astype(str)
#         from sklearn.ensemble import RandomForestRegressor
#         from sklearn.preprocessing import OneHotEncoder, StandardScaler
#         from sklearn.compose import ColumnTransformer
#         from sklearn.model_selection import train_test_split
#         ct = ColumnTransformer([
#             ('onehot', OneHotEncoder(handle_unknown="ignore"), [0,1,2,6,7]),
#             ('scaler', StandardScaler(), [3,4,5])
#         ])
#         X_ct = ct.fit_transform(X)
#         X_train, X_test, y_train, y_test = train_test_split(X_ct, y, test_size=0.2, random_state=29)
#         model = RandomForestRegressor()
#         model.fit(X_train, y_train)
#         return df, model, ct, feature_cols

#     df, model, ct, feature_cols = prepare()
#     if question:
#         import re
#         match = re.search(r"(\d{4})년\s*(\d{1,2})월\s*([가-힣]+)산\s*([가-힣]+)", question)
#         ml_pred = None
#         ml_input = None
#         if match:
#             year = int(match.group(1))
#             month = int(match.group(2))
#             origin = match.group(3)
#             species = match.group(4)
#             partial_input = {'파일어종': species, '산지': origin, 'year': year, 'month': month}
#             def complete_features(df, partial_input):
#                 filt = (
#                     (df['파일어종'] == partial_input['파일어종'])
#                     & (df['산지'] == partial_input['산지'])
#                     & (df['year'].astype(str) == str(partial_input['year']))
#                     & (df['month'].astype(str) == str(partial_input['month']))
#                 )
#                 df_sub = df[filt]
#                 result = dict(partial_input)
#                 fill_cols = ['전처리', '기온 평균', '수온 평균', '풍속 평균']
#                 for col in fill_cols:
#                     if len(df_sub) > 0:
#                         result[col] = df_sub[col].mode()[0] if df_sub[col].dtype == 'O' else float(df_sub[col].mean())
#                     else:
#                         result[col] = df[col].mode()[0] if df[col].dtype == 'O' else float(df[col].mean())
#                 return result
#             ml_input = complete_features(df, partial_input)
#             values = [str(ml_input.get(col)) if col in ['파일어종','전처리','산지','year','month'] else ml_input.get(col) for col in feature_cols]
#             X_query = pd.DataFrame([values], columns=feature_cols)
#             X_query_ct = ct.transform(X_query)
#             ml_pred = model.predict(X_query_ct)[0]
#             st.success(f"ML 평균가 예측: {ml_pred:.2f} 원")
#         else:
#             st.info("질문에서 'YYYY년 MM월 OO산 OO' 형태를 인식하지 못했습니다.")

# # ----- RAG LLM 기반 CSV 정보검색 함수 -----
# def rag_llm_section():
#     st.header("CSV 기반 정보 검색 챗봇")
#     rag_question = st.text_input(
#         "CSV 데이터 Q&A 질문을 입력하세요 (예: 수온이 25도 이상인 날의 갈치의 평균가를 알려줘)", key="rag_question"
#     )
#     @st.cache_resource
#     def prepare_rag():
#         CSV_PATH = "./data/rag_df.csv"
#         CHROMA_DIR = "./csv_storage/chroma_fish"
#         EMBED_MODEL = "text-embedding-004"
#         LLM_MODEL = "gemini-2.5-flash"
#         os.environ["GOOGLE_API_KEY"] = "AIzaSyC_Jj_qbteCJCC5mwCY3AUR05oFCUGGQiQ"
#         df = pd.read_csv(CSV_PATH)
#         docs = []
#         splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#         for idx, row in df.iterrows():
#             text = (
#                 f"파일어종: {row['파일어종']}, 전처리: {row['전처리']}, 산지: {row['산지']}, 날짜: {row['date']}, "
#                 f"기온평균: {row['기온 평균']}, 수온평균: {row['수온 평균']}, 풍속평균: {row['풍속 평균']}"
#             )
#             # 길이 분할(1000자 이하)
#             for chunk in splitter.split_text(str(text)):
#                 docs.append(Document(page_content=chunk, metadata={"row": int(idx)}))
#         # ---- Chroma 폴더 무조건 삭제하여 깨끗하게 재생성 ----
#         if Path(CHROMA_DIR).exists():
#             import shutil
#             shutil.rmtree(CHROMA_DIR)
#         embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
#         vectordb = Chroma.from_documents(
#             documents=docs,
#             embedding=embeddings,
#             persist_directory=CHROMA_DIR,
#         )
#         system_prompt = """
#         당신은 한국어로 답하는 수산물 데이터 전문 어시스턴트입니다.
#         다음 규칙을 반드시 지키세요:
#         - 아래에 제공된 데이터(row 및 요약)를 근거로 하여 간결하고 정확하게 답변하세요.
#         - 표, 수치, 날짜, 어종명, 산지명 등은 반드시 원문 데이터를 바탕으로 인용하세요.
#         - 최근 트렌드, 패턴, 특이사항 설명 또는 비교가 필요한 경우 데이터 중심적으로 서술하세요.
#         - 요청 내용과 직접 관련된 데이터가 없는 경우, 무리해서 가정하지 말고 '검색된 데이터에 근거한 답변이 어렵다'고 안내하세요.
#         - 답변 마지막 줄에는 반드시 '출처: 수산물 CSV 데이터'라고 표시하세요.
#         """
#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human", "질문: {question}\n\n다음은 검색된 데이터 조각입니다:\n{context}")
#         ])
#         llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2)
#         def format_docs(docs):
#             out = []
#             for i, d in enumerate(docs, 1):
#                 meta = d.metadata or {}
#                 row = meta.get("row", "N/A")
#                 out.append(f"[{i}] (row {row}) {d.page_content[:800]}")
#             return "\n\n".join(out)
#         retriever = vectordb.as_retriever(search_kwargs={"k": 5})
#         retriever_step = {
#             "context": lambda x: format_docs(retriever.invoke(x["question"])),
#             "question": lambda x: x["question"]
#         }
#         chain = retriever_step | prompt | llm | StrOutputParser()
#         return chain
#     chain = prepare_rag()
#     if rag_question:
#         answer = chain.invoke({"question": rag_question})
#         st.success(answer)

# # ---- Streamlit 실제 앱 ----
# def run_llm(*args, **kwargs):
#     ml_predict_section()
#     st.divider()
#     rag_llm_section()
import streamlit as st

def run_llm():
    pass