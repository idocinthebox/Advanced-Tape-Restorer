"""Fix QTGMC GPU fallback in Theatre Mode variants"""

# Read entire file
with open('core/vapoursynth_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace line 418 (bob variant) - 0-indexed so 417
lines[416] = '                    "",\n'
lines[417] = '                    "# Theatre Mode: Bob Deinterlacing (Double-Rate)",\n'
lines[418:419] = [
    '                    "# Try GPU acceleration first, fallback to CPU if unavailable",\n',
    '                    "try:",\n',
    "                    f\"    video = haf.QTGMC(video, {', '.join(args)}, opencl=True)  # GPU mode\",\n",
    '                    "    print(\'[Theatre Mode] Bob deinterlacing: GPU accelerated\')",\n',
    '                    "except:",\n',
    "                    f\"    video = haf.QTGMC(video, {', '.join(args)})  # CPU fallback\",\n",
    '                    "    print(\'[Theatre Mode] Bob deinterlacing: CPU mode\')",\n',
]

# Replace line 437 (standard variant) - adjust for new lines added (418->424 = +6 lines)
new_idx = 437 + 6 
lines[new_idx-3] = '                    "",\n'
lines[new_idx-2] = '                    "# Theatre Mode: Standard Progressive Deinterlacing",\n'
lines[new_idx-1:new_idx] = [
    '                    "# Try GPU acceleration first, fallback to CPU if unavailable",\n',
    '                    "try:",\n',
    "                    f\"    video = haf.QTGMC(video, {', '.join(args)}, opencl=True)  # GPU mode\",\n",
    '                    "    print(\'[Theatre Mode] Progressive deinterlacing: GPU accelerated\')",\n',
    '                    "except:",\n',
    "                    f\"    video = haf.QTGMC(video, {', '.join(args)})  # CPU fallback\",\n",
    '                    "    print(\'[Theatre Mode] Progressive deinterlacing: CPU mode\')",\n',
]

# Write back
with open('core/vapoursynth_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✓ Fixed Theatre Mode QTGMC GPU fallback for both bob and standard variants')
print('  - Line ~418: Bob deinterlacing now has GPU fallback')
print('  - Line ~437+: Standard progressive now has GPU fallback')
