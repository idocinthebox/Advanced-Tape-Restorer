"""
Example: Using Custom Cache Locations
Demonstrates how to configure and use custom cache directories
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_config  # noqa: E402
from core.frame_cache import FrameCache  # noqa: E402
from core.resumable_processor import ResumableProcessor  # noqa: E402


def example_1_using_config():
    """Example 1: Set cache location once, use everywhere"""
    print("=== Example 1: Global Configuration ===\n")

    # Configure cache location once
    config = get_config()
    config.set_cache_dir("./my_cache")
    config.set_cache_max_size_gb(20.0)
    config.set_checkpoint_dir("./my_checkpoints")

    # Show configuration
    config.print_config()

    # Now all FrameCache instances will use this location
    cache1 = FrameCache()
    print(f"\nCache 1 using: {cache1.cache_dir}")

    cache2 = FrameCache()
    print(f"Cache 2 using: {cache2.cache_dir}")

    print("\n[OK] Both caches use the configured location!")


def example_2_override_in_code():
    """Example 2: Override cache location for specific use case"""
    print("\n\n=== Example 2: Override in Code ===\n")

    # Use default/configured location
    default_cache = FrameCache()
    print(f"Default cache: {default_cache.cache_dir}")

    # Override for specific use case
    temp_cache = FrameCache(cache_dir="./temp_cache")
    print(f"Temp cache: {temp_cache.cache_dir}")

    print("\n[OK] Can mix default and custom locations!")


def example_3_resumable_processor():
    """Example 3: Configure checkpoint location"""
    print("\n\n=== Example 3: Resumable Processor ===\n")

    # Create processor with default/configured location
    processor1 = ResumableProcessor(
        job_id="video_001",
        input_file=Path("input.mp4"),
        output_file=Path("output.mp4"),
    )
    print(f"Processor 1 checkpoints: {processor1.checkpoint_dir}")

    # Create processor with custom location
    processor2 = ResumableProcessor(
        job_id="video_002",
        input_file=Path("input2.mp4"),
        output_file=Path("output2.mp4"),
        checkpoint_dir=Path("./project_checkpoints"),
    )
    print(f"Processor 2 checkpoints: {processor2.checkpoint_dir}")

    print("\n[OK] Processors can use different checkpoint locations!")


def example_4_environment_variables():
    """Example 4: Using environment variables"""
    print("\n\n=== Example 4: Environment Variables ===\n")

    import os

    # Check if environment variable is set
    env_cache = os.getenv("TAPE_RESTORER_CACHE_DIR")
    env_checkpoint = os.getenv("TAPE_RESTORER_CHECKPOINT_DIR")

    if env_cache:
        print(f"Environment cache override: {env_cache}")
    else:
        print("No environment cache override")
        print("To set: export TAPE_RESTORER_CACHE_DIR=/path/to/cache")

    if env_checkpoint:
        print(f"Environment checkpoint override: {env_checkpoint}")
    else:
        print("No environment checkpoint override")
        print("To set: export TAPE_RESTORER_CHECKPOINT_DIR=/path/to/checkpoints")

    # Create cache - will use env var if set, otherwise config
    cache = FrameCache()
    print(f"\nActual cache location: {cache.cache_dir}")


def example_5_per_project_cache():
    """Example 5: Per-project cache setup"""
    print("\n\n=== Example 5: Per-Project Cache ===\n")

    # Get current project directory
    project_dir = Path(__file__).parent.parent
    print(f"Project directory: {project_dir}")

    # Create project-specific cache
    project_cache_dir = project_dir / "cache"
    cache = FrameCache(cache_dir=project_cache_dir)

    print(f"Project cache: {cache.cache_dir}")
    print("\n[OK] Each project can have its own cache!")


def example_6_cache_on_different_drive():
    """Example 6: Store cache on faster/larger drive"""
    print("\n\n=== Example 6: Cache on Different Drive ===\n")

    # Example: Use SSD for cache (adjust path to your system)
    # This example uses a relative path, but you can use absolute paths
    # like "D:/FastCache" on Windows or "/mnt/ssd/cache" on Linux

    config = get_config()

    print("To use a different drive:")
    print('  config.set_cache_dir("D:/FastCache")  # Windows')
    print('  config.set_cache_dir("/mnt/ssd/cache")  # Linux')

    print("\nCurrent configuration:")
    print(f"  Cache: {config.get_cache_dir()}")
    print(f"  Max size: {config.get_cache_max_size_gb()} GB")


def example_7_cache_stats():
    """Example 7: Monitor cache usage"""
    print("\n\n=== Example 7: Cache Statistics ===\n")

    cache = FrameCache()

    # Add some test data
    cache.set("test_1", {"data": "example 1"})
    cache.set("test_2", {"data": "example 2"})
    cache.set("test_3", {"data": "example 3"})

    # Get stats
    stats = cache.get_stats()
    print(f"Total items: {stats['total_items']}")
    print(f"Cache size: {stats['size_mb']:.2f} MB")
    print(f"Max size: {stats['max_size_mb']:.0f} MB")
    print(f"Hit rate: {stats['hit_rate']:.1%}")

    # Or print formatted stats
    cache.print_stats()


if __name__ == "__main__":
    print("=" * 60)
    print("Custom Cache Location Examples")
    print("=" * 60)

    try:
        # Run all examples
        example_1_using_config()
        example_2_override_in_code()
        example_3_resumable_processor()
        example_4_environment_variables()
        example_5_per_project_cache()
        example_6_cache_on_different_drive()
        example_7_cache_stats()

        print("\n" + "=" * 60)
        print("[OK] All examples completed successfully!")
        print("=" * 60)

        print("\nNext steps:")
        print("  1. Configure your cache location:")
        print("     python core/config.py set-cache 'D:/MyCache'")
        print("\n  2. View configuration:")
        print("     python core/config.py")
        print("\n  3. See full guide:")
        print("     Open CACHE_CONFIGURATION_GUIDE.md")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
