"""
공통 HTTP 유틸리티 모듈
모든 크롤링 스크립트에서 공유하는 requests + BeautifulSoup 래퍼 및 로깅.
Selenium/ChromeDriver 없이 동작.
"""

import sys
import time
import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

from config import (
    HEADERS, FINVIZ_HEADERS,
    DEFAULT_TIMEOUT, RETRY_COUNT, RETRY_BACKOFF,
    INTERNET_CHECK_URL, INTERNET_CHECK_TIMEOUT,
    ARTICLE_DETAIL_DELAY,
)


# ─────────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────────

logger = logging.getLogger("news_crawling")
logger.setLevel(logging.DEBUG)

# 콘솔 핸들러
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setLevel(logging.INFO)
_console_formatter = logging.Formatter("%(message)s")
_console_handler.setFormatter(_console_formatter)
logger.addHandler(_console_handler)

# 파일 핸들러는 setup_file_logging()에서 동적으로 추가
_file_handler = None


def setup_file_logging(log_path):
    """로그 파일 핸들러를 설정. 즉시 기록(flush)."""
    global _file_handler
    if _file_handler is not None:
        logger.removeHandler(_file_handler)
    _file_handler = logging.FileHandler(log_path, encoding="utf-8")
    _file_handler.setLevel(logging.DEBUG)
    _file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    _file_handler.setFormatter(_file_formatter)
    logger.addHandler(_file_handler)


def log(msg=""):
    """콘솔 + 파일에 동시 기록. 기존 인터페이스 호환."""
    if msg:
        logger.info(msg)
    else:
        logger.info("")


# ─────────────────────────────────────────────
# HTTP 세션 (재시도 로직 내장)
# ─────────────────────────────────────────────

def _create_session():
    """재시도 로직이 적용된 requests.Session 생성."""
    session = requests.Session()
    retry = Retry(
        total=RETRY_COUNT,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


_session = _create_session()


def fetch_soup(url, timeout=DEFAULT_TIMEOUT, headers=None, delay=0):
    """
    URL에서 HTML을 가져와 BeautifulSoup 객체로 반환.
    HTTP 레벨 재시도(3회, 백오프 0.5s) 자동 적용.
    """
    if delay > 0:
        time.sleep(delay)
    hdrs = headers if headers is not None else HEADERS
    response = _session.get(url, headers=hdrs, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_text(url, timeout=DEFAULT_TIMEOUT, headers=None, delay=0):
    """URL에서 응답 텍스트(HTML)를 반환."""
    if delay > 0:
        time.sleep(delay)
    hdrs = headers if headers is not None else HEADERS
    response = _session.get(url, headers=hdrs, timeout=timeout)
    response.raise_for_status()
    return response.text


def check_internet(url=INTERNET_CHECK_URL, timeout=INTERNET_CHECK_TIMEOUT):
    """인터넷 연결 여부를 확인."""
    try:
        _session.head(url, timeout=timeout, headers=HEADERS)
        return True
    except requests.RequestException:
        return False


# ─────────────────────────────────────────────
# 공통: 기사 날짜 추출
# ─────────────────────────────────────────────

def fetch_article_dates(url):
    """
    네이버 개별 기사 페이지에서 작성일/수정일을 추출.

    Returns:
        (published_date, modified_date) or (None, None)
    """
    try:
        soup = fetch_soup(url, delay=ARTICLE_DETAIL_DELAY)
        date_elements = soup.find_all(class_="media_end_head_info_datestamp_time")

        published_date = None
        modified_date = None

        if len(date_elements) >= 1:
            published_date = date_elements[0].get_text(strip=True)
        if len(date_elements) >= 2:
            mod_el = soup.find(class_="_ARTICLE_MODIFY_DATE_TIME")
            if mod_el:
                modified_date = mod_el.get_text(strip=True)

        return published_date, modified_date
    except Exception:
        return None, None
