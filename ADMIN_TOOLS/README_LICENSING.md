# Admin Tools for Advanced Tape Restorer v4.1

## License Generation

### generate_license.bat
Interactive batch file for generating activation codes.

**Usage:**
1. Run `generate_license.bat`
2. Enter license type: trial, personal, professional, or enterprise
3. Enter hardware ID (user provides from activation dialog)
4. Enter tester ID (user's email or identifier)
5. Enter expiry days (leave empty for permanent)

**Example:**
```
License type: professional
Hardware ID: A7ED1EC30700517A
Tester ID: customer@example.com
Expiry days: 365
```

### Python Command Line
```bash
# Generate 7-day trial
python -m licensing.generate_keys --type trial --hardware A7ED1EC --tester user@test.com --days 7

# Generate 1-year personal license
python -m licensing.generate_keys --type personal --hardware A7ED1EC --tester customer@gmail.com --days 365

# Generate permanent professional license
python -m licensing.generate_keys --type professional --hardware A7ED1EC --tester company@business.com

# Validate generated serial
python -m licensing.generate_keys --type personal --hardware A7ED1EC --tester test@test.com --days 30 --validate
```

## License Types

### Trial (T)
- 7-day evaluation period
- Full features
- Hardware-bound
- Non-transferable

### Personal (P)
- Single user
- Home use only
- Renewable annually
- Hardware-bound

### Professional (R)
- Commercial use
- Priority support
- Renewable annually
- Hardware-bound

### Enterprise (E)
- Bulk licensing
- Multi-user
- Custom terms
- Contact for pricing

## Hardware ID Format

Hardware IDs are 16-character hexadecimal strings generated from:
- Machine UUID (network MAC address)
- System architecture
- Processor info

**Example:** `A7ED1EC30700517A`

## Security Notes

**IMPORTANT:**
1. Keep `licensing/crypto_utils.py` secure - contains master key
2. Never share generated serials publicly
3. Each serial is bound to specific hardware
4. Serials cannot be transferred between machines
5. Store all generated serials in secure database

## Activation Code Format

```
ATR-XXXX-XXXX-XXXX-XXXX-XXXXX
```

- ATR: Product prefix
- Part 1: License type + Hardware ID start (4 chars)
- Part 2: Hardware ID + Tester hash (4 chars)
- Part 3: Tester + Expiry start (4 chars)
- Part 4: Expiry + Signature start (4 chars)
- Part 5: Signature end (5 chars)

Total: 29 characters including dashes

## Troubleshooting

### "Invalid serial format"
- Check all dashes are present
- Verify no spaces in serial
- Ensure serial starts with ATR-

### "Hardware mismatch"
- Serial is bound to different machine
- Generate new serial for current hardware ID

### "Signature mismatch"
- Serial has been modified or corrupted
- Generate new serial

### "License expired"
- Trial or annual license has expired
- Generate new serial with extended expiry

## Distribution

When distributing activation codes:

1. **Email Template:**
```
Subject: Advanced Tape Restorer - Activation Code

Thank you for purchasing Advanced Tape Restorer!

Your activation code: ATR-XXXX-XXXX-XXXX-XXXX-XXXXX

License Type: [Professional/Personal/Trial]
Hardware ID: [User's HW ID]
Expiry: [Date or "Permanent"]

To activate:
1. Launch Advanced Tape Restorer
2. Enter your activation code
3. Click "Activate"

Need help? support@idocinthebox.com
```

2. **Track in database:**
   - Serial number
   - Hardware ID
   - Tester email
   - License type
   - Issue date
   - Expiry date
   - Status (active/expired/revoked)

3. **Support workflow:**
   - User provides hardware ID from activation dialog
   - Generate serial for that hardware ID
   - Send via secure email
   - Record in database
   - Follow up if issues

## Emergency Deactivation

If you need to deactivate a user's license:

1. User must manually delete: `~/.idocinthebox/activation.lic`
2. Or provide updated software with revoked serials list
3. Or implement online activation checking (future feature)

## Future Enhancements

Planned features for licensing system:

- [ ] Online activation server
- [ ] License transfer mechanism
- [ ] Floating licenses (enterprise)
- [ ] Volume licensing
- [ ] Subscription management
- [ ] Auto-renewal reminders
- [ ] License analytics dashboard
