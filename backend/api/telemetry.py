"""
Telemetry API Routes
Provides real-time sensor data and system information using dynamic data.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

telemetry_bp = Blueprint('telemetry', __name__)

# Import dynamic data manager
from dynamic_data import drone_data_manager

@telemetry_bp.route('/gps', methods=['GET'])
def get_gps_data():
    """Get current GPS coordinates and related data."""
    try:
        telemetry = drone_data_manager.get_telemetry()
        gps_data = {
            'latitude': telemetry['gps']['latitude'],
            'longitude': telemetry['gps']['longitude'],
            'altitude': telemetry['gps']['altitude'],
            'heading': telemetry['orientation']['heading'],
            'speed': telemetry['flight_data']['speed'],
            'satellites': telemetry['gps']['satellites'],
            'timestamp': telemetry['timestamp']
        }
        return jsonify(gps_data), 200
        
    except Exception as e:
        logger.error(f"Error getting GPS data: {e}")
        return jsonify({'error': 'Failed to get GPS data'}), 500

@telemetry_bp.route('/sensors', methods=['GET'])
def get_sensor_data():
    """Get all sensor readings."""
    try:
        telemetry = drone_data_manager.get_telemetry()
        sensor_data = {
            'accelerometer': telemetry['sensors']['accelerometer'],
            'gyroscope': telemetry['sensors']['gyroscope'],
            'magnetometer': telemetry['sensors']['magnetometer'],
            'barometer': telemetry['sensors']['barometer'],
            'timestamp': telemetry['timestamp']
        }
        return jsonify(sensor_data), 200
        
    except Exception as e:
        logger.error(f"Error getting sensor data: {e}")
        return jsonify({'error': 'Failed to get sensor data'}), 500

@telemetry_bp.route('/battery', methods=['GET'])
def get_battery_status():
    """Get battery information."""
    try:
        telemetry = drone_data_manager.get_telemetry()
        battery_data = {
            'level': telemetry['battery']['level'],
            'voltage': telemetry['battery']['voltage'],
            'current': telemetry['battery']['current'],
            'remaining_time': telemetry['battery']['remaining_time'],
            'temperature': telemetry['battery']['temperature'],
            'timestamp': telemetry['timestamp']
        }
        return jsonify(battery_data), 200
        
    except Exception as e:
        logger.error(f"Error getting battery status: {e}")
        return jsonify({'error': 'Failed to get battery status'}), 500

@telemetry_bp.route('/flight-data', methods=['GET'])
def get_flight_data():
    """Get flight performance data."""
    try:
        telemetry = drone_data_manager.get_telemetry()
        flight_data = {
            'speed': telemetry['flight_data']['speed'],
            'vertical_speed': telemetry['flight_data']['vertical_speed'],
            'distance_traveled': telemetry['flight_data']['distance_traveled'],
            'flight_time': telemetry['flight_data']['flight_time'],
            'orientation': telemetry['orientation'],
            'timestamp': telemetry['timestamp']
        }
        return jsonify(flight_data), 200
        
    except Exception as e:
        logger.error(f"Error getting flight data: {e}")
        return jsonify({'error': 'Failed to get flight data'}), 500

@telemetry_bp.route('/current', methods=['GET'])
def get_current_telemetry():
    """Get current telemetry data (legacy endpoint)."""
    try:
        telemetry = drone_data_manager.get_telemetry()
        return jsonify(telemetry), 200
        
    except Exception as e:
        logger.error(f"Error getting current telemetry: {e}")
        return jsonify({'error': 'Failed to get current telemetry'}), 500

@telemetry_bp.route('/full', methods=['GET'])
def get_full_telemetry():
    """Get complete telemetry data."""
    try:
        telemetry = drone_data_manager.get_telemetry()
        status = drone_data_manager.get_drone_status()
        alerts = drone_data_manager.get_alerts()
        
        full_data = {
            'telemetry': telemetry,
            'status': status,
            'alerts': alerts,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(full_data), 200
        
    except Exception as e:
        logger.error(f"Error getting full telemetry: {e}")
        return jsonify({'error': 'Failed to get full telemetry'}), 500
