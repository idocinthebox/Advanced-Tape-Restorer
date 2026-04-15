# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Advanced Tape Restorer v4.0 (Community Edition)
FREE version without AI features - MIT Licensed
Build: pyinstaller --noconfirm --clean main_v4.0.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Determine paths
SCRIPT_DIR = Path.cwd()

a = Analysis(
    ['main.py'],
    pathex=[str(SCRIPT_DIR)],
    binaries=[],
    datas=[
        # Core configuration files
        ('restoration_presets.json', '.'),
        ('restoration_settings.json', '.'),
        ('LICENSE', '.'),
        ('README.md', '.'),
        ('VERSION.txt', '.'),
        ('QUICK_START_GUIDE.md', '.'),
        
        # v4.0 MIT license documentation
        ('LICENSING_GUIDE.md', '.'),
        ('VERSION_FEATURE_MATRIX.md', '.'),
    ],
    hiddenimports=[
        # Core modules
        'core',
        'capture',
        'gui.main_window',
        'gui.settings_manager',
        'gui.processing_thread',
        
        # Multi-GPU and performance (non-AI)
        'core.multi_gpu_manager',
        'core.threaded_io',
        
        # PySide6 UI
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        
        # Standard libraries
        'json',
        'subprocess',
        'threading',
        'queue',
        'hashlib',
        're',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    
    # EXCLUDE AI components - this is the key difference from v4.1
    excludes=[
        'ai_models',                    # Entire AI models package
        'torch',                        # PyTorch (2.2GB saved!)
        'torchvision',
        'torchaudio',
        'onnx',                         # ONNX runtime
        'onnxruntime',
        'onnxruntime_directml',
        'core.ai_bridge',              # AI bridge module
        'core.onnx_converter',         # ONNX converter
        'core.torch_jit_optimizer',    # PyTorch JIT
        'convert_models_to_onnx',      # Model conversion script
        'demo_model',                   # Demo models
        
        # AI model engines
        'ai_models.engines',
        'ai_models.engines.realesrgan',
        'ai_models.engines.rife',
        'ai_models.engines.basicvsrpp',
        'ai_models.engines.swinir',
        'ai_models.engines.znedi3',
        'ai_models.engines.gfpgan',
        'ai_models.engines.deoldify',
        'ai_models.engines.propainter',
        'ai_models.model_manager',
        
        # AI dependencies we don't need
        'numpy',                        # Not needed for basic restoration
        'scipy',
        'opencv-python',
        'cv2',
        'PIL',
        'basicsr',
        'facexlib',
        'realesrgan',
        
        # Test modules
        'test_modules',
        'pytest',
        'unittest',
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
    name='Advanced_Tape_Restorer_v4.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                          # Enable UPX compression for smaller size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                     # Windowed application (no console)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                         # Add icon if available
)

print("""
================================================================================
Advanced Tape Restorer v4.0 (Community Edition) - Build Configuration
================================================================================

VERSION: v4.0 (FREE - MIT Licensed)

INCLUDED:
  ✅ Core restoration (QTGMC, denoise, color correction)
  ✅ Hardware capture (DirectShow, DV/FireWire)
  ✅ Multi-GPU support (NVIDIA + AMD + Intel)
  ✅ Hardware encoders (NVENC, AMF, Quick Sync)
  ✅ Threaded I/O and checkpoint/resume
  ✅ All output formats (ProRes, DNxHD, H.265, etc.)
  ✅ Basic GUI and batch processing

EXCLUDED (AI features - available in v4.1 paid version):
  ❌ RealESRGAN, RIFE, BasicVSR++, SwinIR, ZNEDI3
  ❌ GFPGAN, DeOldify, ProPainter
  ❌ ONNX/NPU acceleration
  ❌ PyTorch JIT compilation
  ❌ AI model management

EXPECTED SIZE: ~500MB (vs 3GB for v4.1 with AI)

LICENSE: MIT (v4.0 components only)

BUILD COMMAND:
  pyinstaller --noconfirm --clean main_v4.0.spec

OUTPUT:
  dist/Advanced_Tape_Restorer_v4.0.exe

================================================================================
""")
