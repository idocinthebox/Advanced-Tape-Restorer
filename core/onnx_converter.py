"""
ONNX Model Converter and Validator for Advanced Tape Restorer
==============================================================

Converts PyTorch AI models to ONNX format for AMD NPU/iGPU execution.
Includes comprehensive validation to ensure conversion quality.

Features:
- PyTorch → ONNX conversion
- Model quantization (FP32 → FP16 → INT8)
- Validation with test inputs
- Performance benchmarking (PyTorch vs ONNX)
- Visual output comparison
- Automatic error detection

Supported Models:
- GFPGAN (face restoration)
- RealESRGAN (upscaling)
- RIFE (frame interpolation)
- Custom VapourSynth filters

Author: Advanced Tape Restorer Team
License: MIT
Version: 4.1.0
"""

import os
import sys
import time
import numpy as np
import torch
import onnx
import onnxruntime as ort
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from enum import Enum


class QuantizationMode(Enum):
    """Quantization precision options"""
    FP32 = "fp32"  # Full precision (default PyTorch)
    FP16 = "fp16"  # Half precision (faster, good quality)
    INT8 = "int8"  # 8-bit integer (fastest, some quality loss)
    INT4 = "int4"  # 4-bit integer (very fast, more quality loss)


@dataclass
class ConversionResult:
    """Results from ONNX conversion"""
    success: bool
    onnx_path: Optional[str]
    original_size_mb: float
    onnx_size_mb: float
    validation_passed: bool
    max_error: float
    mean_error: float
    inference_time_pytorch_ms: float
    inference_time_onnx_ms: float
    speedup_factor: float
    error_message: Optional[str]


@dataclass
class ValidationMetrics:
    """Validation comparison metrics"""
    max_absolute_error: float
    mean_absolute_error: float
    psnr_db: float  # Peak Signal-to-Noise Ratio
    ssim: float     # Structural Similarity Index
    passed: bool
    threshold_max_error: float = 0.01  # 1% max error tolerance
    threshold_mean_error: float = 0.001  # 0.1% mean error tolerance


class ONNXConverter:
    """
    Converts PyTorch models to ONNX format with validation.
    
    Usage:
        converter = ONNXConverter()
        result = converter.convert_model(
            pytorch_model=gfpgan_model,
            input_shape=(1, 3, 512, 512),
            output_path="models/gfpgan.onnx",
            quantization=QuantizationMode.FP16
        )
    """
    
    def __init__(self, log_callback=None):
        """
        Initialize ONNX converter.
        
        Args:
            log_callback: Optional logging function
        """
        self.log_callback = log_callback
        self.output_dir = Path(os.environ.get('LOCALAPPDATA', '.')) / 'Advanced_Tape_Restorer' / 'onnx_models'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _log(self, message: str):
        """Internal logging"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[ONNX] {message}")
    
    def convert_model(
        self,
        pytorch_model: torch.nn.Module,
        input_shape: Tuple[int, ...],
        output_path: str,
        model_name: str = "model",
        quantization: QuantizationMode = QuantizationMode.FP16,
        opset_version: int = 18,
        validate: bool = True,
        dynamic_axes: Optional[Dict] = None
    ) -> ConversionResult:
        """
        Convert PyTorch model to ONNX with validation.
        
        Args:
            pytorch_model: PyTorch model to convert
            input_shape: Input tensor shape (e.g., (1, 3, 512, 512))
            output_path: Where to save ONNX model
            model_name: Model name for logging
            quantization: Quantization mode (FP32, FP16, INT8)
            opset_version: ONNX opset version (default: 17)
            validate: Whether to validate conversion
            dynamic_axes: Optional dynamic axes specification
            quantization: Quantization mode (FP32/FP16/INT8)
            opset_version: ONNX opset version (17 recommended)
            validate: Run validation tests
        
        Returns:
            ConversionResult with metrics
        """
        
        self._log(f"Converting {model_name} to ONNX ({quantization.value})...")
        
        try:
            # Ensure model is in eval mode
            pytorch_model.eval()
            
            # Get model size before conversion
            original_size = self._get_model_size(pytorch_model)
            
            # Create dummy input for tracing
            device = next(pytorch_model.parameters()).device
            dummy_input = torch.randn(*input_shape).to(device)
            
            # Convert to FP16 if requested
            if quantization == QuantizationMode.FP16:
                pytorch_model = pytorch_model.half()
                dummy_input = dummy_input.half()
            
            # Benchmark PyTorch inference
            pytorch_time_ms = self._benchmark_pytorch(pytorch_model, dummy_input)
            
            # Export to ONNX
            self._log(f"Exporting to ONNX (opset {opset_version})...")
            
            # Build export parameters
            export_params = {
                'export_params': True,
                'opset_version': opset_version,
                'do_constant_folding': True,
                'input_names': ['input'],
                'output_names': ['output'],
                'verbose': False  # Reduce console output
            }
            
            # Add dynamic axes if specified
            if dynamic_axes:
                export_params['dynamic_axes'] = dynamic_axes
            
            # Use dynamo export for better stability (PyTorch 2.x)
            try:
                torch.onnx.export(
                    pytorch_model,
                    dummy_input,
                    output_path,
                    **export_params
                )
            except Exception as e:
                self._log(f"Standard export failed, trying with dynamo=False: {e}")
                torch.onnx.export(
                    pytorch_model,
                    dummy_input,
                    output_path,
                    dynamo=False,
                    **export_params
                )
            
            # Verify ONNX model
            self._log("Verifying ONNX model...")
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)
            
            # Get ONNX model size
            onnx_size = os.path.getsize(output_path) / (1024 * 1024)
            
            # Optional quantization to INT8
            if quantization == QuantizationMode.INT8:
                self._log("Quantizing to INT8...")
                output_path = self._quantize_to_int8(output_path)
                onnx_size = os.path.getsize(output_path) / (1024 * 1024)
            
            # Validate conversion if requested
            validation_passed = True
            max_error = 0.0
            mean_error = 0.0
            onnx_time_ms = 0.0
            
            if validate:
                self._log("Validating conversion...")
                validation_result = self._validate_conversion(
                    pytorch_model,
                    output_path,
                    dummy_input
                )
                
                validation_passed = validation_result.passed
                max_error = validation_result.max_absolute_error
                mean_error = validation_result.mean_absolute_error
                
                # Benchmark ONNX inference
                onnx_time_ms = self._benchmark_onnx(output_path, dummy_input)
                
                if validation_passed:
                    self._log(f"✓ Validation passed (max error: {max_error:.6f}, PSNR: {validation_result.psnr_db:.2f} dB)")
                else:
                    self._log(f"✗ Validation failed (max error: {max_error:.6f} > {validation_result.threshold_max_error})")
            
            speedup = pytorch_time_ms / onnx_time_ms if onnx_time_ms > 0 else 1.0
            
            self._log(f"✓ Conversion complete: {original_size:.2f}MB → {onnx_size:.2f}MB")
            self._log(f"  Performance: PyTorch {pytorch_time_ms:.2f}ms → ONNX {onnx_time_ms:.2f}ms ({speedup:.2f}x speedup)")
            
            return ConversionResult(
                success=True,
                onnx_path=output_path,
                original_size_mb=original_size,
                onnx_size_mb=onnx_size,
                validation_passed=validation_passed,
                max_error=max_error,
                mean_error=mean_error,
                inference_time_pytorch_ms=pytorch_time_ms,
                inference_time_onnx_ms=onnx_time_ms,
                speedup_factor=speedup,
                error_message=None
            )
        
        except Exception as e:
            self._log(f"✗ Conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                onnx_path=None,
                original_size_mb=0.0,
                onnx_size_mb=0.0,
                validation_passed=False,
                max_error=0.0,
                mean_error=0.0,
                inference_time_pytorch_ms=0.0,
                inference_time_onnx_ms=0.0,
                speedup_factor=0.0,
                error_message=str(e)
            )
    
    def _get_model_size(self, model: torch.nn.Module) -> float:
        """Get model size in MB"""
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        return (param_size + buffer_size) / (1024 * 1024)
    
    def _benchmark_pytorch(
        self,
        model: torch.nn.Module,
        dummy_input: torch.Tensor,
        iterations: int = 10
    ) -> float:
        """Benchmark PyTorch inference time"""
        model.eval()
        
        # Warmup
        with torch.no_grad():
            for _ in range(3):
                output = model(dummy_input)
                # Handle tuple outputs
                if isinstance(output, (tuple, list)):
                    output = output[0]
        
        # Benchmark
        start = time.perf_counter()
        with torch.no_grad():
            for _ in range(iterations):
                output = model(dummy_input)
                if isinstance(output, (tuple, list)):
                    output = output[0]
        end = time.perf_counter()
        
        return ((end - start) / iterations) * 1000  # Convert to ms
    
    def _benchmark_onnx(
        self,
        onnx_path: str,
        dummy_input: torch.Tensor,
        iterations: int = 10
    ) -> float:
        """Benchmark ONNX inference time"""
        # Create ONNX Runtime session
        providers = ['CPUExecutionProvider']  # Use CPU for validation
        if torch.cuda.is_available():
            providers.insert(0, 'CUDAExecutionProvider')
        
        session = ort.InferenceSession(onnx_path, providers=providers)
        
        # Prepare input
        input_np = dummy_input.cpu().numpy()
        
        # Warmup
        for _ in range(3):
            _ = session.run(None, {'input': input_np})
        
        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            _ = session.run(None, {'input': input_np})
        end = time.perf_counter()
        
        return ((end - start) / iterations) * 1000  # Convert to ms
    
    def _validate_conversion(
        self,
        pytorch_model: torch.nn.Module,
        onnx_path: str,
        test_input: torch.Tensor
    ) -> ValidationMetrics:
        """
        Validate ONNX conversion against PyTorch model.
        
        Compares outputs and calculates error metrics.
        """
        
        # Get PyTorch output
        pytorch_model.eval()
        with torch.no_grad():
            pytorch_output = pytorch_model(test_input)
            
            # Handle tuple/list outputs (some models return multiple outputs)
            if isinstance(pytorch_output, (tuple, list)):
                pytorch_output = pytorch_output[0]  # Use first output
            
            pytorch_output = pytorch_output.cpu().numpy()
        
        # Get ONNX output
        providers = ['CPUExecutionProvider']
        if torch.cuda.is_available():
            providers.insert(0, 'CUDAExecutionProvider')
        
        session = ort.InferenceSession(onnx_path, providers=providers)
        input_np = test_input.cpu().numpy()
        onnx_output = session.run(None, {'input': input_np})[0]
        
        # Calculate error metrics
        abs_error = np.abs(pytorch_output - onnx_output)
        max_abs_error = np.max(abs_error)
        mean_abs_error = np.mean(abs_error)
        
        # Calculate PSNR (Peak Signal-to-Noise Ratio)
        mse = np.mean((pytorch_output - onnx_output) ** 2)
        if mse == 0:
            psnr = 100.0  # Perfect match
        else:
            max_pixel = np.max(pytorch_output)
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        
        # Calculate SSIM (Structural Similarity Index) - simplified version
        # For full SSIM, use skimage.metrics.structural_similarity
        ssim = 1.0 - (mse / (np.var(pytorch_output) + 1e-10))
        
        # Determine if validation passed
        passed = (max_abs_error < 0.01 and mean_abs_error < 0.001)
        
        return ValidationMetrics(
            max_absolute_error=max_abs_error,
            mean_absolute_error=mean_abs_error,
            psnr_db=psnr,
            ssim=ssim,
            passed=passed
        )
    
    def _quantize_to_int8(self, onnx_path: str) -> str:
        """
        Quantize ONNX model to INT8.
        
        Note: Requires onnxruntime-training package
        """
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType
            
            output_path = onnx_path.replace('.onnx', '_int8.onnx')
            
            quantize_dynamic(
                onnx_path,
                output_path,
                weight_type=QuantType.QUInt8
            )
            
            return output_path
        
        except ImportError:
            self._log("Warning: onnxruntime-training not installed, skipping INT8 quantization")
            return onnx_path
    
    def batch_convert_models(
        self,
        model_configs: List[Dict]
    ) -> List[ConversionResult]:
        """
        Convert multiple models in batch.
        
        Args:
            model_configs: List of dicts with keys:
                - pytorch_model: Model instance
                - input_shape: Input shape tuple
                - model_name: Name for logging
                - output_path: Where to save
        
        Returns:
            List of ConversionResult objects
        """
        results = []
        
        for i, config in enumerate(model_configs, 1):
            self._log(f"\n=== Converting model {i}/{len(model_configs)}: {config['model_name']} ===")
            
            result = self.convert_model(
                pytorch_model=config['pytorch_model'],
                input_shape=config['input_shape'],
                output_path=config['output_path'],
                model_name=config['model_name'],
                quantization=config.get('quantization', QuantizationMode.FP16),
                validate=config.get('validate', True)
            )
            
            results.append(result)
        
        # Summary
        self._log(f"\n=== Batch Conversion Summary ===")
        successful = sum(1 for r in results if r.success)
        self._log(f"Successful: {successful}/{len(results)}")
        
        for i, result in enumerate(results, 1):
            status = "✓" if result.success else "✗"
            model_name = model_configs[i-1]['model_name']
            self._log(f"  {status} {model_name}")
        
        return results


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ONNX Converter Test")
    parser.add_argument("--test", action="store_true", help="Run simple conversion test")
    parser.add_argument("--model", type=str, help="Model name to convert (gfpgan, realesrgan)")
    args = parser.parse_args()
    
    converter = ONNXConverter()
    
    if args.test:
        print("\n=== ONNX Converter Test ===\n")
        
        # Create a simple test model
        class SimpleTestModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = torch.nn.Conv2d(3, 64, 3, padding=1)
                self.relu = torch.nn.ReLU()
                self.conv2 = torch.nn.Conv2d(64, 3, 3, padding=1)
            
            def forward(self, x):
                x = self.conv1(x)
                x = self.relu(x)
                x = self.conv2(x)
                return x
        
        test_model = SimpleTestModel()
        
        result = converter.convert_model(
            pytorch_model=test_model,
            input_shape=(1, 3, 256, 256),
            output_path=str(converter.output_dir / "test_model.onnx"),
            model_name="SimpleTestModel",
            quantization=QuantizationMode.FP16,
            validate=True
        )
        
        if result.success:
            print(f"\n✓ Conversion successful!")
            print(f"  Original size: {result.original_size_mb:.2f} MB")
            print(f"  ONNX size: {result.onnx_size_mb:.2f} MB")
            print(f"  Compression: {(1 - result.onnx_size_mb/result.original_size_mb)*100:.1f}%")
            print(f"  Validation: {'PASSED' if result.validation_passed else 'FAILED'}")
            print(f"  Max error: {result.max_error:.6f}")
            print(f"  Mean error: {result.mean_error:.6f}")
            print(f"  PyTorch inference: {result.inference_time_pytorch_ms:.2f} ms")
            print(f"  ONNX inference: {result.inference_time_onnx_ms:.2f} ms")
            print(f"  Speedup: {result.speedup_factor:.2f}x")
            print(f"  Saved to: {result.onnx_path}")
        else:
            print(f"\n✗ Conversion failed: {result.error_message}")
    
    elif args.model:
        print(f"Converting {args.model} model...")
        print("Note: This requires the actual model to be loaded.")
        print("Use this in integration with ai_models/ package.")
    
    else:
        parser.print_help()
