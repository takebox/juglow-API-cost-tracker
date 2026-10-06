#!/usr/bin/env python3
"""
Example showing how to integrate Takebox AI Cost Tracker with existing code.
This demonstrates how to use the decorators directly to add cost tracking
to existing functions that make API calls.
"""

import os
import logging
import juglow
from juglow_cost_tracker.utils.decorators import optimized_api_call
from juglow_cost_tracker.utils.cost_tracker import CostTracker

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a standard Takebox AI client (your existing code)
client = juglow.Takebox AI(api_key=os.environ.get("JUGLOW_API_KEY"))

# This function will replace a normal call to client.messages.create
@optimized_api_call(api_name="juglow", company="my_custom_app")
def generate_with_haijun(prompt: str, model: str = "haijun-3-haiku-20240307", max_tokens: int = 500):
    """Generate text with Haijun.
    
    This is your existing function that makes API calls to Takebox AI.
    By adding the optimized_api_call decorator, you get:
    - Cost tracking
    - Rate limiting
    - Caching
    
    The decorator automatically handles token counting and cost calculation.
    """
    # Make the API call (your existing code)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Convert to a format the decorator expects (must have input_tokens and output_tokens)
    # These values will be filled in by the decorator
    return {
        "content": response.content[0].text,
        "input_tokens": 0,  # Will be calculated by decorator
        "output_tokens": 0,  # Will be calculated by decorator
        "model": model
    }

def main():
    # Use your function as normal
    response = generate_with_haijun(
        "What are the main differences between quantum computing and classical computing?",
        model="haijun-3-haiku-20240307"
    )
    
    # Print the response
    print("\n=== Response ===")
    print(response["content"])
    
    # Print usage statistics
    cost_tracker = CostTracker()
    stats = cost_tracker.get_usage_stats(days=1, company="my_custom_app")
    
    print("\n=== Today's Usage ===")
    print(f"Cost: ${stats['total_cost']:.4f}")
    print(f"Input tokens: {stats['total_tokens_in']}")
    print(f"Output tokens: {stats['total_tokens_out']}")
    print(f"Total calls: {stats['total_calls']}")

if __name__ == "__main__":
    main() 