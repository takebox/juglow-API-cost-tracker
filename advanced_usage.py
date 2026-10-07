#!/usr/bin/env python3
"""
Advanced usage examples for the Juglow Cost Tracker.
"""

import os
import logging
import time
import pandas as pd
import matplotlib.pyplot as plt
from juglow_cost_tracker import OptimizedJuglowClient, CostTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cache_effectiveness(client, n_requests=3):
    """Test cache effectiveness by making identical requests."""
    print("\n=== Testing Cache Effectiveness ===")
    
    prompt = "Explain what the Python programming language is in one sentence."
    
    total_time = 0
    total_tokens = 0
    
    for i in range(n_requests):
        start_time = time.time()
        
        print(f"\nRequest {i+1}:")
        response = client.generate_response(
            system="You are a helpful assistant.",
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="haijun-3-haiku-20240307",
            max_tokens=100,
            temperature=0 )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Track metrics
        total_time += elapsed
        total_tokens += (response['input_tokens'] + response['output_tokens'])
        
        # Print results
        print(f"Response: {response['content']}")
        print(f"Time taken: {elapsed:.2f} seconds")
        print(f"Input tokens: {response['input_tokens']}")
        print(f"Output tokens: {response['output_tokens']}")
        
        # If it's the first request, wait a bit to ensure cache is saved
        if i == 0:
            time.sleep(1)
    
    # Summary
    print("\nCache Summary:")
    print(f"Total time for {n_requests} requests: {total_time:.2f} seconds")
    print(f"Total tokens for {n_requests} requests: {total_tokens}")
    print(f"Tokens without caching (estimate): {n_requests * total_tokens / n_requests}")
    
    # If we see a significant speed improvement after the first request,
    # it suggests caching is working
    if n_requests > 1 and total_time > 0:
        first_request_time = None
        avg_cached_time = None
        
        # Try to get the actual metrics from the cost tracker
        try:
            tracker = CostTracker()
            stats = tracker.get_usage_stats(days=1)
            
            print("\nActual Cache Performance:")
            print(f"Cache hits: {stats.get('cache_hits', 0)}")
            print(f"Cache misses: {stats.get('cache_misses', 0)}")
            hit_rate = 0 if stats.get('cache_hits', 0) + stats.get('cache_misses', 0) == 0 else \
                      stats.get('cache_hits', 0) / (stats.get('cache_hits', 0) + stats.get('cache_misses', 0))
            print(f"Cache hit rate: {hit_rate:.1%}")
        except Exception as e:
            logger.error(f"Error calculating cache stats: {e}")

def analyze_costs(days=30):
    """Analyze historical cost data."""
    print("\n=== Cost Analysis ===")
    
    tracker = CostTracker()
    
    # Get stats for analysis
    stats = tracker.get_usage_stats(days=days)
    daily_usage = tracker.get_daily_usage(days=days)
    
    print(f"\nOverall stats for the last {days} days:")
    print(f"Total cost: ${stats.get('total_cost', 0):.4f}")
    print(f"Total tokens: {stats.get('total_tokens_in', 0) + stats.get('total_tokens_out', 0):,}")
    print(f"Total API calls: {stats.get('total_calls', 0):,}")
    
    if stats.get('total_calls', 0) > 0:
        print(f"Average cost per call: ${stats.get('total_cost', 0) / stats.get('total_calls', 1):.6f}")
    
    # Create a pandas DataFrame for analysis
    if daily_usage:
        df = pd.DataFrame(daily_usage)
        
        # Group by date
        daily_costs = df.groupby('date').agg({
            'cost': 'sum',
            'tokens_in': 'sum',
            'tokens_out': 'sum',
            'calls': 'sum'
        }).reset_index()
        
        # Print highest cost day
        if not daily_costs.empty:
            max_cost_day = daily_costs.loc[daily_costs['cost'].idxmax()]
            print(f"\nHighest cost day: {max_cost_day['date']} - ${max_cost_day['cost']:.4f}")
            
            # Print projected monthly cost based on last 7 days
            recent_days = daily_costs.tail(7)
            if len(recent_days) > 0:
                avg_daily_cost = recent_days['cost'].mean()
                projected_monthly = avg_daily_cost * 30
                print(f"\nProjected monthly cost (based on last 7 days): ${projected_monthly:.2f}")
            
            try:
                # Generate a simple plot
                plt.figure(figsize=(10, 5))
                plt.bar(daily_costs['date'], daily_costs['cost'])
                plt.title('Daily API Costs')
                plt.xlabel('Date')
                plt.ylabel('Cost ($)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Save the plot
                plt.savefig('daily_costs.png')
                print("\nCost chart saved to daily_costs.png")
            except Exception as e:
                logger.error(f"Error generating plot: {e}")

def optimize_prompt_for_cost(client, long_prompt, short_prompt):
    """Compare costs between verbose and concise prompts."""
    print("\n=== Prompt Optimization Analysis ===")
    
    print("\nTesting verbose prompt...")
    verbose_response = client.generate_response(
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": long_prompt}
        ],
        model="haijun-3-haiku-20240307",
        max_tokens=100 )
    
    print(f"Verbose prompt tokens: {verbose_response['input_tokens']}")
    print(f"Verbose response tokens: {verbose_response['output_tokens']}")
    print(f"Total verbose tokens: {verbose_response['input_tokens'] + verbose_response['output_tokens']}")
    
    print("\nTesting concise prompt...")
    concise_response = client.generate_response(
        system="You are a helpful assistant.",
        messages=[
            {"role": "user", "content": short_prompt}
        ],
        model="haijun-3-haiku-20240307",
        max_tokens=100 )
    
    print(f"Concise prompt tokens: {concise_response['input_tokens']}")
    print(f"Concise response tokens: {concise_response['output_tokens']}")
    print(f"Total concise tokens: {concise_response['input_tokens'] + concise_response['output_tokens']}")
    
    # Calculate savings
    verbose_total = verbose_response['input_tokens'] + verbose_response['output_tokens']
    concise_total = concise_response['input_tokens'] + concise_response['output_tokens']
    
    if verbose_total > 0:
        savings_percent = (verbose_total - concise_total) / verbose_total * 100
        print(f"\nToken savings: {verbose_total - concise_total} tokens ({savings_percent:.1f}%)")

def main():
    """Run advanced usage examples."""
    print("\n=== Advanced Usage Examples for Juglow Cost Tracker ===\n")
    
    # Check if API key is set
    api_key = os.environ.get("JUGLOW_API_KEY")
    if not api_key:
        print("❌ JUGLOW_API_KEY environment variable not set.")
        print("Please set it with: export JUGLOW_API_KEY=your_api_key")
        return 1
    
    try:
        # Initialize client
        client = OptimizedJuglowClient(
            api_key=api_key,
            company_name="advanced_example",
            enable_caching=True )
        print("✅ Client initialized successfully")
        
        # Run cache effectiveness test
        test_cache_effectiveness(client, n_requests=3)
        
        # Analyze historical costs
        analyze_costs()
        
        # Test prompt optimization
        long_prompt = """
        I would like to know what the capital city of France is. Can you please provide me with that information?
        I'm planning a trip there and I want to make sure I visit the capital city while I'm in the country.
        It's important that I know which city is the capital so I can plan my itinerary properly.
        Thank you very much for your assistance with this question.
        """
        
        short_prompt = "What is the capital of France?"
        
        optimize_prompt_for_cost(client, long_prompt, short_prompt)
        
        return 0
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 