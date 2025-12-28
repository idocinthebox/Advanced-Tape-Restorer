"""Monitor the running FFmpeg encoding process"""

import psutil
import os
import time
from datetime import datetime

# Configuration
FFMPEG_PID = 27196
OUTPUT_FILE = "C:/interlaced video/TreysBirth2.mp4"
CHECK_INTERVAL = 10  # seconds

print("=" * 70)
print("FFMPEG ENCODING MONITOR")
print("=" * 70)
print(f"Monitoring: {OUTPUT_FILE}")
print(f"FFmpeg PID: {FFMPEG_PID}")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

try:
    process = psutil.Process(FFMPEG_PID)
    print(f"Process found: {process.name()} (PID: {FFMPEG_PID})")
    print(f"Status: {process.status()}")
    print()
except psutil.NoSuchProcess:
    print(f"ERROR: Process {FFMPEG_PID} not found!")
    print("The encoding may have already finished.")
    exit(1)

last_size = 0
stall_count = 0
start_time = time.time()

try:
    while True:
        # Check if process still exists
        if not psutil.pid_exists(FFMPEG_PID):
            print("\n" + "=" * 70)
            print("ENCODING COMPLETE!")
            print("=" * 70)
            print(f"FFmpeg process has finished.")
            print(f"Output file: {OUTPUT_FILE}")
            if os.path.exists(OUTPUT_FILE):
                size_gb = os.path.getsize(OUTPUT_FILE) / (1024**3)
                print(f"Final size: {size_gb:.2f} GB")
            print(f"Total time: {(time.time() - start_time) / 60:.1f} minutes")
            break

        # Get current file size
        if os.path.exists(OUTPUT_FILE):
            current_size = os.path.getsize(OUTPUT_FILE)
            size_gb = current_size / (1024**3)

            # Calculate progress
            if last_size > 0:
                delta = current_size - last_size
                speed_mbps = (delta / CHECK_INTERVAL) / (1024**2)

                # Check if stalled
                if delta == 0:
                    stall_count += 1
                    if stall_count >= 6:  # 60 seconds of no change
                        print(
                            f"\nWARNING: File hasn't grown in {stall_count * CHECK_INTERVAL} seconds!"
                        )
                        print("The process may be finishing up or stalled.")
                else:
                    stall_count = 0

                # Get CPU usage
                try:
                    proc = psutil.Process(FFMPEG_PID)
                    cpu = proc.cpu_percent(interval=1)
                    status_icon = "WORKING" if cpu > 50 else "IDLE"

                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"Size: {size_gb:.2f} GB | "
                        f"Speed: {speed_mbps:.2f} MB/s | "
                        f"CPU: {cpu:.0f}% | "
                        f"Status: {status_icon}"
                    )
                except psutil.NoSuchProcess:
                    break

            last_size = current_size
        else:
            print(f"Output file not found: {OUTPUT_FILE}")

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\n\nMonitoring stopped by user.")
    print(f"Note: FFmpeg process is still running (PID {FFMPEG_PID})")
    print("The encoding will continue in the background.")

print("\n" + "=" * 70)
print("Monitor session ended.")
print("=" * 70)
