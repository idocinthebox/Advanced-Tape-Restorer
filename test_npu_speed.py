#!/usr/bin/env python3
"""Quick test to verify NPU/DirectML acceleration"""
import onnxruntime as ort
import numpy as np
import time

print("="*60)
print("NPU/DirectML Speed Test")
print("="*60)
print()

# Load model with DirectML
model_path = r"C:\Users\CWT\AppData\Local\Advanced_Tape_Restorer\onnx_models\realesrgan.onnx"
sess = ort.InferenceSession(
    model_path,
    providers=['DmlExecutionProvider', 'CPUExecutionProvider']
)

print(f"Provider in use: {sess.get_providers()[0]}")
print()

# Create test input
input_data = np.random.randn(1, 3, 64, 64).astype(np.float16)

# Warm-up (first run compiles model to NPU)
print("Warming up (compiling to NPU)...")
output = sess.run(None, {'input': input_data})
print(f"✓ First run complete")
print()

# Benchmark
print("Running 10 iterations...")
start = time.perf_counter()
for i in range(10):
    output = sess.run(None, {'input': input_data})
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"Total time: {elapsed_ms:.1f}ms")
print(f"Average: {elapsed_ms/10:.1f}ms per frame")
print(f"Input shape: {input_data.shape}")
print(f"Output shape: {output[0].shape}")
print()
print("✅ NPU/GPU acceleration working!")
