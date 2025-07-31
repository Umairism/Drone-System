"""
Mission Planning and Management API Routes
Handles waypoint missions, flight plans, and autonomous operations using dynamic data.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging
import uuid
import json

logger = logging.getLogger(__name__)

missions_bp = Blueprint('missions', __name__)

# Import dynamic data manager
from dynamic_data import drone_data_manager

@missions_bp.route('/', methods=['GET'])
def get_missions():
    """Get all missions."""
    try:
        missions = drone_data_manager.get_missions()
        return jsonify({'missions': missions}), 200
        
    except Exception as e:
        logger.error(f"Error getting missions: {e}")
        return jsonify({'error': 'Failed to get missions'}), 500

@missions_bp.route('/<mission_id>', methods=['GET'])
def get_mission(mission_id):
    """Get specific mission details."""
    try:
        mission = drone_data_manager.get_mission(mission_id)
        if not mission:
            return jsonify({'error': 'Mission not found'}), 404
        
        return jsonify(mission), 200
        
    except Exception as e:
        logger.error(f"Error getting mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to get mission'}), 500

@missions_bp.route('/', methods=['POST'])
def create_mission():
    """Create a new mission."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No mission data provided'}), 400
        
        required_fields = ['name', 'waypoints']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not data['waypoints']:
            return jsonify({'error': 'Mission must have at least one waypoint'}), 400
        
        # Validate waypoints
        for i, waypoint in enumerate(data['waypoints']):
            required_wp_fields = ['latitude', 'longitude', 'altitude']
            for field in required_wp_fields:
                if field not in waypoint:
                    return jsonify({'error': f'Waypoint {i+1} missing required field: {field}'}), 400
        
        mission_data = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'description': data.get('description', ''),
            'waypoints': data['waypoints'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'draft'
        }
        
        mission = drone_data_manager.create_mission(mission_data)
        return jsonify(mission), 201
        
    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        return jsonify({'error': 'Failed to create mission'}), 500

@missions_bp.route('/<mission_id>/start', methods=['POST'])
def start_mission(mission_id):
    """Start executing a mission."""
    try:
        result = drone_data_manager.start_mission(mission_id)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error starting mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to start mission'}), 500

@missions_bp.route('/current', methods=['GET'])
def get_current_mission():
    """Get currently executing mission."""
    try:
        mission = drone_data_manager.get_current_mission()
        if not mission:
            return jsonify({'message': 'No active mission'}), 200
        
        return jsonify(mission), 200
        
    except Exception as e:
        logger.error(f"Error getting current mission: {e}")
        return jsonify({'error': 'Failed to get current mission'}), 500
