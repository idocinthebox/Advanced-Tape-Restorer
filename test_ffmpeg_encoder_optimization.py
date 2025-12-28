"""
Test suite for ffmpeg_encoder.py optimizations

Verifies:
- Module-level constants
- Pre-compiled regex patterns  
- __slots__ memory efficiency
- Command building optimization
- Progress parsing
"""

import unittest
import re
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.ffmpeg_encoder import (
    FFmpegEncoder,
    _PROGRESS_REGEX,
    _BITRATE_REGEX,
    _CODEC_CONFIGS,
    _BENIGN_WARNINGS,
)


class TestModuleOptimizations(unittest.TestCase):
    """Test module-level optimization constants"""

    def test_precompiled_progress_regex(self):
        """Verify progress regex is pre-compiled"""
        self.assertIsInstance(_PROGRESS_REGEX, re.Pattern)
        
        # Test pattern matching
        test_line = "frame= 1234 fps= 45.6 q=-1.0 size=   12345kB time=00:01:23.45"
        match = _PROGRESS_REGEX.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "1234")
        self.assertEqual(match.group(2), "45.6")

    def test_precompiled_bitrate_regex(self):
        """Verify bitrate regex is pre-compiled"""
        self.assertIsInstance(_BITRATE_REGEX, re.Pattern)
        
        # Test valid bitrates
        self.assertTrue(_BITRATE_REGEX.match("192k"))
        self.assertTrue(_BITRATE_REGEX.match("128k"))
        self.assertTrue(_BITRATE_REGEX.match("320k"))
        
        # Test invalid bitrates
        self.assertIsNone(_BITRATE_REGEX.match("1920k"))  # 4 digits
        self.assertIsNone(_BITRATE_REGEX.match("192"))    # No 'k'
        self.assertIsNone(_BITRATE_REGEX.match("9k"))     # 1 digit

    def test_codec_configs_immutable(self):
        """Verify codec configs are module-level dict"""
        self.assertIsInstance(_CODEC_CONFIGS, dict)
        self.assertIn("libx264 (H.264, CPU)", _CODEC_CONFIGS)
        self.assertIn("ProRes 422 (HQ)", _CODEC_CONFIGS)
        self.assertEqual(len(_CODEC_CONFIGS), 13)  # 13 codec configs

    def test_benign_warnings_tuple(self):
        """Verify benign warnings is tuple for fast membership"""
        self.assertIsInstance(_BENIGN_WARNINGS, tuple)
        self.assertEqual(len(_BENIGN_WARNINGS), 3)
        self.assertIn("codec frame size is not set", _BENIGN_WARNINGS)


class TestFFmpegEncoderOptimizations(unittest.TestCase):
    """Test FFmpegEncoder class optimizations"""

    def test_slots_defined(self):
        """Verify __slots__ for memory efficiency"""
        self.assertTrue(hasattr(FFmpegEncoder, '__slots__'))
        self.assertEqual(FFmpegEncoder.__slots__, ('process', 'progress_callback', 'log_callback'))

    def test_slots_memory_reduction(self):
        """Verify __slots__ prevents __dict__ creation"""
        encoder = FFmpegEncoder()
        self.assertFalse(hasattr(encoder, '__dict__'))

    def test_codec_configs_class_variable(self):
        """Verify backward compatibility - CODEC_CONFIGS as class var"""
        self.assertEqual(FFmpegEncoder.CODEC_CONFIGS, _CODEC_CONFIGS)


class TestCommandBuildingOptimization(unittest.TestCase):
    """Test build_command optimization"""

    def setUp(self):
        self.encoder = FFmpegEncoder()

    def test_basic_command_h264(self):
        """Test H.264 command building"""
        options = {
            "codec": "libx264 (H.264, CPU)",
            "crf": "18",
            "ffmpeg_preset": "slow",
            "audio": "No Audio",
        }
        cmd = self.encoder.build_command("input.mp4", "output.mp4", options, pipe_input=False)
        
        self.assertIn("ffmpeg", cmd)
        self.assertIn("-c:v", cmd)
        self.assertIn("libx264", cmd)
        self.assertIn("-crf", cmd)
        self.assertIn("18", cmd)
        self.assertIn("-an", cmd)  # No audio

    def test_pipe_input_command(self):
        """Test pipe input with Y4M format"""
        options = {"codec": "libx264 (H.264, CPU)", "audio": "No Audio"}
        cmd = self.encoder.build_command("pipe:", "output.mp4", options, pipe_input=True)
        
        self.assertIn("-f", cmd)
        self.assertIn("yuv4mpegpipe", cmd)
        self.assertIn("pipe:", cmd)

    def test_audio_copy_mode(self):
        """Test audio copy mode"""
        options = {
            "codec": "libx264 (H.264, CPU)",
            "audio": "Copy Audio",
        }
        cmd = self.encoder.build_command(
            "pipe:", "output.mp4", options, pipe_input=True, original_file="input.mp4"
        )
        
        self.assertIn("-c:a", cmd)
        self.assertIn("copy", cmd)
        self.assertIn("-map", cmd)

    def test_audio_reencode_aac(self):
        """Test AAC audio re-encoding"""
        options = {
            "codec": "libx264 (H.264, CPU)",
            "audio": "Re-encode Audio",
            "audio_codec": "AAC",
            "audio_bitrate": "192k",
        }
        cmd = self.encoder.build_command(
            "pipe:", "output.mp4", options, pipe_input=True, original_file="input.mp4"
        )
        
        self.assertIn("aac", cmd)
        self.assertIn("192k", cmd)

    def test_prores_ai_optimization(self):
        """Test ProRes + AI memory optimization"""
        options = {
            "codec": "ProRes 422 (HQ)",
            "use_ai_upscaling": True,
            "audio": "No Audio",
        }
        cmd = self.encoder.build_command("pipe:", "output.mov", options, pipe_input=True)
        
        self.assertIn("-threads", cmd)
        self.assertIn("4", cmd)
        self.assertIn("-max_muxing_queue_size", cmd)
        self.assertIn("-filter_threads", cmd)


class TestProgressParsing(unittest.TestCase):
    """Test progress parsing optimization"""

    def test_progress_regex_performance(self):
        """Test pre-compiled regex vs runtime compilation"""
        test_line = "frame= 1234 fps= 45.6 q=-1.0 size=   12345kB"
        
        # Pre-compiled (optimized)
        match = _PROGRESS_REGEX.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), 1234)
        self.assertAlmostEqual(float(match.group(2)), 45.6)

    def test_benign_warning_filtering(self):
        """Test tuple-based warning filtering"""
        test_warnings = [
            "codec frame size is not set",
            "Error during demuxing: Invalid data found when processing input",
            "Unknown cover type: some garbage",
            "This is a real error",
        ]
        
        # Test fast membership check
        filtered = [w for w in test_warnings if not any(msg in w for msg in _BENIGN_WARNINGS)]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "This is a real error")


class TestETAFormatting(unittest.TestCase):
    """Test ETA formatting optimization"""

    def test_format_eta_normal(self):
        """Test normal ETA formatting"""
        eta = FFmpegEncoder._format_eta(3661)  # 1 hour, 1 minute, 1 second
        self.assertEqual(eta, "1:01:01")

    def test_format_eta_short(self):
        """Test short ETA"""
        eta = FFmpegEncoder._format_eta(65)  # 1 minute, 5 seconds
        self.assertEqual(eta, "0:01:05")

    def test_format_eta_invalid(self):
        """Test invalid ETA handling (fast path)"""
        self.assertEqual(FFmpegEncoder._format_eta(-5), "--:--:--")
        self.assertEqual(FFmpegEncoder._format_eta(0), "--:--:--")
        self.assertEqual(FFmpegEncoder._format_eta(200000), "--:--:--")  # > 2 days


class TestCleanupOptimization(unittest.TestCase):
    """Test cleanup method optimization"""

    @patch('subprocess.Popen')
    def test_cleanup_terminates_process(self, mock_popen):
        """Test cleanup terminates running process"""
        encoder = FFmpegEncoder()
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process running
        encoder.process = mock_process
        
        encoder.cleanup()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()

    @patch('subprocess.Popen')
    def test_cleanup_kills_on_timeout(self, mock_popen):
        """Test cleanup kills process on timeout"""
        encoder = FFmpegEncoder()
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 5)
        mock_process.kill = Mock()
        encoder.process = mock_process
        
        encoder.cleanup()
        
        mock_process.kill.assert_called_once()


def run_tests():
    """Run all tests and return success status"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
