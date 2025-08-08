from objective_modeling.datasources.library_api import search_books_by_keyword
import json

if __name__ == "__main__":
    rows = search_books_by_keyword("철학", page_size=5)
    print(f"rows={len(rows)}")

    # 라이브러리 함수 내부에서만 파싱한 결과만 리턴하니,
    # 원본을 직접 확인해보려면 임시로 같은 호출을 한 번 더 합니다.
    import requests, os
    BASE = "http://data4library.kr/api/srchBooks"
    params = {
        "authKey": os.getenv("LIBRARY_API_KEY"),
        "keyword": "철학",
        "pageNo": 1,
        "pageSize": 5,
        "format": "json"
    }
    r = requests.get(BASE, params=params, timeout=7)
    print("status:", r.status_code)
    print("raw json:", json.dumps(r.json(), ensure_ascii=False, indent=2))