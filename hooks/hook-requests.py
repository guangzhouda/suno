# PyInstaller hook for requests library
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all requests submodules
hiddenimports = collect_submodules('requests')
hiddenimports += collect_submodules('urllib3')
hiddenimports += collect_submodules('certifi')
hiddenimports += collect_submodules('charset_normalizer')
hiddenimports += collect_submodules('idna')

# Collect all data files
datas, binaries, _ = collect_all('requests')
tmp_datas, tmp_binaries, _ = collect_all('urllib3')
datas += tmp_datas
binaries += tmp_binaries
tmp_datas, tmp_binaries, _ = collect_all('certifi')
datas += tmp_datas
binaries += tmp_binaries
