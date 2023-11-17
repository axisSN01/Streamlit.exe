# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['run_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("./venv/Lib/site-packages/altair/vegalite/v4/schema/vega-lite-schema.json",
        "./altair/vegalite/v4/schema/"),
        ("./venv/Lib/site-packages/streamlit/static",
        "./streamlit/static"),
        ("./venv/Lib/site-packages/streamlit/runtime",
        "./streamlit/runtime"),
        ("./venv/Lib/site-packages/pyarrow/vendored",
        "./pyarrow/vendored"),
        #("./.streamlit",
        #"%userprofile%/.streamlit"),
        ("./my_exe_App_V1.2.py",
        "."),
        ("./logo.png",
        "."),        
        ],          
    hiddenimports=[],
    hookspath=['./hooks'],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='streamlit_my_exe_App_V1.2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir="./tempdir",
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="app.ico",
)
