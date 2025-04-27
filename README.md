# Anthropic Cost Tracker

> *"This toolkit has saved my startup thousands of dollars in AI costs and given me complete visibility into our Claude usage. I can't imagine running our AI features without it now."*

## The Problem This Solves

As founders, we're all excited about integrating Claude and other AI models into our products. But there's a hidden challenge: **unpredictable costs that can quickly spiral out of control**. 

I built this standalone toolkit because I needed to:
- Know exactly how much we were spending on AI in real-time
- Find opportunities to reduce costs without sacrificing quality
- Prevent unexpected charges that could hurt our runway
- Have data I could confidently show to investors

## Key Features

- **Drop-in replacement** for the standard Anthropic client (one line change!)
- **Cost tracking** with detailed breakdowns by model, feature, and day
- **Beautiful dashboard** anyone on your team can understand
- **Smart optimizations** that reduce your API costs by 20-30%
- **Complete budget control** with alerts before costs get too high
- **Zero external dependencies** - everything works locally with no new infrastructure

## Quick Install

```bash
pip install anthropic-cost-tracker
```

That's it! No complex setup, no infrastructure changes, nothing else to configure.

## Getting Started in 30 Seconds

Replace your standard Anthropic client with our optimized version:

```python
# Before:
# from anthropic import Anthropic
# client = Anthropic(api_key="your-api-key")

# After - just two lines changed:
from anthropic_cost_tracker import OptimizedAnthropicClient
client = OptimizedAnthropicClient(api_key="your-api-key", company_name="my-startup")

# Everything else stays exactly the same!
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Write a blog post about AI for startups"}
    ]
)

print(response.content[0].text)
```

That's it! You're now tracking all your Claude API costs automatically.

## See Your Costs in Action

Launch the dashboard with a single command:

```bash
anthropic-dashboard
```

Visit http://localhost:8050 to see:
- Total spending by day, model, and feature
- Cost trends to spot issues before they become problems
- Optimization opportunities to reduce your bills
- Projected monthly spending based on current usage

## Real Startup Benefits

- **Financial Control**: Always know exactly what you're spending on AI
- **Investor Confidence**: Show detailed cost metrics in your pitch deck
- **Performance Insights**: Understand which models give you the best ROI
- **Runway Protection**: Avoid the surprise of an unexpectedly large API bill

## Integration Options

This toolkit works with:
- Any Python application or service
- Web apps, command-line tools, or backends
- Multiple models and AI providers
- Existing codebases (no rewrite needed)

## Documentation

For complete documentation, visit [our documentation site](https://anthropic-cost-tracker.readthedocs.io/).

## Testing and Development

This repository includes several tools to help you test and debug the application:

- `test_app.py` - Basic test for verifying dependencies and installation
- `example_debug.py` - Test the client with a real API key
- `advanced_usage.py` - Advanced examples showing caching and cost optimization
- `run_dashboard.py` - Script for running the dashboard locally

For more information, see [TESTING.md](TESTING.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built by founders, for founders - because every dollar of runway matters.* 