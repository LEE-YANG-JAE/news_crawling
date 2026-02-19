"""
네이버 사설 크롤링 (requests + BeautifulSoup 버전)
Selenium/ChromeDriver 없이 동작.

수집 대상: 특정 언론사의 사설 (한국경제, 서울경제, 파이낸셜뉴스, 디지털타임스, 코리아중앙데일리)
저장 경로: C:\\news\\opinions\\{YYYY}\\{MM}\\{TODAY}_사설_모음.txt

언론사별 officeId 파라미터로 필터링하여 무한스크롤 없이 SSR에서 수집.
"""

import os
import datetime
import time

from http_utils import fetch_soup, log


# 수집 대상 언론사 (이름 → 네이버 뉴스 officeId)
TARGET_PRESS = {
    '한국경제': '015',
    '서울경제': '011',
    '파이낸셜뉴스': '014',
    '디지털타임스': '029',
    '코리아중앙데일리': '640',
}


def fetch_editorial_list():
    """
    대상 언론사별로 사설 페이지를 요청하여 사설 목록을 수집.

    Returns:
        list of (url, press_name)
    """
    editorial_urls = []
    today_str = datetime.datetime.today().strftime('%Y%m%d')

    for press_name, office_id in TARGET_PRESS.items():
        try:
            url = (
                f"https://news.naver.com/opinion/editorial"
                f"?officeId={office_id}&date={today_str}"
            )
            soup = fetch_soup(url)

            editorial_list = soup.find(class_="opinion_editorial_list")
            if editorial_list is None:
                log(f"  [{press_name}] 사설 목록을 찾을 수 없습니다.")
                continue

            items = editorial_list.find_all(class_="opinion_editorial_item")
            count = 0
            for item in items:
                try:
                    link_el = item.find("a", href=True)
                    if link_el:
                        href = link_el.get("href", "")
                        if href and not href.startswith("http"):
                            href = "https://news.naver.com" + href
                        editorial_urls.append((href, press_name))
                        count += 1
                except Exception:
                    continue

            log(f"  [{press_name:10s}] {count}개 수집")
            time.sleep(0.5)

        except Exception as e:
            log(f"  [{press_name}] 사설 수집 실패: {e}")

    return editorial_urls


def fetch_editorial_content(url):
    """
    개별 사설 기사 페이지에서 제목, 날짜, 본문을 추출.

    Returns:
        dict or None
    """
    try:
        soup = fetch_soup(url, delay=1)

        title_el = soup.find(class_="media_end_head_headline")
        title = title_el.get_text(strip=True) if title_el else ""

        date_elements = soup.find_all(class_="media_end_head_info_datestamp_time")
        published_date = None
        modified_date = None

        if len(date_elements) >= 1:
            published_date = date_elements[0].get_text(strip=True)
        if len(date_elements) >= 2:
            mod_el = soup.find(class_="_ARTICLE_MODIFY_DATE_TIME")
            if mod_el:
                modified_date = mod_el.get_text(strip=True)

        body_el = soup.find(class_="_article_body")
        if body_el is None:
            body_el = soup.find(id="newsct_article")
        if body_el is None:
            body_el = soup.find(class_="newsct_article")
        body = body_el.get_text(strip=True) if body_el else ""

        return {
            "title": title,
            "published_date": published_date,
            "modified_date": modified_date,
            "body": body,
        }

    except Exception as e:
        log(f"  ✗ 사설 상세 수집 실패: {e}")
        return None


def main():
    """
    사설 크롤링 메인 함수.

    Returns:
        int: 수집된 총 사설 수
    """
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    opinion_base_dir = os.path.join('C:\\news', 'opinions')
    opinion_directory = os.path.join(opinion_base_dir, year, month)
    os.makedirs(opinion_directory, exist_ok=True)

    opinion_file_path = os.path.join(opinion_directory, f'{today}_사설 모음.txt')

    # 1) 대상 언론사별 사설 목록 수집
    editorial_urls = fetch_editorial_list()

    # 중복 제거
    seen_urls = set()
    unique_urls = []
    for url, press in editorial_urls:
        if url not in seen_urls:
            unique_urls.append((url, press))
            seen_urls.add(url)
    editorial_urls = unique_urls

    if not editorial_urls:
        log("  ✗ 수집된 사설이 없습니다.")
        with open(opinion_file_path, 'w', encoding='utf-8') as file:
            file.write(f"=== {today} 사설 모음 ===\n\n수집된 사설이 없습니다.\n")
        return 0

    # 2) 각 사설 상세 수집 및 파일 작성
    with open(opinion_file_path, 'w', encoding='utf-8') as file:
        file.write(f"=== {today} 사설 모음 ===\n\n\n")

        for idx, (url, press_name) in enumerate(editorial_urls):
            content = fetch_editorial_content(url)
            if content is None:
                file.write(f"사설 수집 실패: {url}\n\n")
                continue

            file.write(f"언론사: {press_name}\n")
            file.write(f"사설 제목: {content['title']}\n")
            if content['published_date']:
                file.write(f"작성일: {content['published_date']}\n")
            if content['modified_date']:
                file.write(f"수정일: {content['modified_date']}\n")
            file.write(f"링크: {url}\n\n")
            file.write(f"내용:\n{content['body']}\n\n")
            file.write("=" * 50 + "\n\n")

    log(f"  ✓ 사설 {len(editorial_urls)}개 → {opinion_file_path}")
    return len(editorial_urls)


if __name__ == "__main__":
    log("=== 사설 크롤링 시작 ===")
    main()
