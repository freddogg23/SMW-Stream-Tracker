"""Small frozen-app entry point for SMW Stream Tracker.

Keeping the large UI module importable instead of freezing it directly avoids a
Windows/PyInstaller Tcl initialization edge case while preserving normal source
execution for development and tests.
"""

import SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER as tracker


if __name__ == "__main__":
    tracker.main()
