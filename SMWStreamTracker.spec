# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


# Development builds keep optional dependencies in local package folders.
# Prefer a local Pillow copy only when it contains the compiled imaging
# extension for the Python runtime doing the build. A complete cp313 Pillow
# folder is still unusable in a cp312 build and otherwise makes PyInstaller
# finish successfully while every branded banner silently disappears at
# runtime.
_python_abi_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
for _pillow_folder_name in (
    ".ui-test-deps",
    ".build-packages",
):
    _pillow_packages = Path(SPECPATH) / _pillow_folder_name
    _pillow_package = _pillow_packages / "PIL"
    if (
        _pillow_package.is_dir()
        and any(
            _pillow_package.glob(
                f"_imaging.{_python_abi_tag}-*.pyd"
            )
        )
    ):
        _pillow_packages_text = str(_pillow_packages)
        while _pillow_packages_text in sys.path:
            sys.path.remove(_pillow_packages_text)
        sys.path.insert(0, _pillow_packages_text)
        break


# Add the remaining optional dependencies after the chosen Python runtime's
# site-packages.
for _package_folder_name in (
    ".build-packages",
    ".app-audio-deps",
    ".volume-mixer-deps",
    ".voice-vad-deps",
):
    _build_packages = Path(SPECPATH) / _package_folder_name
    if _build_packages.is_dir():
        _build_packages_text = str(_build_packages)
        if _build_packages_text not in sys.path:
            sys.path.append(_build_packages_text)


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


# MiSTer setup is a required Windows feature. Do not let collect_all() emit a
# warning and continue with a package that can open but cannot connect over
# SSH. This also verifies Paramiko's compiled cryptography dependencies match
# the exact Python ABI used for the build.
try:
    import bcrypt
    import cryptography
    import nacl
    import paramiko

    if not all(
        hasattr(paramiko, name)
        for name in (
            'AuthenticationException',
            'SSHClient',
            'SSHException',
        )
    ):
        raise ImportError('Paramiko is incomplete')
except Exception as error:
    raise SystemExit(
        'SMW Stream Tracker cannot be packaged without working MiSTer SSH '
        'support. Install Paramiko and matching bcrypt, cryptography, CFFI, '
        f'and PyNaCl wheels for this Python runtime ({type(error).__name__}: '
        f'{error}).'
    ) from error


# Music identification is a required Windows feature too. collect_all() only
# warns when a package is absent, which previously allowed successful EXEs
# with either an empty audio-source picker or a matcher that could record but
# could not compare fingerprints. Stop the build instead.
try:
    import numpy
    import onnxruntime
    import pyaudiowpatch
    import process_audio_capture
    import comtypes
    from pycaw.pycaw import AudioUtilities

    if not hasattr(numpy, 'ndarray'):
        raise ImportError('NumPy is incomplete')
    if not hasattr(onnxruntime, 'InferenceSession'):
        raise ImportError('ONNX Runtime is incomplete')
    if not hasattr(pyaudiowpatch, 'PyAudio'):
        raise ImportError('PyAudioWPatch is incomplete')
    if not hasattr(process_audio_capture, 'ProcessAudioCapture'):
        raise ImportError('ProcessAudioCapture is incomplete')
    if not hasattr(comtypes, 'CoInitialize'):
        raise ImportError('Comtypes is incomplete')
    if not hasattr(AudioUtilities, 'GetAllDevices'):
        raise ImportError('Pycaw is incomplete')
except Exception as error:
    raise SystemExit(
        'SMW Stream Tracker cannot be packaged without Windows music '
        'identification support. Install NumPy, ONNX Runtime, '
        'PyAudioWPatch, ProcessAudioCapture, Pycaw, and Comtypes for this '
        'Python runtime '
        f'({type(error).__name__}: {error}).'
    ) from error


webview_datas, webview_binaries, webview_hiddenimports = collect_all('webview')
paramiko_datas, paramiko_binaries, paramiko_hiddenimports = collect_all('paramiko')
pyaudio_datas, pyaudio_binaries, pyaudio_hiddenimports = collect_all('pyaudiowpatch')
process_audio_datas, process_audio_binaries, process_audio_hiddenimports = collect_all(
    'process_audio_capture'
)
onnxruntime_datas, onnxruntime_binaries, onnxruntime_hiddenimports = collect_all(
    'onnxruntime'
)
pycaw_datas, pycaw_binaries, pycaw_hiddenimports = collect_all('pycaw')
comtypes_datas, comtypes_binaries, comtypes_hiddenimports = collect_all('comtypes')


a = Analysis(
    ['SMWStreamTrackerLauncher.py'],
    pathex=[],
    binaries=(
        webview_binaries
        + paramiko_binaries
        + pyaudio_binaries
        + process_audio_binaries
        + onnxruntime_binaries
        + pycaw_binaries
        + comtypes_binaries
        + [('tools\\chromaprint\\fpcalc.exe', 'chromaprint')]
    ),
    datas=[
        ('banner_background_assets', 'banner_background_assets'),
        ('banner_character_assets', 'banner_character_assets'),
        ('banner_character_assets_user', 'banner_character_assets_user'),
        ('banner_foreground_assets', 'banner_foreground_assets'),
        ('banner_title_assets', 'banner_title_assets'),
        ('banner_element_assets', 'banner_element_assets'),
        ('platform_assets', 'platform_assets'),
        ('app_assets', 'app_assets'),
        ('game_mode_assets', 'game_mode_assets'),
        ('obs_widget', 'obs_widget'),
        (
            'streamdeck\\dist\\SMWStreamTracker-SPC-Controls.streamDeckPlugin',
            'streamdeck',
        ),
        ('tools\\streamerbot_reward_setup.ps1', 'tools'),
        (
            'experiments\\mister_instant_states\\Main_MiSTer_20260816_custom'
            '\\bin_experimental\\MiSTer-SMW-Virtual-States',
            'mister_experimental',
        ),
        (
            'experiments\\mister_instant_states\\Main_MiSTer_20260816_custom\\LICENSE',
            'mister_experimental',
        ),
        (
            'experiments\\mister_instant_states\\UPSTREAM_SOURCE.txt',
            'mister_experimental',
        ),
        (
            'experiments\\mister_instant_states\\README.md',
            'mister_experimental',
        ),
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
    ] + webview_datas + paramiko_datas + pyaudio_datas + process_audio_datas + onnxruntime_datas + pycaw_datas + comtypes_datas,
    hiddenimports=(
        webview_hiddenimports
        + paramiko_hiddenimports
        + pyaudio_hiddenimports
        + process_audio_hiddenimports
        + onnxruntime_hiddenimports
        + pycaw_hiddenimports
        + comtypes_hiddenimports
        + ['numpy']
    ),
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
