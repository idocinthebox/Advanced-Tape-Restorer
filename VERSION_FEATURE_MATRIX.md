# Advanced Tape Restorer - Version Feature Matrix

## Version Overview

| Version | Status | Release Target | Pricing Model | Target User |
|---------|--------|----------------|---------------|-------------|
| **v4.0** | Released | December 2025 | FREE (MIT) | Enthusiasts, hobbyists |
| **v4.1 Early Supporter** | Limited Time | December 2025 | **$45 one-time** 🎉 | Early adopters |
| **v4.1** | Released | December 2025 | $150 one-time | Professionals, small studios |
| **v4.2** | Planned | Q2 2026 | $150 one-time + upgrades | Advanced professionals |
| **v5.0 Pro** | Planned | Q3-Q4 2026 | $75/node/month | Commercial studios |
| **v5.0 Enterprise** | Planned | Q4 2026 | $150/node/month | Large post-production houses |

---

## v4.0 - FREE (Community Edition) - CURRENT RELEASE

### Core Restoration Features
✅ QTGMC deinterlacing (7 quality presets)
✅ Field order auto-detection (TFF/BFF/Progressive)
✅ Temporal denoise (FFT3D, KNLMeansCL, BM3D)
✅ Spatial denoise (RemoveGrain, MCTemporalDenoise)
✅ Sharpening filters (UnsharpMask, LSFmod)
✅ Color correction (auto levels, saturation, hue)
✅ Crop and resize with aspect ratio correction
✅ Deflicker and degrain filters

### Performance Features
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

**Note:** v4.0 is perfect for basic VHS/tape restoration without AI. For professional AI upscaling, upgrade to v4.1.

---

## v4.1 EARLY SUPPORTER EDITION ($45 one-time) - LIMITED TIME OFFER 🎉

**Special Launch Pricing for Initial Supporters!**

**Pricing:** $45 one-time payment (70% OFF regular price)
- **Lifetime software updates** for v4.1
- **Community support** (GitHub discussions, documentation)
- Same features as v4.1 Standard Edition
- Limited availability: First 500 supporters OR until March 31, 2026
- After 1 year: Continue with community support (no additional fees)

**Licensing:** v4.1 uses dual licensing - v4.0 MIT components + proprietary v4.1 AI features. See [LICENSING_GUIDE.md](LICENSING_GUIDE.md) for details.

**What You Get:**
✅ All v4.1 AI features (same as $150 Standard Edition)
✅ Lifetime updates for v4.1 (bug fixes, improvements)
✅ Early access to beta versions
✅ Supporter badge in community forums
✅ Locked-in price (future v4.1 price increases don't affect you)

**What's Different from Standard:**
- Community support instead of 48h priority email
- No priority bug fixing (community queue)
- No direct feature requests

**Why This Offer?**
We're offering this steep discount to reward early supporters who believe in the project. Your support helps fund v4.2 development!

---

## v4.1 - STANDARD EDITION ($150 one-time) - AVAILABLE NOW

**Pricing:** $150 one-time payment + 1 year priority support (then $75/year renewal OR community support)

### AI Models - ALL INCLUDED (NEW)
✅ **RealESRGAN 4x upscaling** - CUDA/CPU frame-by-frame upscaling
✅ **RIFE 2x-4x interpolation** - AI frame interpolation for smooth slow-mo
✅ **BasicVSR++ 2x upscaling** - Video-specific temporal upscaling
✅ **SwinIR 2x/3x/4x** - Transformer-based upscaling
✅ **ZNEDI3 2x upscaling** - Fast CPU/GPU upscaling
✅ **GFPGAN face restoration** - Restore faces in old family videos
✅ **DeOldify colorization** - Convert B&W to color
✅ **ProPainter** - Video inpainting (remove scratches, logos)

### ONNX/NPU Acceleration (NEW)
✅ **ONNX model conversion** - 98% model compression (3.8MB → 0.16MB)
✅ **DirectML runtime** - NPU + GPU + CPU support
✅ **40x speedup** - 2.5ms vs 100ms per frame
✅ **Inference mode selection** - Auto/PyTorch/TorchScript/ONNX
✅ **VRAM-based auto mode** - Intelligent mode selection
✅ **NPU offloading** - Frees 6-8GB GPU VRAM for 4K processing

### AI Performance Features (NEW)
✅ **PyTorch JIT compilation** - 20-30% AI speedup with TorchScript
✅ **Model caching** - Compiled models persist across sessions
✅ **Optimization levels** - Default/aggressive/conservative
✅ **Automatic fallback** - Falls back to eager mode on failure

### Everything from v4.0 PLUS:
✅ All core restoration features (QTGMC, denoise, color correction)
✅ All capture hardware features (DirectShow, DV/FireWire)
✅ All output formats (ProRes, DNxHD, H.265, etc.)
✅ Threaded I/O and multi-GPU support
✅ Checkpoint/resume system
✅ Batch processing queue

### Priority Support
✅ **Email support** - 48-hour response time
✅ **Bug fix priority** - Your issues resolved first
✅ **Feature requests** - Direct input on roadmap
✅ **Early access** - Beta versions before public release

---

## v4.2 - ADVANCED PROFESSIONAL EDITION ($150 one-time) - PLANNED Q2 2026

**Pricing:** $150 one-time payment + 1 year priority support (then $75/year renewal OR community support)

**Note:** Existing v4.1 customers can upgrade to v4.2 for free during the first year.

### Professional AI Features (NEW)
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

| Feature | v4.0 FREE | v4.1 EARLY | v4.1 STANDARD | v4.2 | v5.0 PRO | v5.0 ENTERPRISE |
|---------|-----------|------------|---------------|------|----------|-----------------|
| **Price** | Free | $45 one-time | $150 one-time | $150 one-time | $75/node/month | $150/node/month |
| **Basic restoration** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AI upscaling** | ❌ | ✅ All models | ✅ All models | ✅ Advanced | ✅ Advanced | ✅ Advanced |
| **ONNX/NPU** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Capture hardware** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Batch processing** | ✅ Basic | ✅ Basic | ✅ Basic | ✅ Advanced | ✅ Advanced | ✅ Advanced |
| **Project management** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Audio restoration** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Frame stabilization** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Scene detection** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Custom themes** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Cross-platform** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Network rendering** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Render farm** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Multi-machine** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **API integration** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **White-label** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Support** | Community | Community | 48h email | 48h email | 48h email | 24/7 phone |
| **SLA** | No | No | No | No | No | 99.9% |

---

## Upgrade Paths

### From v4.0 (Free) → v4.1 Early Supporter
- One-time payment: **$45** (LIMITED TIME - First 500 or until March 31, 2026)
- All AI features + ONNX/NPU acceleration
- Lifetime v4.1 updates
- Community support
- Upgrade to Standard later: Pay difference ($105) for priority support

### From v4.0 (Free) → v4.1 (Standard)
- One-time payment: **$150**
- All AI features + ONNX/NPU acceleration
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

### v4.0 FREE - Home Enthusiasts
- **Who:** Home users digitizing family tapes, hobbyists
- **Use case:** Basic restoration without AI (5-20 tapes/year)
- **Technical level:** Beginner
- **Hardware:** Any PC, no GPU required
- **Why choose this:** Just need deinterlacing and cleanup, not interested in AI upscaling

### v4.1 EARLY SUPPORTER - Early Adopters
- **Who:** Tech-savvy users wanting AI features at a discount
- **Use case:** Personal projects with professional quality (20-100 tapes/year)
- **Technical level:** Intermediate
- **Hardware:** Mid-range GPU (GTX 1660, RTX 3060, or similar)
- **ROI:** $45 for lifetime AI features (70% off)
- **Commitment:** Help test features, provide feedback, community support

### v4.1 STANDARD - Semi-Professionals
- **Who:** Freelancers, side businesses, serious enthusiasts
- **Use case:** Client work or large personal collections (50-200 tapes/year)
- **Technical level:** Intermediate to advanced
- **Hardware:** Professional GPU (RTX 3070+, 12GB+ VRAM recommended)
- **ROI:** Pays for itself after 1-2 paid client projects
- **Support:** Priority email support for troubleshooting

### v4.2 - Advanced Professionals
- **Who:** Full-time restoration businesses, archivists, production studios
- **Use case:** Regular client work with advanced workflows (200-500 tapes/year)
- **Technical level:** Advanced
- **Hardware:** High-end GPU, professional workstation
- **ROI:** Audio restoration + workflow tools save hours per project
- **Support:** Priority support + quarterly feature updates

### v5.0 PRO - Studios
- **Who:** Post-production houses, restoration studios with render farms
- **Use case:** High-volume work (500+ tapes/year)
- **Technical level:** Advanced, dedicated IT/render infrastructure
- **Hardware:** Multiple workstations/servers with GPUs
- **ROI:** 5-10x speed increase justifies subscription cost
- **Support:** Priority support + network rendering + render farm tools

### v5.0 ENTERPRISE - Enterprises
- **Who:** Large archives, broadcasters, major studios
- **Use case:** Industrial-scale restoration (1000s of tapes)
- **Technical level:** IT department, system integrators
- **Hardware:** Enterprise render farms, cloud infrastructure
- **ROI:** Mission-critical with SLA guarantees
- **Support:** 24/7 phone support + custom features + white-label branding

---

## Development Timeline

| Version | Start | Release | Duration |
|---------|-------|---------|----------|
| v4.0 | Dec 2025 | Dec 2025 | ✅ Released (Free) |
| v4.1 | Dec 2025 | Dec 2025 | ✅ Released (Paid - $45/$150) |
| v4.2 | Jan 2026 | Q2 2026 | 4-6 months |
| v5.0 Pro | Apr 2026 | Q3-Q4 2026 | 6-9 months |
| v5.0 Enterprise | Jul 2026 | Q4 2026 | 3 months after Pro |

---

**Last Updated:** December 29, 2025  
**Document Version:** 1.0  
**Maintained by:** Advanced Tape Restorer Development Team
