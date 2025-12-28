"""
Quick script to check if AI features are in the generated VapourSynth script
Run after clicking Start Processing to see what's actually being applied
"""

from pathlib import Path

script_file = Path("temp_restoration_script.vpy")

if script_file.exists():
    print("=" * 60)
    print("VAPOURSYNTH SCRIPT CONTENTS")
    print("=" * 60)

    content = script_file.read_text(encoding="utf-8")
    print(content)
    print("\n" + "=" * 60)
    print("AI FEATURES DETECTION")
    print("=" * 60)

    features = {
        "RIFE (Frame Interpolation)": "vsrife" in content and "RIFE(video" in content,
        "RealESRGAN (Upscaling)": "RealESRGAN" in content,
        "ProPainter (Inpainting)": "ProPainter" in content
        and "inference_propainter" in content,
        "BM3D (Denoising)": "bm3d.Basic" in content,
        "QTGMC (Deinterlacing)": "QTGMC" in content,
        "TComb (Artifact Removal)": "tcomb.TComb" in content,
        "Bifrost (Rainbow Artifacts)": "bifrost.Bifrost" in content,
    }

    print("\n✅ = Active | ❌ = Not Found\n")
    for feature, is_active in features.items():
        status = "✅" if is_active else "❌"
        print(f"{status} {feature}")

    print("\n" + "=" * 60)

else:
    print("❌ temp_restoration_script.vpy not found!")
    print("   Run a processing job first, then run this script before it completes.")
