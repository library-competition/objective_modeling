from objective_modeling.recommender import engine as eng

def fake_search(keyword, page_size=40):
    return [
        {"isbn13":"111","title":"니체 철학 입문","authors":"A","publisher":"P","description":"철학 입문 쉽게 시작","kdc":"100"},
        {"isbn13":"222","title":"프로젝트관리 실무","authors":"B","publisher":"Q","description":"업무 실무 노하우 심화","kdc":"300"},
        {"isbn13":"333","title":"데이터분석 전문가 가이드","authors":"C","publisher":"R","description":"전문가 고급 심층","kdc":"300"},
    ]

def fake_detail(isbn):
    return {
        "111":{"target":"일반","kdc":"100","description":"철학 입문 쉽게 시작"},
        "222":{"target":"일반","kdc":"300","description":"업무 실무 노하우 심화"},
        "333":{"target":"전문","kdc":"300","description":"전문가 고급 심층"},
    }[isbn]

def fake_fetch_detail(isbn): return fake_detail(isbn)
def fake_fetch_target(isbn): return fake_detail(isbn)["target"]
def fake_pages(isbn):
    return {"111":180, "222":280, "333":420}[isbn]
def fake_fallback_text_pages(isbn):
    return ("", 0)

# 주입
eng.search_books_by_keyword = fake_search
eng.fetch_detail = fake_fetch_detail
eng.fetch_target_audience = fake_fetch_target
eng.fetch_page_count = fake_pages
eng.fetch_text_and_pages = fake_fallback_text_pages

if __name__ == "__main__":
    # 사용자는 교양70/학습30, 난이도 선호 없음
    res = eng.rank_books([("교양",70),("학습",30)], None, "철학")
    for r in res:
        print(r["isbn13"], r["title"], r["difficulty_level"], r["difficulty_total"], f"{r['final_score']:.3f}")

    # 난이도 선호: 전문 → 전문에 1.7배 가중
    print("\nprefer=전문")
    res2 = eng.rank_books([("교양",70),("학습",30)], "전문", "철학")
    for r in res2:
        print(r["isbn13"], r["title"], r["difficulty_level"], r["difficulty_total"], f"{r['final_score']:.3f}")