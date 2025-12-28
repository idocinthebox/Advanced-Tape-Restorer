from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Config:
    raw: dict
    path: Path

    @property
    def work_dir(self) -> Path:
        return Path(self.raw["paths"]["work_dir"]).expanduser().resolve()

def load_config(path: str | Path) -> Config:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return Config(raw=raw, path=path)
