import requests, re
from urllib.parse import urlencode
from ..config import LIBRARY_API_KEY, HTTP_TIMEOUT

BASE = "https://www.nl.go.kr/seoji/SearchApi.do"

def fetch_text_and_pages(isbn13: str):
    params = {
        "cert_key": LIBRARY_API_KEY, "result_style":"json",
        "page_no":1, "page_size":1, "isbn":isbn13
    }
    try:
        r = requests.get(f"{BASE}?{urlencode(params)}", timeout=HTTP_TIMEOUT)
        rec = (r.json().get("docs") or [{}])[0]
        text = " ".join([rec.get(k,"") for k in ("ETC","NOTE","SUBJECT","PUBLISHER")]).strip()
        page = int(rec["PAGE"]) if rec.get("PAGE") else 0
        if not page:
            import re
            m = re.search(r"(\d{2,4})\s*(쪽|페이지|p|면)?", text)
            page = int(m.group(1)) if m else 0
        return text, page
    except:
        return "", 0