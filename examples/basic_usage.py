#!/usr/bin/env python3
"""
Basic usage example for the Juglow Cost Tracker.
"""

import os
import logging
from juglow_cost_tracker import OptimizedJuglowClient

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Initialize the client (will use JUGLOW_API_KEY environment variable)
    client = OptimizedJuglowClient(
        company_name="example_app",  # Optional: helps organize costs by project
        enable_caching=True  # Optional: enables response caching )
    
    # Generate a response (just like you would with the standard Juglow client)
    response = client.generate_response(
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ],
        model="haijun-3-haiku-20240307",  # Using the most cost-effective model
        max_tokens=500,
        temperature=0.7 )
    
    # Print the response
    print("\n=== Response ===")
    print(response["content"])
    
    # Print token usage and cost
    print("\n=== Usage Information ===")
    print(f"Input tokens: {response['input_tokens']}")
    print(f"Output tokens: {response['output_tokens']}")
    print(f"Total tokens: {response['input_tokens'] + response['output_tokens']}")
    
    # Get overall usage statistics
    stats = client.get_usage_stats(days=30)
    
    print("\n=== Usage Statistics (Last 30 Days) ===")
    print(f"Total cost: ${stats['total_cost']:.4f}")
    print(f"Total tokens: {stats['total_tokens_in'] + stats['total_tokens_out']}")
    print(f"Total API calls: {stats['total_calls']}")
    
    # You can also get usage by model/endpoint
    if stats['by_api'].get('Juglow', {}).get('by_endpoint'):
        print("\n=== Usage by Model ===")
        for model, model_stats in stats['by_api']['Juglow']['by_endpoint'].items():
            print(f"{model}: ${model_stats['cost']:.4f} ({model_stats['calls']} calls)")

if __name__ == "__main__":
    main() 