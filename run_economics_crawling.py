"""
네이버 경제 뉴스 영역별 크롤링 (requests + BeautifulSoup 버전)
Selenium/ChromeDriver 없이 동작.

수집 대상: 경제 섹션 내 서브카테고리별 뉴스
저장 경로: C:\\news\\economics\\{YYYY}\\{MM}\\{TODAY}_경제_영역별_뉴스_모음.txt
"""

import os
import datetime
import time
from difflib import SequenceMatcher

from config import (
    ECONOMICS_DIR, NAVER_ECONOMICS_URL, SECTION_CRAWL_DELAY,
    find_with_fallback,
)
from http_utils import fetch_soup, fetch_article_dates, log


def are_similar(str1, str2, threshold=0.8):
    """두 문자열의 유사도를 비교하여 중복 여부를 판단."""
    return SequenceMatcher(None, str1, str2).ratio() > threshold


def get_economics_subsections():
    """
    경제 섹션 페이지에서 서브카테고리 목록(이름 + URL)을 추출.

    Returns:
        list of dict: [{subsection, url}, ...]
    """
    subsections = []
    try:
        soup = fetch_soup(NAVER_ECONOMICS_URL)

        nav_section = soup.find(class_="ct_snb_nav")
        if nav_section is None:
            log("  ✗ 서브섹션 내비게이션을 찾을 수 없습니다.")
            return subsections

        nav_items = nav_section.find_all(class_="ct_snb_nav_item")
        for item in nav_items:
            link_el = item.find(class_="ct_snb_nav_item_link")
            if link_el:
                text = link_el.get_text(strip=True)
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = "https://news.naver.com" + href
                subsections.append({"subsection": text, "url": href})

    except Exception as e:
        log(f"  ✗ 서브섹션 추출 실패: {e}")

    return subsections


def crawl_subsection_articles(subsection_data):
    """
    특정 서브섹션의 최신 기사 목록을 수집.

    Returns:
        list of dict: [{subsection, title, summary, press, url}, ...]
    """
    articles = []
    try:
        soup = fetch_soup(subsection_data["url"], delay=SECTION_CRAWL_DELAY)

        latest_section = find_with_fallback(soup, "latest_section")
        if latest_section is None:
            return articles

        section_articles = latest_section.find_all(class_="section_article")

        for section_article in section_articles[:4]:
            sa_list = section_article.find(class_="sa_list")
            if sa_list is None:
                continue

            sa_items = sa_list.find_all(class_="sa_item")
            for sa_item in sa_items:
                try:
                    title_el = sa_item.find(class_="sa_text_title")
                    if title_el is None:
                        continue
                    title = title_el.get_text(strip=True)
                    url = title_el.get("href", "")

                    lede_el = sa_item.find(class_="sa_text_lede")
                    summary = lede_el.get_text(strip=True) if lede_el else ""
                    if len(summary) > 70:
                        summary = summary[:70] + "..."

                    press_el = sa_item.find(class_="sa_text_press")
                    press = press_el.get_text(strip=True) if press_el else ""

                    articles.append({
                        "subsection": subsection_data["subsection"],
                        "title": title,
                        "summary": summary,
                        "press": press,
                        "url": url,
                    })
                except Exception:
                    continue

    except Exception as e:
        log(f"  [{subsection_data['subsection']}] 기사 수집 실패: {e}")

    return articles


def main():
    """
    경제 뉴스 크롤링 메인 함수.

    Returns:
        int: 수집된 총 기사 수
    """
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    directory = os.path.join(ECONOMICS_DIR, year, month)
    os.makedirs(directory, exist_ok=True)

    economics_file_path = os.path.join(directory, f'{today}_경제_영역별_뉴스_모음.txt')

    # 1) 서브섹션 목록 수집
    all_section_data = get_economics_subsections()

    # 2) 각 서브섹션별 기사 수집 (중복 제거)
    all_article_data = []
    for section_data in all_section_data:
        articles = crawl_subsection_articles(section_data)
        before = len(all_article_data)
        for article in articles:
            duplicate = False
            for existing in all_article_data:
                if are_similar(existing["title"], article["title"]) or existing["url"] == article["url"]:
                    duplicate = True
                    break
            if not duplicate:
                all_article_data.append(article)
        added = len(all_article_data) - before

        log(f"  [{section_data['subsection']:6s}] {added:3d}개 수집")

    # 3) 파일 작성
    with open(economics_file_path, 'w', encoding='utf-8') as file:
        file.write(f"=== {today} 경제 영역별 뉴스 모음 ===\n\n\n")

        file.write("목차:\n")
        for idx, sd in enumerate(all_section_data, 1):
            file.write(f"{idx}. === {sd['subsection']} ===\n")
        file.write("\n\n")

        current_subsection = None
        for data in all_article_data:
            if current_subsection != data['subsection']:
                current_subsection = data['subsection']
                file.write(f"=== {current_subsection} ===\n\n")

            published_date, modified_date = None, None
            if data["url"]:
                published_date, modified_date = fetch_article_dates(data["url"])

            file.write(f"제목: {data['title']}\n")
            file.write(f"내용: {data['summary']}\n")
            file.write(f"언론사: {data['press']}\n")
            if published_date:
                file.write(f"작성일: {published_date}\n")
            if modified_date:
                file.write(f"수정일: {modified_date}\n")
            file.write(f"링크: {data['url']}\n\n")
            file.write("=" * 50 + "\n\n")

    log(f"  ✓ 경제 뉴스 {len(all_article_data)}개 → {economics_file_path}")
    return len(all_article_data)


if __name__ == "__main__":
    log("=== 경제 뉴스 크롤링 시작 ===")
    main()
