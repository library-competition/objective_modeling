const fs = require('fs');
const path = require('path');
const { getBookInfo } = require('./api/fetchBookInfo');
const { getDifficultyScore } = require('./utils/difficultyScorer');
const { extractKeywordsWithScore } = require('./utils/combinedKeywordExtractor');

async function runBulkTest() {
  const isbnList = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'data/test.json'), 'utf-8')
  );

  const results = [];

  for (const isbn of isbnList) {
    try {
      const book = await getBookInfo(isbn);
      console.log(`[DEBUG] TF-IDF 키워드 (${isbn}):`, tfidfKeywords);
      const { keywords, keywordScore } = extractKeywordsWithScore(`${book.title} ${book.description || ''}`);
      console.log(`[DEBUG] 키워드 (${isbn}):`, keywords, ' / keywordScore:', keywordScore);
      const score = getDifficultyScore(book, keywords, keywordScore);

      console.log(`\n[${isbn}] ${score.title || '(제목없음)'}`);
      console.log(`- 난이도: ${score.level}`);
      console.log(`- 점수 구성 → 이용대상: ${score.targetScore} / 키워드: ${score.keywordScore} / 쪽수: ${score.pageScore} / 총점: ${score.totalScore}`);

      results.push({
        isbn,
        title: score.title,
        level: score.level,
        totalScore: score.totalScore,
        targetScore: score.targetScore,
        keywordScore: score.keywordScore,
        pageScore: score.pageScore
      });
    } catch (e) {
      results.push({ isbn, error: true });
    }
  }
}

runBulkTest();