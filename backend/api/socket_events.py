"""
Socket.IO Event Handlers
Handles real-time communication between frontend and backend.
"""

from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from datetime import datetime
import logging
import json
import asyncio
import threading
import time

logger = logging.getLogger(__name__)

# Active connections tracking
active_connections = {}
telemetry_subscriptions = set()
video_subscriptions = set()

def register_socketio_events(socketio):
    """Register all Socket.IO event handlers."""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection."""
        try:
            client_id = request.sid
            active_connections[client_id] = {
                'connected_at': datetime.now().isoformat(),
                'auth': auth,
                'subscriptions': []
            }
            
            logger.info(f"Client connected: {client_id}")
            emit('connection_status', {
                'status': 'connected',
                'client_id': client_id,
                'server_time': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling client connection: {e}")
            disconnect()
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        try:
            client_id = request.sid
            
            # Remove from subscriptions
            telemetry_subscriptions.discard(client_id)
            video_subscriptions.discard(client_id)
            
            # Remove from active connections
            if client_id in active_connections:
                del active_connections[client_id]
            
            logger.info(f"Client disconnected: {client_id}")
            
        except Exception as e:
            logger.error(f"Error handling client disconnection: {e}")
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle client joining a room."""
        try:
            room = data.get('room')
            if not room:
                emit('error', {'message': 'Room name required'})
                return
            
            join_room(room)
            client_id = request.sid
            
            if client_id in active_connections:
                active_connections[client_id]['subscriptions'].append(room)
            
            logger.info(f"Client {client_id} joined room: {room}")
            emit('room_joined', {'room': room})
            
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            emit('error', {'message': 'Failed to join room'})
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle client leaving a room."""
        try:
            room = data.get('room')
            if not room:
                emit('error', {'message': 'Room name required'})
                return
            
            leave_room(room)
            client_id = request.sid
            
            if client_id in active_connections:
                subscriptions = active_connections[client_id]['subscriptions']
                if room in subscriptions:
                    subscriptions.remove(room)
            
            logger.info(f"Client {client_id} left room: {room}")
            emit('room_left', {'room': room})
            
        except Exception as e:
            logger.error(f"Error leaving room: {e}")
            emit('error', {'message': 'Failed to leave room'})
    
    @socketio.on('subscribe_telemetry')
    def handle_subscribe_telemetry(data):
        """Handle telemetry subscription."""
        try:
            client_id = request.sid
            telemetry_subscriptions.add(client_id)
            
            # Send current telemetry immediately
            from .telemetry import generate_mock_telemetry
            current_telemetry = generate_mock_telemetry()
            emit('telemetry_update', current_telemetry)
            
            logger.info(f"Client {client_id} subscribed to telemetry")
            emit('subscription_status', {
                'type': 'telemetry',
                'status': 'subscribed'
            })
            
        except Exception as e:
            logger.error(f"Error subscribing to telemetry: {e}")
            emit('error', {'message': 'Failed to subscribe to telemetry'})
    
    @socketio.on('unsubscribe_telemetry')
    def handle_unsubscribe_telemetry():
        """Handle telemetry unsubscription."""
        try:
            client_id = request.sid
            telemetry_subscriptions.discard(client_id)
            
            logger.info(f"Client {client_id} unsubscribed from telemetry")
            emit('subscription_status', {
                'type': 'telemetry',
                'status': 'unsubscribed'
            })
            
        except Exception as e:
            logger.error(f"Error unsubscribing from telemetry: {e}")
            emit('error', {'message': 'Failed to unsubscribe from telemetry'})
    
    @socketio.on('subscribe_video')
    def handle_subscribe_video(data):
        """Handle video stream subscription."""
        try:
            client_id = request.sid
            video_subscriptions.add(client_id)
            
            logger.info(f"Client {client_id} subscribed to video stream")
            emit('subscription_status', {
                'type': 'video',
                'status': 'subscribed'
            })
            
        except Exception as e:
            logger.error(f"Error subscribing to video stream: {e}")
            emit('error', {'message': 'Failed to subscribe to video stream'})
    
    @socketio.on('unsubscribe_video')
    def handle_unsubscribe_video():
        """Handle video stream unsubscription."""
        try:
            client_id = request.sid
            video_subscriptions.discard(client_id)
            
            logger.info(f"Client {client_id} unsubscribed from video stream")
            emit('subscription_status', {
                'type': 'video',
                'status': 'unsubscribed'
            })
            
        except Exception as e:
            logger.error(f"Error unsubscribing from video stream: {e}")
            emit('error', {'message': 'Failed to unsubscribe from video stream'})
    
    @socketio.on('drone_command')
    def handle_drone_command(data):
        """Handle drone control commands."""
        try:
            command = data.get('command')
            params = data.get('params', {})
            
            if not command:
                emit('error', {'message': 'Command required'})
                return
            
            # TODO: Integrate with actual drone control system
            # For now, simulate command execution
            result = {
                'command': command,
                'params': params,
                'status': 'success',
                'message': f'Command {command} executed successfully',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Drone command executed: {command} with params: {params}")
            emit('command_result', result)
            
            # Broadcast command to all clients in drone_control room
            socketio.emit('drone_command_broadcast', {
                'command': command,
                'params': params,
                'executed_by': request.sid,
                'timestamp': datetime.now().isoformat()
            }, room='drone_control')
            
        except Exception as e:
            logger.error(f"Error handling drone command: {e}")
            emit('error', {'message': 'Failed to execute drone command'})
    
    @socketio.on('mission_command')
    def handle_mission_command(data):
        """Handle mission control commands."""
        try:
            command = data.get('command')
            mission_id = data.get('mission_id')
            params = data.get('params', {})
            
            if not command:
                emit('error', {'message': 'Command required'})
                return
            
            # TODO: Integrate with actual mission system
            result = {
                'command': command,
                'mission_id': mission_id,
                'params': params,
                'status': 'success',
                'message': f'Mission command {command} executed successfully',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Mission command executed: {command} for mission: {mission_id}")
            emit('mission_result', result)
            
        except Exception as e:
            logger.error(f"Error handling mission command: {e}")
            emit('error', {'message': 'Failed to execute mission command'})
    
    @socketio.on('emergency_stop')
    def handle_emergency_stop(data):
        """Handle emergency stop command."""
        try:
            reason = data.get('reason', 'Emergency stop requested')
            
            # TODO: Integrate with actual emergency stop system
            result = {
                'command': 'emergency_stop',
                'reason': reason,
                'status': 'executed',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.warning(f"Emergency stop executed: {reason}")
            
            # Broadcast emergency stop to all connected clients
            socketio.emit('emergency_stop_broadcast', result)
            emit('emergency_stop_result', result)
            
        except Exception as e:
            logger.error(f"Error handling emergency stop: {e}")
            emit('error', {'message': 'Failed to execute emergency stop'})
    
    @socketio.on('request_status')
    def handle_request_status():
        """Handle status request."""
        try:
            # TODO: Get actual system status
            status = {
                'drone': {
                    'armed': False,
                    'flying': False,
                    'mode': 'STABILIZE',
                    'battery': 85,
                    'gps_fix': True
                },
                'systems': {
                    'flight_controller': 'connected',
                    'camera': 'active',
                    'gps': 'active',
                    'telemetry': 'active'
                },
                'mission': {
                    'active': False,
                    'current_mission': None,
                    'waypoint_progress': 0
                },
                'video': {
                    'streaming': True,
                    'recording': False,
                    'fps': 30,
                    'resolution': '1920x1080'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            emit('status_update', status)
            
        except Exception as e:
            logger.error(f"Error handling status request: {e}")
            emit('error', {'message': 'Failed to get status'})

def start_telemetry_broadcast(socketio):
    """Start broadcasting telemetry data to subscribed clients."""
    def telemetry_worker():
        """Worker function to broadcast telemetry data."""
        while True:
            try:
                if telemetry_subscriptions:
                    from .telemetry import generate_mock_telemetry
                    telemetry_data = generate_mock_telemetry()
                    
                    # Broadcast to all subscribed clients
                    for client_id in list(telemetry_subscriptions):
                        try:
                            socketio.emit('telemetry_update', telemetry_data, room=client_id)
                        except Exception as e:
                            logger.error(f"Error sending telemetry to client {client_id}: {e}")
                            telemetry_subscriptions.discard(client_id)
                
                time.sleep(1)  # Send telemetry every second
                
            except Exception as e:
                logger.error(f"Error in telemetry broadcast: {e}")
                time.sleep(5)  # Wait before retrying
    
    # Start telemetry broadcast thread
    telemetry_thread = threading.Thread(target=telemetry_worker, daemon=True)
    telemetry_thread.start()

def start_video_broadcast(socketio):
    """Start broadcasting video frames to subscribed clients."""
    def video_worker():
        """Worker function to broadcast video frames."""
        while True:
            try:
                if video_subscriptions:
                    # TODO: Get actual video frame
                    # For now, send mock frame data
                    frame_data = {
                        'timestamp': datetime.now().isoformat(),
                        'frame_number': int(time.time() * 30) % 10000,
                        'format': 'jpeg',
                        'width': 1920,
                        'height': 1080,
                        # In production, this would be base64-encoded image data
                        'data': 'mock_frame_data'
                    }
                    
                    # Broadcast to all subscribed clients
                    for client_id in list(video_subscriptions):
                        try:
                            socketio.emit('video_frame', frame_data, room=client_id)
                        except Exception as e:
                            logger.error(f"Error sending video frame to client {client_id}: {e}")
                            video_subscriptions.discard(client_id)
                
                time.sleep(1/30)  # 30 FPS
                
            except Exception as e:
                logger.error(f"Error in video broadcast: {e}")
                time.sleep(1)  # Wait before retrying
    
    # Start video broadcast thread
    video_thread = threading.Thread(target=video_worker, daemon=True)
    video_thread.start()

def broadcast_system_alert(socketio, alert_data):
    """Broadcast system alert to all connected clients."""
    try:
        alert = {
            'type': 'system_alert',
            'severity': alert_data.get('severity', 'info'),
            'title': alert_data.get('title', 'System Alert'),
            'message': alert_data.get('message', ''),
            'timestamp': datetime.now().isoformat(),
            'source': alert_data.get('source', 'system')
        }
        
        socketio.emit('system_alert', alert)
        logger.info(f"System alert broadcasted: {alert['title']}")
        
    except Exception as e:
        logger.error(f"Error broadcasting system alert: {e}")

def broadcast_mission_update(socketio, mission_data):
    """Broadcast mission status update to all connected clients."""
    try:
        update = {
            'type': 'mission_update',
            'mission_id': mission_data.get('mission_id'),
            'status': mission_data.get('status'),
            'progress': mission_data.get('progress', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        socketio.emit('mission_update', update, room='mission_control')
        logger.info(f"Mission update broadcasted: {mission_data.get('mission_id')}")
        
    except Exception as e:
        logger.error(f"Error broadcasting mission update: {e}")

def get_connection_stats():
    """Get statistics about active connections."""
    return {
        'total_connections': len(active_connections),
        'telemetry_subscribers': len(telemetry_subscriptions),
        'video_subscribers': len(video_subscriptions),
        'active_rooms': ['drone_control', 'mission_control', 'telemetry', 'video']
    }
