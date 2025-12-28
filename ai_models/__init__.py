"""
AI Models Package - v3.0 Modular AI Model Management System

Provides centralized model management, auto-downloading, and modular AI engines.

Components:
    - model_manager: Core model registry and download management
    - pipeline_runner: Sequential AI operation orchestration
    - engines: Individual AI engine wrappers (11 total)
    - ui: Model browser and management dialogs

Supported AI Engines:
    Upscaling:
        - RealESRGAN (BSD-3-Clause, 2x scale, GPU PyTorch)
        - BasicVSR++ (Apache-2.0, 2x/4x scale, video-specific temporal)
        - SwinIR (Apache-2.0, 2x/4x scale, transformer-based)

    Frame Interpolation:
        - RIFE (MIT, 2x interpolation, GPU)
        - DAIN (MIT, depth-aware interpolation)
        - FILM (Apache-2.0, Google research)
        - AMT (Apache-2.0, adaptive motion)

    Colorization:
        - DeOldify (MIT, B&W to color)
        - SVDiffusion (Apache-2.0, stable diffusion)

    Face Enhancement:
        - GFPGAN (custom license, face restoration)

    Forensic:
        - Video Cleaner (custom, artifact removal)

Version: 3.0.0
"""

__version__ = "3.0.0"


def __getattr__(name):
    """Lazy imports for AI models - improves startup performance."""
    if name == "ModelManager":
        from .model_manager import ModelManager

        return ModelManager
    elif name == "ModelEntry":
        from .model_manager import ModelEntry

        return ModelEntry
    elif name == "ModelFile":
        from .model_manager import ModelFile

        return ModelFile
    elif name == "PipelineConfig":
        from .pipeline_runner import PipelineConfig

        return PipelineConfig
    elif name == "PipelineStep":
        from .pipeline_runner import PipelineStep

        return PipelineStep
    elif name == "run_pipeline":
        from .pipeline_runner import run_pipeline

        return run_pipeline
    elif name == "ENGINE_REGISTRY":
        from .pipeline_runner import ENGINE_REGISTRY

        return ENGINE_REGISTRY
    else:
        raise AttributeError(f"module 'ai_models' has no attribute '{name}'")
