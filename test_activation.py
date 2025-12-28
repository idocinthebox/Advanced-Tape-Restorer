"""Test license activation script."""
from licensing import LicenseManager

# Initialize manager
mgr = LicenseManager()

# Activate with test license
email = "dev@test.com"
license_key = "IDOC-ATR-RCD-A0A6-50E66A"

print("Activating license...")
print(f"Email: {email}")
print(f"Key: {license_key}")
print()

success, msg = mgr.activate_gumroad(email, license_key, is_trial=False)

if success:
    print("✅ ACTIVATION SUCCESSFUL")
    print(msg)
    print()
    
    # Get license info
    info = mgr.get_license_info()
    print("License Details:")
    print(f"  Type: {info.license_type.value}")
    print(f"  Email: {info.tester_id}")
    print(f"  Status: {info.status.value}")
    print(f"  Activated: {info.activation_date}")
    print()
    print("✓ License saved to: ~/.idocinthebox/activation.lic")
else:
    print("❌ ACTIVATION FAILED")
    print(msg)
