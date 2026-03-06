"""
일일 크롤링 자동화 메인 실행 스크립트.

실행 순서:
1. 인터넷 연결 확인 (5초 간격, 최대 5회 재시도)
2. 영어 명언 수집 (crawling_english_saying.py) → 바탕화면 실제 파일
3. 헤드라인 크롤링 → C:\\news\\headlines
4. 경제 뉴스 크롤링 → C:\\news\\economics
5. 사설 크롤링 → C:\\news\\opinions
6. 영문 주식 뉴스 크롤링 → C:\\news\\stock_news
+ 바탕화면 뉴스 폴더 바로가기 생성 (.lnk)
+ 실행 결과 요약 및 로그 기록

필요 패키지: requests, beautifulsoup4, pywin32
Selenium/ChromeDriver 불필요.

Usage:
    python daily_runner.py
"""

import os
import sys
import time
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─────────────────────────────────────────────
# PyInstaller onefile 호환: _MEIPASS 경로를 sys.path에 추가
# EXE 실행 시 번들된 모듈을 임시 폴더에서 찾을 수 있도록 함
# ─────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

from config import (
    NEWS_DIR, LOGS_DIR,
    INTERNET_MAX_RETRIES, INTERNET_RETRY_INTERVAL,
    MIN_EXPECTED_HEADLINES, MIN_EXPECTED_ECONOMICS,
    MIN_EXPECTED_OPINIONS, MIN_EXPECTED_STOCK_NEWS,
)
from http_utils import check_internet, log, setup_file_logging


# ─────────────────────────────────────────────
# 인터넷 연결 확인
# ─────────────────────────────────────────────

def wait_for_internet(max_retries=INTERNET_MAX_RETRIES, interval=INTERNET_RETRY_INTERVAL):
    """인터넷 연결을 확인. 실패 시 interval초 간격으로 재시도."""
    for attempt in range(1, max_retries + 1):
        log(f"  연결 확인 중... ({attempt}/{max_retries})")
        if check_internet():
            log("  ✓ 인터넷 연결 확인 완료")
            return True

        if attempt < max_retries:
            log(f"  연결 실패. {interval}초 후 재시도...")
            time.sleep(interval)

    return False


# ─────────────────────────────────────────────
# 바탕화면 바로가기 생성
# ─────────────────────────────────────────────

def create_news_shortcut():
    """바탕화면에 C:\\news 폴더의 바로가기(.lnk)를 생성."""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop_path, "뉴스 모음.lnk")

    if os.path.exists(shortcut_path):
        return True

    os.makedirs(NEWS_DIR, exist_ok=True)

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = NEWS_DIR
        shortcut.Description = "일일 뉴스 크롤링 모음"
        shortcut.IconLocation = "shell32.dll,3"
        shortcut.save()
        return True
    except ImportError:
        return False
    except Exception:
        return False


# ─────────────────────────────────────────────
# 크롤링 결과 검증
# ─────────────────────────────────────────────

def validate_count(name, count, min_expected):
    """수집 건수가 기대치 이하이면 WARNING 로그 출력."""
    if count is not None and count < min_expected:
        log(f"  [WARNING] {name}: {count}개 수집 (기대 최소 {min_expected}개) - 셀렉터 변경 확인 필요")


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────

def main():
    start_time = datetime.datetime.now()

    # 로그 파일 핸들러 설정 (즉시 기록)
    today = start_time.strftime('%Y-%m-%d')
    year = start_time.strftime('%Y')
    month = start_time.strftime('%m')
    log_dir = os.path.join(LOGS_DIR, year, month)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f'{today}_실행로그.txt')
    setup_file_logging(log_path)

    log("=" * 60)
    log("  일일 크롤링 자동화")
    log(f"  시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    results = {}

    # ── [1/6] 인터넷 연결 확인 ──
    log("")
    log("[1/6] 인터넷 연결 확인")
    if not wait_for_internet():
        log("  ✗ 인터넷 연결 실패 (5회 시도 후 중단)")
        results["인터넷 연결"] = "실패"
        sys.exit(1)
    results["인터넷 연결"] = "성공"

    # ── [2/6] 영어 명언 수집 ──
    log("")
    log("[2/6] 영어 명언 수집")
    try:
        import crawling_english_saying
        success = crawling_english_saying.insert_latest_quote()
        results["영어 명언 수집"] = "성공" if success else "실패"
    except Exception as e:
        results["영어 명언 수집"] = f"실패: {e}"
        log(f"  ✗ 영어 명언 수집 실패: {e}")

    # ── [3~6] 크롤러 병렬 실행 ──
    log("")
    log("[3~6] 크롤러 4개 병렬 실행")

    import run_headline_crawling
    import run_economics_crawling
    import run_opinions_crawling
    import run_eng_stock_check

    crawlers = [
        ("헤드라인", run_headline_crawling.main, MIN_EXPECTED_HEADLINES),
        ("경제 뉴스", run_economics_crawling.main, MIN_EXPECTED_ECONOMICS),
        ("사설", run_opinions_crawling.main, MIN_EXPECTED_OPINIONS),
        ("영문 주식 뉴스", run_eng_stock_check.main, MIN_EXPECTED_STOCK_NEWS),
    ]

    def _run_crawler(name, func, min_expected):
        """단일 크롤러 실행 래퍼. (name, result_str, count) 반환."""
        try:
            count = func()
            result_str = f"{count}개 수집" if count else "실패"
            return name, result_str, count, min_expected
        except Exception as e:
            return name, f"실패: {e}", None, min_expected

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_run_crawler, name, func, min_exp): name
            for name, func, min_exp in crawlers
        }
        for future in as_completed(futures):
            name, result_str, count, min_exp = future.result()
            results[name] = result_str
            if count is not None:
                validate_count(name, count, min_exp)
            elif "실패" in result_str:
                log(f"  ✗ {name} 크롤링 실패: {result_str}")

    # ── 바탕화면 바로가기 ──
    shortcut_ok = create_news_shortcut()
    results["바탕화면 바로가기"] = "성공" if shortcut_ok else "실패"

    # ── 실행 결과 요약 ──
    end_time = datetime.datetime.now()
    elapsed = end_time - start_time
    total_seconds = int(elapsed.total_seconds())
    h, remainder = divmod(total_seconds, 3600)
    m, s = divmod(remainder, 60)

    log("")
    log("=" * 60)
    log("  실행 결과 요약")
    log("=" * 60)
    for key, value in results.items():
        status = "✓" if "실패" not in str(value) else "✗"
        log(f"  {status} {key}: {value}")
    log("-" * 60)
    log(f"  시작: {start_time.strftime('%H:%M:%S')}")
    log(f"  종료: {end_time.strftime('%H:%M:%S')}")
    log(f"  소요: {h:02d}:{m:02d}:{s:02d}")
    log("=" * 60)

    log("")
    log(f"로그 저장: {log_path}")
    log("일일 크롤링 자동화 완료.")

    # EXE 실행 시 사용자가 결과를 확인할 수 있도록 대기
    if getattr(sys, 'frozen', False):
        log("")
        input("엔터 키를 누르면 종료됩니다...")


if __name__ == "__main__":
    main()
