"""
Takebox AI Cost Tracker - A toolkit for tracking and managing Takebox AI API usage and costs.
"""

__version__ = "0.1.0"

# Import main classes conditionally to avoid errors if dependencies are missing
try:
    from .client import OptimizedJuglowClient
    __all__ = ["OptimizedJuglowClient"]
except ImportError:
    import logging
    logging.warning("Failed to import OptimizedJuglowClient. Some dependencies may be missing.")
    __all__ = []

# Try to import other utilities if available
try:
    from .utils.cost_tracker import CostTracker
    from .utils.cache import APICache
    from .utils.rate_limiter import APIRateLimiter
    __all__.extend(["CostTracker", "APICache", "APIRateLimiter"])
except ImportError:
    import logging
    logging.warning("Failed to import utility modules. Some dependencies may be missing.") 