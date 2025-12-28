import vsrife
import os
import shutil
import glob
from pathlib import Path
import importlib
import sys


def main():
    print(f"vsrife package: {vsrife.__file__}")
    src = os.path.join(os.path.dirname(vsrife.__file__), "models")
    print(f"src models dir: {src}")

    if not os.path.isdir(src):
        print("Error: vsrife models dir not found. Did you run 'python -m vsrife'?")
        sys.exit(1)

    local_app = os.getenv("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    dst = os.path.join(local_app, "Advanced_Tape_Restorer", "ai_models", "rife")
    Path(dst).mkdir(parents=True, exist_ok=True)
    print(f"Destination dir: {dst}")

    files = glob.glob(os.path.join(src, "flownet_v*.pkl"))
    count = 0
    for f in files:
        shutil.copy2(f, dst)
        count += 1

    print(f"Copied {count} model files.")

    # copy preferred model as rife_model.pth
    # The app expects 'rife_model.pth' for the 'rife' key in MODEL_REGISTRY
    pref = os.path.join(src, "flownet_v4.25.pkl")
    if os.path.exists(pref):
        target = os.path.join(dst, "rife_model.pth")
        shutil.copy2(pref, target)
        print(f"Copied {pref} to {target}")
    else:
        print(f"Warning: Preferred model {pref} not found.")

    # Verify
    sys.path.insert(0, os.getcwd())
    try:
        aim = importlib.import_module("core.ai_model_manager")
        expected_path = aim.model_path("rife")
        exists = aim.model_exists("rife")
        print(f"Model path expected: {expected_path}")
        print(f"Model exists: {exists}")
    except Exception as e:
        print(f"Verification failed: {e}")


if __name__ == "__main__":
    main()
