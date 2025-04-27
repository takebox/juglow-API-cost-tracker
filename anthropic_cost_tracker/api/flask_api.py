"""
Flask API for the Anthropic Cost Tracker.
"""

import os
import json
import logging
from typing import Dict, Any, List

from flask import Flask, jsonify, request
from flask_cors import CORS

from ..utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create and configure the Flask application.
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    CORS(app)
    
    # Initialize the cost tracker
    cost_tracker = CostTracker()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy"})
    
    @app.route('/api/usage/stats', methods=['GET'])
    def get_api_usage_stats():
        """Get API usage statistics for the specified period."""
        days = request.args.get('days', 30, type=int)
        company = request.args.get('company', None)
        api_name = request.args.get('api_name', None)
        
        try:
            stats = cost_tracker.get_usage_stats(days=days, api_name=api_name, company=company)
            
            return jsonify({
                "success": True,
                "data": stats
            })
        except Exception as e:
            logger.error(f"Error fetching API usage stats: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error fetching API usage stats: {str(e)}"
            }), 500
    
    @app.route('/api/usage/daily', methods=['GET'])
    def get_daily_usage():
        """Get daily API usage breakdown."""
        days = request.args.get('days', 30, type=int)
        company = request.args.get('company', None)
        
        try:
            daily_data = cost_tracker.get_daily_usage(days=days, company=company)
            
            return jsonify({
                "success": True,
                "data": daily_data
            })
        except Exception as e:
            logger.error(f"Error fetching daily API usage: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error fetching daily API usage: {str(e)}"
            }), 500
    
    @app.route('/api/usage/by-function', methods=['GET'])
    def get_usage_by_function():
        """Get API usage breakdown by function/endpoint."""
        days = request.args.get('days', 30, type=int)
        company = request.args.get('company', None)
        
        try:
            function_data = cost_tracker.get_usage_by_function(days=days, company=company)
            
            return jsonify({
                "success": True,
                "data": function_data
            })
        except Exception as e:
            logger.error(f"Error fetching function API usage: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error fetching function API usage: {str(e)}"
            }), 500
    
    @app.route('/api/usage/budget', methods=['GET', 'POST'])
    def manage_api_budget():
        """Get or update API budget settings."""
        # Get the config file path
        config_dir = os.path.join(os.path.expanduser('~'), '.anthropic-cost-tracker')
        os.makedirs(config_dir, exist_ok=True)
        budget_file = os.path.join(config_dir, 'budget_settings.json')
        
        if request.method == 'GET':
            # Get current budget settings
            try:
                if os.path.exists(budget_file):
                    with open(budget_file, 'r') as f:
                        budget_data = json.load(f)
                else:
                    # Default budget settings
                    budget_data = {
                        "daily_limit": 10.0,
                        "monthly_limit": 100.0,
                        "warning_threshold": 0.8,  # 80% of limit
                        "notify_on_threshold": True,
                        "auto_throttle": True
                    }
                
                return jsonify({
                    "success": True,
                    "data": budget_data
                })
            except Exception as e:
                logger.error(f"Error fetching budget settings: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"Error fetching budget settings: {str(e)}"
                }), 500
        else:  # POST
            # Update budget settings
            try:
                budget_data = request.json
                
                # Validate required fields
                required_fields = ["daily_limit", "monthly_limit", "warning_threshold"]
                for field in required_fields:
                    if field not in budget_data:
                        return jsonify({
                            "success": False,
                            "message": f"Missing required field: {field}"
                        }), 400
                
                # Save to file
                with open(budget_file, 'w') as f:
                    json.dump(budget_data, f, indent=2)
                
                return jsonify({
                    "success": True,
                    "message": "Budget settings updated successfully",
                    "data": budget_data
                })
            except Exception as e:
                logger.error(f"Error updating budget settings: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"Error updating budget settings: {str(e)}"
                }), 500
    
    @app.route('/api/companies', methods=['GET'])
    def get_companies():
        """Get list of companies with API usage."""
        try:
            import sqlite3
            
            # Connect to the database
            conn = sqlite3.connect(cost_tracker.db_path)
            cursor = conn.cursor()
            
            # Query for distinct companies
            cursor.execute('''
                SELECT DISTINCT company 
                FROM api_costs 
                WHERE company IS NOT NULL
                ORDER BY company
            ''')
            
            companies = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return jsonify({
                "success": True,
                "data": companies
            })
        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error fetching companies: {str(e)}"
            }), 500
    
    return app 