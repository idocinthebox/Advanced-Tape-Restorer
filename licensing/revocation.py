"""
License revocation management
"""

import json
from pathlib import Path
from typing import List, Set


class RevocationList:
    """Manages revoked license keys"""
    
    def __init__(self, revocation_file: Path = None):
        """
        Initialize revocation list.
        
        Args:
            revocation_file: Path to revoked_keys.json
        """
        if revocation_file is None:
            # Look in app directory first, then user data
            app_dir = Path(__file__).parent.parent
            revocation_file = app_dir / "revoked_keys.json"
            
            if not revocation_file.exists():
                # Try user data directory
                user_data = Path.home() / ".idocinthebox"
                revocation_file = user_data / "revoked_keys.json"
        
        self.revocation_file = Path(revocation_file)
        self._revoked_keys: Set[str] = set()
        self.load()
    
    def load(self):
        """Load revoked keys from file"""
        if self.revocation_file.exists():
            try:
                with self.revocation_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._revoked_keys = set(data.get('revoked', []))
            except Exception as e:
                print(f"Warning: Failed to load revocation list: {e}")
                self._revoked_keys = set()
    
    def save(self):
        """Save revoked keys to file"""
        self.revocation_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'revoked': sorted(list(self._revoked_keys)),
            'count': len(self._revoked_keys)
        }
        
        with self.revocation_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def is_revoked(self, license_key: str) -> bool:
        """Check if license key is revoked"""
        # Normalize key
        normalized = license_key.upper().replace(" ", "").replace("-", "")
        full_key = license_key.upper()
        
        return normalized in self._revoked_keys or full_key in self._revoked_keys
    
    def revoke(self, license_key: str, reason: str = None):
        """Revoke a license key"""
        normalized = license_key.upper().replace(" ", "")
        self._revoked_keys.add(normalized)
        self.save()
        
        print(f"✓ Revoked: {license_key}")
        if reason:
            print(f"  Reason: {reason}")
    
    def unrevoke(self, license_key: str):
        """Remove license key from revocation list"""
        normalized = license_key.upper().replace(" ", "")
        if normalized in self._revoked_keys:
            self._revoked_keys.remove(normalized)
            self.save()
            print(f"✓ Unrevoked: {license_key}")
        else:
            print(f"Key not in revocation list: {license_key}")
    
    def get_revoked_list(self) -> List[str]:
        """Get list of all revoked keys"""
        return sorted(list(self._revoked_keys))
    
    def count(self) -> int:
        """Get count of revoked keys"""
        return len(self._revoked_keys)


def create_default_revocation_file():
    """Create empty revocation file in app directory"""
    app_dir = Path(__file__).parent.parent
    revocation_file = app_dir / "revoked_keys.json"
    
    if not revocation_file.exists():
        data = {
            'revoked': [],
            'count': 0,
            'note': 'Add revoked license keys here. App checks this file at startup.'
        }
        
        with revocation_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Created revocation file: {revocation_file}")
    else:
        print(f"Revocation file already exists: {revocation_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m licensing.revocation init         # Create empty revocation file")
        print("  python -m licensing.revocation list         # List revoked keys")
        print("  python -m licensing.revocation revoke KEY   # Revoke a key")
        print("  python -m licensing.revocation unrevoke KEY # Unrevoke a key")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        create_default_revocation_file()
    elif command == 'list':
        rev_list = RevocationList()
        keys = rev_list.get_revoked_list()
        if keys:
            print(f"Revoked keys ({len(keys)}):")
            for key in keys:
                print(f"  {key}")
        else:
            print("No revoked keys")
    elif command == 'revoke' and len(sys.argv) >= 3:
        key = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) >= 4 else None
        rev_list = RevocationList()
        rev_list.revoke(key, reason)
    elif command == 'unrevoke' and len(sys.argv) >= 3:
        key = sys.argv[2]
        rev_list = RevocationList()
        rev_list.unrevoke(key)
    else:
        print("Invalid command")
        sys.exit(1)
