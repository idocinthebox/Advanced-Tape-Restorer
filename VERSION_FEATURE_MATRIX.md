# Advanced Tape Restorer - Version Feature Matrix

## Version Overview

| Version | Status | Release Target | Pricing Model | Target User |
|---------|--------|----------------|---------------|-------------|
| **v4.1** | Released | December 2025 | FREE (MIT) | Enthusiasts, hobbyists |
| **v4.2 Early Supporter** | Limited Time | Q2 2026 | **$45 one-time** 🎉 | Early adopters |
| **v4.2** | Planned | Q2 2026 | $150 one-time | Professionals, small studios |
| **v5.0 Pro** | Planned | Q3-Q4 2026 | $75/node/month | Commercial studios |
| **v5.0 Enterprise** | Planned | Q4 2026 | $150/node/month | Large post-production houses |

---

## v4.1 - FREE (Community Edition) - CURRENT RELEASE

### Core Restoration Features
✅ QTGMC deinterlacing (7 quality presets)
✅ Field order auto-detection (TFF/BFF/Progressive)
✅ Temporal denoise (FFT3D, KNLMeansCL, BM3D)
✅ Spatial denoise (RemoveGrain, MCTemporalDenoise)
✅ Sharpening filters (UnsharpMask, LSFmod)
✅ Color correction (auto levels, saturation, hue)
✅ Crop and resize with aspect ratio correction
✅ Deflicker and degrain filters

### AI Models (Basic)
✅ RealESRGAN 4x upscaling (GPU/CPU)
✅ RIFE 2x-4x frame interpolation
✅ BasicVSR++ 2x video upscaling
✅ SwinIR 2x/3x/4x upscaling
✅ ZNEDI3 2x upscaling
✅ GFPGAN face restoration
✅ DeOldify colorization

### ONNX/NPU Acceleration
✅ ONNX model conversion (98% compression)
✅ DirectML runtime (NPU + GPU + CPU)
✅ 40x speedup vs CPU inference
✅ Inference mode selection (Auto/PyTorch/TorchScript/ONNX)
✅ VRAM-based auto mode selection
✅ NPU offloading (frees 6-8GB GPU VRAM)

### Performance Features
✅ PyTorch JIT compilation (20-30% AI speedup)
✅ Threaded I/O (2-4x batch operations)
✅ Multi-GPU support (NVIDIA + AMD + Intel)
✅ Hardware encoder selection (NVENC, AMF, Quick Sync)
✅ Checkpoint/resume system

### Capture Hardware
✅ DirectShow device detection (analog capture cards)
✅ DV/FireWire capture support
✅ Analog input selection (Composite, S-Video, Component)
✅ Device lazy loading
✅ Mock mode for testing

### Output Formats
✅ H.264 (libx264, NVENC, AMF, Quick Sync)
✅ H.265/HEVC (libx265, NVENC HEVC, AMF HEVC)
✅ ProRes (all variants)
✅ DNxHD/DNxHR
✅ FFV1 (lossless archival)
✅ AV1 (experimental)

### GUI & UX
✅ PySide6 modern interface
✅ Restoration presets system
✅ Batch processing queue
✅ Real-time progress with ETA
✅ Preview window (before/after comparison)
✅ Settings persistence

### Support
✅ Community support (GitHub issues, discussions)
✅ Documentation and guides
✅ CLI test utilities

---

## v4.2 EARLY SUPPORTER EDITION ($45 one-time) - LIMITED TIME OFFER 🎉

**Special Launch Pricing for Initial Supporters!**

**Pricing:** $45 one-time payment (70% OFF regular price)
- **Lifetime software updates** for v4.2
- **Community support** (GitHub discussions, documentation)
- Same features as Standard Edition
- Limited availability: First 500 supporters OR until official v4.2 release
- After 1 year: Continue with community support (no additional fees)

**Licensing:** v4.2 uses dual licensing - v4.1 MIT components + proprietary v4.2 features. See [LICENSING_GUIDE.md](LICENSING_GUIDE.md) for details.

**What You Get:**
✅ All v4.2 features (same as $150 Standard Edition)
✅ Lifetime updates for v4.2 (bug fixes, improvements)
✅ Early access to beta versions
✅ Supporter badge in community forums
✅ Locked-in price (future v4.2 price increases don't affect you)

**What's Different from Standard:**
- Community support instead of 48h priority email
- No priority bug fixing (community queue)
- No direct feature requests

**Why This Offer?**
We're offering this steep discount to reward early supporters who believe in the project and help us gather feedback during development. Your support helps fund v4.2 development!

---

## v4.2 - STANDARD EDITION ($150 one-time) - PLANNED Q2 2026

**Pricing:** $150 one-time payment + 1 year priority support (then $75/year renewal OR community support)

### Professional AI Features (NEW)
☐ **Bundled ProPainter** - Integrated installation (currently requires external setup in v4.1)
☐ **CodeFormer** - Enhanced face restoration (alternative to GFPGAN)
☐ **Topaz-level denoise** - Premium AI denoising models
☐ **Smart color grading** - AI-powered auto white balance and color correction
☐ **Audio restoration** - AI noise reduction, declicking, hiss removal, equalization
☐ **Frame stabilization** - Motion tracking and video stabilization
☐ **Auto scene detection** - Intelligent scene boundary detection
☐ **Subtitle/caption extraction** - OCR from embedded VHS/DVD text
☐ **Whisper integration** - AI audio transcription and subtitling

### Professional Workflow Features (NEW)
☐ **Project management** - Multi-tape project organization
☐ **Client database** - Client tracking with notes and preferences
☐ **Job templates** - Save complete workflows as reusable templates
☐ **Batch presets** - Apply settings to multiple files at once
☐ **Quality control dashboard** - Metrics and validation tools
☐ **Metadata tagging system** - Custom tags and searchable library
☐ **Export presets for broadcast** - Industry-standard output profiles
☐ **Time tracking & invoicing** - Built-in billing tools

### Enhanced Capture Features (NEW)
☐ **Live preview with filters** - Real-time restoration preview during capture
☐ **Scene detection during capture** - Auto-segment tapes by scene
☐ **VBI/teletext decoding** - Extract hidden data from VHS tapes
☐ **Timecode extraction** - DV timecode parsing and validation
☐ **Dropped frame monitoring** - Real-time capture quality tracking
☐ **Auto-split by scene** - Automatic file splitting at scene changes

### Advanced UI/UX (NEW)
☐ **Custom dark/light themes** - Professional color schemes
☐ **Dockable panels** - Customizable workspace layouts
☐ **Split-screen preview** - Before/after comparison with A/B toggle
☐ **Waveform display** - Audio visualization and editing
☐ **Timeline scrubbing** - Frame-accurate navigation
☐ **Keyboard shortcuts** - Fully customizable hotkeys
☐ **Drag-and-drop everywhere** - Improved workflow efficiency
☐ **Recent projects** - Quick access to recent work

### Performance Enhancements (NEW)
☐ **CUDA stream optimization** - Better GPU utilization
☐ **Progressive rendering** - Show results while processing
☐ **Smart caching** - Intelligent cache management
☐ **Memory optimization** - Reduced RAM footprint for 4K
☐ **Faster preview generation** - Real-time preview improvements

### Priority Support
☐ **Email support** - 48-hour response time
☐ **Bug fix priority** - Your issues resolved first
☐ **Feature requests** - Direct input on roadmap
☐ **Early access** - Beta versions before public release
☐ **Video tutorials** - Exclusive professional training content
☐ **Quarterly feature updates** - New features every 3 months

### Cross-Platform (NEW)
☐ **Linux support** - Ubuntu 22.04+ and derivatives
☐ **macOS support** - Apple Silicon (M1/M2/M3) priority
☐ **Unified codebase** - Consistent experience across platforms

---

## v5.0 PRO - NETWORK DISTRIBUTED RENDERING ($75/node/month) - PLANNED Q3-Q4 2026

**Pricing:** $75 per render node per month (subscription)

### Everything in v4.2 Standard PLUS:

### Network Distributed Rendering (NEW)
☐ **Video segmentation engine** - Frame-accurate splitting
☐ **Lossless concatenation** - FFmpeg concat demuxer
☐ **Multi-machine processing** - 5-10x speedup with render farms
☐ **REST API** - Job distribution and management
☐ **Worker agent** - Runs on render nodes
☐ **Auto-discovery** - Zeroconf/Bonjour worker detection
☐ **Dynamic load balancing** - VRAM-aware job distribution
☐ **Fault tolerance** - Auto job reassignment on worker crash
☐ **Worker dashboard** - Real-time monitoring of all nodes
☐ **WebSocket progress** - Live aggregated progress tracking

### Enterprise Features (NEW)
☐ **Secure authentication** - TLS encryption for network traffic
☐ **VPN support** - Internet-capable distributed rendering
☐ **Job priority levels** - Urgent/normal/batch queue system
☐ **Cost tracking** - Per-node usage and billing metrics
☐ **Performance analytics** - Detailed rendering statistics
☐ **AI model synchronization** - Auto-deploy models to workers
☐ **Heartbeat monitoring** - Detect crashed workers instantly
☐ **Temporal overlap handling** - Context for RIFE/BasicVSR++
☐ **Audio sync validation** - Frame-accurate alignment checks

### Professional Studio Tools
☐ **Render farm templates** - Pre-configured worker profiles
☐ **GPU capability scoring** - Intelligent workload assignment
☐ **S3/Azure storage** - Cloud storage integration
☐ **Database for job history** - SQLite/PostgreSQL backend
☐ **Resumable file transfers** - HTTP/SFTP with resume support

### Support
☐ **Priority email support** - 48-hour response time
☐ **Quarterly feature updates** - New features every 3 months
☐ **Community forums** - Pro user discussions

---

## v5.0 ENTERPRISE - ENTERPRISE DISTRIBUTED RENDERING ($150/node/month) - PLANNED Q4 2026

**Pricing:** $150 per render node per month (subscription)

### Everything in v5.0 Pro PLUS:

### Enterprise Support (NEW)
☐ **24/7 phone support** - Round-the-clock technical assistance
☐ **Dedicated support engineer** - Direct line to senior engineers
☐ **Custom feature development** - Request bespoke features
☐ **On-premise license server** - Host licensing internally
☐ **Training & deployment** - On-site training and setup assistance
☐ **SLA guarantees** - 99.9% uptime commitment

### Enterprise Features (NEW)
☐ **Multi-tenant support** - Separate clients within one system
☐ **White-label branding** - Rebrand with your logo/colors
☐ **API for third-party integrations** - Connect to existing systems
☐ **Advanced security** - SSO, LDAP, Active Directory
☐ **Audit logging** - Complete activity tracking
☐ **Compliance tools** - HIPAA, GDPR, SOC2 support
☐ **Backup & disaster recovery** - Automated failover systems
☐ **Custom deployment** - Private cloud or on-premise
☐ **Priority feature roadmap** - Influence development direction

### Additional Resources
☐ **Enterprise documentation** - Detailed technical guides
☐ **Dedicated account manager** - Business relationship management
☐ **Annual training sessions** - On-site professional development
☐ **Architecture consulting** - Optimize your infrastructure

---

## Feature Comparison Table

| Feature | v4.1 FREE | v4.2 EARLY | v4.2 STANDARD | v5.0 PRO | v5.0 ENTERPRISE |
|---------|-----------|------------|---------------|----------|-----------------|
| **Price** | Free | $150 one-time | $75/node/month | $150/node/month |
| **Basic restoration** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AI upscaling** | ✅ Basic | ✅ Advanced | ✅ Advanced | ✅ Advanced | ✅ Advanced |
| **ONNX/NPU** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Capture hardware** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Batch processing** | ✅ Basic | ✅ Advanced | ✅ Advanced | ✅ Advanced | ✅ Advanced |
| **Project management** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Audio restoration** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Frame stabilization** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Scene detection** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Custom themes** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Cross-platform** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Network rendering** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Render farm** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Multi-machine** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **API integration** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **White-label** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Support** | Community | Community | 48h email | 48h email | 24/7 phone |
| **SLA** | No | No | No | No | 99.9% |

---

## Upgrade Paths

### From v4.1 (Free) → v4.2 Early Supporter
- One-time payment: **$45** (LIMITED TIME)
- Lifetime v4.2 updates
- Community support
- Upgrade to Standard later: Pay difference ($105) for priority support

### From v4.1 (Free) → v4.2 (Standard)
- One-time payment: **$150**
- Includes 1 year priority support
- Lifetime software updates
- Option to renew support at **$75/year** or use community support

### From v4.2 Early Supporter → v4.2 Standard
- Upgrade payment: **$105** (difference between $45 and $150)
- Adds 1 year priority support
- Option to renew support at **$75/year**

### From v4.2 (Standard) → v5.0 Pro
- Monthly subscription: **$75/node**
- Credit: First month 50% off ($37.50) for existing v4.2 customers
- Includes network rendering + priority support
- No long-term contract required

### From v5.0 Pro → v5.0 Enterprise
- Monthly subscription: **$150/node**
- Upgrade prorated monthly
- Includes 24/7 support + SLA + custom features

---

## Target User Profiles

### v4.1 FREE - Enthusiasts
- **Who:** Home users digitizing family tapes
- **Use case:** Occasional video restoration (5-10 tapes/year)
- **Technical level:** Beginner to intermediate
- **Hardware:** Consumer GPU, standard PC

### v4.2 EARLY SUPPORTER - Early Adopters
- **Who:** Tech-savvy users, enthusiasts ready to upgrade, beta testers
- **Use case:** Regular restoration work (20-100 tapes/year)
- **Technical level:** Intermediate
- **Hardware:** Mid-range GPU, decent PC
- **ROI:** Massive discount (70% off) for supporting development
- **Commitment:** Help test features, provide feedback, community support

### v4.2 STANDARD - Professionals
- **Who:** Freelance video editors, small production studios, archivists
- **Use case:** Regular restoration work (50-200 tapes/year)
- **Technical level:** Intermediate to advanced
- **Hardware:** Professional GPU, high-end PC
- **ROI:** Pays for itself after 1-2 client projects

### v5.0 PRO - Studios
- **Who:** Post-production houses, restoration studios
- **Use case:** High-volume work (500+ tapes/year)
- **Technical level:** Advanced, dedicated render farm
- **Hardware:** Multiple workstations/servers with GPUs
- **ROI:** 5-10x speed increase justifies subscription cost

### v5.0 ENTERPRISE - Enterprises
- **Who:** Large archives, broadcasters, major studios
- **Use case:** Industrial-scale restoration (1000s of tapes)
- **Technical level:** IT department, system integrators
- **Hardware:** Enterprise render farms, cloud infrastructure
- **ROI:** Mission-critical with SLA guarantees

---

## Development Timeline

| Version | Start | Release | Duration |
|---------|-------|---------|----------|
| v4.1 | Dec 2025 | Dec 2025 | ✅ Released |
| v4.2 | Jan 2026 | Q2 2026 | 4-6 months |
| v5.0 Pro | Apr 2026 | Q3-Q4 2026 | 6-9 months |
| v5.0 Enterprise | Jul 2026 | Q4 2026 | 3 months after Pro |

---

**Last Updated:** December 29, 2025  
**Document Version:** 1.0  
**Maintained by:** Advanced Tape Restorer Development Team
