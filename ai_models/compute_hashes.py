import os
from .model_manager import ModelManager


def compute_hashes_for_all(mm: ModelManager):
    for entry in mm.list_models():
        print(f"Model: {entry.id}")
        for mf in entry.files:
            abs_path = os.path.join(mm.model_root, mf.path)
            if os.path.isfile(abs_path):
                sha = mm.compute_sha256(abs_path)
                print(f"  - path: {mf.path}")
                print(f'    sha256: "{sha}"')
            else:
                print(f"  - path: {mf.path}")
                print(f"    sha256: null  # file missing")


if __name__ == "__main__":
    mm = ModelManager(
        registry_path="restoration_pipeline/models/registry.yaml",
        model_root="restoration_pipeline/models/cache",
        commercial_mode=False,
    )
    compute_hashes_for_all(mm)
