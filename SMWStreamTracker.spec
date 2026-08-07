# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


webview_datas, webview_binaries, webview_hiddenimports = collect_all('webview')


a = Analysis(
    ['SMWStreamTrackerLauncher.py'],
    pathex=[],
    binaries=webview_binaries,
    datas=[
        ('banner_background_assets', 'banner_background_assets'),
        ('banner_character_assets', 'banner_character_assets'),
        ('banner_character_assets_user', 'banner_character_assets_user'),
        ('banner_foreground_assets', 'banner_foreground_assets'),
        ('banner_title_assets', 'banner_title_assets'),
        ('banner_element_assets', 'banner_element_assets'),
        ('platform_assets', 'platform_assets'),
        ('app_assets', 'app_assets'),
        ('docs', 'docs'),
        ('installer\\PRIVACY.txt', 'installer'),
        ('installer\\LICENSE.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.txt', 'installer'),
    ] + webview_datas,
    hiddenimports=webview_hiddenimports,
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
    name='SMWStreamTracker',
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
    icon='app_assets\\smw_stream_tracker_icon.ico',
    version='version_info.txt',
)
