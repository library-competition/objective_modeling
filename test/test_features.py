from objective_modeling.features.keywords import extract_keywords, difficulty_keyword_score
from objective_modeling.features.purpose import purpose_score, weighted_purpose_match
from objective_modeling.features.difficulty import difficulty_total

text_learn = "토익 시험 합격을 위한 공부법과 기출문제 해설을 담은 교재"
text_culture = "니체의 철학 사상을 해석하고 세계사적 맥락에서 성찰하는 인문학 에세이"
text_hobby = "홈베이킹 입문자를 위한 쉽게 시작하는 케이크 만들기"

# 1) 키워드 추출
print("kw_learn:", extract_keywords(text_learn)[:10])
print("kw_culture:", extract_keywords(text_culture)[:10])
print("kw_hobby:", extract_keywords(text_hobby)[:10])

# 2) 목적 점수
kdc_800 = "800"
kdc_100 = "100"
ps_learn = purpose_score(extract_keywords(text_learn), kdc_100)
ps_culture_800 = purpose_score(extract_keywords(text_culture), kdc_800)
ps_hobby = purpose_score(extract_keywords(text_hobby), kdc_100)
print("purpose_scores:", ps_learn, ps_culture_800, ps_hobby)

# 3) 목적 가중치(교양70/학습30)
wm = weighted_purpose_match([("교양",70),("학습",30)], ps_culture_800)
print("weighted_match:", wm)

# 4) 난이도 점수
kw_score_expert = difficulty_keyword_score(["전문가","고급"])
kw_score_beginner = difficulty_keyword_score(["입문","처음"])
print("diff_kw_score(expert/beginner):", kw_score_expert, kw_score_beginner)

# audience: 아동/일반/전문 → 0/20/40, pages: <200=0, 200~399=10, 400+=20
print("diff_total examples:")
print("아동, 입문키워드, 150p:",          difficulty_total("아동청소년", ["입문"], 150))
print("일반, 심화키워드, 250p:",          difficulty_total("일반", ["심화"], 250))
print("전문, 전문가키워드, 420p:",        difficulty_total("전문", ["전문가"], 420))
print("누락, 키워드없음, pages없음:",      difficulty_total("", [], 0))