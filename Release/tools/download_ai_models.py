r"""
Release helper: download_ai_models.py (v3.0)

Standalone script to download AI model weights to the default application model
folder (%LOCALAPPDATA%\Advanced_Tape_Restorer\ai_models on Windows).

Usage examples:
    python download_ai_models.py --models realesrgan rife --yes
    python download_ai_models.py --models realesrgan --url <direct-url> --yes

v3.0 Changes:
- RealESRGAN now includes built-in face enhancement (replaces GFPGAN)
- Auto-downloaded by vsrealesrgan plugin when first used
- AI models download automatically when needed in the GUI

The script will prompt for license acceptance unless `--yes` is passed.
"""

from __future__ import annotations

import argparse
import os
import sys
import hashlib
import urllib.request
import shutil
from pathlib import Path

APP_NAME = "Advanced_Tape_Restorer"
DEFAULT_SUBDIR = Path("ai_models")

MODEL_REGISTRY = {
    "realesrgan": {
        "filename": "RealESRGAN_x4plus.pth",
        # Canonical Real-ESRGAN model release (video/general x4 variant)
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
        "sha256": None,
        "size_mb": 50,
    },
    "rife": {
        "filename": "rife_model.pth",
        # Official RIFE repo points to Google Drive assets; using the public Drive link
        "url": "https://drive.google.com/file/d/1h42aGYPNJn2q8j_GVkS_yDu__G_UZ2GX/view?usp=sharing",
        # Add SHA256 once verified to enable checksum verification
        "sha256": None,
        "size_mb": 200,
    },
}


def get_storage_dir() -> Path:
    if sys.platform.startswith("win"):
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    else:
        base = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = Path(base) / APP_NAME / DEFAULT_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def verify_sha256(file_path: Path, expected: str | None) -> bool:
    if not expected:
        return True
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest() == expected.lower()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    # Detect Google Drive share URLs and handle confirmation tokens

    def _extract_gdrive_id(u: str) -> str | None:
        import re

        m = re.search(r"/d/([A-Za-z0-9_-]{10,})", u)
        if m:
            return m.group(1)
        m = re.search(r"[?&]id=([A-Za-z0-9_-]{10,})", u)
        if m:
            return m.group(1)
        return None

    def _download_from_gdrive(file_id: str, dest_path: Path) -> None:
        import http.cookiejar
        import re

        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        base = f"https://docs.google.com/uc?export=download&id={file_id}"
        resp = opener.open(base)
        content = resp.read()
        cd = resp.headers.get("Content-Disposition")
        if cd and b"filename" in content[:512]:
            with open(dest_path, "wb") as f:
                f.write(content)
            return
        text = content.decode("utf-8", errors="ignore")
        m = re.search(r"confirm=([0-9A-Za-z_-]+)", text)
        token = m.group(1) if m else None
        if not token:
            for cookie in cj:
                if "download_warning" in cookie.name:
                    token = cookie.value
                    break
        if not token:
            raise OSError("Could not obtain Google Drive confirmation token")
        download_url_confirm = base + "&confirm=" + token
        with opener.open(download_url_confirm) as r2:
            with open(dest_path, "wb") as out:
                shutil.copyfileobj(r2, out)

    try:
        print(f"Downloading {dest.name} from {url}")
        gd = _extract_gdrive_id(url)
        if gd:
            _download_from_gdrive(gd, tmp)
        else:
            urllib.request.urlretrieve(url, filename=str(tmp))
        tmp.replace(dest)
        print(f"Saved to {dest}")
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Download AI model weights for Advanced Tape Restorer"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="Model keys to download (realesrgan, rife)",
    )
    parser.add_argument(
        "--dest", help="Destination root folder (default: app local data)"
    )
    parser.add_argument("--url", help="Optional URL override for the first model")
    parser.add_argument(
        "--sha256",
        nargs="*",
        help="Optional SHA256 checksums to verify downloaded models. Provide one per model or a single checksum for the first model.",
    )
    parser.add_argument(
        "--yes", action="store_true", help="Accept licenses and do not prompt"
    )
    args = parser.parse_args(argv)

    dest_root = Path(args.dest) if args.dest else get_storage_dir()

    # License text
    license_text = (
        "By downloading these model weights you acknowledge you have read and accepted"
        " the models' license terms. Some weights are large and may be hosted externally."
    )

    if not args.yes:
        print("WARNING: Model weights may be large and have separate licenses.")
        print(license_text)
        ok = input("Do you accept these terms and want to continue? (y/N): ")
        if ok.strip().lower() != "y":
            print("Aborted by user.")
            sys.exit(1)

    sha_list = args.sha256 or []

    for i, key in enumerate(args.models):
        key = key.lower()
        if key not in MODEL_REGISTRY:
            print(f"Unknown model key: {key}")
            continue
        entry = MODEL_REGISTRY[key]
        filename = entry["filename"]
        url = args.url if (i == 0 and args.url) else entry.get("url")
        # Allow user-supplied sha256: either one per model or a single value for first model
        user_sha = None
        if len(sha_list) == len(args.models):
            user_sha = sha_list[i]
        elif len(sha_list) == 1:
            user_sha = sha_list[0]
        else:
            user_sha = None
        model_dir = dest_root / key
        model_path = model_dir / filename
        if model_path.exists():
            print(f"Model '{key}' already exists at {model_path}")
            continue
        if not url:
            print(f"No known download URL for model '{key}'.")
            print(
                "Please provide a direct download URL with --url or consult the docs:"
            )
            print("https://github.com/xinntao/Real-ESRGAN (RealESRGAN)")
            print("https://github.com/hzwer/ (RIFE-related resources)")
            continue
        try:
            download(url, model_path)
            # If user provided a checksum, verify it; otherwise skip verification
            if user_sha:
                ok = verify_sha256(model_path, user_sha)
                if not ok:
                    print(f"Checksum mismatch for {model_path}; removing file")
                    model_path.unlink(missing_ok=True)
                    continue
        except Exception as e:
            print(f"Failed to download {key}: {e}")
            continue

    print("All requested models processed.")


if __name__ == "__main__":
    main()
