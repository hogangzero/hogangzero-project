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
    # st.header("호갱제로 안내 상담 Chatbot")
    rag_question = st.text_input(
        "", key="rag_question", placeholder="여기에 입력하세요"
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
        당신은 한국어로 답하는 수산물 데이터 전문 어시스턴트입니다.
        다음 규칙을 반드시 지키세요:
        - 아래에 제공된 PDF 데이터 조각을 근거로 하여 간결하고 정확하게 답변하세요.
        - 표, 수치, 날짜, 용어 등은 반드시 원문 데이터를 바탕으로 인용하세요.
        - 최근 트렌드, 패턴, 특이사항 설명 또는 비교가 필요한 경우 데이터 중심적으로 서술하세요.
        - 요청 내용과 직접 관련된 데이터가 없는 경우, 무리해서 가정하지 말고 '검색된 데이터에 근거한 답변이 어렵다'고 안내하세요.
        - 답변 마지막 줄에는 반드시 '출처: 호갱제로 사용설명서.pdf'라고 표시하세요.
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
