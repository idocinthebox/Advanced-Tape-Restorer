# GFPGAN Checkpoint System - User Guide

## Overview
Advanced Tape Restorer v4.1 now supports **automatic checkpoint saving** for GFPGAN face enhancement jobs. This means if your restoration is interrupted (crash, disk full, manual stop), you can resume exactly where you left off.

## How It Works

### Automatic Checkpoint Saving
- Checkpoints are saved automatically every **50 frames**
- Each checkpoint stores:
  - Current frame number
  - Total frames processed
  - Processing settings
  - Job status (running, paused, completed)
- No manual intervention needed

### Disk Space Monitoring
- Checks available space every 50 frames
- Pauses automatically if disk space drops below 5GB
- Shows clear warnings with exact space requirements
- Prevents the "508GB crash" scenario

### Resume on Startup
- App automatically detects incomplete jobs on launch
- Shows dialog listing all interrupted jobs with progress
- Options:
  - **Resume** - Continue from last saved frame
  - **Discard** - Delete checkpoint and start fresh
  - **Discard All** - Remove all checkpoints

### Manual Resume
If you close the startup dialog:
1. Load the original video file
2. Enable GFPGAN in AI Tools tab
3. Click "Start Processing"
4. The app will automatically detect the checkpoint and resume

## Checkpoint Storage

### Location
```
%LOCALAPPDATA%\Advanced_Tape_Restorer\checkpoints\
```

Example:
```
C:\Users\YourName\AppData\Local\Advanced_Tape_Restorer\checkpoints\
```

### Filename Format
```
gfpgan_<hash>.checkpoint.json
```

Example:
```
gfpgan_a3f8e2b19c4d.checkpoint.json
```

The hash is derived from your video file path to uniquely identify each job.

## Checkpoint Status Types

### Running
- Job is currently being processed
- Checkpoint updated every 50 frames
- Automatically converts to "Paused" on app close

### Paused
- Job was interrupted (closed app, manual stop, disk space issue)
- Can be resumed at any time
- Progress preserved

### Completed
- Job finished successfully
- Checkpoint kept for reference
- Won't appear in resume dialog

### Failed
- Job encountered an error
- Can attempt to resume (may fail again)
- Check console log for error details

## Common Scenarios

### Scenario 1: App Crash During GFPGAN
**What happens:**
- Last checkpoint saved at frame 2,450 out of 5,000
- App crashes at frame 2,487

**Recovery:**
1. Restart app
2. Resume dialog shows: "Progress: 2,450/5,000 frames (49.0%)"
3. Click "Resume Selected"
4. Load original video and start processing
5. Processing continues from frame 2,451 (skips first 2,450 frames)

### Scenario 2: Disk Space Exhausted
**What happens:**
- Processing pauses at frame 1,800
- Console shows: "⚠️ Insufficient disk space - pausing"
- Checkpoint saved with status "Paused"

**Recovery:**
1. Free up disk space (or switch to alternative drive)
2. Restart app
3. Resume dialog shows the paused job
4. Click "Resume" and restart processing
5. Continues from frame 1,801

### Scenario 3: Manual Stop (Want to Resume Later)
**What happens:**
- Click "Stop" button at frame 3,200
- Checkpoint saved immediately
- Status: "Paused"

**Recovery:**
- Same as above - just resume when ready

### Scenario 4: Settings Changed
**What happens:**
- Started job with weight=0.5
- Stopped and want to restart with weight=0.7

**Action:**
1. Click "Discard" for the old checkpoint
2. Change GFPGAN weight to 0.7
3. Start processing fresh

## Best Practices

### 1. Let It Save Checkpoints
- Don't worry about checkpoint files
- They're small (~1KB each)
- Cleaned up automatically on completion

### 2. Use Alternative Drives for Large Videos
- Set GFPGAN temp directory in Settings → Performance & Cache
- Checkpoint system respects your custom temp directory
- D:\ drive recommended if C:\ is limited

### 3. Monitor Disk Space
- Pre-flight check shows estimated space requirements
- Periodic checks during processing
- Automatic pause if space runs low

### 4. Discard Old Checkpoints
- Use "Discard All" if you have many old jobs
- Checkpoints from completed jobs are safe to delete
- Frees up a few KB of space

## Troubleshooting

### Resume Not Working
**Symptom:** Clicking resume doesn't continue from saved frame

**Solutions:**
1. Ensure you load the **exact same video file**
2. Check GFPGAN is enabled in AI Tools tab
3. Verify checkpoint file exists in checkpoints directory
4. Check console log for errors

### Checkpoint Not Found
**Symptom:** No resume dialog on startup despite interruption

**Causes:**
- Checkpoint was manually deleted
- Different user account (checkpoints in %LOCALAPPDATA%)
- Job completed before interruption (checkpoint cleaned up)

### Wrong Frame Count
**Symptom:** Resume shows different total frames than expected

**Solution:**
- Different video file loaded (same name, different content)
- Video was edited/re-encoded since original job
- Discard checkpoint and start fresh

## Technical Details

### Checkpoint Contents
```json
{
  "job_id": "gfpgan_a3f8e2b19c4d",
  "input_file": "C:/Videos/tape_001.mp4",
  "output_file": "C:/Videos/restored/tape_001_restored.mp4",
  "total_frames": 5000,
  "processed_frames": 2450,
  "current_frame": 2450,
  "start_time": 1703720145.5,
  "last_update": 1703721245.8,
  "settings_hash": "abc123def456",
  "status": "paused",
  "error_message": null
}
```

### Performance Impact
- **Checkpoint save time:** <10ms (negligible)
- **Disk space:** 1-2KB per checkpoint
- **Resume overhead:** 1-2 seconds at startup

### Safety Features
- **Atomic writes:** Checkpoints written atomically (no partial corruption)
- **Hash verification:** Settings hash prevents incompatible resumes
- **Frame validation:** Checks output directory for already-processed frames
- **Graceful degradation:** Processing continues if checkpoint save fails

## See Also
- [Disk Space Management Guide](DISK_SPACE_FIX_V4.1.md)
- [GFPGAN Performance Optimizations](GFPGAN_OPTIMIZATIONS.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

## Version History
- **v4.1** - Initial checkpoint system implementation
  - Automatic checkpoint saving every 50 frames
  - Resume dialog on startup
  - Disk space monitoring
  - Compatible with existing SmartGFP optimizations

---

**Need Help?** Check the console log (View → Console) for detailed progress and error messages.
