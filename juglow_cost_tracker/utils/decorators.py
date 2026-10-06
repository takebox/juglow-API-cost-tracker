"""
Decorator utilities for API optimization.
"""

import functools
import logging
from typing import Callable, TypeVar, Any, Optional

from .cache import APICache
from .rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)

# Type variable for generic function type
T = TypeVar('T')

def cached_api_call(ttl: int = 86400, cache_instance: Optional[APICache] = None):
    """Decorator for caching API calls.
    
    Args:
        ttl: Time-to-live in seconds (default: 1 day)
        cache_instance: Optional specific cache instance
        
    Returns:
        Decorator function
    """
    # Create or use cache instance
    cache = cache_instance or APICache(ttl=ttl)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if bypass_cache is specified
            bypass_cache = kwargs.pop('bypass_cache', False)
            
            if bypass_cache:
                return func(*args, **kwargs)
            
            # Generate a unique key for this function call
            cache_key = cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Not in cache, call the function
            result = func(*args, **kwargs)
            
            # Store in cache if cacheable (None results are not cached)
            if result is not None:
                cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator

def rate_limited_api_call(rate_limiter: Optional[APIRateLimiter] = None):
    """Decorator for rate limiting API calls.
    
    Args:
        rate_limiter: Optional specific rate limiter instance
        
    Returns:
        Decorator function
    """
    # Create or use rate limiter instance
    limiter = rate_limiter or APIRateLimiter()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Wait if needed based on rate limits
            limiter.wait_if_needed()
            
            # Call the function
            return func(*args, **kwargs)
        return wrapper
    return decorator

def tracked_api_call(api_name: str, endpoint: str = None, company: str = None):
    """Decorator for tracking API call costs.
    
    This decorator requires the wrapped function to return a dictionary
    that includes 'input_tokens' and 'output_tokens' keys.
    
    Args:
        api_name: Name of the API being called
        endpoint: Optional endpoint or model name
        company: Optional company or project name
        
    Returns:
        Decorator function
    """
    from .cost_tracker import CostTracker
    
    def decorator(func: Callable[..., dict]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get actual endpoint and company from kwargs if provided
            actual_endpoint = kwargs.get('model', endpoint)
            actual_company = kwargs.get('company', company)
            
            # Call the function and get result
            result = func(*args, **kwargs)
            
            # Track the API usage cost
            cost_tracker = CostTracker()
            
            # Extract token counts from result
            tokens_in = result.get('input_tokens', 0)
            tokens_out = result.get('output_tokens', 0)
            
            if tokens_in > 0 or tokens_out > 0:
                cost_tracker.log_cost(
                    api_name=api_name,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    endpoint=actual_endpoint,
                    company=actual_company )
            
            return result
        return wrapper
    return decorator

def optimized_api_call(api_name: str, endpoint: str = None, company: str = None, 
                     ttl: int = 86400, cache_instance: Optional[APICache] = None,
                     rate_limiter: Optional[APIRateLimiter] = None):
    """Combined decorator for optimization, rate limiting, and tracking.
    
    This decorator combines caching, rate limiting, and cost tracking.
    
    Args:
        api_name: Name of the API being called
        endpoint: Optional endpoint or model name
        company: Optional company or project name
        ttl: Cache time-to-live in seconds
        cache_instance: Optional specific cache instance
        rate_limiter: Optional specific rate limiter instance
        
    Returns:
        Decorator function
    """
    def decorator(func):
        # Apply decorators in the correct order:
        # 1. Caching (outermost - we check cache before rate limiting)
        # 2. Rate limiting (middle - only rate limit actual API calls)
        # 3. Tracking (innermost - track actual API calls)
        tracked_func = tracked_api_call(api_name, endpoint, company)(func)
        rate_limited_func = rate_limited_api_call(rate_limiter)(tracked_func)
        cached_func = cached_api_call(ttl, cache_instance)(rate_limited_func)
        
        return cached_func
    return decorator 