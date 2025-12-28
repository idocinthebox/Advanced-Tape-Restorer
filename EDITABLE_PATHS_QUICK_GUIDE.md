# Editable File Paths - Quick Guide

## Before and After

### ❌ Before (v3.2 and earlier)
```
┌─────────────────────────────────────────────────┐
│ Input File:  [No file selected       ] [Browse]│
│ Output File: [No file selected       ] [Browse]│
└─────────────────────────────────────────────────┘
```
- **Read-only labels** - Could only click Browse
- No way to paste or type paths
- Had to navigate through folders every time

### ✅ After (v3.3)
```
┌────────────────────────────────────────────────────────┐
│ Input File:  [Type or paste file path...     ] [Browse]│
│              ↑ Click here to type or paste!             │
│                                                         │
│ Output File: [Type or paste output path...   ] [Browse]│
│              ↑ Editable too!                            │
└────────────────────────────────────────────────────────┘
```
- **Editable text fields** - Type, paste, or browse
- Real-time validation with color feedback
- Automatic quote removal from pasted paths

---

## How to Use

### Method 1: Type Manually
```
1. Click in the Input File field
2. Type: C:\Videos\my_tape.avi
3. Field turns green ✅ if file exists
4. Press Tab to move to output field
```

### Method 2: Copy/Paste from Explorer
```
1. In File Explorer: Right-click file → "Copy as path"
2. Click in the Input File field
3. Press Ctrl+V
4. Quotes automatically removed
5. Path validated instantly
```

### Method 3: Edit Existing Path
```
1. Use Browse to select: C:\Videos\tape_01.avi
2. Click in the field
3. Change to: C:\Videos\tape_02.avi
4. No need to browse again!
```

### Method 4: Browse (Still Works!)
```
1. Click [Browse...] button
2. Select file as usual
3. Path appears in editable field
4. Can still edit after browsing
```

---

## Color Guide

### 🟢 Green Background
```
┌─────────────────────────────────────────┐
│ C:\Videos\my_tape.avi                   │ ← GREEN = Valid ✅
└─────────────────────────────────────────┘
```
**Meaning:** File exists / Directory is valid

### 🟠 Orange Background  
```
┌─────────────────────────────────────────┐
│ C:\Videos\missing_file.avi              │ ← ORANGE = Warning ⚠️
└─────────────────────────────────────────┘
```
**Meaning:** File not found / Directory doesn't exist

### ⚪ White Background
```
┌─────────────────────────────────────────┐
│                                         │ ← WHITE = Empty/Default
└─────────────────────────────────────────┘
```
**Meaning:** No path entered yet

---

## Tips & Tricks

### ✅ Fast Workflow
```
1. Paste input path (Ctrl+V)
2. Wait for green validation
3. Tab to output field
4. Type output name
5. Start processing
```

### ✅ Batch Processing
```
Prepare list of paths:
C:\Tapes\VHS_001.avi
C:\Tapes\VHS_002.avi
C:\Tapes\VHS_003.avi

Copy/paste each one
↓
Much faster than browsing!
```

### ✅ Network Paths
```
Can type UNC paths directly:
\\server\Videos\tape.avi
\\NAS\media\vhs_collection\tape01.mp4
```

### ✅ Fix Typos Quickly
```
Wrong:  C:\Vidoes\tape.avi  ← Orange (typo!)
Fixed:  C:\Videos\tape.avi  ← Green ✅
```

---

## Common Issues

### Q: Field is orange but file exists?
**A:** Check for:
- Trailing spaces
- Invisible characters
- Use "Copy as path" from Explorer

### Q: Can't paste path?
**A:** Make sure:
- Field has focus (click it first)
- Use Ctrl+V (not right-click paste)
- Path is in clipboard

### Q: Path with spaces not working?
**A:** No problem! Paths with spaces work fine:
```
✅ C:\My Videos\old tape.avi
✅ C:\Users\John Smith\Documents\file.mp4
```

### Q: Want to clear the field?
**A:** Select all (Ctrl+A) and press Delete

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+V** | Paste path |
| **Ctrl+A** | Select all text |
| **Ctrl+C** | Copy current path |
| **Tab** | Move to next field |
| **Shift+Tab** | Move to previous field |
| **Esc** | Cancel edit (reverts) |

---

## What Changed in the Code

**File:** `gui/main_window.py`

**Old (v3.2):**
```python
self.input_label = QLabel("No file selected")
self.output_label = QLabel("No file selected")
# Labels were read-only displays
```

**New (v3.3):**
```python
self.input_line_edit = QLineEdit()
self.output_line_edit = QLineEdit()
# Now editable text fields with validation!
```

**Added Features:**
- `_on_input_path_changed()` - Validates as you type
- `_on_output_path_changed()` - Checks directory exists
- Quote removal for pasted paths
- Color-coded feedback
- Smarter Browse dialogs

---

## Benefits

### ⚡ Speed
- No more browsing through folders
- Paste paths instantly
- Edit paths in-place

### 🎯 Accuracy
- Visual feedback = fewer mistakes
- See full path at all times
- Easy to spot typos

### 💪 Power User
- Network paths supported
- Long paths work fine
- Copy/paste friendly

### 🔄 Compatibility
- Browse buttons still work
- Old presets compatible
- No breaking changes

---

**Enjoy the new editable file path fields!** 🎉

