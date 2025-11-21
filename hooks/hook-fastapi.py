# PyInstaller hook for FastAPI
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all FastAPI and Starlette submodules
hiddenimports = collect_submodules('fastapi')
hiddenimports += collect_submodules('starlette')
hiddenimports += collect_submodules('pydantic')
hiddenimports += collect_submodules('pydantic_core')
hiddenimports += collect_submodules('uvicorn')

# Collect all data files
datas, binaries, _ = collect_all('fastapi')
tmp_datas, tmp_binaries, _ = collect_all('starlette')
datas += tmp_datas
binaries += tmp_binaries
tmp_datas, tmp_binaries, _ = collect_all('pydantic')
datas += tmp_datas
binaries += tmp_binaries
tmp_datas, tmp_binaries, _ = collect_all('uvicorn')
datas += tmp_datas
binaries += tmp_binaries
