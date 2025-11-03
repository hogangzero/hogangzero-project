import os
import streamlit as st
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

def rag_llm_inner_ui():
    st.header("호갱제로 안내 상담 Chatbot")
    rag_question = st.text_input(
        "이용 중 모르시는 부분은 챗봇에게 물어보세요!", key="rag_question"
    )
    
    @st.cache_resource
    def prepare_rag():
        PDF_PATH = "./data/호갱제로_사용설명서.pdf"
        CHROMA_DIR = "./pdf_storage/chroma_fish"
        EMBED_MODEL = "text-embedding-004"
        LLM_MODEL = "gemini-2.5-flash"
        os.environ["GOOGLE_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        
        # PDF → 문서 객체 변환
        loader = PyPDFLoader(PDF_PATH)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
        docs = splitter.split_documents(pages)
        
        # ---- Chroma 폴더 무조건 삭제하여 깨끗하게 재생성 ----
        if Path(CHROMA_DIR).exists():
            import shutil
            shutil.rmtree(CHROMA_DIR)
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=CHROMA_DIR,
        )
        system_prompt = """
        당신은 '호갱제로'라는 수산물 가격 데이터 분석 대시보드의 설명서, 시스템 사용법, FAQ, 전문 용어 등을 기반으로 답변하는 AI 비서입니다. 
        다음의 지침을 따릅니다.:
        - 답변은 한국어로, 명확하고 친절하게 작성합니다.
        - 질문에 대해 항상 대시보드의 공식 기능, 데이터 출처, 분석 방식, Chart 해석법, FAQ, 문제 해결 가이드를 기반으로 정확하게 답변하세요.
        - 사용자가 앱 기본 기능(데이터 조회, 가격 비교, 예측 기능, 해양환경 영향 분석, 챗봇 등)에 대해 묻는 경우 구체적 사용법과 주요 화면(홈, 시세, 예측, 챗봇 등) 안내 절차를 안내하세요.
        - 예측값, 신뢰구간, AI 모델(Prophet, Random Forest), 해양환경 데이터, 데이터 기준 정보(수산물유통정보시스템, FIPS 등)에 대한 질문엔 설명서 내용만 바탕으로 설명하고 가정/추측을 하지 않습니다.
        - 각종 메트릭과 데이터 해석, 시각화(Plotly 기반 차트), 주요 사용 주의사항 및 제약(예: 데이터가 부족할 때/예측 불확실성/웹·브라우저 요구사양 등)은 반드시 안내하세요.
        - 사용자가 너무 모호한 질문을 하면 “더 구체적으로 질문해 달라”고 요청할 수 있습니다.
        - RAG 답변 능력에 맞춰, 시스템 내 정보 외 주관적인 조언, 추론이나 직접적인 점치는 문장은 하지 않습니다.
        - 용어, 데이터 구조, 권장 사양 등 요청하면 각 설명서를 기반으로 표, 리스트, 개념해설로 안내하세요.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "질문: {question}\n\n다음은 검색된 데이터 조각입니다:\n{context}")
        ])
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.2)
        def format_docs(docs):
            out = []
            for i, d in enumerate(docs, 1):
                meta = d.metadata or {}
                page = meta.get("page", "N/A")
                out.append(f"[{i}] (p.{page}) {d.page_content[:800]}")
            return "\n\n".join(out)
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})
        retriever_step = {
            "context": lambda x: format_docs(retriever.invoke(x["question"])),
            "question": lambda x: x["question"]
        }
        chain = retriever_step | prompt | llm | StrOutputParser()
        return chain

    chain = prepare_rag()
    if rag_question:
        answer = chain.invoke({"question": rag_question})
        st.markdown(
            f"""
            <div style='background:#f4f8fc;padding:16px;border-radius:10px;border:1px solid #dbeafe;margin-top:20px;'>
            <b>답변</b>:<br>{answer}
            </div>
            """, unsafe_allow_html=True
        )

# ---- Streamlit 실제 앱 ----
def run_llm(*args, **kwargs):
    st.divider()
    rag_llm_inner_ui()
