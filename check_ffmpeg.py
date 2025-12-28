"""Check running ffmpeg process and output file"""

import psutil
import os
from datetime import datetime

print("=== CHECKING FFMPEG PROCESSES ===\n")

for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        if proc.info["name"] and "ffmpeg" in proc.info["name"].lower():
            print(f"Process: {proc.info['name']} (PID: {proc.info['pid']})")
            cmdline = proc.info["cmdline"]
            if cmdline:
                print("Command line:")
                for i, arg in enumerate(cmdline):
                    print(f"  [{i}] {arg}")

                # Find output file (last argument that's a file path)
                for i in range(len(cmdline) - 1, -1, -1):
                    arg = cmdline[i]
                    if (
                        arg
                        and not arg.startswith("-")
                        and ("." in arg or "\\" in arg or "/" in arg)
                    ):
                        if os.path.exists(arg):
                            size_mb = os.path.getsize(arg) / (1024 * 1024)
                            mtime = datetime.fromtimestamp(os.path.getmtime(arg))
                            print(f"\n📁 Output file: {arg}")
                            print(f"   Size: {size_mb:.2f} MB")
                            print(f"   Last modified: {mtime}")
                            break
            print()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

print("\n=== CHECKING VSPIPE PROCESSES ===\n")

for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        if proc.info["name"] and "vspipe" in proc.info["name"].lower():
            print(f"Process: {proc.info['name']} (PID: {proc.info['pid']})")
            cmdline = proc.info["cmdline"]
            if cmdline:
                print("Command line:")
                for i, arg in enumerate(cmdline):
                    print(f"  [{i}] {arg}")
            print()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
