# Editable File Path Fields - Feature Update

**Date:** December 24, 2025  
**Version:** Advanced Tape Restorer v3.3  
**Feature:** Manual file path editing

---

## What Changed

The input and output file selection fields have been upgraded from display-only labels to **fully editable text fields** that accept manually typed or pasted file paths.

---

## New Capabilities

### 1. ✅ Manual Path Entry
You can now type or paste file paths directly into the input/output fields without using the Browse button.

**Example:**
```
Input File:  C:\Videos\VHS_Tape_01.avi
Output File: D:\Restored\VHS_Tape_01_restored.mp4
```

### 2. ✅ Path Validation with Visual Feedback
The fields change color to indicate validity:

- **Green background** (`#e8f5e9`): Valid path
  - Input file exists on disk
  - Output directory exists
  
- **Orange background** (`#fff3e0`): Warning
  - Input file not found (may be typo)
  - Output directory doesn't exist
  
- **White background**: Empty field

### 3. ✅ Smart Quote Removal
Automatically removes quotes if you copy/paste paths from File Explorer:
- `"C:\My Videos\file.avi"` → `C:\My Videos\file.avi`
- `'C:\My Videos\file.avi'` → `C:\My Videos\file.avi`

### 4. ✅ Browse Dialog Improvements
- Browse dialogs now start in the current file's directory (if valid)
- Makes it easier to select related files or change output location

---

## Usage Examples

### Example 1: Type Path Directly
1. Click in the "Input File" field
2. Type: `C:\Users\YourName\Videos\old_tape.avi`
3. Field turns green if file exists
4. Press Tab or click outside to confirm

### Example 2: Paste from File Explorer
1. Right-click file in Windows Explorer → Copy as path
2. Click in "Input File" field
3. Press Ctrl+V
4. Quotes are automatically removed
5. Path is validated

### Example 3: Drag and Drop (Future Enhancement)
*Note: Drag and drop not yet implemented, but paths can be pasted*

### Example 4: Edit Existing Path
1. Use Browse to select a file
2. Click in the text field
3. Edit part of the path (e.g., change filename)
4. Watch color feedback for validation

---

## Field Behavior

### Input File Field
- **Placeholder:** "Type or paste file path, or click Browse..."
- **Validation:** Checks if file exists (`os.path.isfile()`)
- **Green:** File found on disk
- **Orange:** File not found (may need to browse or fix typo)

### Output File Field
- **Placeholder:** "Type or paste output path, or click Browse..."
- **Validation:** Checks if parent directory exists
- **Green:** Directory exists (file will be created there)
- **Orange:** Directory doesn't exist (will fail during processing)

---

## Technical Details

### Modified Code
**File:** `gui/main_window.py`

#### Changes Made:
1. Replaced `QLabel` widgets with `QLineEdit` for input/output paths
2. Added `textChanged` signal handlers:
   - `_on_input_path_changed()` - Validates input file
   - `_on_output_path_changed()` - Validates output directory
3. Updated `select_input()` and `select_output()` methods to:
   - Use current path as starting directory
   - Update `QLineEdit` text instead of `QLabel`
4. Added quote removal for pasted paths
5. Added visual feedback via background colors

### New Methods:
```python
def _on_input_path_changed(self, text: str):
    """Handle manual input path changes with validation."""
    # Strips whitespace, removes quotes, validates file existence
    # Sets background color: green (valid), orange (invalid)

def _on_output_path_changed(self, text: str):
    """Handle manual output path changes with validation."""
    # Strips whitespace, removes quotes, validates parent directory
    # Sets background color: green (valid), orange (invalid)
```

---

## Benefits

### For Users:
- ✅ **Faster workflow:** No need to browse for files you know the path to
- ✅ **Copy/paste friendly:** Paste paths from anywhere
- ✅ **Edit paths:** Fix typos or change filenames without re-browsing
- ✅ **Visual feedback:** Immediately see if path is valid

### For Power Users:
- ✅ **Batch scripting:** Can prepare file lists and paste paths
- ✅ **Network paths:** Type UNC paths like `\\server\share\video.avi`
- ✅ **Long paths:** Easier to see full path vs. truncated display

---

## Known Limitations

### Current Implementation:
- ⚠️ Drag and drop not yet supported (paste paths instead)
- ⚠️ Tab completion not available (use Browse or paste)
- ⚠️ No auto-complete suggestions based on recent files

### Future Enhancements (Ideas):
1. **Drag and drop support:** Drag file from Explorer → drop on field
2. **Recent paths dropdown:** Quick access to recently used files
3. **Path auto-completion:** Type partial path, press Tab for suggestions
4. **Browse button right-click menu:** "Open folder location" option

---

## Troubleshooting

### Issue: Field stays orange even though file exists

**Cause:** Path may have trailing spaces or special characters

**Solution:**
1. Copy the exact path from File Explorer (right-click → Copy as path)
2. Clear the field completely
3. Paste the path
4. System will auto-remove quotes and validate

### Issue: Can't type in the field

**Cause:** Field may be disabled during processing

**Solution:**
- Wait for processing to complete
- Fields are enabled when idle

### Issue: Pasted path has `%20` or other URL encoding

**Cause:** Pasted from browser or URL

**Solution:**
- Use Windows File Explorer to get path instead
- Or manually replace `%20` with spaces

---

## Backward Compatibility

✅ **Fully compatible** with existing workflows:
- Browse buttons work exactly as before
- Auto-suggest output filename still works
- Settings load/save unchanged
- Presets compatible

**No breaking changes** - this is purely an enhancement!

---

## Testing Checklist

### Basic Functionality:
- [x] Type valid input path → Field turns green
- [x] Type invalid input path → Field turns orange
- [x] Paste path with quotes → Quotes removed automatically
- [x] Use Browse button → Field updates with selected path
- [x] Edit path manually → Validation updates in real-time
- [x] Empty field → Returns to white background

### Edge Cases:
- [x] Path with spaces: `C:\My Videos\file.avi`
- [x] Network path: `\\server\share\video.avi` (if accessible)
- [x] Long path: Over 260 characters (Windows long path support)
- [x] Unicode characters: Non-English filenames

---

## User Feedback

If you encounter any issues with the new editable fields:
1. Check console log for validation messages
2. Verify path exists in File Explorer
3. Try using Browse button as fallback
4. Report any unexpected behavior

---

**Status:** ✅ Feature Complete and Tested  
**Impact:** Improved user experience, faster workflow  
**Breaking Changes:** None

