const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { getDifficultyScore } = require('./utils/difficultyScorer');
const { getBookInfo } = require('./api/fetchBookInfo');
const { extractKeywordsWithScore } = require('./utils/combinedKeywordExtractor');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function askISBN() {
  rl.question('\nISBN을 입력하세요 (종료하려면 "exit"): ', async (input) => {
    if (input.toLowerCase() === 'exit') {
      rl.close();
      return;
    }

    try {
      const book = await getBookInfo(input);
      const { keywords, keywordScore } = extractKeywordsWithScore(`${book.title} ${book.description || ''}`);
      const score = getDifficultyScore(book);

      console.log(`쪽수: ${book.pages}`);
      console.log(`\n도서명: ${score.title}`);
      console.log(`난이도: ${score.level}`);
      console.log(`점수 구성 → 이용대상: ${score.targetScore} / 키워드: ${score.keywordScore} / 쪽수: ${score.pageScore} / 총점: ${score.totalScore}`);
    } catch (err) {
      console.error('도서 정보를 가져오는데 실패했습니다. ISBN을 확인해주세요.');
      console.error('[DEBUG] 에러 메시지:', err.message);
      console.error('[DEBUG] 에러 스택:\n', err.stack);
    }

    askISBN();
  });
}

askISBN();