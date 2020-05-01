# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


def find_packages():
    import os.path
    from pathlib import Path

    out = []

    for f in Path(".").rglob("**/for_redistribution_files_only/*"):
        head, tail = os.path.split(f)

        if os.path.isdir(f) and tail.lower() in head.lower():
            out.append((f, tail,))

    return out


data = [
    ("res", "res"),
    ("LICENSE", "."),
    *find_packages(),
]

a = Analysis(
    ["src\\main.py"],
    pathex=["C:\\pymoda"],
    binaries=[],
    datas=data,
    hiddenimports=[
        "qasync",
        "gui.dialogs.files.DragDropLabel",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PyMODA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="main",
)
