"""
Mission Planning and Management API Routes
Handles waypoint missions, flight plans, and autonomous operations.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging
import uuid
import json

logger = logging.getLogger(__name__)

missions_bp = Blueprint('missions', __name__)

# Mock mission storage (in production, use database)
mock_missions = {}
current_mission = None

def create_mock_mission():
    """Create a mock mission for development."""
    return {
        'id': str(uuid.uuid4()),
        'name': f'Mission {len(mock_missions) + 1}',
        'description': 'Automated surveillance mission',
        'created_at': datetime.now().isoformat(),
        'status': 'draft',
        'waypoints': [
            {
                'id': 1,
                'latitude': 33.6844,
                'longitude': 73.0479,
                'altitude': 50,
                'action': 'takeoff',
                'speed': 5,
                'hold_time': 5
            },
            {
                'id': 2,
                'latitude': 33.6854,
                'longitude': 73.0489,
                'altitude': 50,
                'action': 'waypoint',
                'speed': 8,
                'hold_time': 10
            },
            {
                'id': 3,
                'latitude': 33.6864,
                'longitude': 73.0499,
                'altitude': 60,
                'action': 'surveillance',
                'speed': 3,
                'hold_time': 30
            },
            {
                'id': 4,
                'latitude': 33.6844,
                'longitude': 73.0479,
                'altitude': 50,
                'action': 'return_to_launch',
                'speed': 10,
                'hold_time': 0
            }
        ],
        'parameters': {
            'max_speed': 15,
            'altitude_mode': 'relative',
            'rtl_altitude': 70,
            'auto_continue': True,
            'failsafe_action': 'rtl'
        },
        'estimated_duration': 1800,  # seconds
        'total_distance': 500,  # meters
        'execution_count': 0,
        'last_executed': None
    }

@missions_bp.route('/', methods=['GET'])
def get_missions():
    """Get all missions."""
    try:
        # Add some mock missions if none exist
        if not mock_missions:
            for i in range(3):
                mission = create_mock_mission()
                mission['name'] = f'Surveillance Route {i+1}'
                mock_missions[mission['id']] = mission
        
        missions_list = list(mock_missions.values())
        
        return jsonify({
            'missions': missions_list,
            'count': len(missions_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting missions: {e}")
        return jsonify({'error': 'Failed to get missions'}), 500

@missions_bp.route('/<mission_id>', methods=['GET'])
def get_mission(mission_id):
    """Get a specific mission by ID."""
    try:
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        mission = mock_missions[mission_id]
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
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'waypoints']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new mission
        mission = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'status': 'draft',
            'waypoints': data['waypoints'],
            'parameters': data.get('parameters', {
                'max_speed': 10,
                'altitude_mode': 'relative',
                'rtl_altitude': 50,
                'auto_continue': True,
                'failsafe_action': 'rtl'
            }),
            'execution_count': 0,
            'last_executed': None
        }
        
        # Calculate estimated duration and distance
        mission['estimated_duration'] = len(mission['waypoints']) * 60  # rough estimate
        mission['total_distance'] = calculate_mission_distance(mission['waypoints'])
        
        # Store mission
        mock_missions[mission['id']] = mission
        
        logger.info(f"Created new mission: {mission['name']} ({mission['id']})")
        return jsonify(mission), 201
        
    except Exception as e:
        logger.error(f"Error creating mission: {e}")
        return jsonify({'error': 'Failed to create mission'}), 500

@missions_bp.route('/<mission_id>', methods=['PUT'])
def update_mission(mission_id):
    """Update an existing mission."""
    try:
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        mission = mock_missions[mission_id]
        
        # Update allowed fields
        updatable_fields = ['name', 'description', 'waypoints', 'parameters']
        for field in updatable_fields:
            if field in data:
                mission[field] = data[field]
        
        mission['updated_at'] = datetime.now().isoformat()
        
        # Recalculate estimates if waypoints changed
        if 'waypoints' in data:
            mission['estimated_duration'] = len(mission['waypoints']) * 60
            mission['total_distance'] = calculate_mission_distance(mission['waypoints'])
        
        logger.info(f"Updated mission: {mission['name']} ({mission_id})")
        return jsonify(mission), 200
        
    except Exception as e:
        logger.error(f"Error updating mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to update mission'}), 500

@missions_bp.route('/<mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    """Delete a mission."""
    try:
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        mission = mock_missions.pop(mission_id)
        
        logger.info(f"Deleted mission: {mission['name']} ({mission_id})")
        return jsonify({'message': 'Mission deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to delete mission'}), 500

@missions_bp.route('/<mission_id>/execute', methods=['POST'])
def execute_mission(mission_id):
    """Execute a mission."""
    try:
        global current_mission
        
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        mission = mock_missions[mission_id]
        
        # Check if drone is ready
        # TODO: Integrate with actual drone status
        drone_ready = True  # Mock status
        if not drone_ready:
            return jsonify({'error': 'Drone not ready for mission execution'}), 400
        
        # Start mission execution
        mission['status'] = 'executing'
        mission['started_at'] = datetime.now().isoformat()
        mission['execution_count'] += 1
        current_mission = mission_id
        
        # TODO: Integrate with actual mission execution system
        logger.info(f"Started executing mission: {mission['name']} ({mission_id})")
        
        return jsonify({
            'message': 'Mission execution started',
            'mission_id': mission_id,
            'status': 'executing',
            'started_at': mission['started_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to execute mission'}), 500

@missions_bp.route('/<mission_id>/pause', methods=['POST'])
def pause_mission(mission_id):
    """Pause mission execution."""
    try:
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        mission = mock_missions[mission_id]
        
        if mission['status'] != 'executing':
            return jsonify({'error': 'Mission is not currently executing'}), 400
        
        mission['status'] = 'paused'
        mission['paused_at'] = datetime.now().isoformat()
        
        logger.info(f"Paused mission: {mission['name']} ({mission_id})")
        
        return jsonify({
            'message': 'Mission paused',
            'mission_id': mission_id,
            'status': 'paused'
        }), 200
        
    except Exception as e:
        logger.error(f"Error pausing mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to pause mission'}), 500

@missions_bp.route('/<mission_id>/resume', methods=['POST'])
def resume_mission(mission_id):
    """Resume paused mission."""
    try:
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        mission = mock_missions[mission_id]
        
        if mission['status'] != 'paused':
            return jsonify({'error': 'Mission is not paused'}), 400
        
        mission['status'] = 'executing'
        mission['resumed_at'] = datetime.now().isoformat()
        
        logger.info(f"Resumed mission: {mission['name']} ({mission_id})")
        
        return jsonify({
            'message': 'Mission resumed',
            'mission_id': mission_id,
            'status': 'executing'
        }), 200
        
    except Exception as e:
        logger.error(f"Error resuming mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to resume mission'}), 500

@missions_bp.route('/<mission_id>/abort', methods=['POST'])
def abort_mission(mission_id):
    """Abort mission execution."""
    try:
        global current_mission
        
        if mission_id not in mock_missions:
            return jsonify({'error': 'Mission not found'}), 404
        
        mission = mock_missions[mission_id]
        
        if mission['status'] not in ['executing', 'paused']:
            return jsonify({'error': 'Mission is not currently active'}), 400
        
        mission['status'] = 'aborted'
        mission['aborted_at'] = datetime.now().isoformat()
        current_mission = None
        
        logger.warning(f"Aborted mission: {mission['name']} ({mission_id})")
        
        return jsonify({
            'message': 'Mission aborted',
            'mission_id': mission_id,
            'status': 'aborted'
        }), 200
        
    except Exception as e:
        logger.error(f"Error aborting mission {mission_id}: {e}")
        return jsonify({'error': 'Failed to abort mission'}), 500

@missions_bp.route('/current', methods=['GET'])
def get_current_mission():
    """Get currently executing mission."""
    try:
        global current_mission
        
        if not current_mission:
            return jsonify({'message': 'No mission currently executing'}), 204
        
        if current_mission not in mock_missions:
            current_mission = None
            return jsonify({'message': 'Current mission not found'}), 404
        
        mission = mock_missions[current_mission]
        
        # Add execution progress
        mission_with_progress = mission.copy()
        mission_with_progress['progress'] = {
            'current_waypoint': 2,  # Mock progress
            'total_waypoints': len(mission['waypoints']),
            'completion_percentage': 45,
            'elapsed_time': 630,  # seconds
            'remaining_time': 770  # seconds
        }
        
        return jsonify(mission_with_progress), 200
        
    except Exception as e:
        logger.error(f"Error getting current mission: {e}")
        return jsonify({'error': 'Failed to get current mission'}), 500

@missions_bp.route('/templates', methods=['GET'])
def get_mission_templates():
    """Get predefined mission templates."""
    try:
        templates = [
            {
                'id': 'surveillance_pattern',
                'name': 'Surveillance Pattern',
                'description': 'Standard surveillance mission with search pattern',
                'waypoints': [
                    {'latitude': 33.6844, 'longitude': 73.0479, 'altitude': 50, 'action': 'takeoff'},
                    {'latitude': 33.6854, 'longitude': 73.0489, 'altitude': 50, 'action': 'waypoint'},
                    {'latitude': 33.6864, 'longitude': 73.0489, 'altitude': 50, 'action': 'waypoint'},
                    {'latitude': 33.6864, 'longitude': 73.0469, 'altitude': 50, 'action': 'waypoint'},
                    {'latitude': 33.6844, 'longitude': 73.0469, 'altitude': 50, 'action': 'waypoint'},
                    {'latitude': 33.6844, 'longitude': 73.0479, 'altitude': 50, 'action': 'return_to_launch'}
                ]
            },
            {
                'id': 'perimeter_check',
                'name': 'Perimeter Check',
                'description': 'Check perimeter of designated area',
                'waypoints': [
                    {'latitude': 33.6844, 'longitude': 73.0479, 'altitude': 40, 'action': 'takeoff'},
                    {'latitude': 33.6874, 'longitude': 73.0479, 'altitude': 40, 'action': 'waypoint'},
                    {'latitude': 33.6874, 'longitude': 73.0509, 'altitude': 40, 'action': 'waypoint'},
                    {'latitude': 33.6814, 'longitude': 73.0509, 'altitude': 40, 'action': 'waypoint'},
                    {'latitude': 33.6814, 'longitude': 73.0449, 'altitude': 40, 'action': 'waypoint'},
                    {'latitude': 33.6844, 'longitude': 73.0479, 'altitude': 40, 'action': 'return_to_launch'}
                ]
            }
        ]
        
        return jsonify({'templates': templates}), 200
        
    except Exception as e:
        logger.error(f"Error getting mission templates: {e}")
        return jsonify({'error': 'Failed to get mission templates'}), 500

def calculate_mission_distance(waypoints):
    """Calculate total distance of mission waypoints."""
    try:
        total_distance = 0
        for i in range(1, len(waypoints)):
            # Simple distance calculation (not accounting for Earth's curvature)
            lat1, lon1 = waypoints[i-1]['latitude'], waypoints[i-1]['longitude']
            lat2, lon2 = waypoints[i]['latitude'], waypoints[i]['longitude']
            
            # Approximate distance in meters
            distance = ((lat2 - lat1) * 111000) ** 2 + ((lon2 - lon1) * 111000) ** 2
            total_distance += distance ** 0.5
        
        return round(total_distance, 2)
    except:
        return 0
