# 🐟 호갱제로(Hogangzero)

> 투명한 수산 시장을 위한 AI 기반 데이터 분석 솔루션

호갱제로는 수산물 도매 거래 시장의 가격 동향을 분석하고, 머신러닝과 시계열 예측 모델을 활용하여 미래 가격을 예측하는 종합 데이터 분석 플랫폼입니다. 
사용자는 직관적인 대시보드를 통해 실시간 시장 정보를 파악하고, AI 챗봇의 도움을 받아 효율적인 거래 의사결정을 할 수 있습니다.

---

## 📋 주요 기능

### 1️⃣ 홈 (데이터 조회)
- **전국 수산물 경매 데이터 조회**: 전국 주요 산지(군산, 여수, 제주, 통영, 안흥 등)의 실시간 경매가 정보 제공
- **어종별 가격 추이**: 12개 주요 어종별(갈치, 고등어, 꽁치, 넙치, 대구, 명태, 바지락, 오징어, 우럭, 전복, 조기, 홍어) 월단위 가격 변화 시각화
- **통계 분석**: 최고가, 최저가, 평균가 통계 제공

### 2️⃣ 시세 알아보기 (가격 비교 분석)
- **어종별 시세**: 선택한 어종의 산지별 경매가 비교 분석
- **산지별 시세**: 특정 산지의 전체 어종 경매가 조회
- **인터랙티브 시각화**: Plotly 기반 확대/축소, 필터링 가능한 동적 차트

### 3️⃣ 시세 예측하기 (AI 기반 가격 예측)

#### 📊 날짜별 예측
- **Prophet 시계열 모델**: 월단위 가격 데이터를 기반으로 향후 1~5년 가격 예측
- **계절성 분석**: 어종별 거래월(3월, 6월, 9월, 12월) 선택으로 중점 분석 가능
- **신뢰구간 제공**: 예측값과 함께 상한/하한 범위(yhat_lower, yhat_upper) 표시로 리스크 관리 지원
- **모델 우선순위**: prophet_best > prophet > baseline 순서로 최적 모델 자동 선택

#### 🎯 맞춤형 예측 (상세 검색)
- **RandomForest 머신러닝 모델**: 어종, 산지, 규격, 등급, 포장, 수량, 중량 등 세부 조건 기반 가격 예측
- **파이프라인 전처리**: OneHotEncoder로 카테고리형 데이터 처리, MinMaxScaler로 수치 표준화
- **하이퍼파라미터 최적화**: GridSearchCV/RandomizedSearchCV로 자동 튜닝된 모델 활용

### 4️⃣ AI 챗봇 (RAG 기반)
- **플로팅 UI**: 화면 우측 하단에 떠있는 챗봇 창으로 언제든 질문 가능
- **문서 기반 답변**: 호갱제로 사용설명서 PDF 기반 RAG(Retrieval Augmented Generation) 시스템
- **Google Gemini 연동**: Gemini 2.5-flash 모델로 자연스러운 한국어 답변 생성
- **의미 검색**: 사용자 질문과 관련된 상위 5개 문서를 자동으로 검색해 답변에 포함
- **보안**: Streamlit Secrets을 통해 API 키 안전 관리

---

## 🛠️ 기술 스택

### 백엔드 & 웹 프레임워크
- **Streamlit** (≥1.28.0): 데이터 분석 대시보드 및 웹 UI
- **streamlit_float**: 플로팅 챗봇 UI 구현
- **Python** 3.10+: 핵심 개발 언어

### 데이터 처리 & 분석
- **Pandas**: CSV 데이터 로딩, 전처리, 월단위 시계열 집계
- **NumPy**: 수치 계산 및 배열 연산
- **Seaborn**: 통계적 시각화 (상관분석, 분포)

### 시각화
- **Plotly** (express, graph_objects): 인터랙티브 차트
- **Matplotlib**: 정적 차트, 회귀 분석 시각화
- **koreanize_matplotlib**: 한글 폰트 자동 설정

### 머신러닝 & 예측 모델
- **scikit-learn (sklearn)**
  - RandomForestRegressor: 맞춤형 가격 예측
  - ColumnTransformer, Pipeline: 데이터 전처리 파이프라인
  - GridSearchCV, RandomizedSearchCV: 하이퍼파라미터 튜닝
  - 평가 메트릭: MSE, MAE, R² Score
  
- **Prophet**: 시계열 예측 (월단위 계절성 분석)
- **joblib**: 모델 아티팩트 직렬화 및 버전 관리

### LLM & RAG 시스템
- **LangChain** (core, community, text_splitters)
  - PDF 문서 로딩 및 청크 분할
  - 프롬프트 템플릿 관리
  - 체인 오케스트레이션
  
- **langchain_google_genai**
  - ChatGoogleGenerativeAI: Gemini 2.5-flash 모델
  - GoogleGenerativeAIEmbeddings: 벡터 임베딩 (gemini-embedding-001)
  
- **Chroma**: 벡터 데이터베이스 (로컬 파일 저장소)
- **PyPDF**: PDF 문서 로더

### 문서 생성
- **ReportLab**: PDF 사용설명서 자동 생성
- **Pillow (PIL)**: 이미지 처리

---

## 📁 프로젝트 구조

```
hogangzero-project/
├── app.py                              # 메인 Streamlit 앱 (페이지 라우팅)
├── streamlit_app.py                    # 배포 진입점
│
├── app_home.py                         # 홈 페이지 (데이터 조회)
├── app_species.py                      # 어종별 시세 분석
├── app_source.py                       # 산지별 시세 분석
├── app_ml.py                           # 날짜별 가격 예측 (Prophet)
├── app_ml2.py                          # 맞춤형 가격 예측 (RandomForest)
├── app_llm.py                          # RAG 챗봇 백엔드
├── app_chatbot.py                      # 챗봇 플로팅 UI
├── app_rag.py                          # PDF 문서 생성
├── app_status.py                       # 상태 페이지 (예정)
│
├── data/                               # 데이터 디렉토리
│   ├── 수산물_통합전처리_3컬럼.csv     # 시계열 분석 데이터 (날짜, 어종, 가격)
│   ├── ai데이터가공.csv                # ML 학습 데이터
│   ├── rag_df.csv, rag_df2.csv         # RAG 데이터
│   ├── 어종별.csv                      # 어종 마스터 데이터
│   ├── 갈치csv/, 고등어csv/, ...      # 12개 어종별 폴더 (연도별 월별 CSV)
│   └── 해양정보_추출/                  # 산지별 해양 환경 데이터 (기온, 수온, 풍속)
│
├── models/                             # 학습된 모델 아티팩트
│   ├── prophet_best_{species}.pkl      # Prophet 최적 모델
│   ├── prophet_{species}.pkl           # Prophet 모델
│   ├── baseline_{species}.pkl          # 기준 모델
│   └── trained_models_summary.csv      # 모델 메타데이터
│
├── best_randomforest.joblib            # RandomForest 최적 모델
├── model_xgboost.joblib                # XGBoost 모델
├── model_lightgbm.joblib               # LightGBM 모델
├── pipe.pkl                            # 전처리 파이프라인
│
├── pdf_storage/
│   └── chroma_fish/                    # Chroma 벡터 DB (RAG 저장소)
│       ├── chroma.sqlite3
│       └── {document_id}/
│
├── fonts/                              # 한글 폰트 파일
├── packages.txt                        # 시스템 폰트 패키지 (CJK, Nanum)
├── requirements.txt                    # Python 의존성
│
├── .streamlit/
│   └── config.toml                     # Streamlit 설정
│
├── 호갱제로_사용설명서.pdf             # RAG 챗봇 학습 문서
├── prophet_validation_summary.csv      # Prophet 모델 검증 결과
│
└── notebooks/                          # Jupyter 분석 노트북
    ├── AI.ipynb
    ├── Prophet.ipynb
    ├── 상세검색AI.ipynb
    ├── 데이터분석.ipynb
    ├── 데이터분석_12어종.ipynb
    ├── 기본데이터셋팅.ipynb
    ├── 고등어_데이터분석.ipynb
    ├── 기상_해양 환경 변수간의 상관분석.ipynb
    ├── 해양 정보 파악 2021~2024년도 데이터 추출.ipynb
    └── csv파일변환 및 가공테스트.ipynb
```

---

## 🚀 빠른 시작

### 요구사항
- Python 3.10 이상
- pip 또는 conda

### 1. 저장소 클론
```bash
git clone https://github.com/gwonhoemin/hogangzero-project.git
cd hogangzero-project
```

### 2. 가상환경 설정 (권장)
```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 시스템 폰트 설치 (Linux/Ubuntu)
```bash
sudo apt-get install fonts-noto-cjk fonts-nanum fonts-nanum-coding fonts-nanum-extra
```

### 5. Google API 키 설정 (RAG 챗봇 사용 시)

#### 로컬 개발 환경
`.streamlit/secrets.toml` 파일 생성:
```toml
GOOGLE_API_KEY = "your-google-api-key-here"
```

#### Streamlit Cloud 배포
1. [Streamlit Cloud](https://share.streamlit.io/) 로그인
2. 앱 설정 → Secrets에 `GOOGLE_API_KEY` 추가

### 6. 앱 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📊 주요 데이터

### 수산물 데이터
- **기간**: 2021년 1월 ~ 2024년 12월
- **어종**: 12개 (갈치, 고등어, 꽁치, 넙치, 대구, 명태, 바지락, 오징어, 우럭, 전복, 조기, 홍어)
- **산지**: 6개 (군산, 여수, 제주, 통영, 안흥, 산지통합)
- **항목**: 평균가, 최고가, 최저가, 거래량, 수량 등

### 해양 환경 데이터
- **기온, 수온, 풍속** (산지별)
- **상관분석**: 수산물 가격과 해양환경 변수 간의 상관성 분석

---

## 🤖 모델 아키텍처

### Prophet 시계열 예측
```
월별 시장 데이터 (csv) 
  ↓
Pandas 그룹화 및 집계 (resample('M').mean())
  ↓
Prophet 모델 학습 (로그 변환, 계절성=12개월)
  ↓
향후 N개월 예측 (forecast())
  ↓
신뢰구간과 함께 Plotly 시각화
```

### RandomForest 맞춤형 예측
```
세부 조건 입력 (어종, 산지, 규격, 등급, 포장, 수량, 중량)
  ↓
Pipeline 전처리
  - OneHotEncoder: 카테고리형 → 더미 변수
  - MinMaxScaler: 수치 정규화 [0, 1]
  ↓
RandomForest 예측 (n_estimators=200, n_jobs=-1)
  ↓
예상 가격 출력
```

### RAG 챗봇
```
사용자 질문
  ↓
Google Embedding (gemini-embedding-001)
  ↓
Chroma 벡터 DB 검색 (top-5)
  ↓
검색 결과 + 프롬프트 + 질문
  ↓
Gemini 2.5-flash 응답 생성
  ↓
한글 답변 반환
```

---

## ⚙️ 주요 설정

### Streamlit 설정 (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#2c3e50"
font = "sans serif"

[client]
showErrorDetails = true
```

### 모델 로딩 전략
- **우선순위**: prophet_best → prophet → baseline → 신규 학습
- **캐싱**: @st.cache_resource로 모델 싱글톤 관리
- **메모리**: joblib 직렬화로 효율적 저장/로드

---

## 📈 성능 최적화

### 데이터 처리
- Pandas resample(): 월단위 시계열 집계
- NumPy 벡터화: 반복 루프 제거
- joblib n_jobs=-1: RandomForest 병렬 처리

### 모델 캐싱
- @st.cache_data: 데이터 로드 결과 캐싱
- @st.cache_resource: 모델/벡터DB 싱글톤 관리

### 벡터 DB
- Chroma SQLite 백엔드: 빠른 벡터 검색
- 청크 크기 최적화: 800자 (오버랩 120자)

---

## 🔐 보안

### API 키 관리
```python
# Streamlit Secrets 사용
api_key = st.secrets.get("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key
```

### 다중 폴백 메커니즘
- 여러 키 이름 시도 (GOOGLE_API_KEY, google_api_key, OPENAI_API_KEY)
- 폰트 로딩 실패 시 시스템 기본값 자동 사용

---

## 🌍 배포

### Streamlit Cloud 배포
1. GitHub 저장소 연결
2. [share.streamlit.io](https://share.streamlit.io) → "New app"
3. Repository, branch, main file path 설정
4. Secrets에 GOOGLE_API_KEY 추가
5. Deploy 클릭

### 로컬 Streamlit 서버
```bash
streamlit run app.py
```

---

## 📝 사용 예시

### 가격 예측 시 거래 팁
- **분기별 가격 변동**: 3월, 6월, 9월, 12월 추이 주목
- **계절성 고려**: 어종별 성수기/비수기 파악
- **신뢰구간 활용**: 상한/하한으로 리스크 관리
- **장기 트렌드**: 연간 가격 흐름 파악

### 맞춤형 예측 활용
- 특정 산지의 특정 등급 수산물 가격 예측
- 거래량/중량별 가격 변화 분석
- 최적의 거래 조건 찾기

---

## 🐛 트러블슈팅

### 한글 폰트 렌더링 오류
**문제**: 그래프에 한글이 표시되지 않음
**해결**:
- koreanize_matplotlib 설치 확인: `pip install koreanize-matplotlib`
- 또는 시스템 폰트 설치: macOS는 AppleGothic, Linux는 Noto Sans CJK 설치

### Google API 키 오류
**문제**: "Google API 키가 설정되지 않았습니다" 에러
**해결**:
- .streamlit/secrets.toml 파일 생성 확인
- GOOGLE_API_KEY 값 확인
- Streamlit Cloud 배포 시 Secrets 메뉴에서 추가

### Chroma 벡터 DB 권한 오류
**문제**: "Permission Denied" 에러
**해결**:
- pdf_storage/chroma_fish 디렉토리 권한 확인
- `chmod 755 pdf_storage/chroma_fish` 실행

### 모델 로드 실패
**문제**: joblib.load() 에러
**해결**:
- models/ 디렉토리의 .pkl/.joblib 파일 존재 확인
- 파일이 손상된 경우 재학습 (Jupyter 노트북에서 실행)

---

## 📚 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Prophet 공식 문서](https://facebook.github.io/prophet/)
- [scikit-learn 공식 문서](https://scikit-learn.org/)
- [LangChain 공식 문서](https://python.langchain.com/)
- [Chroma 공식 문서](https://docs.trychroma.com/)

---

## 👨‍💻 개발자

**권회민** (Hoemin Gwon)
- GitHub: [@gwonhoemin](https://github.com/gwonhoemin)
- GitHub: [@devel-hj](https://github.com/devel-hj)
- GitHub: [@klop57](https://github.com/klop57)
- GitHub: [@kmjun3203](https://github.com/kmjun3203)


---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---

## 🤝 기여

이 프로젝트에 기여하고 싶으신가요?

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 문의

질문이나 피드백이 있으시면 이슈를 등록하거나 이메일로 연락주세요.

---

**마지막 업데이트**: 2026년 2월 11일