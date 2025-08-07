const axios = require('axios');
require('dotenv').config();

const LIBRARY_API_KEY = process.env.LIBRARY_API_KEY;

async function fetchPageCountFromLOD(isbn) {
  const query = `
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?page WHERE {
      ?book dcterms:identifier "${isbn}" .
      ?book dcterms:extent ?page .
    } LIMIT 1
  `;
  const fullUrl = `https://lod.nl.go.kr/sparql?query=${encodeURIComponent(query)}&format=json`;

  try {
    const res = await axios.get(fullUrl);
    const value = res.data?.results?.bindings?.[0]?.page?.value || '';
    const match = value.match(/(\d{2,4})/);
    return match ? parseInt(match[1], 10) : 0;
  } catch {
    return 0;
  }
}

async function fetchExtentFromData4Library(isbn) {
  const url = `http://data4library.kr/api/srchDtlList?authKey=${LIBRARY_API_KEY}&isbn13=${isbn}&format=json`;
  try {
    const res = await axios.get(url);
    const doc = res.data.response?.detail?.[0]?.book;
    const extent = doc?.extent || '';
    const match = extent.match(/(\d{2,4})\s*(쪽|페이지|p|면)?/i);
    return match ? parseInt(match[1], 10) : 0;
  } catch {
    return 0;
  }
}

async function fetchPageFromFallbackAPI(isbn) {
  const url = `https://www.nl.go.kr/seoji/SearchApi.do?cert_key=${LIBRARY_API_KEY}&result_style=json&page_no=1&page_size=1&isbn=${isbn}`;
  try {
    const res = await axios.get(url);
    const record = res.data.docs?.[0];
    if (!record) return 0;

    if (record.PAGE) return parseInt(record.PAGE, 10);

    const combined = [record.ETC, record.NOTE, record.SUBJECT].filter(Boolean).join(' ');
    const match = combined.match(/(\d{2,4})\s*(쪽|페이지|p|면)?/i);
    return match ? parseInt(match[1], 10) : 0;
  } catch {
    return 0;
  }
}

function extractPagesFromText(text) {
  const match = text?.match?.(/(\d{2,4})\s*(쪽|페이지|p|면)?/i);
  return match ? parseInt(match[1], 10) : 0;
}

async function resolvePageCount(isbn, description = '') {
  const lod = await fetchPageCountFromLOD(isbn);
  if (lod > 0) {
    return lod;
  }

  const extent = await fetchExtentFromData4Library(isbn);
  if (extent > 0) {
    return extent;
  }

  const fallback = await fetchPageFromFallbackAPI(isbn);
  if (fallback > 0) {
    return fallback;
  }

  const extracted = extractPagesFromText(description);
  if (extracted > 0) {
    return extracted;
  }

  return 200;
}

module.exports = { resolvePageCount };