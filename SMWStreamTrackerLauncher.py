"""Small frozen-app entry point for SMW Stream Tracker.

Keeping the large UI module importable instead of freezing it directly avoids a
Windows/PyInstaller Tcl initialization edge case while preserving normal source
execution for development and tests.
"""

import sys

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


if __name__ == "__main__":
    tracker.main()
