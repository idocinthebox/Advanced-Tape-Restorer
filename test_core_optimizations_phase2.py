"""
Comprehensive test suite for Phase 2 core optimizations:
- ai_bridge.py
- gpu_accelerator.py
- resumable_processor.py

Tests verify:
1. __slots__ implementation
2. Functionality preservation
3. Memory optimizations
4. API compatibility
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent))


class TestAIBridgeOptimization(unittest.TestCase):
    """Test ai_bridge.py optimizations"""
    
    def test_ai_bridge_has_slots(self):
        """Verify AIBridge uses __slots__"""
        # Mock vapoursynth before import
        sys.modules['vapoursynth'] = MagicMock()
        from core.ai_bridge import AIBridge
        
        self.assertTrue(hasattr(AIBridge, '__slots__'))
        self.assertIn('manager', AIBridge.__slots__)
        self.assertIn('progress_callback', AIBridge.__slots__)
        self.assertIn('log_callback', AIBridge.__slots__)
        
        # Verify no __dict__ when using __slots__
        with patch('core.ai_bridge.ModelManager'):
            with patch('core.ai_bridge.ENGINE_REGISTRY', {'realesrgan': Mock()}):
                bridge = AIBridge.__new__(AIBridge)
                self.assertFalse(hasattr(bridge, '__dict__'),
                               "__slots__ should prevent __dict__ creation")
    
    def test_ai_bridge_initialization(self):
        """Test AIBridge can be instantiated"""
        sys.modules['vapoursynth'] = MagicMock()
        from core.ai_bridge import AIBridge
        
        with patch('core.ai_bridge.ModelManager') as MockManager:
            with patch('core.ai_bridge.ENGINE_REGISTRY', {'realesrgan': Mock()}):
                mock_manager = MockManager.return_value
                
                bridge = AIBridge(
                    registry_path="test_registry.yaml",
                    model_root="/test/models",
                    commercial_mode=True
                )
                
                self.assertEqual(bridge.manager, mock_manager)
                self.assertIsNone(bridge.progress_callback)
                self.assertIsNone(bridge.log_callback)
    
    def test_log_callback_optimization(self):
        """Test optimized logging doesn't call print when no callback"""
        sys.modules['vapoursynth'] = MagicMock()
        from core.ai_bridge import AIBridge
        
        with patch('core.ai_bridge.ModelManager'):
            with patch('core.ai_bridge.ENGINE_REGISTRY', {'realesrgan': Mock()}):
                bridge = AIBridge.__new__(AIBridge)
                bridge.log_callback = None
                
                # Should not raise error or print
                bridge._log("Test message")  # No-op when callback is None
    
    def test_list_available_models(self):
        """Test model listing works"""
        sys.modules['vapoursynth'] = MagicMock()
        from core.ai_bridge import AIBridge
        
        with patch('core.ai_bridge.ModelManager') as MockManager:
            with patch('core.ai_bridge.ENGINE_REGISTRY', {'realesrgan': Mock()}):
                mock_manager = MockManager.return_value
                mock_manager.list_models.return_value = [
                    {'id': 'model1', 'engine': 'realesrgan'},
                    {'id': 'model2', 'engine': 'rife'}
                ]
                
                bridge = AIBridge("test.yaml", "/models")
                result = bridge.list_available_models()
                
                self.assertEqual(len(result), 2)
                mock_manager.list_models.assert_called_once_with(None)


class TestGPUAcceleratorOptimization(unittest.TestCase):
    """Test gpu_accelerator.py optimizations"""
    
    def test_module_constants_defined(self):
        """Verify module-level constants exist"""
        from core import gpu_accelerator
        
        self.assertTrue(hasattr(gpu_accelerator, '_GB_IN_BYTES'))
        self.assertEqual(gpu_accelerator._GB_IN_BYTES, 1024 ** 3)
        self.assertTrue(hasattr(gpu_accelerator, '_DEFAULT_DEVICE_NAME'))
        self.assertEqual(gpu_accelerator._DEFAULT_DEVICE_NAME, "CPU (No GPU)")
    
    def test_gpu_accelerator_has_slots(self):
        """Verify GPUAccelerator uses __slots__"""
        from core.gpu_accelerator import GPUAccelerator
        
        self.assertTrue(hasattr(GPUAccelerator, '__slots__'))
        expected_slots = ('device', 'backend', 'gpu_available', 'device_name', 'memory_gb')
        for slot in expected_slots:
            self.assertIn(slot, GPUAccelerator.__slots__)
    
    def test_cuda_video_processor_has_slots(self):
        """Verify CUDAVideoProcessor uses __slots__"""
        from core.gpu_accelerator import CUDAVideoProcessor
        
        self.assertTrue(hasattr(CUDAVideoProcessor, '__slots__'))
        expected_slots = ('gpu', 'torch', 'device')
        for slot in expected_slots:
            self.assertIn(slot, CUDAVideoProcessor.__slots__)
    
    def test_gpu_accelerator_cpu_fallback(self):
        """Test GPU accelerator falls back to CPU correctly"""
        from core.gpu_accelerator import GPUAccelerator
        
        with patch('core.gpu_accelerator.warnings.warn'):
            gpu = GPUAccelerator()
            
            # Should work even without GPU
            self.assertIsNotNone(gpu.backend)
            self.assertIsNotNone(gpu.device_name)
            self.assertEqual(gpu.memory_gb, 0)
    
    def test_get_info_returns_dict(self):
        """Test get_info returns proper dictionary"""
        from core.gpu_accelerator import GPUAccelerator
        
        gpu = GPUAccelerator()
        info = gpu.get_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('available', info)
        self.assertIn('backend', info)
        self.assertIn('device_name', info)
        self.assertIn('memory_gb', info)
    
    def test_is_available_method(self):
        """Test is_available method works"""
        from core.gpu_accelerator import GPUAccelerator
        
        gpu = GPUAccelerator()
        result = gpu.is_available()
        
        self.assertIsInstance(result, bool)
        self.assertEqual(result, gpu.gpu_available)
    
    def test_check_gpu_requirements(self):
        """Test GPU requirements check function"""
        from core.gpu_accelerator import check_gpu_requirements
        
        reqs = check_gpu_requirements()
        
        self.assertIsInstance(reqs, dict)
        self.assertIn('cuda_available', reqs)
        self.assertIn('opencl_available', reqs)
        self.assertIn('recommended_libraries', reqs)
        self.assertIn('install_commands', reqs)


class TestResumableProcessorOptimization(unittest.TestCase):
    """Test resumable_processor.py optimizations"""
    
    def test_processing_checkpoint_dataclass(self):
        """Test ProcessingCheckpoint dataclass works"""
        from core.resumable_processor import ProcessingCheckpoint
        
        checkpoint = ProcessingCheckpoint(
            job_id="test_001",
            input_file="input.mp4",
            output_file="output.mp4",
            total_frames=1000,
            processed_frames=500,
            current_frame=500,
            start_time=1000.0,
            last_update=1500.0,
            settings_hash="abc123",
            status="running"
        )
        
        self.assertEqual(checkpoint.job_id, "test_001")
        self.assertEqual(checkpoint.total_frames, 1000)
        self.assertEqual(checkpoint.processed_frames, 500)
    
    def test_progress_percent_calculation(self):
        """Test progress percentage calculation"""
        from core.resumable_processor import ProcessingCheckpoint
        
        checkpoint = ProcessingCheckpoint(
            job_id="test", input_file="in.mp4", output_file="out.mp4",
            total_frames=1000, processed_frames=250, current_frame=250,
            start_time=0.0, last_update=10.0, settings_hash="hash", status="running"
        )
        
        self.assertEqual(checkpoint.progress_percent(), 25.0)
    
    def test_elapsed_time_calculation(self):
        """Test elapsed time calculation"""
        from core.resumable_processor import ProcessingCheckpoint
        
        checkpoint = ProcessingCheckpoint(
            job_id="test", input_file="in.mp4", output_file="out.mp4",
            total_frames=1000, processed_frames=500, current_frame=500,
            start_time=100.0, last_update=200.0, settings_hash="hash", status="running"
        )
        
        self.assertEqual(checkpoint.elapsed_time(), 100.0)
    
    def test_resumable_processor_has_slots(self):
        """Verify ResumableProcessor uses __slots__"""
        from core.resumable_processor import ResumableProcessor
        
        self.assertTrue(hasattr(ResumableProcessor, '__slots__'))
        expected_slots = ('job_id', 'input_file', 'output_file', 'checkpoint_dir', 
                         'checkpoint_interval', 'checkpoint')
        for slot in expected_slots:
            self.assertIn(slot, ResumableProcessor.__slots__)
    
    def test_checkpoint_to_dict(self):
        """Test checkpoint serialization to dict"""
        from core.resumable_processor import ProcessingCheckpoint
        
        checkpoint = ProcessingCheckpoint(
            job_id="test", input_file="in.mp4", output_file="out.mp4",
            total_frames=100, processed_frames=50, current_frame=50,
            start_time=0.0, last_update=10.0, settings_hash="hash", status="running"
        )
        
        data = checkpoint.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['job_id'], "test")
        self.assertEqual(data['total_frames'], 100)
        self.assertEqual(data['processed_frames'], 50)
    
    def test_checkpoint_from_dict(self):
        """Test checkpoint deserialization from dict"""
        from core.resumable_processor import ProcessingCheckpoint
        
        data = {
            'job_id': "test",
            'input_file': "in.mp4",
            'output_file': "out.mp4",
            'total_frames': 100,
            'processed_frames': 50,
            'current_frame': 50,
            'start_time': 0.0,
            'last_update': 10.0,
            'settings_hash': "hash",
            'status': "running",
            'error_message': None
        }
        
        checkpoint = ProcessingCheckpoint.from_dict(data)
        
        self.assertEqual(checkpoint.job_id, "test")
        self.assertEqual(checkpoint.total_frames, 100)
        self.assertEqual(checkpoint.processed_frames, 50)
    
    def test_estimated_remaining_calculation(self):
        """Test remaining time estimation"""
        from core.resumable_processor import ProcessingCheckpoint
        
        # 500 frames in 100 seconds = 5 fps
        # 500 remaining frames / 5 fps = 100 seconds remaining
        checkpoint = ProcessingCheckpoint(
            job_id="test", input_file="in.mp4", output_file="out.mp4",
            total_frames=1000, processed_frames=500, current_frame=500,
            start_time=0.0, last_update=100.0, settings_hash="hash", status="running"
        )
        
        estimated = checkpoint.estimated_remaining()
        self.assertAlmostEqual(estimated, 100.0, places=1)


class TestMemoryOptimizationVerification(unittest.TestCase):
    """Verify all optimized classes prevent __dict__ creation"""
    
    def test_no_dict_on_optimized_classes(self):
        """Verify __slots__ prevents __dict__ on all optimized classes"""
        from core.gpu_accelerator import GPUAccelerator, CUDAVideoProcessor
        from core.resumable_processor import ResumableProcessor
        from pathlib import Path
        
        # GPUAccelerator
        gpu = GPUAccelerator()
        self.assertFalse(hasattr(gpu, '__dict__'),
                        "GPUAccelerator should not have __dict__ with __slots__")
        
        # ResumableProcessor
        with patch('core.resumable_processor.Path.mkdir'):
            with patch('core.resumable_processor.Path.exists', return_value=False):
                processor = ResumableProcessor(
                    job_id="test",
                    input_file=Path("in.mp4"),
                    output_file=Path("out.mp4"),
                    checkpoint_dir=Path("/tmp")
                )
                self.assertFalse(hasattr(processor, '__dict__'),
                                "ResumableProcessor should not have __dict__ with __slots__")


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAIBridgeOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestGPUAcceleratorOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestResumableProcessorOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryOptimizationVerification))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("  Phase 2 Core Module Optimization Tests")
    print("  Testing: ai_bridge, gpu_accelerator, resumable_processor")
    print("=" * 70)
    print()
    
    result = run_tests()
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("  ✓ ALL TESTS PASSED")
    else:
        print("  ✗ SOME TESTS FAILED")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
