"""
공통 설정 모듈.

모든 크롤링 스크립트가 공유하는 상수/헤더/셀렉터와 **저장 경로 설정**을 정의한다.

저장 경로 설정(config.json)
────────────────────────────
- 실행 파일(또는 이 스크립트) 근처의 `config.json` 에서 저장 폴더를 읽는다.
- 최초 실행 시 `config.json` 이 없으면 기본값으로 자동 생성한다.
    · 영어 명언 저장 폴더 = 사용자 바탕화면(Desktop)
    · 뉴스 저장 폴더      = C:\\news
- 사용자가 `config.json` 의 경로를 수정하면 다음 실행부터 해당 경로에 저장된다.
- `config.json` 은 사용자별 설정이므로 git 추적에서 제외(.gitignore)한다.
"""

import os
import sys
import json


# ─────────────────────────────────────────────
# 저장 경로 설정 (config.json)
# ─────────────────────────────────────────────

def _base_dir():
    """config.json 이 위치할 기준 폴더.

    - EXE(PyInstaller onefile)로 실행 시: 실행 파일이 있는 폴더
    - 일반 파이썬 실행 시: 프로젝트 루트 (core 패키지의 상위 폴더)
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # core/ 의 상위 = 프로젝트 루트
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _desktop_dir():
    """사용자 바탕화면 경로."""
    return os.path.join(os.path.expanduser("~"), "Desktop")


CONFIG_PATH = os.path.join(_base_dir(), "config.json")

# config.json 기본값
DEFAULT_CONFIG = {
    "quotes_dir": _desktop_dir(),   # 영어 명언 저장 폴더 (기본: 바탕화면)
    "news_dir": r"C:\news",         # 뉴스 저장 폴더 (기본: C:\news)
}


def _load_or_create_config():
    """config.json 을 읽어 반환. 없으면 기본값으로 생성.

    - 파일이 없으면: 기본값으로 새로 생성 후 기본값 반환.
    - 파일이 있으면: 읽어서 기본값과 병합(누락 키는 기본값으로 보강).
    - 손상되어 파싱 실패 시: 기본값 사용.
    """
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}

        # 누락 키 보강: 기본값 위에 사용자가 지정한 유효한 값만 덮어쓴다.
        merged = dict(DEFAULT_CONFIG)
        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                merged[key] = value
            elif key not in DEFAULT_CONFIG:
                merged[key] = value

        # 누락 키가 있었다면 파일에 보강해 저장 (선택적 편의 기능).
        if merged != data:
            _save_config(merged)
        return merged

    # 최초 실행: 기본값으로 config.json 생성
    _save_config(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def _save_config(cfg):
    """config.json 을 저장. 실패해도 크롤링은 계속되도록 예외를 흡수한다."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


_cfg = _load_or_create_config()

# ── 사용자 설정에서 파생되는 저장 경로 ──
QUOTES_DIR = _cfg["quotes_dir"]                          # 영어 명언 저장 폴더
NEWS_DIR = _cfg["news_dir"]                              # 뉴스 루트 폴더
LOGS_DIR = os.path.join(NEWS_DIR, "logs")               # 실행 로그
HEADLINES_DIR = os.path.join(NEWS_DIR, "headlines")     # 헤드라인
ECONOMICS_DIR = os.path.join(NEWS_DIR, "economics")     # 경제 뉴스
OPINIONS_DIR = os.path.join(NEWS_DIR, "opinions")       # 사설
STOCK_NEWS_DIR = os.path.join(NEWS_DIR, "stock_news")   # 영문 주식 뉴스


# ─────────────────────────────────────────────
# HTTP 헤더
# ─────────────────────────────────────────────

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

# 네이버 등 일반 요청용
HEADERS = {
    "User-Agent": _USER_AGENT,
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}

# finviz 전용 (봇 차단 회피용 Referer 포함)
FINVIZ_HEADERS = {
    "User-Agent": _USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finviz.com/",
}


# ─────────────────────────────────────────────
# 타임아웃 / 재시도 / 요청 간 딜레이
# ─────────────────────────────────────────────

DEFAULT_TIMEOUT = 10          # 일반 요청 타임아웃(초)
RETRY_COUNT = 3               # HTTP 재시도 횟수
RETRY_BACKOFF = 0.5           # 재시도 백오프 계수

INTERNET_CHECK_URL = "https://www.google.com"
INTERNET_CHECK_TIMEOUT = 5    # 인터넷 연결 확인 타임아웃(초)
INTERNET_MAX_RETRIES = 5      # 인터넷 연결 재시도 최대 횟수
INTERNET_RETRY_INTERVAL = 5   # 인터넷 연결 재시도 간격(초)

ARTICLE_DETAIL_DELAY = 0.5    # 기사 상세 요청 간 딜레이(초)
SECTION_CRAWL_DELAY = 1       # 섹션/서브섹션 크롤링 간 딜레이(초)
EDITORIAL_LIST_DELAY = 1      # 사설 목록 요청 간 딜레이(초)
EDITORIAL_DETAIL_DELAY = 0.5  # 사설 상세 요청 간 딜레이(초)
FINVIZ_TIMEOUT = 15           # finviz 요청 타임아웃(초)


# ─────────────────────────────────────────────
# 수집 건수 검증 임계값 (이하이면 WARNING)
# ─────────────────────────────────────────────

MIN_EXPECTED_HEADLINES = 10
MIN_EXPECTED_ECONOMICS = 10
MIN_EXPECTED_OPINIONS = 3
MIN_EXPECTED_STOCK_NEWS = 10


# ─────────────────────────────────────────────
# 네이버 뉴스 섹션 (헤드라인 크롤링 대상)
#   섹션 번호: 정치 100 / 경제 101 / 사회 102 / 생활·문화 103 / 세계 104 / IT·과학 105
# ─────────────────────────────────────────────

NAVER_SECTIONS = {
    "경제": "https://news.naver.com/section/101",
    "IT/과학": "https://news.naver.com/section/105",
    "세계": "https://news.naver.com/section/104",
    "정치": "https://news.naver.com/section/100",
    "사회": "https://news.naver.com/section/102",
    "생활/문화": "https://news.naver.com/section/103",
}

# 경제 뉴스(서브섹션) 진입 페이지
NAVER_ECONOMICS_URL = "https://news.naver.com/section/101"


# ─────────────────────────────────────────────
# 사설 수집 대상 언론사 (이름 → 네이버 officeId)
# ─────────────────────────────────────────────

TARGET_PRESS = {
    "한국경제": "015",
    "서울경제": "011",
    "파이낸셜뉴스": "014",
    "디지털타임스": "029",
    "코리아중앙데일리": "640",
}


# ─────────────────────────────────────────────
# CSS 셀렉터 (fallback 목록)
#   네이버가 DOM 구조를 바꿔도 견디도록 후보 셀렉터를 순서대로 시도한다.
# ─────────────────────────────────────────────

SELECTORS = {
    # 헤드라인 섹션 컨테이너
    "headline_section": [
        ".section_component.as_section_headline",
        ".as_section_headline",
        ".section_latest",
        ".section_component",
    ],
    # 헤드라인 개별 기사 아이템
    "headline_items": [
        ".sa_item",
        ".sa_list .sa_item",
    ],
    # 경제 서브섹션 최신 기사 영역
    "latest_section": [
        ".section_latest",
        ".section_component.as_section_latest",
        ".section_latest_article",
    ],
    # 사설 목록 컨테이너 (못 찾으면 body 에서 item 을 직접 탐색)
    "editorial_list": [
        "ul.opinion_editorial_list",
        ".opinion_editorial_list",
        ".list_editorial",
        ".opinion_editorial",
        "body",
    ],
    # 기사 본문
    "article_body": [
        "#dic_area",
        "article#dic_area",
        "#newsct_article ._article_body",
        ".newsct_article",
        "._article_content",
        "#articeBody",
    ],
}


def find_with_fallback(node, key):
    """SELECTORS[key] 후보를 순서대로 시도해 처음 매칭되는 단일 요소를 반환.

    매칭이 없으면 None.
    """
    for selector in SELECTORS.get(key, []):
        try:
            element = node.select_one(selector)
        except Exception:
            continue
        if element is not None:
            return element
    return None


def find_all_with_fallback(node, key):
    """SELECTORS[key] 후보를 순서대로 시도해 처음으로 결과가 있는 요소 목록을 반환.

    매칭이 없으면 빈 리스트.
    """
    for selector in SELECTORS.get(key, []):
        try:
            elements = node.select(selector)
        except Exception:
            continue
        if elements:
            return elements
    return []
