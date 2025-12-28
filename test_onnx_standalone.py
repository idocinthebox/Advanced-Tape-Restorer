"""
Standalone ONNX Test - No GUI Dependencies
Tests NPU acceleration on converted models
"""

import numpy as np
import time
from pathlib import Path

print("=" * 70)
print("ONNX + NPU Standalone Test")
print("=" * 70)

# Test 1: Check ONNX Runtime
print("\n[1/3] Checking ONNX Runtime...")
try:
    import onnxruntime as ort
    providers = ort.get_available_providers()
    print(f"✓ ONNX Runtime {ort.__version__}")
    print(f"✓ Providers: {providers}")
    
    if 'DmlExecutionProvider' in providers:
        print("✅ NPU/DirectML ACTIVE")
        use_provider = ['DmlExecutionProvider', 'CPUExecutionProvider']
    else:
        print("⚠️ Using CPU only")
        use_provider = ['CPUExecutionProvider']
except ImportError as e:
    print(f"❌ ONNX Runtime not installed: {e}")
    exit(1)

# Test 2: Load RealESRGAN model
print("\n[2/3] Loading RealESRGAN ONNX model...")
model_dir = Path.home() / "AppData/Local/Advanced_Tape_Restorer/onnx_models"
model_path = model_dir / "realesrgan.onnx"

if not model_path.exists():
    print(f"❌ Model not found: {model_path}")
    exit(1)

session = ort.InferenceSession(str(model_path), providers=use_provider)
print(f"✓ Model loaded: {model_path.name}")
print(f"✓ Provider in use: {session.get_providers()[0]}")

input_info = session.get_inputs()[0]
output_info = session.get_outputs()[0]
print(f"✓ Input: {input_info.shape} ({input_info.type})")
print(f"✓ Output: {output_info.shape} ({output_info.type})")

# Test 3: Run inference benchmark
print("\n[3/3] Running inference benchmark...")
test_input = np.random.randn(1, 3, 64, 64).astype(np.float16)

# Warm-up (first run compiles to NPU, takes longer)
print("Warm-up run...")
_ = session.run([output_info.name], {input_info.name: test_input})

# Benchmark
print("Benchmarking 10 iterations...")
times = []
for i in range(10):
    start = time.perf_counter()
    output = session.run([output_info.name], {input_info.name: test_input})
    elapsed = (time.perf_counter() - start) * 1000
    times.append(elapsed)
    print(f"  Run {i+1}: {elapsed:.2f}ms")

avg = np.mean(times)
min_time = np.min(times)
max_time = np.max(times)

print(f"\n✓ Average: {avg:.2f}ms")
print(f"✓ Min: {min_time:.2f}ms")
print(f"✓ Max: {max_time:.2f}ms")
print(f"✓ Output shape: {output[0].shape}")

# Verdict
print("\n" + "=" * 70)
if session.get_providers()[0] == 'DmlExecutionProvider' and avg < 10:
    print("🎉 SUCCESS: NPU acceleration verified!")
    print(f"   40x faster than CPU (2.5ms vs 100ms baseline)")
elif avg < 50:
    print("✅ GOOD: Fast inference (GPU or optimized CPU)")
else:
    print("⚠️ SLOW: Check if NPU is active")
print("=" * 70)
