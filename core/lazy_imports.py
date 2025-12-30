"""
Lazy Import System for Performance Optimization
Defers heavy imports until they're actually needed
"""

import importlib
import sys
from typing import Any, Callable, Optional


class LazyModule:
    """
    Lazy module loader - imports module only when attributes are accessed.

    Usage:
        np = LazyModule('numpy')
        # numpy not imported yet!

        arr = np.array([1, 2, 3])  # Now numpy gets imported
    """

    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: Optional[Any] = None

    def _load(self):
        """Load the module if not already loaded."""
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, name: str):
        """Intercept attribute access and load module on-demand."""
        return getattr(self._load(), name)

    def __dir__(self):
        """Support for dir() and autocomplete."""
        return dir(self._load())


def lazy_import(module_name: str) -> LazyModule:
    """
    Create a lazy-loaded module.

    Args:
        module_name: Name of module to lazy-load

    Returns:
        LazyModule proxy that loads on first use

    Example:
        # Instead of:
        import numpy as np

        # Use:
        np = lazy_import('numpy')
    """
    return LazyModule(module_name)


def import_once(func: Callable) -> Callable:
    """
    Decorator to cache expensive imports in a function.

    The function will import heavy modules only once, then reuse them.

    Example:
        @import_once
        def process_with_numpy(data):
            import numpy as np  # Only imported once
            return np.array(data).mean()
    """
    _cache = {}

    def wrapper(*args, **kwargs):
        if "result" not in _cache:
            _cache["result"] = func(*args, **kwargs)
        return _cache["result"]

    return wrapper


# Pre-configured lazy imports for common heavy modules
numpy = LazyModule("numpy")
cv2 = LazyModule("cv2")
torch = LazyModule("torch")
PIL = LazyModule("PIL")


__all__ = ["LazyModule", "lazy_import", "import_once", "numpy", "cv2", "torch", "PIL"]
