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

> 저장 경로는 **기본값**이며 `config.json` 으로 변경할 수 있다. 아래 [설정](#설정-저장-폴더-변경) 참고.

## 설정 (저장 폴더 변경)

저장 폴더는 **실행 파일(또는 스크립트) 근처의 `config.json`** 으로 지정한다.
최초 실행 시 `config.json` 이 없으면 아래 기본값으로 자동 생성된다.

```json
{
  "quotes_dir": "C:\\Users\\<사용자>\\Desktop",
  "news_dir": "C:\\news"
}
```

| 키 | 의미 | 기본값 |
|---|---|---|
| `quotes_dir` | 영어 명언 `.txt` 저장 폴더 | 사용자 바탕화면(Desktop) |
| `news_dir` | 뉴스 저장 루트 폴더 (headlines·economics·opinions·stock_news·logs 하위 생성) | `C:\news` |

- 폴더를 바꾸려면 `config.json` 의 값을 원하는 경로로 수정 후 다시 실행한다. (역슬래시는 `\\` 로 입력)
- 지정한 폴더가 없으면 자동으로 만든다.
- `config.json` 은 사용자별 설정이라 git 추적에서 제외된다(`.gitignore`).
- EXE를 새로 빌드하면(`build_exe.bat`) 위 동작이 그대로 적용된다.

## 파일 구조

```
daily_gatherings/
├── daily_runner.py                # 진입점 (전체 흐름 제어)
├── core/                          # 핵심 모듈 패키지
│   ├── __init__.py
│   ├── config.py                  # 설정 모듈 (저장 경로/헤더/셀렉터/officeId)
│   ├── http_utils.py              # 공통 HTTP 유틸리티 (requests + BS4 래퍼)
│   ├── crawling_english_saying.py # 영어 명언 수집
│   ├── run_headline_crawling.py   # 네이버 헤드라인 크롤링
│   ├── run_economics_crawling.py  # 네이버 경제 뉴스 크롤링
│   ├── run_opinions_crawling.py   # 네이버 사설 크롤링
│   └── run_eng_stock_check.py     # finviz 영문 주식 뉴스 크롤링
├── daily_runner.spec              # PyInstaller EXE 빌드 설정
├── build_exe.bat                  # EXE 빌드 스크립트
├── config.json                    # 사용자 저장 경로 설정 (첫 실행 시 자동 생성, git 제외)
└── dist/
    └── 일일크롤링.exe              # 빌드된 단일 실행 파일
```

> `daily_runner.py` 만 진입점으로 루트에 두고, 나머지 모듈은 `core/` 패키지로 묶어
> `from core.config import ...` 처럼 불러온다.

## 실행 방법

### Python으로 직접 실행

```bash
pip install requests beautifulsoup4 pywin32
python daily_runner.py
```

개별 크롤러만 따로 실행하려면 프로젝트 루트에서 **모듈 형태(`-m`)** 로 실행한다
(절대 import 사용으로 `python core/run_x.py` 직접 실행은 안 됨).

```bash
python -m core.run_headline_crawling
```

### EXE로 실행 (빌드 후)

빌드는 아래 [빌드 (EXE 만들기)](#빌드-exe-만들기) 참고. 빌드 완료 후
`dist/일일크롤링.exe`를 더블클릭하면 된다.

## 빌드 (EXE 만들기)

[PyInstaller](https://pyinstaller.org/)로 **단일 실행 파일(onefile)** 을 만든다.
파이썬이 설치되지 않은 PC에서도 `일일크롤링.exe` 하나만 복사하면 실행된다.

### 빠른 빌드

프로젝트 폴더에서 아래 배치 파일을 더블클릭(또는 실행):

```bash
build_exe.bat
```

`build_exe.bat` 은 3단계를 자동으로 수행한다.

1. **필요 패키지 설치** — `requests`, `beautifulsoup4`, `pywin32`, `pyinstaller` 를 `pip install`
2. **EXE 빌드** — `pyinstaller daily_runner.spec --noconfirm` (약 1~2분 소요)
3. **결과 확인** — `dist\일일크롤링.exe` 생성 여부 출력

### 수동 빌드

배치 파일 없이 직접 실행해도 된다.

```bash
pip install requests beautifulsoup4 pywin32 pyinstaller
pyinstaller daily_runner.spec --noconfirm
```

### 빌드 설정 (`daily_runner.spec`)

- **onefile** — 모든 모듈·라이브러리를 하나의 `.exe`로 패키징
- **console=True** — 콘솔 창에 크롤링 진행 로그 표시
- 프로젝트 모듈(`config.py`, `http_utils.py`, `run_*.py` 등)을 명시적으로 포함
- 불필요한 대용량 패키지(`selenium`, `numpy`, `pandas` 등)는 제외해 용량 최소화

> 빌드 산출물 `build/`, `dist/` 폴더는 git 추적에서 제외된다(`.gitignore`).

### 결과물과 배포

- 빌드 결과: **`dist/일일크롤링.exe`** (단일 파일)
- 이 `.exe` 하나만 원하는 PC/폴더에 복사하면 더블클릭으로 실행된다.
- **첫 실행 시 `.exe` 와 같은 폴더에 `config.json` 이 자동 생성**된다.
  저장 폴더를 바꾸려면 이 `config.json` 을 수정하면 된다
  ([설정](#설정-저장-폴더-변경) 참고). `config.json` 은 exe 내부에 포함되지 않으므로,
  exe를 다시 빌드해도 기존 설정은 유지된다.

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
