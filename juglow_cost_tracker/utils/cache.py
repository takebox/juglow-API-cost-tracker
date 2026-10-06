"""
Cache implementation for API responses.
"""

import os
import json
import time
import hashlib
import logging
import sqlite3
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class APICache:
    """Simple cache for API responses to avoid duplicate calls.
    
    This cache implementation helps reduce API costs by storing and retrieving
    responses for identical requests, avoiding unnecessary duplicate calls.
    """
    
    def __init__(self, cache_dir: str = None, ttl: int = 86400):
        """Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live for cache entries in seconds (default: 1 day)
        """
        if cache_dir is None:
            # Use user's cache directory by default
            self.cache_dir = os.path.join(os.path.expanduser('~'), '.Takebox AI-cost-tracker', 'cache')
        else:
            self.cache_dir = cache_dir
            
        self.ttl = ttl
        self.memory_cache = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize sqlite cache
        self.db_path = os.path.join(self.cache_dir, 'api_cache.db')
        self._init_db()
    
    def _init_db(self):
        """Initialize the cache database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            data TEXT,
            timestamp INTEGER )
        ''')
        conn.commit()
        conn.close()
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key from function name and arguments.
        
        Args:
            func_name: Name of the function being cached
            args: Positional arguments to the function
            kwargs: Keyword arguments to the function
            
        Returns:
            Cache key as an MD5 hash
        """
        # Combine function name and arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        
        # Convert to a consistent string and hash it
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached item or None if not found/expired
        """
        # Check memory cache first for fastest retrieval
        memory_result = self.memory_cache.get(key)
        if memory_result:
            timestamp, data = memory_result
            if time.time() - timestamp <= self.ttl:
                return data
            # Remove from memory if expired
            del self.memory_cache[key]
        
        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT data, timestamp FROM cache WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            data_str, timestamp = result
            
            # Check if expired
            if time.time() - timestamp <= self.ttl:
                data = json.loads(data_str)
                
                # Add to memory cache for faster future retrieval
                self.memory_cache[key] = (timestamp, data)
                
                return data
            else:
                # Remove expired item
                self.remove(key)
        
        return None
    
    def set(self, key: str, value: Any):
        """Store item in cache.
        
        Args:
            key: Cache key
            value: Item to cache
        """
        timestamp = time.time()
        
        # Store in memory
        self.memory_cache[key] = (timestamp, value)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            data_str = json.dumps(value)
            cursor.execute(
                'INSERT OR REPLACE INTO cache (key, data, timestamp) VALUES (?, ?, ?)',
                (key, data_str, timestamp)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
        finally:
            conn.close()
    
    def remove(self, key: str):
        """Remove item from cache.
        
        Args:
            key: Cache key
        """
        # Remove from memory
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
        conn.commit()
        conn.close()
    
    def clear(self):
        """Clear all cache entries."""
        # Clear memory cache
        self.memory_cache = {}
        
        # Clear database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache')
        conn.commit()
        conn.close()
    
    def clear_expired(self):
        """Remove all expired cache entries."""
        expired_time = time.time() - self.ttl
        
        # Clear from memory
        for key, (timestamp, _) in list(self.memory_cache.items()):
            if timestamp < expired_time:
                del self.memory_cache[key]
        
        # Clear from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache WHERE timestamp < ?', (expired_time,))
        conn.commit()
        conn.close()
        
        logger.info(f"Cleared expired cache entries older than {self.ttl} seconds") 