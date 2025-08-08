# READING_COMPASS

사용자의 **독서 목적(학습/업무/교양/취미)** 과 **난이도(입문/심화/전문)** 를 반영해 도서를 추천하는 웹 앱입니다.  
백엔드(FastAPI)에서 추천 API를 제공하고, `web/`의 정적 페이지에서 API를 호출해 결과를 보여줍니다.


## 요구사항

- Python 3.10+ (3.11/3.12/3.13 동작 확인)
- pip 최신 버전
- (Windows 권장) PowerShell


## 디렉토리 구조

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


## 추천 알고리즘 개요

1. **데이터 수집 단계**
   - `library_api.py`에서 **도서관 정보나루 API**를 통해 ISBN 기반 도서 정보 수집
   - `nl_lod.py`에서 **국립중앙도서관 LOD SPARQL**로 페이지 수 데이터 보완
   - `fallback_api.py`에서 누락 데이터 보완(텍스트 기반 분석)

2. **피처 엔지니어링**
   - **키워드 추출**: `Kiwi`(형태소 분석)와 `KeyBERT`(BERT 임베딩 기반 키워드 추출)
   - **목적 매칭**: 사용자 선택 목적과 도서 주제/카테고리를 매핑하여 가중치 부여
   - **난이도 산정**:
     - 이용대상 (아동/청소년/성인)
     - 추출된 키워드 점수
     - 페이지 수
     → 가중 합산으로 난이도 등급(입문/심화/전문) 부여

3. **스코어링 & 정렬**
   - 목적 적합도 + 난이도 적합도 + 키워드 관련성을 종합 점수화
   - 상위 k개 결과를 반환


## 설치 & 실행

### 1) 가상환경
```bash
cd objective_modeling

python -m venv venv           # Windows
venv\Scripts\activate         # macOS / Linux
source venv/bin/activate


### 2) 의존성
pip install --upgrade pip
pip install -r requirements.txt


### 3) 환경 변수
LIBRARY_API_KEY=your_library_api_key


### 4) 서버 실행
uvicorn serve:app --reload --port 8000


## 주요 사용 패키지

| 패키지 | 역할 |
|--------|------|
| **FastAPI** | 비동기 API 서버 및 정적 파일 제공 |
| **Uvicorn** | ASGI 서버 |
| **Kiwi** | 한국어 형태소 분석 |
| **KeyBERT** | BERT 임베딩 기반 키워드 추출 |
| **requests** | 외부 API 호출 |
| **SPARQLWrapper** | LOD(SPARQL) 데이터 질의 |
| **python-dotenv** | 환경 변수 로드 |
| **tqdm** | 데이터 처리 진행률 표시 |
| **pytest** | 테스트 실행 |


## API 스펙
`GET /api/recommend`

### Query
- keyword (string, required)
- purposes (string, repeatable)
- level (string, optional)

### Response 예시
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


## 기여자(Constributors)
- 김동희: 데이터 소스 연동, 알고리즘 설계, 프론트엔드 UI, README 및 기술 문서 작성
- 엄태범: 알고리즘 설계
- 김정현: 프로젝트 기획, 알고리즘 설계
- 김예은: 프로젝트 기획