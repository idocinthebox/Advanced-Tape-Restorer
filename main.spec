# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for Advanced Tape Restorer v4.1
Builds single-file portable executable with real capture hardware support

v4.1 NEW FEATURES:
- Real DirectShow capture device detection
- Analog capture engine (VHS, Hi8, S-Video, Component)
- DV/FireWire capture engine
- Lazy device loading for faster startup
- Built-in PyInstaller temp cleanup
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Config files
        ('restoration_presets.json', '.'),
        ('restoration_settings.json', '.'),
    ],
    hiddenimports=[
        # PySide6 (GUI)
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',

        # Core modules
        'core',
        'core.processor',
        'core.video_analyzer',
        'core.vapoursynth_engine',
        'core.ffmpeg_encoder',
        'core.propainter_engine',

        # Capture modules (v4.0 - Real Hardware Support)
        'capture',
        'capture.device_manager',
        'capture.analog_capture',
        'capture.dv_capture',

        # GUI modules
        'gui',
        'gui.main_window',
        'gui.processing_thread',
        'gui.settings_manager',
        'gui.splash_screen',
        'gui.preset_manager',

        # VapourSynth plugins (direct import)
        # Uses vsrealesrgan, vsbasicvsrpp, etc. via VapourSynth plugin system

        # YAML library (for config files)
        'yaml',

        # Other dependencies
        'json',
        'pathlib',
        'tempfile',
        'subprocess',
        're',
        'typing',
    ],
    hookspath=[],
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
    name='Advanced_Tape_Restorer_v4.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application (set to True for debugging)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if you have one
)
