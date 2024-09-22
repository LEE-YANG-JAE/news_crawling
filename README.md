
## 네이버 뉴스 크롤링

#### 환경
##### 윈도우 기반
- 파이썬: 3.12
```batch
# selenium 필요
pip install selenium
pip install pyinstaller
```
- 크롬 드라이버: 129.0.6668.58
- 크롬: 129.0.6668.59

#### 파이썬 파일

1. run_headline_crawling.py : 네이버 헤드라인 뉴스들 가져오기기
- C:\news\headlines\연\월\연-월-일_헤드라인 모음.txt 로 저장

2. run_opinions_crawling.py : 네이버 칼럼 특정 사설 위주로 가져오기
- C:\news\opinions\연\월\연-월-_사설 모음.txt 로 저장

3. run_combined.py : run_headline_crawling + run_opinions_crawling

#### 실행파일 만들기

```batch
# pyinstaller 필요
pyinstaller --onefile --add-data "./chromedriver.exe;." --name "기사 헤드라인 및 사설 수집" .\run_combined.py
```
- 위 명령어를 실행 후 프로젝트 경로의 dist 폴더에 '기사 헤드라인 및 사설 수집.exe' 파일이 생성



