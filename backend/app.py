"""
Flask Application Factory
Main Flask application setup and configuration.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from pathlib import Path

def create_app(config_name='development'):
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins="*")
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Store socketio instance for access in other modules
    app.socketio = socketio
    
    # Create directories first
    create_directories()
    
    # Setup logging
    setup_logging(app)
    
    # Initialize advanced systems
    initialize_advanced_systems(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register socket events
    register_socket_events(socketio)
    
    return app, socketio

def setup_logging(app):
    """Setup application logging."""
    if not app.debug:
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_dir / 'flask_app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Surveillance Drone Flask application startup')

def register_blueprints(app):
    """Register Flask blueprints."""
    from api import register_api_routes
    register_api_routes(app)
    
    # Register advanced API routes
    try:
        from api.advanced import register_advanced_api_routes
        register_advanced_api_routes(app)
    except ImportError as e:
        app.logger.warning(f"Could not import advanced API routes: {e}")

def initialize_advanced_systems(app):
    """Initialize advanced systems (logging, celebrations, mobile)."""
    try:
        # Initialize advanced logging system
        from utils.logger import init_logger
        init_logger(app)
        app.logger.info("Advanced logging system initialized")
    except ImportError as e:
        app.logger.warning(f"Could not initialize advanced logging: {e}")
    
    try:
        # Initialize celebration system
        from utils.celebrations import init_celebration_system
        init_celebration_system()
        app.logger.info("Celebration system initialized")
    except ImportError as e:
        app.logger.warning(f"Could not initialize celebration system: {e}")
    
    try:
        # Initialize mobile compatibility system
        from utils.mobile import init_mobile_compatibility
        init_mobile_compatibility()
        app.logger.info("Mobile compatibility system initialized")
    except ImportError as e:
        app.logger.warning(f"Could not initialize mobile compatibility: {e}")

def register_socket_events(socketio):
    """Register Socket.IO events."""
    from api.socket_events import register_socketio_events
    register_socketio_events(socketio)

def create_directories():
    """Create necessary directories."""
    directories = [
        'logs', 'logs/flight_logs', 'logs/error_logs', 'logs/mission_logs', 
        'logs/performance_logs', 'logs/security_logs', 'logs/api_logs', 
        'logs/telemetry_logs', 'logs/achievements',
        'data', 'data/recordings', 'data/missions', 'data/mobile', 
        'uploads'
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Main application instance
if __name__ == '__main__':
    app, socketio = create_app('development')
    print("🚁 Surveillance Drone System Starting...")
    print("🌟 Advanced Features: Logging ✓ Celebrations ✓ Mobile ✓")
    print("🌐 Server running at: http://localhost:5000")
    print("📊 Advanced Dashboard: http://localhost:5000/advanced-dashboard.html")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
