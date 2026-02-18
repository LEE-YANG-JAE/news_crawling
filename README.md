
## 뉴스 크롤링

#### 환경
##### 윈도우 기반
- 파이썬: 3.12 이상
```batch
pip install selenium webdriver-manager pyinstaller
```

#### 파이썬 파일

1. run_headline_crawling.py : 네이버 헤드라인 뉴스들 가져오기기
- C:\news\headlines\연\월\연-월-일_헤드라인 모음.txt 로 저장

2. run_opinions_crawling.py : 네이버 칼럼 특정 사설 위주로 가져 오기
- C:\news\opinions\연\월\연-월-_사설 모음.txt 로 저장
- 
3. run_economics_crawling.py : 네이버 경제 영역별 뉴스로 가져 오기
- C:\news\economics\연\월\연-월-_경제_영역별_뉴스_모음.txt 로 저장

4. run_eng_stock_check.py : inviz.com 주식의 최신 뉴스 30개로 가져 오기
- C:\news\stock_news\연\월\연-월-_Stock_News.txt 로 저장

5. run_combined.py : run_headline_crawling + run_opinions_crawling + run_economics_crawling + run_eng_stock_check

#### 실행파일 만들기

```batch
# pyinstaller 필요
pyinstaller run_combined.spec
```
- 위 명령어를 실행 후 프로젝트 경로의 dist 폴더에 '기사 헤드라인 및 사설 수집.exe' 파일이 생성



