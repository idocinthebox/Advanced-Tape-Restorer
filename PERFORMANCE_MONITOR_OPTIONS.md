# Performance Monitor Placement Options

## Current GUI Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Advanced Tape Restorer v3.3 (Window Title)                 │
├─────────────────────────────────────────────────────────────┤
│ File Selection Area (Input/Output)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tabs: [Capture][Input][Restoration][Advanced][AI][Output] │
│                                                             │
│         (Main content area - expandable)                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Start Processing]  [Stop Processing]                       │
│ Progress: 0.0%                        ETA: --:--:--         │
│ [█████████░░░░░░░░░░░░░░░░░░░░░░] (Progress Bar)            │
├─────────────────────────────────────────────────────────────┤
│ AI Model Dir: C:\...  [🤖 AI Models...] [Hide Console]      │
├─────────────────────────────────────────────────────────────┤
│ Console Output (collapsible, 120px fixed height)            │
│ > Advanced Tape Restorer v3.2 - Ready                       │
│ > Using modular architecture...                             │
└─────────────────────────────────────────────────────────────┘
```

---

## **Option 1: Status Bar (Bottom) - RECOMMENDED** ⭐

**Location:** New QStatusBar at the very bottom of window

```
┌─────────────────────────────────────────────────────────────┐
│ [File Selection, Tabs, Controls, Progress Bar - same]       │
├─────────────────────────────────────────────────────────────┤
│ AI Model Dir: C:\...  [🤖 AI Models...] [Hide Console]      │
├─────────────────────────────────────────────────────────────┤
│ Console Output (collapsible)                                │
├═════════════════════════════════════════════════════════════┤
│ 🖥️ CPU: 34% | 🎮 GPU: 87% | 💾 RAM: 2.3GB | ⚡ 45.2 fps     │ ← NEW
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Standard location (users expect status info here)
- Always visible, never scrolls away
- Doesn't interfere with existing layout
- Easy to implement (QStatusBar widget)
- Can show left-aligned metrics + right-aligned speed
- Minimal code changes

**Cons:**
- Takes up vertical space (20-25px)
- May be overlooked if console is expanded

**Implementation:**
```python
# In __init__:
self.status_bar = self.statusBar()
self._create_performance_widgets()

# Create labels:
self.cpu_label = QLabel("CPU: --")
self.gpu_label = QLabel("GPU: --")
self.ram_label = QLabel("RAM: --")
self.fps_label = QLabel("fps: --")

# Add to status bar
self.status_bar.addWidget(self.cpu_label)
self.status_bar.addWidget(self.gpu_label)
self.status_bar.addWidget(self.ram_label)
self.status_bar.addPermanentWidget(self.fps_label)
```

---

## **Option 2: Integrated with Progress Bar**

**Location:** Add metrics directly above/beside progress bar

```
┌─────────────────────────────────────────────────────────────┐
│ [Start Processing]  [Stop Processing]                       │
│ Progress: 45.2%        CPU: 34%  GPU: 87%  RAM: 2.3GB       │ ← Modified
│ [██████████████░░░░░░░░░░░░░░░░]  ETA: 00:15:32   45.2 fps  │ ← Modified
├─────────────────────────────────────────────────────────────┤
```

**Pros:**
- Contextually relevant (shows metrics during processing)
- Uses existing space efficiently
- Users naturally look here during processing
- Compact, grouped information

**Cons:**
- Only visible when progress bar is active
- May feel cluttered
- Limited space for detailed metrics
- Not visible during idle state

**Implementation:**
```python
# Modify _build_control_section():
progress_info = QHBoxLayout()
self.progress_label = QLabel("0.0%")
self.cpu_label = QLabel("CPU: --")  # NEW
self.gpu_label = QLabel("GPU: --")  # NEW
self.ram_label = QLabel("RAM: --")  # NEW
progress_info.addWidget(self.progress_label)
progress_info.addWidget(self.cpu_label)
progress_info.addWidget(self.gpu_label)
progress_info.addWidget(self.ram_label)
progress_info.addStretch()
progress_info.addWidget(self.eta_label)
```

---

## **Option 3: Dedicated Performance Tab**

**Location:** New tab in main tab widget

```
┌─────────────────────────────────────────────────────────────┐
│ Tabs: [Capture][Input][Restoration]...[Output][📊 Performance] │ ← NEW
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Real-Time Performance Monitoring                        │ │
│ │                                                         │ │
│ │ CPU Usage:    [███████░░░] 34%     (chart)            │ │
│ │ GPU Usage:    [█████████░] 87%     (chart)            │ │
│ │ RAM Usage:    [████░░░░░░] 2.3/8GB (chart)            │ │
│ │ VRAM Usage:   [██████░░░░] 4.2/8GB (chart)            │ │
│ │ Processing:   45.2 fps                                 │ │
│ │                                                         │ │
│ │ [Historical graphs with 60s timeline]                  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Detailed monitoring with graphs
- Doesn't crowd existing UI
- Can show historical data
- Professional look
- Can add GPU temperature, power usage, etc.

**Cons:**
- Not always visible (requires tab switch)
- Requires more implementation (charts/graphs)
- Most users won't check it regularly
- Overkill for quick monitoring

**Implementation:**
```python
def _build_performance_tab(self):
    """Build performance monitoring tab."""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # CPU group
    cpu_group = QGroupBox("CPU Usage")
    cpu_layout = QVBoxLayout()
    self.cpu_progress = QProgressBar()
    self.cpu_label = QLabel("0%")
    cpu_layout.addWidget(self.cpu_progress)
    cpu_layout.addWidget(self.cpu_label)
    cpu_group.setLayout(cpu_layout)
    layout.addWidget(cpu_group)
    
    # GPU group...
    # RAM group...
    # etc.
```

---

## **Option 4: Floating Panel (Dockable Widget)**

**Location:** Separate dockable window on right side

```
┌───────────────────────────────┬─────────────┐
│ Main Window                   │ Performance │
│ [All existing content]        │ ═════════════│
│                               │ CPU:   34%  │
│                               │ ███████░░░  │
│                               │             │
│                               │ GPU:   87%  │
│                               │ █████████░  │
│                               │             │
│                               │ RAM: 2.3GB  │
│                               │ ████░░░░░░  │
│                               │             │
│                               │ fps: 45.2   │
└───────────────────────────────┴─────────────┘
```

**Pros:**
- Always visible without taking main window space
- Can be hidden/shown on demand
- Can be floating or docked
- Professional multi-window interface
- Users can position where they want

**Cons:**
- Complex implementation (QDockWidget)
- May be overwhelming for casual users
- Requires window management
- Takes screen space

**Implementation:**
```python
# In __init__:
self.perf_dock = QDockWidget("Performance Monitor", self)
perf_widget = self._create_performance_widget()
self.perf_dock.setWidget(perf_widget)
self.addDockWidget(Qt.RightDockWidgetArea, self.perf_dock)
```

---

## **Option 5: Top Status Panel (Above Tabs)**

**Location:** Between file selection and tabs

```
┌─────────────────────────────────────────────────────────────┐
│ Input File: C:\video.avi    Output File: C:\restored.mp4    │
├═════════════════════════════════════════════════════════════┤
│ 🖥️ CPU: 34% | 🎮 GPU: 87% | 💾 RAM: 2.3GB | ⚡ 45.2 fps     │ ← NEW
├─────────────────────────────────────────────────────────────┤
│  Tabs: [Capture][Input][Restoration][Advanced][AI][Output]  │
│         (Main content area)                                  │
└─────────────────────────────────────────────────────────────┘
```

**Pros:**
- Prominent position (always seen)
- Doesn't interfere with bottom controls
- Clear separation from other elements

**Cons:**
- Pushes content down (loses vertical space)
- May be distracting during configuration
- Not contextually near processing controls

---

## **Option 6: Overlay on Progress Bar (During Processing Only)**

**Location:** Floating overlay that appears during processing

```
┌─────────────────────────────────────────────────────────────┐
│ [Start Processing]  [Stop Processing]                       │
│ Progress: 45.2%                        ETA: 00:15:32         │
│ [██████████████░░░░░░░░░░░░░░░░]                            │
│ ┌───────────────────────────────────┐                       │
│ │ 🖥️ CPU: 34% | 🎮 GPU: 87% 🔥 75°C │ ← Floating overlay   │
│ │ 💾 RAM: 2.3GB | ⚡ 45.2 fps       │                       │
│ └───────────────────────────────────┘                       │
├─────────────────────────────────────────────────────────────┤
```

**Pros:**
- Only appears when relevant (during processing)
- Doesn't permanently consume space
- Eye-catching and contextual

**Cons:**
- May obscure other elements
- Complex implementation (custom painting)
- Not visible during idle
- May be jarring when it appears

---

## **Comparison Matrix**

| Option | Visibility | Implementation | Space Usage | User Impact | Recommended |
|--------|-----------|----------------|-------------|-------------|-------------|
| **1. Status Bar** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **YES** |
| 2. Progress Bar | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Maybe |
| 3. Performance Tab | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | No |
| 4. Floating Panel | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | No |
| 5. Top Panel | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Maybe |
| 6. Overlay | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | No |

---

## **My Recommendation: Option 1 (Status Bar)** ⭐

**Why:**
1. **Standard UX Pattern** - Users expect system info in status bar
2. **Always Visible** - Never hidden behind tabs or scrolling
3. **Easy Implementation** - 2-3 hours of work, minimal complexity
4. **Non-Intrusive** - Doesn't disrupt existing workflow
5. **Qt Native** - Built-in QStatusBar widget with good support
6. **Professional** - Matches industry standards (VS Code, PyCharm, etc.)

**Proposed Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🖥️ CPU: 34%  |  🎮 GPU: 87% (75°C)  |  💾 RAM: 2.3/16GB    │ ← Left side
│                                        ⚡ 45.2 fps  CUDA ✓ │ ← Right side
└─────────────────────────────────────────────────────────────┘
```

**What to Monitor:**
- **CPU Usage %** - Overall system load
- **GPU Usage %** - CUDA/video card load
- **GPU Temperature** - Thermal monitoring (if available)
- **RAM Usage** - Current / Total memory
- **VRAM Usage** - GPU memory (if available)
- **Processing Speed** - fps during encoding
- **GPU Status** - "CUDA ✓" or "CPU Mode" indicator

**Update Frequency:**
- **500ms intervals** during processing (responsive but not CPU-heavy)
- **2000ms intervals** during idle (minimal overhead)

---

## **Alternative: Hybrid Approach (Option 1 + 2)**

**Best of both worlds:**
1. **Status Bar** - Always shows real-time system stats (CPU/GPU/RAM)
2. **Progress Area** - Shows processing-specific metrics (fps, GPU temp) only during active encoding

```
┌─────────────────────────────────────────────────────────────┐
│ [Start Processing]  [Stop Processing]                       │
│ Progress: 45.2%    🎮 GPU: 87% 🔥 75°C    ETA: 00:15:32     │ ← Processing metrics
│ [██████████████░░░░░░░░░░░░░░░░]         ⚡ 45.2 fps        │
├─────────────────────────────────────────────────────────────┤
│ Console / AI Model buttons...                               │
├═════════════════════════════════════════════════════════════┤
│ 🖥️ CPU: 34%  |  💾 RAM: 2.3/16GB  |  CUDA Available ✓      │ ← Always visible
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- **Status bar** provides ambient awareness (always-on system monitoring)
- **Progress area** shows task-specific details during active work
- Total space: ~25px at bottom (status bar only)

---

## Next Steps

**Which option would you prefer?**

1. **Option 1** - Status bar only (simple, recommended)
2. **Option 2** - Integrated with progress bar
3. **Option 5** - Top status panel
4. **Hybrid (1+2)** - Status bar + enhanced progress area
5. **Custom** - Your own idea?

I can implement any of these in 2-4 hours depending on complexity. Let me know your preference and I'll start coding!
