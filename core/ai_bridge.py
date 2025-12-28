"""
AI Bridge - Connects v2.0 VapourSynth Engine to AI Model Manager System

This module provides a compatibility layer between the existing v2.0 AI features
and the new modular AI Model Manager system introduced in v3.0.

Architecture:
    - AIBridge wraps ModelManager and provides simple apply_* methods
    - Each method corresponds to an AI engine (realesrgan, rife, etc.)
    - Automatically downloads models if missing (with progress callbacks)
    - Handles all engine-specific parameter preparation

Usage:
    from core.ai_bridge import AIBridge

    bridge = AIBridge(registry_path, model_root, commercial_mode=True)

    # Apply RealESRGAN upscaling
    clip = bridge.apply_realesrgan(clip, model_id="realesrgan_x2plus")

    # Apply RIFE interpolation
    clip = bridge.apply_rife(clip, model_id="rife_v4_22", factor=2.0)
"""

import os
import vapoursynth as vs
from pathlib import Path
from typing import Optional, Callable

from ai_models.model_manager import ModelManager
from ai_models.pipeline_runner import ENGINE_REGISTRY


class AIBridge:
    """
    Bridge between v2.0 VapourSynth engine and v3.0 AI Model Manager.

    Provides backward-compatible API for existing AI features while using
    the new modular model management system.
    """
    
    __slots__ = ('manager', 'progress_callback', 'log_callback')  # Memory optimization

    def __init__(
        self,
        registry_path: str,
        model_root: str,
        commercial_mode: bool = True,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize AI Bridge.

        Args:
            registry_path: Path to models/registry.yaml
            model_root: Root directory for downloaded models
            commercial_mode: Whether to allow commercial-licensed models
            progress_callback: Optional callback(model_id, percent) for download progress
            log_callback: Optional callback(message) for logging
        """
        self.manager = ModelManager(registry_path, model_root, commercial_mode)
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        self._log(f"AI Bridge initialized - Registry: {registry_path}")
        self._log(f"Model root: {model_root}")
        self._log(f"Commercial mode: {commercial_mode}")

    def _log(self, message: str):
        """Internal logging helper (optimized)."""
        if self.log_callback:
            self.log_callback(f"[AI Bridge] {message}")
        # No fallback print to reduce overhead

    def _progress(self, model_id: str, percent: int):
        """Internal progress tracking helper."""
        if self.progress_callback:
            self.progress_callback(model_id, percent)

    def list_available_models(self, engine: Optional[str] = None) -> list:
        """
        List all available models, optionally filtered by engine.

        Args:
            engine: Optional engine filter (e.g., 'realesrgan', 'rife')

        Returns:
            List of model entries matching filter
        """
        return self.manager.list_models(engine)

    def apply_realesrgan(
        self,
        clip: vs.VideoNode,
        model_id: str = "realesrgan_x2plus",
        scale: int = 2,
        tile_w: int = 0,
        tile_h: int = 0,
        tta: bool = False,
        fp16: bool = True,
        auto_download: bool = True,
        **kwargs,
    ) -> vs.VideoNode:
        """
        Apply RealESRGAN AI upscaling using model manager.

        Backward-compatible replacement for hardcoded RealESRGAN in v2.0.

        Args:
            clip: Input VapourSynth clip
            model_id: Model ID from registry (default: realesrgan_x2plus)
            scale: Upscaling factor (2, 4, 8)
            tile_w: Tile width for GPU memory management (0 = auto)
            tile_h: Tile height for GPU memory management (0 = auto)
            tta: Test-time augmentation (slower, better quality)
            fp16: Use half-precision (faster, less VRAM)
            auto_download: Automatically download model if missing
            **kwargs: Additional engine-specific parameters

        Returns:
            Upscaled VapourSynth clip

        Raises:
            RuntimeError: If model not available and auto_download=False
            ValueError: If model_id not found in registry
        """
        self._log(f"Applying RealESRGAN: model={model_id}, scale={scale}")

        # Ensure model is available
        if auto_download:
            self._log(f"Checking model availability: {model_id}")
            self.manager.ensure_model_available(model_id, auto_download=True)

        # Get engine function from registry
        engine_fn = ENGINE_REGISTRY.get("realesrgan")
        if not engine_fn:
            raise RuntimeError("RealESRGAN engine not found in ENGINE_REGISTRY")

        # Prepare engine arguments from model manager
        engine_args = self.manager.prepare_engine_args(
            "realesrgan",
            model_id,
            overrides={
                "scale": scale,
                "tile_w": tile_w,
                "tile_h": tile_h,
                "tta": tta,
                "fp16": fp16,
                **kwargs,
            },
        )

        # Apply engine
        self._log(f"Applying RealESRGAN with args: {engine_args}")
        result = engine_fn(clip, **engine_args)

        self._log("RealESRGAN applied successfully")
        return result

    def apply_rife(
        self,
        clip: vs.VideoNode,
        model_id: str = "rife_v4_22",
        factor: float = 2.0,
        auto_download: bool = True,
        **kwargs,
    ) -> vs.VideoNode:
        """
        Apply RIFE frame interpolation using model manager.

        Backward-compatible replacement for hardcoded RIFE in v2.0.

        Args:
            clip: Input VapourSynth clip
            model_id: Model ID from registry (default: rife_v4_22)
            factor: Interpolation factor (2.0 = double framerate)
            auto_download: Automatically download model if missing
            **kwargs: Additional engine-specific parameters

        Returns:
            Interpolated VapourSynth clip

        Raises:
            RuntimeError: If model not available and auto_download=False
            ValueError: If model_id not found in registry
        """
        self._log(f"Applying RIFE: model={model_id}, factor={factor}")

        # Ensure model is available
        if auto_download:
            self._log(f"Checking model availability: {model_id}")
            self.manager.ensure_model_available(model_id, auto_download=True)

        # Get engine function from registry
        engine_fn = ENGINE_REGISTRY.get("rife")
        if not engine_fn:
            raise RuntimeError("RIFE engine not found in ENGINE_REGISTRY")

        # Prepare engine arguments from model manager
        engine_args = self.manager.prepare_engine_args(
            "rife", model_id, overrides={"factor": factor, **kwargs}
        )

        # Apply engine
        self._log(f"Applying RIFE with args: {engine_args}")
        result = engine_fn(clip, **engine_args)

        self._log("RIFE applied successfully")
        return result

    def apply_basicvsrpp(
        self,
        clip: vs.VideoNode,
        model_id: str = "basicvsrpp_general_x2",
        scale: int = 2,
        auto_download: bool = True,
        **kwargs,
    ) -> vs.VideoNode:
        """
        Apply BasicVSR++ video super-resolution (NEW in v3.0).

        BasicVSR++ is video-specific and uses temporal information for better quality.

        Args:
            clip: Input VapourSynth clip
            model_id: Model ID from registry (default: basicvsrpp_general_x2)
            scale: Upscaling factor (2, 4)
            auto_download: Automatically download model if missing
            **kwargs: Additional engine-specific parameters

        Returns:
            Upscaled VapourSynth clip
        """
        self._log(f"Applying BasicVSR++: model={model_id}, scale={scale}")

        if auto_download:
            self.manager.ensure_model_available(model_id, auto_download=True)

        engine_fn = ENGINE_REGISTRY.get("basicvsrpp")
        if not engine_fn:
            raise RuntimeError("BasicVSR++ engine not found in ENGINE_REGISTRY")

        engine_args = self.manager.prepare_engine_args(
            "basicvsrpp", model_id, overrides={"scale": scale, **kwargs}
        )

        result = engine_fn(clip, **engine_args)
        self._log("BasicVSR++ applied successfully")
        return result

    def apply_swinir(
        self,
        clip: vs.VideoNode,
        model_id: str = "swinir_real_sr_x4",
        scale: int = 4,
        auto_download: bool = True,
        **kwargs,
    ) -> vs.VideoNode:
        """
        Apply SwinIR transformer-based upscaling (NEW in v3.0).

        SwinIR provides excellent quality with reasonable speed.

        Args:
            clip: Input VapourSynth clip
            model_id: Model ID from registry (default: swinir_real_sr_x4)
            scale: Upscaling factor (2, 4)
            auto_download: Automatically download model if missing
            **kwargs: Additional engine-specific parameters

        Returns:
            Upscaled VapourSynth clip
        """
        self._log(f"Applying SwinIR: model={model_id}, scale={scale}")

        if auto_download:
            self.manager.ensure_model_available(model_id, auto_download=True)

        engine_fn = ENGINE_REGISTRY.get("swinir")
        if not engine_fn:
            raise RuntimeError("SwinIR engine not found in ENGINE_REGISTRY")

        engine_args = self.manager.prepare_engine_args(
            "swinir", model_id, overrides={"scale": scale, **kwargs}
        )

        result = engine_fn(clip, **engine_args)
        self._log("SwinIR applied successfully")
        return result

    def get_model_info(self, model_id: str) -> dict:
        """
        Get detailed information about a model.

        Args:
            model_id: Model ID from registry

        Returns:
            Dict with model metadata (engine, version, license, files, etc.)

        Raises:
            ValueError: If model_id not found
        """
        model = self.manager.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        return {
            "id": model.id,
            "engine": model.engine,
            "friendly_name": getattr(model, "friendly_name", model.id),
            "version": model.version,
            "license": model.license,
            "license_url": getattr(model, "license_url", None),
            "non_commercial": model.non_commercial,
            "files": [f.path for f in model.files],
            "installed": self._is_model_installed(model),
        }

    def _is_model_installed(self, model) -> bool:
        """Check if all model files are present locally."""
        model_root = Path(self.manager.model_root)
        for file_entry in model.files:
            file_path = model_root / file_entry.path
            if not file_path.exists():
                return False
        return True


def create_ai_bridge(
    model_root: Optional[str] = None,
    commercial_mode: bool = True,
    progress_callback: Optional[Callable] = None,
    log_callback: Optional[Callable] = None,
) -> AIBridge:
    """
    Convenience factory function for creating AIBridge with default paths.

    Args:
        model_root: Root directory for models (default: %LOCALAPPDATA%/Advanced_Tape_Restorer/ai_models)
        commercial_mode: Allow commercial models
        progress_callback: Optional download progress callback
        log_callback: Optional logging callback

    Returns:
        Configured AIBridge instance
    """
    # Determine default paths
    if model_root is None:
        localappdata = os.getenv("LOCALAPPDATA", os.path.expanduser("~/.local/share"))
        model_root = os.path.join(localappdata, "Advanced_Tape_Restorer", "ai_models")

    # Registry path relative to this file
    script_dir = Path(__file__).parent.parent
    registry_path = script_dir / "ai_models" / "models" / "registry.yaml"

    if not registry_path.exists():
        raise RuntimeError(f"Model registry not found: {registry_path}")

    return AIBridge(
        str(registry_path), model_root, commercial_mode, progress_callback, log_callback
    )
