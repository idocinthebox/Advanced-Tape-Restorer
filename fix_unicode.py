"""Fix Unicode arrows in vapoursynth_engine.py"""

with open(r'C:\Advanced Tape Restorer v4.0\core\vapoursynth_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all Unicode arrows with ASCII
content = content.replace('→', '->')

with open(r'C:\Advanced Tape Restorer v4.0\core\vapoursynth_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed all Unicode arrows (→ -> ->)")
