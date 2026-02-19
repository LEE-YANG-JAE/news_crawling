# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 파일 - 일일 크롤링 단일 EXE 빌드용 (onefile)

빌드 방법:
    1. pip install pyinstaller requests beautifulsoup4 pywin32
    2. 이 파일이 있는 폴더에서 실행:
       pyinstaller daily_runner.spec --noconfirm

결과물:
    dist/일일크롤링.exe  (단일 파일, 어디서든 더블클릭으로 실행)
"""

block_cipher = None

# ─────────────────────────────────────────────
# 1. 분석
# ─────────────────────────────────────────────

entry_script = 'daily_runner.py'

# 동적 import되는 모듈을 명시적으로 지정
hidden_imports = [
    # 프로젝트 내부 모듈
    'http_utils',
    'crawling_english_saying',
    'run_combined',
    'run_headline_crawling',
    'run_economics_crawling',
    'run_opinions_crawling',
    'run_eng_stock_check',
    # requests 관련
    'requests',
    'urllib3',
    'charset_normalizer',
    'certifi',
    'idna',
    # BeautifulSoup
    'bs4',
    'bs4.builder',
    'bs4.builder._htmlparser',
    # pywin32 (바로가기 생성)
    'win32com',
    'win32com.client',
    'win32com.shell',
    'pythoncom',
    'pywintypes',
    'win32api',
    # difflib (경제 뉴스 중복 검사)
    'difflib',
    # json (사설 API)
    'json',
]

# 번들할 데이터 파일: 내부 Python 모듈들
# onefile 모드에서는 _MEIPASS 임시 폴더에 풀림
# daily_runner.py 내 sys.path 설정으로 import 가능
added_data = [
    ('http_utils.py', '.'),
    ('crawling_english_saying.py', '.'),
    ('run_combined.py', '.'),
    ('run_headline_crawling.py', '.'),
    ('run_economics_crawling.py', '.'),
    ('run_opinions_crawling.py', '.'),
    ('run_eng_stock_check.py', '.'),
]

a = Analysis(
    [entry_script],
    pathex=['.'],
    binaries=[],
    datas=added_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 불필요한 패키지 제외 (EXE 크기 최소화)
        'selenium',
        'webdriver_manager',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'Pillow',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'wx',
        'pytest',
        'unittest',
        'setuptools',
        'pip',
        'wheel',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ─────────────────────────────────────────────
# 2. PYZ 바이트코드 아카이브
# ─────────────────────────────────────────────

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# ─────────────────────────────────────────────
# 3. 단일 EXE (onefile 모드)
# ─────────────────────────────────────────────

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # onefile: 바이너리 포함
    a.zipfiles,       # onefile: zip 포함
    a.datas,          # onefile: 데이터 포함
    [],
    name='일일크롤링',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,      # 콘솔 창 표시 (크롤링 진행 로그 확인용)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 아이콘 (원하면 .ico 파일 경로 지정)
    # icon='daily_crawler.ico',
)
