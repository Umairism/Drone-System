"""
Main API Routes
General API endpoints for the surveillance drone system.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def get_system_status():
    """Get system status and health information."""
    try:
        status = {
            'status': 'operational',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': '00:00:00',  # TODO: Calculate actual uptime
            'components': {
                'flight_controller': 'connected',
                'camera': 'active',
                'gps': 'fixed',
                'sensors': 'operational'
            },
            'system_info': {
                'cpu_usage': 0,  # TODO: Get actual CPU usage
                'memory_usage': 0,  # TODO: Get actual memory usage
                'disk_space': 0,  # TODO: Get actual disk space
                'temperature': 0  # TODO: Get system temperature
            }
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': 'Failed to get system status'}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@api_bp.route('/version', methods=['GET'])
def get_version():
    """Get application version information."""
    return jsonify({
        'name': 'Surveillance Drone System',
        'version': '1.0.0',
        'api_version': 'v1',
        'build_date': '2025-07-31',
        'author': 'Muhammad Umair Hakeem'
    }), 200

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get system configuration (non-sensitive data only)."""
    try:
        from flask import current_app
        
        config = {
            'camera': {
                'resolution': current_app.config['CAMERA_RESOLUTION'],
                'fps': current_app.config['CAMERA_FPS']
            },
            'flight_limits': {
                'max_altitude': current_app.config['MAX_ALTITUDE'],
                'max_speed': current_app.config['MAX_SPEED']
            },
            'features': {
                'object_detection': True,
                'video_recording': True,
                'gps_tracking': True,
                'autonomous_flight': True
            }
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        return jsonify({'error': 'Failed to get configuration'}), 500

@api_bp.route('/logs', methods=['GET'])
def get_recent_logs():
    """Get recent system logs."""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        level = request.args.get('level', 'INFO')
        
        # TODO: Implement actual log reading
        logs = [
            {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': 'System operational',
                'module': 'main'
            }
        ]
        
        return jsonify({
            'logs': logs,
            'count': len(logs),
            'limit': limit,
            'level': level
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'error': 'Failed to get logs'}), 500

@api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500
