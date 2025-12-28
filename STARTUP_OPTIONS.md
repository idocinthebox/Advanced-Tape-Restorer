# Advanced Tape Restorer v4.0 - Startup Options

## 🚀 Normal Use (Recommended)

```
Double-click: Clean_Start.bat
```

**What it does:**
1. Cleans cache automatically
2. Launches the app in background
3. You can close the command window
4. App keeps running independently

**Result:** App opens, no console window cluttering your screen ✨

---

## 🔧 Debug Mode (For Troubleshooting)

```
Double-click: Clean_Start_With_Console.bat
```

**What it does:**
1. Cleans cache automatically
2. Launches the app with console output visible
3. Shows all logs and error messages
4. **Keep the console window open** to see output

**Result:** App opens with console showing what it's doing 🛠️

**Use this when:**
- Something isn't working right
- You want to see what the app is doing
- Reporting bugs (copy console output)

---

## 🖥️ Create Desktop Shortcut

```
Double-click: Create_Desktop_Shortcut.bat
```

Creates a shortcut on your desktop so you can launch the app easily.

---

## ⚙️ Advanced Options

### Direct Python Launch (No cleanup)
```powershell
python main.py          # With console
pythonw main.py         # Without console
```

### Manual Cleanup + Start
```powershell
# Clear cache
Remove-Item -Recurse -Force __pycache__, gui\__pycache__, core\__pycache__

# Start app
pythonw main.py
```

---

## 🆘 Emergency Recovery

If app is completely stuck:

1. **Task Manager** (`Ctrl+Shift+Esc`)
2. Find `python.exe` or `pythonw.exe`
3. Right-click → End Task
4. Run `Emergency_Cleanup.ps1`
5. Run `Clean_Start.bat`

---

## 📁 File Reference

| File | What It Does |
|------|--------------|
| **Clean_Start.bat** | Normal startup (closes independently) |
| **Clean_Start_With_Console.bat** | Debug startup (shows output) |
| **Create_Desktop_Shortcut.bat** | Makes desktop icon |
| **Emergency_Cleanup.ps1** | Nuclear option - full cleanup |
| START_HERE.md | Quick reference guide |
| FIX_LOADING_SCREEN.md | Detailed troubleshooting |

---

## 💡 Pro Tips

- **First time?** Use `Clean_Start.bat`
- **Having issues?** Use `Clean_Start_With_Console.bat` to see what's wrong
- **Want desktop icon?** Run `Create_Desktop_Shortcut.bat` once
- **App won't close?** Task Manager → End `python.exe`

---

**Current Status:** ✅ All startup issues fixed - App works normally!

The app now:
- Starts fast (no hanging)
- Loads capture devices on-demand
- Runs independently of the launcher window
- Has proper cleanup on startup
