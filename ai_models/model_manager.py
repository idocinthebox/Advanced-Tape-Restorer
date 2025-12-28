import os
import json
import hashlib
from dataclasses import dataclass
from typing import Optional, Any

try:
    import yaml

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

try:
    import requests

    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

import zipfile
from io import BytesIO


@dataclass
class ModelFile:
    path: str
    sha256: Optional[str] = None


@dataclass
class ModelEntry:
    id: str
    engine: str
    friendly_name: str
    version: str
    license: str
    license_url: Optional[str]
    non_commercial: bool
    default_for_engine: bool
    source: dict[str, Any]
    files: list[ModelFile]
    engine_args: dict[str, Any]


class ModelManager:
    def __init__(
        self, registry_path: str, model_root: str, commercial_mode: bool = True
    ) -> None:
        self.registry_path = registry_path
        self.model_root = model_root
        self.commercial_mode = commercial_mode
        self._models: dict[str, ModelEntry] = {}

        os.makedirs(self.model_root, exist_ok=True)
        self._load_registry()

    def _load_registry(self) -> None:
        if not os.path.isfile(self.registry_path):
            raise FileNotFoundError(f"Model registry not found: {self.registry_path}")

        if self.registry_path.lower().endswith((".yml", ".yaml")):
            if not _HAS_YAML:
                raise RuntimeError("PyYAML is required to load YAML registry files.")
            with open(self.registry_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            with open(self.registry_path, encoding="utf-8") as f:
                data = json.load(f)

        models = data.get("models", [])
        for m in models:
            files = [
                ModelFile(path=f["path"], sha256=f.get("sha256"))
                for f in m.get("files", [])
            ]
            entry = ModelEntry(
                id=m["id"],
                engine=m["engine"],
                friendly_name=m.get("friendly_name", m["id"]),
                version=m.get("version", ""),
                license=m.get("license", ""),
                license_url=m.get("license_url"),
                non_commercial=bool(m.get("non_commercial", False)),
                default_for_engine=bool(m.get("default_for_engine", False)),
                source=m.get("source", {}),
                files=files,
                engine_args=m.get("engine_args", {}),
            )
            self._models[entry.id] = entry

    def list_models(self, engine: Optional[str] = None) -> list[ModelEntry]:
        if engine is None:
            return list(self._models.values())
        return [m for m in self._models.values() if m.engine == engine]

    def get_model(self, model_id: str) -> ModelEntry:
        if model_id not in self._models:
            raise KeyError(f"Unknown model id: {model_id}")
        return self._models[model_id]

    def get_default_model_for_engine(self, engine: str) -> Optional[ModelEntry]:
        for m in self._models.values():
            if m.engine == engine and m.default_for_engine:
                return m
        for m in self._models.values():
            if m.engine == engine:
                return m
        return None

    def _check_license(self, entry: ModelEntry) -> None:
        if self.commercial_mode and entry.non_commercial:
            raise PermissionError(
                f"Model '{entry.id}' is marked non-commercial ({entry.license})."
            )

    def _abs_path(self, rel_path: str) -> str:
        return os.path.join(self.model_root, rel_path)

    def _file_exists_and_ok(self, mf: ModelFile) -> bool:
        abs_path = self._abs_path(mf.path)
        if not os.path.isfile(abs_path):
            return False
        if mf.sha256:
            return self._verify_sha256(abs_path, mf.sha256)
        return True

    @staticmethod
    def _verify_sha256(path: str, expected: str) -> bool:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest().lower() == expected.lower()

    @staticmethod
    def compute_sha256(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest().lower()

    def ensure_model_available(
        self,
        model_id: str,
        auto_download: bool = True,
        progress_callback=None,
        hf_token=None,
    ) -> ModelEntry:
        entry = self.get_model(model_id)
        self._check_license(entry)

        all_present = True
        for mf in entry.files:
            if not self._file_exists_and_ok(mf):
                all_present = False
                break

        if all_present:
            return entry

        if not auto_download:
            raise FileNotFoundError(
                f"Model '{model_id}' is missing files and auto_download=False."
            )

        self._download_model_files(
            entry, progress_callback=progress_callback, hf_token=hf_token
        )

        for mf in entry.files:
            if not self._file_exists_and_ok(mf):
                raise RuntimeError(
                    f"Model '{model_id}' files still missing/invalid after download."
                )

        return entry

    def _download_model_files(
        self, entry: ModelEntry, progress_callback=None, hf_token=None
    ) -> None:
        src_type = (entry.source.get("type") or "").lower()
        url = entry.source.get("url")

        # Types that require manual installation
        if src_type in ("", "manual", "external_app", "github_repo") or not url:
            note = entry.source.get("note", "")
            msg = f"Model '{entry.id}' requires manual download."
            if note:
                msg += f" {note}"
            raise RuntimeError(msg)

        # Automatic download types: huggingface, github_release
        if src_type not in ("huggingface", "github_release", "direct", "zip"):
            raise RuntimeError(
                f"Unknown source type '{src_type}' for model '{entry.id}'"
            )

        if not _HAS_REQUESTS:
            raise RuntimeError(
                "The 'requests' package is required for model downloads."
            )

        os.makedirs(self.model_root, exist_ok=True)
        print(f"[ModelManager] Downloading model '{entry.id}' from: {url}")

        # Prepare headers for authentication
        headers = {}
        if src_type == "huggingface" and hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
            print(f"[ModelManager] Using HuggingFace authentication")

        resp = requests.get(url, stream=True, timeout=120, headers=headers)

        # Handle 401/403 errors with helpful message
        if resp.status_code in (401, 403):
            if src_type == "huggingface":
                raise RuntimeError(
                    f"Authentication required for HuggingFace model '{entry.id}'.\n"
                    f"Please enter a valid HuggingFace token in the Model Manager.\n"
                    f"Get a free token at: https://huggingface.co/settings/tokens"
                )
            else:
                raise RuntimeError(
                    f"Access denied (HTTP {resp.status_code}) for model '{entry.id}'"
                )

        resp.raise_for_status()

        # Get total size for progress tracking
        total_size = int(resp.headers.get("content-length", 0))

        content_type = resp.headers.get("content-type", "").lower()
        is_zip = (
            src_type == "zip"
            or "zip" in url.lower()
            or "application/zip" in content_type
        )

        if is_zip:
            data = b""
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                data += chunk
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    progress_callback(downloaded, total_size)
            zf = zipfile.ZipFile(BytesIO(data))
            zf.extractall(self.model_root)
            print(
                f"[ModelManager] Extracted ZIP for '{entry.id}' into {self.model_root}"
            )
        else:
            if len(entry.files) != 1:
                target = self._abs_path(f"{entry.id}_download.bin")
            else:
                target = self._abs_path(entry.files[0].path)
                os.makedirs(os.path.dirname(target), exist_ok=True)

            downloaded = 0
            with open(target, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded, total_size)

            print(f"[ModelManager] Saved model file to {target}")

    def prepare_engine_args(
        self,
        engine: str,
        model_id: Optional[str] = None,
        auto_download: bool = True,
        overrides: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        if model_id is None:
            entry = self.get_default_model_for_engine(engine)
            if entry is None:
                raise KeyError(f"No model found for engine '{engine}'.")
        else:
            entry = self.get_model(model_id)

        self.ensure_model_available(entry.id, auto_download=auto_download)

        args = dict(entry.engine_args)
        overrides = overrides or {}
        args.update(overrides)

        if entry.files:
            if len(entry.files) == 1:
                args.setdefault("weights_path", self._abs_path(entry.files[0].path))
            else:
                args.setdefault(
                    "weights_paths",
                    [self._abs_path(f.path) for f in entry.files],
                )

        return args
