import requests, re
from urllib.parse import quote
from ..config import HTTP_TIMEOUT

SPARQL = "https://lod.nl.go.kr/sparql"

def fetch_page_count(isbn13: str) -> int:
    q = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?page WHERE {{
      ?book dcterms:identifier "{isbn13}" .
      ?book dcterms:extent ?page .
    }} LIMIT 1
    """
    url = f"{SPARQL}?query={quote(q)}&format=json"
    try:
        r = requests.get(url, timeout=HTTP_TIMEOUT)
        v = r.json().get("results",{}).get("bindings",[{}])[0].get("page",{}).get("value","")
        m = re.search(r"(\d{2,4})", v)
        return int(m.group(1)) if m else 0
    except:
        return 0