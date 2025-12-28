"""
Test GPU Tile Optimization
Verifies that video dimensions are properly passed to tile calculation
"""

import sys
from core import VapourSynthEngine

def test_tile_calculation():
    """Test tile size calculation with various video dimensions"""
    print("=" * 60)
    print("GPU Tile Optimization Test")
    print("=" * 60)
    
    # Create engine with log callback
    log_messages = []
    def log_callback(msg):
        print(msg)
        log_messages.append(msg)
    
    engine = VapourSynthEngine(
        script_file="test_tile_script.vpy",
        log_callback=log_callback
    )
    
    # Test scenarios
    test_cases = [
        {"width": 1920, "height": 1080, "name": "1080p (HD)"},
        {"width": 3840, "height": 2160, "name": "4K"},
        {"width": 1280, "height": 720, "name": "720p (HD)"},
        {"width": 720, "height": 480, "name": "480p (SD)"},
    ]
    
    print("\nTesting tile calculation for different resolutions:\n")
    
    for test in test_cases:
        print(f"\n--- {test['name']}: {test['width']}x{test['height']} ---")
        
        # Create test options
        options = {
            'input_file': 'test.mp4',
            'width': test['width'],
            'height': test['height'],
            'use_ai_upscaling': True,
            'ai_upscaling_method': 'RealESRGAN (High Quality, GPU)',  # Trigger RealESRGAN
            'field_order': 'Progressive'
        }
        
        try:
            # Generate script (will trigger tile calculation)
            engine.create_script('test.mp4', options)
            
            # Read generated script to check tile size
            with open(engine.script_file, 'r') as f:
                script_content = f.read()
                
            # Extract tile size from script
            for line in script_content.split('\n'):
                if 'tile=' in line:
                    print(f"   Generated: {line.strip()}")
                    break
                    
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nGPU Optimization Messages:")
    print("-" * 60)
    for msg in log_messages:
        if '[GPU Optimization]' in msg:
            print(msg)

if __name__ == "__main__":
    test_tile_calculation()
