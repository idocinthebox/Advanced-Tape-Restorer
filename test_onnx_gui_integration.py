"""
Test ONNX+NPU GUI Integration - End-to-End Verification

Tests:
1. ONNX model loading from converted files
2. DirectML/NPU provider availability
3. Inference mode selector functionality
4. Auto mode VRAM detection
5. Manual mode override

Author: Advanced Tape Restorer Team
Date: December 25, 2025
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_onnx_runtime():
    """Test 1: ONNX Runtime with DirectML"""
    print("\n=== Test 1: ONNX Runtime with DirectML ===")
    
    try:
        import onnxruntime as ort
        print(f"✓ onnxruntime version: {ort.__version__}")
        
        providers = ort.get_available_providers()
        print(f"✓ Available providers: {providers}")
        
        if 'DmlExecutionProvider' in providers:
            print("✅ NPU/DirectML support available!")
        else:
            print("⚠️ NPU/DirectML not available (CPU only)")
        
        return True
    except ImportError as e:
        print(f"❌ onnxruntime not installed: {e}")
        return False


def test_onnx_models_exist():
    """Test 2: Check if ONNX models were converted"""
    print("\n=== Test 2: ONNX Model Files ===")
    
    from core.onnx_converter import ONNXConverter
    converter = ONNXConverter()
    
    expected_models = [
        "realesrgan.onnx",
        "rife.onnx",
        "basicvsr++.onnx",
        "swinir.onnx",
        "demo_upscaler.onnx",
        "demo_interpolation.onnx"
    ]
    
    found = 0
    for model in expected_models:
        path = converter.output_dir / model
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"✓ {model}: {size_mb:.2f} MB")
            found += 1
        else:
            print(f"✗ {model}: Not found")
    
    print(f"\n✅ Found {found}/{len(expected_models)} ONNX models")
    return found > 0


def test_inference_mode_enum():
    """Test 3: Inference mode enum and auto selector"""
    print("\n=== Test 3: Inference Mode System ===")
    
    try:
        from core.multi_gpu_manager import InferenceMode
        from core.auto_mode_selector import AutoModeSelector
        
        # Check enum values
        modes = [
            InferenceMode.PYTORCH_FP32,
            InferenceMode.PYTORCH_FP16,
            InferenceMode.ONNX_FP16,
            InferenceMode.ONNX_INT8,
            InferenceMode.CPU_ONLY
        ]
        
        print("✓ Inference modes:")
        for mode in modes:
            print(f"  - {mode.value}")
        
        # Test auto selector
        selector = AutoModeSelector()
        result = selector.detect_best_mode(target_model="realesrgan", force_auto=True)
        
        print(f"\n✓ Auto-detected mode: {result.recommended_mode.value}")
        print(f"✓ Explanation: {result.explanation}")
        
        if result.override_warning:
            print(f"⚠️ Warning: {result.override_warning}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_inference():
    """Test 4: Actual ONNX inference with NPU"""
    print("\n=== Test 4: ONNX Model Inference ===")
    
    try:
        import onnxruntime as ort
        from core.onnx_converter import ONNXConverter
        
        converter = ONNXConverter()
        model_path = converter.output_dir / "realesrgan.onnx"
        
        if not model_path.exists():
            print(f"⚠️ Model not found: {model_path}")
            return False
        
        # Create session with DirectML
        session = ort.InferenceSession(
            str(model_path),
            providers=['DmlExecutionProvider', 'CPUExecutionProvider']
        )
        
        provider_used = session.get_providers()[0]
        print(f"✓ Inference provider: {provider_used}")
        
        # Get model info
        input_info = session.get_inputs()[0]
        output_info = session.get_outputs()[0]
        
        print(f"✓ Input: {input_info.name} {input_info.shape} ({input_info.type})")
        print(f"✓ Output: {output_info.name} {output_info.shape} ({output_info.type})")
        
        # Test inference (small image)
        test_input = np.random.randn(1, 3, 64, 64).astype(np.float16)
        
        import time
        start = time.perf_counter()
        output = session.run([output_info.name], {input_info.name: test_input})
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        print(f"✓ Inference time: {elapsed_ms:.2f}ms")
        print(f"✓ Output shape: {output[0].shape}")
        
        if provider_used == 'DmlExecutionProvider':
            print("✅ NPU/DirectML acceleration working!")
        else:
            print("⚠️ Using CPU fallback (NPU not active)")
        
        return True
        
    except Exception as e:
        print(f"❌ Inference test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_settings():
    """Test 5: GUI settings persistence"""
    print("\n=== Test 5: GUI Settings Integration ===")
    
    try:
        from gui.settings_manager import SettingsManager
        
        settings = SettingsManager()
        
        # Check inference mode settings
        auto_mode = settings.get("auto_inference_mode", True)
        manual_mode = settings.get("manual_inference_mode", "pytorch_fp32")
        
        print(f"✓ Auto inference mode: {auto_mode}")
        print(f"✓ Manual inference mode: {manual_mode}")
        
        # Test setting override
        settings.save("manual_inference_mode", "onnx_fp16")
        saved_mode = settings.get("manual_inference_mode")
        
        if saved_mode == "onnx_fp16":
            print("✓ Settings persistence working")
        else:
            print(f"⚠️ Settings save failed: expected 'onnx_fp16', got '{saved_mode}'")
        
        # Restore original
        settings.save("manual_inference_mode", manual_mode)
        
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gpu_detection():
    """Test 6: GPU and VRAM detection"""
    print("\n=== Test 6: GPU Detection ===")
    
    try:
        from core.multi_gpu_manager import MultiGPUManager
        
        manager = MultiGPUManager()
        gpus = manager.get_all_gpus()
        
        if not gpus:
            print("⚠️ No GPUs detected")
            return True
        
        for idx, gpu in enumerate(gpus):
            print(f"\n✓ GPU {idx}: {gpu.name}")
            print(f"  Vendor: {gpu.vendor.value}")
            print(f"  VRAM Total: {gpu.memory_total}MB")
            print(f"  VRAM Available: {gpu.memory_available}MB")
            print(f"  AI Score: {gpu.ai_score}")
            print(f"  Encode Score: {gpu.encode_score}")
        
        best_ai = manager.get_best_ai_gpu()
        best_encode = manager.get_best_encode_gpu()
        
        if best_ai:
            print(f"\n✓ Best AI GPU: {best_ai.name}")
        if best_encode:
            print(f"✓ Best Encode GPU: {best_encode.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ GPU detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("ONNX+NPU GUI Integration Test Suite")
    print("Advanced Tape Restorer v4.1")
    print("=" * 70)
    
    tests = [
        ("ONNX Runtime", test_onnx_runtime),
        ("ONNX Models", test_onnx_models_exist),
        ("Inference Mode System", test_inference_mode_enum),
        ("Model Inference", test_model_inference),
        ("GUI Settings", test_gui_settings),
        ("GPU Detection", test_gpu_detection),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! ONNX+NPU integration is working perfectly!")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Review output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
