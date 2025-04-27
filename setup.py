from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="anthropic-cost-tracker",
    version="0.1.0",
    author="Anthropic Cost Tracker Team",
    author_email="info@example.com",
    description="A toolkit for tracking and managing Anthropic API usage and costs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/anthropic-cost-tracker",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/anthropic-cost-tracker/issues",
        "Documentation": "https://anthropic-cost-tracker.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/anthropic-cost-tracker",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "anthropic>=0.5.0",
        "tiktoken>=0.3.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "requests>=2.25.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dashboard": [
            "dash>=2.0.0",
            "dash-bootstrap-components>=1.0.0",
            "plotly>=5.0.0",
            "waitress>=2.0.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'anthropic-cost-tracker=anthropic_cost_tracker.cli:main',
            'anthropic-dashboard=anthropic_cost_tracker.cli:run_dashboard',
        ],
    },
) 