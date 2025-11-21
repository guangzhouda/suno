# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules
import os

# 收集所有必需的模块和数据
datas = [
    ('suno_outputs', 'suno_outputs'),
    ('config.example.json', '.')  # 包含配置文件示例
]
binaries = []

# 显式收集所有子模块
hiddenimports = []

# Requests 及其依赖
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('urllib3')
hiddenimports += collect_submodules('certifi')
hiddenimports += collect_submodules('charset_normalizer')
hiddenimports += collect_submodules('idna')

# FastAPI 及其依赖
hiddenimports += collect_submodules('fastapi')
hiddenimports += collect_submodules('starlette')
hiddenimports += collect_submodules('pydantic')
hiddenimports += collect_submodules('pydantic_core')

# Uvicorn
hiddenimports += collect_submodules('uvicorn')

# 其他必需模块
hiddenimports += collect_submodules('multipart')
hiddenimports += ['json', 'base64', 'tempfile', 'pathlib', 'typing', 'os', 're', 'time']

# 使用 collect_all 收集所有资源
packages = ['requests', 'urllib3', 'certifi', 'fastapi', 'starlette', 'pydantic', 'pydantic_core', 'uvicorn']
for package in packages:
    try:
        tmp_ret = collect_all(package)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f"Warning: Could not collect {package}: {e}")

a = Analysis(
    ['suno_web_app_modern.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=list(set(hiddenimports)),  # 去重
    hookspath=['hooks'],  # 使用自定义 hooks 目录
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'tkinter',
        'test',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SunoWeb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
