"""
Dash dashboard for visualizing API usage.
"""

import logging
from typing import Dict, List, Any, Optional

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

from ..utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)

def create_dashboard() -> dash.Dash:
    """Create a Dash application for the dashboard.
    
    Returns:
        Configured Dash application
    """
    # Create the Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="Anthropic Cost Tracker"
    )
    
    # Define layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Anthropic Cost Tracker Dashboard", className="mt-4 mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filter Options"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Time Period:"),
                                dcc.Dropdown(
                                    id="time-period-dropdown",
                                    options=[
                                        {"label": "Last 7 days", "value": 7},
                                        {"label": "Last 30 days", "value": 30},
                                        {"label": "Last 90 days", "value": 90},
                                        {"label": "Last 365 days", "value": 365},
                                    ],
                                    value=30,
                                    clearable=False
                                )
                            ], width=4),
                            
                            dbc.Col([
                                html.Label("Company/Project:"),
                                dcc.Dropdown(
                                    id="company-dropdown",
                                    options=[],  # Will be populated from API
                                    placeholder="All companies"
                                )
                            ], width=4),
                            
                            dbc.Col([
                                html.Label("API:"),
                                dcc.Dropdown(
                                    id="api-dropdown",
                                    options=[
                                        {"label": "All APIs", "value": "all"},
                                        {"label": "Anthropic", "value": "anthropic"},
                                    ],
                                    value="all",
                                    clearable=False
                                )
                            ], width=4)
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Usage Summary"),
                    dbc.CardBody(id="summary-card")
                ])
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Daily Cost Trend"),
                    dbc.CardBody([
                        dcc.Graph(id="daily-cost-chart")
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Cost by Model"),
                    dbc.CardBody([
                        dcc.Graph(id="model-cost-chart")
                    ])
                ])
            ], width=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Usage by Function/Endpoint"),
                    dbc.CardBody([
                        html.Div(id="function-table")
                    ])
                ])
            ], width=12)
        ])
    ], fluid=True)
    
    # Initialize cost tracker
    cost_tracker = CostTracker()
    
    # Callback to populate company dropdown
    @app.callback(
        Output("company-dropdown", "options"),
        Input("time-period-dropdown", "value")
    )
    def populate_companies(days):
        try:
            import sqlite3
            
            # Connect to database
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
            
            # Create dropdown options
            options = [{"label": "All companies", "value": "all"}]
            options.extend([{"label": company, "value": company} for company in companies])
            
            return options
        except Exception as e:
            logger.error(f"Error fetching companies: {str(e)}")
            return [{"label": "All companies", "value": "all"}]
    
    # Callback to update summary card
    @app.callback(
        Output("summary-card", "children"),
        [Input("time-period-dropdown", "value"),
         Input("company-dropdown", "value"),
         Input("api-dropdown", "value")]
    )
    def update_summary(days, company, api):
        try:
            # Get usage stats
            api_name = None if api == "all" else api
            company_name = None if not company or company == "all" else company
            
            stats = cost_tracker.get_usage_stats(days=days, api_name=api_name, company=company_name)
            
            # Create summary card
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H4(f"${stats['total_cost']:.2f}"),
                        html.P("Total Cost", className="text-muted")
                    ], width=3),
                    
                    dbc.Col([
                        html.H4(f"{stats['total_tokens_in'] + stats['total_tokens_out']:,}"),
                        html.P("Total Tokens", className="text-muted")
                    ], width=3),
                    
                    dbc.Col([
                        html.H4(f"{stats['total_calls']:,}"),
                        html.P("API Calls", className="text-muted")
                    ], width=3),
                    
                    dbc.Col([
                        html.H4(f"${stats['total_cost'] / max(1, stats['total_calls']):.4f}"),
                        html.P("Avg. Cost per Call", className="text-muted")
                    ], width=3)
                ])
            ])
        except Exception as e:
            logger.error(f"Error updating summary: {str(e)}")
            return html.Div("Error loading summary data")
    
    # Callback to update daily cost chart
    @app.callback(
        Output("daily-cost-chart", "figure"),
        [Input("time-period-dropdown", "value"),
         Input("company-dropdown", "value"),
         Input("api-dropdown", "value")]
    )
    def update_daily_chart(days, company, api):
        try:
            # Get daily usage data
            company_name = None if not company or company == "all" else company
            daily_data = cost_tracker.get_daily_usage(days=days, company=company_name)
            
            # Filter by API if needed
            if api != "all":
                daily_data = [entry for entry in daily_data if entry["api"] == api]
            
            # Convert to dataframe for plotting
            if daily_data:
                df = pd.DataFrame(daily_data)
                
                # Group by date and sum costs
                daily_costs = df.groupby('date').agg({
                    'cost': 'sum',
                    'tokens_in': 'sum',
                    'tokens_out': 'sum'
                }).reset_index()
                
                # Sort by date
                daily_costs = daily_costs.sort_values('date')
                
                # Create the chart
                fig = px.bar(
                    daily_costs,
                    x='date',
                    y='cost',
                    labels={'date': 'Date', 'cost': 'Cost ($)'},
                    title='Daily API Cost'
                )
                
                fig.update_layout(xaxis_title="Date", yaxis_title="Cost ($)")
                
                return fig
            else:
                # Return empty chart
                return go.Figure().update_layout(
                    title="No data available for the selected period",
                    xaxis_title="Date",
                    yaxis_title="Cost ($)"
                )
        except Exception as e:
            logger.error(f"Error updating daily chart: {str(e)}")
            return go.Figure().update_layout(title=f"Error: {str(e)}")
    
    # Callback to update model cost chart
    @app.callback(
        Output("model-cost-chart", "figure"),
        [Input("time-period-dropdown", "value"),
         Input("company-dropdown", "value"),
         Input("api-dropdown", "value")]
    )
    def update_model_chart(days, company, api):
        try:
            # Get usage data
            api_name = None if api == "all" else api
            company_name = None if not company or company == "all" else company
            
            stats = cost_tracker.get_usage_stats(days=days, api_name=api_name, company=company_name)
            
            # Extract model data
            model_data = []
            
            for api_name, api_stats in stats['by_api'].items():
                for endpoint, ep_stats in api_stats['by_endpoint'].items():
                    model_data.append({
                        'api': api_name,
                        'model': endpoint,
                        'cost': ep_stats['cost'],
                        'tokens': ep_stats['tokens_in'] + ep_stats['tokens_out'],
                        'calls': ep_stats['calls']
                    })
            
            if model_data:
                # Convert to dataframe
                df = pd.DataFrame(model_data)
                
                # Create the chart
                fig = px.pie(
                    df,
                    values='cost',
                    names='model',
                    title='Cost Distribution by Model'
                )
                
                fig.update_layout(legend_title="Model")
                
                return fig
            else:
                # Return empty chart
                return go.Figure().update_layout(
                    title="No model data available for the selected period"
                )
        except Exception as e:
            logger.error(f"Error updating model chart: {str(e)}")
            return go.Figure().update_layout(title=f"Error: {str(e)}")
    
    # Callback to update function table
    @app.callback(
        Output("function-table", "children"),
        [Input("time-period-dropdown", "value"),
         Input("company-dropdown", "value"),
         Input("api-dropdown", "value")]
    )
    def update_function_table(days, company, api):
        try:
            # Get function usage data
            company_name = None if not company or company == "all" else company
            function_data = cost_tracker.get_usage_by_function(days=days, company=company_name)
            
            # Filter by API if needed
            if api != "all":
                function_data = [entry for entry in function_data if entry["api"] == api]
            
            if function_data:
                # Create a table from the data
                rows = []
                
                # Add table header
                header = html.Tr([
                    html.Th("API"),
                    html.Th("Function/Model"),
                    html.Th("Calls"),
                    html.Th("Tokens"),
                    html.Th("Cost ($)"),
                    html.Th("Cost/Call ($)")
                ])
                
                # Sort by cost (descending)
                function_data.sort(key=lambda x: x['cost'], reverse=True)
                
                # Add table rows
                for entry in function_data:
                    cost_per_call = entry['cost'] / max(1, entry['calls'])
                    rows.append(html.Tr([
                        html.Td(entry['api']),
                        html.Td(entry['function']),
                        html.Td(f"{entry['calls']:,}"),
                        html.Td(f"{entry['tokens_in'] + entry['tokens_out']:,}"),
                        html.Td(f"${entry['cost']:.4f}"),
                        html.Td(f"${cost_per_call:.4f}")
                    ]))
                
                return dbc.Table([html.Thead(header), html.Tbody(rows)], striped=True, bordered=True, hover=True)
            else:
                return html.P("No function usage data available for the selected period")
        except Exception as e:
            logger.error(f"Error updating function table: {str(e)}")
            return html.P(f"Error: {str(e)}")
    
    return app

def run_dashboard(host: str = '127.0.0.1', port: int = 8050, debug: bool = False):
    """Run the dashboard.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Whether to run in debug mode
    """
    app = create_dashboard()
    app.run_server(host=host, port=port, debug=debug) 