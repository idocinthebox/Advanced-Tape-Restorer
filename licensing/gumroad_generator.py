"""
Generate license keys for Gumroad upload

Creates CSV file with pre-generated license keys for Gumroad products.
"""

import csv
import argparse
from pathlib import Path
from .crypto_utils import generate_serial_number_gumroad


def generate_keys_csv(num_keys: int, license_type: str, output_file: str = "gumroad_licenses.csv"):
    """
    Generate CSV file of license keys for Gumroad.
    
    Args:
        num_keys: Number of keys to generate
        license_type: License type (trial, personal, professional, enterprise)
        output_file: Output CSV filename
    """
    keys = []
    
    print(f"Generating {num_keys} {license_type} license keys...")
    
    for i in range(num_keys):
        # Use index as pseudo-email for generation
        # Gumroad will map these to actual customer emails
        pseudo_email = f"customer{i+1:04d}@placeholder.com"
        license_key = generate_serial_number_gumroad(pseudo_email, license_type)
        keys.append(license_key)
    
    # Write to CSV (Gumroad format)
    output_path = Path(output_file)
    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['license_key'])  # Header
        for key in keys:
            writer.writerow([key])
    
    print(f"✓ Generated {len(keys)} keys")
    print(f"✓ Saved to: {output_path.absolute()}")
    print(f"\nUpload to Gumroad:")
    print(f"  1. Go to product settings")
    print(f"  2. Enable 'Generate license keys'")
    print(f"  3. Upload {output_file}")
    print(f"  4. Set 'One key per purchase'")


def generate_email_specific_key(email: str, license_type: str):
    """
    Generate license key for specific email (manual orders).
    
    Args:
        email: Customer email
        license_type: License type
    """
    license_key = generate_serial_number_gumroad(email, license_type)
    
    print("=" * 60)
    print("ADVANCED TAPE RESTORER - LICENSE KEY")
    print("=" * 60)
    print(f"Email:         {email}")
    print(f"License Type:  {license_type.upper()}")
    print(f"License Key:   {license_key}")
    print("=" * 60)
    print("\nEmail Template:")
    print("-" * 60)
    print(f"Subject: Advanced Tape Restorer - License Key\n")
    print(f"Thank you for purchasing Advanced Tape Restorer!\n")
    print(f"Your license key: {license_key}\n")
    print(f"Email: {email}")
    print(f"License Type: {license_type.title()}\n")
    print("To activate:")
    print("1. Launch Advanced Tape Restorer")
    print("2. Enter your email and license key")
    print("3. Click 'Activate'\n")
    print("Need help? support@idocinthebox.com")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="Generate Gumroad license keys")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Batch generation for Gumroad
    batch_parser = subparsers.add_parser('batch', help='Generate CSV for Gumroad')
    batch_parser.add_argument('--count', type=int, required=True,
                             help='Number of keys to generate')
    batch_parser.add_argument('--type', required=True,
                             choices=['trial', 'personal', 'professional', 'enterprise'],
                             help='License type')
    batch_parser.add_argument('--output', default='gumroad_licenses.csv',
                             help='Output CSV filename')
    
    # Single key generation for manual orders
    single_parser = subparsers.add_parser('single', help='Generate single key for email')
    single_parser.add_argument('--email', required=True,
                              help='Customer email')
    single_parser.add_argument('--type', required=True,
                              choices=['trial', 'personal', 'professional', 'enterprise'],
                              help='License type')
    
    args = parser.parse_args()
    
    if args.command == 'batch':
        generate_keys_csv(args.count, args.type, args.output)
    elif args.command == 'single':
        generate_email_specific_key(args.email, args.type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
