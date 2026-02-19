"""
Hackers영어 '오늘의 한줄 영어명언' 크롤링 스크립트.

바탕화면의 `{YYYY}년 영어 명언 모음.txt` 파일에 최신 명언을 추가.
파일이 없으면 자동으로 새 파일을 생성.

Usage:
    python crawling_english_saying.py
"""

import os
import re
from datetime import datetime
from typing import Optional, Tuple

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:
    BeautifulSoup = None  # type: ignore

import requests


def contains_hangul(text: str) -> bool:
    """Return True if the given text contains at least one Hangul character."""
    return any("\uac00" <= ch <= "\ud7a3" for ch in text)


def fetch_latest_quote() -> Optional[Tuple[str, str, str]]:
    """
    Fetch the latest quote from the Hackers영어 site.

    Returns:
        A tuple of (date, english_quote, korean_quote) if successful,
        otherwise None.
    """
    url = "https://www.hackers.co.kr/?c=s_eng/eng_contents/B_others_wisesay"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        ),
        "Referer": "https://www.hackers.co.kr/",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as exc:
        from http_utils import log
        log(f"  ✗ 사이트 접속 실패: {exc}")
        return None

    # Extract text from HTML
    if BeautifulSoup is not None:
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(separator="\n")
    else:
        page_text = re.sub(r"<[^>]+>", "\n", response.text)

    lines = [line.strip() for line in page_text.split("\n") if line.strip()]

    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    date: Optional[str] = None
    english_quote: Optional[str] = None
    korean_quote: Optional[str] = None

    for line in lines:
        if date is None:
            m = date_pattern.search(line)
            if m:
                date = m.group(0)
                continue
        if date is not None and english_quote is None:
            if not contains_hangul(line) and len(line.split()) >= 5:
                english_quote = line
                continue
        if english_quote is not None and korean_quote is None:
            if contains_hangul(line) and len(line) >= 10:
                korean_quote = line
                break

    if date and english_quote and korean_quote:
        return date, english_quote, korean_quote

    from http_utils import log
    log("  ✗ 페이지에서 명언 정보를 찾을 수 없습니다.")
    return None


def create_new_file(file_path: str, year: int) -> None:
    """
    연초에 파일이 없을 때 새 파일을 자동 생성.

    Args:
        file_path: 생성할 파일 경로
        year: 연도
    """
    # 바탕화면 디렉토리가 없으면 생성하지 않음 (Desktop은 이미 존재해야 함)
    from http_utils import log
    desktop_dir = os.path.dirname(file_path)
    if not os.path.isdir(desktop_dir):
        log(f"  ✗ 바탕화면 경로를 찾을 수 없습니다: {desktop_dir}")
        return

    header = f"{year}년 영어 명언 모음\n\n"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header)

    log(f"  새 파일 생성: {file_path}")


def insert_latest_quote() -> bool:
    """
    Insert the latest fetched quote into the desktop file.

    Returns:
        True if successful, False otherwise.
    """
    quote_data = fetch_latest_quote()
    if quote_data is None:
        return False
    date, english_quote, korean_quote = quote_data

    year = datetime.now().year
    filename = f"{year}년 영어 명언 모음.txt"

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, filename)

    from http_utils import log

    # 파일이 없으면 자동 생성
    if not os.path.isfile(file_path):
        create_new_file(file_path, year)
        if not os.path.isfile(file_path):
            log(f"  ✗ 파일 생성 실패: {file_path}")
            return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if date in content:
        log(f"  ✓ {date} 명언 이미 존재")
        return True  # 이미 존재하므로 성공으로 처리

    lines = content.splitlines()
    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "":
            insert_index = i + 1
            break

    new_entry = [date, english_quote, "", korean_quote, "", ""]
    new_lines = lines[:insert_index] + new_entry + lines[insert_index:]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    log(f"  ✓ {date} 명언 추가 완료")
    return True


if __name__ == "__main__":
    insert_latest_quote()
