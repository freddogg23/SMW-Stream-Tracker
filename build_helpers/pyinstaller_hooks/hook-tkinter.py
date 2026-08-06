from pathlib import Path
import sys


python_root = Path(sys.base_prefix)
tcl_root = python_root / "tcl"

datas = [
    (str(tcl_root / "tcl8.6"), "_tcl_data"),
    (str(tcl_root / "tk8.6"), "_tk_data"),
]

binaries = [
    (str(python_root / "DLLs" / "tcl86t.dll"), "."),
    (str(python_root / "DLLs" / "tk86t.dll"), "."),
]
