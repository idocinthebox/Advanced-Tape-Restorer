# Advanced Tape Restorer - Licensing Guide

## Overview

Advanced Tape Restorer uses a **dual licensing model** that balances open-source community development with sustainable commercial development.

## Licensing Structure

```
┌─────────────────────────────────────────────────────────┐
│ v4.0 - MIT Licensed (Forever Free)                      │
├─────────────────────────────────────────────────────────┤
│ • Core restoration engine (QTGMC, denoise, color)      │
│ • DirectShow capture (analog/DV/FireWire)              │
│ • Hardware encoders (NVENC, AMF, Quick Sync)           │
│ • Multi-GPU support                                     │
│ • Threaded I/O and checkpoint/resume                    │
│ • Basic GUI and batch processing                        │
│                                                         │
│ ✅ Source code available on GitHub                      │
│ ✅ Free forever                                         │
│ ✅ Modify and redistribute freely                       │
│ ❌ NO AI features                                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│ v4.1 - Dual License (Paid - $45/$150)                  │
├─────────────────────────────────────────────────────────┤
│ INCLUDES: All v4.0 MIT components (remain MIT)         │
│                                                         │
│ PLUS: Proprietary AI features (closed source):         │
│ • RealESRGAN 4x upscaling                              │
│ • RIFE 2x-4x frame interpolation                        │
│ • BasicVSR++, SwinIR, ZNEDI3 upscaling                 │
│ • GFPGAN face restoration                               │
│ • DeOldify colorization                                 │
│ • ProPainter video inpainting                           │
│ • ONNX/NPU acceleration (98% compression, 40x speedup)  │
│ • PyTorch JIT compilation (20-30% speedup)              │
│                                                         │
│ 🔒 AI features require license                          │
│ 🔒 No redistribution of v4.1 binaries                  │
│ ✅ v4.0 components remain MIT                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│ v4.2+ - Advanced Professional (Paid - $150+)           │
├─────────────────────────────────────────────────────────┤
│ • Audio restoration, scene detection                    │
│ • Project management, client database                   │
│ • Frame stabilization, cross-platform                   │
│ • Network rendering (v5.0 Pro - subscription)           │
└─────────────────────────────────────────────────────────┘
```

## What This Means for Users

### If You Use v4.0 (MIT - FREE)
- ✅ **Completely free forever**
- ✅ Source code available
- ✅ Modify and redistribute as you wish
- ✅ Use commercially without restrictions
- ✅ No license keys or activation
- ⚠️ Community support only
- ❌ No AI upscaling features

### If You Buy v4.1 Early Supporter ($45)
- ✅ All v4.0 features (MIT components)
- ✅ All v4.1 AI features (8 models + ONNX/NPU)
- ✅ Lifetime v4.1 updates
- ✅ Early access to beta versions
- ✅ Supporter badge in community
- ⚠️ Community support (not priority)
- ❌ Cannot redistribute v4.1 binaries
- ❌ AI features require license key

### If You Buy v4.1 Standard ($150)
- ✅ All v4.0 features (MIT components)
- ✅ All v4.1 AI features (8 models + ONNX/NPU)
- ✅ Lifetime v4.1 updates
- ✅ 1 year priority support (48h response)
- ✅ Can renew support at $75/year
- ❌ Cannot redistribute v4.1 binaries
- ❌ AI features require license key

## Legal Questions & Answers

### Q: Can I fork v4.0 and sell my own version?
**A:** Yes! v4.0 is MIT licensed. You can:
- Fork the v4.1 codebase
- Add your own features
- Sell your modified version
- Redistribute freely

You must:
- Include the original MIT license
- Credit the original authors
- Not claim you created the original v4.1 code

### Q: Can I use v4.1 in my commercial video production business?
**A:** Yes! MIT license allows unlimited commercial use.

### Q: If I buy v4.2, can I share it with my team?
**A:** No. Each user requires their own license (single-user license). For teams:
- Buy multiple individual licenses, or
- Contact us for volume discounts, or
- Wait for v5.0 Enterprise (multi-user licensing)

### Q: Can I decompile v4.2 to see how proprietary features work?
**A:** No. Reverse engineering proprietary components violates the license and terminates your license immediately.

### Q: What if I build the v4.2 features myself using v4.1?
**A:** You can! v4.1 is MIT, so you can extend it however you want. The v4.2 license only restricts redistribution of **our proprietary implementation** of those features.

### Q: Can I use v4.1 components in my own software?
**A:** Yes! MIT license allows this. You can extract code from v4.1 and use it in your projects (open source or commercial), as long as you include the MIT license text.

### Q: Why dual licensing instead of fully open source?
**A:** 
- v4.1 provides powerful free tools for everyone
- v4.2 commercial features fund ongoing development
- Dual licensing lets us:
  - Keep core features free and open
  - Develop professional features sustainably
  - Offer affordable pricing ($45 early supporter)
  - Maintain the project long-term

### Q: Will v4.1 continue to receive updates?
**A:** v4.1 will receive:
- ✅ Security patches
- ✅ Bug fixes for core features
- ✅ Compatibility updates (new FFmpeg/VapourSynth versions)
- ❌ New professional features (those are v4.2+)

### Q: Can I "downgrade" from v4.2 to v4.1 MIT?
**A:** Yes! You can always use v4.1 (MIT) instead. Simply:
- Download v4.1 from GitHub
- You keep your v4.2 license (non-refundable)
- Continue using v4.1 under MIT terms

## License Compliance Checklist

### For v4.1 Users (MIT)
- [ ] Include MIT license text if redistributing
- [ ] Credit original authors
- [ ] Don't claim you created the original work
- ✅ That's it! Use freely.

### For v4.2 Users (Commercial)
- [ ] Use only on licensed number of computers
- [ ] Don't share license key
- [ ] Don't redistribute v4.2 binaries
- [ ] Don't reverse engineer proprietary features
- [ ] Renew support if you want priority assistance
- [ ] Comply with v4.1 MIT terms for MIT components

## Source Code Availability

### v4.1 (MIT Licensed)
- **Repository:** https://github.com/[your-repo]/advanced-tape-restorer/tree/v4.1
- **License:** MIT (see LICENSE_MIT.txt)
- **Status:** Public, open source

### v4.2 (Proprietary Features)
- **Repository:** Private
- **License:** Proprietary (see LICENSE_V4.2.txt)
- **Status:** Closed source (binaries only)
- **Note:** v4.1 MIT components within v4.2 remain under MIT

## How to Comply with MIT License (v4.1 Components)

If you use or redistribute v4.1 components, you must include this notice:

```
Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Migration Path

### From v4.1 (Free) to v4.2
1. Purchase v4.2 license (Early Supporter $45 or Standard $150)
2. Download v4.2 installer
3. Enter license key during installation
4. All v4.1 settings and projects carry over
5. Proprietary features unlock automatically

### From v4.2 back to v4.1
1. Uninstall v4.2
2. Download v4.1 from GitHub
3. Install v4.1 (no license key needed)
4. Continue using MIT-licensed features
5. Your v4.2 license remains valid (non-refundable)

## Support Options by License

| License Type | Support Method | Response Time | Cost |
|--------------|---------------|---------------|------|
| v4.1 MIT | Community (GitHub, Discord) | Best effort | Free |
| v4.2 Early Supporter | Community (GitHub, Discord) | Best effort | Included |
| v4.2 Standard (Year 1) | Priority email | 48 hours | Included |
| v4.2 Standard (Year 2+) | Community OR renew | 48h if renewed | $75/year |
| v5.0 Pro | Priority email | 48 hours | Included |
| v5.0 Enterprise | 24/7 phone + email | Immediate | Included |

## Contact

**Licensing Questions:**
- Email: licensing@[your-domain.com]
- Before purchasing, check: [website]/faq

**Technical Support:**
- v4.1 MIT: GitHub Issues or Discord
- v4.2+: support@[your-domain.com]

**Sales & Volume Licensing:**
- Email: sales@[your-domain.com]
- For 10+ licenses, contact us for volume discounts

## Version History

- **v4.1** (December 2025) - MIT licensed, free forever
- **v4.2 Early Supporter** (Q2 2026) - $45 launch offer (first 500)
- **v4.2 Standard** (Q2 2026) - $150 with priority support
- **v5.0 Pro** (Q3-Q4 2026) - $75/node/month subscription
- **v5.0 Enterprise** (Q4 2026) - $150/node/month subscription

---

**Last Updated:** December 29, 2025  
**Document Version:** 1.0  
**Applies to:** Advanced Tape Restorer v4.1 and v4.2
