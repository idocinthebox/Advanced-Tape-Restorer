from dataclasses import dataclass, field
from typing import Any, Optional, Callable

import vapoursynth as vs

from .model_manager import ModelManager

# Import engines with optional handling for missing dependencies


def _safe_import_engine(module_name):
    """Try to import an engine module, return None if unavailable."""
    try:
        from . import engines

        return getattr(engines, module_name, None)
    except (ImportError, AttributeError):
        return None


# Try to import each engine
upscaling_basicvsrpp = _safe_import_engine("upscaling_basicvsrpp")
upscaling_realesrgan = _safe_import_engine("upscaling_realesrgan")
upscaling_swinir = _safe_import_engine("upscaling_swinir")
interpolation_rife = _safe_import_engine("interpolation_rife")
interpolation_dain = _safe_import_engine("interpolation_dain")
interpolation_film = _safe_import_engine("interpolation_film")
interpolation_amt = _safe_import_engine("interpolation_amt")
color_deoldify = _safe_import_engine("color_deoldify")
color_svdiffusion = _safe_import_engine("color_svdiffusion")
face_gfpgan = _safe_import_engine("face_gfpgan")
forensic_videocleaner = _safe_import_engine("forensic_videocleaner")

core = vs.core


@dataclass
class PipelineStep:
    name: str
    engine: str
    model_id: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    steps: list[PipelineStep]


# Build ENGINE_REGISTRY with only available engines
ENGINE_REGISTRY: dict[str, Callable] = {}

if upscaling_basicvsrpp:
    ENGINE_REGISTRY["basicvsrpp"] = upscaling_basicvsrpp.apply
if upscaling_realesrgan:
    ENGINE_REGISTRY["realesrgan"] = upscaling_realesrgan.apply
if upscaling_swinir:
    ENGINE_REGISTRY["swinir"] = upscaling_swinir.apply
if interpolation_rife:
    ENGINE_REGISTRY["rife"] = interpolation_rife.apply
if interpolation_dain:
    ENGINE_REGISTRY["dain"] = interpolation_dain.apply
if interpolation_film:
    ENGINE_REGISTRY["film"] = interpolation_film.apply
if interpolation_amt:
    ENGINE_REGISTRY["amt"] = interpolation_amt.apply
if color_deoldify:
    ENGINE_REGISTRY["deoldify"] = color_deoldify.apply
if color_svdiffusion:
    ENGINE_REGISTRY["svdiffusion"] = color_svdiffusion.apply
if face_gfpgan:
    ENGINE_REGISTRY["gfpgan"] = face_gfpgan.apply
if forensic_videocleaner:
    ENGINE_REGISTRY["videocleaner"] = forensic_videocleaner.apply


def run_pipeline(
    src_clip: vs.VideoNode,
    cfg: PipelineConfig,
    model_manager: ModelManager,
    auto_download: bool = True,
) -> vs.VideoNode:
    clip = src_clip

    for step in cfg.steps:
        engine_name = step.engine
        if engine_name not in ENGINE_REGISTRY:
            raise ValueError(f"Unknown engine: {engine_name}")

        engine_fn = ENGINE_REGISTRY[engine_name]

        engine_args: dict[str, Any] = {}
        try:
            if step.model_id is not None or model_manager.get_default_model_for_engine(
                engine_name
            ):
                engine_args = model_manager.prepare_engine_args(
                    engine=engine_name,
                    model_id=step.model_id,
                    auto_download=auto_download,
                )
        except KeyError:
            engine_args = {}

        final_kwargs = {**engine_args, **step.params}

        print(
            f"[PipelineRunner] Applying step '{step.name}' (engine={engine_name}, model={step.model_id})"
        )

        clip = engine_fn(clip, **final_kwargs)

    return clip
