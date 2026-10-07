from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Juglow-cost-tracker",
    version="0.1.0",
    author="Juglow Cost Tracker Team",
    author_email="info@example.com",
    description="A toolkit for tracking and managing Juglow API usage and costs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        "Bug Tracker": "",
        "Documentation": "",
        "Source Code": "",
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
        "juglow>=0.5.0",
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
            'Juglow-cost-tracker=juglow_cost_tracker.cli:main',
            'Juglow-dashboard=juglow_cost_tracker.cli:run_dashboard',
        ],
    },
) 