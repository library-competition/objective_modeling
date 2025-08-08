from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from objective_modeling.recommender.engine import rank_books

app = FastAPI(title="독서나침반 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/recommend")
def api_recommend(
    keyword: str,
    purposes: List[str] = Query(["교양"]),
    level: Optional[str] = Query(None)
):
    # 목적 가중치: 1개=100, 2개=70/30
    if len(purposes) == 0:
        user_purposes = [("교양", 100)]
    elif len(purposes) == 1:
        user_purposes = [(purposes[0], 100)]
    else:
        user_purposes = [(purposes[0], 70), (purposes[1], 30)]

    results = rank_books(user_purposes, level if level in ("입문","심화","전문") else None, keyword, k=12)

    payload = []
    for r in results:
        payload.append({
            "isbn": r.get("isbn13"),
            "title": r.get("title"),
            "authors": r.get("authors"),
            "score": round(float(r.get("final_score", 0.0)), 3),
            "difficulty_level": r.get("difficulty_level"),
            "difficulty_total": r.get("difficulty_total"),
            "reason": r.get("reason", ""),
            "pages": r.get("pages", 0),
            "image": r.get("image", ""),
        })
    return {"items": payload}