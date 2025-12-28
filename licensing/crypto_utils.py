"""
Cryptographic utilities for licensing system
"""

import hashlib
import hmac
import secrets
import base64
from typing import Tuple


# Master secret key (in production, this would be securely stored/obfuscated)
# For a commercial product, use proper key management
MASTER_KEY = b"IDOCINTHEBOX_ATR_LICENSE_SECRET_2025_DO_NOT_SHARE"


def generate_hardware_id() -> str:
    """
    Generate unique hardware ID based on machine characteristics.
    Uses multiple hardware identifiers for stability.
    
    NOTE: Hardware binding is OPTIONAL. For Gumroad workflow,
    use email-based licenses instead (platform-agnostic).
    """
    import platform
    import uuid
    
    # Collect hardware identifiers
    identifiers = []
    
    # Machine UUID (most stable)
    try:
        machine_uuid = str(uuid.UUID(int=uuid.getnode()))
        identifiers.append(machine_uuid)
    except:
        pass
    
    # System info
    identifiers.append(platform.machine())
    identifiers.append(platform.processor())
    
    # Combine and hash
    combined = "|".join(identifiers).encode('utf-8')
    hardware_hash = hashlib.sha256(combined).hexdigest()[:16]
    
    return hardware_hash.upper()


def generate_serial_number_gumroad(email: str, license_type: str = "professional") -> str:
    """
    Generate Gumroad-compatible license key (email-based, platform-agnostic).
    
    Format: IDOC-ATR-XXXX-XXXX-XXXX
    
    Components:
    - Product prefix: IDOC-ATR
    - License type code (1 char)
    - Random component (8 chars)
    - Email signature (8 chars from HMAC)
    
    This key works on Windows, macOS, and Linux.
    No hardware binding, no expiry encoding.
    """
    from datetime import datetime
    import secrets
    
    # License type codes
    type_codes = {
        'trial': 'T',
        'personal': 'P',
        'professional': 'R',
        'enterprise': 'E',
    }
    
    type_code = type_codes.get(license_type.lower(), 'P')
    
    # Random component for uniqueness
    random_part = secrets.token_hex(3).upper()  # 6 chars
    
    # Email-based HMAC signature (platform-agnostic)
    payload = email.lower().strip().encode('utf-8')
    signature = hmac.new(MASTER_KEY, payload, hashlib.sha256).hexdigest()[:6].upper()
    
    # Build license key: IDOC-ATR-TXXX-XXX-XXX (total 13 chars after IDOC-ATR-)
    part1 = type_code + random_part[:2]  # 3 chars
    part2 = random_part[2:6]  # 4 chars  
    part3 = signature[:6]  # 6 chars
    
    license_key = f"IDOC-ATR-{part1}-{part2}-{part3}"
    
    return license_key


def validate_license_gumroad(email: str, license_key: str, revoked_keys: list = None) -> Tuple[bool, str]:
    """
    Validate Gumroad-style license key (email-based).
    
    Args:
        email: Customer email
        license_key: License key from Gumroad
        revoked_keys: Optional list of revoked keys
    
    Returns:
        (is_valid, message)
    """
    try:
        # Normalize input
        email = email.lower().strip()
        license_key = license_key.upper().replace(" ", "").replace("-", "")
        
        # Check format
        if not license_key.startswith("IDOCATR"):
            return False, "Invalid license format (must start with IDOC-ATR)"
        
        # Remove prefix
        license_key = license_key[7:]  # Remove IDOCATR
        
        if len(license_key) != 13:
            return False, f"Invalid license length (expected 13, got {len(license_key)})"
        
        # Check if revoked
        if revoked_keys:
            full_key = f"IDOC-ATR-{license_key[:4]}-{license_key[4:8]}-{license_key[8:]}"
            if full_key in revoked_keys or license_key in revoked_keys:
                return False, "License has been revoked. Contact support."
        
        # Extract signature from license
        provided_sig = license_key[7:13]  # Last 6 chars
        
        # Compute expected signature from email
        payload = email.encode('utf-8')
        expected_sig = hmac.new(MASTER_KEY, payload, hashlib.sha256).hexdigest()[:6].upper()
        
        if provided_sig != expected_sig:
            return False, "Invalid license key for this email address"
        
        # Extract license type
        type_code = license_key[0]
        type_map = {'T': 'trial', 'P': 'personal', 'R': 'professional', 'E': 'enterprise'}
        license_type = type_map.get(type_code, 'unknown')
        
        return True, f"Valid {license_type} license"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def generate_serial_number(license_type: str, hardware_id: str, tester_id: str, 
                          expiry_days: int = None) -> str:
    """
    Generate hardware-bound serial number (LEGACY - for backward compatibility).
    
    For new Gumroad workflow, use generate_serial_number_gumroad() instead.
    
    Format: ATR-XXXX-XXXX-XXXX-XXXX-XXXXX
    
    Components:
    - License type code (1 char)
    - Hardware binding (4 chars)
    - Tester ID hash (4 chars)
    - Expiry timestamp (4 chars) or PERM for permanent
    - HMAC signature (8 chars)
    """
    from datetime import datetime, timedelta
    
    # License type codes
    type_codes = {
        'trial': 'T',
        'personal': 'P',
        'professional': 'R',
        'enterprise': 'E',
    }
    
    type_code = type_codes.get(license_type.lower(), 'T')
    
    # Hardware binding (first 4 chars of hardware ID)
    hw_part = hardware_id[:4]
    
    # Tester ID hash
    tester_hash = hashlib.sha256(tester_id.encode()).hexdigest()[:4].upper()
    
    # Expiry encoding
    if expiry_days is None:
        expiry_part = "PERM"
    else:
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        # Encode as days since epoch (base36 for compactness)
        days_since_epoch = int(expiry_date.timestamp() // 86400)
        expiry_encoded = base36_encode(days_since_epoch).upper()
        # Pad to 4 chars
        expiry_part = expiry_encoded[-4:].zfill(4)
    
    # Build payload
    payload = f"{type_code}{hw_part}{tester_hash}{expiry_part}"
    
    # Generate HMAC signature
    signature = hmac.new(MASTER_KEY, payload.encode(), hashlib.sha256).hexdigest()[:8].upper()
    
    # Format as serial: ATR-XXXX-XXXX-XXXX-XXXX-XXXXX (total 29 chars)
    # Payload is 13 chars (1+4+4+4), signature is 8 chars, total 21 after ATR-
    full_code = payload + signature
    
    # Split into 5 groups of 4-5 chars
    part1 = full_code[0:4]
    part2 = full_code[4:8]
    part3 = full_code[8:12]
    part4 = full_code[12:16]
    part5 = full_code[16:21]
    
    serial = f"ATR-{part1}-{part2}-{part3}-{part4}-{part5}"
    
    return serial


def validate_serial_number(serial: str, hardware_id: str) -> Tuple[bool, str, dict]:
    """
    Validate serial number.
    
    Returns:
        (is_valid, message, info_dict)
    """
    from datetime import datetime
    
    try:
        # Remove dashes and validate format
        serial_clean = serial.replace("-", "").replace(" ", "").upper()
        
        if not serial_clean.startswith("ATR"):
            return False, "Invalid serial format", {}
        
        serial_clean = serial_clean[3:]  # Remove ATR prefix
        
        if len(serial_clean) != 21:
            return False, f"Serial number incorrect length (expected 21, got {len(serial_clean)})", {}
        
        # Extract components (13 char payload + 8 char signature = 21 total)
        type_code = serial_clean[0]
        hw_part = serial_clean[1:5]
        tester_hash = serial_clean[5:9]
        expiry_part = serial_clean[9:13]
        provided_sig = serial_clean[13:21]  # 8 chars
        
        # Reconstruct payload
        payload = f"{type_code}{hw_part}{tester_hash}{expiry_part}"
        
        # Verify HMAC signature
        expected_sig = hmac.new(MASTER_KEY, payload.encode(), hashlib.sha256).hexdigest()[:8].upper()
        
        if provided_sig != expected_sig:
            return False, "Invalid serial number (signature mismatch)", {}
        
        # Check hardware binding
        if hardware_id[:4] != hw_part:
            return False, "Hardware mismatch - serial is bound to different machine", {}
        
        # Decode license type
        type_map = {'T': 'trial', 'P': 'personal', 'R': 'professional', 'E': 'enterprise'}
        license_type = type_map.get(type_code, 'unknown')
        
        # Decode expiry
        expiry_date = None
        if expiry_part != "PERM":
            try:
                days_since_epoch = base36_decode(expiry_part)
                expiry_timestamp = days_since_epoch * 86400
                expiry_date = datetime.fromtimestamp(expiry_timestamp)
                
                if datetime.now() > expiry_date:
                    return False, f"License expired on {expiry_date.strftime('%Y-%m-%d')}", {
                        'license_type': license_type,
                        'expiry_date': expiry_date,
                        'expired': True
                    }
            except:
                pass
        
        info = {
            'license_type': license_type,
            'expiry_date': expiry_date,
            'hardware_id': hardware_id,
            'expired': False,
        }
        
        return True, "Valid license", info
        
    except Exception as e:
        return False, f"Validation error: {str(e)}", {}


def base36_encode(number: int) -> str:
    """Encode number to base36"""
    if number == 0:
        return '0'
    
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    
    while number:
        number, remainder = divmod(number, 36)
        result = alphabet[remainder] + result
    
    return result


def base36_decode(string: str) -> int:
    """Decode base36 string to number"""
    return int(string, 36)


def encrypt_activation_data(data: str) -> str:
    """Simple XOR encryption for activation data storage"""
    key = MASTER_KEY
    encrypted = bytearray()
    
    for i, byte in enumerate(data.encode('utf-8')):
        encrypted.append(byte ^ key[i % len(key)])
    
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_activation_data(encrypted: str) -> str:
    """Decrypt activation data"""
    try:
        key = MASTER_KEY
        encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
        decrypted = bytearray()
        
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key[i % len(key)])
        
        return decrypted.decode('utf-8')
    except:
        return None
