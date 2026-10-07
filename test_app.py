#!/usr/bin/env python3
"""
Test script for the Juglow Cost Tracker package.
This script will test the basic functionality of the package.
"""

import os
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required packages are available."""
    missing_packages = []
    packages = ["juglow", "flask"]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ Package {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ Package {package} is missing")
    
    # Test flask-cors specifically
    try:
        from flask_cors import CORS
        print("✅ Package flask-cors is available")
    except ImportError:
        missing_packages.append("flask-cors")
        print("❌ Package flask-cors is missing")
    
    # Test other packages
    other_packages = ["requests", "pandas"]
    for package in other_packages:
        try:
            __import__(package)
            print(f"✅ Package {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ Package {package} is missing")
    
    # Test tiktoken specifically
    try:
        import tiktoken
        print("✅ Package tiktoken is available")
    except ImportError:
        missing_packages.append("tiktoken")
        print(f"❌ Package tiktoken is missing - you'll need to install it separately")
    
    return len(missing_packages) == 0

def test_dashboard():
    """Test if dashboard components are available."""
    missing_packages = []
    packages = ["dash", "dash_bootstrap_components", "plotly"]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ Dashboard dependency {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ Dashboard dependency {package} is missing")
    
    return len(missing_packages) == 0

def test_module_structure():
    """Test the module structure."""
    try:
        import juglow_cost_tracker
        print("✅ Module juglow_cost_tracker is importable")
        
        # Check for expected directories
        expected_dirs = ["client", "utils", "dashboard", "db", "api"]
        module_path = os.path.dirname(juglow_cost_tracker.__file__)
        
        for dir_name in expected_dirs:
            if os.path.isdir(os.path.join(module_path, dir_name)):
                print(f"✅ Directory {dir_name} exists")
            else:
                print(f"❌ Directory {dir_name} is missing")
                
        return True
    except ImportError:
        print("❌ Module juglow_cost_tracker cannot be imported")
        return False

def main():
    print("\n=== Testing Juglow Cost Tracker ===\n")

    # Run tests
    print("\n--- Testing Required Packages ---")
    packages_ok = test_imports()
    
    print("\n--- Testing Dashboard Components ---")
    dashboard_ok = test_dashboard()
    
    print("\n--- Testing Module Structure ---")
    structure_ok = test_module_structure()

    print("\n=== Test Summary ===")
    if packages_ok and dashboard_ok and structure_ok:
        print("✅ All tests passed! The installation appears to be working correctly.")
    else:
        print("❌ Some tests failed. Please check the output above for details.")
    
    print("\nTo run the application with an actual API key, set the JUGLOW_API_KEY environment variable.")
    print("Then initialize the client with: client = OptimizedJuglowClient(company_name='my_app')")

if __name__ == "__main__":
    main() 