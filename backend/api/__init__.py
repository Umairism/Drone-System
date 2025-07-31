"""
API Package Initialization
Registers all API blueprints and routes.
"""

from flask import Blueprint

def register_api_routes(app):
    """Register all API routes with the Flask app."""
    
    # Import blueprints
    from .routes import api_bp
    from .drone_control import drone_bp
    from .telemetry import telemetry_bp
    from .missions import missions_bp
    from .video import video_bp
    from .ui import ui_bp
    
    # Register UI routes directly to app (not under /api)
    app.register_blueprint(ui_bp)
    
    # Create main API blueprint
    main_api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # Register sub-blueprints
    main_api_bp.register_blueprint(api_bp)
    main_api_bp.register_blueprint(drone_bp, url_prefix='/drone')
    main_api_bp.register_blueprint(telemetry_bp, url_prefix='/telemetry')
    main_api_bp.register_blueprint(missions_bp, url_prefix='/missions')
    main_api_bp.register_blueprint(video_bp, url_prefix='/video')
    
    # Register main API blueprint with app
    app.register_blueprint(main_api_bp)
    
    return main_api_bp
