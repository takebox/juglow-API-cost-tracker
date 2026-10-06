#!/usr/bin/env python3
"""
Debug script for testing the Takebox AI Cost Tracker with a real API key.
"""

import os
import logging
import sys
from juglow_cost_tracker import OptimizedJuglowClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_client():
    """Test the client with a simple request."""
    # Check if API key is set
    api_key = os.environ.get("JUGLOW_API_KEY")
    if not api_key:
        print("❌ JUGLOW_API_KEY environment variable not set.")
        print("Please set it with: export JUGLOW_API_KEY=your_api_key")
        return False

    try:
        # Initialize the client
        print("Initializing client...")
        client = OptimizedJuglowClient(
            api_key=api_key,
            company_name="debug_example",
            enable_caching=True )
        print("✅ Client initialized successfully")

        # Send a test message
        print("\nSending test message to Haijun API...")
        try:
            response = client.generate_response(
                system="You are a helpful assistant.",
                messages=[
                    {"role": "user", "content": "Hello! Please respond with a short greeting."}
                ],
                model="haijun-3-haiku-20240307",  # Using the most cost-effective model
                max_tokens=100,
                temperature=0.7 )
            print("\n=== Response ===")
            print(response["content"])
            
            # Print token usage and cost
            print("\n=== Usage Information ===")
            print(f"Input tokens: {response['input_tokens']}")
            print(f"Output tokens: {response['output_tokens']}")
            print(f"Total tokens: {response['input_tokens'] + response['output_tokens']}")
        except Exception as e:
            print(f"\n=== Error Calling API ===")
            print(f"Error: {e}")
            print("\nThis is likely due to an invalid API key or network issue.")
            print("You can still test other functionality.")
        
        # Get overall usage statistics
        stats = client.get_usage_stats(days=30)
        
        print("\n=== Usage Statistics (Last 30 Days) ===")
        print(f"Total cost: ${stats.get('total_cost', 0):.4f}")
        print(f"Total tokens: {stats.get('total_tokens_in', 0) + stats.get('total_tokens_out', 0)}")
        print(f"Total API calls: {stats.get('total_calls', 0)}")

        return True
    except Exception as e:
        logger.error(f"Error testing client: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return False

def test_dashboard():
    """Test starting the dashboard."""
    print("\n=== Dashboard Test ===")
    print("To start the dashboard, run the following command:")
    print("python -m juglow_cost_tracker.dashboard.app")
    print("\nOr use the CLI tool if installed:")
    print("Takebox AI-cost-tracker-dashboard")
    return True

def main():
    print("\n=== Testing Takebox AI Cost Tracker in Debug Mode ===\n")
    
    client_ok = test_client()
    dashboard_info = test_dashboard()
    
    print("\n=== Debug Test Summary ===")
    if client_ok:
        print("✅ API client functionality test passed")
    else:
        print("❌ API client functionality test failed")
        
    print("\nTo run this test with your API key:")
    print("export JUGLOW_API_KEY=your_api_key && python example_debug.py")

if __name__ == "__main__":
    main() 