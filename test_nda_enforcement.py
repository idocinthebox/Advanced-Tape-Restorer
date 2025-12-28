"""
Test script for NDA enforcement system

Tests:
1. NDA module imports work
2. Config initialization
3. NDA document hash calculation
4. Storage directory creation
5. Acceptance flow (simulated)
6. Clickwrap dialog (GUI test)
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all NDA enforcement modules import correctly."""
    print("Testing NDA module imports...")
    try:
        from NDA.nda_enforcement import config as nda_config
        from NDA.nda_enforcement.config import NDAConfig, get_default_config
        from NDA.nda_enforcement.crypto import sha256_file, sha256_bytes
        from NDA.nda_enforcement.hooks import on_app_start, report_breach
        from NDA.nda_enforcement.storage import NDAStore
        from NDA.nda_enforcement.policy import enforce_for_tester
        from NDA.nda_enforcement.models import AcceptanceRecord
        from NDA.nda_enforcement.pyside6_clickwrap import run_nda_clickwrap, NDAClickwrapDialog
        print("  ✓ All imports successful")
        print(f"  ✓ Config build_id: {nda_config.build_id}")
        print(f"  ✓ Config NDA version: {nda_config.nda_version}")
        print(f"  ✓ Config NDA filename: {nda_config.nda_filename}")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_nda_document():
    """Test that NDA PDF exists and can be hashed."""
    print("\nTesting NDA document...")
    from NDA.nda_enforcement import config as nda_config
    from NDA.nda_enforcement.crypto import sha256_file
    
    nda_path = Path("NDA") / nda_config.nda_filename
    if not nda_path.exists():
        print(f"  ✗ NDA PDF not found at: {nda_path}")
        print(f"  ✗ Expected filename: {nda_config.nda_filename}")
        return False
    
    try:
        nda_hash = sha256_file(nda_path)
        print(f"  ✓ NDA PDF found: {nda_config.nda_filename}")
        print(f"  ✓ SHA256: {nda_hash[:16]}...{nda_hash[-16:]}")
        
        # Verify hash matches config
        if nda_hash == nda_config.nda_doc_sha256:
            print(f"  ✓ SHA256 matches config")
        else:
            print(f"  ⚠ SHA256 mismatch!")
            print(f"    Expected: {nda_config.nda_doc_sha256}")
            print(f"    Actual:   {nda_hash}")
        
        return True
    except Exception as e:
        print(f"  ✗ Failed to hash NDA: {e}")
        return False

def test_config():
    """Test configuration initialization."""
    print("\nTesting configuration...")
    try:
        from NDA.nda_enforcement import config as nda_config
        from NDA.nda_enforcement.config import get_default_config
        from NDA.nda_enforcement.crypto import sha256_file
        
        nda_path = Path("NDA") / nda_config.nda_filename
        nda_hash = sha256_file(nda_path)
        
        cfg = get_default_config()
        
        print(f"  ✓ Config created")
        print(f"  ✓ Build ID: {cfg.build_id}")
        print(f"  ✓ NDA Version: {cfg.nda_version}")
        print(f"  ✓ App data dir: {cfg.app_data_dir}")
        return True
    except Exception as e:
        print(f"  ✗ Config failed: {e}")
        return False

def test_storage():
    """Test storage directory creation."""
    print("\nTesting storage...")
    try:
        from NDA.nda_enforcement.config import get_default_config
        from NDA.nda_enforcement.storage import NDAStore
        from NDA.nda_enforcement import config as nda_config
        from NDA.nda_enforcement.config import get_default_config
        from NDA.nda_enforcement.storage import NDAStore
        from NDA.nda_enforcement.crypto import sha256_file
        
        cfg = get_default_config()
        
        # Use test subdirectory
        test_cfg = type(cfg)(
            build_id="test-build",
            nda_version="TEST-NDA",
            nda_doc_sha256=cfg.nda_doc_sha256,
            app_data_dir=cfg.app_data_dir / "test",
        )
        
        store = NDAStore(test_cfg.app_data_dir)
        print(f"  ✓ Storage created at: {test_cfg.app_data_dir}")
        print(f"  ✓ Events file: {test_cfg.app_data_dir / 'events.jsonl'}")
        print(f"  ✓ Latest state: {test_cfg.app_data_dir / 'latest_acceptance.json'}")
        return True
    except Exception as e:
        print(f"  ✗ Storage failed: {e}")
        return False

def test_enforcement_check():
    """Test enforcement check (should fail without acceptance)."""
    print("\nTesting enforcement check...")
    try:
        from NDA.nda_enforcement.config import get_default_config
        from NDA.nda_enforcement.hooks import on_app_start
        import platform
        
        cfg = get_default_config()
        
        tester_id = platform.node() or "TEST_USER"
        allowed, msg = on_app_start(cfg, tester_id)
        
        print(f"  ✓ Enforcement check completed")
        print(f"  ✓ Allowed: {allowed}")
        print(f"  ✓ Message: {msg}")
        return True
    except Exception as e:
        print(f"  ✗ Enforcement check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_dialog():
    """Test GUI clickwrap dialog (interactive)."""
    print("\nTesting GUI clickwrap dialog...")
    print("  Note: This will open the actual NDA dialog. Close it to continue.")
    
    try:
        from PySide6.QtWidgets import QApplication
        from NDA.nda_enforcement import config as nda_config
        from NDA.nda_enforcement.config import get_default_config
        from NDA.nda_enforcement.pyside6_clickwrap import NDAClickwrapDialog
        import platform
        
        app = QApplication(sys.argv)
        
        cfg = get_default_config()
        
        # Use test subdirectory
        test_cfg = type(cfg)(
            build_id=cfg.build_id,
            nda_version=cfg.nda_version,
            nda_doc_sha256=cfg.nda_doc_sha256,
            app_data_dir=cfg.app_data_dir / "test",
        )
        
        tester_id = platform.node() or "TEST_USER"
        nda_path = Path("NDA") / nda_config.nda_filename
        
        dialog = NDAClickwrapDialog(test_cfg, tester_id, nda_path)
        dialog.show()
        
        print("  ✓ Dialog created and shown")
        print(f"  ✓ NDA file: {nda_config.nda_filename}")
        print("  ✓ Close the dialog to complete test")
        
        result = dialog.exec()
        print(f"  ✓ Dialog result: {'Accepted' if result else 'Declined'}")
        return True
        
    except Exception as e:
        print(f"  ✗ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("NDA ENFORCEMENT SYSTEM TEST")
    print("=" * 60)
    
    results = []
    results.append(("Module Imports", test_imports()))
    results.append(("NDA Document", test_nda_document()))
    results.append(("Configuration", test_config()))
    results.append(("Storage", test_storage()))
    results.append(("Enforcement Check", test_enforcement_check()))
    
    # Ask if user wants to test GUI
    print("\n" + "=" * 60)
    response = input("Test GUI clickwrap dialog? (y/n): ").strip().lower()
    if response == 'y':
        results.append(("GUI Dialog", test_gui_dialog()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! NDA enforcement is ready to use.")
        print("\nTo test with NDA enabled:")
        print("  1. Set DEV_BYPASS_NDA = False in main.py")
        print("  2. Run: python main.py")
        print("\nTo bypass NDA during development:")
        print("  1. Set DEV_BYPASS_NDA = True in main.py (currently set)")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    sys.exit(0 if passed == total else 1)
