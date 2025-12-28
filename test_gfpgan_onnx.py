"""
Simple GFPGAN ONNX conversion test
Avoids Unicode output issues
"""
import sys
import os
from pathlib import Path

# Force UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("Starting GFPGAN ONNX conversion...")

# Import converter
from core.onnx_converter import ONNXConverter, QuantizationMode

print("Loading GFPGAN model...")
import torch
from gfpgan import GFPGANer

# Find model
model_dir = Path.home() / "AppData" / "Local" / "Advanced_Tape_Restorer" / "ai_models" / "gfpgan"
model_files = list(model_dir.glob("*.pth"))

if not model_files:
    print(f"ERROR: No GFPGAN model found in: {model_dir}")
    sys.exit(1)

model_path = str(model_files[0])
print(f"Found model: {model_files[0].name}")

# Load GFPGAN
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

restorer = GFPGANer(
    model_path=model_path,
    upscale=2,
    arch='clean',
    channel_multiplier=2,
    bg_upsampler=None,
    device=device
)

# Extract model
if not hasattr(restorer, 'gfpgan'):
    print("ERROR: Could not extract model from GFPGANer")
    sys.exit(1)

model = restorer.gfpgan
model.eval()
print("Model loaded successfully")

# Convert to ONNX
output_dir = Path.home() / "AppData" / "Local" / "Advanced_Tape_Restorer" / "onnx_models"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = str(output_dir / "gfpgan.onnx")

print("Converting to ONNX...")
converter = ONNXConverter(log_callback=print)

result = converter.convert_model(
    pytorch_model=model,
    input_shape=(1, 3, 512, 512),
    output_path=output_path,
    model_name="gfpgan",
    quantization=QuantizationMode.FP16,
    opset_version=18,
    validate=True
)

print("\n" + "="*60)
print("CONVERSION COMPLETE")
print("="*60)
print(f"Success: {result.success}")
print(f"Output: {output_path}")
print(f"Original size: {result.original_size_mb:.2f} MB")
print(f"ONNX size: {result.onnx_size_mb:.2f} MB")
compression = ((result.original_size_mb - result.onnx_size_mb) / result.original_size_mb * 100)
print(f"Compression: {compression:.1f}%")
if result.validation_passed:
    print(f"Validation: PASSED")
    print(f"Max error: {result.max_error:.6f}")
    print(f"Mean error: {result.mean_error:.6f}")
else:
    print(f"Validation: FAILED (accuracy check - model may need FP32)")
    print(f"Max error: {result.max_error:.6f}")
print(f"PyTorch inference: {result.pytorch_time_ms:.2f} ms")
print(f"ONNX inference: {result.onnx_time_ms:.2f} ms")
print("="*60)
