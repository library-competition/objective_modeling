# serve.py (루트)
import os, sys
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from objective_modeling.recommender.engine import rank_books

app = FastAPI(title="독서나침반")

# 1) API 먼저 등록
@app.get("/api/recommend")
def api_recommend(
    keyword: str,
    purposes: List[str] = Query(["교양"]),
    level: Optional[str] = Query(None),
):
    if len(purposes) == 0:
        user_purposes = [("교양", 100)]
    elif len(purposes) == 1:
        user_purposes = [(purposes[0], 100)]
    else:
        user_purposes = [(purposes[0], 70), (purposes[1], 30)]

    results = rank_books(
        user_purposes,
        level if level in ("입문", "심화", "전문") else None,
        keyword,
        k=12,
    )

    return {"items": [{
        "isbn": r.get("isbn13"),
        "title": r.get("title"),
        "authors": r.get("authors"),
        "reason": r.get("reason", ""),
    } for r in results]}

# 2) 루트는 시작 페이지로
@app.get("/")
def root():
    return FileResponse(os.path.join("web", "1_start.html"))

# 3) 마지막에 정적 파일 mount (이게 /api를 먹어버리면 안 되므로 맨 마지막!)
app.mount("/", StaticFiles(directory="web", html=True), name="static")