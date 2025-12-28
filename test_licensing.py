"""
Test script for licensing system
"""

import sys
from pathlib import Path
import tempfile


def test_hardware_id():
    """Test hardware ID generation"""
    print("Testing hardware ID generation...")
    from licensing.crypto_utils import generate_hardware_id
    
    hw_id = generate_hardware_id()
    print(f"  ✓ Hardware ID: {hw_id}")
    print(f"  ✓ Length: {len(hw_id)} chars")
    
    # Test consistency
    hw_id2 = generate_hardware_id()
    if hw_id == hw_id2:
        print("  ✓ Hardware ID is consistent")
    else:
        print("  ✗ Hardware ID not consistent!")
        return False
    
    return True


def test_serial_generation():
    """Test serial number generation"""
    print("\nTesting serial number generation...")
    from licensing.crypto_utils import generate_serial_number
    
    hardware_id = "ABCD1234EFGH5678"
    tester_id = "test@example.com"
    
    # Test trial (7 days)
    trial_serial = generate_serial_number("trial", hardware_id, tester_id, expiry_days=7)
    print(f"  ✓ Trial serial: {trial_serial}")
    
    # Test permanent professional
    pro_serial = generate_serial_number("professional", hardware_id, tester_id)
    print(f"  ✓ Professional serial: {pro_serial}")
    
    # Verify format
    if trial_serial.startswith("ATR-") and len(trial_serial) == 29:
        print("  ✓ Serial format correct")
    else:
        print("  ✗ Serial format incorrect!")
        return False
    
    return True


def test_serial_validation():
    """Test serial number validation"""
    print("\nTesting serial validation...")
    from licensing.crypto_utils import generate_serial_number, validate_serial_number
    
    hardware_id = "TEST1234ABCD5678"
    tester_id = "validator@test.com"
    
    # Generate valid serial
    serial = generate_serial_number("personal", hardware_id, tester_id, expiry_days=30)
    print(f"  Generated: {serial}")
    
    # Test valid serial
    is_valid, message, info = validate_serial_number(serial, hardware_id)
    if is_valid:
        print(f"  ✓ Valid: {message}")
        print(f"    Type: {info['license_type']}")
    else:
        print(f"  ✗ Should be valid: {message}")
        return False
    
    # Test invalid serial (wrong hardware)
    is_valid, message, info = validate_serial_number(serial, "WRONG123")
    if not is_valid and "Hardware mismatch" in message:
        print(f"  ✓ Correctly rejected wrong hardware: {message}")
    else:
        print(f"  ✗ Should reject wrong hardware!")
        return False
    
    # Test invalid format
    is_valid, message, info = validate_serial_number("INVALID-SERIAL", hardware_id)
    if not is_valid:
        print(f"  ✓ Correctly rejected invalid format: {message}")
    else:
        print(f"  ✗ Should reject invalid format!")
        return False
    
    return True


def test_license_manager():
    """Test license manager"""
    print("\nTesting license manager...")
    from licensing.license_manager import LicenseManager
    from licensing.crypto_utils import generate_serial_number, generate_hardware_id
    
    # Use temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        manager = LicenseManager(app_data_dir=temp_dir)
        print(f"  ✓ Manager created")
        print(f"  ✓ Hardware ID: {manager.get_hardware_id()}")
        
        # Check not activated initially
        if not manager.is_activated():
            print("  ✓ Not activated initially")
        else:
            print("  ✗ Should not be activated!")
            return False
        
        # Generate and activate with valid serial
        hw_id = manager.get_hardware_id()
        serial = generate_serial_number("professional", hw_id, "test_user", expiry_days=365)
        
        success, message = manager.activate(serial, "test_user")
        if success:
            print(f"  ✓ Activation successful: {message}")
        else:
            print(f"  ✗ Activation failed: {message}")
            return False
        
        # Verify activated
        if manager.is_activated():
            print("  ✓ Now activated")
        else:
            print("  ✗ Should be activated!")
            return False
        
        # Get license info
        license_info = manager.get_license_info()
        if license_info:
            print(f"  ✓ License type: {license_info.license_type.value}")
            print(f"  ✓ Days remaining: {license_info.days_remaining()}")
        else:
            print("  ✗ No license info!")
            return False
        
        # Test deactivation
        if manager.deactivate():
            print("  ✓ Deactivated successfully")
        else:
            print("  ✗ Deactivation failed!")
            return False
        
        # Verify not activated after deactivation
        if not manager.is_activated():
            print("  ✓ Not activated after deactivation")
        else:
            print("  ✗ Should not be activated after deactivation!")
            return False
        
        return True
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_encryption():
    """Test encryption/decryption"""
    print("\nTesting encryption...")
    from licensing.crypto_utils import encrypt_activation_data, decrypt_activation_data
    
    test_data = "This is test license data with special chars: @#$%^&*()"
    
    encrypted = encrypt_activation_data(test_data)
    print(f"  ✓ Encrypted: {encrypted[:30]}...")
    
    decrypted = decrypt_activation_data(encrypted)
    if decrypted == test_data:
        print("  ✓ Decryption successful")
    else:
        print("  ✗ Decryption failed!")
        return False
    
    # Test invalid data
    invalid_decrypted = decrypt_activation_data("INVALID_BASE64!!!")
    if invalid_decrypted is None:
        print("  ✓ Correctly handled invalid data")
    else:
        print("  ✗ Should return None for invalid data!")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("LICENSING SYSTEM TEST")
    print("=" * 60)
    
    results = []
    results.append(("Hardware ID", test_hardware_id()))
    results.append(("Serial Generation", test_serial_generation()))
    results.append(("Serial Validation", test_serial_validation()))
    results.append(("Encryption", test_encryption()))
    results.append(("License Manager", test_license_manager()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed_count}/{total} passed")
    
    if passed_count == total:
        print("\n🎉 All tests passed! Licensing system is ready.")
    else:
        print("\n⚠ Some tests failed. Please review the output above.")
        sys.exit(1)
