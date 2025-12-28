"""
License management and activation system
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from .crypto_utils import (
    generate_hardware_id,
    validate_serial_number,
    validate_license_gumroad,
    encrypt_activation_data,
    decrypt_activation_data
)
from .models import LicenseInfo, ActivationStatus, LicenseType
from .revocation import RevocationList


class LicenseManager:
    """Manages license activation and validation"""
    
    def __init__(self, app_data_dir: Path = None):
        """
        Initialize license manager.
        
        Args:
            app_data_dir: Directory for license storage
        """
        if app_data_dir is None:
            app_data_dir = Path.home() / ".idocinthebox"
        
        self.app_data_dir = Path(app_data_dir)
        self.license_file = self.app_data_dir / "activation.lic"
        self.hardware_id = generate_hardware_id()
        self.revocation_list = RevocationList()
        
        # Ensure directory exists
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_hardware_id(self) -> str:
        """Get current machine's hardware ID"""
        return self.hardware_id
    
    def is_activated(self) -> bool:
        """Check if application is activated"""
        license_info = self.load_license()
        
        if license_info is None:
            return False
        
        return license_info.is_valid()
    
    def get_license_info(self) -> Optional[LicenseInfo]:
        """Get current license information"""
        return self.load_license()
    
    def activate(self, serial_number: str, tester_id: str) -> Tuple[bool, str]:
        """
        Activate application with serial number.
        
        Returns:
            (success, message)
        """
        # Validate serial number
        is_valid, message, info = validate_serial_number(serial_number, self.hardware_id)
        
        if not is_valid:
            return False, message
        
        # Create license info
        license_type_map = {
            'trial': LicenseType.TRIAL,
            'personal': LicenseType.PERSONAL,
            'professional': LicenseType.PROFESSIONAL,
            'enterprise': LicenseType.ENTERPRISE,
        }
        
        license_info = LicenseInfo(
            serial_number=serial_number,
            license_type=license_type_map.get(info['license_type'], LicenseType.TRIAL),
            activation_date=datetime.now(),
            expiry_date=info.get('expiry_date'),
            hardware_id=self.hardware_id,
            tester_id=tester_id,
            status=ActivationStatus.ACTIVATED,
        )
        
        # Save license
        self.save_license(license_info)
        
        days_msg = ""
        if license_info.expiry_date:
            days = license_info.days_remaining()
            days_msg = f" ({days} days remaining)"
        
        return True, f"Activated successfully as {info['license_type']}{days_msg}"
    
    def activate_gumroad(self, email: str, license_key: str, is_trial: bool = False) -> Tuple[bool, str]:
        """
        Activate with Gumroad-style email + license key (platform-agnostic).
        
        Args:
            email: Customer email
            license_key: License key from Gumroad
            is_trial: Whether this is a trial activation
        
        Returns:
            (success, message)
        """
        # Get revoked keys list
        revoked_keys = self.revocation_list.get_revoked_list()
        
        # Check if revoked first
        if self.revocation_list.is_revoked(license_key):
            return False, "This license has been revoked. Contact support@idocinthebox.com"
        
        # Validate license
        is_valid, message = validate_license_gumroad(email, license_key, revoked_keys)
        
        if not is_valid:
            return False, message
        
        # Extract license type from message
        license_type_str = message.split()[1] if len(message.split()) > 1 else 'personal'
        
        license_type_map = {
            'trial': LicenseType.TRIAL,
            'personal': LicenseType.PERSONAL,
            'professional': LicenseType.PROFESSIONAL,
            'enterprise': LicenseType.ENTERPRISE,
        }
        
        license_type = license_type_map.get(license_type_str, LicenseType.PERSONAL)
        
        # Set expiry for trial
        expiry_date = None
        if is_trial or license_type == LicenseType.TRIAL:
            from datetime import timedelta
            expiry_date = datetime.now() + timedelta(days=7)
        
        # Create license info
        license_info = LicenseInfo(
            serial_number=license_key,
            license_type=license_type,
            activation_date=datetime.now(),
            expiry_date=expiry_date,
            hardware_id="",  # No hardware binding for Gumroad
            tester_id=email,
            status=ActivationStatus.ACTIVATED,
        )
        
        # Save license
        self.save_license(license_info)
        
        days_msg = ""
        if license_info.expiry_date:
            days = license_info.days_remaining()
            days_msg = f" ({days} days remaining)"
        
        return True, f"Activated successfully as {license_type_str}{days_msg}"
    
    def deactivate(self) -> bool:
        """Deactivate current license"""
        if self.license_file.exists():
            self.license_file.unlink()
            return True
        return False
    
    def save_license(self, license_info: LicenseInfo):
        """Save license information (encrypted)"""
        data = {
            'serial_number': license_info.serial_number,
            'license_type': license_info.license_type.value,
            'activation_date': license_info.activation_date.isoformat(),
            'expiry_date': license_info.expiry_date.isoformat() if license_info.expiry_date else None,
            'hardware_id': license_info.hardware_id,
            'tester_id': license_info.tester_id,
            'status': license_info.status.value,
        }
        
        json_data = json.dumps(data)
        encrypted = encrypt_activation_data(json_data)
        
        self.license_file.write_text(encrypted, encoding='utf-8')
    
    def load_license(self) -> Optional[LicenseInfo]:
        """Load and validate license information"""
        if not self.license_file.exists():
            return None
        
        try:
            encrypted = self.license_file.read_text(encoding='utf-8')
            decrypted = decrypt_activation_data(encrypted)
            
            if decrypted is None:
                return None
            
            data = json.loads(decrypted)
            
            # Verify hardware ID
            if data['hardware_id'] != self.hardware_id:
                return LicenseInfo(
                    serial_number=data['serial_number'],
                    license_type=LicenseType(data['license_type']),
                    activation_date=datetime.fromisoformat(data['activation_date']),
                    expiry_date=datetime.fromisoformat(data['expiry_date']) if data['expiry_date'] else None,
                    hardware_id=data['hardware_id'],
                    tester_id=data['tester_id'],
                    status=ActivationStatus.HARDWARE_MISMATCH,
                )
            
            license_info = LicenseInfo(
                serial_number=data['serial_number'],
                license_type=LicenseType(data['license_type']),
                activation_date=datetime.fromisoformat(data['activation_date']),
                expiry_date=datetime.fromisoformat(data['expiry_date']) if data['expiry_date'] else None,
                hardware_id=data['hardware_id'],
                tester_id=data['tester_id'],
                status=ActivationStatus(data['status']),
            )
            
            # Check if expired
            if license_info.expiry_date and datetime.now() > license_info.expiry_date:
                license_info.status = ActivationStatus.EXPIRED
            
            return license_info
            
        except Exception as e:
            print(f"Error loading license: {e}")
            return None
