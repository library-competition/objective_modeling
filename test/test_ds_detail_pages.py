from objective_modeling.datasources.library_api import fetch_detail
from objective_modeling.datasources.nl_lod import fetch_page_count

if __name__ == "__main__":
    sample_isbn = input("ISBN13 입력: ").strip()
    d = fetch_detail(sample_isbn)
    p = fetch_page_count(sample_isbn)