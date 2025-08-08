import requests, sys, time
from ..config import LIBRARY_API_KEY, HTTP_TIMEOUT, HTTP_RETRY

BASE = "http://data4library.kr/api"

def _get(url, params):
    last_err = None
    for attempt in range(HTTP_RETRY+1):
        try:
            r = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
            print("[libapi]", r.url, r.status_code, file=sys.stderr)
            try:
                data = r.json()
            except ValueError:
                data = {"raw": r.text}
            
            if r.status_code != 200:
                last_err = f"HTTP {r.status_code}"
                time.sleep(0.4 * (attempt + 1))
                continue
            
            if data.get("response", {}).get("error"):
                msg = data["response"]["error"]
                print("[libapi][error]", msg, file=sys.stderr)
                return data
            return data
        except Exception as e:
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    print(f"[LIBAPI][fatal] {url} -> {last_err}", file=sys.stderr)
    return {}

def search_books_by_keyword(keyword: str, page_size=20, page_no=1):
    params = {"authKey": LIBRARY_API_KEY, "keyword": keyword, "pageNo": page_no,
              "pageSize": page_size, "format":"json"}
    data = _get(f"{BASE}/srchBooks", params) or {}
    resp = data.get("response", {})
    if resp.get("error"):
        return []
    docs = resp.get("docs", [])
    # 최소 필드 통일
    out = []
    for item in docs:
        d = item.get("doc",{})
        out.append({
            "isbn13": d.get("isbn13") or d.get("isbn"),
            "title": d.get("bookname",""),
            "authors": d.get("authors",""),
            "publisher": d.get("publisher",""),
            "description": d.get("description",""),
            "kdc": d.get("class_no","")[:1] + "00" if d.get("class_no") else "",
            "extent_raw": None,  # 상세에서 보강
        })
    return out

def fetch_detail(isbn13: str):
    params = {"authKey": LIBRARY_API_KEY, "isbn13": isbn13, "format":"json"}
    data = _get(f"{BASE}/srchDtlList", params)
    book = (data.get("response",{}).get("detail") or [{}])[0].get("book", {})
    return {
        "title": book.get("bookname",""),
        "description": book.get("description",""),
        "extent": book.get("extent",""),   # "350 p." 같은 문자열
        "target": book.get("target",""),   # 이용대상(아동청소년/일반/전문 등)
        "kdc": book.get("class_no","")[:1] + "00" if book.get("class_no") else ""
    }

def fetch_target_audience(isbn13: str) -> str:
    return fetch_detail(isbn13).get("target","")