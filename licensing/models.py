"""
Licensing data models
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ActivationStatus(Enum):
    """Activation status codes"""
    NOT_ACTIVATED = "not_activated"
    ACTIVATED = "activated"
    EXPIRED = "expired"
    INVALID = "invalid"
    HARDWARE_MISMATCH = "hardware_mismatch"


class LicenseType(Enum):
    """License types"""
    TRIAL = "trial"
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class LicenseInfo:
    """License information"""
    serial_number: str
    license_type: LicenseType
    activation_date: datetime
    expiry_date: Optional[datetime]
    hardware_id: str
    tester_id: str
    status: ActivationStatus
    
    def is_valid(self) -> bool:
        """Check if license is currently valid"""
        if self.status != ActivationStatus.ACTIVATED:
            return False
        
        if self.expiry_date and datetime.now() > self.expiry_date:
            return False
        
        return True
    
    def days_remaining(self) -> Optional[int]:
        """Get days remaining until expiration"""
        if not self.expiry_date:
            return None
        
        delta = self.expiry_date - datetime.now()
        return max(0, delta.days)
