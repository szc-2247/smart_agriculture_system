# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['account.py'],
    pathex=[],
    binaries=[],
    datas=[('accounts.txt', '.'), ('dirt.txt', '.'), ('logo.png', '.'), ('logo1.png', '.'), ('message.txt', '.'), ('price.txt', '.'), ('search_results.txt', '.'), ('seed.txt', '.'), ('traceability_data.txt', '.'), ('weather1.txt', '.'), ('weather7.txt', '.'), ('willdo.txt', '.')],
    hiddenimports=['tkcalendar'],
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
    [],
    exclude_binaries=True,
    name='account',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='account',
)
