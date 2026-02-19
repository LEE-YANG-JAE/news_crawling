"""
네이버 사설 크롤링 (requests + BeautifulSoup 버전)
Selenium/ChromeDriver 없이 동작.

수집 대상: 특정 언론사의 사설 (한국경제, 서울경제, 파이낸셜뉴스, 디지털타임스, 코리아중앙데일리)
저장 경로: C:\news\opinions\{YYYY}\{MM}\{TODAY}_사설_모음.txt

무한 스크롤 대체 전략:
- 네이버 뉴스 사설 페이지의 초기 SSR 응답에서 사설 목록 추출
- 추가로 내부 API 엔드포인트를 통해 더 많은 사설을 페이지네이션으로 수집
"""

import os
import datetime
import time
import json

import requests as req
from http_utils import fetch_soup, HEADERS


# 수집 대상 언론사
TARGET_PRESS_NAMES = ['한국경제', '서울경제', '파이낸셜뉴스', '디지털타임스', '코리아중앙데일리']


def fetch_editorial_list_from_ssr():
    """
    사설 페이지의 SSR(서버사이드렌더링) 응답에서 사설 목록을 추출.

    Returns:
        list of (url, press_name)
    """
    editorial_urls = []
    try:
        soup = fetch_soup("https://news.naver.com/opinion/editorial")

        # opinion_editorial_list 내 각 아이템에서 언론사명 + URL 추출
        editorial_list = soup.find(class_="opinion_editorial_list")
        if editorial_list is None:
            print("  SSR에서 사설 목록을 찾을 수 없습니다.")
            return editorial_urls

        items = editorial_list.find_all(class_="opinion_editorial_item")
        for item in items:
            try:
                press_el = item.find(class_="press_name")
                if press_el is None:
                    continue
                press_name = press_el.get_text(strip=True)

                if press_name in TARGET_PRESS_NAMES:
                    link_el = item.find("a", href=True)
                    if link_el:
                        href = link_el.get("href", "")
                        if href and not href.startswith("http"):
                            href = "https://news.naver.com" + href
                        editorial_urls.append((href, press_name))
            except Exception:
                continue

        print(f"  SSR에서 {len(editorial_urls)}개 사설 수집 (대상 언론사 기준)")

    except Exception as e:
        print(f"  SSR 사설 목록 수집 실패: {e}")

    return editorial_urls


def fetch_editorial_list_from_api():
    """
    네이버 뉴스 사설 API를 통해 추가 사설 목록을 수집.
    무한 스크롤 대체 방법.

    Returns:
        list of (url, press_name)
    """
    editorial_urls = []
    today_str = datetime.datetime.today().strftime('%Y%m%d')

    # 네이버 뉴스 사설 API 엔드포인트 (date 기반)
    api_url = (
        "https://news.naver.com/api/opinion/editorial"
        f"?date={today_str}"
        "&page={page}"
    )

    for page in range(1, 6):  # 최대 5페이지 시도
        try:
            url = api_url.format(page=page)
            response = req.get(url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                break

            data = response.json()

            # API 응답 구조에 따라 파싱
            items = []
            if isinstance(data, dict):
                items = data.get("editorialList", data.get("items", data.get("data", [])))
            elif isinstance(data, list):
                items = data

            if not items:
                break

            for item in items:
                try:
                    press_name = item.get("pressName", item.get("officeName", ""))
                    if press_name in TARGET_PRESS_NAMES:
                        article_url = item.get("articleUrl", item.get("url", ""))
                        if not article_url:
                            oid = item.get("officeId", item.get("oid", ""))
                            aid = item.get("articleId", item.get("aid", ""))
                            if oid and aid:
                                article_url = f"https://n.news.naver.com/article/{oid}/{aid}"
                        if article_url:
                            editorial_urls.append((article_url, press_name))
                except Exception:
                    continue

            time.sleep(0.5)

        except (req.RequestException, json.JSONDecodeError):
            break

    if editorial_urls:
        print(f"  API에서 추가 {len(editorial_urls)}개 사설 수집")

    return editorial_urls


def fetch_editorial_content(url):
    """
    개별 사설 기사 페이지에서 제목, 날짜, 본문을 추출.

    Returns:
        dict or None
    """
    try:
        soup = fetch_soup(url, delay=1)

        # 제목
        title_el = soup.find(class_="media_end_head_headline")
        title = title_el.get_text(strip=True) if title_el else ""

        # 작성일/수정일
        date_elements = soup.find_all(class_="media_end_head_info_datestamp_time")
        published_date = None
        modified_date = None

        if len(date_elements) >= 1:
            published_date = date_elements[0].get_text(strip=True)
        if len(date_elements) >= 2:
            mod_el = soup.find(class_="_ARTICLE_MODIFY_DATE_TIME")
            if mod_el:
                modified_date = mod_el.get_text(strip=True)

        # 본문
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
        print(f"  사설 상세 수집 실패 ({url}): {e}")
        return None


def main():
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    opinion_base_dir = os.path.join('C:\\news', 'opinions')
    opinion_directory = os.path.join(opinion_base_dir, year, month)
    os.makedirs(opinion_directory, exist_ok=True)

    opinion_file_path = os.path.join(opinion_directory, f'{today}_사설 모음.txt')

    print("=== 사설 크롤링 시작 ===")

    # 1) SSR에서 사설 목록 수집
    editorial_urls = fetch_editorial_list_from_ssr()

    # 2) API에서 추가 수집 시도
    api_urls = fetch_editorial_list_from_api()

    # 중복 제거 후 합치기
    seen_urls = set(url for url, _ in editorial_urls)
    for url, press in api_urls:
        if url not in seen_urls:
            editorial_urls.append((url, press))
            seen_urls.add(url)

    print(f"  총 {len(editorial_urls)}개 사설 수집 완료")

    if not editorial_urls:
        print("  수집된 사설이 없습니다.")
        # 빈 파일이라도 생성
        with open(opinion_file_path, 'w', encoding='utf-8') as file:
            file.write(f"=== {today} 사설 모음 ===\n\n수집된 사설이 없습니다.\n")
        return

    # 3) 각 사설 상세 수집 및 파일 작성
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

    print(f"Opinion file saved at: {opinion_file_path}")


if __name__ == "__main__":
    main()
