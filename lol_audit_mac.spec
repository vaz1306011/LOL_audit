# -*- mode: python ; coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
from lolaudit import __version__

a = Analysis(  # type: ignore
    ["lol_audit.pyw"],
    pathex=[],
    binaries=[],
    datas=[("lol_audit.ico", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)  # type: ignore

exe = EXE(  # type: ignore
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f"lol_audit_{__version__}",
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
    icon=["lol_audit.ico"],
)
app = BUNDLE(  # type: ignore
    exe,
    name="lol_audit.app",
    icon=None,
    bundle_identifier=None,
)
