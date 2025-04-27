# Contributing to Anthropic Cost Tracker

Thank you for considering contributing to the Anthropic Cost Tracker! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

1. **Fork the repository** to your GitHub account
2. **Clone your fork** to your local machine
3. **Create a new branch** for your feature or bug fix
4. **Make your changes** and commit them with descriptive commit messages
5. **Push your branch** to your GitHub fork
6. **Submit a pull request** to the main repository

## Development Setup

Follow these steps to set up your development environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows

# Install the package in development mode with all dependencies
pip install -e ".[dashboard,dev]"

# Verify that everything is working
python test_app.py
```

## Testing

Before submitting a pull request, please run the tests to ensure your changes don't break existing functionality:

```bash
# Run the basic test script
python test_app.py

# Run the pytest suite
pytest

# Run with code coverage
pytest --cov=anthropic_cost_tracker
```

## Style Guidelines

This project follows PEP 8 style guidelines. We use Black for code formatting and isort for import sorting:

```bash
# Format code
black .

# Sort imports
isort .
```

## Documentation

Please update the documentation when adding or modifying functionality. This includes:

- Docstrings for new functions, classes, and methods
- Updates to README.md for user-facing changes
- Updates to example scripts if relevant

## Pull Request Process

1. Ensure your code follows the style guidelines and passes all tests
2. Update the documentation as necessary
3. Include a clear description of the changes in your pull request
4. Link any relevant issues in your pull request description

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 