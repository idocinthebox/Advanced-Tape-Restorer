# -*- mode: python ; coding: utf-8 -*-
# Advanced Tape Restorer v4.1 - PyInstaller Spec File
# MIT Licensed - GitHub Release Build
# This spec file only includes v4.1 MIT-licensed components

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

block_cipher = None

# Collect all ai_models data files
ai_models_datas = collect_data_files('ai_models')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('LICENSE', '.'),
        ('README.md', '.'),
        ('restoration_presets.json', '.'),
        ('restoration_settings.json', '.'),
        ('QUICK_START_GUIDE.md', '.'),
        ('CHANGELOG.txt', '.'),
        # AI models registry (MIT components only)
        ('ai_models/models/registry.yaml', 'ai_models/models'),
    ] + ai_models_datas,
    hiddenimports=[
        # Core modules
        'core',
        'capture',
        'gui.main_window',
        'gui.settings_manager',
        'gui.processing_thread',
        
        # AI models (v4.1 MIT licensed)
        'ai_models',
        'ai_models.model_manager',
        'ai_models.engines',
        'ai_models.engines.realesrgan',
        'ai_models.engines.rife',
        'ai_models.engines.basicvsrpp',
        'ai_models.engines.swinir',
        'ai_models.engines.znedi3',
        'ai_models.engines.gfpgan',
        'ai_models.engines.deoldify',
        
        # Core processing
        'core.video_processor',
        'core.vapoursynth_engine',
        'core.ffmpeg_encoder',
        'core.ai_bridge',
        'core.multi_gpu_manager',
        'core.torch_jit_optimizer',
        'core.threaded_io',
        'core.onnx_converter',
        'core.gfpgan_checkpoint_processor',
        
        # GUI modules
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        
        # PyTorch and ML
        'torch',
        'torch.nn',
        'torchvision',
        'onnx',
        'onnxruntime',
        
        # Utilities
        'yaml',
        'requests',
        'PIL',
        'numpy',
        'cv2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude proprietary v4.2 modules (these don't exist yet in v4.1)
        'proprietary_v42',
        'proprietary',
    ],
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
    name='Advanced_Tape_Restorer_v4.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,  # Optional icon
    version_file=None,
)
