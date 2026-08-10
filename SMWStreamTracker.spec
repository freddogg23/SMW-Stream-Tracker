# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


# Keep this validation in the spec itself so quick/manual test builds receive
# the same protection as full release builds. PyInstaller can otherwise finish
# successfully while silently excluding tkinter when the selected Python
# installation has an unusable Tcl/Tk runtime.
try:
    import tkinter as tk

    _tk_build_probe = tk.Tk()
    _tk_build_probe.withdraw()
    _tk_build_probe.update_idletasks()
    _tk_build_probe.destroy()
except Exception as error:
    raise SystemExit(
        "SMW Stream Tracker cannot be packaged with this Python runtime: "
        f"Tkinter/Tcl-Tk failed its build probe ({type(error).__name__}: "
        f"{error}). Use a standard python.org installation with working "
        "Tkinter."
    ) from error


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
        ('installer\\PRIVACY.au.txt', 'installer'),
        ('installer\\PRIVACY.es.txt', 'installer'),
        ('installer\\PRIVACY.fr.txt', 'installer'),
        ('installer\\PRIVACY.de.txt', 'installer'),
        ('installer\\PRIVACY.pt-BR.txt', 'installer'),
        ('installer\\LICENSE.txt', 'installer'),
        ('installer\\LICENSE.au.txt', 'installer'),
        ('installer\\LICENSE.es.txt', 'installer'),
        ('installer\\LICENSE.fr.txt', 'installer'),
        ('installer\\LICENSE.de.txt', 'installer'),
        ('installer\\LICENSE.pt-BR.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.au.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.es.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.fr.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.de.txt', 'installer'),
        ('installer\\THIRD_PARTY_NOTICE.pt-BR.txt', 'installer'),
    ] + webview_datas,
    hiddenimports=webview_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['release_tools\\pyi_rth_tcl_find_executable.py'],
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
