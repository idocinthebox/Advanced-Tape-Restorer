# Advanced Tape Restorer v3.2 - Changelog

**Release Date:** December 22, 2025  
**Focus:** Fix VapourSynth AI plugin integration for virgin installs

---

## 🎯 Critical Fix: Direct VapourSynth Plugin Usage

### The Problem (v3.0 & v3.1)
- Generated VapourSynth scripts imported custom Python packages (`ai_models.model_manager`)
- These packages only existed on development systems
- Virgin installs failed with cascade of missing module errors:
  - `ModuleNotFoundError: No module named 'ai_models'`
  - `ModuleNotFoundError: No module named 'PyYAML'`
  - `ModuleNotFoundError: No module named 'requests'`
  - Users pip installing these only led to more errors
  - **vsrealesrgan is NOT a pip package** - it's a VapourSynth plugin!

### The Solution (v3.2)
- **Direct VapourSynth plugin usage** - no Python package imports
- Scripts now use plugins directly:
  - `from vsrealesrgan import realesrgan, RealESRGANModel`
  - `from vsbasicvsrpp import BasicVSRPP`
  - `from vsswinir import SwinIR`
- **Zero Python dependencies** for AI upscaling
- Models auto-download via plugins (no Model Manager needed)

---

## 📋 Changes by Component

### Core Engine (`core/vapoursynth_engine.py`)

#### Modified:
- **`_generate_ai_upscaling()` method** - Complete rewrite
  - Removed all `ai_models` package imports
  - Removed Model Manager initialization
  - Direct plugin imports: `vsrealesrgan`, `vsbasicvsrpp`, `vsswinir`
  - Simplified model selection (plugin handles models internally)
  - Better error messages for missing plugins with installation instructions

#### Key Code Changes:
```python
# OLD (v3.0/v3.1) - Required Python packages:
from ai_models.model_manager import ModelManager
from ai_models.engines.upscaling_realesrgan import apply as realesrgan_apply
manager = ModelManager(...)
video = realesrgan_apply(video, **engine_args)

# NEW (v3.2) - Direct plugin usage:
from vsrealesrgan import realesrgan, RealESRGANModel
video = realesrgan(
    video,
    model=RealESRGANModel.realesr_general_x4v3,
    auto_download=True,  # Models download automatically
    device_index=0
)
```

### Error Messages

#### Improved:
- **ImportError handling** - Distinguishes between missing plugin vs other errors
- **Installation instructions** - Shows exact vsrepo commands:
  ```
  py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install realesrgan
  ```
- **Removed misleading PyTorch hints** - No longer suggests pip installing PyTorch (plugins have bundled PyTorch)

### Documentation

#### New Files:
- `REALESRGAN_DEPENDENCY_CLARIFICATION.md` - Explains two separate systems (VapourSynth plugins vs standalone PyTorch)
- `TEST_SYSTEM_REQUIREMENTS.md` - What's actually needed on virgin installs
- `DISTRIBUTION/Setup/Diagnose_Test_System.bat` - Diagnostic script for troubleshooting

#### Updated:
- `.github/copilot-instructions.md` - Updated architecture details for v3.2
- `DISTRIBUTION/Setup/Install_PyTorch_CUDA.bat` - Better warnings that this is optional

---

## 🔧 Technical Details

### VapourSynth Script Generation

**Before (v3.0/v3.1):**
```python
# Generated .vpy script tried to import project packages
import sys
from pathlib import Path
sys.path.insert(0, str(project_root))
from ai_models.model_manager import ModelManager  # ❌ Fails on virgin install!
```

**After (v3.2):**
```python
# Generated .vpy script uses plugins directly
from vsrealesrgan import realesrgan, RealESRGANModel  # ✅ Works if plugin installed!
video = realesrgan(video, model=..., auto_download=True)
```

### Dependencies on Virgin Installs

**What's Required:**
1. FFmpeg (encoding/decoding)
2. VapourSynth R73 (processing framework)
3. Python 3.12 (to run vsrepo.py only)
4. VapourSynth plugins via vsrepo:
   - `vsutil`, `havsfunc`, `ffms2`, `mvtools` (core)
   - `realesrgan` (for RealESRGAN upscaling)
   - `basicvsrpp`, `swinir`, `znedi3` (optional AI engines)

**What's NOT Required:**
- ❌ PyTorch installation (bundled in plugins)
- ❌ Python packages (PyYAML, requests, etc.)
- ❌ Project's `ai_models` package
- ❌ Model Manager system
- ❌ `Install_PyTorch_CUDA.bat` (only for external tools like ProPainter)

### Model Auto-Download

**v3.0/v3.1:** Model Manager handled downloads (required Python packages)  
**v3.2:** VapourSynth plugins handle downloads (no dependencies)

Example - RealESRGAN models:
- First run: Plugin downloads `realesr-general-x4v3.pth` (~17MB)
- Cached: `%APPDATA%\VapourSynth\models\realesrgan\`
- No Python packages needed!

---

## 🧪 Testing on Virgin Install

### Test Workflow:
1. Fresh Windows 10/11 system (no Python/VapourSynth)
2. Run: `DISTRIBUTION\Setup\Install_Prerequisites_Auto.bat`
3. Run: `DISTRIBUTION\Setup\Install_VapourSynth_Plugins.bat`
4. Launch: `Advanced_Tape_Restorer_v3.2.exe`
5. Enable AI upscaling (RealESRGAN 4x)
6. Process test video
7. **Expected:** Models auto-download, processing works
8. **Previous (v3.1):** Cascade of module errors

### Diagnostic Tool:
```bat
DISTRIBUTION\Setup\Diagnose_Test_System.bat
```
Shows:
- What's installed (FFmpeg, VapourSynth, Python)
- Which plugins are available
- Missing dependencies
- Installation instructions

---

## 🚀 Upgrade Path

### From v3.0 or v3.1:
1. **Replace executable** with v3.2.0
2. **No changes needed** - settings/presets compatible
3. **Benefit:** Cleaner VapourSynth scripts, better error messages
4. **Note:** Old generated `.vpy` scripts won't work (new ones are simpler)

### For New Installs:
1. Install prerequisites (FFmpeg, VapourSynth R73, Python 3.12)
2. Install VapourSynth plugins via vsrepo
3. Run app - AI features work immediately!

---

## 🐛 Known Issues

### Resolved in v3.2:
- ✅ Module cascade errors on virgin installs
- ✅ Misleading PyTorch installation hints
- ✅ Dependency on project's `ai_models` package
- ✅ Model Manager complexity for simple plugin usage

### Still Present:
- Capture module is mock implementation (no real hardware support)
- ProPainter requires separate installation (external tool)
- Some AI models require 12GB+ VRAM

---

## 📊 v3.0 vs v3.1 vs v3.2 Comparison

| Feature | v3.0 | v3.1 | v3.2 |
|---------|------|------|------|
| AI Model Manager | ✅ | ✅ | 🔄 Bypassed |
| Direct Plugin Usage | ❌ | ❌ | ✅ |
| Virgin Install Works | ❌ | ❌ | ✅ |
| Python Dependencies | Many | Many | None (for plugins) |
| Error Messages | Generic | Generic | Specific |
| Model Auto-Download | Via Manager | Via Manager | Via Plugin |

---

## 💡 Architecture Philosophy Change

**v3.0/v3.1 Philosophy:**
- Build comprehensive Model Manager system
- Abstract plugin differences
- Centralized model downloads
- **Problem:** Too complex for VapourSynth script context

**v3.2 Philosophy:**
- Use plugins as intended (direct imports)
- Let plugins handle their own models
- Minimal abstraction layer
- **Benefit:** Works out-of-box on virgin installs

---

## 🎓 Lessons Learned

1. **VapourSynth runs in isolated Python process** - can't import project packages
2. **vsrealesrgan is a plugin, not a pip package** - install via vsrepo
3. **Plugins have bundled PyTorch** - no separate installation needed
4. **Simpler is better** - direct plugin usage beats abstraction layers
5. **Test on virgin systems** - development system hides dependency issues

---

## 🔮 Future Plans

### v3.3 (Planned):
- Stabilization improvements (better auto-detect)
- GUI refinements based on user feedback
- Batch processing queue enhancements
- Better progress reporting for long encodes

### v4.0 (Roadmap):
- Real capture hardware support (analog/DV)
- Live preview window
- Hardware encoder support (NVENC, QuickSync)
- Plugin marketplace integration

---

## 📝 Migration Notes for Developers

### If you're modifying v3.2:

**DO:**
- ✅ Use direct VapourSynth plugin imports in generated scripts
- ✅ Let plugins handle model downloads
- ✅ Provide installation instructions in error messages
- ✅ Test on virgin install systems

**DON'T:**
- ❌ Import project packages in VapourSynth scripts
- ❌ Suggest pip installing plugins (use vsrepo)
- ❌ Assume Python packages are available
- ❌ Over-abstract simple plugin calls

---

**Version:** 3.2.0  
**Build Date:** December 22, 2025  
**Critical Fix:** Direct VapourSynth plugin usage for virgin installs  
**Compatibility:** Settings/presets from v3.0/v3.1 work without changes
