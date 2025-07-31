"""
Dynamic Data Manager
Generates realistic, time-based dynamic data for the surveillance drone system.
"""

import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading
import json

class DroneDataManager:
    """Manages dynamic drone data simulation."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.base_position = {'lat': 33.6844, 'lng': 73.0479, 'alt': 0}
        self.current_position = self.base_position.copy()
        self.mission_active = False
        self.flight_time = 0
        self.battery_drain_rate = 0.1  # % per minute
        self.initial_battery = 100
        self.armed = False
        self.flying = False
        self.mode = 'STABILIZE'
        self.speed = 0
        self.heading = 0
        self.mission_waypoints = []
        self.current_waypoint = 0
        self.alerts = []
        
        # Start background thread for continuous updates
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def _update_loop(self):
        """Background thread to continuously update drone data."""
        while self.running:
            if self.flying:
                self._update_flight_data()
            self._update_system_data()
            time.sleep(1)  # Update every second
    
    def _update_flight_data(self):
        """Update flight-related data."""
        self.flight_time += 1
        
        # Simulate movement if mission is active
        if self.mission_active and self.mission_waypoints:
            self._simulate_mission_movement()
        else:
            # Random drift for realistic simulation
            self.current_position['lat'] += random.uniform(-0.00001, 0.00001)
            self.current_position['lng'] += random.uniform(-0.00001, 0.00001)
            self.current_position['alt'] += random.uniform(-0.5, 0.5)
        
        # Update heading and speed
        self.heading += random.uniform(-2, 2)
        self.heading = self.heading % 360
        
        if self.mission_active:
            self.speed = random.uniform(5, 15)
        else:
            self.speed = random.uniform(0, 3)
    
    def _simulate_mission_movement(self):
        """Simulate movement towards mission waypoints."""
        if self.current_waypoint < len(self.mission_waypoints):
            target = self.mission_waypoints[self.current_waypoint]
            
            # Calculate distance to target
            lat_diff = target['lat'] - self.current_position['lat']
            lng_diff = target['lng'] - self.current_position['lng']
            alt_diff = target['alt'] - self.current_position['alt']
            
            # Move towards target
            move_speed = 0.00005  # degrees per second
            if abs(lat_diff) > move_speed:
                self.current_position['lat'] += move_speed if lat_diff > 0 else -move_speed
            if abs(lng_diff) > move_speed:
                self.current_position['lng'] += move_speed if lng_diff > 0 else -move_speed
            if abs(alt_diff) > 1:
                self.current_position['alt'] += 1 if alt_diff > 0 else -1
            
            # Check if reached waypoint
            if (abs(lat_diff) < move_speed * 2 and 
                abs(lng_diff) < move_speed * 2 and 
                abs(alt_diff) < 2):
                self.current_waypoint += 1
                if self.current_waypoint >= len(self.mission_waypoints):
                    self.mission_active = False
                    self.add_alert("Mission completed successfully", "info")
    
    def _update_system_data(self):
        """Update system-related data."""
        # Battery drain
        if self.flying:
            drain = self.battery_drain_rate / 60  # per second
            self.initial_battery -= drain
            if self.initial_battery < 20 and not any(a['type'] == 'low_battery' for a in self.alerts):
                self.add_alert("Low battery warning", "warning", alert_type="low_battery")
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get current telemetry data."""
        uptime = datetime.now() - self.start_time
        
        return {
            'timestamp': datetime.now().isoformat(),
            'flight_data': {
                'armed': self.armed,
                'flying': self.flying,
                'mode': self.mode,
                'flight_time': self.flight_time,
                'position': {
                    'latitude': round(self.current_position['lat'], 8),
                    'longitude': round(self.current_position['lng'], 8),
                    'altitude': round(self.current_position['alt'], 2),
                    'relative_altitude': round(max(0, self.current_position['alt']), 2)
                },
                'attitude': {
                    'roll': random.uniform(-5, 5),
                    'pitch': random.uniform(-5, 5),
                    'yaw': round(self.heading, 2)
                },
                'velocity': {
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'vz': random.uniform(-1, 1),
                    'ground_speed': round(self.speed, 2)
                }
            },
            'sensor_data': {
                'gps': {
                    'fix_type': 3 if self.flying else 2,
                    'satellites': random.randint(8, 12) if self.flying else random.randint(4, 8),
                    'hdop': round(random.uniform(0.8, 1.5), 2),
                    'vdop': round(random.uniform(1.0, 2.0), 2)
                },
                'battery': {
                    'voltage': round(11.1 + (self.initial_battery / 100) * 1.5, 2),
                    'current': round(random.uniform(8, 25) if self.flying else random.uniform(2, 8), 2),
                    'remaining': max(0, round(self.initial_battery, 1)),
                    'capacity': 5000
                },
                'rc': {
                    'rssi': random.randint(70, 100) if self.flying else random.randint(50, 90),
                    'channels': [random.randint(1000, 2000) for _ in range(8)]
                }
            },
            'system_status': {
                'cpu_usage': round(random.uniform(30, 80), 1),
                'memory_usage': round(random.uniform(40, 90), 1),
                'temperature': round(random.uniform(25, 45), 1),
                'uptime': str(uptime).split('.')[0]
            }
        }
    
    def get_drone_status(self) -> Dict[str, Any]:
        """Get current drone status."""
        return {
            'armed': self.armed,
            'flying': self.flying,
            'mode': self.mode,
            'position': {
                'lat': round(self.current_position['lat'], 8),
                'lng': round(self.current_position['lng'], 8),
                'alt': round(self.current_position['alt'], 2)
            },
            'battery': {
                'percentage': max(0, round(self.initial_battery, 1)),
                'voltage': round(11.1 + (self.initial_battery / 100) * 1.5, 2),
                'current': round(random.uniform(8, 25) if self.flying else random.uniform(2, 8), 2)
            },
            'sensors': {
                'gps_satellites': random.randint(8, 12) if self.flying else random.randint(4, 8),
                'gps_hdop': round(random.uniform(0.8, 1.5), 2),
                'compass_heading': round(self.heading, 1)
            },
            'mission': {
                'active': self.mission_active,
                'current_waypoint': self.current_waypoint,
                'total_waypoints': len(self.mission_waypoints)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def arm_drone(self) -> Dict[str, Any]:
        """Arm the drone."""
        if self.initial_battery < 15:
            return {'success': False, 'message': 'Battery too low to arm'}
        
        self.armed = True
        self.mode = 'GUIDED'
        self.add_alert("Drone armed successfully", "info")
        return {'success': True, 'message': 'Drone armed successfully'}
    
    def disarm_drone(self) -> Dict[str, Any]:
        """Disarm the drone."""
        if self.flying:
            return {'success': False, 'message': 'Cannot disarm while flying'}
        
        self.armed = False
        self.mode = 'STABILIZE'
        self.add_alert("Drone disarmed", "info")
        return {'success': True, 'message': 'Drone disarmed successfully'}
    
    def takeoff(self, altitude: float = 10) -> Dict[str, Any]:
        """Takeoff to specified altitude."""
        if not self.armed:
            return {'success': False, 'message': 'Drone must be armed first'}
        
        self.flying = True
        self.current_position['alt'] = altitude
        self.mode = 'GUIDED'
        self.add_alert(f"Takeoff to {altitude}m initiated", "info")
        return {'success': True, 'message': f'Taking off to {altitude}m'}
    
    def land(self) -> Dict[str, Any]:
        """Land the drone."""
        if not self.flying:
            return {'success': False, 'message': 'Drone is not flying'}
        
        self.flying = False
        self.current_position['alt'] = 0
        self.speed = 0
        self.mission_active = False
        self.add_alert("Landing initiated", "info")
        return {'success': True, 'message': 'Landing initiated'}
    
    def goto_position(self, lat: float, lng: float, alt: float) -> Dict[str, Any]:
        """Navigate to specified position."""
        if not self.flying:
            return {'success': False, 'message': 'Drone must be flying'}
        
        # Calculate distance
        distance = self._calculate_distance(
            self.current_position['lat'], self.current_position['lng'],
            lat, lng
        )
        
        # Set as single waypoint mission
        self.mission_waypoints = [{'lat': lat, 'lng': lng, 'alt': alt}]
        self.current_waypoint = 0
        self.mission_active = True
        
        return {'success': True, 'message': f'Navigating to position (distance: {distance:.1f}m)'}
    
    def start_mission(self, waypoints: List[Dict]) -> Dict[str, Any]:
        """Start a mission with multiple waypoints."""
        if not self.flying:
            return {'success': False, 'message': 'Drone must be flying to start mission'}
        
        self.mission_waypoints = waypoints
        self.current_waypoint = 0
        self.mission_active = True
        self.add_alert(f"Mission started with {len(waypoints)} waypoints", "info")
        
        return {'success': True, 'message': f'Mission started with {len(waypoints)} waypoints'}
    
    def add_alert(self, message: str, severity: str = "info", alert_type: str = None):
        """Add system alert."""
        alert = {
            'id': len(self.alerts) + 1,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'type': alert_type or 'general'
        }
        self.alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts."""
        return self.alerts[-10:]  # Return last 10 alerts
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in meters."""
        # Simplified distance calculation
        lat_diff = (lat2 - lat1) * 111000  # roughly 111km per degree
        lng_diff = (lng2 - lng1) * 111000 * math.cos(math.radians(lat1))
        return math.sqrt(lat_diff**2 + lng_diff**2)

# Global instance
drone_data_manager = DroneDataManager()
