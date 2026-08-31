# MiSTer virtual save states 5–11

This feature is included in the normal SMW Stream Tracker build.

## Use

1. Open **Downloads > Connection & Emulator Setup > Set Up MiSTer**.
2. Select **Find & Set Up MiSTer** or **Install Virtual Save State Slots**.
3. The app backs up and verifies the exact current
   `/media/fat/MiSTer` file before changing it, then restarts MiSTer.
4. In the SNES core:
   - **Alt+F5 through Alt+F11** saves virtual states 5–11.
   - **F5 through F11** loads virtual states 5–11.
   - **F12** still opens MiSTer's menu.

Native save states 1–4 are preserved. Slot 4 is used only as a temporary
bridge. After a virtual load, its shared data is left untouched for a
three-second safety window so the SNES core can finish reading it before the
native slot 4 data is restored. Save-state input is briefly ignored during that
window to prevent overlapping save-state operations. The feature is SNES-only.

## Return to the original MiSTer

Open the same MiSTer Setup window and select **Restore Previous MiSTer Version**. The
app verifies and restores the exact binary it saved before the experiment,
disables virtual states 5–11, and restarts MiSTer. ROMs and save-state files are
not deleted.

## Rebuilding the MiSTer binary

The release source contains the modified `user_io.cpp`, the upstream license,
the exact official base binary used for verification, and the resulting
`MiSTer-SMW-Virtual-States` binary. `UPSTREAM_SOURCE.txt` records the exact
upstream repository and commit.

To rebuild it, check out that upstream commit as `Main_MiSTer_20260816_custom`,
apply the included `input.cpp`, `user_io.cpp`, and `user_io.h` changes, provide the Arm GNU
10.2-2020.11-compatible Windows toolchain, and run
`build_mister_experimental.ps1`. The build's SHA-256 must match the value pinned
in the tracker before it can be installed.
