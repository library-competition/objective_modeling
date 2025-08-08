from .recommender.engine import rank_books

def parse_purposes_input(raw: str):
    # "교양" or "교양,학습" → [("교양",70),("학습",30)] 규칙
    items = [s.strip() for s in raw.replace(" ", "").split(",") if s.strip()]
    if not items: return [("교양",100)]
    if len(items) == 1: return [(items[0],100)]
    return [(items[0],70), (items[1],30)]

if __name__ == "__main__":
    print("독서 목적에 따른 난이도별 도서 추천 서비스")
    topic = input("검색 키워드(주제/자유검색): ").strip()
    purpose_raw = input("독서 목적 선택(학습/업무/교양/취미 중 최대2개, 쉼표로 구분): ").strip()
    user_purposes = parse_purposes_input(purpose_raw)

    level = input("원하는 난이도(입문/심화/전문, 미입력시 엔터): ").strip()
    level = level if level in ("입문","심화","전문") else None

    results = rank_books(user_purposes, level, topic, k=9)
    if not results:
        print("\n조건에 맞는 결과가 없습니다.")
    else:
        print(f"\n추천 결과({len(results)}권):")
        for r in results:
            print(f"- {r['title']} | {r['authors']} | 난이도:{r['difficulty_level']}({r['difficulty_total']}) | p.{r['pages']} | 점수:{r['final_score']:.3f}")