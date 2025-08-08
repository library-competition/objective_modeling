from ..config import W_AUDIENCE, W_DIFF_KW, W_PAGES, DEFAULT_AUDIENCE_SCORE, DEFAULT_PAGES_SCORE
from .keywords import difficulty_keyword_score, difficulty_keyword_score_from_text

def score_audience(target: str) -> int:
    # '아동청소년' → 0, '일반' → 20, '전문' → 40, 누락 → 20
    if not target: return DEFAULT_AUDIENCE_SCORE
    t = target.strip()
    if "아동" in t: return 0
    if "전문" in t: return 40
    return 20  # 기본 '일반'

def score_pages(pages: int) -> int:
    if not pages or pages <= 0: return DEFAULT_PAGES_SCORE
    if pages < 200: return 0
    if pages < 400: return 10
    return 20

def difficulty_total(audience: str, keywords: list[str], pages: int, raw_text: str="") -> tuple[int,str]:
    s_aud = score_audience(audience)      # 0/20/40
    s_kw  = difficulty_keyword_score(keywords)  # 0/20/40
    if s_kw == 0 and raw_text:
        s_kw = difficulty_keyword_score_from_text(raw_text)
    s_pg  = score_pages(pages)            # 0/10/20
    total = s_aud + s_kw + s_pg           # 0~100
    level = "입문" if total < 30 else ("심화" if total < 60 else "전문")
    return total, level