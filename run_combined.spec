# run_combined.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# Path to the executable
exe_file_path = os.path.join('dist', '기사 헤드라인 및 사설 수집.exe')

# Check if the exe file exists and delete it
if os.path.exists(exe_file_path):
    print(f"Deleting existing executable: {exe_file_path}")
    os.remove(exe_file_path)

block_cipher = None

a = Analysis(
    ['run_combined.py'],
    pathex=[],
    datas=[('run_headline_crawling.py', '.'), ('run_economics_crawling.py', '.'), ('run_opinions_crawling.py', '.')
         , ('run_eng_stock_check.py', '.')] + collect_data_files('selenium', includes=['**/selenium-manager*']),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='기사 헤드라인 및 사설 수집',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set this to True to see console output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
