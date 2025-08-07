const { extractKeywordsWithScore } = require('./combinedKeywordExtractor');

const keywordMap = {
  입문: [
    '기초', '초급', '입문', '쉽게', '처음', '시작', '해설', '가이드',
    '개론', '이해', '설명', '소개', '기본', '설정', '처음하는', '차근차근'
  ],
  심화: [
    '실무', '실전', '노하우', '심화', '중급', '활용', '응용', '확장',
    '중요', '심도', '핵심', '중급자', '심층', '통합', '전환', '적용'
  ],
  전문: [
    '전문', '연구', '고급', '마스터', '전문가', '심층', '분석', '이론',
    '논문', '학회', '세미나', '심포지엄', '논의', '통계', '알고리즘', '프레임워크'
  ]
};

// [1] TF-IDF 기반 키워드 배열 → 점수 환산
function computeKeywordScore(tfidfKeywords) {
  let score = 0;
  const lowerKeywords = tfidfKeywords.map(k => k.toLowerCase());

  for (const level in keywordMap) {
    const matched = keywordMap[level].filter(kw =>
      lowerKeywords.includes(kw.toLowerCase())
    );
    const weight = level === '전문' ? 40 : level === '심화' ? 20 : 0;
    score += matched.length * weight;
  }

  return Math.min(score, 40);
}

// [2] 종합 난이도 점수 계산
function getDifficultyScore(book, tfidfKeywords = [], keywordScore = null) {
  // 1) 키워드 점수 확보: (외부에서 안 넘겨주면 내부에서 추출)
  if (keywordScore === null) {
    if (Array.isArray(tfidfKeywords) && tfidfKeywords.length > 0) {
      keywordScore = computeKeywordScore(tfidfKeywords);
    } else {
      const { keywords, keywordScore: ks } =
        extractKeywordsWithScore(`${book.title} ${book.description || ''}`);
      tfidfKeywords = keywords;
      keywordScore = ks;
    }
  }

  // 2) 이용대상 점수
  let targetScore = 0;
  if (!book.target || book.target.trim() === '') {
    targetScore = 20;
  } else if (book.target.includes('전문')) targetScore = 40;
  else if (book.target.includes('일반')) targetScore = 20;
  else if (book.target.includes('아동') || book.target.includes('청소년')) targetScore = 0;

  // 3) 쪽수 점수
  let pageScore = 0;
  if (book.pages >= 400) pageScore = 20;
  else if (book.pages >= 200) pageScore = 10;
  else pageScore = 0;

  // 4) 총점/레벨
  const totalScore = targetScore * 0.4 + keywordScore * 0.4 + pageScore * 0.2;

  let level = '입문';
  if (totalScore >= 60) level = '전문';
  else if (totalScore >= 30) level = '심화';

  return {
    isbn: book.isbn,
    title: book.title,
    targetScore,
    keywordScore,
    pageScore,
    totalScore,
    level,
  };
}

module.exports = { getDifficultyScore }