"""
Multi-GPU Manager for Heterogeneous GPU Setups
==============================================

Manages workload distribution across multiple GPUs (NVIDIA, AMD, integrated).

Architecture:
- NVIDIA CUDA GPUs: AI models (PyTorch), NVENC encoding
- AMD GPUs: AMF encoding, OpenCL filters
- Intel/AMD integrated: Video decoding, preprocessing
- CPU fallback: When no GPU available

Limitations:
- PyTorch AI models require CUDA (NVIDIA only on Windows)
- AMD ROCm support limited to Linux
- Can't mix CUDA/ROCm in same PyTorch process
- VapourSynth filters are backend-specific

Strategy:
1. Detect all GPUs and categorize by vendor
2. Assign AI workload to NVIDIA GPUs (CUDA)
3. Assign encoding to best available (NVENC > AMF > CPU)
4. Use integrated GPUs for decode assist
5. For multi-segment processing: Distribute across all capable GPUs

Author: Advanced Tape Restorer Team
License: MIT
"""

import os
import sys
import platform
import subprocess
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class InferenceMode(Enum):
    """AI model inference mode based on GPU capabilities"""
    PYTORCH_FP32 = "pytorch_fp32"    # Full precision PyTorch (best quality, high VRAM)
    PYTORCH_FP16 = "pytorch_fp16"    # Half precision PyTorch (good quality, medium VRAM)
    ONNX_FP16 = "onnx_fp16"          # ONNX half precision (good quality, low VRAM)
    ONNX_INT8 = "onnx_int8"          # ONNX quantized (acceptable quality, very low VRAM)
    CPU_ONLY = "cpu_only"            # CPU fallback (slow but always works)


class GPUVendor(Enum):
    """GPU vendor enumeration"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    UNKNOWN = "unknown"


class GPUCapability(Enum):
    """GPU capability flags"""
    CUDA = "cuda"              # NVIDIA CUDA compute
    ROCM = "rocm"              # AMD ROCm compute (Linux only)
    OPENCL = "opencl"          # Universal compute (limited)
    NVENC = "nvenc"            # NVIDIA hardware encoding
    NVDEC = "nvdec"            # NVIDIA hardware decoding
    AMF = "amf"                # AMD Advanced Media Framework
    VCE = "vce"                # AMD Video Coding Engine (encoding)
    UVD = "uvd"                # AMD Unified Video Decoder
    QUICKSYNC = "quicksync"    # Intel Quick Sync Video
    VULKAN = "vulkan"          # Vulkan compute
    NPU = "npu"                # Neural Processing Unit (AMD XDNA)


@dataclass
class GPUInfo:
    """Information about a detected GPU"""
    index: int                          # GPU index (0, 1, 2...)
    vendor: GPUVendor                   # NVIDIA, AMD, Intel
    name: str                           # GPU model name
    memory_total: int                   # Total VRAM in MB
    memory_available: int               # Available VRAM in MB
    capabilities: List[GPUCapability]   # Supported features
    compute_units: int                  # CUDA cores / Stream processors
    is_integrated: bool                 # True for APU/iGPU
    pcie_gen: Optional[int]             # PCIe generation (3, 4, 5)
    driver_version: Optional[str]       # Driver version
    npu_tops: Optional[float]           # NPU TOPS (if NPU present)
    
    def supports(self, capability: GPUCapability) -> bool:
        """Check if GPU supports a capability"""
        return capability in self.capabilities
    
    def get_ai_score(self) -> float:
        """Calculate AI workload suitability score (0-100)"""
        score = 0.0
        
        # NPU is highly efficient for AI inference (50 TOPS on Ryzen AI)
        if self.supports(GPUCapability.NPU) and self.npu_tops:
            score += 40.0  # Base NPU score
            score += min(30.0, self.npu_tops / 2.0)  # Max 30 pts for 60+ TOPS
        
        # CUDA is primary AI backend
        elif self.supports(GPUCapability.CUDA):
            score += 50.0
            # More VRAM = better for AI
            score += min(30.0, self.memory_total / 1024.0 * 3)  # Max 30 pts for 10GB+
            # More CUDA cores = faster
            score += min(20.0, self.compute_units / 500.0)  # Max 20 pts for 10000+ cores
        
        # ROCm support (Linux only, less mature)
        elif self.supports(GPUCapability.ROCM):
            score += 30.0
            score += min(20.0, self.memory_total / 1024.0 * 2)
            score += min(10.0, self.compute_units / 1000.0)
        
        # OpenCL fallback (slow)
        elif self.supports(GPUCapability.OPENCL):
            score += 10.0
        
        # Penalty for integrated GPUs (shared memory)
        if self.is_integrated:
            score *= 0.5
        
        return min(100.0, score)
    
    def get_encode_score(self) -> float:
        """Calculate encoding suitability score (0-100)"""
        score = 0.0
        
        # NVENC is best quality/speed
        if self.supports(GPUCapability.NVENC):
            score += 90.0
        
        # AMF is good
        elif self.supports(GPUCapability.AMF) or self.supports(GPUCapability.VCE):
            score += 80.0
        
        # Quick Sync is decent
        elif self.supports(GPUCapability.QUICKSYNC):
            score += 70.0
        
        # More VRAM helps with high-res encoding
        score += min(10.0, self.memory_total / 2048.0 * 10)
        
        return min(100.0, score)


class MultiGPUManager:
    """
    Manages multiple GPUs for distributed video processing.
    
    Detects NVIDIA, AMD, and Intel GPUs and assigns workload
    based on capabilities.
    """
    
    def __init__(self, log_callback=None):
        """
        Initialize multi-GPU manager.
        
        Args:
            log_callback: Optional callback for logging (func(str))
        """
        self.gpus: List[GPUInfo] = []
        self.log_callback = log_callback
        self.platform = platform.system()
        
        # Detect all GPUs
        self._detect_gpus()
    
    def _log(self, message: str):
        """Internal logging"""
        if self.log_callback:
            self.log_callback(message)
    
    def _detect_gpus(self):
        """Detect all available GPUs"""
        self._log("Detecting GPUs...")
        
        # Try NVIDIA CUDA GPUs first
        nvidia_gpus = self._detect_nvidia_gpus()
        self.gpus.extend(nvidia_gpus)
        
        # Try AMD GPUs
        amd_gpus = self._detect_amd_gpus()
        self.gpus.extend(amd_gpus)
        
        # Try Intel GPUs
        intel_gpus = self._detect_intel_gpus()
        self.gpus.extend(intel_gpus)
        
        # Try AMD NPU (Ryzen AI)
        npu_device = self._detect_amd_npu()
        if npu_device:
            self.gpus.append(npu_device)
        
        if not self.gpus:
            self._log("No GPUs detected, CPU-only mode")
        else:
            self._log(f"Detected {len(self.gpus)} GPU(s)")
            for gpu in self.gpus:
                self._log(f"  [{gpu.index}] {gpu.vendor.value.upper()}: {gpu.name} "
                         f"({gpu.memory_total}MB, AI score: {gpu.get_ai_score():.1f})")
    
    def _detect_nvidia_gpus(self) -> List[GPUInfo]:
        """Detect NVIDIA GPUs via nvidia-smi"""
        gpus = []
        
        try:
            # Try nvidia-smi first (most reliable)
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free,"
                 "compute_cap,driver_version,pcie.link.gen.current",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line.strip():
                        continue
                    
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        index = int(parts[0])
                        name = parts[1]
                        mem_total = int(float(parts[2]))
                        mem_free = int(float(parts[3]))
                        compute_cap = parts[4]
                        driver = parts[5] if len(parts) > 5 else None
                        pcie_gen = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None
                        
                        # Estimate CUDA cores (rough approximation)
                        cuda_cores = self._estimate_cuda_cores(name, compute_cap)
                        
                        capabilities = [
                            GPUCapability.CUDA,
                            GPUCapability.NVENC,
                            GPUCapability.NVDEC,
                            GPUCapability.VULKAN
                        ]
                        
                        gpu = GPUInfo(
                            index=index,
                            vendor=GPUVendor.NVIDIA,
                            name=name,
                            memory_total=mem_total,
                            memory_available=mem_free,
                            capabilities=capabilities,
                            compute_units=cuda_cores,
                            is_integrated=False,  # NVIDIA doesn't make integrated GPUs
                            pcie_gen=pcie_gen,
                            driver_version=driver,
                            npu_tops=None
                        )
                        gpus.append(gpu)
                        self._log(f"Detected NVIDIA GPU: {name} ({mem_total}MB, {cuda_cores} CUDA cores)")
        
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            # Try PyTorch CUDA detection as fallback
            try:
                import torch
                if torch.cuda.is_available():
                    for i in range(torch.cuda.device_count()):
                        props = torch.cuda.get_device_properties(i)
                        name = props.name
                        mem_total = props.total_memory // (1024 * 1024)
                        cuda_cores = props.multi_processor_count * 128  # Rough estimate
                        
                        capabilities = [
                            GPUCapability.CUDA,
                            GPUCapability.NVENC,
                            GPUCapability.NVDEC
                        ]
                        
                        gpu = GPUInfo(
                            index=i,
                            vendor=GPUVendor.NVIDIA,
                            name=name,
                            memory_total=mem_total,
                            memory_available=mem_total,  # Approximate
                            capabilities=capabilities,
                            compute_units=cuda_cores,
                            is_integrated=False,
                            pcie_gen=None,
                            driver_version=None,
                            npu_tops=None
                        )
                        gpus.append(gpu)
                        self._log(f"Detected NVIDIA GPU via PyTorch: {name}")
            except ImportError:
                pass
        
        return gpus
    
    def _detect_amd_gpus(self) -> List[GPUInfo]:
        """Detect AMD GPUs via rocm-smi or FFmpeg"""
        gpus = []
        
        # Try rocm-smi (Linux only)
        if self.platform == "Linux":
            try:
                result = subprocess.run(
                    ["rocm-smi", "--showproductname", "--showmeminfo", "vram"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Parse rocm-smi output (format varies by version)
                    # This is a simplified parser
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines):
                        if "GPU" in line and i + 1 < len(lines):
                            # Extract GPU info (very basic)
                            name = "AMD GPU"
                            mem_total = 4096  # Default estimate
                            
                            capabilities = [
                                GPUCapability.ROCM,
                                GPUCapability.OPENCL,
                                GPUCapability.AMF,
                                GPUCapability.VCE,
                                GPUCapability.VULKAN
                            ]
                            
                            gpu = GPUInfo(
                                index=len(gpus),
                                vendor=GPUVendor.AMD,
                                name=name,
                                memory_total=mem_total,
                                memory_available=mem_total,
                                capabilities=capabilities,
                                compute_units=2048,  # Estimate
                                is_integrated=False,
                                pcie_gen=None,
                                driver_version=None
                            )
                            gpus.append(gpu)
                            self._log(f"Detected AMD GPU via ROCm: {name}")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        # Try detecting via FFmpeg hardware encoders
        if not gpus:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-hide_banner", "-encoders"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and "h264_amf" in result.stdout:
                    # AMD AMF encoder is available
                    
                    # Check if it's integrated (Ryzen APU) by checking for AMD CPU
                    is_integrated = False
                    gpu_name = "AMD Radeon GPU"
                    
                    try:
                        # Check CPU name on Windows using PowerShell
                        if self.platform == "Windows":
                            cpu_result = subprocess.run(
                                ["powershell", "-Command", 
                                 "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"],
                                capture_output=True,
                                text=True,
                                timeout=3
                            )
                            if cpu_result.returncode == 0:
                                cpu_name = cpu_result.stdout.strip().lower()
                                if "ryzen" in cpu_name:
                                    is_integrated = True
                                    # Extract GPU model from CPU name (e.g., "Radeon 860M")
                                    if "radeon" in cpu_name:
                                        # Extract everything after "w/" or "with"
                                        parts = cpu_name.split("w/") if "w/" in cpu_name else cpu_name.split("with")
                                        if len(parts) > 1:
                                            gpu_model = parts[1].strip()
                                            gpu_name = f"AMD {gpu_model.title()} (Ryzen APU)"
                                        else:
                                            gpu_name = "AMD Radeon Graphics (Ryzen APU)"
                                    else:
                                        gpu_name = "AMD Radeon Graphics (Ryzen APU)"
                    except Exception:
                        pass
                    
                    if not is_integrated:
                        gpu_name = "AMD Radeon GPU (discrete)"
                    
                    self._log(f"Detected AMD GPU via FFmpeg AMF encoder: {gpu_name}")
                    
                    capabilities = [
                        GPUCapability.OPENCL,
                        GPUCapability.AMF,
                        GPUCapability.VCE,
                        GPUCapability.UVD,
                        GPUCapability.VULKAN
                    ]
                    
                    gpu = GPUInfo(
                        index=len(gpus),
                        vendor=GPUVendor.AMD,
                        name=gpu_name,
                        memory_total=2048 if is_integrated else 4096,
                        memory_available=2048 if is_integrated else 4096,
                        capabilities=capabilities,
                        compute_units=768 if is_integrated else 2048,  # 860M has ~768 cores
                        is_integrated=is_integrated,
                        pcie_gen=None,
                        driver_version=None,
                        npu_tops=None
                    )
                    gpus.append(gpu)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        return gpus
    
    def _detect_intel_gpus(self) -> List[GPUInfo]:
        """Detect Intel GPUs via Quick Sync detection"""
        gpus = []
        
        # Only check for Intel GPU if processor is Intel
        processor_info = platform.processor().lower()
        if "intel" not in processor_info:
            # Not an Intel system, skip detection
            return gpus
        
        try:
            # Check for Intel Quick Sync via FFmpeg
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "h264_qsv" in result.stdout:
                self._log("Detected Intel GPU via Quick Sync")
                
                capabilities = [
                    GPUCapability.QUICKSYNC,
                    GPUCapability.OPENCL,
                    GPUCapability.VULKAN
                ]
                
                gpu = GPUInfo(
                    index=len(gpus),
                    vendor=GPUVendor.INTEL,
                    name="Intel Integrated GPU (Quick Sync)",
                    memory_total=1024,  # Shared memory
                    memory_available=1024,
                    capabilities=capabilities,
                    compute_units=256,  # Rough estimate
                    is_integrated=True,
                    pcie_gen=None,
                    driver_version=None,
                    npu_tops=None
                )
                gpus.append(gpu)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return gpus
    
    def _detect_amd_npu(self) -> Optional[GPUInfo]:
        """Detect AMD XDNA NPU (Neural Processing Unit) on Ryzen AI systems"""
        
        # Only check on Windows AMD systems
        if self.platform != "Windows":
            return None
        
        try:
            # Check for xrt-smi.exe (AMD NPU management tool)
            xrt_smi_path = r"C:\Windows\System32\AMD\xrt-smi.exe"
            if not os.path.exists(xrt_smi_path):
                return None
            
            # Query NPU status
            result = subprocess.run(
                [xrt_smi_path, "examine"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "NPU" in result.stdout:
                # NPU detected, determine TOPS based on processor
                npu_tops = 50.0  # Default for Ryzen AI 7/5 series
                npu_name = "AMD XDNA NPU"
                
                try:
                    # Get CPU name to determine NPU generation
                    cpu_result = subprocess.run(
                        ["powershell", "-Command",
                         "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    
                    if cpu_result.returncode == 0:
                        cpu_name = cpu_result.stdout.strip().lower()
                        
                        if "ryzen ai 9" in cpu_name:
                            npu_tops = 55.0  # Future models
                            npu_name = "AMD XDNA 2 NPU (Ryzen AI 9)"
                        elif "ryzen ai 7" in cpu_name or "ryzen 7 ai" in cpu_name:
                            npu_tops = 50.0  # Current models (350, 370)
                            npu_name = "AMD XDNA 2 NPU (Ryzen AI 7)"
                        elif "ryzen ai 5" in cpu_name or "ryzen 5 ai" in cpu_name:
                            npu_tops = 45.0  # Lower SKUs
                            npu_name = "AMD XDNA 2 NPU (Ryzen AI 5)"
                except Exception:
                    pass
                
                self._log(f"Detected {npu_name} ({npu_tops} TOPS)")
                
                capabilities = [
                    GPUCapability.NPU,
                    GPUCapability.OPENCL  # NPU may support OpenCL
                ]
                
                npu_device = GPUInfo(
                    index=len(self.gpus),
                    vendor=GPUVendor.AMD,
                    name=npu_name,
                    memory_total=4096,  # Shared system memory
                    memory_available=4096,
                    capabilities=capabilities,
                    compute_units=0,  # NPU uses different architecture
                    is_integrated=True,
                    pcie_gen=None,
                    driver_version=None,
                    npu_tops=npu_tops
                )
                
                return npu_device
        
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            # NPU not available or error occurred
            pass
        
        return None
    
    def _estimate_cuda_cores(self, gpu_name: str, compute_cap: str) -> int:
        """Estimate CUDA core count from GPU name"""
        # Rough estimates for common GPUs
        estimates = {
            "4090": 16384, "4080": 9728, "4070": 5888, "4060": 3072,
            "3090": 10496, "3080": 8704, "3070": 5888, "3060": 3584,
            "2080": 2944, "2070": 2304, "2060": 1920,
            "1080": 2560, "1070": 1920, "1060": 1280,
            "A6000": 10752, "A5000": 8192, "A4000": 6144,
            "RTX 6000": 4608, "RTX 5000": 3072
        }
        
        for key, cores in estimates.items():
            if key in gpu_name:
                return cores
        
        # Default estimate based on compute capability
        if compute_cap.startswith("8."):  # Ampere/Ada
            return 5000
        elif compute_cap.startswith("7."):  # Turing
            return 3000
        else:
            return 2000
    
    def get_gpu_count(self) -> int:
        """Get total number of detected GPUs"""
        return len(self.gpus)
    
    def get_gpus(self, vendor: Optional[GPUVendor] = None) -> List[GPUInfo]:
        """
        Get list of GPUs, optionally filtered by vendor.
        
        Args:
            vendor: Filter by vendor (None = all)
        
        Returns:
            List of GPUInfo objects
        """
        if vendor is None:
            return self.gpus.copy()
        return [gpu for gpu in self.gpus if gpu.vendor == vendor]
    
    def get_best_ai_gpu(self) -> Optional[GPUInfo]:
        """Get the best GPU for AI workloads (highest AI score)"""
        if not self.gpus:
            return None
        return max(self.gpus, key=lambda g: g.get_ai_score())
    
    def get_best_encode_gpu(self) -> Optional[GPUInfo]:
        """Get the best GPU for encoding (highest encode score)"""
        if not self.gpus:
            return None
        return max(self.gpus, key=lambda g: g.get_encode_score())
    
    def get_ai_capable_gpus(self, min_vram_mb: int = 4096) -> List[GPUInfo]:
        """
        Get GPUs capable of AI workloads with minimum VRAM.
        
        Args:
            min_vram_mb: Minimum VRAM in MB (default 4GB)
        
        Returns:
            List of AI-capable GPUs sorted by score (best first)
        """
        capable = [
            gpu for gpu in self.gpus
            if gpu.supports(GPUCapability.CUDA) or gpu.supports(GPUCapability.ROCM)
            if gpu.memory_total >= min_vram_mb
        ]
        return sorted(capable, key=lambda g: g.get_ai_score(), reverse=True)
    
    def assign_workload(self, num_segments: int) -> List[Tuple[int, GPUInfo]]:
        """
        Assign video segments to GPUs based on capabilities.
        
        Args:
            num_segments: Number of video segments to process
        
        Returns:
            List of (segment_index, gpu) tuples
        """
        if not self.gpus:
            return [(i, None) for i in range(num_segments)]
        
        # Get AI-capable GPUs
        ai_gpus = self.get_ai_capable_gpus()
        
        if not ai_gpus:
            # Use best encode GPU if no AI GPUs
            best_gpu = self.get_best_encode_gpu()
            return [(i, best_gpu) for i in range(num_segments)]
        
        # Distribute segments round-robin weighted by AI score
        assignments = []
        gpu_weights = [gpu.get_ai_score() for gpu in ai_gpus]
        total_weight = sum(gpu_weights)
        
        # Calculate how many segments each GPU should handle
        gpu_segments = []
        for i, weight in enumerate(gpu_weights):
            count = max(1, int(num_segments * (weight / total_weight)))
            gpu_segments.append(count)
        
        # Adjust to exactly match num_segments
        diff = num_segments - sum(gpu_segments)
        if diff > 0:
            gpu_segments[0] += diff
        elif diff < 0:
            gpu_segments[-1] += diff
        
        # Create assignments
        segment_idx = 0
        for gpu_idx, count in enumerate(gpu_segments):
            for _ in range(count):
                if segment_idx < num_segments:
                    assignments.append((segment_idx, ai_gpus[gpu_idx]))
                    segment_idx += 1
        
        return assignments
    
    def get_ffmpeg_encoder(self, gpu: Optional[GPUInfo] = None) -> str:
        """
        Get optimal FFmpeg encoder for given GPU.
        
        Args:
            gpu: Target GPU (None = auto-select best)
        
        Returns:
            FFmpeg encoder name (e.g., "h264_nvenc", "h264_amf")
        """
        if gpu is None:
            gpu = self.get_best_encode_gpu()
        
        if gpu is None:
            return "libx264"  # CPU fallback
        
        if gpu.supports(GPUCapability.NVENC):
            return "h264_nvenc"
        elif gpu.supports(GPUCapability.AMF):
            return "h264_amf"
        elif gpu.supports(GPUCapability.QUICKSYNC):
            return "h264_qsv"
        else:
            return "libx264"
    
    def get_recommended_inference_mode(
        self,
        target_model_size_mb: int = 800,
        prefer_quality: bool = True
    ) -> Tuple[InferenceMode, str]:
        """
        Recommend optimal inference mode based on GPU VRAM.
        
        Args:
            target_model_size_mb: Expected model VRAM usage (default: 800MB for RealESRGAN)
            prefer_quality: If True, use higher quality when VRAM allows
        
        Returns:
            Tuple of (InferenceMode, explanation string)
        """
        
        best_gpu = self.get_best_ai_gpu()
        
        if not best_gpu:
            return (InferenceMode.CPU_ONLY, 
                    "No GPU detected. Using CPU inference (slow but functional).")
        
        available_vram = best_gpu.memory_available
        
        # VRAM thresholds for different modes
        # Assumes model + working memory + output buffer
        vram_needed_fp32 = target_model_size_mb * 2.5  # PyTorch overhead
        vram_needed_fp16 = target_model_size_mb * 1.5  # 50% smaller
        vram_needed_int8 = target_model_size_mb * 1.0  # 75% smaller
        
        # Decision logic
        if available_vram >= vram_needed_fp32 and prefer_quality:
            return (InferenceMode.PYTORCH_FP32,
                    f"High VRAM available ({available_vram}MB). Using PyTorch FP32 for best quality.")
        
        elif available_vram >= vram_needed_fp16:
            if best_gpu.supports(GPUCapability.CUDA) and prefer_quality:
                return (InferenceMode.PYTORCH_FP16,
                        f"Good VRAM available ({available_vram}MB). Using PyTorch FP16 (same quality, 2x faster).")
            else:
                return (InferenceMode.ONNX_FP16,
                        f"Moderate VRAM ({available_vram}MB). Using ONNX FP16 for better compatibility.")
        
        elif available_vram >= vram_needed_int8:
            return (InferenceMode.ONNX_INT8,
                    f"Low VRAM ({available_vram}MB). Using ONNX INT8 quantization (some quality loss).")
        
        else:
            return (InferenceMode.CPU_ONLY,
                    f"Very low VRAM ({available_vram}MB). Falling back to CPU inference.")
    
    def get_info(self) -> Dict:
        """Get comprehensive multi-GPU info as dict"""
        return {
            "platform": self.platform,
            "gpu_count": len(self.gpus),
            "gpus": [
                {
                    "index": gpu.index,
                    "vendor": gpu.vendor.value,
                    "name": gpu.name,
                    "memory_total_mb": gpu.memory_total,
                    "memory_available_mb": gpu.memory_available,
                    "capabilities": [c.value for c in gpu.capabilities],
                    "compute_units": gpu.compute_units,
                    "is_integrated": gpu.is_integrated,
                    "pcie_gen": gpu.pcie_gen,
                    "ai_score": round(gpu.get_ai_score(), 1),
                    "encode_score": round(gpu.get_encode_score(), 1),
                    "npu_tops": gpu.npu_tops
                }
                for gpu in self.gpus
            ],
            "best_ai_gpu": self.get_best_ai_gpu().name if self.get_best_ai_gpu() else None,
            "best_encode_gpu": self.get_best_encode_gpu().name if self.get_best_encode_gpu() else None,
        }


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-GPU Manager Test")
    parser.add_argument("--info", action="store_true", help="Show GPU info")
    parser.add_argument("--assign", type=int, metavar="N", help="Test workload assignment with N segments")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    def log_print(msg):
        if not args.json:
            print(f"[MultiGPU] {msg}")
    
    manager = MultiGPUManager(log_callback=log_print)
    
    if args.info:
        if args.json:
            print(json.dumps(manager.get_info(), indent=2))
        else:
            print("\n=== Multi-GPU Manager Info ===")
            print(f"Platform: {manager.platform}")
            print(f"Total GPUs: {manager.get_gpu_count()}")
            print()
            
            if manager.get_gpu_count() == 0:
                print("No GPUs detected (CPU-only mode)")
            else:
                for gpu in manager.gpus:
                    print(f"GPU {gpu.index}: {gpu.name}")
                    print(f"  Vendor: {gpu.vendor.value.upper()}")
                    print(f"  Memory: {gpu.memory_total}MB total, {gpu.memory_available}MB available")
                    print(f"  Compute Units: {gpu.compute_units}")
                    print(f"  Integrated: {gpu.is_integrated}")
                    print(f"  Capabilities: {', '.join(c.value for c in gpu.capabilities)}")
                    print(f"  AI Score: {gpu.get_ai_score():.1f}/100")
                    print(f"  Encode Score: {gpu.get_encode_score():.1f}/100")
                    if gpu.driver_version:
                        print(f"  Driver: {gpu.driver_version}")
                    print()
                
                best_ai = manager.get_best_ai_gpu()
                best_encode = manager.get_best_encode_gpu()
                
                print("Recommendations:")
                print(f"  Best for AI: {best_ai.name if best_ai else 'None'}")
                print(f"  Best for Encoding: {best_encode.name if best_encode else 'None'}")
                print(f"  FFmpeg Encoder: {manager.get_ffmpeg_encoder()}")
    
    elif args.assign:
        num_segments = args.assign
        assignments = manager.assign_workload(num_segments)
        
        if args.json:
            result = [
                {"segment": seg, "gpu_index": gpu.index if gpu else None, "gpu_name": gpu.name if gpu else "CPU"}
                for seg, gpu in assignments
            ]
            print(json.dumps(result, indent=2))
        else:
            print(f"\n=== Workload Assignment ({num_segments} segments) ===")
            for seg, gpu in assignments:
                if gpu:
                    print(f"Segment {seg:2d} → GPU {gpu.index} ({gpu.name})")
                else:
                    print(f"Segment {seg:2d} → CPU")
    
    else:
        parser.print_help()
