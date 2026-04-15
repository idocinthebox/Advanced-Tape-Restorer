# Advanced Tape Restorer

Advanced Tape Restorer Community Edition is the public, MIT-licensed home for the v4.0 release line.

This repository is focused on the free community workflow for analog and DV restoration.

## Product Line Clarity

- Community Edition (this repo): free, MIT licensed
- ATR 6.0 Professional: separate commercial product line
- LTX Generative Repair: separate paid add-on for ATR 6.0 Professional

## What Community Edition Includes

- Core restoration workflow for analog and DV sources
- Deinterlacing and cleanup filters
- Capture and export workflow used by the community branch
- Batch-oriented processing features present in the v4.0 release line
- MIT-licensed source code for community use and contribution

## What Community Edition Does Not Include

- Commercial licensing/entitlement workflows from ATR 6.0 Professional
- Paid marketplace/add-on fulfillment logic
- Bundled access to paid add-ons such as LTX Generative Repair

## Getting Started from Source

```powershell
git clone https://github.com/idocinthebox/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Requirements

- Windows 10 or 11
- FFmpeg available on PATH
- VapourSynth available on PATH
- Python environment for source-based use

## Core Documents

- VERSION_FEATURE_MATRIX.md
- LICENSING_GUIDE.md
- LICENSE_SUMMARY_FOR_BUYERS.md
- QUICK_START_GUIDE.md
- ROADMAP_v4.0.md

## License

This repository is distributed under the MIT License.

Commercial products and paid add-ons referenced in documentation are separate offerings and are not granted by this repository license.

See LICENSE and LICENSING_GUIDE.md for details.
