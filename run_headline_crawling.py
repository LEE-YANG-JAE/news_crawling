"""
네이버 뉴스 헤드라인 크롤링 (requests + BeautifulSoup 버전)
Selenium/ChromeDriver 없이 동작.

수집 대상: 경제, IT/과학, 세계, 정치, 사회, 생활/문화
저장 경로: C:\news\headlines\{YYYY}\{MM}\{TODAY}_헤드라인_모음.txt
"""

import os
import datetime
import time

from http_utils import fetch_soup, HEADERS


# 네이버 뉴스 섹션별 직접 URL (탭 클릭 대체)
SECTIONS = {
    "경제": "https://news.naver.com/section/101",
    "IT/과학": "https://news.naver.com/section/105",
    "세계": "https://news.naver.com/section/104",
    "정치": "https://news.naver.com/section/100",
    "사회": "https://news.naver.com/section/102",
    "생활/문화": "https://news.naver.com/section/103",
}


def crawl_section_headlines(section_name, section_url):
    """
    특정 섹션의 헤드라인 목록을 수집.

    Returns:
        list of dict: [{tab, headline, press, summary, url}, ...]
    """
    results = []
    try:
        soup = fetch_soup(section_url)

        # 헤드라인 섹션 찾기
        headline_section = soup.find("div", class_="section_component as_section_headline")
        if headline_section is None:
            # 클래스명이 여러 개인 경우 대비
            headline_section = soup.find("div", class_=lambda c: c and "as_section_headline" in c)

        if headline_section is None:
            print(f"  [{section_name}] 헤드라인 섹션을 찾을 수 없습니다.")
            return results

        # 각 헤드라인 아이템 추출
        items = headline_section.find_all("div", class_="sa_item")
        if not items:
            # sa_item이 없으면 sa_text 기반으로 시도
            items = headline_section.find_all("li", class_="sa_item")

        for item in items:
            try:
                # 제목
                title_el = item.find(class_="sa_text_strong")
                headline_text = title_el.get_text(strip=True) if title_el else ""

                # 언론사
                press_el = item.find(class_="sa_text_press")
                press_text = press_el.get_text(strip=True) if press_el else ""

                # 요약
                lede_el = item.find(class_="sa_text_lede")
                summary_text = lede_el.get_text(strip=True) if lede_el else ""
                if len(summary_text) > 70:
                    summary_text = summary_text[:70] + "..."

                # URL
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

        print(f"  [{section_name}] {len(results)}개 헤드라인 수집")

    except Exception as e:
        print(f"  [{section_name}] 크롤링 실패: {e}")

    return results


def fetch_article_dates(url):
    """
    개별 기사 페이지에서 작성일/수정일을 추출.

    Returns:
        (published_date, modified_date) or (None, None)
    """
    try:
        soup = fetch_soup(url, delay=0.5)
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


def main():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    base_dir = os.path.join('C:\\news', 'headlines')
    directory = os.path.join(base_dir, year, month)
    os.makedirs(directory, exist_ok=True)

    headline_file_path = os.path.join(directory, f'{today}_헤드라인_모음.txt')

    print("=== 헤드라인 크롤링 시작 ===")

    # 모든 섹션의 헤드라인 수집
    all_headlines = []
    section_names = []

    for section_name, section_url in SECTIONS.items():
        headlines = crawl_section_headlines(section_name, section_url)
        if headlines:
            section_names.append(section_name)
            all_headlines.extend(headlines)
        time.sleep(1)  # 섹션 간 딜레이

    # 파일 작성
    with open(headline_file_path, 'w', encoding='utf-8') as file:
        file.write(f"=== {today} 헤드라인 모음 ===\n\n\n")

        # 목차
        file.write("목차:\n")
        for idx, name in enumerate(section_names, 1):
            file.write(f"{idx}. === {name} ===\n")
        file.write("\n\n")

        # 각 헤드라인 상세 (기사별 날짜 포함)
        current_tab = None
        for data in all_headlines:
            if current_tab != data['tab']:
                current_tab = data['tab']
                file.write(f"=== {current_tab} ===\n\n")

            # 기사 페이지에서 날짜 추출
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

    print(f"Headline file saved at: {headline_file_path}")


if __name__ == "__main__":
    main()
