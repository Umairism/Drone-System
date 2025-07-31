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
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register socket events
    register_socket_events(socketio)
    
    # Create directories
    create_directories()
    
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

def register_socket_events(socketio):
    """Register Socket.IO events."""
    from api.socket_events import register_socketio_events
    register_socketio_events(socketio)

def create_directories():
    """Create necessary directories."""
    directories = ['logs', 'data', 'data/recordings', 'data/missions', 'uploads']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
