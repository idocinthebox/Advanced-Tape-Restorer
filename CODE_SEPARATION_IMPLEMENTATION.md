# Code Separation Implementation - Bulletproof Licensing

## Critical: Enforcing Dual License Architecture

To maintain legally defensible separation between MIT (v4.1) and proprietary (v4.2) components, we MUST implement strict code organization.

## Required Directory Structure

```
Advanced_Tape_Restorer/
│
├── core_mit/                    ← v4.1 MIT-licensed components
│   ├── LICENSE                  ← MIT License text
│   ├── core.py                  ← Core restoration engine
│   ├── capture.py               ← DirectShow capture
│   ├── video_analyzer.py        ← Field detection
│   ├── vapoursynth_engine.py    ← VapourSynth integration
│   ├── ffmpeg_encoder.py        ← FFmpeg pipeline
│   ├── multi_gpu_manager.py     ← GPU management
│   ├── torch_jit_optimizer.py   ← JIT compilation
│   ├── threaded_io.py           ← I/O operations
│   ├── checkpoint_processor.py  ← Checkpoint system
│   ├── onnx_converter.py        ← ONNX framework
│   ├── ai_models/               ← Basic AI integration
│   │   ├── realesrgan.py
│   │   ├── rife.py
│   │   ├── basicvsrpp.py
│   │   ├── swinir.py
│   │   ├── znedi3.py
│   │   ├── gfpgan.py
│   │   └── deoldify.py
│   └── gui/
│       ├── basic_ui.py          ← Basic PySide6 GUI
│       └── batch_processor.py   ← Simple batch queue
│
├── proprietary_v42/             ← v4.2 PROPRIETARY components
│   ├── LICENSE_PROPRIETARY.txt  ← Proprietary EULA
│   ├── audio_restoration/       ← Audio cleanup modules
│   │   ├── __init__.py
│   │   ├── denoise.py
│   │   ├── declicker.py
│   │   └── whisper_integration.py
│   ├── project_management/      ← Project/client tools
│   │   ├── __init__.py
│   │   ├── project_db.py
│   │   ├── client_manager.py
│   │   ├── invoicing.py
│   │   └── time_tracker.py
│   ├── frame_stabilization/     ← Stabilization algorithms
│   │   ├── __init__.py
│   │   └── motion_tracker.py
│   ├── scene_detection/         ← Scene detection
│   │   ├── __init__.py
│   │   └── detector.py
│   ├── advanced_ui/             ← Premium UI features
│   │   ├── __init__.py
│   │   ├── theme_manager.py
│   │   ├── dockable_panels.py
│   │   ├── split_screen.py
│   │   ├── waveform_display.py
│   │   └── timeline_scrubber.py
│   ├── cross_platform/          ← Linux/macOS ports
│   │   ├── linux_support.py
│   │   └── macos_support.py
│   ├── professional_ai/         ← Premium AI features
│   │   ├── propainter_bundled.py
│   │   ├── codeformer.py
│   │   └── premium_denoise.py
│   ├── enhanced_capture/        ← Advanced capture features
│   │   ├── live_preview.py
│   │   ├── vbi_decoder.py
│   │   └── timecode_parser.py
│   └── license_validation/      ← License checking
│       ├── __init__.py
│       └── validator.py
│
├── LICENSE                      ← MIT License (v4.1)
├── LICENSE_V4.2.txt             ← Full EULA (v4.2)
├── LICENSE_SUMMARY_FOR_BUYERS.md
├── LICENSING_GUIDE.md
├── README.md
└── main.py                      ← Entry point (imports from both)
```

## Source Code Headers

### MIT-Licensed Files (core_mit/)

Every file in `core_mit/` must contain:

```python
"""
Advanced Tape Restorer - Core Restoration Engine
Copyright (c) 2025 [Your Company Name, LLC]

This file is part of Advanced Tape Restorer v4.1 and is licensed under the MIT License.
See LICENSE file in the core_mit/ directory for full license text.

You may freely use, modify, and redistribute this file under MIT License terms.
"""
```

### Proprietary Files (proprietary_v42/)

Every file in `proprietary_v42/` must contain:

```python
"""
Advanced Tape Restorer v4.2 - Audio Restoration Module
Copyright (c) 2025 [Your Company Name, LLC]

This file is PROPRIETARY and requires a commercial license.
Unauthorized redistribution, reverse engineering, or use is strictly prohibited.

See LICENSE_V4.2.txt for full End User License Agreement.
"""
```

## Import Rules

### main.py Entry Point

```python
"""
Advanced Tape Restorer v4.2
Dual License: MIT (v4.1 components) + Proprietary (v4.2 features)
"""

import sys
import os

# Import MIT-licensed core functionality
from core_mit.core import VideoProcessor
from core_mit.capture import CaptureDeviceManager
from core_mit.gui.basic_ui import BasicMainWindow

# Import proprietary features (requires license validation)
try:
    from proprietary_v42.license_validation import validate_license
    
    if validate_license():
        from proprietary_v42.audio_restoration import AudioRestorer
        from proprietary_v42.project_management import ProjectManager
        from proprietary_v42.advanced_ui import AdvancedMainWindow
        PROPRIETARY_FEATURES_ENABLED = True
    else:
        print("No valid v4.2 license found. Using v4.1 MIT features only.")
        PROPRIETARY_FEATURES_ENABLED = False
except ImportError:
    # Running v4.1 only (MIT components)
    PROPRIETARY_FEATURES_ENABLED = False

if __name__ == "__main__":
    if PROPRIETARY_FEATURES_ENABLED:
        app = AdvancedMainWindow()  # v4.2 proprietary UI
    else:
        app = BasicMainWindow()     # v4.1 MIT UI
    
    sys.exit(app.exec())
```

## License Validation (Proprietary)

### proprietary_v42/license_validation/validator.py

```python
"""
Advanced Tape Restorer v4.2 - License Validator
Copyright (c) 2025 [Your Company Name, LLC]
PROPRIETARY - Do not redistribute
"""

import hashlib
import os
from pathlib import Path

def validate_license() -> bool:
    """
    Validates v4.2 commercial license.
    
    Returns:
        True if valid license found, False otherwise
    """
    license_file = Path.home() / ".advanced_tape_restorer" / "license.key"
    
    if not license_file.exists():
        return False
    
    try:
        with open(license_file, 'r') as f:
            license_key = f.read().strip()
        
        # Validate license key (implement your validation logic)
        # This could check against a signature, online activation, etc.
        if is_valid_key(license_key):
            return True
    except Exception:
        pass
    
    return False

def is_valid_key(key: str) -> bool:
    """
    Validates license key format and signature.
    Implement your license validation logic here.
    """
    # Example: Check key format, signature, expiration
    # In production: Use cryptographic verification
    if len(key) < 20:
        return False
    
    # Add your validation logic
    return True  # Placeholder
```

## Build Process Separation

### For GitHub Release (MIT v4.1 Only)

```bash
# Build v4.1 MIT version for GitHub
git clone https://github.com/yourusername/advanced-tape-restorer.git
cd advanced-tape-restorer

# Only include core_mit/
rm -rf proprietary_v42/
pyinstaller main_v41.spec  # Spec file configured for MIT only

# Result: MIT-licensed open source build
```

### For Commercial Release (v4.2 with Proprietary)

```bash
# Build v4.2 commercial version (private)
cd advanced-tape-restorer-commercial/

# Include both core_mit/ and proprietary_v42/
pyinstaller main_v42.spec  # Spec file includes license validation

# Bundle installer with clickwrap EULA
makensis installer_v42.nsi

# Result: Commercial build with license key requirement
```

## PyInstaller Spec Files

### main_v41.spec (MIT Only)

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_v41.py'],
    pathex=['core_mit'],  # Only MIT components
    binaries=[],
    datas=[
        ('core_mit/LICENSE', 'core_mit'),
    ],
    hiddenimports=[],
    # ... rest of spec
)
```

### main_v42.spec (Commercial)

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_v42.py'],
    pathex=['core_mit', 'proprietary_v42'],  # Both MIT and proprietary
    binaries=[],
    datas=[
        ('core_mit/LICENSE', 'core_mit'),
        ('LICENSE_V4.2.txt', '.'),
        ('LICENSE_SUMMARY_FOR_BUYERS.md', '.'),
    ],
    hiddenimports=[
        'proprietary_v42.license_validation',
        'proprietary_v42.audio_restoration',
        # ... all proprietary modules
    ],
    # ... rest of spec
)
```

## Clickwrap EULA Implementation

### Installer (NSIS Example)

```nsis
; Advanced Tape Restorer v4.2 Installer
!include "MUI2.nsh"

Name "Advanced Tape Restorer v4.2"
OutFile "Advanced_Tape_Restorer_v4.2_Setup.exe"

; License page (clickwrap)
!insertmacro MUI_PAGE_LICENSE "LICENSE_V4.2.txt"

; User MUST click "I Agree" to continue
LicenseData "LICENSE_V4.2.txt"
LicenseForceSelection checkbox "I accept the terms of the EULA"

; Installation directory
!insertmacro MUI_PAGE_DIRECTORY

; License key entry
Page custom LicenseKeyPage LicenseKeyLeave
Function LicenseKeyPage
  ; Show license key input dialog
  nsDialogs::Create 1018
  ${NSD_CreateLabel} 0 0 100% 12u "Enter your license key:"
  ${NSD_CreateText} 0 13u 100% 12u ""
  Pop $LicenseKeyInput
  nsDialogs::Show
FunctionEnd

Function LicenseKeyLeave
  ; Validate license key before installation
  ${NSD_GetText} $LicenseKeyInput $LicenseKey
  ; Call validation function
  ; Abort if invalid
FunctionEnd

; Install files
!insertmacro MUI_PAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"
```

## Testing License Separation

### Test Checklist

- [ ] v4.1 build runs without proprietary components
- [ ] v4.2 build requires valid license key
- [ ] Invalid license key blocks proprietary features
- [ ] MIT components usable in both builds
- [ ] Source headers correct in all files
- [ ] LICENSE files in correct directories
- [ ] No proprietary code in core_mit/
- [ ] No MIT code unnecessarily duplicated in proprietary_v42/
- [ ] Clickwrap EULA shown in installer
- [ ] License validation prevents binary redistribution

## Legal Compliance Notes

1. **Source Separation**: Physically separate directories prevent accidental MIT licensing of proprietary code
2. **License Headers**: Every file explicitly states its license
3. **License Files**: Separate LICENSE files in each directory
4. **Build Separation**: Different build scripts for MIT vs commercial
5. **Clickwrap**: Installer forces EULA acceptance before installation
6. **Key Validation**: Runtime check prevents unauthorized use

## Migration Path

### Current State → Separated Structure

1. Create `core_mit/` and `proprietary_v42/` directories
2. Move existing v4.1 files to `core_mit/`
3. Add MIT license headers to all `core_mit/` files
4. Develop new v4.2 features in `proprietary_v42/`
5. Add proprietary headers to all `proprietary_v42/` files
6. Implement license validation system
7. Update build scripts for separation
8. Create clickwrap installer
9. Test both MIT and commercial builds
10. Document separation in LICENSING_GUIDE.md

---

**Critical Reminder:** This separation is ESSENTIAL for legal defensibility and investor confidence. Without it, the dual licensing model is unenforceable.

**Last Updated:** December 29, 2025
