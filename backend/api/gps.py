"""
GPS API Routes
Handles GPS location updates and tracking for real drone integration.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

gps_bp = Blueprint('gps', __name__)

# Store current GPS location (in production, use database)
current_gps_location = {
    'lat': 33.6844,  # Default to Islamabad, Pakistan
    'lng': 73.0479,
    'altitude': 500,
    'satellites': 0,
    'fix_quality': 0,
    'accuracy': 0,
    'speed': 0,
    'heading': 0,
    'timestamp': None
}

# Flight path tracking
flight_path = []

@gps_bp.route('/update', methods=['POST'])
def update_gps_location():
    """Receive GPS updates from external GPS reader or flight controller."""
    global current_gps_location, flight_path
    
    try:
        data = request.get_json()
        
        # Update current location
        if 'lat' in data and 'lng' in data:
            current_gps_location.update(data)
            current_gps_location['timestamp'] = datetime.now().isoformat()
            
            # Add to flight path (keep last 1000 points)
            flight_path.append({
                'lat': data['lat'],
                'lng': data['lng'],
                'altitude': data.get('altitude', 0),
                'timestamp': current_gps_location['timestamp']
            })
            
            if len(flight_path) > 1000:
                flight_path = flight_path[-1000:]
            
            # Update dynamic data manager
            try:
                from dynamic_data import drone_data_manager
                drone_data_manager.current_position = {
                    'lat': data['lat'],
                    'lng': data['lng'],
                    'alt': data.get('altitude', drone_data_manager.current_position.get('alt', 0))
                }
            except ImportError:
                pass
            
            # Log GPS update
            try:
                from utils.logger import get_drone_logger
                logger = get_drone_logger()
                if logger:
                    logger.log_gps_event(
                        event_type="location_update",
                        location=current_gps_location,
                        message=f"GPS location updated: {data.get('lat'):.6f}, {data.get('lng'):.6f}"
                    )
            except:
                pass
            
            # Broadcast to connected clients via Socket.IO
            try:
                from flask import current_app
                if hasattr(current_app, 'socketio'):
                    current_app.socketio.emit('gps_location_update', current_gps_location)
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': 'GPS location updated',
            'location': current_gps_location
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@gps_bp.route('/current', methods=['GET'])
def get_current_location():
    """Get current GPS location."""
    return jsonify({
        'success': True,
        'location': current_gps_location,
        'status': {
            'fix_available': current_gps_location['satellites'] >= 4,
            'accuracy': calculate_gps_accuracy(current_gps_location['satellites']),
            'last_update': current_gps_location['timestamp']
        }
    })

@gps_bp.route('/path', methods=['GET'])
def get_flight_path():
    """Get flight path data."""
    limit = request.args.get('limit', 100, type=int)
    
    return jsonify({
        'success': True,
        'path': flight_path[-limit:],
        'total_points': len(flight_path)
    })

@gps_bp.route('/path/clear', methods=['DELETE'])
def clear_flight_path():
    """Clear flight path data."""
    global flight_path
    flight_path = []
    
    return jsonify({
        'success': True,
        'message': 'Flight path cleared'
    })

@gps_bp.route('/waypoints', methods=['GET'])
def get_waypoints():
    """Get mission waypoints."""
    # This would typically come from mission data
    return jsonify({
        'success': True,
        'waypoints': [
            {'lat': 33.6844, 'lng': 73.0479, 'altitude': 50, 'name': 'Home'},
            {'lat': 33.6854, 'lng': 73.0489, 'altitude': 50, 'name': 'Waypoint 1'},
            {'lat': 33.6864, 'lng': 73.0499, 'altitude': 50, 'name': 'Waypoint 2'},
        ]
    })

@gps_bp.route('/simulate', methods=['POST'])
def simulate_gps_movement():
    """Simulate GPS movement for testing (when no real GPS available)."""
    import random
    import math
    
    # Simulate movement around current position
    base_lat = current_gps_location['lat']
    base_lng = current_gps_location['lng']
    
    # Small random movement (within ~100 meters)
    lat_offset = random.uniform(-0.001, 0.001)
    lng_offset = random.uniform(-0.001, 0.001)
    
    simulated_data = {
        'lat': base_lat + lat_offset,
        'lng': base_lng + lng_offset,
        'altitude': current_gps_location['altitude'] + random.uniform(-5, 5),
        'satellites': random.randint(6, 12),
        'fix_quality': 1,
        'accuracy': random.uniform(1, 3),
        'speed': random.uniform(0, 15),  # m/s
        'heading': random.uniform(0, 360)
    }
    
    # Use the same update logic
    return update_gps_location_internal(simulated_data)

def update_gps_location_internal(data):
    """Internal GPS update function."""
    global current_gps_location
    current_gps_location.update(data)
    current_gps_location['timestamp'] = datetime.now().isoformat()
    
    return current_gps_location

def calculate_gps_accuracy(satellites):
    """Calculate GPS accuracy based on satellite count."""
    if satellites >= 8:
        return 'High (< 3m)'
    elif satellites >= 6:
        return 'Medium (< 5m)'
    elif satellites >= 4:
        return 'Low (< 10m)'
    else:
        return 'Poor (> 10m)'

@gps_bp.route('/status', methods=['GET'])
def get_gps_status():
    """Get comprehensive GPS status."""
    return jsonify({
        'success': True,
        'status': {
            'connected': current_gps_location['timestamp'] is not None,
            'satellites': current_gps_location['satellites'],
            'fix_quality': current_gps_location['fix_quality'],
            'accuracy': calculate_gps_accuracy(current_gps_location['satellites']),
            'last_update': current_gps_location['timestamp'],
            'location_available': current_gps_location['lat'] != 0 and current_gps_location['lng'] != 0,
            'flight_path_points': len(flight_path)
        }
    })
