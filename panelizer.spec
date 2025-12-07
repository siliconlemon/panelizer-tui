# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

PROJECT_DIR = os.getcwd()

a = Analysis(
    ['panelizer/app.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        ('panelizer/tui/css/home.tcss', 'panelizer/tui/css'),
        ('textual_neon/css/globals.tcss', 'textual_neon/css'),
        ('assets', 'assets'),

        *collect_data_files('textual_fspicker'),
    ],
    hiddenimports=[
        'PIL',
        *collect_submodules('PIL'),
        *collect_submodules('textual_fspicker'),
        *collect_submodules('textual_neon'),
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='panelizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='panelizer-tui',
)