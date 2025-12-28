"""
Performance profiler for Advanced Tape Restorer
Analyzes import times and startup bottlenecks
"""

import sys
import time
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))


def profile_import(module_name, description=""):
    """Profile the import time of a module."""
    start = time.perf_counter()
    try:
        __import__(module_name)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        status = "OK"
        return elapsed, status
    except ImportError as e:
        elapsed = (time.perf_counter() - start) * 1000
        status = f"FAIL: {e}"
        return elapsed, status


def main():
    """Profile all major imports."""
    print("=" * 70)
    print("Advanced Tape Restorer - Startup Performance Profile")
    print("=" * 70)
    print()

    imports_to_test = [
        ("sys", "Standard library - system"),
        ("pathlib", "Standard library - paths"),
        ("json", "Standard library - JSON"),
        ("PySide6.QtWidgets", "Qt GUI framework"),
        ("PySide6.QtCore", "Qt core"),
        ("PySide6.QtGui", "Qt GUI utilities"),
        ("numpy", "Numerical processing (if installed)"),
        ("core.video_analyzer", "Video analysis module"),
        ("core.processor", "Video processor"),
        ("core.vapoursynth_engine", "VapourSynth engine"),
        ("gui.main_window", "Main GUI window"),
        ("gui.splash_screen", "Splash screen"),
        ("ai_models.model_manager", "AI model manager"),
    ]

    results = []
    total_time = 0

    for module, desc in imports_to_test:
        print(f"Importing {module:40} ", end="", flush=True)
        elapsed, status = profile_import(module, desc)
        total_time += elapsed

        if status == "OK":
            print(f"[{status}] {elapsed:7.2f}ms - {desc}")
        else:
            print(f"[{status}]")

        results.append((module, desc, elapsed, status))

    print()
    print("=" * 70)
    print(f"Total import time: {total_time:.2f}ms ({total_time/1000:.2f}s)")
    print("=" * 70)
    print()

    # Sort by time
    results.sort(key=lambda x: x[2], reverse=True)

    print("Top 5 slowest imports:")
    for i, (module, desc, elapsed, status) in enumerate(results[:5], 1):
        if status == "OK":
            print(f"  {i}. {module:35} {elapsed:7.2f}ms ({elapsed/total_time*100:5.1f}%)")

    print()
    print("Recommendations:")
    print("  - Heavy imports (>100ms) should be lazy-loaded")
    print("  - GUI imports should be deferred until window creation")
    print("  - AI model loading should happen on-demand")
    print()


if __name__ == "__main__":
    main()
