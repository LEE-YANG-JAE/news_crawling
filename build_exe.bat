@echo off
chcp 65001 >nul
echo ============================================
echo   일일 크롤링 단일 EXE 빌드
echo ============================================
echo.

REM 1. 필요 패키지 설치
echo [1/3] 필요 패키지 설치 중...
pip install requests beautifulsoup4 pywin32 pyinstaller --quiet
if errorlevel 1 (
    echo [오류] 패키지 설치 실패. pip 확인 필요.
    pause
    exit /b 1
)
echo       완료.
echo.

REM 2. EXE 빌드 (onefile)
echo [2/3] 단일 EXE 빌드 중... (1~2분 소요)
pyinstaller daily_runner.spec --noconfirm
if errorlevel 1 (
    echo [오류] EXE 빌드 실패.
    pause
    exit /b 1
)
echo       완료.
echo.

REM 3. 결과 확인
echo [3/3] 빌드 결과 확인
if exist "dist\일일크롤링.exe" (
    echo.
    echo ============================================
    echo   빌드 성공!
    echo   파일: dist\일일크롤링.exe
    echo ============================================
    echo.
    echo   이 파일 하나만 복사해서 아무 곳에서나
    echo   더블클릭으로 실행하면 됩니다.
    echo.
) else (
    echo [오류] dist\일일크롤링.exe 를 찾을 수 없습니다.
)

pause
