
a = Analysis(
    ['GUI.py', 'createCVgraph.py', 'genColors.py', 'loadExcel.py', 'processExcel.py'],
    pathex=['.'],  # Assuming all scripts are in the same directory
    binaries=[],
    datas=[('config.ini', '.')],  # Include config.ini
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='Arbin CV Grapher',
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
)
app = BUNDLE(
    exe,
    name='Arbin CV Grapher.app',
    icon='/Users/hunmac/Downloads/ArbinCVlogo.png',  
    bundle_identifier=None,
)
