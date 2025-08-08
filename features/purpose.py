from ..config import PURPOSE_KEYWORDS

def purpose_score(text_keywords: list[str], kdc_major: str|None) -> dict:
    # kdc_major 예: "800" → 문학
    scores = { "학습":0, "업무":0, "교양":0, "취미":0 }

    # 10/7/5 규칙
    for cat, buckets in PURPOSE_KEYWORDS.items():
        s = 0
        if any(k in text_keywords for k in buckets[1]): s += 10
        if any(k in text_keywords for k in buckets[2]): s += 7
        if any(k in text_keywords for k in buckets[3]): s += 5
        scores[cat] = s

    # KDC 800(문학) 예외
    if kdc_major == "800":
        # 학습: 해설/평론 → 키워드가 없으면 0, 있으면 가산되도록 현 규칙 유지
        # 취미: 쓰기/작법 → 동일
        # 교양: 그 외 전부 → 문학 일반은 교양 가중. 키워드 전무 시 교양 기본 가점 5
        if max(scores.values()) == 0:
            scores["교양"] = 5

    return scores

def weighted_purpose_match(user_purposes: list[tuple[str,int]], book_purpose_scores: dict) -> float:
    # user_purposes: [("교양",70), ("학습",30)] 형태
    total = 0.0
    for cat, w in user_purposes:
        total += book_purpose_scores.get(cat,0) * (w/100)
    return total