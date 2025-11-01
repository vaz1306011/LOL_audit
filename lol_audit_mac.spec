# -*- mode: python ; coding: utf-8 -*-
import os
import sys

sys.path.append(os.getcwd())
from lolaudit import __version__

name = f"LolAudit_{__version__}"

a = Analysis(  # type: ignore
    ["lol_audit.pyw"],
    pathex=[],
    binaries=[],
    datas=[("lol_audit.icns", ".")],
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
    name=name,
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
    icon="lol_audit.icns",
)

app = BUNDLE(  # type: ignore
    exe,
    name=name + ".app",
    icon="lol_audit.icns",
    bundle_identifier=None,
)

exe_path = os.path.join("dist", name)
if os.path.exists(exe_path) and not exe_path.endswith(".app"):
    try:
        os.remove(exe_path)
        print(f"Removed extra executable: {exe_path}")
    except Exception as e:
        print(f"Warning: could not remove {exe_path}: {e}")
