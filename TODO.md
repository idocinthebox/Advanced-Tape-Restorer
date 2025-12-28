# Advanced Tape Restorer v4.0 - TODO List

## High Priority

### ✅ Real Capture Hardware Support (COMPLETED - Dec 25, 2025)
**Status:** Complete  
**Description:** Replaced mock implementation with real DirectShow device detection
**Implementation:**
- DirectShow device detection via FFmpeg
- Analog capture engine (HuffYUV, FFV1, Lagarith)
- DV/FireWire capture engine (stream copy)
- Crossbar input selection (Composite, S-Video, Component)
- Audio device matching
- GUI integration with "Refresh Devices" button
- Automatic fallback to mock devices if no hardware
- CLI test utilities

**Files Modified:**
- `capture.py` - Complete rewrite with real hardware support
- `gui/main_window.py` - Added device refresh method and imports
- `REAL_CAPTURE_HARDWARE_GUIDE.md` - Comprehensive documentation

**Testing:**
- ✅ Device detection without hardware (mock fallback)
- ✅ CLI test utilities work
- ⏳ Requires real hardware for full capture testing

---

## High Priority (Remaining)

### Debug Logging System
**Status:** Planned  
**Description:** Develop optional debug mode for troubleshooting user issues
**Requirements:**
- GUI toggle for "Debug Mode" (Settings menu or Expert Mode section)
- When enabled, add verbose logging:
  - Performance monitor: GPU initialization, metric updates
  - BM3D: Option values, sigma conversion, line generation
  - VapourSynth: Script generation steps, filter application
  - FFmpeg: Full command output
- Save debug logs to file: `%LOCALAPPDATA%\Advanced_Tape_Restorer\debug_TIMESTAMP.log`
- Add "Export Debug Log" button to GUI for easy sharing with developer

**Preserved Debug Code Locations:**
- `gui/performance_monitor.py` - GPU monitoring debug prints (removed but patterns saved)
- `core/vapoursynth_engine.py` - BM3D option tracking (removed but patterns saved)
- Can reference git history for exact debug statement locations

**User Story:** User encounters issue → Enables Debug Mode → Reproduces issue → Exports log → Sends to developer

---

## Medium Priority

### Capture Module Implementation
**Status:** Mock only  
**Description:** Implement real capture hardware support (DirectShow, DV over FireWire)

### Real-time Preview Improvements
**Status:** Working but basic  
**Description:** Add frame-accurate seeking, side-by-side comparison, waveform monitor

---

## Low Priority

### Additional AI Models
**Status:** Planning  
**Description:** Integrate AMT, DAIN, FILM for frame interpolation alternatives

---

## Completed (v3.3)

- ✅ BM3D GPU support with format conversion
- ✅ FPS detection and display
- ✅ GPU monitoring (utilization, temp, VRAM)
- ✅ Performance monitor real-time updates
- ✅ Version string correction (v3.2 → v3.3)
- ✅ **GPU Memory Management Optimization** (Dec 23, 2025)
  - VapourSynth memory limits (auto-calculated, prevents OOM)
  - Per-filter VRAM requirement estimation
  - Pre-flight VRAM checks with user warnings
  - Smart suggestions when insufficient VRAM detected
  - Comprehensive test suite (`test_gpu_memory_optimization.py`)
- ✅ **Editable File Path Fields** (Dec 24, 2025)
  - Input/output fields now accept manual typing and pasting
  - Visual validation feedback (green=valid, orange=warning)
  - Auto-removes quotes from pasted paths
  - Browse dialogs start in current file's directory

## Completed (v4.0)

- ✅ **Real Capture Hardware Support** (Dec 25, 2025)
  - DirectShow device detection via FFmpeg
  - Analog capture engine (VHS, Hi8, S-Video, Component)
  - DV/FireWire capture engine with stream copy
  - Crossbar input selection
  - Audio device matching
  - GUI integration with lazy loading
  - CLI test utilities
  - Comprehensive documentation (400+ lines)

- ✅ **PyTorch JIT Compilation** (Dec 25, 2025)
  - TorchScript compilation for 20-30% AI performance boost
  - Automatic model caching with disk persistence
  - Model-specific optimization strategies
  - Integration with GFPGAN face restoration
  - Integration with GPU accelerator
  - Fallback to eager mode on failure
  - Cache management CLI utilities

- ✅ **Threaded I/O Operations** (Dec 25, 2025)
  - Async file reading/writing with background threads
  - Parallel file operations (copy, verify, delete)
  - Buffered streaming for large files (8MB chunks)
  - Thread pool executor with configurable workers
  - Queue-based data flow to prevent blocking
  - Progress tracking for long operations
  - Automatic resource cleanup

- ✅ **Multi-GPU Support** (Dec 25, 2025)
  - Heterogeneous GPU detection (NVIDIA + AMD + Intel)
  - CUDA, ROCm, OpenCL, and hardware encoder detection
  - NVENC, AMF, Quick Sync encoder selection
  - AI workload scoring (best GPU for PyTorch models)
  - Encode workload scoring (best GPU for video encoding)
  - Intelligent workload distribution across multiple GPUs
  - Support for integrated GPUs (Ryzen APU, Intel iGPU)
  - Fallback to CPU when no GPU available
  - CLI utilities for GPU info and assignment testing

---

## Future: Pro Version (Commercial Development)

### Network Distributed Rendering
**Target:** Commercial restoration studios, post-production facilities  
**Goal:** 5-10x faster processing using render farms  
**Timeline:** 3-6 months after v4.0 release  
**Revenue Model:** $75/render-node/month subscription  

#### Phase 1 - Local Multi-Process (Foundation)
- ⏸️ Video segmentation engine (frame-accurate cuts with FFmpeg)
- ⏸️ Lossless segment concatenation (concat demuxer)
- ⏸️ Multiprocessing for same-machine parallelism
- ⏸️ Temporal overlap handling for AI models (RIFE, BasicVSR++)
- ⏸️ Audio sync validation (frame-accurate alignment)
- ⏸️ Test suite for reassembly logic
- ⏸️ Metadata preservation (timecodes, HDR, color space)

#### Phase 2 - LAN Rendering (Basic Network)
- ⏸️ REST API for job distribution (Flask/FastAPI)
  - POST /jobs, GET /jobs/{id}, DELETE /jobs/{id}
- ⏸️ Worker agent (runs on render nodes)
  - Auto-register with master
  - Process assigned segments
  - Report progress (frames/sec, ETA)
- ⏸️ Worker discovery on local network
- ⏸️ File transfer system (HTTP/SFTP with resumable uploads)
- ⏸️ Real-time progress aggregation (WebSocket/Socket.IO)
- ⏸️ Manual worker registration GUI
- ⏸️ Job queue management (FIFO, priority levels)

#### Phase 3 - Production Ready (Enterprise)
- ⏸️ Auto-discovery (Zeroconf/Bonjour)
- ⏸️ Secure authentication & TLS encryption
- ⏸️ Internet-capable with VPN support
- ⏸️ Dynamic load balancing (VRAM-aware job sizing)
  - Benchmark workers by GPU specs
  - Assign proportional segment sizes
- ⏸️ Fault tolerance & automatic job reassignment
  - Heartbeat monitoring (60s timeout)
  - Retry failed segments (3x max)
- ⏸️ Worker management dashboard
- ⏸️ Job priority levels (urgent/normal/batch)
- ⏸️ Cost tracking per render node
- ⏸️ Performance analytics & reporting
- ⏸️ AI model version synchronization (SHA256 verification)

**Commercial Features:**
- License server for node management
- Usage tracking & billing integration
- Priority support & SLA guarantees (24/7 for Enterprise)
- Custom deployment assistance
- Enterprise documentation & training
- Multi-tenant support (studio with multiple clients)
- API for third-party integrations
- S3/Azure Blob Storage support
- White-label branding option

**Pricing Tiers:**
- **Free:** Single-machine only
- **Pro:** $75/node/month - Network rendering + priority email support
- **Enterprise:** $150/node/month - Everything + 24/7 support + custom features

**Technical Challenges:**
1. Segment boundaries (AI temporal context) → 1-2 second overlap
2. AI model sync (version mismatches) → SHA256 + auto-download
3. Load balancing (GPU variance) → Benchmark first, proportional jobs
4. Fault tolerance (worker crashes) → Heartbeat + auto-reassign
5. Audio sync (frame alignment) → FFmpeg -ss/-t input seeking

**Development Resources:**
- Estimated: 600-900 hours total
- Team: Senior dev, UI dev, QA, tech writer
- Hardware: 5+ machine render farm for testing

---

**Last Updated:** December 25, 2025
