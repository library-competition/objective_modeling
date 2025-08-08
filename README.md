# READING_COMPASS
![preview1](https://github.com/user-attachments/assets/6498b32d-499e-44ea-b1a6-7c3a654170be)  




**독서나침반**은 사용자의 **독서 목적**과 **난이도**를 반영해 도서를 추천하는 웹 앱입니다.  
백엔드(FastAPI)에서 추천 API를 제공하고, `web/`의 정적 페이지에서 API를 호출해 결과를 보여줍니다.
또한 `app.py`를 실행하면 터미널 환경에서 동일한 추천 로직을 수행하며, 콘솔 출력으로 로우 데이터와 중간 계산 과정을 직접 확인할 수 있습니다.




## 요구사항

- Python 3.10+ (3.11/3.12/3.13 동작 확인)
- pip 최신 버전
- (Windows 권장) PowerShell




## 설치 & 실행

### 1) 가상환경
```bash
cd objective_modeling

python -m venv venv           # Windows
venv\Scripts\activate         # macOS / Linux
source venv/bin/activate
```

### 2) 의존성
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) 환경 변수
```bash
LIBRARY_API_KEY=your_library_api_key
```

### 4) 서버 실행
```bash
uvicorn serve:app --reload --port 8000
```




## 디렉토리 구조

```text
objective_modeling/
├─ serve.py                        # FastAPI 서버(정적 + API)
├─ api.py                          # API만 분리 구현
├─ config.py                       # 환경 변수/상수(키워드 맵 등)
├─ app.py                          # 터미널 단에서 구현한 버전
│
├─ datasources/                # 데이터 소스
│ ├─ library_api.py                # 도서관 정보나루 API 검색/상세
│ ├─ nl_lod.py                     # 국립중앙도서관 LOD
│ └─ fallback_api.py               # fallback 시 보조 텍스트/쪽수 추출
│
├─ features/                   # 피쳐별 계산 및 매핑
│ ├─ keywords.py                   # 키워드: Kiwi/KeyBERT 기반 키워드 추출, 난이도 키워드 점수
│ ├─ purpose.py                    # 목적: 목적 점수(카테고리 매칭/가중치)
│ └─ difficulty.py                 # 난이도: 이용대상/키워드/쪽수 → 난이도 총점/등급
│
├─ recommender/                # 처리 파이프라인
│ └─ engine.py                     # 검색 → 보강 → 스코어링 → 정렬 핵심 엔진
│
├─ tests/                      # 개별 기능 수행 확인
│ ├─ test_ds_search.py             # 검색 API 호출 테스트
│ ├─ test_ds_detail_pages.py       # 상세/쪽수/대상 테스트
│ ├─ test_features.py              # 키워드/난이도/목적 함수 테스트
│ └─ test_engine_mock.py           # 엔진 모킹 테스트
│
└─ web/                        # 이용자의 서비스 여정을 반영함
├─ 1_start.html                    # 1. 시작
├─ 2_keyword.html                  # 2. 키워드/주제 입력
├─ 3_purpose.html                  # 3. 목적 선택
├─ 4_level.html                    # 4. 난이도 선택
├─ 5_result.html                   # 5. 추천 결과
├─ style.css                       # 스타일
└─ main.js                         # 페이지 공통 스크립트
```




## 주요 데이터 분석 및 활용 개요

### 1. **데이터 수집(Data Acquisition)**
- 도서관 정보나루 API
  - ISBN 기반의 도서 메타데이터(제목, 저자, 소개, 출판사, 쪽수, 이용대상 등) 실시간조회
  - 쪽수 정보(`extent`)는 정규식 기반 추출로 숫자 및 단위 변환
- 국립중앙도서관 LOD
  - RDF 기반의 도서 메타데이터(주제어, KDC 분류, 관련 자료 링크) 수집
  - `SPARQLWrapper`를 이용해 쿼리 자동화
- Fallback API
  - 주 API 호출 실패 시, 대체 데이터(페이지 수, 텍스트 설명 등)를 보강
  - `xmltodict` 기반 XML 파싱 처리

### 2. **전처리(Preprocessing)**
- 텍스트 정제
  - HTML 태그, 특수문자, 불필요 공백 제거
- 형태소 분석
  - `kiwipiepy`(Kiwi) 사용
  - 명사, 형용사, 고유명사 위주로 토큰 필터링
- 영문/숫자 처리
  영어, 숫자 토큰은 그대로 유지하여 ISBN, 연도, 영어제목 인식 가능하게 처리

### 3. **특징 추출(Feature Engineering)**
- 키워드 추출
  - `KeyBERT` + BERT 임베딩 기반 의미 유사도 계산
  - TF-IDF 보정으로 일반 단어 가중치 축소, 주제 키워드 강조
  - 예: '인공지능', '금융 데이터 분석' 같은 복합 키워드 인식
- 난이도 산정 로직
  - 페이지 수(Page Count): 쪽수가 많을수록 난이도 가중치 상승
  - 이용대상(Audience): '아동' -> 낮음, '전문가' -> 높음
  - 난이도 키워드 매칭: 사전 정의된 난이도 맵과 비교하여 점수 부여
  - 최종 난이도 = `(쪽수 점수 * 0.4) + (이용대상 점수 * 0.3) + (키워드 점수 * 0.3)`
- 목적별 가중치
  - 사용자가 선택한 독서 목적(학습, 업무, 교양, 취미)에 따라 100% 혹은 7:3 비율 가중치 적용

### 4. **스코어링 & 랭킹(Scoring & Ranking)**
- 각 도서에 대해 `목적 점수 + 난이도 적합도 + 키워드 적합도`를 종합 계산
- 점수가 높은 순으로 정렬, 상위 N권(기본 12권) 추천
- 동점 처리 시 키워드 유사도 점수가 높은 도서를 우선 노출





## 주요 사용 패키지

| 패키지 | 역할 |
|--------|------|
| **FastAPI** | 비동기 API 서버 및 정적 파일 제공 |
| **Uvicorn** | ASGI 서버 |
| **Kiwi** | 한국어 형태소 분석 |
| **KeyBERT** | BERT 임베딩 기반 키워드 추출 |
| **requests** | 외부 API 호출 |
| **python-dotenv** | 환경 변수 로드 |
| **tqdm** | 데이터 처리 진행률 표시 |
| **transformers** | 사전학습 언어모델 로딩 및 임베딩 생성 |
| **pandas** | 데이터 구조 및 처리 |
| **scikit-learn** | TF-IDF 등 머신러닝 기반 벡터화 처리 |
| **SPARQLWrapper** | LOD(SPARQL) 데이터 질의 |





## API 스펙
`GET /api/recommend`

### Query
- keyword (string, required)
- purposes (string, repeatable)
- level (string, optional)

### Response 예시
```json
{
  "items": [
    {
      "isbn": "9788972756194",
      "title": "나미야 잡화점의 기적",
      "authors": "히가시노 게이고",
      "reason": "선택한 목적과 주제의 연관성 점수 상위",
      "pages": 320,
      "image": "https://example.com/image.jpg"
    }
  ]
}
```





## 기여자(Constributors)
- 김동희: 프로젝트 기획, 데이터 소스 연동, 알고리즘 설계, 프론트엔드 UI, README 및 기술 문서 작성
- 엄태범: 데이터 소스 연동, 알고리즘 설계
- 김정현: 프로젝트 기획, 알고리즘 설계
- 김예은: 프로젝트 기획