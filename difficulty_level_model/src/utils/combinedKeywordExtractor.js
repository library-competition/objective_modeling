const natural = require('natural');
const keyword_extractor = require('keyword-extractor');

const keywordMap = {
  입문: ['기초', '초급', '입문', '쉽게', '처음', '시작'],
  심화: ['실무', '실전', '노하우', '심화', '중급', '활용'],
  전문: ['전문', '연구', '고급', '심층', '마스터', '전문가']
};

function extractTFIDFKeywords(text, topN = 10) {
  const tokenizer = new natural.WordTokenizer();
  const tfidf = new natural.TfIdf();

  tfidf.addDocument(text);
  const terms = tfidf.listTerms(0);

  return terms
    .filter(item => /^[가-힣a-zA-Z]+$/.test(item.term) && item.term.length >= 2)
    .slice(0, topN)
    .map(item => item.term);
}

function computeKeywordScore(keywords) {
  let score = 0;
  for (const level in keywordMap) {
    if (keywordMap[level].some(k => keywords.includes(k))) {
      if (level === '전문') return 40;
      if (level === '심화') score = Math.max(score, 20);
      if (level === '입문') score = Math.max(score, 0);
    }
  }
  return score;
}

function extractKeywordsWithScore(text) {
  const tfidfKeywords = extractTFIDFKeywords(text, 10);
  const extracted = keyword_extractor.extract(text, {
    language: 'korean',
    remove_digits: true,
    return_changed_case: false,
    remove_duplicates: true
  });
  const merged = Array.from(new Set([...tfidfKeywords, ...extracted]));
  const score = computeKeywordScore(merged);
  console.log('[debug]키워드 병합: ', merged);
  return { keywords: merged, keywordScore: score};

};
module.exports = { extractKeywordsWithScore };