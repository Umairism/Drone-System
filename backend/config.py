"""
Flask Configuration Classes
"""

import os
from pathlib import Path

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'surveillance-drone-secret-key-change-in-production'
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///data/drone_data.db'
    
    # Video streaming
    CAMERA_DEVICE = int(os.environ.get('CAMERA_DEVICE', 0))
    CAMERA_RESOLUTION = os.environ.get('CAMERA_RESOLUTION', '1920x1080')
    CAMERA_FPS = int(os.environ.get('CAMERA_FPS', 30))
    
    # MAVLink
    MAVLINK_PORT = os.environ.get('MAVLINK_PORT', '/dev/ttyUSB0')
    MAVLINK_BAUDRATE = int(os.environ.get('MAVLINK_BAUDRATE', 57600))
    
    # GPS
    GPS_PORT = os.environ.get('GPS_PORT', '/dev/ttyACM0')
    GPS_BAUDRATE = int(os.environ.get('GPS_BAUDRATE', 9600))
    
    # Flight limits
    MAX_ALTITUDE = int(os.environ.get('MAX_ALTITUDE', 120))
    MAX_SPEED = int(os.environ.get('MAX_SPEED', 15))
    
    # Upload folder
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///test_drone_data.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
