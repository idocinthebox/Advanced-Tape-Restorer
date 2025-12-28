"""
Quick test script to verify GUI integration with AI Model Manager
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")

    try:
        print("✓ AIModelDialog imported successfully")
    except Exception as e:
        print(f"✗ Failed to import AIModelDialog: {e}")
        return False

    try:
        print("✓ ModelManager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ModelManager: {e}")
        return False

    try:
        print("✓ PySide6 imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PySide6: {e}")
        return False

    return True


def test_model_manager():
    """Test ModelManager initialization."""
    print("\nTesting ModelManager...")

    try:
        from ai_models.model_manager import ModelManager
        import os

        registry_path = Path("ai_models/models/registry.yaml")
        if not registry_path.exists():
            print(f"✗ Registry not found: {registry_path}")
            return False

        model_root = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "Advanced_Tape_Restorer",
            "ai_models",
        )

        manager = ModelManager(str(registry_path), model_root, commercial_mode=True)
        print(f"✓ ModelManager initialized with {len(manager.list_models())} models")

        # List some models
        models = manager.list_models()
        print(f"\nAvailable models:")
        for i, model in enumerate(models[:5]):  # Show first 5
            print(f"  {i + 1}. {model.friendly_name} ({model.engine})")

        if len(models) > 5:
            print(f"  ... and {len(models) - 5} more")

        return True

    except Exception as e:
        print(f"✗ Failed to initialize ModelManager: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_dialog_creation():
    """Test creating the dialog (without showing it)."""
    print("\nTesting dialog creation...")

    try:
        from PySide6.QtWidgets import QApplication
        from gui.ai_model_dialog import AIModelDialog

        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create dialog
        dialog = AIModelDialog()
        print("✓ AIModelDialog created successfully")

        # Check that it has the expected attributes
        if hasattr(dialog, "model_manager"):
            print("✓ Dialog has model_manager attribute")
        else:
            print("✗ Dialog missing model_manager attribute")
            return False

        if hasattr(dialog, "table"):
            print("✓ Dialog has table widget")
        else:
            print("✗ Dialog missing table widget")
            return False

        return True

    except Exception as e:
        print(f"✗ Failed to create dialog: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Advanced Tape Restorer v3.0 - GUI Integration Test")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("ModelManager", test_model_manager()))
    results.append(("Dialog Creation", test_dialog_creation()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed. ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
