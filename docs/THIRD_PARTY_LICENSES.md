# Third-Party Software Licenses and Acknowledgments

**Advanced Tape Restorer v2.0** is built upon many excellent open-source projects. This document provides required license acknowledgments and attribution for all third-party software used in or integrated with this application.

---

## Bundled Dependencies (Included in EXE)

### PySide6 (Qt for Python)
- **License:** LGPL v3 / Commercial
- **Version:** 6.10.0
- **Copyright:** The Qt Company Ltd.
- **Website:** https://www.qt.io/qt-for-python
- **Usage:** GUI framework (dynamically linked)
- **Compliance:** LGPL allows commercial use with dynamic linking
- **Source:** https://code.qt.io/cgit/pyside/pyside-setup.git/

**Attribution Required:** Yes
**License Text:** See [Qt LGPL License](https://www.gnu.org/licenses/lgpl-3.0.html)

---

### Python 3.13
- **License:** Python Software Foundation License (PSF)
- **Copyright:** Python Software Foundation
- **Website:** https://www.python.org/
- **Usage:** Runtime environment
- **Compliance:** PSF license is GPL-compatible and allows commercial use

**Attribution Required:** Yes
```
Copyright (c) 2001-2025 Python Software Foundation. All Rights Reserved.
```

---

## External Tools (User Must Install Separately)

### FFmpeg
- **License:** LGPL v2.1+ or GPL v2+ (depending on build configuration)
- **Copyright:** FFmpeg developers
- **Website:** https://ffmpeg.org/
- **Usage:** Video encoding/decoding (called as external executable)
- **Compliance:** Used as separate process, not linked
- **Required:** Yes (user installs)

**Attribution Required:** Yes
```
FFmpeg is a trademark of Fabrice Bellard
This application uses FFmpeg under LGPL v2.1+
```

**Note:** Application does NOT bundle FFmpeg. User must install separately from https://ffmpeg.org/

---

### VapourSynth
- **License:** LGPL v2.1+
- **Copyright:** Fredrik Mellbin and contributors
- **Website:** https://www.vapoursynth.com/
- **Usage:** Video filtering framework (external process via vspipe)
- **Compliance:** Called as external tool, not linked
- **Required:** Yes (user installs)

**Attribution Required:** Yes
```
VapourSynth Copyright (c) 2012-2024 Fredrik Mellbin
Licensed under LGPL v2.1+
```

---

## VapourSynth Plugins (User Installs via vsrepo)

### QTGMC (havsfunc)
- **License:** GPL v3
- **Author:** Didée, updated by Dogway and others
- **Repository:** https://github.com/HomeOfVapourSynthEvolution/havsfunc
- **Usage:** Deinterlacing algorithm
- **Compliance:** External plugin, not bundled

**Attribution Required:** Yes
```
QTGMC: High-quality deinterlacing
Copyright (c) Didée and contributors
GPL v3 License
```

---

### BM3D
- **License:** MIT
- **Author:** HolyWu
- **Repository:** https://github.com/HomeOfVapourSynthEvolution/VapourSynth-BM3D
- **Usage:** Video denoising
- **Compliance:** Permissive license allows commercial use

**Attribution Required:** Yes (courtesy)
```
VapourSynth-BM3D
Copyright (c) HolyWu
MIT License
```

---

### vs-rife (RIFE Frame Interpolation)
- **License:** MIT
- **Author:** HolyWu
- **Repository:** https://github.com/HolyWu/vs-rife
- **Original RIFE:** https://github.com/megvii-research/ECCV2022-RIFE
- **Usage:** AI frame interpolation
- **Compliance:** Permissive, allows commercial use

**Attribution Required:** Yes
```
vs-rife - VapourSynth plugin for RIFE
Copyright (c) HolyWu - MIT License

Based on RIFE (Real-Time Intermediate Flow Estimation)
Copyright (c) Megvii Inc.
```

---

### vs-realesrgan (RealESRGAN)
- **License:** BSD 3-Clause
- **Author:** HolyWu
- **Repository:** https://github.com/HolyWu/vs-realesrgan
- **Original:** https://github.com/xinntao/Real-ESRGAN
- **Usage:** AI super-resolution upscaling
- **Compliance:** Permissive, allows commercial use

**Attribution Required:** Yes
```
vs-realesrgan - VapourSynth plugin
Copyright (c) HolyWu - BSD 3-Clause License

Based on Real-ESRGAN
Copyright (c) Xintao Wang - BSD 3-Clause License
```

---

### FFMS2
- **License:** MIT
- **Author:** Fredrik Mellbin
- **Repository:** https://github.com/FFMS/ffms2
- **Usage:** Video source filter
- **Compliance:** Permissive, allows commercial use

**Attribution Required:** Yes (courtesy)
```
FFMS2 - FFmpegSource
Copyright (c) Fredrik Mellbin
MIT License
```

---

### L-SMASH-Works
- **License:** ISC (permissive)
- **Author:** Oka Motofumi (VFR maniac)
- **Repository:** https://github.com/AkarinVS/L-SMASH-Works
- **Usage:** Alternative video source filter
- **Compliance:** Permissive, allows commercial use

---

### f3kdb (Debanding)
- **License:** GPL v3
- **Author:** SAPikachu
- **Repository:** https://github.com/SAPikachu/flash3kyuu_deband
- **Usage:** Debanding filter
- **Compliance:** External plugin, not bundled

**Attribution Required:** Yes
```
flash3kyuu_deband (f3kdb)
Copyright (c) SAPikachu
GPL v3 License
```

---

### TComb / Bifrost
- **License:** GPL (VapourSynth ports)
- **Usage:** VHS artifact removal
- **Compliance:** External plugins, not bundled

---

## Python Packages (Bundled in EXE)

### Core Dependencies

#### psutil
- **License:** BSD 3-Clause
- **Copyright:** Giampaolo Rodola
- **Usage:** System monitoring, process management
- **Compliance:** Permissive, allows commercial use

#### pathlib
- **License:** PSF (part of Python standard library)
- **Usage:** Path manipulation
- **Compliance:** Python license allows commercial use

---

## DirectShow / Windows Media Foundation
- **License:** Windows SDK License
- **Copyright:** Microsoft Corporation
- **Usage:** Video capture from analog devices (Windows API)
- **Compliance:** Standard Windows API usage
- **Note:** No redistribution of Windows components

---

## GPL Compliance Statement

### How We Comply with GPL/LGPL Requirements

**GPL-licensed components** (QTGMC, f3kdb, etc.) are:
- ✅ **NOT bundled** in the executable
- ✅ **NOT statically linked**
- ✅ **Installed separately** by the user via vsrepo
- ✅ **Called as external processes** (VapourSynth plugins)
- ✅ **Properly attributed** in this document

**LGPL-licensed components** (FFmpeg, VapourSynth, PySide6):
- ✅ **Dynamically linked** or called as external processes
- ✅ **Not statically linked** (LGPL compliance)
- ✅ **Source code available** at official repositories
- ✅ **User can replace** with different versions
- ✅ **Proper attribution** provided

### GPL Separation Architecture

```
Advanced Tape Restorer EXE (Proprietary/Your License)
    │
    ├─→ Calls FFmpeg (external .exe) ─────→ LGPL v2.1+ ✅
    │   └─ subprocess.run(["ffmpeg", ...])
    │
    ├─→ Calls VapourSynth (external .exe) ─→ LGPL v2.1+ ✅
    │   └─ subprocess.run(["vspipe", ...])
    │       │
    │       ├─→ Loads QTGMC plugin ─────→ GPL v3 ✅
    │       ├─→ Loads f3kdb plugin ─────→ GPL v3 ✅
    │       └─→ Loads other plugins ───→ Various ✅
    │
    ├─→ Uses PySide6 (dynamic linking) ───→ LGPL v3 ✅
    │   └─ Import, not static compilation
    │
    └─→ Uses Python (runtime) ────────────→ PSF ✅
        └─ Interpreted, not compiled in
```

**Result:** No GPL "viral effect" on your application because:
1. GPL tools are separate executables (not linked)
2. LGPL tools are dynamically linked (allowed)
3. Clear process boundaries maintained
4. User installs GPL components separately

---

## Commercial Distribution Compliance

### ✅ You CAN Sell/Distribute This EXE Because:

1. **No GPL Code Bundled**
   - GPL plugins installed separately by user
   - Called via external process (VapourSynth)
   - No GPL code in your EXE binary

2. **LGPL Properly Handled**
   - PySide6: Dynamic import (not static linking)
   - FFmpeg: Separate executable
   - VapourSynth: Separate executable
   - User can replace LGPL components

3. **Permissive Licenses**
   - MIT, BSD, PSF licenses allow commercial use
   - Python, BM3D, RIFE, RealESRGAN: All permissive

4. **External Tool Integration**
   - ProPainter: Not bundled (user installs)
   - GPL plugins: User installs via vsrepo
   - Clear separation maintained

### License Obligations for Distribution:

✅ **Required:**
- Include this THIRD_PARTY_LICENSES.md file
- Display "About" dialog with attributions
- Provide links to source repositories
- Maintain copyright notices

✅ **Recommended:**
- Offer to help users install dependencies
- Provide documentation for setup
- Link to original project pages

❌ **NOT Required:**
- Provide source code for your application (unless you choose GPL)
- Bundle GPL/LGPL sources (they're separate tools)
- Open-source your proprietary code

---

## External AI Tools (Optional - User Installs)

### ProPainter Integration

**Advanced Tape Restorer v2.0** provides **integration support** for ProPainter, but does **NOT** include, bundle, or redistribute ProPainter or its components.

---

## Legal Separation

### What This Application Provides:
- ✅ **Integration interface** (API wrapper for external CLI tool)
- ✅ **Setup wizard** (guides user through manual installation)
- ✅ **Documentation** (instructions to obtain ProPainter)
- ✅ **Configuration storage** (saves user's installation path)

### What This Application Does NOT Provide:
- ❌ ProPainter source code
- ❌ ProPainter model weights
- ❌ ProPainter dependencies
- ❌ ProPainter installer/bundled package

---

## ProPainter License

**ProPainter** is developed by:
- **Authors:** Shangchen Zhou, Chongyi Li, Kelvin C.K. Chan, Chen Change Loy
- **Institution:** S-Lab, Nanyang Technological University
- **Repository:** https://github.com/sczhou/ProPainter
- **License:** NTU S-Lab License 1.0

### License Terms (Summary):

**ProPainter is licensed for NON-COMMERCIAL USE ONLY.**

#### You MAY:
- ✅ Use for personal, non-commercial video restoration
- ✅ Use for academic research
- ✅ Use for educational purposes
- ✅ Modify for non-commercial use
- ✅ Distribute modifications for non-commercial use (with attribution)

#### You MAY NOT:
- ❌ Use for commercial purposes
- ❌ Use in commercial products/services
- ❌ Charge fees for ProPainter-processed content
- ❌ Redistribute without proper attribution
- ❌ Remove copyright notices

#### Commercial Use Requires:
For commercial licensing, contact:
- **Dr. Shangchen Zhou:** shangchenzhou@gmail.com

### Full License:
https://github.com/sczhou/ProPainter/blob/main/LICENSE

---

## User Responsibilities

**By using ProPainter integration in this application, you acknowledge:**

1. **You will obtain ProPainter independently** from the official repository
2. **You will review and accept** the NTU S-Lab License 1.0 terms
3. **You will ensure your use complies** with the non-commercial license
4. **You understand** this application is a separate work that only provides integration
5. **You are responsible** for determining if your use case is non-commercial

---

## Application License vs. ProPainter License

### Advanced Tape Restorer v2.0:
- **License:** [Your Application License]
- **Scope:** Core application, GUI, VapourSynth integration, capture features
- **Usage:** [Your terms]

### ProPainter (External Tool):
- **License:** NTU S-Lab License 1.0 (Non-Commercial)
- **Scope:** ProPainter code, models, inference scripts
- **Usage:** Non-commercial only (obtain separately from official repo)

**These are separate software packages with separate licenses.**

---

## Integration Architecture

```
┌─────────────────────────────────────────────────┐
│ Advanced Tape Restorer v2.0                     │
│ (Your License)                                  │
│                                                 │
│  ┌──────────────────────────────────┐          │
│  │ ProPainter Integration Layer     │          │
│  │ (API Wrapper - Your Code)        │          │
│  │                                  │          │
│  │ • CLI command builder            │          │
│  │ • Path configuration             │          │
│  │ • Setup wizard                   │          │
│  └──────────────┬───────────────────┘          │
└─────────────────┼───────────────────────────────┘
                  │ subprocess.run()
                  │ (External call)
                  ▼
┌─────────────────────────────────────────────────┐
│ ProPainter (External Installation)              │
│ (NTU S-Lab License 1.0 - Non-Commercial)        │
│                                                 │
│ User obtained from:                             │
│ https://github.com/sczhou/ProPainter            │
│                                                 │
│ User accepted license terms independently       │
└─────────────────────────────────────────────────┘
```

**Clear Separation:** Your application calls ProPainter as an external tool, similar to how it calls FFmpeg or VapourSynth.

---

## Other AI Tools

### RIFE (VapourSynth Plugin)
- **License:** MIT License (permissive)
- **Repository:** https://github.com/HolyWu/vs-rife
- **Usage:** Can be freely used and redistributed
- **Installation:** User installs via `vsrepo install rife`

### RealESRGAN (VapourSynth Plugin)
- **License:** BSD 3-Clause License (permissive)
- **Repository:** https://github.com/HolyWu/vs-realesrgan
- **Usage:** Can be freely used and redistributed
- **Installation:** User installs via `vsrepo install realesrgan`

---

## Best Practices for Users

### Non-Commercial Use Examples:
✅ **Allowed:**
- Restoring family VHS tapes for personal archives
- Academic research on video restoration
- Student projects and learning
- Non-profit organization archival work
- Open-source project contributions

### Commercial Use Examples:
❌ **Requires License:**
- Professional video restoration services for clients
- Products/services that charge fees
- Commercial film/TV production work
- Business archival services
- Any revenue-generating activity

### When in Doubt:
- Contact ProPainter authors for clarification
- Err on the side of caution
- Consider commercial licensing if unclear

---

## Attribution Requirements

When publishing work that used ProPainter, cite:

```bibtex
@inproceedings{zhou2023propainter,
  title={{ProPainter}: Improving Propagation and Transformer for Video Inpainting},
  author={Zhou, Shangchen and Li, Chongyi and Chan, Kelvin C.K and Loy, Chen Change},
  booktitle={Proceedings of IEEE International Conference on Computer Vision (ICCV)},
  year={2023}
}
```

---

## Disclaimer

**IMPORTANT:** This document provides a summary and is not legal advice. Users must:

1. Read the complete NTU S-Lab License 1.0 at:
   https://github.com/sczhou/ProPainter/blob/main/LICENSE

2. Determine their own license compliance

3. Contact license holders for commercial use permissions

4. Understand that this application's developers are NOT responsible for user's ProPainter license compliance

**The integration provided in this application is for user convenience only.**

---

## Support & Questions

### About Advanced Tape Restorer Integration:
- Contact: [Your support channel]
- Issues: [Your issue tracker]

### About ProPainter License:
- Contact: shangchenzhou@gmail.com (ProPainter author)
- Issues: https://github.com/sczhou/ProPainter/issues

### Commercial ProPainter Licensing:
- Contact: Dr. Shangchen Zhou directly
- Email: shangchenzhou@gmail.com

---

## Complete Acknowledgments

**Advanced Tape Restorer v2.0** would not be possible without these excellent open-source projects:

### Core Technologies
- **Python** - Python Software Foundation
- **PySide6 / Qt** - The Qt Company
- **FFmpeg** - FFmpeg developers and Fabrice Bellard
- **VapourSynth** - Fredrik Mellbin and contributors

### Video Processing Plugins
- **QTGMC** - Didée, Dogway, and contributors
- **BM3D** - HolyWu
- **vs-rife (RIFE)** - HolyWu, based on work by Megvii Inc.
- **vs-realesrgan** - HolyWu, based on Real-ESRGAN by Xintao Wang
- **FFMS2** - Fredrik Mellbin
- **L-SMASH-Works** - Oka Motofumi
- **f3kdb** - SAPikachu
- **TComb/Bifrost** - Various contributors

### AI Research
- **RIFE** - Zhewei Huang, Tianyuan Zhang, Wen Heng, Boxin Shi, Shuchang Zhou (Megvii)
- **RealESRGAN** - Xintao Wang, Liangbin Xie, Chao Dong, Ying Shan (Tencent ARC Lab)
- **ProPainter** - Shangchen Zhou, Chongyi Li, Kelvin C.K. Chan, Chen Change Loy (NTU S-Lab)

### Development Tools
- **PyInstaller** - PyInstaller Development Team
- **Python Community** - Countless contributors worldwide

**Thank you to all open-source developers who make projects like this possible!** 🙏

---

## License Compliance Checklist for Distributors

If you are distributing this application, ensure:

- [ ] Include THIRD_PARTY_LICENSES.md in distribution
- [ ] Display attribution in "About" dialog
- [ ] Do not bundle GPL plugins (user installs separately)
- [ ] PySide6 dynamically linked (not static)
- [ ] FFmpeg/VapourSynth called as external tools
- [ ] Provide links to source repositories
- [ ] Maintain all copyright notices
- [ ] Document that ProPainter requires separate user installation
- [ ] Do not make false claims about GPL tool licensing

---

## Summary

✅ **Correct Integration Approach:**
- Application provides setup assistance only
- User obtains ProPainter independently
- User accepts license terms directly
- Clear separation of software packages
- User responsible for license compliance

❌ **What We DON'T Do:**
- Bundle/redistribute ProPainter
- Circumvent license restrictions
- Make licensing decisions for users
- Provide commercial permissions

✅ **Commercial Distribution OK Because:**
- No GPL code bundled in EXE
- LGPL components properly dynamic linked
- GPL tools installed separately by user
- All required attributions provided
- Clean architecture maintains license boundaries

**Result:** Clean, legal, ethical integration that respects all licenses and puts responsibility where it belongs: with the end user.

---

**Last Updated:** November 19, 2025  
**Document Version:** 1.0
