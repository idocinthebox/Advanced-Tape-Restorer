# Cache Configuration Guide

## Overview

Advanced Tape Restorer v3.0 allows you to configure where cache files and checkpoints are stored. This is useful if you want to:

- Store cache on a faster SSD
- Use a drive with more available space
- Keep cache separate from your project files
- Share cache between multiple projects
- Store cache on a network drive

## Configuration Priority

The system checks for cache location in this order (highest priority first):

1. **Environment Variables** - Set system-wide or per-session
2. **Configuration File** - Persistent user preferences
3. **Code Parameters** - Explicitly specified in code
4. **Default Values** - `./cache` and `./checkpoints`

## Method 1: Environment Variables (Recommended for Development)

Set environment variables to temporarily override cache locations without changing config files.

### Windows (Command Prompt)
```cmd
set TAPE_RESTORER_CACHE_DIR=D:\MyCache
set TAPE_RESTORER_CHECKPOINT_DIR=D:\MyCheckpoints
python your_script.py
```

### Windows (PowerShell)
```powershell
$env:TAPE_RESTORER_CACHE_DIR="D:\MyCache"
$env:TAPE_RESTORER_CHECKPOINT_DIR="D:\MyCheckpoints"
python your_script.py
```

### Linux/Mac (Terminal)
```bash
export TAPE_RESTORER_CACHE_DIR="/mnt/ssd/cache"
export TAPE_RESTORER_CHECKPOINT_DIR="/mnt/ssd/checkpoints"
python your_script.py
```

### Permanent Environment Variables

**Windows:**
1. Open System Properties → Advanced → Environment Variables
2. Add new User/System variables:
   - `TAPE_RESTORER_CACHE_DIR` = `D:\MyCache`
   - `TAPE_RESTORER_CHECKPOINT_DIR` = `D:\MyCheckpoints`

**Linux/Mac (add to ~/.bashrc or ~/.zshrc):**
```bash
export TAPE_RESTORER_CACHE_DIR="/mnt/ssd/cache"
export TAPE_RESTORER_CHECKPOINT_DIR="/mnt/ssd/checkpoints"
```

---

## Method 2: Configuration File (Recommended for Permanent Settings)

The configuration file `tape_restorer_config.json` stores persistent user preferences.

### Using Command Line

```bash
# View current configuration
python core/config.py

# Set cache directory
python core/config.py set-cache "D:\MyCache"

# Set checkpoint directory
python core/config.py set-checkpoint "D:\MyCheckpoints"

# Set maximum cache size (in GB)
python core/config.py set-size 20

# Reset to defaults
python core/config.py reset
```

### Using Python Code

```python
from core.config import get_config

# Get config instance
config = get_config()

# Set custom cache directory
config.set_cache_dir("D:/MyCache")

# Set maximum cache size
config.set_cache_max_size_gb(20.0)

# Set cache TTL (time-to-live in hours)
config.set_cache_ttl_hours(48)

# Set checkpoint directory
config.set_checkpoint_dir("D:/MyCheckpoints")

# View current configuration
config.print_config()
```

### Manual Configuration File

Create or edit `tape_restorer_config.json`:

```json
{
    "cache_dir": "D:/MyCache",
    "cache_max_size_gb": 20.0,
    "cache_ttl_hours": 48,
    "checkpoint_dir": "D:/MyCheckpoints"
}
```

---

## Method 3: Code Parameters (For Specific Use Cases)

Override cache location in code when creating cache instances:

```python
from core.frame_cache import FrameCache
from core.resumable_processor import ResumableProcessor

# Custom cache directory
cache = FrameCache(
    cache_dir="./custom_cache",
    max_size_gb=15.0,
    ttl_hours=72
)

# Custom checkpoint directory
processor = ResumableProcessor(
    job_id="my_job",
    input_file="input.mp4",
    output_file="output.mp4",
    checkpoint_dir="./custom_checkpoints"
)
```

---

## Use Cases

### 1. Store Cache on Faster SSD

```bash
# Set cache to SSD for better performance
python core/config.py set-cache "D:\SSD_Cache"
```

### 2. Store Cache on Larger Drive

```bash
# Move cache to drive with more space
python core/config.py set-cache "E:\LargeCache"
python core/config.py set-size 100  # Allow 100 GB
```

### 3. Network Storage for Team Collaboration

```bash
# Use network drive (slower, but shared)
python core/config.py set-cache "\\server\shared\tape_restorer_cache"
```

### 4. Temporary Directory (Auto-Cleanup)

```python
import tempfile
from core.frame_cache import FrameCache

# Use system temp directory
temp_cache = tempfile.mkdtemp(prefix="tape_restorer_")
cache = FrameCache(cache_dir=temp_cache)
```

### 5. Per-Project Cache

Keep cache separate for each project:

```python
from pathlib import Path
from core.frame_cache import FrameCache

project_dir = Path(__file__).parent
cache = FrameCache(cache_dir=project_dir / "cache")
```

---

## Checking Current Configuration

### Command Line
```bash
python core/config.py
```

**Output:**
```
=== Advanced Tape Restorer Configuration ===
Cache Directory: D:\MyCache
Cache Max Size: 20.0 GB
Cache TTL: 48 hours
Checkpoint Directory: D:\MyCheckpoints

Config file: C:\...\tape_restorer_config.json
```

### Python Code
```python
from core.config import get_config

config = get_config()
print(f"Cache Directory: {config.get_cache_dir()}")
print(f"Max Size: {config.get_cache_max_size_gb()} GB")
print(f"TTL: {config.get_cache_ttl_hours()} hours")
```

---

## Configuration File Location

The config file is stored in the current working directory:
- **File:** `tape_restorer_config.json`
- **Format:** JSON

To use a different location, you can:
1. Set the working directory before running
2. Copy the config file to your project directory
3. Modify `CacheConfig.CONFIG_FILE` in `core/config.py`

---

## Cache Management

### View Cache Stats

```python
from core.frame_cache import FrameCache

cache = FrameCache()
cache.print_stats()
```

**Output:**
```
=== Cache Statistics ===
Hits: 1523
Misses: 127
Hit rate: 92.3%
Items: 234
Size: 2,145.3 / 10,240.0 MB
```

### Clear Cache

```python
from core.frame_cache import FrameCache

cache = FrameCache()
cache.clear()  # Deletes all cached files
```

### Manual Cleanup

```bash
# Delete cache directory
rm -rf ./cache

# Or on Windows
rmdir /s /q cache
```

---

## Best Practices

### 1. **Use SSD for Cache**
   - Significantly faster read/write speeds
   - Set via: `python core/config.py set-cache "D:\SSD_Cache"`

### 2. **Allocate Sufficient Space**
   - Video processing generates large cache files
   - Recommended: 20-50 GB for typical projects
   - Set via: `python core/config.py set-size 50`

### 3. **Adjust TTL Based on Usage**
   - Development: Short TTL (24 hours)
   - Production: Longer TTL (72+ hours)
   - Set via: `config.set_cache_ttl_hours(72)`

### 4. **Monitor Cache Size**
   - Check regularly: `cache.print_stats()`
   - Clear old cache if space is limited

### 5. **Use Environment Variables for CI/CD**
   - Easy to configure per-environment
   - No code changes needed

---

## Troubleshooting

### Cache Directory Not Found

**Problem:** Error creating cache directory

**Solution:**
```python
from pathlib import Path

# Ensure parent directories exist
cache_dir = Path("D:/MyCache")
cache_dir.mkdir(parents=True, exist_ok=True)
```

### Permission Denied

**Problem:** Cannot write to cache directory

**Solution:**
1. Check directory permissions
2. Run with administrator/sudo if needed
3. Use a directory you have write access to

### Cache Not Being Used

**Problem:** Cache always shows 0% hit rate

**Solution:**
1. Check that version strings match
2. Verify cache_dir is correct
3. Check TTL hasn't expired all entries

### Environment Variable Not Working

**Problem:** Environment variable not recognized

**Solution:**
1. Restart terminal/IDE after setting
2. Verify with: `echo %TAPE_RESTORER_CACHE_DIR%` (Windows) or `echo $TAPE_RESTORER_CACHE_DIR` (Linux/Mac)
3. Check spelling is exact

---

## Examples

### Complete Configuration Example

```python
from core.config import get_config
from core.frame_cache import FrameCache
from core.resumable_processor import ResumableProcessor

# Configure directories
config = get_config()
config.set_cache_dir("D:/FastCache")
config.set_checkpoint_dir("D:/Checkpoints")
config.set_cache_max_size_gb(50.0)
config.set_cache_ttl_hours(72)

# Create cache (automatically uses config)
cache = FrameCache()  # Uses D:/FastCache

# Create processor (automatically uses config)
processor = ResumableProcessor(
    job_id="video_001",
    input_file="input.mp4",
    output_file="output.mp4"
)  # Uses D:/Checkpoints

# Or override for specific use case
special_cache = FrameCache(cache_dir="./temp_cache")
```

### Multi-Project Setup

```python
import os
from pathlib import Path
from core.frame_cache import FrameCache

# Get project-specific cache based on current directory
project_name = Path.cwd().name
cache_dir = Path(f"D:/ProjectCaches/{project_name}")

cache = FrameCache(cache_dir=cache_dir)
print(f"Using cache: {cache_dir}")
```

---

## Related Documentation

- **Frame Cache:** `core/frame_cache.py` - Cache implementation
- **Config Manager:** `core/config.py` - Configuration system
- **Resumable Processing:** `core/resumable_processor.py` - Checkpoint system
- **Quick Reference:** `OPTIMIZATION_QUICK_REFERENCE.md` - Performance tips

---

## Summary

**Quick Setup (Most Users):**
```bash
# Set once, use forever
python core/config.py set-cache "D:\MyCache"
python core/config.py set-size 50
```

**Advanced Setup (Developers):**
```bash
# Use environment variables
export TAPE_RESTORER_CACHE_DIR="/mnt/ssd/cache"
export TAPE_RESTORER_CHECKPOINT_DIR="/mnt/ssd/checkpoints"
```

**Per-Use Override:**
```python
cache = FrameCache(cache_dir="./custom_location")
```

That's it! Your cache is now configured and ready to use. 🚀
