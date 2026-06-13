"""
중앙 설정 모듈.
경로, 타임아웃, 딜레이, 섹션 URL, 언론사 ID 등 모든 설정값을 한 곳에서 관리.
"""

import os

# ─────────────────────────────────────────────
# 기본 경로
# ─────────────────────────────────────────────
NEWS_DIR = os.environ.get("NEWS_DIR", r"C:\news")
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

# 하위 디렉토리
HEADLINES_DIR = os.path.join(NEWS_DIR, "headlines")
ECONOMICS_DIR = os.path.join(NEWS_DIR, "economics")
OPINIONS_DIR = os.path.join(NEWS_DIR, "opinions")
STOCK_NEWS_DIR = os.path.join(NEWS_DIR, "stock_news")
LOGS_DIR = os.path.join(NEWS_DIR, "logs")

# ─────────────────────────────────────────────
# HTTP 설정
# ─────────────────────────────────────────────
DEFAULT_TIMEOUT = 10
FINVIZ_TIMEOUT = 15
INTERNET_CHECK_URL = "https://www.google.com"
INTERNET_CHECK_TIMEOUT = 3

# 재시도 설정
RETRY_COUNT = 3
RETRY_BACKOFF = 0.5

# 요청 간 딜레이 (초)
SECTION_CRAWL_DELAY = 1
ARTICLE_DETAIL_DELAY = 0.5
EDITORIAL_LIST_DELAY = 0.5
EDITORIAL_DETAIL_DELAY = 1

# ─────────────────────────────────────────────
# 인터넷 연결 확인
# ─────────────────────────────────────────────
INTERNET_MAX_RETRIES = 5
INTERNET_RETRY_INTERVAL = 5

# ─────────────────────────────────────────────
# 네이버 뉴스 섹션 URL
# ─────────────────────────────────────────────
NAVER_SECTIONS = {
    "경제": "https://news.naver.com/section/101",
    "IT/과학": "https://news.naver.com/section/105",
    "세계": "https://news.naver.com/section/104",
    "정치": "https://news.naver.com/section/100",
    "사회": "https://news.naver.com/section/102",
    "생활/문화": "https://news.naver.com/section/103",
}

NAVER_ECONOMICS_URL = "https://news.naver.com/section/101"

# ─────────────────────────────────────────────
# 사설 대상 언론사 (이름 → officeId)
# ─────────────────────────────────────────────
TARGET_PRESS = {
    "한국경제": "015",
    "서울경제": "011",
    "파이낸셜뉴스": "014",
    "디지털타임스": "029",
    "코리아중앙데일리": "640",
}

# ─────────────────────────────────────────────
# 크롤링 결과 검증 임계값 (이 수 이하이면 WARNING)
# ─────────────────────────────────────────────
MIN_EXPECTED_HEADLINES = 5
MIN_EXPECTED_ECONOMICS = 5
MIN_EXPECTED_OPINIONS = 1
MIN_EXPECTED_STOCK_NEWS = 3

# ─────────────────────────────────────────────
# HTTP 헤더
# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

FINVIZ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finviz.com/",
}

# ─────────────────────────────────────────────
# 셀렉터 fallback 체인
# ─────────────────────────────────────────────
SELECTORS = {
    "headline_section": [
        ("div", {"class_": "section_component as_section_headline"}),
        ("div", {"class_": lambda c: c and "as_section_headline" in c}),
    ],
    "headline_items": [
        ("div", {"class_": "sa_item"}),
        ("li", {"class_": "sa_item"}),
    ],
    "latest_section": [
        (None, {"class_": "section_latest"}),
        (None, {"class_": lambda c: c and "section_latest" in c}),
    ],
    "editorial_list": [
        (None, {"class_": "opinion_editorial_list"}),
    ],
    "article_body": [
        (None, {"class_": "_article_body"}),
        (None, {"id": "newsct_article"}),
        (None, {"class_": "newsct_article"}),
    ],
}


def find_with_fallback(soup, selector_key):
    """셀렉터 fallback 체인을 사용하여 요소를 찾는다."""
    for tag, attrs in SELECTORS[selector_key]:
        if tag:
            el = soup.find(tag, **attrs)
        else:
            el = soup.find(**attrs)
        if el is not None:
            return el
    return None


def find_all_with_fallback(soup, selector_key):
    """셀렉터 fallback 체인을 사용하여 요소 목록을 찾는다."""
    for tag, attrs in SELECTORS[selector_key]:
        if tag:
            elements = soup.find_all(tag, **attrs)
        else:
            elements = soup.find_all(**attrs)
        if elements:
            return elements
    return []
