from ..datasources.library_api import search_books_by_keyword, fetch_detail
from ..datasources.nl_lod import fetch_page_count
from ..datasources.fallback_api import fetch_text_and_pages
from ..features.keywords import extract_keywords
from ..features.purpose import purpose_score, weighted_purpose_match
from ..features.difficulty import difficulty_total
import re
from ..config import MAX_BOOKS

def hydrate_book(b):  # b: search result row
    isbn = b.get("isbn13")
    detail = fetch_detail(isbn) if isbn else {}
    audience = detail.get("target","")
    kdc = detail.get("kdc") or b.get("kdc")
    extent_raw = detail.get("extent", "")
    # 쪽수: LOD → data4library extent 파싱은 detail 내부에서 필요 시 구현 가능. 우선 LOD 우선.
    pages = fetch_page_count(isbn)
    if pages == 0:
        try:
            m = re.search(r'(\d{2,4})\s*(쪽|페이지|p|면)?', extent_raw or "")
            if m:
                pages = int(m.group(1))
        except Exception:
            pass
    if pages == 0:
        text, p2 = fetch_text_and_pages(isbn)
        pages = p2
        if not b.get("description"):
            b["description"] = (b.get("description","") + " " + text).strip()
    # 키워드: 제목+소개
    text = " ".join([b.get("title",""), b.get("description","")])
    kws = extract_keywords(text, top_n=20)
    return {
        "isbn13": isbn,
        "title": b.get("title",""),
        "authors": b.get("authors",""),
        "publisher": b.get("publisher",""),
        "description": b.get("description",""),
        "kdc": kdc,
        "audience": audience,
        "pages": pages,
        "keywords": kws
    }

def _dedup_books(rows):
    seen = set()
    out = []
    for b in rows:
        key = ( (b.get("title") or "").strip(), (b.get("authors") or "").strip() )
        if key in seen: 
            continue
        seen.add(key); out.append(b)
    return out

def rank_books(user_purposes: list[tuple[str,int]], prefer_level: str|None, keyword: str, k=12):
    # 1) 검색
    raw = search_books_by_keyword(keyword, page_size=MAX_BOOKS*2)
    if not raw:
        raw = search_books_by_keyword(keyword, page_size=MAX_BOOKS*2)
    raw = _dedup_books(raw)[:MAX_BOOKS]

    # 2) 정제/보강
    enriched = [hydrate_book(b) for b in raw]

    # 3) 스코어링
    ranked = []
    for bk in enriched:
        p_scores = purpose_score(bk["keywords"], bk["kdc"])
        p_match = weighted_purpose_match(user_purposes, p_scores)  # 0~22 (대략)
        raw_text = " ".join([bk.get("title", ""), bk.get("description")])
        diff_total, diff_level = difficulty_total(bk["audience"], bk["keywords"], bk["pages"], raw_text)

        # 난이도 선호 가중
        level_weight = 1.0
        if prefer_level:
            level_weight = 1.7 if diff_level == prefer_level else 0.3

        # 최종 점수: 목적 적합(정규화) + 난이도 총점(정규화) * 가중
        # 간단 가중 합산(튜닝 지점)
        final = (p_match/22.0)*0.6 + (diff_total/100.0)*0.4
        final *= level_weight

        ranked.append({**bk, "difficulty_total": diff_total, "difficulty_level": diff_level,
                       "purpose_scores": p_scores, "final_score": final})

    ranked.sort(key=lambda x: x["final_score"], reverse=True)
    return ranked[:k]