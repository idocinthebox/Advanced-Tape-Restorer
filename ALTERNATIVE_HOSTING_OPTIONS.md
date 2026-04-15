# File Too Large for GitHub (2.93GB > 2GB Limit)

## Option 1: Google Drive (Recommended)
**Best for: Free, reliable, no account required for downloaders**

1. Upload EXE to Google Drive
2. Right-click → Share → "Anyone with the link"
3. Copy shareable link
4. Update GitHub release notes with download link

**Pros:** Free, 15GB storage, fast, trusted
**Cons:** Users may need to click "Download anyway" (virus scan warning for large files)

---

## Option 2: OneDrive
**Best for: Microsoft users**

1. Upload to OneDrive
2. Right-click → Share → Create link
3. Post link in GitHub release

**Pros:** Free 5GB, integrated with Windows
**Cons:** Slower than Google Drive

---

## Option 3: Mega.nz
**Best for: Large file hosting specialists**

1. Create free account at https://mega.nz
2. Upload file (50GB free storage)
3. Generate share link
4. Post in GitHub release

**Pros:** 50GB free storage, fast downloads, privacy-focused
**Cons:** Requires account, less trusted than Google/Microsoft

---

## Option 4: SourceForge
**Best for: Traditional open-source distribution**

1. Create project at https://sourceforge.net
2. Upload to "Files" section
3. Link from GitHub

**Pros:** Designed for software releases, unlimited bandwidth
**Cons:** Ads on download page, setup required

---

## Option 5: Build Smaller EXE (Technical)
**Best for: Avoiding external hosting**

Create a build WITHOUT PyTorch embedded:

```powershell
# Update main_v4.1.spec to exclude PyTorch
# Users install PyTorch separately via pip
```

**Pros:** Fits on GitHub (<500MB)
**Cons:** Users must install PyTorch manually (more complex setup)

---

## Recommended Approach

**For v4.1 free version:**
1. Upload to **Google Drive** (easiest, most trusted)
2. Update GitHub release with:
   - Download link to Google Drive
   - SHA256 checksum in release notes
   - Instructions: "Download from Google Drive (GitHub 2GB limit)"

**For v4.2 commercial version:**
Use a paid platform designed for software sales:
- **Gumroad** - Handles hosting, payments, licensing
- **Sellfy** - Similar to Gumroad
- **Payhip** - Good for digital products
- Your own website + Stripe

---

## Quick Update for GitHub Release

Since the file is too large, update your release notes:

```markdown
## 📥 Downloads

### Standalone Executable (3.0 GB)
⚠️ **File too large for GitHub** (2GB limit)

**Download from Google Drive:**
[Advanced_Tape_Restorer_v4.1.exe](YOUR_GOOGLE_DRIVE_LINK_HERE)

**SHA256:** 4293E5B971278E968BD3322E66EC9364ED834105ED87A03D50F31628982FEA98

**Alternative:** Install from source (no large download):
```bash
git clone https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer
pip install -r requirements.txt
python main.py
```
```

---

## Why Is It So Large?

The EXE includes:
- Python 3.13 runtime (~50MB)
- **PyTorch 2.5** (~2.2GB) ← Main culprit
- ONNX Runtime (~200MB)
- NumPy, SciPy, OpenCV (~300MB)
- All other dependencies (~200MB)

**Total:** ~2.95GB

Users installing from source only download what they need (pip manages it).

---

## Next Steps

1. **Choose hosting** (Google Drive recommended)
2. **Upload EXE** to chosen platform
3. **Get shareable link**
4. **Update GitHub release notes** with download link
5. **Include SHA256 checksum** for verification
6. **Explain why external hosting** (GitHub 2GB limit)

This is common for large applications - even major projects use external hosting for binaries over 2GB.
