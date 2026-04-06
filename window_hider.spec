# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['window_hider.py'],
    pathex=[],
    binaries=[('hider.dll', '.')],
    datas=[('settings.json', '.')],
    hiddenimports=['win32gui', 'win32process', 'win32console', 'pystray', 'PIL', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Window Hider',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon='icon.ico',
)
