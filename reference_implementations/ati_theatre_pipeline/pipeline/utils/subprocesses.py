from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Sequence

class CommandError(RuntimeError):
    pass

def run(cmd: Sequence[str], cwd: str | None = None) -> None:
    p = subprocess.run(list(cmd), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise CommandError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n\n{p.stdout}")

def capture_output(cmd: Sequence[str]) -> str:
    p = subprocess.run(list(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise CommandError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n\n{p.stdout}")
    return p.stdout
