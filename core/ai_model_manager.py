r"""
AI Model Manager

Provides simple utilities to download, verify, and locate AI model weights used
by plugins (RealESRGAN, RIFE, etc.)

Default storage location (Windows): %LOCALAPPDATA%\Advanced_Tape_Restorer\ai_models
Cross-platform: use user's local data directory.

This module uses only the standard library so it can be imported in minimal envs.
"""

from __future__ import annotations

import hashlib
import os
import sys
import shutil
import urllib.request
from pathlib import Path
from typing import Callable

APP_NAME = "Advanced_Tape_Restorer"
DEFAULT_SUBDIR = Path("ai_models")

# Built-in model registry. URLs and checksums may change; these are defaults.
# If a model URL is not present or fails, the downloader will prompt the user
# to provide an alternate URL.
MODEL_REGISTRY: dict[str, dict[str, str | None]] = {
    "realesrgan": {
        "filename": "RealESRGAN_x4plus.pth",
        # Canonical release asset (Real-ESRGAN project)
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
        "sha256": None,
    },
    "rife": {
        "filename": "rife_model.pth",
        # Canonical RIFE model (official repo provides Google Drive assets)
        "url": "https://drive.google.com/file/d/1h42aGYPNJn2q8j_GVkS_yDu__G_UZ2GX/view?usp=sharing",
        # Replace with real SHA256 once you have the canonical link
        "sha256": None,
    },
}


def get_storage_dir() -> Path:
    """Return application model storage directory (create if needed)."""
    # Allow user override via settings file (restoration_settings.json) key: ai_model_dir
    try:
        settings_file = Path("restoration_settings.json")
        if settings_file.exists():
            import json

            with settings_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            ai_dir = data.get("ai_model_dir")
            if ai_dir:
                p = Path(ai_dir).expanduser()
                p.mkdir(parents=True, exist_ok=True)
                return p
    except Exception:
        # Fall back to default if settings cannot be read
        pass

    if sys.platform.startswith("win"):
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    else:
        base = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = Path(base) / APP_NAME / DEFAULT_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def model_path(name: str) -> Path:
    """Return expected model file path for a model key."""
    name = name.lower()
    entry = MODEL_REGISTRY.get(name)
    if not entry:
        raise KeyError(f"Unknown model '{name}'")
    filename = entry.get("filename")
    if not filename:
        raise KeyError(f"Model entry for '{name}' has no filename configured")
    return get_storage_dir() / name / filename


def model_exists(name: str) -> bool:
    try:
        p = model_path(name)
    except KeyError:
        return False
    return p.exists()


def verify_sha256(
    file_path: Path, expected: str | None
) -> tuple[bool, str | None]:
    if expected is None:
        return True, None
    try:
        h = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        digest = h.hexdigest()
        return digest == expected.lower(), digest
    except Exception:
        return False, None


def download_url(
    url: str,
    dest: Path,
    progress: bool = True,
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_flag: dict | None = None,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    # Helper to detect Google Drive file id

    def _extract_gdrive_id(u: str) -> str | None:
        import re

        # Patterns: /d/<id>/, id=, open?id=
        m = re.search(r"/d/([A-Za-z0-9_-]{10,})", u)
        if m:
            return m.group(1)
        m = re.search(r"[?&]id=([A-Za-z0-9_-]{10,})", u)
        if m:
            return m.group(1)
        return None

    def _download_from_gdrive(file_id: str, dest_path: Path) -> None:
        # Use urllib with cookie handling to follow Google Drive confirmation for large files
        import http.cookiejar
        import re

        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

        base = f"https://docs.google.com/uc?export=download&id={file_id}"
        resp = opener.open(base)
        content = resp.read()
        # If content-disposition present, we have the file
        cd = resp.headers.get("Content-Disposition")
        if cd and b"filename" in content[:512]:
            with open(dest_path, "wb") as f:
                f.write(content)
            return

        # Otherwise, look for confirm token in content
        text = content.decode("utf-8", errors="ignore")
        m = re.search(r"confirm=([0-9A-Za-z_-]+)", text)
        token = m.group(1) if m else None
        if not token:
            # Try cookies for download_warning
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

    def _report(block_num, block_size, total_size):
        if cancel_flag and cancel_flag.get("cancelled"):
            raise OSError("Download cancelled")
        if not progress:
            return
        downloaded = block_num * block_size
        if total_size > 0:
            if progress_callback:
                try:
                    progress_callback(downloaded, total_size)
                except Exception:
                    pass
            pct = downloaded * 100 / total_size
            print(
                f"Downloading {
                    dest.name}: {
                    pct:.1f}% ({
                    downloaded /
                    1024 /
                    1024:.2f} MiB of {
                    total_size /
                    1024 /
                    1024:.2f} MiB)",
                end="\r",
            )
        else:
            if progress_callback:
                try:
                    progress_callback(downloaded, -1)
                except Exception:
                    pass
            print(
                f"Downloading {dest.name}: {downloaded / 1024 / 1024:.2f} MiB", end="\r"
            )

    try:
        gd_id = _extract_gdrive_id(url)
        if gd_id:
            _download_from_gdrive(gd_id, tmp)
        else:
            urllib.request.urlretrieve(
                url, filename=str(tmp), reporthook=_report if progress else None
            )
        # move to final
        tmp.replace(dest)
        if progress:
            print(f"\nSaved to {dest}")
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


def download_model(
    name: str,
    url: str | None = None,
    sha256: str | None = None,
    *,
    accept_license: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_flag: dict | None = None,
) -> Path:
    """Download a named model to the storage directory.

    If `url` is None the registry entry will be used; if that is also None the
    function will raise ValueError and the caller should provide a URL.
    """
    key = name.lower()
    if key not in MODEL_REGISTRY:
        raise KeyError(f"Unknown model '{name}'")

    entry = MODEL_REGISTRY[key]
    model_filename = entry.get("filename")
    if not model_filename:
        raise KeyError(f"Model '{name}' missing filename in registry")
    model_url = url or entry.get("url")
    expected_sha = sha256 or entry.get("sha256")

    if model_url is None:
        raise ValueError(
            f"No default URL for model '{name}'. Please call with explicit --url."
        )

    dest_dir = get_storage_dir() / key
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / model_filename

    # License acceptance check (caller may handle UI); we do a minimal check here.
    if not accept_license:
        raise PermissionError(
            "Model download requires explicit license acceptance (accept_license=True)"
        )

    # Download
    print(f"Downloading model '{name}' from: {model_url}")
    download_url(
        model_url,
        dest,
        progress=True,
        progress_callback=progress_callback,
        cancel_flag=cancel_flag,
    )

    ok, digest = verify_sha256(dest, expected_sha)
    if expected_sha and not ok:
        raise OSError(
            f"Checksum mismatch for {dest} (got: {digest}, expected: {expected_sha})"
        )

    return dest


def ensure_models(names, *, prompt_if_missing: bool = True) -> dict[str, Path]:
    """Ensure the requested models exist locally. Return a dict name->Path.

    If a model is missing and `prompt_if_missing` is True the function will print
    instructions and raise a FileNotFoundError so the caller UI can handle it.
    """
    results: dict[str, Path] = {}
    for name in names:
        try:
            p = model_path(name)
        except KeyError:
            raise
        if p.exists():
            results[name] = p
        else:
            if prompt_if_missing:
                raise FileNotFoundError(
                    f"Model '{name}' not found at {p}. Use the model downloader to obtain it."
                )
            else:
                results[name] = p
    return results


if __name__ == "__main__":
    # Simple CLI for testing / manual downloads
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Model Manager helper (download models)"
    )
    parser.add_argument(
        "models", nargs="+", help="Model keys to download (e.g. realesrgan rife)"
    )
    parser.add_argument(
        "--yes", action="store_true", help="Accept model licenses and continue"
    )
    parser.add_argument("--url", help="Optional URL override for the first model")
    args = parser.parse_args()

    for i, m in enumerate(args.models):
        url = args.url if i == 0 and args.url else None
        try:
            path = download_model(m, url=url, accept_license=args.yes)
            print(f"Downloaded: {path}")
        except Exception as e:
            print(f"Error downloading {m}: {e}")
            sys.exit(2)

    print("All done.")
