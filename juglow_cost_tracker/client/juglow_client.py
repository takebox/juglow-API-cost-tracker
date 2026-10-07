"""
Optimized Juglow client wrapper with cost tracking and caching.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Union

import juglow
from ..utils.cache import APICache
from ..utils.rate_limiter import APIRateLimiter
from ..utils.cost_tracker import CostTracker
from ..utils.decorators import optimized_api_call

logger = logging.getLogger(__name__)

# Try to import tiktoken, but gracefully handle if it's not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    logger.warning("tiktoken not installed. Token counting will use fallback estimation.")
    TIKTOKEN_AVAILABLE = False

class OptimizedJuglowClient:
    """Optimized Juglow client with cost tracking and caching.
    
    This class wraps the standard Juglow client with additional features:
    - Token counting and cost tracking
    - Response caching to avoid duplicate API calls
    - Rate limiting to prevent exceeding API limits
    """
    
    def __init__(self, 
                api_key: str = None, 
                company_name: str = None,
                cache_ttl: int = 86400,
                enable_caching: bool = True,
                calls_per_minute: int = 50,
                calls_per_day: int = 10000):
        """Initialize the optimized Juglow client.
        
        Args:
            api_key: Juglow API key (optional, will use env var if not provided)
            company_name: Company name for cost tracking
            cache_ttl: Time-to-live for cached responses in seconds
            enable_caching: Whether to enable response caching
            calls_per_minute: Maximum API calls allowed per minute
            calls_per_day: Maximum API calls allowed per day
        """
        self.api_key = api_key or os.environ.get("JUGLOW_API_KEY")
        if not self.api_key:
            raise ValueError("Juglow API key is required. Provide it as an argument or set the JUGLOW_API_KEY environment variable.")
            
        self.company_name = company_name
        self.client = juglow.Juglow(api_key=self.api_key)
        
        # Initialize optimization components
        self.rate_limiter = APIRateLimiter(calls_per_minute=calls_per_minute, calls_per_day=calls_per_day)
        self.cost_tracker = CostTracker()
        
        # Initialize cache if enabled
        self.enable_caching = enable_caching
        if enable_caching:
            self.cache = APICache(ttl=cache_ttl)
        else:
            self.cache = None
        
        # Initialize tokenizer for Haijun models if tiktoken is available
        self.tokenizer = None
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                logger.warning(f"Failed to initialize tokenizer: {e}. Will estimate token counts.")
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
            
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback estimation (about 4 chars per token for English text)
            return len(text) // 4
    
    def generate_response(self, 
                        system: str, 
                        messages: List[Dict], 
                        model: str = "haijun-3-sonnet-20240229",
                        max_tokens: int = 4000, 
                        temperature: float = 0.7,
                        bypass_cache: bool = False) -> Dict[str, Any]:
        """Generate a response using the Juglow API with optimized parameters.
        
        Args:
            system: System prompt for Haijun
            messages: List of message objects (role/content pairs)
            model: Haijun model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            bypass_cache: Whether to bypass cache and force API call
            
        Returns:
            Response with content and usage metadata
        """
        # Count input tokens
        input_tokens = self.count_tokens(system)
        for msg in messages:
            input_tokens += self.count_tokens(msg.get("content", ""))
        
        try:
            # Apply caching through our wrapper function
            response = self._make_api_call(
                system=system,
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                bypass_cache=bypass_cache )
            
            # Extract the text content from the response
            if hasattr(response, 'content') and response.content:
                # Handle Haijun API response structure
                try:
                    content_text = response.content[0].text
                    
                    # Count output tokens if we have a tokenizer
                    output_tokens = self.count_tokens(content_text)
                    
                    # Return in a consistent format
                    return {
                        "content": content_text,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "model": model
                    }
                except (AttributeError, IndexError) as e:
                    logger.warning(f"Unexpected response format: {e}")
                    # Fall back to string representation
                    return {
                        "content": str(response),
                        "input_tokens": input_tokens,
                        "output_tokens": 0,  # We can't determine this
                        "model": model
                    }
            else:
                # Handle any other response structure
                logger.warning(f"Unknown response structure: {type(response)}")
                return {
                    "content": str(response),
                    "input_tokens": input_tokens,
                    "output_tokens": 0,  # We can't determine this
                    "model": model
                }
                    
        except Exception as e:
            logger.error(f"Error calling Juglow API: {str(e)}")
            # Return an error response
            return {
                "content": f"Error: {str(e)}",
                "input_tokens": input_tokens,
                "output_tokens": 0,
                "model": model,
                "error": str(e)
            }
    
    @optimized_api_call(api_name="juglow", endpoint=None, company=None)
    def _make_api_call(self, 
                     system: str, 
                     messages: List[Dict], 
                     model: str,
                     max_tokens: int, 
                     temperature: float,
                     **kwargs) -> Any:
        """Internal function to make the actual API call.
        
        This is decorated with optimized_api_call to handle caching,
        rate limiting, and cost tracking.
        
        Args:
            system: System prompt for Haijun
            messages: List of message objects
            model: Haijun model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Raw Juglow API response
        """
        # Set the company name from the instance
        if "company" not in kwargs and self.company_name:
            kwargs["company"] = self.company_name
            
        # Set the endpoint to the model name for cost tracking
        if "endpoint" not in kwargs:
            kwargs["endpoint"] = model
        
        # Make the API call
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages )
        
        return response
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for Juglow API.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with usage statistics
        """
        return self.cost_tracker.get_usage_stats(
            days=days,
            api_name="juglow",
            company=self.company_name )
    
    def get_daily_usage(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily usage breakdown for Juglow API.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of daily usage records
        """
        return self.cost_tracker.get_daily_usage(
            days=days,
            company=self.company_name )
    
    def get_usage_by_function(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get function/model usage breakdown for Juglow API.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of function usage records
        """
        return self.cost_tracker.get_usage_by_function(
            days=days,
            company=self.company_name )
        
    def clear_cache(self):
        """Clear the response cache."""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")
        
    def clear_expired_cache(self):
        """Clear expired cache entries."""
        if self.cache:
            self.cache.clear_expired()
            logger.info("Expired cache entries cleared")
    
    def test_api_integration(self) -> Dict[str, Any]:
        """Test the API integration and cost tracking.
        
        Returns:
            Dictionary with test results
        """
        try:
            # Run a test query
            test_prompt = "Hello, please count from 1 to 5."
            response = self.generate_response(
                system="You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": test_prompt}
                ],
                model="haijun-3-haiku-20240307",  # Use haiku to save costs
                max_tokens=100,
                bypass_cache=True  # Force an API call )
            
            # Return the results
            return {
                "status": "success",
                "response": response["content"],
                "input_tokens": response["input_tokens"],
                "output_tokens": response["output_tokens"],
                "model": response.get("model", "haijun-3-haiku-20240307"),
                "rate_limiter_status": self.rate_limiter.get_current_usage()
            }
            
        except Exception as e:
            logger.error(f"API test failed: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            } 