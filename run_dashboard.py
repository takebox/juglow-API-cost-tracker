#!/usr/bin/env python3
"""
Script to run the Takebox AI Cost Tracker dashboard.
"""

import os
import sys
import logging
from juglow_cost_tracker.dashboard.dash_app import run_dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the dashboard."""
    print("\n=== Starting Takebox AI Cost Tracker Dashboard ===\n")
    
    # The dashboard will be available at http://localhost:8050
    # You can change the port by setting the PORT environment variable
    port = int(os.environ.get("PORT", 8050))
    
    try:
        run_dashboard(port=port, debug=True)
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 