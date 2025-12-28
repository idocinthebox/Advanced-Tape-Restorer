"""
Test suite for propainter_engine.py optimizations

Verifies:
- Module-level pre-compiled regex patterns
- __slots__ memory efficiency
- Simplified path finding
- Progress parsing optimization
"""

import unittest
import re
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.propainter_engine import (
    ProPainterEngine,
    _FRAME_REGEX,
    _FRAME_REGEX_ALT,
    _PROGRESS_SLASH,
    _PROGRESS_PERCENT,
    _FRAME_WORD,
    _IMPORTANT_KEYWORDS,
)


class TestModuleOptimizations(unittest.TestCase):
    """Test module-level optimization constants"""

    def test_precompiled_frame_regex(self):
        """Verify frame count regex is pre-compiled"""
        self.assertIsInstance(_FRAME_REGEX, re.Pattern)
        
        # Test pattern matching
        test_line = "Processing: test [252 frames]..."
        match = _FRAME_REGEX.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "252")

    def test_precompiled_frame_regex_alt(self):
        """Verify alternate frame regex"""
        self.assertIsInstance(_FRAME_REGEX_ALT, re.Pattern)
        
        test_line = "Processing 252 video frames"
        match = _FRAME_REGEX_ALT.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "252")

    def test_precompiled_progress_slash(self):
        """Verify slash-style progress regex"""
        self.assertIsInstance(_PROGRESS_SLASH, re.Pattern)
        
        test_line = "100/252"
        match = _PROGRESS_SLASH.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "100")
        self.assertEqual(match.group(2), "252")

    def test_precompiled_progress_percent(self):
        """Verify percentage progress regex"""
        self.assertIsInstance(_PROGRESS_PERCENT, re.Pattern)
        
        test_line = "Progress: 45%"
        match = _PROGRESS_PERCENT.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "45")

    def test_precompiled_frame_word(self):
        """Verify frame word regex"""
        self.assertIsInstance(_FRAME_WORD, re.Pattern)
        
        test_line = "Processing frame: 100"
        match = _FRAME_WORD.search(test_line)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "100")

    def test_important_keywords_frozenset(self):
        """Verify important keywords is frozenset for fast membership"""
        self.assertIsInstance(_IMPORTANT_KEYWORDS, frozenset)
        self.assertIn("error", _IMPORTANT_KEYWORDS)
        self.assertIn("warning", _IMPORTANT_KEYWORDS)
        self.assertIn("completed", _IMPORTANT_KEYWORDS)
        self.assertEqual(len(_IMPORTANT_KEYWORDS), 5)


class TestProPainterEngineOptimizations(unittest.TestCase):
    """Test ProPainterEngine class optimizations"""

    def test_slots_defined(self):
        """Verify __slots__ for memory efficiency"""
        self.assertTrue(hasattr(ProPainterEngine, '__slots__'))
        self.assertEqual(
            ProPainterEngine.__slots__,
            ('propainter_path', 'inference_script', 'gpu_info')
        )

    @patch('core.propainter_engine.Path')
    def test_slots_memory_reduction(self, mock_path):
        """Verify __slots__ prevents __dict__ creation"""
        # Mock Path.exists to avoid filesystem operations
        mock_path.return_value.exists.return_value = False
        
        engine = ProPainterEngine(propainter_path=None)
        self.assertFalse(hasattr(engine, '__dict__'))

    def test_memory_presets_class_constant(self):
        """Verify memory presets is class-level constant"""
        self.assertTrue(hasattr(ProPainterEngine, 'MEMORY_PRESETS'))
        presets = ProPainterEngine.MEMORY_PRESETS
        self.assertIn('low', presets)
        self.assertIn('medium', presets)
        self.assertIn('high', presets)
        self.assertIn('ultra', presets)
        self.assertEqual(len(presets), 5)  # auto, low, medium, high, ultra


class TestPathFindingOptimization(unittest.TestCase):
    """Test optimized path finding methods"""

    @patch('core.propainter_engine.Path')
    def test_find_propainter_path_custom(self, mock_path_class):
        """Test custom path with early return"""
        # Setup mock
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path
        
        engine = ProPainterEngine.__new__(ProPainterEngine)
        result = engine._find_propainter_path("C:/custom/path")
        
        self.assertIsNotNone(result)
        mock_path.exists.assert_called_once()

    @patch('core.propainter_engine.Path')
    def test_find_venv_python_simplified_loop(self, mock_path_class):
        """Test simplified venv finding with tuple iteration"""
        # Setup mock
        mock_path = Mock()
        mock_path.joinpath.return_value.exists.return_value = False
        
        engine = ProPainterEngine.__new__(ProPainterEngine)
        engine.propainter_path = mock_path
        
        result = engine._find_venv_python()
        
        # Should check multiple paths efficiently
        self.assertTrue(mock_path.joinpath.called)


class TestProgressParsingOptimization(unittest.TestCase):
    """Test optimized progress parsing with pre-compiled regex"""

    def test_frame_regex_performance(self):
        """Test pre-compiled regex vs runtime compilation"""
        test_lines = [
            "Processing: test [252 frames]...",
            "Processing 252 video frames",
            "100/252",
            "Progress: 45%",
            "Processing frame: 100",
        ]
        
        # All should match with pre-compiled patterns
        self.assertIsNotNone(_FRAME_REGEX.search(test_lines[0]))
        self.assertIsNotNone(_FRAME_REGEX_ALT.search(test_lines[1]))
        self.assertIsNotNone(_PROGRESS_SLASH.search(test_lines[2]))
        self.assertIsNotNone(_PROGRESS_PERCENT.search(test_lines[3]))
        self.assertIsNotNone(_FRAME_WORD.search(test_lines[4]))

    def test_keyword_filtering_frozenset(self):
        """Test frozenset-based keyword filtering"""
        test_messages = [
            "Error: Something went wrong",
            "Warning: Low memory",
            "Processing frame 100",
            "Completed successfully",
        ]
        
        # Filter using frozenset (optimized)
        filtered = [
            msg for msg in test_messages
            if any(kw in msg.lower() for kw in _IMPORTANT_KEYWORDS)
        ]
        
        self.assertEqual(len(filtered), 3)  # error, warning, completed
        self.assertIn("Error: Something went wrong", filtered)
        self.assertIn("Warning: Low memory", filtered)
        self.assertIn("Completed successfully", filtered)


class TestGPUDetection(unittest.TestCase):
    """Test GPU detection and memory preset recommendation"""

    @patch('subprocess.run')
    def test_detect_gpu_nvidia(self, mock_run):
        """Test NVIDIA GPU detection"""
        # Mock nvidia-smi output
        mock_run.return_value = Mock(
            returncode=0,
            stdout="GeForce RTX 3080, 10240 MiB\n"
        )
        
        engine = ProPainterEngine.__new__(ProPainterEngine)
        engine.propainter_path = Path("dummy")
        engine.inference_script = Path("dummy/inference.py")
        
        gpu_info = engine._detect_gpu()
        
        self.assertIsNotNone(gpu_info)
        self.assertIn("name", gpu_info)
        self.assertIn("vram_gb", gpu_info)

    @patch('core.propainter_engine.Path')
    def test_get_recommended_preset(self, mock_path):
        """Test preset recommendation based on VRAM"""
        mock_path.return_value.exists.return_value = False
        
        engine = ProPainterEngine(propainter_path=None)
        
        # Test different VRAM levels
        engine.gpu_info = {"vram_gb": 4}
        self.assertEqual(engine.get_recommended_preset(), "low")
        
        engine.gpu_info = {"vram_gb": 10}
        self.assertEqual(engine.get_recommended_preset(), "medium")
        
        engine.gpu_info = {"vram_gb": 14}
        self.assertEqual(engine.get_recommended_preset(), "high")
        
        engine.gpu_info = {"vram_gb": 24}
        self.assertEqual(engine.get_recommended_preset(), "ultra")


class TestMemoryRequirements(unittest.TestCase):
    """Test GPU memory requirement estimation"""

    @patch('core.propainter_engine.Path')
    def test_gpu_requirements_calculation(self, mock_path):
        """Test VRAM requirement estimation for different resolutions"""
        mock_path.return_value.exists.return_value = False
        engine = ProPainterEngine(propainter_path=None)
        
        # Test SD resolution
        req = engine.get_gpu_requirements(640, 480, use_fp16=True)
        self.assertEqual(req["estimated_vram_gb"], 6)
        self.assertTrue(req["use_fp16"])
        
        # Test HD resolution
        req = engine.get_gpu_requirements(1280, 720, use_fp16=True)
        self.assertEqual(req["estimated_vram_gb"], 19)
        
        # Test without FP16
        req = engine.get_gpu_requirements(640, 480, use_fp16=False)
        self.assertEqual(req["estimated_vram_gb"], 10)


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
