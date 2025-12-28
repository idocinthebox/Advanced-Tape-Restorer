# ATI Theatre capture + VapourSynth(QTGMC) + FFmpeg batch pipeline

This is a **starter** modular pipeline intended for:
- lossless / near-lossless capture ingest (FFmpeg)
- VapourSynth processing (QTGMC + chroma phase correction + field-aware variants)
- per-tape auto-profiling (quick stats from sample frames)
- Resolve preview LUT generation (.cube)

It does **not** include any Windows driver work for ATI Theatre chips.
Instead, it assumes you can already capture via some working driver stack (often XP-era rigs, or other supported capture devices),
and then you run this pipeline on the captured files.

## Quick start
1. Install:
   - Python 3.10+ (3.11/3.12 recommended)
   - VapourSynth R70+ (and ensure `python -c "import vapoursynth as vs"` works)
   - Plugins:
     - QTGMC dependencies (commonly: `havsfunc`, `mvtools`, `nnedi3/znedi3`, `fmtconv`, `rgtools`, etc.)
   - FFmpeg (in PATH)

2. Copy `config/config.example.yaml` to `config/config.yaml` and edit paths.

3. Run:
   ```bash
   python -m pipeline.cli profile "D:\captures\TAPE001.avi"
   python -m pipeline.cli process "D:\captures\TAPE001.avi" --preset qtgmc_slow
   ```

Outputs:
- processed intermediates in `work/`
- `.cube` LUTs in `work/luts/`

## Notes
- If your source is interlaced (VHS/Hi8), QTGMC preset outputs progressive.
- Field-aware options are in `pipeline/vs/variants.py`.

