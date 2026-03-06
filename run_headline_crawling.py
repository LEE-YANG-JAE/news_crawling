"""
네이버 뉴스 헤드라인 크롤링 (requests + BeautifulSoup 버전)
Selenium/ChromeDriver 없이 동작.

수집 대상: 경제, IT/과학, 세계, 정치, 사회, 생활/문화
저장 경로: C:\\news\\headlines\\{YYYY}\\{MM}\\{TODAY}_헤드라인_모음.txt
"""

import os
import datetime
import time

from config import (
    HEADLINES_DIR, NAVER_SECTIONS, SECTION_CRAWL_DELAY,
    find_with_fallback, find_all_with_fallback,
)
from http_utils import fetch_soup, fetch_article_dates, log


def crawl_section_headlines(section_name, section_url):
    """
    특정 섹션의 헤드라인 목록을 수집.

    Returns:
        list of dict: [{tab, headline, press, summary, url}, ...]
    """
    results = []
    try:
        soup = fetch_soup(section_url)

        headline_section = find_with_fallback(soup, "headline_section")
        if headline_section is None:
            log(f"  [{section_name}] 헤드라인 섹션을 찾을 수 없습니다.")
            return results

        items = find_all_with_fallback(headline_section, "headline_items")

        for item in items:
            try:
                title_el = item.find(class_="sa_text_strong")
                headline_text = title_el.get_text(strip=True) if title_el else ""

                press_el = item.find(class_="sa_text_press")
                press_text = press_el.get_text(strip=True) if press_el else ""

                lede_el = item.find(class_="sa_text_lede")
                summary_text = lede_el.get_text(strip=True) if lede_el else ""
                if len(summary_text) > 70:
                    summary_text = summary_text[:70] + "..."

                link_el = item.find("a", class_="sa_text_title")
                if link_el is None:
                    link_el = item.find("a", href=True)
                news_url = ""
                if link_el:
                    news_url = link_el.get("data-imp-url") or link_el.get("href", "")

                if headline_text:
                    results.append({
                        "tab": section_name,
                        "headline": headline_text,
                        "press": press_text,
                        "summary": summary_text,
                        "url": news_url,
                    })
            except Exception:
                continue

        log(f"  [{section_name:6s}] {len(results)}개 수집")

    except Exception as e:
        log(f"  [{section_name}] 크롤링 실패: {e}")

    return results


def main():
    """
    헤드라인 크롤링 메인 함수.

    Returns:
        int: 수집된 총 헤드라인 수
    """
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    directory = os.path.join(HEADLINES_DIR, year, month)
    os.makedirs(directory, exist_ok=True)

    headline_file_path = os.path.join(directory, f'{today}_헤드라인_모음.txt')

    # 모든 섹션의 헤드라인 수집
    all_headlines = []
    section_names = []

    for section_name, section_url in NAVER_SECTIONS.items():
        headlines = crawl_section_headlines(section_name, section_url)
        if headlines:
            section_names.append(section_name)
            all_headlines.extend(headlines)
        time.sleep(SECTION_CRAWL_DELAY)

    # 파일 작성
    with open(headline_file_path, 'w', encoding='utf-8') as file:
        file.write(f"=== {today} 헤드라인 모음 ===\n\n\n")

        file.write("목차:\n")
        for idx, name in enumerate(section_names, 1):
            file.write(f"{idx}. === {name} ===\n")
        file.write("\n\n")

        current_tab = None
        for data in all_headlines:
            if current_tab != data['tab']:
                current_tab = data['tab']
                file.write(f"=== {current_tab} ===\n\n")

            published_date, modified_date = None, None
            if data["url"]:
                published_date, modified_date = fetch_article_dates(data["url"])

            file.write(f"제목: {data['headline']}\n")
            file.write(f"내용: {data['summary']}\n")
            file.write(f"언론사: {data['press']}\n")
            if published_date:
                file.write(f"작성일: {published_date}\n")
            if modified_date:
                file.write(f"수정일: {modified_date}\n")
            file.write(f"링크: {data['url']}\n\n")
            file.write("=" * 50 + "\n\n")

    log(f"  ✓ 헤드라인 {len(all_headlines)}개 → {headline_file_path}")
    return len(all_headlines)


if __name__ == "__main__":
    log("=== 헤드라인 크롤링 시작 ===")
    main()
