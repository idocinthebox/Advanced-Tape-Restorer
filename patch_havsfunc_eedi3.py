"""
Patch havsfunc.py to use CPU EEDI3 instead of non-existent EEDI3CL
This enables GPU acceleration for NNEDI3 (via nnedi3cl) while using CPU for EEDI3
"""

import os
import shutil

havsfunc_path = r"C:\Users\CWT\AppData\Roaming\Python\Python313\site-packages\havsfunc.py"
backup_path = havsfunc_path + ".backup"

print(f"Patching {havsfunc_path}...")
print()

# Restore from backup if it exists
if os.path.exists(backup_path):
    print("Restoring from backup first...")
    shutil.copy(backup_path, havsfunc_path)
    print(f"✓ Restored from {backup_path}")
else:
    print("Creating backup...")
    shutil.copy(havsfunc_path, backup_path)
    print(f"✓ Created backup: {backup_path}")

print()

# Read the file
with open(havsfunc_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace EEDI3CL references
changes_made = 0

for i, line in enumerate(lines):
    # Line ~185: eedi3 = partial(core.eedi3m.EEDI3CL, alpha=alpha, beta=beta, gamma=gamma, nrad=nrad, mdis=mdis, vcheck=vcheck, device=device)
    if 'eedi3 = partial(core.eedi3m.EEDI3CL, alpha=alpha' in line:
        lines[i] = line.replace('core.eedi3m.EEDI3CL', 'core.eedi3m.EEDI3').replace(', device=device', '')
        changes_made += 1
        print(f"✓ Patched line {i+1}: Replaced EEDI3CL with EEDI3, removed device parameter")
    
    # Line ~1616: eedi3 = partial(core.eedi3m.EEDI3CL, field=field, planes=planes, mdis=EdiMaxD, device=device, **eedi3_args)
    elif 'eedi3 = partial(core.eedi3m.EEDI3CL, field=field' in line:
        lines[i] = line.replace('core.eedi3m.EEDI3CL', 'core.eedi3m.EEDI3').replace(', device=device', '')
        changes_made += 1
        print(f"✓ Patched line {i+1}: Replaced EEDI3CL with EEDI3, removed device parameter")

# Write the patched file
with open(havsfunc_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print()
if changes_made > 0:
    print(f"✓ Successfully patched {changes_made} line(s) in havsfunc.py!")
    print()
    print("Result: QTGMC now uses GPU nnedi3cl + CPU eedi3 (hybrid mode)")
else:
    print("⚠ No EEDI3CL references found (may already be patched)")
print()
print(f"To restore original: copy {backup_path} to {havsfunc_path}")
