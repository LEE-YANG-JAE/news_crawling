"""
뉴스 크롤링 통합 실행 스크립트.
각 크롤러를 순차 실행하며, 하나가 실패해도 나머지는 계속 진행.

독립 실행 용도. daily_runner.py에서는 사용하지 않음.
"""

from http_utils import log

import run_headline_crawling
import run_economics_crawling
import run_opinions_crawling
import run_eng_stock_check


def main():
    """모든 뉴스 크롤러를 순차 실행."""
    log("=== 뉴스 크롤링 통합 실행 ===")

    results = {}

    try:
        count = run_headline_crawling.main()
        results["헤드라인"] = f"{count}개 수집" if count else "실패"
    except Exception as e:
        results["헤드라인"] = f"실패: {e}"
        log(f"  ✗ 헤드라인 크롤링 실패: {e}")

    try:
        count = run_economics_crawling.main()
        results["경제 뉴스"] = f"{count}개 수집" if count else "실패"
    except Exception as e:
        results["경제 뉴스"] = f"실패: {e}"
        log(f"  ✗ 경제 뉴스 크롤링 실패: {e}")

    try:
        count = run_opinions_crawling.main()
        results["사설"] = f"{count}개 수집" if count else "실패"
    except Exception as e:
        results["사설"] = f"실패: {e}"
        log(f"  ✗ 사설 크롤링 실패: {e}")

    try:
        count = run_eng_stock_check.main()
        results["영문 주식 뉴스"] = f"{count}개 수집" if count else "실패"
    except Exception as e:
        results["영문 주식 뉴스"] = f"실패: {e}"
        log(f"  ✗ 영문 주식 뉴스 크롤링 실패: {e}")

    log("\n=== 통합 실행 완료 ===")
    return results


if __name__ == "__main__":
    main()
