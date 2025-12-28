"""
Test model download functionality
"""

from ai_models.model_manager import ModelManager
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_download():
    """Test downloading a model."""
    print("Testing Model Download...")
    print("=" * 60)

    # Setup paths
    registry_path = Path("ai_models/models/registry.yaml")
    model_root = Path("test_models")
    model_root.mkdir(exist_ok=True)

    try:
        # Initialize manager
        print(f"Registry: {registry_path}")
        print(f"Model root: {model_root}")

        manager = ModelManager(
            str(registry_path), str(model_root), commercial_mode=True
        )
        print(f"✓ ModelManager initialized")

        # List available models
        models = manager.list_models()
        print(f"\nFound {len(models)} models:")
        for i, m in enumerate(models[:5]):
            print(f"  {i + 1}. {m.friendly_name} ({m.id})")
            print(f"      Source: {m.source.get('type')} - {m.source.get('url')}")

        # Try to download RealESRGAN (smallest downloadable one)
        print("\n" + "=" * 60)
        print("Testing download: realesrgan_x2plus")
        print("=" * 60)

        def progress_cb(current, total):
            percent = (current / total) * 100
            mb_current = current / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            print(
                f"Progress: {percent:.1f}% ({mb_current:.2f} MB / {mb_total:.2f} MB)",
                end="\r",
            )

        result = manager.ensure_model_available(
            "realesrgan_x2plus", auto_download=True, progress_callback=progress_cb
        )

        print("\n✓ Download completed!")
        print(f"Model: {result.friendly_name}")
        print(f"Files:")
        for f in result.files:
            path = model_root / f.path
            exists = "✓" if path.exists() else "✗"
            size = path.stat().st_size / (1024 * 1024) if path.exists() else 0
            print(f"  {exists} {f.path} ({size:.2f} MB)")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_download()
    sys.exit(0 if success else 1)
