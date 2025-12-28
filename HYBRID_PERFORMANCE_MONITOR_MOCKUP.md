# Hybrid Performance Monitor - Visual Mockup

## Full Window Layout with Hybrid Monitoring

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║ Advanced Tape Restorer v3.3 - Professional Video Restoration (Optimized)     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  Input File:  C:\Videos\VHS_Family_1995.avi                     [Browse...]  ║
║               1620x1080, 29.97fps, Interlaced (TFF), 45:30 duration          ║
║                                                                               ║
║  Output File: C:\Restored\VHS_Family_1995_Restored.mp4          [Browse...]  ║
║               3240x2160 (4x upscale), Progressive, H.264                      ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌──────────────────────────────────────────────────────────────────────┐   ║
║   │ 🎬 Capture  │ 📥 Input  │ ✨ Restoration │ ⚙️  Advanced │ 🤖 AI Tools │   ║
║   └──────────────────────────────────────────────────────────────────────┘   ║
║                                                                               ║
║   ┌─ Restoration Settings ─────────────────────────────────────────────┐     ║
║   │                                                                     │     ║
║   │  Deinterlacing:     [QTGMC ▼]  Quality: [Medium ▼]               │     ║
║   │  AI Upscaling:      [RealESRGAN 4x ✓]                             │     ║
║   │  Frame Interpolation: [RIFE 2x ✓]                                  │     ║
║   │  Noise Reduction:   [25] Sharpen: [15]                            │     ║
║   │  Color Correction:  [✓] Stabilization: [✓]                        │     ║
║   │                                                                     │     ║
║   └─────────────────────────────────────────────────────────────────────┘     ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌────────────────────────────────────────────────────────────────────────┐ ║
║   │  [▶ Start Processing]                    [⏹ Stop Processing]          │ ║
║   └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                               ║
║   ╔═══════════════════════════════════════════════════════════════════════╗ ║
║   ║  Progress: 45.2%     🎮 GPU: 87% 🔥 75°C     VRAM: 4.2/8.0 GB      ║ ║
║   ║  [████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░]                 ║ ║
║   ║  ETA: 00:15:32      Frame: 68,445/151,200      ⚡ 72.3 fps           ║ ║
║   ╚═══════════════════════════════════════════════════════════════════════╝ ║
║                                     ▲                                         ║
║                                     │                                         ║
║                        ENHANCED PROGRESS AREA (Shows during processing)      ║
║                        • Real-time GPU metrics (usage, temp, VRAM)           ║
║                        • Frame count and fps                                 ║
║                        • Contextual to active encoding                       ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  AI Model Dir: C:\Users\...\Advanced_Tape_Restorer\ai_models                 ║
║  [🤖 AI Models...]  [Hide Console]                                           ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  ┌─ Console Output ──────────────────────────────────────────────────────┐   ║
║  │ > Advanced Tape Restorer v3.3 - Ready                                 │   ║
║  │ > GPU Detected: NVIDIA GeForce RTX 5070 Laptop (8.0 GB VRAM)         │   ║
║  │ > CUDA 12.1 available - GPU acceleration enabled                      │   ║
║  │ > Loading AI model: RealESRGAN-x4plus.pth (64.3 MB)                  │   ║
║  │ > VapourSynth script generated: 927 lines                             │   ║
║  │ > FFmpeg encoding started: H.264, CRF 18, preset medium               │   ║
║  │ > Processing frame 68445/151200 (45.2%) - GPU utilization optimal     │   ║
║  └────────────────────────────────────────────────────────────────────────┘   ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🖥️ CPU: 34%  │  💾 RAM: 5.2/32.0 GB  │  ⚙️ Threads: 16  │  CUDA: Available ✓ ║
╚═══════════════════════════════════════════════════════════════════════════════╝
                                    ▲
                                    │
                               STATUS BAR (Always visible)
                               • System-wide metrics (CPU, RAM)
                               • Not processing-specific
                               • Ambient awareness
```

---

## State 1: IDLE (No Processing Active)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  [▶ Start Processing]                    [⏹ Stop Processing] (disabled)       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Progress: 0.0%                                            ETA: --:--:--      ║
║  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]              ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🖥️ CPU: 12%  │  💾 RAM: 3.1/32.0 GB  │  ⚙️ Threads: 16  │  CUDA: Available ✓ ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Key Points:**
- Enhanced progress area shows minimal info (just progress bar + ETA)
- Status bar still shows system metrics (idle state)
- No GPU-specific metrics shown (not needed when idle)
- Clean, uncluttered appearance

---

## State 2: PROCESSING (CPU Mode - No GPU)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  [▶ Start Processing] (disabled)         [⏹ Stop Processing]                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Progress: 23.8%                            Frame: 35,985/151,200             ║
║  [███████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]                ║
║  ETA: 01:23:45                                               ⚡ 128.5 fps     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🖥️ CPU: 94%  │  💾 RAM: 8.7/32.0 GB  │  ⚙️ Threads: 16/16  │  Mode: CPU     ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Key Points:**
- Enhanced progress area shows frame count and fps (CPU encoding)
- Status bar highlights high CPU usage (94%)
- "Mode: CPU" indicator (no GPU acceleration)
- Faster fps typical of CPU-only encoding

---

## State 3: PROCESSING (GPU Mode - With AI Upscaling)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  [▶ Start Processing] (disabled)         [⏹ Stop Processing]                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Progress: 45.2%     🎮 GPU: 87% 🔥 75°C     VRAM: 4.2/8.0 GB  💧 Fan: 78%   ║
║  [████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]                ║
║  ETA: 00:15:32      Frame: 68,445/151,200      ⚡ 72.3 fps                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🖥️ CPU: 34%  │  💾 RAM: 5.2/32.0 GB  │  ⚙️ Threads: 8/16  │  CUDA: Active ⚡ ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Key Points:**
- **Enhanced progress area (top section):**
  - GPU usage: 87% (heavy AI processing)
  - GPU temperature: 75°C with fire emoji
  - VRAM usage: 4.2/8.0 GB
  - Fan speed: 78% (optional, if available)
  - Frame progress: 68,445/151,200
  - Processing speed: 72.3 fps (slower due to AI upscaling)
  
- **Status bar (bottom):**
  - CPU usage: 34% (lower, GPU doing heavy work)
  - RAM: 5.2 GB
  - Threads: 8/16 active (some idle since GPU processing)
  - "CUDA: Active ⚡" with lightning bolt

---

## State 4: PROCESSING (GPU Thermal Throttling Warning)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  [▶ Start Processing] (disabled)         [⏹ Stop Processing]                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Progress: 67.3%  🎮 GPU: 92% 🔥🔥 83°C ⚠️  VRAM: 7.1/8.0 GB  💧 Fan: 98%   ║
║  [██████████████████████████████████████░░░░░░░░░░░░░░░░░░░░]                ║
║  ETA: 00:08:12      Frame: 101,657/151,200    ⚡ 58.7 fps (throttled)        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🖥️ CPU: 28%  │  💾 RAM: 6.8/32.0 GB  │  ⚙️ Threads: 6/16  │  CUDA: Throttled⚠️║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Key Points:**
- **Visual warnings when GPU is stressed:**
  - Double fire emoji (🔥🔥) at 83°C
  - Warning triangle (⚠️) appears
  - VRAM near capacity (7.1/8.0 GB)
  - Fan at max (98%)
  - fps shows "(throttled)" indicator
  
- **Status bar shows:**
  - "CUDA: Throttled ⚠️" warning

---

## State 5: PROCESSING (High VRAM Pressure)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  [▶ Start Processing] (disabled)         [⏹ Stop Processing]                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Progress: 89.1%  🎮 GPU: 95% 🔥 78°C     VRAM: 7.8/8.0 GB ⚠️  💧 Fan: 89%   ║
║  [██████████████████████████████████████████████████░░░░░░░░]                ║
║  ETA: 00:02:35      Frame: 134,724/151,200    ⚡ 64.2 fps                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ 🖥️ CPU: 31%  │  💾 RAM: 11.2/32.0 GB  │  ⚙️ Threads: 8/16  │  CUDA: Active ⚡ ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**Key Points:**
- VRAM at 7.8/8.0 GB (97.5% full) shows warning ⚠️
- Still processing normally, just flagging potential issue
- RAM usage also increased to 11.2 GB

---

## Color-Coded Status Indicators

### GPU Temperature Colors:
```
50°C-65°C:  🎮 GPU: 65% 🌡️  65°C  (Normal, gray)
66°C-75°C:  🎮 GPU: 78% 🔥 72°C  (Warm, orange)
76°C-85°C:  🎮 GPU: 89% 🔥🔥 81°C ⚠️  (Hot, red + warning)
86°C+:      🎮 GPU: 95% 🔥🔥🔥 89°C ⚠️ CRITICAL  (Critical)
```

### VRAM Usage Colors:
```
0-60%:      VRAM: 3.2/8.0 GB (40%)  (Normal, gray)
61-85%:     VRAM: 6.1/8.0 GB (76%)  (High, yellow)
86-95%:     VRAM: 7.4/8.0 GB ⚠️  (Warning, orange)
96-100%:    VRAM: 7.9/8.0 GB ⚠️ CRITICAL  (Critical, red)
```

### CPU Usage Colors:
```
0-50%:      🖥️ CPU: 34%  (Normal, gray)
51-75%:     🖥️ CPU: 68%  (Busy, yellow)
76-90%:     🖥️ CPU: 84%  (High, orange)
91-100%:    🖥️ CPU: 97% ⚠️  (Maxed, red)
```

---

## Benefits of Hybrid Approach

### 1. Context-Aware Information
```
IDLE:        Status bar only (no clutter)
PROCESSING:  Progress area + status bar (full metrics)
```

### 2. Clear Information Hierarchy
```
TOP SECTION (Progress Area):      Task-specific, temporary
  ↓ What's happening right now
  ↓ GPU load, temperature, VRAM
  ↓ Frame progress, fps

BOTTOM SECTION (Status Bar):      System-wide, permanent
  ↓ Overall system health
  ↓ CPU, RAM, thread count
  ↓ GPU mode indicator
```

### 3. Visual Priority
```
HIGH PRIORITY:    Progress area (larger, centered)
                  Shows critical encoding metrics

AMBIENT:          Status bar (subtle, bottom)
                  Always available, never intrusive
```

### 4. Space Efficiency
```
VERTICAL SPACE USED:
  - Progress area: 80px (3 lines, only during processing)
  - Status bar: 22px (always visible)
  - Total: 102px (~7% of 900px window height)
```

---

## Implementation Details

### Enhanced Progress Area Components:
```python
# Line 1: GPU metrics (horizontal layout)
self.gpu_usage_label = QLabel("🎮 GPU: --")
self.gpu_temp_label = QLabel("🔥 --°C")
self.vram_label = QLabel("VRAM: --/-- GB")
self.fan_label = QLabel("💧 Fan: --%")

# Line 2: Progress bar (existing)
self.progressbar = QProgressBar()

# Line 3: Details
self.frame_label = QLabel("Frame: --/--")
self.fps_label = QLabel("⚡ -- fps")
```

### Status Bar Components:
```python
# Left side (system metrics)
self.cpu_label = QLabel("🖥️ CPU: --")
self.ram_label = QLabel("💾 RAM: --/-- GB")
self.threads_label = QLabel("⚙️ Threads: --")

# Right side (GPU mode)
self.cuda_status = QLabel("CUDA: --")
```

### Update Frequencies:
```python
# Enhanced progress area (during processing)
UPDATE_INTERVAL_PROCESSING = 500  # 500ms = 2x per second

# Status bar (always)
UPDATE_INTERVAL_IDLE = 2000       # 2000ms = 0.5x per second
```

---

## Summary

**Hybrid = Best of Both Worlds**

✅ **Always-visible system monitoring** (status bar)  
✅ **Detailed task metrics** (progress area, when needed)  
✅ **Clean UI** (no clutter when idle)  
✅ **Context-aware** (shows what matters)  
✅ **Minimal space** (102px total = 7% of window)  
✅ **Professional appearance** (industry standard)

**Total implementation time: 3-4 hours**

Would you like me to implement this hybrid approach?
