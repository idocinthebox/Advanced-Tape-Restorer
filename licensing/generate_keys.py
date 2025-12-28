"""
Admin tool for generating activation codes

Usage:
    python -m licensing.generate_keys --type personal --hardware ABCD1234 --tester user@example.com --days 365
    python -m licensing.generate_keys --type trial --hardware ABCD1234 --tester test_user --days 7
    python -m licensing.generate_keys --type professional --hardware ABCD1234 --tester company_user
"""

import argparse
from .crypto_utils import generate_serial_number, validate_serial_number


def main():
    parser = argparse.ArgumentParser(description="Generate activation codes for Advanced Tape Restorer")
    
    parser.add_argument("--type", required=True, choices=["trial", "personal", "professional", "enterprise"],
                       help="License type")
    parser.add_argument("--hardware", required=True,
                       help="Hardware ID (first 4 chars minimum)")
    parser.add_argument("--tester", required=True,
                       help="Tester ID (email or identifier)")
    parser.add_argument("--days", type=int, default=None,
                       help="Expiry days (omit for permanent)")
    parser.add_argument("--validate", action="store_true",
                       help="Validate generated serial")
    
    args = parser.parse_args()
    
    # Ensure hardware ID is at least 4 chars
    hardware_id = args.hardware.upper()
    if len(hardware_id) < 4:
        print("Error: Hardware ID must be at least 4 characters")
        return
    
    # Generate serial
    serial = generate_serial_number(
        license_type=args.type,
        hardware_id=hardware_id,
        tester_id=args.tester,
        expiry_days=args.days
    )
    
    print("=" * 60)
    print("ADVANCED TAPE RESTORER - ACTIVATION CODE")
    print("=" * 60)
    print(f"License Type:  {args.type.upper()}")
    print(f"Hardware ID:   {hardware_id}")
    print(f"Tester ID:     {args.tester}")
    print(f"Expiry:        {'Permanent' if args.days is None else f'{args.days} days'}")
    print()
    print(f"ACTIVATION CODE:")
    print(f"  {serial}")
    print()
    
    # Validate if requested
    if args.validate:
        print("Validating generated serial...")
        is_valid, message, info = validate_serial_number(serial, hardware_id)
        
        if is_valid:
            print(f"✓ Valid: {message}")
            print(f"  License Type: {info['license_type']}")
            print(f"  Expiry: {info['expiry_date'] if info['expiry_date'] else 'Permanent'}")
        else:
            print(f"✗ Invalid: {message}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
