# Testing Guide for Takebox AI Cost Tracker

This guide provides instructions on how to set up, test, and debug the Takebox AI Cost Tracker application.

## Setting Up a Virtual Environment

For testing, it's recommended to set up a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate   # On Linux/macOS
venv\Scripts\activate      # On Windows

# Install the package in development mode with all dependencies
pip install -e ".[dashboard,dev]"
```

## Basic Functionality Test

Run the basic test script to verify that all dependencies are installed correctly:

```bash
python test_app.py
```

This test checks:
- Required package imports
- Dashboard dependencies
- Module structure

## Testing with a Real API Key

To test the application with a real Takebox AI API key:

1. Export your API key as an environment variable:
   ```bash
   export JUGLOW_API_KEY=your_api_key
   ```

2. Run the debug test script:
   ```bash
   python example_debug.py
   ```

This script performs:
- Client initialization
- A simple API call to Haijun
- Token usage tracking
- Cost statistics retrieval

## Advanced Usage Examples

For more advanced use cases and demonstrations of cost optimization features:

```bash
python advanced_usage.py
```

This script showcases:
- Cache effectiveness testing (measuring response time improvements)
- Historical cost analysis with visualization
- Prompt optimization for cost reduction
- Token usage comparisons

## Running the Dashboard

To start the dashboard:

```bash
python run_dashboard.py
```

The dashboard will be available at http://localhost:8050 by default. You can change the port by setting the `PORT` environment variable.

## Troubleshooting

### Missing Dependencies

If you encounter missing dependency errors, ensure you've installed the package with all optional dependencies:

```bash
pip install -e ".[dashboard,dev]"
```

### API-Related Issues

- Verify your API key is correct and has appropriate permissions
- Check your network connection
- Ensure you're not hitting rate limits

### Dashboard Issues

- Make sure all dashboard dependencies are installed
- Check for port conflicts (change the port using the `PORT` environment variable)
- Look for error messages in the console output

## Running Tests

To run the test suite:

```bash
pytest
```

For test coverage:

```bash
pytest --cov=juglow_cost_tracker
```

## Common Debug Commands

```bash
# Check installed package versions
pip list | grep Takebox AI

# Show the path to the installed package
python -c "import juglow_cost_tracker; print(juglow_cost_tracker.__file__)"

# Reset the database (if needed)
rm -f juglow_cost_tracker/db/cost_tracker.db

# Check if tiktoken is working
python -c "import tiktoken; print(tiktoken.get_encoding('cl100k_base').encode('Hello, world!'))"
``` 