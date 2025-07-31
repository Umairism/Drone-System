"""
Communication Manager Module
Handles real-time communication between drone and ground station.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import socketio
from aiohttp import web
from aiohttp_cors import setup as cors_setup, ResourceOptions

logger = logging.getLogger(__name__)

class CommunicationManager:
    """Manages real-time communication via WebSocket and HTTP API."""
    
    def __init__(self, port: int = 5001):
        """Initialize communication manager.
        
        Args:
            port: Port for the communication server
        """
        self.port = port
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            async_mode='aiohttp'
        )
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # Connected clients
        self.connected_clients = {}
        self.client_subscriptions = {}
        
        # Message queues for different data types
        self.telemetry_queue = asyncio.Queue(maxsize=100)
        self.video_queue = asyncio.Queue(maxsize=10)
        self.detection_queue = asyncio.Queue(maxsize=50)
        self.alert_queue = asyncio.Queue(maxsize=20)
        
        # Setup routes and events
        self._setup_socket_events()
        self._setup_http_routes()
        
        logger.info(f"Initialized CommunicationManager on port {port}")
    
    def _setup_socket_events(self):
        """Setup WebSocket event handlers."""
        
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            self.connected_clients[sid] = {
                'connected_at': datetime.now(),
                'remote_addr': environ.get('REMOTE_ADDR', 'unknown'),
                'user_agent': environ.get('HTTP_USER_AGENT', 'unknown')
            }
            
            self.client_subscriptions[sid] = {
                'telemetry': True,
                'video': True,
                'detections': True,
                'alerts': True
            }
            
            logger.info(f"Client connected: {sid} from {self.connected_clients[sid]['remote_addr']}")
            
            # Send initial system status
            await self.sio.emit('system_status', {
                'status': 'connected',
                'timestamp': datetime.now().isoformat(),
                'server_info': {
                    'version': '1.0.0',
                    'capabilities': ['telemetry', 'video', 'detections', 'control']
                }
            }, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            client_info = self.connected_clients.pop(sid, {})
            self.client_subscriptions.pop(sid, {})
            
            logger.info(f"Client disconnected: {sid}")
        
        @self.sio.event
        async def subscribe(sid, data):
            """Handle subscription updates."""
            try:
                if sid in self.client_subscriptions:
                    self.client_subscriptions[sid].update(data.get('subscriptions', {}))
                    
                await self.sio.emit('subscription_updated', {
                    'subscriptions': self.client_subscriptions[sid],
                    'timestamp': datetime.now().isoformat()
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Error handling subscription: {e}")
        
        @self.sio.event
        async def drone_command(sid, data):
            """Handle drone control commands."""
            try:
                command = data.get('command')
                params = data.get('parameters', {})
                
                logger.info(f"Received drone command: {command} from {sid}")
                
                # Emit command to drone control system
                # This would integrate with the flight controller
                response = await self._handle_drone_command(command, params)
                
                await self.sio.emit('command_response', {
                    'command': command,
                    'success': response.get('success', False),
                    'message': response.get('message', ''),
                    'timestamp': datetime.now().isoformat()
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Error handling drone command: {e}")
                await self.sio.emit('command_response', {
                    'command': data.get('command'),
                    'success': False,
                    'message': f"Command failed: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }, room=sid)
        
        @self.sio.event
        async def request_data(sid, data):
            """Handle data requests."""
            try:
                data_type = data.get('type')
                
                if data_type == 'system_status':
                    status = await self._get_system_status()
                    await self.sio.emit('system_status', status, room=sid)
                
                elif data_type == 'telemetry':
                    # Send latest telemetry if available
                    pass
                
                elif data_type == 'mission_list':
                    missions = await self._get_missions()
                    await self.sio.emit('mission_list', missions, room=sid)
                
            except Exception as e:
                logger.error(f"Error handling data request: {e}")
    
    def _setup_http_routes(self):
        """Setup HTTP API routes."""
        
        # CORS setup
        cors = cors_setup(self.app, defaults={
            "*": ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # API routes
        self.app.router.add_get('/api/status', self._handle_status)
        self.app.router.add_get('/api/telemetry', self._handle_get_telemetry)
        self.app.router.add_post('/api/command', self._handle_post_command)
        self.app.router.add_get('/api/missions', self._handle_get_missions)
        self.app.router.add_post('/api/missions', self._handle_post_mission)
        self.app.router.add_get('/api/detections', self._handle_get_detections)
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
        
        # Attach socketio
        self.sio.attach(self.app)
    
    async def _handle_status(self, request):
        """Handle status API request."""
        try:
            status = await self._get_system_status()
            return web.json_response(status)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_get_telemetry(self, request):
        """Handle telemetry API request."""
        try:
            # Return latest telemetry data
            return web.json_response({
                'telemetry': {},  # Placeholder
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_post_command(self, request):
        """Handle command API request."""
        try:
            data = await request.json()
            command = data.get('command')
            params = data.get('parameters', {})
            
            response = await self._handle_drone_command(command, params)
            return web.json_response(response)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_get_missions(self, request):
        """Handle missions list API request."""
        try:
            missions = await self._get_missions()
            return web.json_response(missions)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_post_mission(self, request):
        """Handle create mission API request."""
        try:
            mission_data = await request.json()
            result = await self._create_mission(mission_data)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_get_detections(self, request):
        """Handle detections API request."""
        try:
            # Return recent detections
            return web.json_response({
                'detections': [],  # Placeholder
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def _handle_drone_command(self, command: str, params: Dict) -> Dict:
        """Handle drone control commands.
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            Dict: Command response
        """
        # This would interface with the actual flight controller
        # For now, return mock responses
        
        if command == 'arm':
            return {'success': True, 'message': 'Drone armed successfully'}
        elif command == 'disarm':
            return {'success': True, 'message': 'Drone disarmed successfully'}
        elif command == 'takeoff':
            altitude = params.get('altitude', 10)
            return {'success': True, 'message': f'Taking off to {altitude}m'}
        elif command == 'land':
            return {'success': True, 'message': 'Landing initiated'}
        elif command == 'goto':
            lat = params.get('latitude')
            lng = params.get('longitude')
            alt = params.get('altitude', 10)
            return {'success': True, 'message': f'Going to {lat}, {lng} at {alt}m'}
        elif command == 'return_home':
            return {'success': True, 'message': 'Returning to home'}
        else:
            return {'success': False, 'message': f'Unknown command: {command}'}
    
    async def _get_system_status(self) -> Dict:
        """Get system status information."""
        return {
            'status': 'operational',
            'connected_clients': len(self.connected_clients),
            'uptime': '00:00:00',  # Placeholder
            'version': '1.0.0',
            'capabilities': {
                'video_streaming': True,
                'object_detection': True,
                'gps_tracking': True,
                'flight_control': True
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def _get_missions(self) -> Dict:
        """Get missions list."""
        # Placeholder - would load from database
        return {
            'missions': [],
            'count': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _create_mission(self, mission_data: Dict) -> Dict:
        """Create a new mission."""
        # Placeholder - would save to database
        return {
            'success': True,
            'mission_id': 'mission_123',
            'message': 'Mission created successfully'
        }
    
    async def start(self):
        """Start the communication server."""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            
            # Start message broadcast loops
            asyncio.create_task(self._telemetry_broadcast_loop())
            asyncio.create_task(self._video_broadcast_loop())
            asyncio.create_task(self._detection_broadcast_loop())
            asyncio.create_task(self._alert_broadcast_loop())
            
            logger.info(f"Communication server started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start communication server: {e}")
            raise
    
    async def _telemetry_broadcast_loop(self):
        """Broadcast telemetry data to connected clients."""
        while True:
            try:
                if not self.telemetry_queue.empty():
                    telemetry_data = await self.telemetry_queue.get()
                    
                    # Broadcast to subscribed clients
                    for sid, subscriptions in self.client_subscriptions.items():
                        if subscriptions.get('telemetry', False):
                            await self.sio.emit('telemetry_update', telemetry_data, room=sid)
                
                await asyncio.sleep(0.1)  # 10Hz telemetry updates
                
            except Exception as e:
                logger.error(f"Error in telemetry broadcast: {e}")
                await asyncio.sleep(1)
    
    async def _video_broadcast_loop(self):
        """Broadcast video frames to connected clients."""
        while True:
            try:
                if not self.video_queue.empty():
                    video_data = await self.video_queue.get()
                    
                    # Broadcast to subscribed clients
                    for sid, subscriptions in self.client_subscriptions.items():
                        if subscriptions.get('video', False):
                            await self.sio.emit('video_frame', video_data, room=sid)
                
                await asyncio.sleep(1/30)  # 30 FPS video updates
                
            except Exception as e:
                logger.error(f"Error in video broadcast: {e}")
                await asyncio.sleep(1)
    
    async def _detection_broadcast_loop(self):
        """Broadcast detection results to connected clients."""
        while True:
            try:
                if not self.detection_queue.empty():
                    detection_data = await self.detection_queue.get()
                    
                    # Broadcast to subscribed clients
                    for sid, subscriptions in self.client_subscriptions.items():
                        if subscriptions.get('detections', False):
                            await self.sio.emit('detection_update', detection_data, room=sid)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in detection broadcast: {e}")
                await asyncio.sleep(1)
    
    async def _alert_broadcast_loop(self):
        """Broadcast alerts to connected clients."""
        while True:
            try:
                if not self.alert_queue.empty():
                    alert_data = await self.alert_queue.get()
                    
                    # Broadcast alerts to all clients
                    await self.sio.emit('system_alert', alert_data)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in alert broadcast: {e}")
                await asyncio.sleep(1)
    
    async def broadcast_telemetry(self, telemetry_data: Dict):
        """Add telemetry data to broadcast queue.
        
        Args:
            telemetry_data: Telemetry data to broadcast
        """
        try:
            if not self.telemetry_queue.full():
                await self.telemetry_queue.put(telemetry_data)
        except Exception as e:
            logger.error(f"Error queuing telemetry: {e}")
    
    async def broadcast_video_frame(self, frame_data: str):
        """Add video frame to broadcast queue.
        
        Args:
            frame_data: Base64 encoded video frame
        """
        try:
            video_message = {
                'frame': frame_data,
                'timestamp': datetime.now().isoformat(),
                'format': 'jpeg'
            }
            
            if not self.video_queue.full():
                await self.video_queue.put(video_message)
        except Exception as e:
            logger.error(f"Error queuing video frame: {e}")
    
    async def broadcast_detections(self, detections: List[Dict]):
        """Add detection results to broadcast queue.
        
        Args:
            detections: List of detection dictionaries
        """
        try:
            detection_message = {
                'detections': detections,
                'count': len(detections),
                'timestamp': datetime.now().isoformat()
            }
            
            if not self.detection_queue.full():
                await self.detection_queue.put(detection_message)
        except Exception as e:
            logger.error(f"Error queuing detections: {e}")
    
    async def send_alert(self, alert_type: str, message: str, severity: int = 1):
        """Send system alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (1-5)
        """
        try:
            alert_data = {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            
            if not self.alert_queue.full():
                await self.alert_queue.put(alert_data)
                
            logger.warning(f"Alert sent: {alert_type} - {message}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_connected_clients(self) -> Dict:
        """Get information about connected clients.
        
        Returns:
            Dict: Connected clients information
        """
        return {
            'count': len(self.connected_clients),
            'clients': self.connected_clients.copy()
        }
    
    async def is_healthy(self) -> bool:
        """Check if communication manager is healthy.
        
        Returns:
            bool: Health status
        """
        return self.runner is not None and self.site is not None
    
    async def stop(self):
        """Stop the communication server."""
        try:
            if self.site:
                await self.site.stop()
            
            if self.runner:
                await self.runner.cleanup()
            
            logger.info("Communication server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping communication server: {e}")
