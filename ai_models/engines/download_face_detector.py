"""
Download OpenCV Face Detector for GFPGAN optimization
"""
import urllib.request
import os
from pathlib import Path

def download_face_detector():
    """Download face detector model files"""
    
    models_dir = Path(__file__).parent
    
    model_file = models_dir / "res10_300x300_ssd_iter_140000.caffemodel"
    config_file = models_dir / "deploy.prototxt"
    
    if model_file.exists() and config_file.exists():
        print("[OK] Face detector models already exist")
        return True
    
    print("[GFPGAN] Downloading face detector models...")
    
    try:
        # Download prototxt (already exists, but verify)
        if not config_file.exists():
            prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
            print(f"Downloading {config_file.name}...")
            urllib.request.urlretrieve(prototxt_url, str(config_file))
        
        # Download caffemodel
        if not model_file.exists():
            base_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/"
            caffemodel_url = base_url + "res10_300x300_ssd_iter_140000.caffemodel"
            print(f"Downloading {model_file.name} (10.7 MB)...")
            urllib.request.urlretrieve(caffemodel_url, str(model_file))
        
        print("[OK] Face detector models downloaded successfully")
        print(f"  Model: {model_file}")
        print(f"  Config: {config_file}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to download face detector: {e}")
        return False

if __name__ == "__main__":
    print("=== GFPGAN Face Detector Setup ===\n")
    success = download_face_detector()
    
    if success:
        print("\n[OK] Setup complete!")
        print("GFPGAN will now skip frames without faces for 50-80% speedup")
    else:
        print("\n[WARNING] Setup failed")
        print("GFPGAN will process all frames (slower but still works)")
