"""
뉴스 크롤링 통합 실행 스크립트.
각 크롤러를 순차 실행하며, 하나가 실패해도 나머지는 계속 진행.
"""

import run_headline_crawling
import run_economics_crawling
import run_opinions_crawling
import run_eng_stock_check


def main():
    """모든 뉴스 크롤러를 순차 실행."""
    print("Starting combined execution...")

    results = {}

    # Run headline crawling
    try:
        run_headline_crawling.main()
        results["헤드라인"] = "성공"
    except Exception as e:
        results["헤드라인"] = f"실패: {e}"
        print(f"[오류] 헤드라인 크롤링 실패: {e}")

    # Run economics crawling
    try:
        run_economics_crawling.main()
        results["경제 뉴스"] = "성공"
    except Exception as e:
        results["경제 뉴스"] = f"실패: {e}"
        print(f"[오류] 경제 뉴스 크롤링 실패: {e}")

    # Run opinions crawling
    try:
        run_opinions_crawling.main()
        results["사설"] = "성공"
    except Exception as e:
        results["사설"] = f"실패: {e}"
        print(f"[오류] 사설 크롤링 실패: {e}")

    # Run eng stock news crawling
    try:
        run_eng_stock_check.main()
        results["영문 주식 뉴스"] = "성공"
    except Exception as e:
        results["영문 주식 뉴스"] = f"실패: {e}"
        print(f"[오류] 영문 주식 뉴스 크롤링 실패: {e}")

    print("\nFinished combined execution.")
    return results


if __name__ == "__main__":
    main()
