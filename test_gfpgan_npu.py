"""
Test GFPGAN ONNX on NPU
"""
import sys
import os
from pathlib import Path
import numpy as np
import onnxruntime as ort
import time

print("="*60)
print("GFPGAN ONNX NPU Test")
print("="*60)

# Find ONNX model
onnx_path = Path.home() / "AppData" / "Local" / "Advanced_Tape_Restorer" / "onnx_models" / "gfpgan.onnx"

if not onnx_path.exists():
    print(f"ERROR: ONNX model not found: {onnx_path}")
    sys.exit(1)

print(f"\nModel: {onnx_path}")
print(f"Size: {onnx_path.stat().st_size / (1024**2):.2f} MB")

# Check available providers
print(f"\nAvailable providers: {ort.get_available_providers()}")

# Create session with DirectML (NPU/GPU)
providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
print(f"Using providers: {providers}")

session = ort.InferenceSession(str(onnx_path), providers=providers)
print(f"Active provider: {session.get_providers()[0]}")

# Get input/output info
input_name = session.get_inputs()[0].name
input_shape = session.get_inputs()[0].shape
output_name = session.get_outputs()[0].name

print(f"\nInput: {input_name} {input_shape}")
print(f"Output: {output_name}")

# Create test input (512x512 face image)
print("\nCreating test input (512x512 RGB face)...")
test_input = np.random.randn(1, 3, 512, 512).astype(np.float32)

# Warmup
print("Warming up...")
for i in range(5):
    output = session.run([output_name], {input_name: test_input})[0]
    print(f"  Warmup {i+1}/5: Output shape {output.shape}")

# Benchmark
print("\nBenchmarking 20 iterations...")
times = []
for i in range(20):
    start = time.perf_counter()
    output = session.run([output_name], {input_name: test_input})[0]
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000
    times.append(elapsed_ms)
    if i < 5 or i >= 15:  # Print first 5 and last 5
        print(f"  Iteration {i+1:2d}: {elapsed_ms:7.2f} ms")
    elif i == 5:
        print(f"  ...")

# Statistics
times = np.array(times)
print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Provider: {session.get_providers()[0]}")
print(f"Iterations: {len(times)}")
print(f"Average: {times.mean():.2f} ms per frame")
print(f"Min: {times.min():.2f} ms")
print(f"Max: {times.max():.2f} ms")
print(f"Std Dev: {times.std():.2f} ms")
print(f"Output shape: {output.shape}")
print("="*60)

# Performance analysis
if times.mean() < 100:
    print("✓ EXCELLENT: < 100ms (suitable for real-time processing)")
elif times.mean() < 500:
    print("✓ GOOD: < 500ms (suitable for video processing)")
else:
    print("⚠ SLOW: > 500ms (CPU fallback?)")

print("\nNote: GFPGAN is computationally intensive (face restoration)")
print("FP16 quantization provides 99.7% compression but slower on NPU")
print("For faster inference, use PyTorch CUDA version")
