# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import re

from PyInstaller.utils.hooks import collect_all


project_root = Path(SPECPATH).resolve()
source_text = (project_root / "SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py").read_text(
    encoding="utf-8"
)
version_match = re.search(r'^APP_VERSION = "([^"]+)"', source_text, flags=re.MULTILINE)
app_version = version_match.group(1) if version_match else "0.0.0"
webview_datas, webview_binaries, webview_hiddenimports = collect_all("webview")
certifi_datas, certifi_binaries, certifi_hiddenimports = collect_all("certifi")

localized_notices = []
for notice_name in ("PRIVACY", "LICENSE", "THIRD_PARTY_NOTICE"):
    for language_suffix in ("", ".au", ".es", ".fr", ".de", ".pt-BR"):
        localized_notices.append(
            (
                str(project_root / "installer" / f"{notice_name}{language_suffix}.txt"),
                "installer",
            )
        )

a = Analysis(
    [str(project_root / "SMWStreamTrackerLauncher.py")],
    pathex=[str(project_root)],
    binaries=webview_binaries + certifi_binaries,
    datas=[
        (str(project_root / "banner_background_assets"), "banner_background_assets"),
        (str(project_root / "banner_character_assets"), "banner_character_assets"),
        (str(project_root / "banner_character_assets_user"), "banner_character_assets_user"),
        (str(project_root / "banner_foreground_assets"), "banner_foreground_assets"),
        (str(project_root / "banner_title_assets"), "banner_title_assets"),
        (str(project_root / "banner_element_assets"), "banner_element_assets"),
        (str(project_root / "platform_assets"), "platform_assets"),
        (str(project_root / "app_assets"), "app_assets"),
        (str(project_root / "docs"), "docs"),
    ] + localized_notices + webview_datas + certifi_datas,
    hiddenimports=webview_hiddenimports + certifi_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pythonnet", "clr"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SMWStreamTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "app_assets" / "smw_stream_tracker_icon.png"),
)

collection = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="SMWStreamTracker",
)

app = BUNDLE(
    collection,
    name="SMW Stream Tracker.app",
    icon=str(project_root / "app_assets" / "smw_stream_tracker_icon.png"),
    bundle_identifier="com.freddogg23.smwstreamtracker",
    info_plist={
        "CFBundleDisplayName": "SMW Stream Tracker",
        "CFBundleName": "SMW Stream Tracker",
        "CFBundleShortVersionString": app_version,
        "CFBundleVersion": app_version,
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "NSHumanReadableCopyright": "Copyright (c) 2026 FredDOGG23",
    },
)
