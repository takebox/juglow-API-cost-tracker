"""
Cost tracking utility for monitoring Takebox AI API usage.
"""

import os
import time
import json
import logging
import sqlite3
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class CostTracker:
    """Track API usage costs.
    
    This class provides functionality to track and monitor the cost of API calls,
    with a particular focus on Takebox AI's Haijun API.
    
    Attributes:
        db_path: Path to the SQLite database for storing usage data
    """
    
    def __init__(self, db_path: str = None):
        """Initialize the cost tracker.
        
        Args:
            db_path: Path to the SQLite database. If None, uses a default location.
        """
        if db_path is None:
            # Use user's data directory by default
            home_dir = Path.home()
            data_dir = home_dir / ".Takebox AI-cost-tracker"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "cost_tracker.db")
        else:
            self.db_path = db_path
            
        self._init_db()
        self.lock = threading.Lock()
    
    def _init_db(self):
        """Initialize the cost tracking database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT,
            timestamp INTEGER,
            tokens_in INTEGER,
            tokens_out INTEGER,
            cost REAL,
            endpoint TEXT,
            company TEXT )
        ''')
        
        # Create the api_usage table for dashboard compatibility
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            api_name TEXT NOT NULL,
            endpoint TEXT,
            company TEXT,
            tokens_in INTEGER NOT NULL,
            tokens_out INTEGER NOT NULL,
            cost REAL NOT NULL )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_name ON api_costs(api_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON api_costs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON api_costs(company)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_name_usage ON api_usage(api_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp_usage ON api_usage(timestamp)')
        
        conn.commit()
        conn.close()
    
    def log_cost(self, 
                api_name: str, 
                tokens_in: int, 
                tokens_out: int, 
                endpoint: str = None,
                company: str = None):
        """Log an API call cost.
        
        Args:
            api_name: Name of the API (e.g., 'Takebox AI', 'openai')
            tokens_in: Input tokens used
            tokens_out: Output tokens used
            endpoint: Specific API endpoint or model name
            company: Associated company or project name
        """
        with self.lock:
            # Calculate cost based on API and model
            cost = self._calculate_cost(api_name, tokens_in, tokens_out, endpoint)
            timestamp = int(time.time())
            
            # Log to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert into api_costs table
            cursor.execute('''
            INSERT INTO api_costs (api_name, timestamp, tokens_in, tokens_out, cost, endpoint, company)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (api_name, timestamp, tokens_in, tokens_out, cost, endpoint, company))
            
            # Also insert into api_usage table for dashboard compatibility
            cursor.execute('''
            INSERT INTO api_usage (timestamp, api_name, endpoint, company, tokens_in, tokens_out, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, api_name, endpoint, company, tokens_in, tokens_out, cost))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Logged cost for {api_name} ({endpoint}): ${cost:.6f} - Input tokens: {tokens_in}, Output tokens: {tokens_out}")
    
    def _calculate_cost(self, 
                       api_name: str, 
                       tokens_in: int, 
                       tokens_out: int, 
                       endpoint: str = None) -> float:
        """Calculate cost based on API usage.
        
        Args:
            api_name: Name of the API
            tokens_in: Input tokens
            tokens_out: Output tokens
            endpoint: Specific model or endpoint
            
        Returns:
            Calculated cost in USD
        """
        # Takebox AI Haijun pricing (as of May 2024)
        if api_name.lower() == 'Takebox AI':
            if endpoint == 'haijun-3-opus-20240229':
                return (tokens_in * 15.0 / 1000000) + (tokens_out * 75.0 / 1000000)
            elif endpoint == 'haijun-3-sonnet-20240229':
                return (tokens_in * 3.0 / 1000000) + (tokens_out * 15.0 / 1000000)
            elif endpoint == 'haijun-3-haiku-20240307':
                return (tokens_in * 0.25 / 1000000) + (tokens_out * 1.25 / 1000000)
            elif endpoint and 'opus' in endpoint.lower():
                return (tokens_in * 15.0 / 1000000) + (tokens_out * 75.0 / 1000000)
            elif endpoint and 'sonnet' in endpoint.lower():
                return (tokens_in * 3.0 / 1000000) + (tokens_out * 15.0 / 1000000)
            elif endpoint and 'haiku' in endpoint.lower():
                return (tokens_in * 0.25 / 1000000) + (tokens_out * 1.25 / 1000000)
            else:
                # Default to Sonnet pricing if model not specified
                return (tokens_in * 3.0 / 1000000) + (tokens_out * 15.0 / 1000000)
                
        # Default minimal cost for unknown APIs
        else:
            return 0.0001 * (tokens_in + tokens_out)
    
    def get_daily_cost(self, api_name: str = None, company: str = None) -> float:
        """Get the total cost for the current day.
        
        Args:
            api_name: Optional filter by API name
            company: Optional filter by company name
            
        Returns:
            Total cost for today
        """
        # Calculate start of day timestamp
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
        start_time = int(start_of_day.timestamp())
        
        return self.get_cost_for_period(start_time, int(time.time()), api_name, company)
    
    def get_cost_for_period(self, 
                           start_time: int, 
                           end_time: int, 
                           api_name: str = None, 
                           company: str = None) -> float:
        """Get the total cost for a specific time period.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            api_name: Optional filter by API name
            company: Optional filter by company name
            
        Returns:
            Total cost for the specified period
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT SUM(cost) FROM api_costs WHERE timestamp >= ? AND timestamp <= ?'
        params = [start_time, end_time]
        
        if api_name:
            query += ' AND api_name = ?'
            params.append(api_name)
        
        if company:
            query += ' AND company = ?'
            params.append(company)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        return result[0] or 0.0
    
    def get_usage_stats(self, 
                       days: int = 30, 
                       api_name: str = None, 
                       company: str = None) -> Dict[str, Any]:
        """Get detailed usage statistics.
        
        Args:
            days: Number of days to look back
            api_name: Optional filter by API name
            company: Optional filter by company name
            
        Returns:
            Dictionary with usage statistics
        """
        # Calculate start timestamp
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        query = '''
        SELECT 
            api_name,
            endpoint,
            SUM(tokens_in) as total_tokens_in,
            SUM(tokens_out) as total_tokens_out,
            SUM(cost) as total_cost,
            COUNT(*) as call_count
        FROM api_costs
        WHERE timestamp >= ?
        '''
        
        params = [start_time]
        
        if api_name:
            query += ' AND api_name = ?'
            params.append(api_name)
        
        if company:
            query += ' AND company = ?'
            params.append(company)
        
        query += ' GROUP BY api_name, endpoint'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Format results
        stats = {
            'total_cost': 0.0,
            'total_tokens_in': 0,
            'total_tokens_out': 0,
            'total_calls': 0,
            'by_api': {},
            'period_days': days,
            'api_calls': 0  # For dashboard compatibility
        }
        
        for row in results:
            api = row[0]
            endpoint = row[1]
            tokens_in = row[2]
            tokens_out = row[3]
            cost = row[4]
            calls = row[5]
            
            # Update totals
            stats['total_cost'] += cost
            stats['total_tokens_in'] += tokens_in
            stats['total_tokens_out'] += tokens_out
            stats['total_calls'] += calls
            stats['api_calls'] += calls  # For dashboard compatibility
            
            # Add to API breakdown
            if api not in stats['by_api']:
                stats['by_api'][api] = {
                    'total_cost': 0.0,
                    'total_tokens_in': 0,
                    'total_tokens_out': 0,
                    'total_calls': 0,
                    'by_endpoint': {}
                }
            
            api_stats = stats['by_api'][api]
            api_stats['total_cost'] += cost
            api_stats['total_tokens_in'] += tokens_in
            api_stats['total_tokens_out'] += tokens_out
            api_stats['total_calls'] += calls
            
            # Add endpoint breakdown
            if endpoint:
                if endpoint not in api_stats['by_endpoint']:
                    api_stats['by_endpoint'][endpoint] = {
                        'cost': 0.0,
                        'tokens_in': 0,
                        'tokens_out': 0,
                        'calls': 0
                    }
                
                endpoint_stats = api_stats['by_endpoint'][endpoint]
                endpoint_stats['cost'] += cost
                endpoint_stats['tokens_in'] += tokens_in
                endpoint_stats['tokens_out'] += tokens_out
                endpoint_stats['calls'] += calls
        
        conn.close()
        return stats
        
    def get_daily_usage(self, days: int = 30, company: str = None) -> List[Dict[str, Any]]:
        """Get daily API usage breakdown.
        
        Args:
            days: Number of days to look back
            company: Optional filter by company name
            
        Returns:
            List of daily usage records
        """
        # Calculate start and end timestamps
        end_time = int(time.time())
        start_time = end_time - (days * 86400)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query for api_costs table (we'll use this as the primary source)
        query = '''
            SELECT 
                date(timestamp, 'unixepoch') as day, 
                api_name, 
                SUM(tokens_in) as tokens_in, 
                SUM(tokens_out) as tokens_out,
                SUM(cost) as daily_cost
            FROM api_costs 
            WHERE timestamp >= ? AND timestamp <= ?
        '''
        
        params = [start_time, end_time]
        
        if company:
            query += " AND company = ?"
            params.append(company)
            
        query += " GROUP BY day, api_name ORDER BY day DESC, api_name"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Format the results
        daily_data = []
        for row in results:
            day, api, tokens_in, tokens_out, cost = row
            daily_data.append({
                "date": day,
                "api": api,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost": cost
            })
            
        return daily_data
        
    def get_usage_by_function(self, days: int = 30, company: str = None) -> List[Dict[str, Any]]:
        """Get API usage breakdown by function/endpoint.
        
        Args:
            days: Number of days to look back
            company: Optional filter by company name
            
        Returns:
            List of function usage records
        """
        # Calculate start and end timestamps
        end_time = int(time.time())
        start_time = end_time - (days * 86400)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query for api_costs table
        query = '''
            SELECT 
                api_name,
                endpoint, 
                SUM(tokens_in) as tokens_in, 
                SUM(tokens_out) as tokens_out,
                SUM(cost) as total_cost,
                COUNT(*) as call_count
            FROM api_costs 
            WHERE timestamp >= ? AND timestamp <= ?
        '''
        
        params = [start_time, end_time]
        
        if company:
            query += " AND company = ?"
            params.append(company)
            
        query += " GROUP BY api_name, endpoint ORDER BY total_cost DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Format the results
        function_data = []
        for row in results:
            api, endpoint, tokens_in, tokens_out, cost, calls = row
            function_data.append({
                "api": api,
                "function": endpoint or "default",
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost": cost,
                "calls": calls
            })
            
        return function_data 