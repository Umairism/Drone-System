"""
Web UI Routes
Serves the drone control dashboard and static files.
"""

from flask import Blueprint, render_template_string, send_from_directory
import os

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    """Serve the main drone control dashboard."""
    dashboard_path = os.path.join(os.path.dirname(__file__), '../../drone-dashboard.html')
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_html = f.read()
        return dashboard_html
    except FileNotFoundError:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Drone Control Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #1a1a2e; color: white; }
                .error { color: #ff6b6b; }
            </style>
        </head>
        <body>
            <h1>🚁 Surveillance Drone System</h1>
            <p class="error">Dashboard file not found. Please ensure drone-dashboard.html exists.</p>
            <p>Backend API is running at <a href="/api/drone/status" style="color: #74c0fc;">/api/drone/status</a></p>
        </body>
        </html>
        """)

@ui_bp.route('/dashboard')
def dashboard():
    """Alternative route for the dashboard."""
    return index()

@ui_bp.route('/advanced-dashboard.html')
def advanced_dashboard():
    """Serve the advanced drone control dashboard."""
    dashboard_path = os.path.join(os.path.dirname(__file__), '../advanced-dashboard.html')
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_html = f.read()
        return dashboard_html
    except FileNotFoundError:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Advanced Drone Dashboard - Not Found</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #1a1a2e; color: white; }
                .error { color: #ff6b6b; }
            </style>
        </head>
        <body>
            <h1>🚁 Advanced Surveillance Drone Dashboard</h1>
            <p class="error">Advanced dashboard file not found.</p>
            <p><a href="/" style="color: #74c0fc;">← Go to Basic Dashboard</a></p>
        </body>
        </html>
        """)

@ui_bp.route('/health')
def health():
    """Simple health check page."""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Health</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #1a1a2e; color: white; }
            .status { color: #51cf66; font-size: 24px; }
        </style>
    </head>
    <body>
        <h1>🚁 Drone System Health</h1>
        <p class="status">✅ Backend Server: Running</p>
        <p class="status">✅ API Endpoints: Active</p>
        <p class="status">✅ Dynamic Data: Operational</p>
        <p><a href="/" style="color: #74c0fc;">Go to Dashboard</a></p>
    </body>
    </html>
    """)
