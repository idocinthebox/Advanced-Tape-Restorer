# v3.2 FIX for vapoursynth_engine.py
# Replace the _generate_ai_upscaling method with this version
# This uses DIRECT vsrealesrgan/vsrife plugin calls instead of Model Manager

def _generate_ai_upscaling(self, options: dict) -> list:
    """
    Generate AI upscaling filter lines (v3.2 - Direct Plugin Usage).
    
    **v3.2 CHANGE:** Uses vsrealesrgan/vsbasicvsrpp/vsswinir plugins directly
    instead of the ai_models Model Manager approach. This eliminates the
    dependency cascade on virgin installs.
    
    Works with VapourSynth plugins that have bundled PyTorch:
    - vs-realesrgan: RealESRGAN upscaling (auto-downloads models)
    - vs-basicvsrpp: BasicVSR++ video upscaling
    - vs-swinir: SwinIR transformer upscaling
    - znedi3: Fast CPU/GPU upscaling (no external dependencies)
    """
    lines = []

    # Check if AI upscaling is enabled
    if not options.get("use_ai_upscaling", False):
        return lines

    method = options.get("ai_upscaling_method", "RealESRGAN (General 4x)")
    target_width = options.get("output_width", 1920)
    target_height = options.get("output_height", 1080)
    resize_algo = options.get("resize_algorithm", "Spline36")
    
    # Determine if we need manual resize after AI upscaling
    manual_resize = options.get("manual_resize", False)

    lines.append("")
    lines.append(f"# AI Upscaling: {method}")

    # Parse method and determine engine
    if "RealESRGAN" in method:
        engine = "realesrgan"
        
        # Determine model based on method name
        if "General 4x" in method or "x4" in method.lower():
            model_name = "realesr-general-x4v3"
            scale = 4
        elif "x2" in method.lower() or "2x" in method:
            model_name = "RealESRGAN_x2plus"
            scale = 2
        elif "Anime" in method:
            model_name = "realesr-animevideov3"
            scale = 4
        else:
            model_name = "realesr-general-x4v3"  # Default
            scale = 4
            
    elif "BasicVSR++" in method:
        engine = "basicvsrpp"
        model_name = "BasicVSR++"  # Plugin handles model internally
        scale = 2  # BasicVSR++ is typically 2x
        
    elif "SwinIR" in method:
        engine = "swinir"
        if "4x" in method:
            model_name = "003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN"
            scale = 4
        elif "2x" in method:
            model_name = "003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x2_GAN"
            scale = 2
        else:
            model_name = "003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN"
            scale = 4
            
    elif "ZNEDI3" in method:
        # ZNEDI3 stays as-is (fast VapourSynth plugin, no model management needed)
        lines.append("try:")
        if manual_resize:
            lines.append(
                f"    print('[AI] Applying ZNEDI3 AI Upscaling (2x) then resizing to {target_width}x{target_height}...')"
            )
        else:
            lines.append(
                "    print('[AI] Applying ZNEDI3 AI Upscaling (2x)...')"
            )
        lines.append("    # ZNEDI3 double upscaling (2x total)")
        lines.append(
            "    video = core.znedi3.nnedi3(video, field=1, dh=True, nsize=4, nns=4, qual=2)"
        )
        lines.append("    video = core.std.Transpose(video)")
        lines.append(
            "    video = core.znedi3.nnedi3(video, field=1, dh=True, nsize=4, nns=4, qual=2)"
        )
        lines.append("    video = core.std.Transpose(video)")
        if manual_resize:
            lines.append(
                f"    # Resize to exact target dimensions using {resize_algo}"
            )
            lines.append(
                f"    video = core.resize.{resize_algo}(video, width={target_width}, height={target_height})"
            )
        lines.append(
            "    print('[AI] ZNEDI3 upscaling completed successfully')"
        )
        lines.append("except Exception as e:")
        lines.append(
            "    print(f'--- WARNING: ZNEDI3 failed: {e}. Skipping AI upscaling. ---')"
        )
        if manual_resize:
            lines.append(
                f"    video = core.resize.{resize_algo}(video, width={target_width}, height={target_height})"
            )
        lines.append("    pass")
        return lines
    else:
        # Unknown method - skip
        self._log(f"[WARNING] Unknown AI upscaling method: {method}")
        return lines

    # ===== v3.2 CRITICAL FIX: Direct Plugin Usage =====
    # Use vsrealesrgan, vsbasicvsrpp, vsswinir plugins DIRECTLY
    # NO Model Manager imports = NO Python package dependencies!
    
    lines.append(f"print('[v3.2] Using {engine} VapourSynth plugin directly...')")
    lines.append("try:")
    
    # Log what we're doing
    if manual_resize:
        lines.append(
            f"    print('[AI] Applying {engine} AI Upscaling ({scale}x) then resizing to {target_width}x{target_height}...')"
        )
    else:
        lines.append(
            f"    print('[AI] Applying {engine} AI Upscaling ({scale}x)...')"
        )
    lines.append(f"    print('[AI] Model: {model_name}')")
    lines.append("    ")
    
    # Import the appropriate VapourSynth plugin
    if engine == "realesrgan":
        lines.append("    # Import vsrealesrgan plugin")
        lines.append("    from vsrealesrgan import realesrgan, RealESRGANModel")
        lines.append("    ")
        lines.append("    # Convert to RGB for AI processing")
        lines.append("    video = core.resize.Bicubic(video, format=vs.RGBS, matrix_in_s='709')")
        lines.append("    ")
        lines.append("    # Apply RealESRGAN upscaling (plugin auto-downloads models)")
        lines.append("    video = realesrgan(")
        lines.append("        video,")
        lines.append(f"        model=RealESRGANModel.{model_name.replace('-', '_')},")
        lines.append("        device_index=0,")
        lines.append("        auto_download=True,  # Models download automatically!")
        lines.append("        tile=0,  # Auto tile size")
        lines.append("        tile_pad=10")
        lines.append("    )")
        
    elif engine == "basicvsrpp":
        lines.append("    # Import vsbasicvsrpp plugin")
        lines.append("    from vsbasicvsrpp import BasicVSRPP")
        lines.append("    ")
        lines.append("    # Convert to RGB for AI processing")
        lines.append("    video = core.resize.Bicubic(video, format=vs.RGBS, matrix_in_s='709')")
        lines.append("    ")
        lines.append("    # Apply BasicVSR++ upscaling")
        lines.append("    video = BasicVSRPP(")
        lines.append("        video,")
        lines.append("        device_index=0,")
        lines.append("        auto_download=True,")
        lines.append("        interval=15  # Process 15 frames at a time")
        lines.append("    )")
        
    elif engine == "swinir":
        lines.append("    # Import vsswinir plugin")
        lines.append("    from vsswinir import SwinIR")
        lines.append("    ")
        lines.append("    # Convert to RGB for AI processing")
        lines.append("    video = core.resize.Bicubic(video, format=vs.RGBS, matrix_in_s='709')")
        lines.append("    ")
        lines.append("    # Apply SwinIR upscaling")
        lines.append("    video = SwinIR(")
        lines.append("        video,")
        lines.append(f"        scale={scale},")
        lines.append("        device_index=0,")
        lines.append("        auto_download=True")
        lines.append("    )")
    
    lines.append("    ")
    lines.append("    # Convert back to YUV420P8")
    lines.append("    video = core.resize.Bicubic(video, format=vs.YUV420P8, matrix_s='709')")
    
    # Optional manual resize
    if manual_resize:
        lines.append("    ")
        lines.append(f"    # Resize to exact target dimensions using {resize_algo}")
        lines.append(
            f"    video = core.resize.{resize_algo}(video, width={target_width}, height={target_height})"
        )
    
    lines.append("    ")
    lines.append(f"    print('[AI] {engine} upscaling completed successfully')")
    
    # Error handling with helpful messages
    lines.append("except ImportError as e:")
    lines.append("    import traceback")
    lines.append(f"    print('[ERROR] {engine} plugin not installed!')")
    lines.append("    print(f'   Error: {str(e)}')")
    lines.append("    traceback.print_exc()")
    lines.append(f"    print('--- WARNING: {engine} plugin missing. Skipping AI upscaling. ---')")
    
    if engine == "realesrgan":
        lines.append("    print('   Install with: py -3.12 \"%LOCALAPPDATA%\\\\Programs\\\\VapourSynth\\\\vsrepo\\\\vsrepo.py\" install realesrgan')")
    elif engine == "basicvsrpp":
        lines.append("    print('   Install with: py -3.12 \"%LOCALAPPDATA%\\\\Programs\\\\VapourSynth\\\\vsrepo\\\\vsrepo.py\" install basicvsrpp')")
    elif engine == "swinir":
        lines.append("    print('   Install with: py -3.12 \"%LOCALAPPDATA%\\\\Programs\\\\VapourSynth\\\\vsrepo\\\\vsrepo.py\" install swinir')")
    
    # Convert back to YUV if needed (in case of failure)
    lines.append("    if video.format.id != vs.YUV420P8:")
    lines.append("        video = core.resize.Bicubic(video, format=vs.YUV420P8, matrix_s='709')")
    
    if manual_resize:
        lines.append(f"    # Fallback to regular resize using {resize_algo}")
        lines.append(
            f"    video = core.resize.{resize_algo}(video, width={target_width}, height={target_height})"
        )
    
    lines.append("    pass")
    lines.append("except Exception as e:")
    lines.append("    import traceback")
    lines.append(f"    print('[ERROR] {engine} failed with exception:')")
    lines.append("    print(f'   Exception type: {type(e).__name__}')")
    lines.append("    print(f'   Exception message: {str(e)}')")
    lines.append("    print('   Full traceback:')")
    lines.append("    traceback.print_exc()")
    lines.append(f"    print('--- WARNING: {engine} failed. Skipping AI upscaling. ---')")
    
    # Convert back to YUV if needed (in case of failure)
    lines.append("    if video.format.id != vs.YUV420P8:")
    lines.append("        video = core.resize.Bicubic(video, format=vs.YUV420P8, matrix_s='709')")
    
    if manual_resize:
        lines.append(f"    # Fallback to regular resize using {resize_algo}")
        lines.append(
            f"    video = core.resize.{resize_algo}(video, width={target_width}, height={target_height})"
        )
    
    lines.append("    pass")

    return lines
