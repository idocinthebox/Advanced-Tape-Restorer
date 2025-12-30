"""
Performance Monitor Widget - Real-time system metrics
"""
import psutil
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer, Signal, QObject

class PerformanceMonitor(QObject):
    """Monitors system performance metrics and provides formatted strings."""
    
    # Signals for metric updates
    metrics_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        
        # Cached values
        self._cpu_percent = 0.0
        self._ram_used_gb = 0.0
        self._ram_total_gb = 0.0
        self._gpu_percent = 0.0
        self._gpu_temp = 0.0
        self._vram_used_gb = 0.0
        self._vram_total_gb = 0.0
        self._thread_count = 0
        self._fps = 0.0
        
        # GPU monitoring (NVIDIA only for now)
        self._gpu_available = False
        self._pynvml_available = False
        self._gpu_handle = None
        
        # Try to initialize NVIDIA monitoring
        try:
            import pynvml  # nvidia-ml-py package (import name unchanged)
            pynvml.nvmlInit()
            self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self._pynvml_available = True
            self._gpu_available = True
        except Exception:
            self._pynvml_available = False
            self._gpu_available = False
        
        # Update timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_metrics)
        self._is_processing = False
    
    def start_monitoring(self, processing: bool = False):
        """Start monitoring with appropriate interval."""
        self._is_processing = processing
        interval = 500 if processing else 2000  # 500ms when processing, 2s when idle
        self._timer.start(interval)
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self._timer.stop()
    
    def _update_metrics(self):
        """Update all metrics and emit signal."""
        # CPU and RAM (always available)
        try:
            self._cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            self._ram_used_gb = mem.used / (1024**3)
            self._ram_total_gb = mem.total / (1024**3)
            self._thread_count = psutil.cpu_count(logical=True)
        except Exception:
            # CPU/RAM monitoring failed, use defaults
            pass
        
        # GPU metrics (if available and not disabled)
        import os
        if os.getenv('DISABLE_GPU_MONITOR') or os.getenv('SKIP_GPU_MONITORING'):
            # GPU monitoring disabled via environment variable
            return
        
        if self._pynvml_available and self._gpu_handle:
            try:
                import pynvml
                
                # GPU utilization (with exception handling for hangs)
                try:
                    util = pynvml.nvmlDeviceGetUtilizationRates(self._gpu_handle)
                    self._gpu_percent = util.gpu
                except Exception:
                    # GPU monitoring failed, silently skip
                    pass
                
                # GPU temperature
                try:
                    self._gpu_temp = pynvml.nvmlDeviceGetTemperature(
                        self._gpu_handle, pynvml.NVML_TEMPERATURE_GPU
                    )
                except:
                    self._gpu_temp = 0
                
                # VRAM
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(self._gpu_handle)
                self._vram_used_gb = mem_info.used / (1024**3)
                self._vram_total_gb = mem_info.total / (1024**3)
                
            except Exception:
                # GPU monitoring failed silently (can be re-enabled with debug mode)
                pass
        
        # Emit metrics
        metrics = {
            'cpu_percent': self._cpu_percent,
            'ram_used_gb': self._ram_used_gb,
            'ram_total_gb': self._ram_total_gb,
            'gpu_percent': self._gpu_percent,
            'gpu_temp': self._gpu_temp,
            'vram_used_gb': self._vram_used_gb,
            'vram_total_gb': self._vram_total_gb,
            'thread_count': self._thread_count,
            'fps': self._fps,
            'gpu_available': self._gpu_available
        }
        self.metrics_updated.emit(metrics)
    
    def set_fps(self, fps: float):
        """Update FPS from external source (FFmpeg)."""
        self._fps = fps
    
    def get_cpu_label(self) -> str:
        """Get formatted CPU label."""
        return f"🖥️ CPU: {self._cpu_percent:.0f}%"
    
    def get_ram_label(self) -> str:
        """Get formatted RAM label."""
        return f"💾 RAM: {self._ram_used_gb:.1f}/{self._ram_total_gb:.1f} GB"
    
    def get_threads_label(self) -> str:
        """Get formatted threads label."""
        active = int(self._cpu_percent / 100 * self._thread_count)
        return f"⚙️ Threads: {active}/{self._thread_count}"
    
    def get_cuda_status(self) -> str:
        """Get CUDA status label."""
        if not self._gpu_available:
            return "CUDA: Unavailable"
        if not self._is_processing:
            return "CUDA: Available ✓"
        
        # Check for thermal throttling (>80°C)
        if self._gpu_temp > 80:
            return "CUDA: Throttled ⚠️"
        return "CUDA: Active ⚡"
    
    def get_gpu_label(self) -> str:
        """Get formatted GPU label."""
        if not self._gpu_available:
            return ""
        
        # Temperature emoji based on heat
        if self._gpu_temp < 66:
            temp_icon = "🌡️"
        elif self._gpu_temp < 76:
            temp_icon = "🔥"
        elif self._gpu_temp < 86:
            temp_icon = "🔥🔥 ⚠️"
        else:
            temp_icon = "🔥🔥🔥 ⚠️"
        
        return f"🎮 GPU: {self._gpu_percent:.0f}% {temp_icon} {self._gpu_temp:.0f}°C"
    
    def get_vram_label(self) -> str:
        """Get formatted VRAM label with pressure warnings."""
        if not self._gpu_available:
            return ""
        
        percent = (self._vram_used_gb / self._vram_total_gb * 100) if self._vram_total_gb > 0 else 0
        
        # VRAM pressure warnings
        if percent > 95:
            warning = " ⚠️ CRITICAL"
        elif percent > 90:
            warning = " ⚠️ HIGH"
        elif percent > 85:
            warning = " ⚠️"
        else:
            warning = ""
        
        return f"VRAM: {self._vram_used_gb:.1f}/{self._vram_total_gb:.1f} GB{warning}"
    
    def get_fps_label(self) -> str:
        """Get formatted FPS label."""
        if self._fps <= 0:
            return "⚡ -- fps"
        return f"⚡ {self._fps:.1f} fps"
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_monitoring()
        if self._pynvml_available:
            try:
                import pynvml
                pynvml.nvmlShutdown()
            except:
                pass
