"""
공통 HTTP 유틸리티 모듈
모든 크롤링 스크립트에서 공유하는 requests + BeautifulSoup 래퍼.
Selenium/ChromeDriver 없이 동작.
"""

import time
import requests
from bs4 import BeautifulSoup

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


def fetch_soup(url, timeout=10, headers=None, delay=0):
    """
    URL에서 HTML을 가져와 BeautifulSoup 객체로 반환.

    Args:
        url: 요청할 URL
        timeout: 요청 타임아웃 (초)
        headers: 커스텀 헤더 (None이면 기본 HEADERS 사용)
        delay: 요청 전 대기 시간 (초), 서버 부하 방지용

    Returns:
        BeautifulSoup 객체

    Raises:
        requests.RequestException: 요청 실패 시
    """
    if delay > 0:
        time.sleep(delay)
    hdrs = headers if headers is not None else HEADERS
    response = requests.get(url, headers=hdrs, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_text(url, timeout=10, headers=None, delay=0):
    """
    URL에서 응답 텍스트(HTML)를 반환.

    Args:
        url: 요청할 URL
        timeout: 요청 타임아웃 (초)
        headers: 커스텀 헤더
        delay: 요청 전 대기 시간 (초)

    Returns:
        응답 텍스트 (str)
    """
    if delay > 0:
        time.sleep(delay)
    hdrs = headers if headers is not None else HEADERS
    response = requests.get(url, headers=hdrs, timeout=timeout)
    response.raise_for_status()
    return response.text


def check_internet(url="https://www.google.com", timeout=3):
    """
    인터넷 연결 여부를 확인.

    Returns:
        True: 연결됨, False: 연결 안 됨
    """
    try:
        requests.head(url, timeout=timeout, headers=HEADERS)
        return True
    except requests.RequestException:
        return False
