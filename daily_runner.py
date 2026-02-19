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

# ─────────────────────────────────────────────
# PyInstaller onefile 호환: _MEIPASS 경로를 sys.path에 추가
# EXE 실행 시 번들된 모듈을 임시 폴더에서 찾을 수 있도록 함
# ─────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

from http_utils import check_internet, log, get_log_buffer, clear_log_buffer


# ─────────────────────────────────────────────
# 인터넷 연결 확인
# ─────────────────────────────────────────────

def wait_for_internet(max_retries=5, interval=5):
    """
    인터넷 연결을 확인. 실패 시 interval초 간격으로 재시도.

    Args:
        max_retries: 최대 재시도 횟수
        interval: 재시도 간격 (초)

    Returns:
        True: 연결 성공
        False: max_retries 초과 시 연결 실패
    """
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
    """
    바탕화면에 C:\\news 폴더의 바로가기(.lnk)를 생성.
    이미 존재하면 건너뛴다.

    Returns:
        True: 생성 성공 또는 이미 존재
        False: 생성 실패
    """
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop_path, "뉴스 모음.lnk")
    target_path = "C:\\news"

    if os.path.exists(shortcut_path):
        return True

    os.makedirs(target_path, exist_ok=True)

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.Description = "일일 뉴스 크롤링 모음"
        shortcut.IconLocation = "shell32.dll,3"
        shortcut.save()
        return True
    except ImportError:
        return False
    except Exception:
        return False


# ─────────────────────────────────────────────
# 로그 파일 기록
# ─────────────────────────────────────────────

def write_log():
    """
    전체 콘솔 출력 버퍼를 로그 파일에 기록.
    로그 파일 = 콘솔 출력의 완전한 복사본.
    """
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    log_dir = os.path.join('C:\\news', 'logs', year, month)
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f'{today}_실행로그.txt')

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(get_log_buffer())

    log(f"로그 저장: {log_path}")


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────

def main():
    clear_log_buffer()
    start_time = datetime.datetime.now()

    log("=" * 60)
    log("  일일 크롤링 자동화")
    log(f"  시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)

    results = {}

    # ── [1/6] 인터넷 연결 확인 ──
    log("")
    log("[1/6] 인터넷 연결 확인")
    if not wait_for_internet(max_retries=5, interval=5):
        log("  ✗ 인터넷 연결 실패 (5회 시도 후 중단)")
        results["인터넷 연결"] = "실패"
        write_log()
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

    # ── [3/6] 헤드라인 크롤링 ──
    log("")
    log("[3/6] 헤드라인 크롤링")
    try:
        import run_headline_crawling
        headline_count = run_headline_crawling.main()
        results["헤드라인"] = f"{headline_count}개 수집" if headline_count else "실패"
    except Exception as e:
        results["헤드라인"] = f"실패: {e}"
        log(f"  ✗ 헤드라인 크롤링 실패: {e}")

    # ── [4/6] 경제 뉴스 크롤링 ──
    log("")
    log("[4/6] 경제 뉴스 크롤링")
    try:
        import run_economics_crawling
        economics_count = run_economics_crawling.main()
        results["경제 뉴스"] = f"{economics_count}개 수집" if economics_count else "실패"
    except Exception as e:
        results["경제 뉴스"] = f"실패: {e}"
        log(f"  ✗ 경제 뉴스 크롤링 실패: {e}")

    # ── [5/6] 사설 크롤링 ──
    log("")
    log("[5/6] 사설 크롤링")
    try:
        import run_opinions_crawling
        opinions_count = run_opinions_crawling.main()
        results["사설"] = f"{opinions_count}개 수집" if opinions_count else "실패"
    except Exception as e:
        results["사설"] = f"실패: {e}"
        log(f"  ✗ 사설 크롤링 실패: {e}")

    # ── [6/6] 영문 주식 뉴스 크롤링 ──
    log("")
    log("[6/6] 영문 주식 뉴스 크롤링")
    try:
        import run_eng_stock_check
        stock_count = run_eng_stock_check.main()
        results["영문 주식 뉴스"] = f"{stock_count}개 수집" if stock_count else "실패"
    except Exception as e:
        results["영문 주식 뉴스"] = f"실패: {e}"
        log(f"  ✗ 영문 주식 뉴스 크롤링 실패: {e}")

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

    # ── 로그 파일 기록 ──
    log("")
    try:
        write_log()
    except Exception as e:
        log(f"  ✗ 로그 기록 실패: {e}")

    log("일일 크롤링 자동화 완료.")

    # EXE 실행 시 사용자가 결과를 확인할 수 있도록 대기
    if getattr(sys, 'frozen', False):
        log("")
        input("엔터 키를 누르면 종료됩니다...")


if __name__ == "__main__":
    main()
