"""
Command-line interface for Anthropic Cost Tracker.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any
from datetime import datetime

from .utils.cost_tracker import CostTracker
from .client import OptimizedAnthropicClient
from .api import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def format_currency(value: float) -> str:
    """Format a value as USD currency."""
    return f"${value:.6f}"

def format_date(timestamp: int) -> str:
    """Format a timestamp as a date string."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def show_stats(cost_tracker: CostTracker, days: int, api_name: str = None, company: str = None):
    """Display usage statistics."""
    stats = cost_tracker.get_usage_stats(days=days, api_name=api_name, company=company)
    
    print("\n=== Anthropic API Usage Statistics ===")
    print(f"Period: Last {days} days")
    if api_name:
        print(f"API: {api_name}")
    if company:
        print(f"Company/Project: {company}")
    print("=" * 40)
    
    print(f"Total Cost: {format_currency(stats['total_cost'])}")
    print(f"Total Tokens: {stats['total_tokens_in'] + stats['total_tokens_out']:,}")
    print(f"  - Input Tokens: {stats['total_tokens_in']:,}")
    print(f"  - Output Tokens: {stats['total_tokens_out']:,}")
    print(f"Total API Calls: {stats['total_calls']:,}")
    
    if stats['by_api']:
        print("\n-- Breakdown by API --")
        for api, api_stats in stats['by_api'].items():
            print(f"\n{api}:")
            print(f"  Cost: {format_currency(api_stats['total_cost'])}")
            print(f"  Tokens: {api_stats['total_tokens_in'] + api_stats['total_tokens_out']:,}")
            print(f"  Calls: {api_stats['total_calls']:,}")
            
            if api_stats['by_endpoint']:
                print("\n  By Model/Endpoint:")
                for endpoint, ep_stats in api_stats['by_endpoint'].items():
                    print(f"    {endpoint}:")
                    print(f"      Cost: {format_currency(ep_stats['cost'])}")
                    print(f"      Tokens: {ep_stats['tokens_in'] + ep_stats['tokens_out']:,}")
                    print(f"      Calls: {ep_stats['calls']:,}")

def show_daily_usage(cost_tracker: CostTracker, days: int, company: str = None):
    """Display daily usage breakdown."""
    daily_data = cost_tracker.get_daily_usage(days=days, company=company)
    
    if not daily_data:
        print("No usage data found for the specified period.")
        return
    
    print("\n=== Daily Usage Breakdown ===")
    print(f"Period: Last {days} days")
    if company:
        print(f"Company/Project: {company}")
    print("=" * 30)
    
    # Group by date
    by_date = {}
    for entry in daily_data:
        date = entry['date']
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(entry)
    
    # Print in reverse chronological order
    for date in sorted(by_date.keys(), reverse=True):
        entries = by_date[date]
        total_cost = sum(entry['cost'] for entry in entries)
        
        print(f"\n{date} - Total: {format_currency(total_cost)}")
        for entry in sorted(entries, key=lambda e: e['api']):
            print(f"  {entry['api']}: {format_currency(entry['cost'])} "
                  f"({entry['tokens_in'] + entry['tokens_out']:,} tokens)")

def test_api(api_key: str = None):
    """Test the API connection and cost tracking."""
    try:
        client = OptimizedAnthropicClient(
            api_key=api_key,
            company_name="cli_test",
            enable_caching=False  # Disable caching for test
        )
        
        print("Testing API connection...")
        result = client.test_api_integration()
        
        if result['status'] == 'success':
            print("\n✅ API test successful!")
            print(f"Response: {result['response']}")
            print(f"Input tokens: {result['input_tokens']}")
            print(f"Output tokens: {result['output_tokens']}")
            print(f"Model: {result['model']}")
            
            # Verify cost tracking
            stats = client.get_usage_stats(days=1)
            if stats['total_calls'] > 0:
                print("\n✅ Cost tracking successful!")
                print(f"Cost logged: {format_currency(stats['total_cost'])}")
                print(f"Tokens logged: {stats['total_tokens_in'] + stats['total_tokens_out']:,}")
            else:
                print("\n❌ Cost tracking verification failed - no records found")
        else:
            print(f"\n❌ API test failed: {result.get('error_message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error during API test: {str(e)}")
        
def run_api_server(host: str = '127.0.0.1', port: int = 5000):
    """Run the RESTful API server."""
    try:
        from waitress import serve
        
        app = create_app()
        print(f"Starting Anthropic Cost Tracker API server on http://{host}:{port}")
        print("Press Ctrl+C to stop")
        
        serve(app, host=host, port=port)
    except ImportError:
        print("Error: waitress package is required to run the API server.")
        print("Install with: pip install waitress")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting API server: {str(e)}")
        sys.exit(1)

def run_dashboard(host: str = '127.0.0.1', port: int = 8050):
    """Run the interactive dashboard."""
    try:
        # Try to import the Dash dashboard
        try:
            from .dashboard import create_dashboard
            
            print(f"Starting Anthropic Cost Tracker dashboard on http://{host}:{port}")
            print("Press Ctrl+C to stop")
            
            app = create_dashboard()
            app.run_server(host=host, port=port, debug=False)
            
        except ImportError:
            print("Error: Dash dashboard components are not installed.")
            print("Install with: pip install \"anthropic-cost-tracker[dashboard]\"")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error starting dashboard: {str(e)}")
        sys.exit(1)

def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Anthropic Cost Tracker CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show usage statistics')
    stats_parser.add_argument('--days', type=int, default=30, help='Number of days to look back')
    stats_parser.add_argument('--api', help='Filter by API name')
    stats_parser.add_argument('--company', help='Filter by company/project name')
    
    # Daily command
    daily_parser = subparsers.add_parser('daily', help='Show daily usage breakdown')
    daily_parser.add_argument('--days', type=int, default=30, help='Number of days to look back')
    daily_parser.add_argument('--company', help='Filter by company/project name')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test API connection and cost tracking')
    test_parser.add_argument('--api-key', help='Anthropic API key (or use ANTHROPIC_API_KEY env var)')
    
    # API server command
    api_parser = subparsers.add_parser('api', help='Run the RESTful API server')
    api_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    api_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Run the interactive dashboard')
    dashboard_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=8050, help='Port to bind to')
    
    # Parse args
    args = parser.parse_args()
    
    # Create cost tracker
    cost_tracker = CostTracker()
    
    # Execute command
    if args.command == 'stats':
        show_stats(cost_tracker, args.days, args.api, args.company)
    elif args.command == 'daily':
        show_daily_usage(cost_tracker, args.days, args.company)
    elif args.command == 'test':
        test_api(args.api_key)
    elif args.command == 'api':
        run_api_server(args.host, args.port)
    elif args.command == 'dashboard':
        run_dashboard(args.host, args.port)
    else:
        parser.print_help()
        
if __name__ == '__main__':
    main() 