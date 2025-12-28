"""
Advanced Tape Restorer - Licensing System

Professional serial number and activation management.
Supports both hardware-bound (legacy) and email-based (Gumroad) licenses.
"""

from .license_manager import LicenseManager
from .activation_dialog import ActivationDialog, show_activation_dialog
from .gumroad_dialog import GumroadActivationDialog, show_gumroad_activation_dialog
from .models import LicenseInfo, ActivationStatus
from .revocation import RevocationList

__all__ = [
    'LicenseManager',
    'ActivationDialog',
    'show_activation_dialog',
    'GumroadActivationDialog',
    'show_gumroad_activation_dialog',
    'LicenseInfo',
    'ActivationStatus',
    'RevocationList',
]
