"""
영문 주식 뉴스 크롤링 (requests + BeautifulSoup 버전)
Selenium/ChromeDriver 없이 동작.

수집 대상: finviz.com 뉴스 + 개별 소스별 기사 상세
저장 경로: C:\\news\\stock_news\\{YYYY}\\{MM}\\{TODAY}_Stock_News.txt

지원 소스: Yahoo Finance, PR Newswire, BusinessWire, GlobeNewsWire,
          Investopedia, NewsFileCorp 등
JS 렌더링이 필요한 소스는 제목/URL만 수집 (graceful degradation)
"""

import os
import datetime
import time
import re

from http_utils import fetch_soup, FINVIZ_HEADERS, HEADERS, log


def crawl_finviz_news():
    """
    finviz.com 뉴스 페이지에서 뉴스 목록을 수집.

    Returns:
        list of dict: [{title, url, labels, press, time, body}, ...]
    """
    news_data = []
    try:
        soup = fetch_soup(
            "https://finviz.com/news.ashx?v=3",
            headers=FINVIZ_HEADERS,
            timeout=15,
        )

        news_div = soup.find(id="news")
        if news_div is None:
            log("  finviz 뉴스 섹션을 찾을 수 없습니다.")
            return news_data

        news_tables = news_div.find_all(class_="news")

        for news_table in news_tables:
            table = news_table.find("table")
            if table is None:
                continue

            rows = table.find_all("tr")

            for row in rows:
                try:
                    news_link_cell = row.find(class_="news_link-cell")
                    if news_link_cell is None:
                        continue

                    badges_container = news_link_cell.find(class_="news-badges-container")
                    if badges_container is None:
                        continue

                    anchors = badges_container.find_all("a")
                    if not anchors:
                        continue

                    # onclick에서 전체 URL 추출 (href는 잘릴 수 있음)
                    onclick = anchors[0].get("onclick", "")
                    onclick_match = re.search(
                        r"trackAndOpenNews\(event,\s*'[^']*',\s*'([^']+)'\)",
                        onclick,
                    )
                    news_url = onclick_match.group(1) if onclick_match else anchors[0].get("href", "")

                    # finviz 내부 URL과 외부 URL 분리
                    finviz_url = ""
                    if news_url and not news_url.startswith("http"):
                        finviz_url = "https://finviz.com" + news_url
                        news_url = finviz_url

                    news_title = anchors[0].get_text(strip=True)

                    # 종목 라벨
                    stock_labels = [
                        label.get_text(strip=True)
                        for label in badges_container.find_all(class_="stock-news-label")
                    ]

                    # 언론사/시간
                    date_cell = news_link_cell.find(class_="news_date-cell")
                    press_name = date_cell.get_text(strip=True) if date_cell else ""

                    news_data.append({
                        "title": news_title,
                        "url": news_url,
                        "finviz_url": finviz_url,
                        "labels": stock_labels,
                        "press": press_name,
                        "time": "",
                        "body": "",
                    })

                except Exception:
                    continue

        log(f"  finviz {len(news_data)}개 수집")

    except Exception as e:
        log(f"  ✗ finviz 크롤링 실패: {e}")

    return news_data


def _fetch_from_finviz_page(url):
    """
    finviz 내부 뉴스 페이지(finviz.com/news/...)에서 날짜와 본문을 추출.

    Returns:
        (time_str, body_str) or (None, None) if parsing fails
    """
    try:
        soup = fetch_soup(url, headers=FINVIZ_HEADERS, timeout=15, delay=1)
        nc = soup.find(class_="news-content")
        if nc is None:
            return None, None

        wrapper = nc.find("div")
        if wrapper is None:
            return None, None

        # 날짜: "February 19, 2026, 4:02 PM" 패턴
        full_text = wrapper.get_text(separator=" ", strip=True)
        date_match = re.search(
            r"((?:January|February|March|April|May|June|July|August|September"
            r"|October|November|December)\s+\d{1,2},\s+\d{4},?\s*\d{1,2}:\d{2}\s*(?:AM|PM)?)",
            full_text,
        )
        article_time = date_match.group(1) if date_match else ""

        # 본문: 첫 번째 충분히 긴 문단
        article_body = ""
        for p in wrapper.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 80:
                article_body = text[:300] + "..." if len(text) > 300 else text
                break

        # 긴 문단이 없으면 첫 몇 개 문단 합치기
        if not article_body:
            paragraphs = wrapper.find_all("p")
            if paragraphs:
                combined = " ".join(p.get_text(strip=True) for p in paragraphs[:3])
                if combined:
                    article_body = combined[:300] + "..." if len(combined) > 300 else combined

        return article_time, article_body
    except Exception:
        return None, None


def fetch_article_detail(data):
    """
    개별 뉴스 소스에 따라 기사 상세(시간, 본문)를 추출.

    finviz 내부 URL은 finviz 페이지에서 직접 파싱.
    외부 URL은 해당 소스 사이트에서 파싱 시도 후,
    실패하면 finviz 내부 페이지로 fallback.

    Args:
        data: dict with 'url' key

    Returns:
        (time_str, body_str)
    """
    url = data.get("url", "")
    article_time = ""
    article_body = ""

    try:
        # finviz 내부 뉴스 페이지 (finviz.com/news/...)
        if "finviz.com/news/" in url:
            t, b = _fetch_from_finviz_page(url)
            if t:
                article_time = t
            if b:
                article_body = b
            return article_time, article_body

        if "finance.yahoo.com" in url:
            soup = fetch_soup(url, delay=1)

            time_el = soup.find(class_="byline-attr-meta-time")
            if time_el:
                article_time = time_el.get_text(strip=True)

            article_div = soup.find(class_="article")
            if article_div:
                body_wrap = article_div.find(class_="body-wrap")
                if body_wrap:
                    body_div = body_wrap.find(class_="body")
                    if body_div:
                        paragraphs = body_div.find_all("p")
                        if paragraphs:
                            first_p = paragraphs[0].get_text(strip=True)
                            if first_p.startswith("By") or len(first_p) < 50:
                                first_p = paragraphs[1].get_text(strip=True) if len(paragraphs) > 1 else first_p
                            article_body = first_p[:300] + "..." if len(first_p) > 300 else first_p

        elif "www.prnewswire.co.uk" in url or "www.prnewswire.com" in url:
            soup = fetch_soup(url, delay=1)

            time_el = soup.find(class_="mb-no")
            if time_el:
                article_time = time_el.get_text(strip=True)

            release_body = soup.find(class_="release-body")
            if release_body:
                row_div = release_body.find(class_="row")
                if row_div:
                    first_p = row_div.find("p")
                    if first_p:
                        text = first_p.get_text(strip=True)
                        article_body = text[:300] + "..." if len(text) > 300 else text

        elif "www.businesswire.com" in url:
            soup = fetch_soup(url, delay=1)

            story = soup.find(class_="bw-release-story")
            if story:
                align_el = story.find(class_="bwalignc")
                if align_el:
                    text = align_el.get_text(strip=True)
                    article_body = text[:300] + "..." if len(text) > 300 else text

        elif "www.globenewswire.com" in url:
            soup = fetch_soup(url, delay=1)

            time_el = soup.find(class_="article-published-source")
            if time_el:
                article_time = time_el.get_text(strip=True)

            body_div = soup.find(class_="article-body")
            if body_div:
                first_p = body_div.find("p")
                if first_p:
                    text = first_p.get_text(strip=True)
                    article_body = text[:300] + "..." if len(text) > 300 else text

        elif "www.investopedia.com" in url:
            soup = fetch_soup(url, delay=1)

            time_el = soup.find(class_="mntl-attribution__item-date")
            if time_el:
                article_time = time_el.get_text(strip=True)

            body_div = soup.find(class_="article-body-content")
            if body_div:
                paragraphs = body_div.find_all(class_="finance-sc-block-html")
                if paragraphs:
                    text = " ".join(p.get_text(strip=True) for p in paragraphs)
                    article_body = text[:300] + "..." if len(text) > 300 else text

        elif "www.newsfilecorp.com" in url:
            soup = fetch_soup(url, delay=1)

            release_el = soup.find(id="release")
            if release_el:
                article_time = release_el.get_text(strip=True)[:100]

            paragraphs = soup.find_all("p")
            if paragraphs:
                text = " ".join(
                    p.get_text(strip=True)
                    for p in paragraphs
                    if not p.get("style")
                )
                article_body = text[:300] + "..." if len(text) > 300 else text

        # 기타 소스는 제목/URL만 유지 (graceful degradation)

    except Exception:
        pass

    # 외부 소스에서 본문을 못 가져온 경우, finviz 내부 페이지로 fallback
    if not article_body:
        finviz_url = data.get("finviz_url", "")
        if finviz_url:
            t, b = _fetch_from_finviz_page(finviz_url)
            if t and not article_time:
                article_time = t
            if b:
                article_body = b

    return article_time, article_body


def main():
    """
    영문 주식 뉴스 크롤링 메인 함수.

    Returns:
        int: 수집된 총 뉴스 수
    """
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    year = datetime.datetime.today().strftime('%Y')
    month = datetime.datetime.today().strftime('%m')

    base_dir = os.path.join('C:\\news', 'stock_news')
    directory = os.path.join(base_dir, year, month)
    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, f'{today}_Stock_News.txt')

    # 1) finviz 뉴스 목록 수집
    news_data = crawl_finviz_news()

    if not news_data:
        log("  ✗ 수집된 뉴스가 없습니다.")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"=== {today} Latest 30 Stock News ===\n\n수집된 뉴스가 없습니다.\n")
        return 0

    # 2) 각 뉴스의 상세 정보 수집
    for data in news_data:
        article_time, article_body = fetch_article_detail(data)
        data["time"] = article_time
        data["body"] = article_body

    # 3) 파일 작성
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"=== {today} Latest 30 Stock News ===\n\n\n")
        for data in news_data:
            file.write(f"Title: {data['title']}\n")
            file.write(f"Press: {data['press']}\n")
            file.write(f"Labels: {', '.join(data['labels'])}\n")
            file.write(f"Date: {data['time']}\n")
            file.write(f"Content: {data['body']}\n")
            file.write(f"Link: {data['url']}\n\n")
            file.write("=" * 50 + "\n\n")

    log(f"  ✓ 주식 뉴스 {len(news_data)}개 → {file_path}")
    return len(news_data)


if __name__ == "__main__":
    log("=== 영문 주식 뉴스 크롤링 시작 ===")
    main()
