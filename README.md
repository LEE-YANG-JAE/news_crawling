# Daily Gatherings - 일일 크롤링 자동화

매일 뉴스와 영어 명언을 자동 수집하는 크롤링 도구.
Selenium/ChromeDriver 없이 `requests` + `BeautifulSoup`만으로 동작한다.

## 수집 항목

| 항목 | 소스 | 저장 경로 |
|---|---|---|
| 영어 명언 | Hackers영어 | `~/Desktop/{YYYY}년 영어 명언 모음.txt` |
| 뉴스 헤드라인 | 네이버 뉴스 (경제, IT/과학, 세계, 정치, 사회, 생활/문화) | `C:\news\headlines\{YYYY}\{MM}\` |
| 경제 뉴스 | 네이버 경제 섹션 (서브카테고리별) | `C:\news\economics\{YYYY}\{MM}\` |
| 사설 | 네이버 사설 (한국경제, 서울경제, 파이낸셜뉴스, 디지털타임스, 코리아중앙데일리) | `C:\news\opinions\{YYYY}\{MM}\` |
| 영문 주식 뉴스 | finviz.com (전체) | `C:\news\stock_news\{YYYY}\{MM}\` |

## 파일 구조

```
daily_gatherings/
├── daily_runner.py            # 메인 실행 스크립트 (전체 흐름 제어)
├── http_utils.py              # 공통 HTTP 유틸리티 (requests + BS4 래퍼)
├── crawling_english_saying.py # 영어 명언 수집
├── run_combined.py            # 뉴스 크롤링 통합 실행
├── run_headline_crawling.py   # 네이버 헤드라인 크롤링
├── run_economics_crawling.py  # 네이버 경제 뉴스 크롤링
├── run_opinions_crawling.py   # 네이버 사설 크롤링
├── run_eng_stock_check.py     # finviz 영문 주식 뉴스 크롤링
├── daily_runner.spec          # PyInstaller EXE 빌드 설정
├── build_exe.bat              # EXE 빌드 스크립트
└── dist/
    └── 일일크롤링.exe          # 빌드된 단일 실행 파일
```

## 실행 방법

### Python으로 직접 실행

```bash
pip install requests beautifulsoup4 pywin32
python daily_runner.py
```

### EXE로 실행 (빌드 후)

```bash
build_exe.bat
```

빌드 완료 후 `dist/일일크롤링.exe`를 더블클릭하면 된다.

## 실행 흐름

1. **[1/6] 인터넷 연결 확인** - 최대 5회 재시도 (5초 간격)
2. **[2/6] 영어 명언 수집** - 바탕화면 파일에 직접 추가
3. **[3/6] 헤드라인 크롤링** - 네이버 뉴스 섹션별 수집
4. **[4/6] 경제 뉴스 크롤링** - 네이버 경제 서브카테고리별 수집 (중복 제거)
5. **[5/6] 사설 크롤링** - 대상 언론사별 사설 수집
6. **[6/6] 영문 주식 뉴스 크롤링** - finviz 전체 뉴스 수집 + 기사 상세
+ **바탕화면 바로가기 생성** - `C:\news` 폴더의 `.lnk` 파일
+ **실행 결과 요약** - 시작/종료/소요 시간 표시, 콘솔 출력 전체를 로그 파일에 저장

각 크롤러는 독립적으로 실행되며, 하나가 실패해도 나머지는 계속 진행한다.

## 영문 주식 뉴스 상세

`run_eng_stock_check.py`는 finviz.com에서 최신 주식 뉴스 전체를 수집한다.

### 기사 상세 추출 전략

뉴스 소스에 따라 날짜와 본문 추출 방법이 다르다:

| 소스 | 방법 | 비고 |
|---|---|---|
| finviz 내부 (`/news/...`) | finviz 뉴스 상세 페이지에서 직접 파싱 | PR Newswire, GlobeNewswire, MarketBeat 등 대부분의 기사 |
| Yahoo Finance | yahoo 기사 페이지 직접 접근 | 정상 동작 |
| Investopedia | investopedia 기사 페이지 직접 접근 | 정상 동작 |
| BusinessWire | 403 차단 → 본문 수집 불가 | requests로 우회 불가 (봇 차단) |

- finviz가 래퍼 페이지를 제공하는 기사(약 80%)는 `_fetch_from_finviz_page`에서 날짜와 본문을 추출
- 외부 소스에서 실패하면 `finviz_url`이 있는 경우 finviz 페이지로 자동 fallback
- BusinessWire처럼 finviz 래퍼도 없고 직접 접근도 차단되는 경우 제목/URL만 수집

## 필요 패키지

- `requests` - HTTP 요청
- `beautifulsoup4` - HTML 파싱
- `pywin32` - 바탕화면 바로가기 생성

## 로그

실행 로그는 `C:\news\logs\{YYYY}\{MM}\{YYYY-MM-DD}_실행로그.txt`에 저장된다.
