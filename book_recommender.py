import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
LIBRARY_API_KEY = os.getenv("LIBRARY_API_KEY")

# 난이도 키워드 기준 점수
keywords_score = {
    '입문': ['기초', '초급', '입문', '처음', '쉬운', '쉽게'],
    '심화': ['실전', '심화', '노하우', '중급', '응용', '활용'],
    '전문': ['전문', '고급', '학술', '연구', '전문가']
}
audience_score = {
    '아동': 0, '청소년': 0, '일반': 20, '전문': 40
}

def score_by_page(p):
    try:
        p = int(p)
        if p < 200:
            return 0
        elif 200 <= p <= 400:
            return 10
        else:
            return 20
    except:
        return 0

def score_by_keywords(text):
    for level, keywords in keywords_score.items():
        if any(k in text for k in keywords):
            return {'입문': 0, '심화': 20, '전문': 40}[level]
    return 0

def classify_level(score):
    if score < 10:        # 0~9.9 → 입문
        return '입문'
    elif score < 20:      # 10~19.9 → 심화
        return '심화'
    else:                 # 20 이상 → 전문
        return '전문'

purpose_keywords = {
    '학습': ['공부', '학습', '시험', '입시', '교재'],
    '업무': ['실무', '직장', '업무', '보고서', '프레젠테이션'],
    '교양': ['인문', '역사', '철학', '교양', '상식'],
    '취미': ['여가', '취미', '자기계발', '소설', '에세이', '요리', '여행']
}

def analyze_purpose(text):
    matched = []
    for category, words in purpose_keywords.items():
        if any(w in text for w in words) or category in text:
            matched.append(category)
    return matched

def get_purpose_weight(book_desc, selected_categories):
    score = 0
    for i, cat in enumerate(selected_categories):
        weight = 0.7 if i == 0 else 0.3
        if any(k in book_desc for k in purpose_keywords.get(cat, [])):
            score += weight * 100
    return score

def calculate_total_score(row, selected_purpose=[]):
    desc = (row.get('description') or '') + ' ' + (row.get('class_nm') or '')
    page = row.get('page', 0)

    keyword_score = score_by_keywords(desc)
    aud_score = 0
    for k in audience_score:
        if k in desc:
            aud_score = audience_score[k]
            break
    page_score = score_by_page(page)
    purpose_score = get_purpose_weight(desc, selected_purpose)

    return 0.3 * keyword_score + 0.3 * aud_score + 0.2 * page_score + 0.2 * purpose_score / 100

def fetch_books(keyword, max_results=30):
    url = "https://data4library.kr/api/srchBooks"
    params = {
        "authKey": LIBRARY_API_KEY,
        "title": keyword,
        "pageNo": 1,
        "pageSize": max_results,
        "format": "json"
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        print("API 오류:", res.status_code)
        return pd.DataFrame()
    data = res.json()
    items = data.get("response", {}).get("docs", [])
    books = []
    for item in items:
        doc = item.get("doc", {})
        books.append({
            "title": doc.get("bookname", ""),
            "author": doc.get("authors", ""),
            "publisher": doc.get("publisher", ""),
            "description": doc.get("description", ""),
            "class_nm": doc.get("class_nm", ""),
            "page": doc.get("bookDtl", {}).get("bookPageNo", 0)
        })
    return pd.DataFrame(books)

def recommend_books(keyword, purpose, user_level):
    df = fetch_books(keyword)
    print(f"API로 불러온 도서 수: {len(df)}")

    if df.empty:
        return pd.DataFrame()
    
    selected_purposes = analyze_purpose(purpose)
    if len(selected_purposes) == 0:
        print("입력된 목적에서 분류된 카테고리가 없어 목적 가중치를 적용하지 않습니다.")

    df["score"] = df.apply(lambda row: calculate_total_score(row, selected_purposes), axis=1)
    df["predicted_level"] = df["score"].apply(classify_level)

    if user_level in ["입문", "심화", "전문"]:     # ← [Line B]
        filtered = df[df["predicted_level"] == user_level]
        others = df[df["predicted_level"] != user_level]
        result = pd.concat([
            filtered.sort_values(by="score", ascending=False).head(7),
            others.sort_values(by="score", ascending=False).head(3)
        ])
    else:
        result = pd.concat([
            df[df["predicted_level"] == "입문"].sort_values(by="score", ascending=False).head(3),
            df[df["predicted_level"] == "심화"].sort_values(by="score", ascending=False).head(3),
            df[df["predicted_level"] == "전문"].sort_values(by="score", ascending=False).head(3),
        ])

    return result[["title","author","publisher","score","predicted_level"]]

# 실행
if __name__ == "__main__":
    print("독서 목적에 따른 난이도별 도서 추천 서비스")

    # 1. 주제 입력
    keyword = input("키워드를 입력하세요: ")

    # 2. 목적 입력
    print("독서 목적을 선택하세요. {학습, 업무, 교양, 취미, 기타} (최대 2개, 쉼표로 구분)")
    purpose = input("선택 또는 직접 입력: ").strip()

    # 3. 난이도 선택
    level = input("원하는 난이도(입문/심화/전문)를 입력하세요: ")

    result = recommend_books(keyword, purpose, level)
    print("\n추천 도서:")
    print(result)