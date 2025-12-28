"""
Auto Mode Selector - Intelligent inference mode detection for ATR v4.1

Automatically detects GPU capabilities and recommends optimal inference mode.
Users can override via GUI settings.

Author: Advanced Tape Restorer Team
License: MIT
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import json

from core.multi_gpu_manager import MultiGPUManager, InferenceMode


@dataclass
class AutoModeResult:
    """Result of automatic mode selection"""
    recommended_mode: InferenceMode
    explanation: str
    can_override: bool
    override_warning: Optional[str] = None
    vram_available: int = 0
    vram_required: int = 0


class AutoModeSelector:
    """
    Automatically select optimal inference mode based on:
    - Available GPU VRAM
    - Target AI model requirements
    - User preferences (quality vs performance vs battery)
    - Historical OOM events
    """
    
    # Model VRAM requirements (MB) - approximate peak usage
    MODEL_VRAM_REQUIREMENTS = {
        "realesrgan": 1200,      # RealESRGAN 4x upscaling
        "basicvsr++": 2400,      # BasicVSR++ video restoration
        "swinir": 1800,          # SwinIR transformer upscaling
        "rife": 800,             # RIFE frame interpolation
        "gfpgan": 1000,          # GFPGAN face restoration
        "propainter": 3200,      # ProPainter video inpainting
        "deoldify": 600,         # DeOldify colorization
        "znedi3": 400,           # ZNEDI3 fast upscaling
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize auto mode selector.
        
        Args:
            config_path: Path to user preferences JSON (overrides)
        """
        self.multi_gpu = MultiGPUManager()
        self.config_path = config_path or Path.home() / "AppData" / "Local" / "Advanced_Tape_Restorer" / "auto_mode_config.json"
        self.user_preferences = self._load_preferences()
        self.oom_history = []  # Track OOM events to adjust recommendations
    
    def _load_preferences(self) -> Dict:
        """Load user preferences from config file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default preferences
        return {
            "auto_mode_enabled": True,
            "prefer_quality": True,
            "prefer_battery": False,
            "manual_override": None,  # None = auto, or InferenceMode value
            "warned_low_vram": False,
        }
    
    def _save_preferences(self):
        """Save user preferences to config file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save preferences: {e}")
    
    def detect_best_mode(
        self,
        target_model: str = "realesrgan",
        force_auto: bool = False
    ) -> AutoModeResult:
        """
        Detect the best inference mode for the user's system.
        
        Args:
            target_model: Name of AI model to run (affects VRAM requirement)
            force_auto: Ignore manual override and detect automatically
        
        Returns:
            AutoModeResult with recommendation and explanation
        """
        
        # Check for manual override
        if not force_auto and self.user_preferences.get("manual_override"):
            override_mode = InferenceMode(self.user_preferences["manual_override"])
            return AutoModeResult(
                recommended_mode=override_mode,
                explanation=f"Using manual override: {override_mode.value}",
                can_override=True,
                vram_available=self.multi_gpu.get_best_ai_gpu().memory_available if self.multi_gpu.get_best_ai_gpu() else 0
            )
        
        # Check if auto mode is disabled
        if not self.user_preferences.get("auto_mode_enabled", True) and not force_auto:
            # Default to PyTorch FP32 if auto disabled
            return AutoModeResult(
                recommended_mode=InferenceMode.PYTORCH_FP32,
                explanation="Auto-detection disabled. Using default PyTorch FP32.",
                can_override=True
            )
        
        # Get VRAM requirement for target model
        vram_required = self.MODEL_VRAM_REQUIREMENTS.get(target_model.lower(), 1000)
        
        # Get recommendation from GPU manager
        prefer_quality = self.user_preferences.get("prefer_quality", True)
        mode, explanation = self.multi_gpu.get_recommended_inference_mode(
            target_model_size_mb=vram_required,
            prefer_quality=prefer_quality
        )
        
        # Get available VRAM
        best_gpu = self.multi_gpu.get_best_ai_gpu()
        vram_available = best_gpu.memory_available if best_gpu else 0
        
        # Check if we should warn about low VRAM
        override_warning = None
        if mode in [InferenceMode.ONNX_INT8, InferenceMode.CPU_ONLY]:
            if not self.user_preferences.get("warned_low_vram", False):
                override_warning = (
                    f"Your GPU has limited VRAM ({vram_available}MB). "
                    f"We recommend using {mode.value} for stability. "
                    f"You can override this in Settings, but may encounter out-of-memory errors."
                )
                self.user_preferences["warned_low_vram"] = True
                self._save_preferences()
        
        return AutoModeResult(
            recommended_mode=mode,
            explanation=explanation,
            can_override=True,
            override_warning=override_warning,
            vram_available=vram_available,
            vram_required=vram_required
        )
    
    def set_manual_override(self, mode: Optional[InferenceMode]):
        """
        Set manual inference mode override.
        
        Args:
            mode: InferenceMode to force, or None to re-enable auto
        """
        if mode is None:
            self.user_preferences["manual_override"] = None
            self.user_preferences["auto_mode_enabled"] = True
        else:
            self.user_preferences["manual_override"] = mode.value
            self.user_preferences["auto_mode_enabled"] = False
        
        self._save_preferences()
    
    def report_oom(self, mode: InferenceMode, model: str):
        """
        Report an out-of-memory error to adjust future recommendations.
        
        Args:
            mode: Inference mode that caused OOM
            model: Model name that caused OOM
        """
        self.oom_history.append({
            "mode": mode.value,
            "model": model,
            "vram_available": self.multi_gpu.get_best_ai_gpu().memory_available if self.multi_gpu.get_best_ai_gpu() else 0
        })
        
        # If PyTorch FP32 caused OOM, downgrade recommendation
        if mode == InferenceMode.PYTORCH_FP32:
            self.user_preferences["prefer_quality"] = False
            self._save_preferences()
    
    def get_mode_info(self, mode: InferenceMode) -> Dict:
        """
        Get detailed information about an inference mode.
        
        Args:
            mode: Inference mode to get info for
        
        Returns:
            Dict with quality, speed, VRAM usage, compatibility info
        """
        info = {
            InferenceMode.PYTORCH_FP32: {
                "quality": "Best (100%)",
                "speed": "Slower",
                "vram_usage": "High (100%)",
                "compatibility": "Requires CUDA GPU",
                "description": "Full precision PyTorch inference. Best quality, highest VRAM usage."
            },
            InferenceMode.PYTORCH_FP16: {
                "quality": "Excellent (99%)",
                "speed": "Fast",
                "vram_usage": "Medium (60%)",
                "compatibility": "Requires CUDA GPU",
                "description": "Half precision PyTorch inference. Near-identical quality, 2x faster, 50% less VRAM."
            },
            InferenceMode.ONNX_FP16: {
                "quality": "Excellent (98%)",
                "speed": "Very Fast",
                "vram_usage": "Low (50%)",
                "compatibility": "Any GPU or NPU",
                "description": "ONNX optimized inference. Great quality, works on AMD/Intel/NPU, 50% less VRAM."
            },
            InferenceMode.ONNX_INT8: {
                "quality": "Good (90-95%)",
                "speed": "Very Fast",
                "vram_usage": "Very Low (25%)",
                "compatibility": "Any GPU or NPU",
                "description": "ONNX quantized inference. Some quality loss, works on very low VRAM GPUs (2-4GB)."
            },
            InferenceMode.CPU_ONLY: {
                "quality": "Best (100%)",
                "speed": "Very Slow",
                "vram_usage": "None (uses RAM)",
                "compatibility": "Always works",
                "description": "CPU inference fallback. Slow but functional on any system."
            }
        }
        
        return info.get(mode, {})


if __name__ == "__main__":
    """CLI test utility"""
    import sys
    
    selector = AutoModeSelector()
    
    if "--test" in sys.argv:
        print("\n=== Auto Mode Selector Test ===\n")
        
        # Test each AI model (excluding GFPGAN - not compatible with DirectML/NPU)
        models = ["realesrgan", "rife", "basicvsr++", "swinir"]
        
        for model in models:
            result = selector.detect_best_mode(target_model=model, force_auto=True)
            print(f"Model: {model}")
            print(f"  Recommended: {result.recommended_mode.value}")
            print(f"  VRAM Available: {result.vram_available}MB")
            print(f"  VRAM Required: {result.vram_required}MB")
            print(f"  Explanation: {result.explanation}")
            if result.override_warning:
                print(f"  Warning: {result.override_warning}")
            print()
    
    elif "--info" in sys.argv:
        print("\n=== Inference Mode Comparison ===\n")
        
        for mode in InferenceMode:
            info = selector.get_mode_info(mode)
            print(f"{mode.value.upper()}:")
            print(f"  Quality: {info.get('quality', 'N/A')}")
            print(f"  Speed: {info.get('speed', 'N/A')}")
            print(f"  VRAM Usage: {info.get('vram_usage', 'N/A')}")
            print(f"  Compatibility: {info.get('compatibility', 'N/A')}")
            print(f"  Description: {info.get('description', 'N/A')}")
            print()
    
    else:
        # Quick detection
        result = selector.detect_best_mode()
        print(f"\nRecommended Mode: {result.recommended_mode.value}")
        print(f"Explanation: {result.explanation}")
        if result.override_warning:
            print(f"\nWarning: {result.override_warning}")
        
        print("\n(Use --test to check all models, --info for mode comparison)")
