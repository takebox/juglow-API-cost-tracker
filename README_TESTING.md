# Anthropic Cost Tracker - Testing and Debugging

This repository contains tools to test, run, and debug the Anthropic Cost Tracker package.

## Available Tools

| File | Description |
|------|-------------|
| `test_app.py` | Basic functionality test to verify package installation and dependencies |
| `example_debug.py` | Simple example that tests the API client with your Anthropic API key |
| `advanced_usage.py` | Advanced usage examples showing caching, cost analysis, and optimization techniques |
| `run_dashboard.py` | Script to run the dashboard interface |
| `TESTING.md` | Comprehensive testing guide with instructions for all testing scenarios |
| `venv/` | Virtual environment with all dependencies installed |

## Quick Start

For a complete testing guide, see [TESTING.md](TESTING.md).

### Basic Testing (No API Key Required)

```bash
# Activate the virtual environment
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows

# Run the basic test script
python test_app.py
```

### Testing with API Key

```bash
# Set your API key
export ANTHROPIC_API_KEY=your_api_key  # On Linux/macOS
set ANTHROPIC_API_KEY=your_api_key     # On Windows CMD
$env:ANTHROPIC_API_KEY="your_api_key"  # On Windows PowerShell

# Run the debug test
python example_debug.py

# Run advanced usage examples
python advanced_usage.py
```

### Running the Dashboard

```bash
# Start the dashboard (runs in background)
python run_dashboard.py

# Access dashboard at http://localhost:8050
```

## Troubleshooting

If you encounter any issues, please refer to [TESTING.md](TESTING.md) for detailed troubleshooting steps.

Common solutions:

1. Reinstall dependencies: `pip install -e ".[dashboard,dev]"`
2. Check your API key: Make sure it's valid and properly exported
3. Reset the database: `rm -f anthropic_cost_tracker/db/cost_tracker.db`
4. Check for port conflicts with the dashboard 