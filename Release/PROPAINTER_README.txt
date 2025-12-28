ProPainter Installation & License Guide
=====================================

This file explains how to obtain and install ProPainter (external AI inpainting tool).

Important:
- ProPainter is NOT distributed with Advanced Tape Restorer.
- You must obtain ProPainter yourself from the official repository and accept its license.
- ProPainter is licensed for NON-COMMERCIAL USE only (see repository LICENSE).

Official repository:
https://github.com/sczhou/ProPainter

Quick install steps (Windows - recommended using Conda):

1) Clone the repository
   git clone https://github.com/sczhou/ProPainter.git
   cd ProPainter

2) Create and activate conda environment
   conda create -n propainter python=3.8 -y
   conda activate propainter

3) Install Python dependencies
   pip install -r requirements.txt

4) Download pretrained models
   The first run of ProPainter may auto-download models. If not, get the models
   from the project's releases page and place them in the `weights/` folder:
   - ProPainter.pth
   - recurrent_flow_completion.pth
   - raft-things.pth

5) Test ProPainter (example)
   python inference_propainter.py --video inputs/object_removal/bmx-trees --mask inputs/object_removal/bmx-trees_mask

GPU & Requirements:
- CUDA-enabled NVIDIA GPU recommended
- PyTorch with CUDA (matching your CUDA drivers)
- 8GB+ VRAM recommended for 720x480 processing; 16GB+ recommended for HD

License & Redistribution:
- ProPainter has its own license (see https://github.com/sczhou/ProPainter/blob/main/LICENSE).
- Advanced Tape Restorer does NOT redistribute ProPainter code, models, or installers.
- By following these instructions you acknowledge and accept ProPainter's license terms.

Support & Troubleshooting:
- For ProPainter-specific issues, use the project's GitHub Issues.
- For integration questions (how to configure ProPainter path inside Advanced Tape Restorer), use the ProPainter Setup Assistant in the Advanced tab of the app.

Notes for packagers:
- Do NOT redistribute ProPainter binaries or model weights without explicit permission.

