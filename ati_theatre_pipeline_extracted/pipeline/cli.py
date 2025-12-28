from __future__ import annotations
import argparse
from pathlib import Path

from .config import load_config
from .profiling.profiler import quick_profile
from .resolve.lut_cube import write_cube, LutParams
from .processing.runner import process_with_vspipe_and_ffmpeg, ProcessRequest

def main():
    ap = argparse.ArgumentParser(prog="ati-pipe")
    ap.add_argument("--config", default="config/config.yaml", help="Path to config YAML")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_prof = sub.add_parser("profile", help="Create a quick per-tape profile JSON")
    p_prof.add_argument("input", type=str)

    p_proc = sub.add_parser("process", help="Process an input file with a VS variant")
    p_proc.add_argument("input", type=str)
    p_proc.add_argument("--variant", default="deinterlace_qtgmc", help="VS variant name")
    p_proc.add_argument("--preset", default=None, help="Override QTGMC preset (e.g., Slow, Very Slow)")
    p_proc.add_argument("--tff", action="store_true", help="Assume Top-Field-First")
    p_proc.add_argument("--bff", action="store_true", help="Assume Bottom-Field-First")
    p_proc.add_argument("--chroma-x", type=float, default=None, help="Chroma phase X shift (pixels)")
    p_proc.add_argument("--chroma-y", type=float, default=0.0, help="Chroma phase Y shift (pixels)")

    args = ap.parse_args()
    cfg = load_config(args.config)
    work = cfg.work_dir
    work.mkdir(parents=True, exist_ok=True)

    if args.cmd == "profile":
        inp = Path(args.input)
        prof = quick_profile(
            inp,
            sample_frames=int(cfg.raw["profiling"]["sample_frames"]),
            stride=int(cfg.raw["profiling"]["sample_stride"]),
            chroma_phase_default_px=float(cfg.raw["profiling"]["chroma_phase_default_px"]),
            default_field_order=str(cfg.raw["profiling"]["default_field_order"]),
        )
        out = work / "profiles" / (inp.stem + ".profile.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(prof.to_json(), encoding="utf-8")
        print(out)
        return

    if args.cmd == "process":
        inp = Path(args.input)
        prof_path = work / "profiles" / (inp.stem + ".profile.json")
        profile = None
        if prof_path.exists():
            import json
            profile = json.loads(prof_path.read_text(encoding="utf-8"))

        # field order
        if args.tff and args.bff:
            raise SystemExit("Choose only one of --tff or --bff")
        if args.tff:
            tff = True
        elif args.bff:
            tff = False
        else:
            tff = True if (profile and profile.get("field_order","tff") == "tff") else True

        qtgmc_preset = args.preset or cfg.raw["processing"]["qtgmc"]["preset"]
        sharpness = float(cfg.raw["processing"]["qtgmc"]["sharpness"])

        chroma_x = args.chroma_x
        if chroma_x is None:
            chroma_x = float(profile["chroma_phase_x_px"]) if profile else float(cfg.raw["profiling"]["chroma_phase_default_px"])

        out = work / "processed" / f"{inp.stem}.{args.variant}.mkv"

        # Generate a preview LUT alongside the process output.
        if profile:
            lut_size = int(cfg.raw["resolve_luts"]["size"])
            lut_name_prefix = str(cfg.raw["resolve_luts"]["name_prefix"])
            # Saturation heuristic: if avg_saturation is low, boost a bit.
            avg_sat = float(profile.get("avg_saturation", 0.0))
            sat = 1.0 + max(0.0, (0.12 - avg_sat)) * 2.0
            lut_params = LutParams(
                black_point=float(profile["black_point"]),
                white_point=float(profile["white_point"]),
                saturation=float(sat),
            )
            lut_path = work / "luts" / f"{lut_name_prefix}{inp.stem}.cube"
            write_cube(lut_path, size=lut_size, params=lut_params, title=f"{lut_name_prefix}{inp.stem}")
            print(f"Wrote LUT: {lut_path}")

        vspipe = cfg.raw["paths"]["vspipe"]
        ffmpeg = cfg.raw["paths"]["ffmpeg"]

        req = ProcessRequest(
            input_path=inp,
            out_path=out,
            variant=args.variant,
            tff=tff,
            qtgmc_preset=qtgmc_preset,
            sharpness=sharpness,
            chroma_phase_x_px=float(chroma_x),
            chroma_phase_y_px=float(args.chroma_y),
        )
        process_with_vspipe_and_ffmpeg(vspipe=vspipe, ffmpeg=ffmpeg, req=req, temp_dir=work / "vpy")
        print(out)
        return

if __name__ == "__main__":
    main()
