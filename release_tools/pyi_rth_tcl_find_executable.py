"""Initialize Tcl's executable path in frozen portable-Python builds.

The python.org embeddable runtime does not initialize Tcl's process path on
its own.  Tk can then see the bundled ``init.tcl`` but still reject it during
application startup.  Calling ``Tcl_FindExecutable`` before tkinter creates
its first interpreter gives frozen builds the same initialization performed
by a normal python.org installation.
"""

from __future__ import annotations

import ctypes
import os
import sys


if os.name == "nt" and getattr(sys, "frozen", False):
    try:
        tcl_dll = ctypes.CDLL(os.path.join(sys._MEIPASS, "tcl86t.dll"))
        tcl_dll.Tcl_FindExecutable.argtypes = [ctypes.c_char_p]
        tcl_dll.Tcl_FindExecutable.restype = None
        tcl_dll.Tcl_FindExecutable(os.fsencode(sys.executable))
    except Exception:
        # The app's normal startup check will report a useful error if Tcl is
        # genuinely unavailable.  Never hide a platform-specific import issue
        # behind this compatibility helper.
        pass
