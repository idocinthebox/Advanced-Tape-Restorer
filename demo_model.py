"""
Demo AI Model - Simple CNN for Testing ONNX Conversion

This demonstrates the full ONNX conversion pipeline with a real (but simple) model.
Use this to verify the conversion system works before attempting complex models.
"""

import torch
import torch.nn as nn
from pathlib import Path


class DemoUpscalerModel(nn.Module):
    """
    Simple 2x upscaling model for demonstration.
    Mimics RealESRGAN architecture but much smaller.
    """
    
    def __init__(self, num_features=64, num_blocks=5):
        super().__init__()
        
        # Initial feature extraction
        self.conv_first = nn.Conv2d(3, num_features, 3, 1, 1)
        
        # Residual blocks (simplified RRDB)
        blocks = []
        for _ in range(num_blocks):
            blocks.append(self._make_residual_block(num_features))
        self.body = nn.Sequential(*blocks)
        
        # Upsampling (2x)
        self.upconv1 = nn.Conv2d(num_features, num_features * 4, 3, 1, 1)
        self.pixel_shuffle = nn.PixelShuffle(2)
        
        # Final output
        self.conv_last = nn.Conv2d(num_features, 3, 3, 1, 1)
        
        # Activation
        self.lrelu = nn.LeakyReLU(0.2, inplace=True)
    
    def _make_residual_block(self, num_features):
        """Create a residual block"""
        return nn.Sequential(
            nn.Conv2d(num_features, num_features, 3, 1, 1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(num_features, num_features, 3, 1, 1)
        )
    
    def forward(self, x):
        """Forward pass"""
        # Initial features
        feat = self.lrelu(self.conv_first(x))
        
        # Residual processing
        body_feat = self.body(feat)
        feat = feat + body_feat  # Skip connection
        
        # Upsampling
        feat = self.lrelu(self.upconv1(feat))
        feat = self.pixel_shuffle(feat)
        
        # Final output
        out = self.conv_last(feat)
        
        return out


class DemoInterpolationModel(nn.Module):
    """
    Simple frame interpolation model for demonstration.
    Takes 2 frames (6 channels) and outputs middle frame (3 channels).
    """
    
    def __init__(self, num_features=32):
        super().__init__()
        
        self.conv1 = nn.Conv2d(6, num_features, 3, 1, 1)  # 2 frames = 6 channels
        self.conv2 = nn.Conv2d(num_features, num_features, 3, 1, 1)
        self.conv3 = nn.Conv2d(num_features, num_features, 3, 1, 1)
        self.conv4 = nn.Conv2d(num_features, 3, 3, 1, 1)  # Output = 1 frame = 3 channels
        
        self.lrelu = nn.LeakyReLU(0.2, inplace=True)
    
    def forward(self, x):
        """Forward pass (x = [frame1, frame2] concatenated)"""
        x = self.lrelu(self.conv1(x))
        x = self.lrelu(self.conv2(x))
        x = self.lrelu(self.conv3(x))
        x = self.conv4(x)
        return x


def create_demo_model(model_type: str = "upscaler") -> nn.Module:
    """
    Create a demo model for testing.
    
    Args:
        model_type: "upscaler" or "interpolation"
    
    Returns:
        PyTorch model
    """
    if model_type == "upscaler":
        model = DemoUpscalerModel(num_features=64, num_blocks=5)
    elif model_type == "interpolation":
        model = DemoInterpolationModel(num_features=32)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.eval()
    return model


def save_demo_model(model_type: str = "upscaler", output_dir: Path = None):
    """
    Save a demo model to disk for testing.
    
    Args:
        model_type: "upscaler" or "interpolation"
        output_dir: Output directory (default: temp directory)
    """
    model = create_demo_model(model_type)
    
    if output_dir is None:
        output_dir = Path.home() / "AppData" / "Local" / "Advanced_Tape_Restorer" / "demo_models"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"demo_{model_type}.pth"
    
    torch.save(model.state_dict(), output_path)
    print(f"✓ Demo model saved: {output_path}")
    
    # Print model info
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Parameters: {total_params:,}")
    print(f"   Model type: {model_type}")
    
    return output_path


if __name__ == "__main__":
    """Test demo models"""
    import sys
    
    if "--create" in sys.argv:
        print("\n=== Creating Demo Models ===\n")
        
        # Create upscaler
        path1 = save_demo_model("upscaler")
        
        # Create interpolation
        path2 = save_demo_model("interpolation")
        
        print(f"\n✓ Demo models created successfully!")
        print(f"\nTo convert to ONNX:")
        print(f"  python convert_models_to_onnx.py --model demo_upscaler")
        print(f"  python convert_models_to_onnx.py --model demo_interpolation")
    
    elif "--test" in sys.argv:
        print("\n=== Testing Demo Models ===\n")
        
        # Test upscaler
        print("Testing upscaler...")
        model = create_demo_model("upscaler")
        input_tensor = torch.randn(1, 3, 64, 64)
        output = model(input_tensor)
        print(f"  Input shape: {input_tensor.shape}")
        print(f"  Output shape: {output.shape}")
        assert output.shape == (1, 3, 128, 128), "Upscaler should 2x dimensions"
        print("  ✓ Upscaler test passed!\n")
        
        # Test interpolation
        print("Testing interpolation...")
        model = create_demo_model("interpolation")
        input_tensor = torch.randn(1, 6, 256, 256)  # 2 frames concatenated
        output = model(input_tensor)
        print(f"  Input shape: {input_tensor.shape}")
        print(f"  Output shape: {output.shape}")
        assert output.shape == (1, 3, 256, 256), "Interpolation should output 1 frame"
        print("  ✓ Interpolation test passed!\n")
        
        print("✓ All tests passed!")
    
    else:
        print("\nUsage:")
        print("  python demo_model.py --create    # Create demo models")
        print("  python demo_model.py --test      # Test demo models")
