# NDA Enforcement Quick Reference

## Status: ✅ Fully Integrated & Tested

**Version:** v4.1  
**Date:** December 27, 2025  
**Test Results:** 5/5 tests passed

## Current Configuration

### Development Mode (Default)
```python
# main.py line 13
DEV_BYPASS_NDA = True  # NDA enforcement DISABLED for development
```

**When enabled (True):**
- Application starts immediately
- No NDA dialog shown
- No acceptance required
- Perfect for development/testing

### Production Mode (Tester Builds)
```python
# main.py line 13
DEV_BYPASS_NDA = False  # NDA enforcement ENABLED for testers
```

**When disabled (False):**
- Application checks for NDA acceptance on startup
- Shows NDA clickwrap dialog if not accepted
- Blocks access until NDA is accepted
- Records acceptance with timestamp, tester info, build ID

## Testing the NDA System

### 1. Quick Test (No GUI)
```bash
python test_nda_enforcement.py
```
Tests all NDA modules without showing dialogs.

### 2. Full Test (With GUI Dialog)
```bash
python test_nda_enforcement.py
# When prompted, type: y
```
Opens the actual NDA clickwrap dialog for visual inspection.

### 3. Test In Production Mode
```python
# 1. Edit main.py line 13:
DEV_BYPASS_NDA = False

# 2. Run application:
python main.py
```

Expected behavior:
- App starts
- NDA dialog appears (first run only)
- Shows NDA PDF with embedded viewer
- Requires name, email, and checkbox
- Records acceptance
- Subsequent runs bypass dialog (acceptance stored)

## NDA Storage Location

Acceptance records stored at:
```
Windows: C:\Users\<username>\AppData\Roaming\AdvancedTapeRestorer\nda\
Linux:   ~/.local/share/AdvancedTapeRestorer/nda/
```

Files created:
- `events.jsonl` - Append-only event log
- `latest_acceptance.json` - Current acceptance state
- `revocations/` - Breach/revocation records (if any)

## NDA Configuration

Located in `main.py` lines 175-177:

```python
BUILD_ID = f"beta-{__version__}+2025-12-27"      # Build identifier
NDA_VERSION = "NDA-HARDENED-2025-12-27"          # NDA version
NDA_PDF_PATH = Path(__file__).parent / "NDA" / "NDA_Hardened_Final_Tightened.pdf"
```

**Important:** Each unique combination of (BUILD_ID + NDA_VERSION + NDA_HASH) requires new acceptance.

## Tester Identification

Testers identified by:
1. `ATR_TESTER_ID` environment variable (if set)
2. Machine hostname (`platform.node()`)
3. Fallback: "UNKNOWN"

To set custom tester ID:
```bash
# Windows PowerShell
$env:ATR_TESTER_ID="TESTER_001"
python main.py

# Windows CMD
set ATR_TESTER_ID=TESTER_001
python main.py
```

## Common Workflows

### Development Workflow (Current State)
```
✓ DEV_BYPASS_NDA = True
✓ Run: python main.py
✓ App starts immediately, no NDA prompt
```

### Testing NDA Dialog
```
1. Set: DEV_BYPASS_NDA = False
2. Delete acceptance: rmdir /s C:\Users\<user>\AppData\Roaming\AdvancedTapeRestorer\nda
3. Run: python main.py
4. NDA dialog appears
5. Test acceptance flow
6. Set: DEV_BYPASS_NDA = True (return to dev mode)
```

### Building for Testers
```
1. Set: DEV_BYPASS_NDA = False
2. Verify NDA PDF is present: NDA\NDA_Hardened_Final_Tightened.pdf
3. Update BUILD_ID in main.py (e.g., "beta-4.1.0+2025-12-27")
4. Build: pyinstaller main.spec
5. Distribute: dist\Advanced_Tape_Restorer_v4.1.exe
```

## NDA Dialog Features

- **PDF Viewer:** Embedded NDA display (requires QtPdf)
- **External Open:** Button to open NDA in default PDF viewer
- **Required Fields:**
  - Tester name (2+ characters)
  - Tester email (valid format)
  - "I agree" checkbox
- **Copy Version:** Button to copy build/NDA info to clipboard
- **Acceptance Recording:** Saves to `%APPDATA%` with timestamp
- **Modal Dialog:** Must accept or decline before proceeding

## Troubleshooting

### "NDA Missing" Error
**Cause:** NDA PDF not found  
**Solution:** Ensure `NDA\NDA_Hardened_Final_Tightened.pdf` exists

### "NDA System Error - Module not found"
**Cause:** NDA enforcement package not in path  
**Solution:** Verify `NDA\nda_enforcement\` folder structure

### Dialog Shows Every Time
**Cause:** Acceptance not being saved  
**Solution:** Check write permissions to `%APPDATA%\AdvancedTapeRestorer\nda\`

### Want to Force Re-acceptance
**Solution:** Delete acceptance files:
```powershell
Remove-Item -Recurse "$env:APPDATA\AdvancedTapeRestorer\nda"
```

## Revocation System (Future Use)

If NDA breach detected, revoke access:

```python
from NDA.nda_enforcement.hooks import report_breach

report_breach(cfg, tester_id, detail="Leaked build screenshot on forum")
```

Revoked testers permanently blocked from using builds with same BUILD_ID.

## Files Overview

### NDA Folder Structure
```
NDA/
├── NDA_Hardened_Final_Tightened.pdf      # Legal NDA document
├── Tester_OnePage_Legal_Summary.pdf      # Quick reference for testers
├── README_NDA_Enforcement.md             # Technical documentation
├── example_integration.py                # Example CLI integration
├── demo_pyside6_clickwrap.py             # Standalone GUI demo
└── nda_enforcement/                      # Python package
    ├── __init__.py
    ├── config.py                         # Configuration dataclass
    ├── crypto.py                         # SHA256 helpers
    ├── hooks.py                          # on_app_start, report_breach
    ├── storage.py                        # File I/O for acceptance records
    ├── policy.py                         # Enforcement logic
    ├── models.py                         # Data models
    ├── acceptance_flow.py                # Acceptance recording
    └── pyside6_clickwrap.py             # Qt dialog (integrated)
```

### Integration Points

**main.py** (lines 1-13, 155-228):
- DEV_BYPASS_NDA flag
- NDA enforcement block
- Error handling

**test_nda_enforcement.py**:
- Automated test suite
- Verifies all modules work

## Next Steps

### Before Distributing to Testers:
1. ✅ Verify NDA PDF is present
2. ✅ Test NDA dialog appearance
3. ⚠️  **Set DEV_BYPASS_NDA = False**
4. ✅ Update BUILD_ID to release version
5. ✅ Build with PyInstaller
6. ✅ Test built EXE shows NDA on first run
7. ✅ Distribute to testers

---

**Integration Status:** ✅ Complete  
**Test Status:** ✅ All tests passing  
**Ready for Production:** ⚠️  Set DEV_BYPASS_NDA = False first
