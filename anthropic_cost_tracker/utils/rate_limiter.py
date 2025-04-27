"""
Rate limiter for API calls.
"""

import time
import logging
import threading
from typing import List

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """Rate limiter to prevent exceeding API rate limits.
    
    This class helps prevent hitting rate limits by tracking API calls
    and waiting if necessary before allowing additional calls.
    """
    
    def __init__(self, calls_per_minute: int = 60, calls_per_day: int = 10000):
        """Initialize the rate limiter.
        
        Args:
            calls_per_minute: Maximum API calls allowed per minute
            calls_per_day: Maximum API calls allowed per day
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        self.minute_calls: List[float] = []
        self.day_calls: List[float] = []
        self.lock = threading.Lock()
        
    def wait_if_needed(self):
        """Check rate limits and wait if necessary.
        
        This method should be called before making an API call.
        It will block if rate limits would be exceeded, 
        ensuring that API calls stay within the defined limits.
        """
        with self.lock:
            current_time = time.time()
            
            # Remove timestamps older than a minute
            minute_ago = current_time - 60
            self.minute_calls = [t for t in self.minute_calls if t > minute_ago]
            
            # Remove timestamps older than a day
            day_ago = current_time - 86400
            self.day_calls = [t for t in self.day_calls if t > day_ago]
            
            # Check if we're over the limits
            if len(self.minute_calls) >= self.calls_per_minute:
                # Calculate wait time (to the oldest call + 60s)
                wait_time = self.minute_calls[0] + 60 - current_time
                logger.warning(f"Rate limit approaching: waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                return self.wait_if_needed()  # Recursively check again after waiting
            
            if len(self.day_calls) >= self.calls_per_day:
                wait_time = self.day_calls[0] + 86400 - current_time
                logger.warning(f"Daily limit reached: waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                return self.wait_if_needed()  # Recursively check again after waiting
            
            # Record this call
            self.minute_calls.append(current_time)
            self.day_calls.append(current_time)
            
    def get_current_usage(self):
        """Get the current usage levels.
        
        Returns:
            Dictionary with current usage statistics
        """
        with self.lock:
            current_time = time.time()
            
            # Remove timestamps older than a minute or day
            minute_ago = current_time - 60
            day_ago = current_time - 86400
            
            # Clean up and count current usage
            self.minute_calls = [t for t in self.minute_calls if t > minute_ago]
            self.day_calls = [t for t in self.day_calls if t > day_ago]
            
            minute_usage = len(self.minute_calls)
            day_usage = len(self.day_calls)
            
            return {
                "minute_usage": minute_usage,
                "minute_limit": self.calls_per_minute,
                "minute_percent": (minute_usage / self.calls_per_minute) * 100 if self.calls_per_minute else 0,
                "day_usage": day_usage,
                "day_limit": self.calls_per_day,
                "day_percent": (day_usage / self.calls_per_day) * 100 if self.calls_per_day else 0
            } 