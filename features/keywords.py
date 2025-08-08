from kiwipiepy import Kiwi
from keybert import KeyBERT
from ..config import DIFF_KEYWORD_MAP
import re, unicodedata

_kiwi = Kiwi()
_kw = KeyBERT()  # 모델 미지정: 경량. 필요 시 KoBERT로 교체 가능.

def _strip_all_spaces(s: str) -> str:
    if not s:
        return ""
    return "".join(ch for ch in s if not unicodedata.category(ch).startswith("Z") and not ch.isspace())

def _normalize_tokens(tokens):
    seen, out = set(), []
    for t in tokens:
        t = (t or "").replace("\u200b", "")
        t = _strip_all_spaces(t)
        if t and t not in seen:
            seen.add(t); out.append(t)
    return out

def extract_keywords(text: str, top_n=10):
    # 1) Kiwi 명사
    nouns = []
    for sent in _kiwi.analyze(text or ""):
        nouns.extend([t.form for t in sent[0] if t.tag.startswith("NN")])
    nouns = list(dict.fromkeys(nouns))  # 중복 제거(순서 유지)

    # 2) KeyBERT 단일어
    try:
        kb = _kw.extract_keywords(text or "", keyphrase_ngram_range=(1,1), stop_words=None, top_n=top_n)
        kb_terms = [k[0] for k in kb]
    except Exception:
        kb_terms = []

    # 병합 + 공백 제거 + 중복 제거
    merged = _normalize_tokens(kb_terms + nouns)
    return merged[:max(top_n, len(merged))]

def difficulty_keyword_score(keywords: list[str]) -> int:
    # 상위 난이도 1개만 반영 규칙
    if any(k in keywords for k in DIFF_KEYWORD_MAP["전문"]): return 40
    if any(k in keywords for k in DIFF_KEYWORD_MAP["심화"]): return 20
    if any(k in keywords for k in DIFF_KEYWORD_MAP["입문"]): return 0
    return 0

def difficulty_keyword_score_from_text(text: str) -> int:
    if not text:
        return 0
    if any(k in text for k in DIFF_KEYWORD_MAP["전문"]): return 40
    if any(k in text for k in DIFF_KEYWORD_MAP["심화"]): return 20
    if any(k in text for k in DIFF_KEYWORD_MAP["입문"]): return 0
    return 0