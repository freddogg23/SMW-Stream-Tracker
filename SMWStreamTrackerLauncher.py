"""Small frozen-app entry point for SMW Stream Tracker.

Keeping the large UI module importable instead of freezing it directly avoids a
Windows/PyInstaller Tcl initialization edge case while preserving normal source
execution for development and tests.
"""

import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

try:
    import certifi
except ImportError:
    certifi = None


NETWORK_CHECK_ARGUMENT = "--network-check"


def configure_secure_networking(
    platform_name=None,
    environment=None,
    certifi_module=None,
):
    """Give frozen Mac builds a reliable HTTPS certificate bundle."""
    active_platform = platform_name or sys.platform
    if active_platform != "darwin":
        return ""

    selected_environment = os.environ if environment is None else environment
    selected_certifi = certifi if certifi_module is None else certifi_module
    if selected_certifi is None:
        raise RuntimeError(
            "The Mac build is missing its HTTPS certificate package."
        )
    ca_bundle = Path(selected_certifi.where()).resolve()
    if not ca_bundle.is_file():
        raise FileNotFoundError(
            f"The bundled HTTPS certificate file is missing: {ca_bundle}"
        )

    for variable_name in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"):
        existing = str(selected_environment.get(variable_name, "")).strip()
        if not existing or not Path(existing).is_file():
            selected_environment[variable_name] = str(ca_bundle)
    return str(ca_bundle)


configure_secure_networking()

import SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER as tracker


def configure_platform_runtime(tracker_module, platform_name=None):
    """Apply platform-only behavior before the main TrackerApp is created."""
    active_platform = platform_name or sys.platform
    if active_platform != "darwin":
        return

    def configure_without_tray(app):
        # pystray's AppKit loop cannot run on TrackerApp's Windows-oriented
        # background tray thread. macOS uses its Dock and normal window instead.
        app.tray_icon = None

    def close_main_window(app):
        # With no menu-bar tray icon, closing the main Mac window must terminate
        # the app instead of hiding a window that cannot be restored.
        app.shutdown()

    tracker_module.pystray = None
    tracker_module.TrackerApp._configure_tray = configure_without_tray
    tracker_module.TrackerApp.hide_to_tray = close_main_window


configure_platform_runtime(tracker)


def run_macos_network_check(tracker_module=tracker):
    """Verify HTTPS from the finished app without downloading large packages."""
    endpoints = (
        (
            "SMW Central catalog",
            (
                tracker_module.SMWC_API_URL
                + "?a=getsectionlist&s=smwhacks&n=1&u=0"
            ),
            "GET",
        ),
        ("SNI", tracker_module.MACOS_SNI_DOWNLOAD_URL, "HEAD"),
        ("QUsb2Snes", tracker_module.MACOS_QUSB2SNES_DOWNLOAD_URL, "HEAD"),
        ("RetroArch", tracker_module.MACOS_RETROARCH_DOWNLOAD_URL, "HEAD"),
    )
    for name, url, method in endpoints:
        request = Request(
            url,
            headers={"User-Agent": f"SMWStreamTracker/{tracker_module.APP_VERSION}"},
            method=method,
        )
        with urlopen(request, timeout=90) as response:
            if method == "GET":
                payload = json.loads(response.read(2 * 1024 * 1024).decode("utf-8"))
                if not isinstance(payload.get("data"), list):
                    raise RuntimeError(
                        "SMW Central returned an invalid catalog response."
                    )
    print("macOS network check passed")


if __name__ == "__main__":
    if NETWORK_CHECK_ARGUMENT in sys.argv:
        run_macos_network_check()
    else:
        tracker.main()
