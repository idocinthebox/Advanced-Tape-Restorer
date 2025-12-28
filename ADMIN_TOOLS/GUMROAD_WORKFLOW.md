# Gumroad Licensing Workflow - Complete Guide

## Overview

Advanced Tape Restorer v4.1+ uses an **email-based, platform-agnostic** licensing system that works seamlessly with Gumroad. No hardware binding, no backend server required, works offline.

## License Format

```
IDOC-ATR-XXX-XXXX-XXXXXX

Example: IDOC-ATR-R81-B1C0-7420EC
```

- **IDOC-ATR**: Product prefix
- **R**: License type (T=Trial, P=Personal, R=Professional, E=Enterprise)
- **81**: Random uniqueness component
- **B1C0**: Random uniqueness component  
- **7420EC**: Email HMAC signature (6 chars)

Total: 22 characters including dashes

## Customer Purchase Flow

### 1. Customer Visits Website
```
https://idocinthebox.com/advanced-tape-restorer
```

### 2. Customer Clicks "Buy Now"
- Redirected to Gumroad checkout
- Pays via Gumroad

### 3. Gumroad Sends Email
```
Subject: Your Advanced Tape Restorer License

Thank you for your purchase!

Download: [Windows Installer Link]
License Key: IDOC-ATR-R81-B1C0-7420EC
Email: customer@example.com

To activate:
1. Install Advanced Tape Restorer
2. Launch the application
3. Enter your email and license key
4. Click "Activate"

Support: support@idocinthebox.com
```

### 4. Customer Activates
- Installs application
- First launch shows activation dialog
- Enters email + license key
- Clicks "Activate"
- ✓ Activated (works offline forever)

## Admin: License Generation

### Generate Single License (Manual Orders)

```bash
cd "C:\Advanced Tape Restorer v4.0"

# Professional License
python -m licensing.gumroad_generator single --email customer@example.com --type professional

# Personal License
python -m licensing.gumroad_generator single --email user@gmail.com --type personal

# Trial License (7 days)
python -m licensing.gumroad_generator single --email trial@test.com --type trial
```

Output:
```
============================================================
ADVANCED TAPE RESTORER - LICENSE KEY
============================================================
Email:         customer@example.com
License Type:  PROFESSIONAL
License Key:   IDOC-ATR-R81-B1C0-7420EC
============================================================

Email Template:
[Ready-to-send email template provided]
```

### Generate Bulk Licenses (Gumroad CSV Upload)

```bash
# Generate 100 professional licenses
python -m licensing.gumroad_generator batch --count 100 --type professional --output pro_licenses.csv

# Generate 50 personal licenses
python -m licensing.gumroad_generator batch --count 50 --type personal --output personal_licenses.csv
```

Output: `gumroad_licenses.csv`
```csv
license_key
IDOC-ATR-R81-B1C0-7420EC
IDOC-ATR-P92-A3D1-8531FD
IDOC-ATR-E73-C4E2-9642GE
...
```

### Upload to Gumroad

1. Go to Gumroad product settings
2. Enable "Generate license keys"
3. Upload `pro_licenses.csv`
4. Set "One key per purchase"
5. Done! Gumroad handles distribution

## License Revocation

### Revoke a License

```bash
# Revoke specific key
python -m licensing.revocation revoke "IDOC-ATR-R81-B1C0-7420EC" "Chargeback"

# List all revoked keys
python -m licensing.revocation list

# Create revocation file
python -m licensing.revocation init
```

### Update Revocation List

1. Edit `revoked_keys.json` in app directory:
```json
{
  "revoked": [
    "IDOC-ATR-R81-B1C0-7420EC",
    "IDOCATRP92A3D18531FD"
  ],
  "count": 2
}
```

2. Include in next app update
3. App checks on startup
4. Revoked licenses denied access

## Technical Details

### Validation Algorithm

```python
import hmac
import hashlib

MASTER_KEY = b"IDOCINTHEBOX_ATR_LICENSE_SECRET_2025_DO_NOT_SHARE"

def validate(email: str, license_key: str) -> bool:
    email = email.lower().strip()
    signature = license_key[-6:]  # Last 6 chars
    
    expected = hmac.new(MASTER_KEY, email.encode(), hashlib.sha256).hexdigest()[:6].upper()
    
    return signature == expected
```

### Security Features

✅ **HMAC-SHA256** - Cryptographically secure signatures  
✅ **Offline validation** - No server required  
✅ **Platform-agnostic** - Works on Windows, macOS, Linux  
✅ **Email-bound** - License tied to email, not hardware  
✅ **Revocation support** - Optional blacklist checking  
✅ **No expiry** - Permanent licenses (except trials)

### Storage

License stored encrypted in:
```
C:\Users\[User]\.idocinthebox\activation.lic
```

Contents (encrypted):
```json
{
  "serial_number": "IDOC-ATR-R81-B1C0-7420EC",
  "license_type": "professional",
  "activation_date": "2025-12-27T10:30:00",
  "tester_id": "customer@example.com",
  "status": "activated"
}
```

## Gumroad Setup

### 1. Create Product

- Product name: "Advanced Tape Restorer Professional"
- Price: $49 (adjust as needed)
- Description: Full feature description
- Upload: Windows installer

### 2. Enable License Keys

- Go to "License Keys" tab
- Enable "Generate license keys on purchase"
- Upload CSV: `pro_licenses.csv`
- Set: "One key per purchase"

### 3. Email Configuration

Gumroad automatically sends:
- Download link
- License key
- Customer email

### 4. Webhook (Optional)

For analytics, configure webhook:
```
https://your-domain.com/webhooks/gumroad
```

Receives:
- Purchase events
- Refund events
- License key assigned

## Support Scenarios

### "I lost my license key"

1. Check Gumroad email  
2. Or lookup in Gumroad dashboard (seller.gumroad.com)
3. Resend via Gumroad

### "Wrong email used"

Generate new license for correct email:
```bash
python -m licensing.gumroad_generator single --email correct@email.com --type professional
```

Send to customer manually.

### "License not working"

1. Verify email matches exactly (case-insensitive)
2. Check for typos in license key
3. Verify not revoked: `python -m licensing.revocation list`
4. Generate replacement if needed

### "New computer"

No action needed! Email-based licenses work on any machine.

### "Refund requested"

1. Process refund in Gumroad
2. Revoke license:
```bash
python -m licensing.revocation revoke "IDOC-ATR-XXX-XXXX-XXXXXX" "Refund"
```
3. Include in next app update

## Migration from Hardware-Bound

Existing customers with ATR-XXXX-XXXX-XXXX-XXXX-XXXXX licenses:

1. Contact customer for email
2. Generate Gumroad license:
```bash
python -m licensing.gumroad_generator single --email their@email.com --type professional
```
3. Send new license
4. Old license continues to work (backward compatible)

## Testing

### Test License Generation

```bash
python -c "from licensing.crypto_utils import generate_serial_number_gumroad, validate_license_gumroad; email = 'test@test.com'; key = generate_serial_number_gumroad(email, 'professional'); print(f'Email: {email}'); print(f'License: {key}'); valid, msg = validate_license_gumroad(email, key); print(f'Valid: {valid} - {msg}')"
```

Expected output:
```
Email: test@test.com
License: IDOC-ATR-R81-B1C0-7420EC
Valid: True - Valid professional license
```

### Test Activation Dialog

```bash
python main.py
```

- Enter test email
- Enter generated license
- Click "Activate"
- Should succeed

## Cost Analysis

| Component | Cost |
|-----------|------|
| Netlify hosting | $0 (static site) |
| Gumroad fees | ~10% per sale |
| License infrastructure | $0 (local validation) |
| Revocation updates | $0 (bundled in app updates) |

**Total ongoing cost**: Only Gumroad fees when you make sales.

## Files Reference

### For Customers
- `Advanced_Tape_Restorer_v4.1.exe` - Installer
- `IDOC-ATR-XXX-XXXX-XXXXXX` - License key (from email)

### For Admin
- `licensing/gumroad_generator.py` - Generate licenses
- `licensing/revocation.py` - Revoke licenses
- `revoked_keys.json` - Blacklist (optional)
- `ADMIN_TOOLS/generate_license.bat` - Interactive generator

### For Gumroad
- `gumroad_licenses.csv` - Bulk licenses to upload
- Product page with installer
- Email template with license key

## Future Enhancements

Planned features:

- [ ] Subscription licenses (annual renewal)
- [ ] License transfer mechanism
- [ ] Online activation server (optional)
- [ ] Usage analytics
- [ ] Auto-update with license check
- [ ] Team/organization licenses
- [ ] Volume licensing for enterprises

---

**Questions?** support@idocinthebox.com  
**Sales?** https://idocinthebox.com/advanced-tape-restorer
