"""
Drone Control API Routes
Handles flight control commands and operations using dynamic data.
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

drone_bp = Blueprint('drone', __name__)

# Import dynamic data manager
from dynamic_data import drone_data_manager

@drone_bp.route('/status', methods=['GET'])
def get_drone_status():
    """Get current drone status and telemetry."""
    try:
        status = drone_data_manager.get_drone_status()
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting drone status: {e}")
        return jsonify({'error': 'Failed to get drone status'}), 500

@drone_bp.route('/arm', methods=['POST'])
def arm_drone():
    """Arm the drone motors."""
    try:
        result = drone_data_manager.arm_drone()
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error arming drone: {e}")
        return jsonify({'error': 'Failed to arm drone'}), 500

@drone_bp.route('/disarm', methods=['POST'])
def disarm_drone():
    """Disarm the drone motors."""
    try:
        result = drone_data_manager.disarm_drone()
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error disarming drone: {e}")
        return jsonify({'error': 'Failed to disarm drone'}), 500

@drone_bp.route('/takeoff', methods=['POST'])
def takeoff():
    """Command drone to takeoff."""
    try:
        data = request.get_json() or {}
        altitude = data.get('altitude', 10)
        
        if altitude < 1 or altitude > 100:
            return jsonify({'error': 'Altitude must be between 1 and 100 meters'}), 400
        
        result = drone_data_manager.takeoff(altitude)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error during takeoff: {e}")
        return jsonify({'error': 'Failed to takeoff'}), 500

@drone_bp.route('/land', methods=['POST'])
def land():
    """Command drone to land."""
    try:
        result = drone_data_manager.land()
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error during landing: {e}")
        return jsonify({'error': 'Failed to land'}), 500

@drone_bp.route('/goto', methods=['POST'])
def goto_position():
    """Navigate drone to specific coordinates."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No position data provided'}), 400
        
        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        altitude = float(data.get('altitude', 10))
        
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            return jsonify({'error': 'Invalid latitude'}), 400
        if not (-180 <= longitude <= 180):
            return jsonify({'error': 'Invalid longitude'}), 400
        if not (1 <= altitude <= 100):
            return jsonify({'error': 'Altitude must be between 1 and 100 meters'}), 400
        
        result = drone_data_manager.goto_position(latitude, longitude, altitude)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except ValueError:
        return jsonify({'error': 'Invalid coordinate values'}), 400
    except Exception as e:
        logger.error(f"Error navigating to position: {e}")
        return jsonify({'error': 'Failed to navigate to position'}), 500

@drone_bp.route('/return-home', methods=['POST'])
def return_home():
    """Return drone to launch position."""
    try:
        # Return to base position
        result = drone_data_manager.goto_position(33.6844, 73.0479, 10)
        if result['success']:
            result['message'] = 'Returning to launch position'
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Error returning home: {e}")
        return jsonify({'error': 'Failed to return home'}), 500

@drone_bp.route('/emergency-stop', methods=['POST'])
def emergency_stop():
    """Emergency stop - immediate landing."""
    try:
        drone_data_manager.add_alert("Emergency stop activated", "warning")
        result = drone_data_manager.land()
        result['message'] = 'Emergency stop activated - landing immediately'
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error during emergency stop: {e}")
        return jsonify({'error': 'Failed to execute emergency stop'}), 500

@drone_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get current system alerts."""
    try:
        alerts = drone_data_manager.get_alerts()
        return jsonify({'alerts': alerts}), 200
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': 'Failed to get alerts'}), 500
