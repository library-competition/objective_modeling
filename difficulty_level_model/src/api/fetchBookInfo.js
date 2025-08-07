const { resolvePageCount } = require('./pageResolver');

const axios = require('axios');
require('dotenv').config();

const LIBRARY_API_KEY = process.env.LIBRARY_API_KEY;

// 1. 도서관 정보나루 API (도서명/소개)
async function fetchLibraryInfo(isbn) {
  const url = `http://data4library.kr/api/srchDtlList?authKey=${LIBRARY_API_KEY}&isbn13=${isbn}&format=json`;

  try {
    const res = await axios.get(url);
    const raw = res.data;
    if (!raw.response?.detail || raw.response.detail.length === 0) {
      throw new Error("도서 정보 없음");
    }
    const doc = raw.response.detail[0].book;

    const extent = doc.extent || '';
    const match = extent.match(/(\d{2,4}).{0,5}?(쪽|p|페이지)/i); // 정규식 개선
    const pagesFromExtent = match ? parseInt(match[1], 10) : 0;

    return {
      title: doc.bookname || '',
      description: doc.description || '',
      pagesFromExtent,
    };
  } catch (err) {
    return await fetchLibraryInfoFallback(isbn);
  }
}

async function fetchLibraryInfoFallback(isbn) {
  const url = `https://www.nl.go.kr/seoji/SearchApi.do?cert_key=${LIBRARY_API_KEY}&result_style=json&page_no=1&page_size=1&isbn=${isbn}`;
  const res = await axios.get(url);
  const record = res.data.docs?.[0];
  if (!record) throw new Error("fallback도 실패");

  const title = record.TITLE || '(제목없음)';
  const description = [
    record.ETC, record.NOTE, record.SUBJECT, record.PUBLISHER
  ].filter(Boolean).join(' ');
  let pageGuess = 0;
  if (record.PAGE) {
    pageGuess = parseInt(record.PAGE, 10);
  } else {
    const text = [record.ETC, record.NOTE, record.SUBJECT].filter(Boolean).join(' ');
    const match = text.match(/(\d{2,4})\s*(쪽|페이지|p|면)?/i);
    pageGuess = match ? parseInt(match[1], 10) : 0;
  }

  return {
    title,
    description,
    pagesFromExtent: pageGuess,
  };
}

// 2. (이용 대상)
async function fetchTargetAudience(isbn) {
  try {
    const url1 = `http://data4library.kr/api/srchDtlList?authKey=${LIBRARY_API_KEY}&isbn13=${isbn}&format=json`;
    const res1 = await axios.get(url1);
    const doc = res1.data.response?.detail?.[0]?.book;
    if (doc?.target) return doc.target;
  } catch (e) {}

  try {
    const url2 = `https://www.nl.go.kr/seoji/SearchApi.do?cert_key=${LIBRARY_API_KEY}&result_style=json&page_no=1&page_size=1&isbn=${isbn}`;
    const res2 = await axios.get(url2);
    return res2.data.docs?.[0]?.TARGET || '';
  } catch (e) {
    return '';
  }
}

// 3. LOD 쪽수 정보
async function fetchPageCount(isbn) {
  const url = `https://lod.nl.go.kr/sparql`;

  const query = `
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?page WHERE {
      ?book dcterms:identifier "${isbn}" .
      ?book dcterms:extent ?page .
    } LIMIT 1
  `;

  const encoded = encodeURIComponent(query);
  const fullUrl = `${url}?query=${encoded}&format=json`;

  try {
    const res = await axios.get(fullUrl);
    const result = res.data?.results?.bindings?.[0]?.page?.value || '';
    const match = result.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  } catch {
    return 0;
  }
}

async function getBookInfo(isbn) {
  const [libInfo, target] = await Promise.all([
    fetchLibraryInfo(isbn),
    fetchTargetAudience(isbn),
  ]);

  const pages = await resolvePageCount(isbn, libInfo.description);

  return {
    isbn,
    title: libInfo.title,
    description: libInfo.description,
    target,
    pages
  };
}

module.exports = { getBookInfo };