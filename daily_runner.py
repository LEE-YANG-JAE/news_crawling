"""
일일 크롤링 자동화 메인 실행 스크립트.

실행 순서:
1. 인터넷 연결 확인 (5초 간격, 최대 5회 재시도)
2. 영어 명언 수집 (crawling_english_saying.py) → 바탕화면 실제 파일
3. 뉴스 크롤링 (run_combined.py) → C:\\news 에 저장
4. 바탕화면 뉴스 폴더 바로가기 생성 (.lnk)
5. 실행 결과 요약 및 로그 기록

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
    # PyInstaller로 빌드된 EXE에서 실행 중
    bundle_dir = sys._MEIPASS
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

from http_utils import check_internet


# ─────────────────────────────────────────────
# 1. 인터넷 연결 확인
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
        print(f"  인터넷 연결 확인 중... ({attempt}/{max_retries})")
        if check_internet():
            print("  인터넷 연결 확인 완료.")
            return True

        if attempt < max_retries:
            print(f"  연결 실패. {interval}초 후 재시도합니다...")
            time.sleep(interval)

    return False


# ─────────────────────────────────────────────
# 2. 바탕화면 바로가기 생성
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

    # 이미 존재하면 건너뛰기
    if os.path.exists(shortcut_path):
        print("  바탕화면 바로가기가 이미 존재합니다.")
        return True

    # 대상 폴더가 없으면 생성
    os.makedirs(target_path, exist_ok=True)

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.Description = "일일 뉴스 크롤링 모음"
        shortcut.IconLocation = "shell32.dll,3"  # 폴더 아이콘
        shortcut.save()
        print(f"  바탕화면 바로가기 생성 완료: {shortcut_path}")
        return True
    except ImportError:
        print("  [경고] pywin32가 설치되지 않아 바로가기를 생성할 수 없습니다.")
        print("  설치 방법: pip install pywin32")
        return False
    except Exception as e:
        print(f"  [오류] 바로가기 생성 실패: {e}")
        return False


# ─────────────────────────────────────────────
# 3. 로그 기록
# ─────────────────────────────────────────────

def write_log(results):
    """
    실행 결과를 로그 파일에 기록.

    Args:
        results: dict of {항목: 결과문자열}
    """
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    log_dir = os.path.join('C:\\news', 'logs', year, month)
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f'{today}_실행로그.txt')
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"=== 일일 크롤링 실행 로그 ===\n")
        f.write(f"실행 시각: {now}\n\n")

        for key, value in results.items():
            status = "✓" if "성공" in str(value) else "✗"
            f.write(f"  {status} {key}: {value}\n")

        f.write(f"\n로그 기록 완료: {now}\n")

    print(f"  로그 저장: {log_path}")


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  일일 크롤링 자동화 시작")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {}

    # ── Step 1: 인터넷 연결 확인 ──
    print("\n[Step 1] 인터넷 연결 확인")
    if not wait_for_internet(max_retries=5, interval=5):
        msg = "인터넷 연결을 확인할 수 없습니다. 크롤링을 중단합니다."
        print(f"\n  ✗ {msg}")
        results["인터넷 연결"] = "실패 (5회 시도 후 중단)"
        write_log(results)
        sys.exit(1)
    results["인터넷 연결"] = "성공"

    # ── Step 2: 영어 명언 수집 (우선 실행) ──
    print("\n[Step 2] 영어 명언 수집")
    try:
        import crawling_english_saying
        success = crawling_english_saying.insert_latest_quote()
        results["영어 명언 수집"] = "성공" if success else "실패 (데이터 없음)"
    except Exception as e:
        results["영어 명언 수집"] = f"실패: {e}"
        print(f"  [오류] 영어 명언 수집 실패: {e}")

    # ── Step 3: 뉴스 크롤링 전 인터넷 재확인 ──
    print("\n[Step 3] 뉴스 크롤링 전 인터넷 재확인")
    if not check_internet():
        print("  인터넷 연결이 끊어졌습니다. 뉴스 크롤링을 건너뜁니다.")
        results["뉴스 크롤링"] = "건너뜀 (인터넷 연결 끊김)"
    else:
        print("  인터넷 연결 확인.")

        # ── Step 4: 뉴스 크롤링 실행 ──
        print("\n[Step 4] 뉴스 크롤링 실행")
        try:
            import run_combined
            crawl_results = run_combined.main()
            if crawl_results:
                results.update(crawl_results)
            else:
                results["뉴스 크롤링"] = "성공"
        except Exception as e:
            results["뉴스 크롤링"] = f"실패: {e}"
            print(f"  [오류] 뉴스 크롤링 실패: {e}")

    # ── Step 5: 바탕화면 바로가기 생성 ──
    print("\n[Step 5] 바탕화면 바로가기 생성")
    shortcut_ok = create_news_shortcut()
    results["바탕화면 바로가기"] = "성공" if shortcut_ok else "실패"

    # ── Step 6: 실행 결과 요약 ──
    print("\n" + "=" * 60)
    print("  실행 결과 요약")
    print("=" * 60)
    for key, value in results.items():
        status = "✓" if "성공" in str(value) else "✗"
        print(f"  {status} {key}: {value}")
    print("=" * 60)

    # ── Step 7: 로그 기록 ──
    print("\n[Step 6] 로그 기록")
    try:
        write_log(results)
    except Exception as e:
        print(f"  [경고] 로그 기록 실패: {e}")

    print("\n일일 크롤링 자동화 완료.")


if __name__ == "__main__":
    main()
