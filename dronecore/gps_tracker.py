"""
GPS Tracker Module
Handles GPS communication and location tracking.
"""

import asyncio
import logging
import serial
from typing import Dict, Optional, Tuple
from datetime import datetime
import math

try:
    import pynmea2
    PYNMEA2_AVAILABLE = True
except ImportError:
    PYNMEA2_AVAILABLE = False
    logging.warning("pynmea2 not available. Using mock GPS implementation.")

logger = logging.getLogger(__name__)

class GPSTracker:
    """GPS tracking and navigation functionality."""
    
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 9600, timeout: int = 5):
        """Initialize GPS tracker.
        
        Args:
            port: Serial port for GPS module
            baudrate: Communication baudrate
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.running = False
        self.mock_mode = not PYNMEA2_AVAILABLE
        
        # GPS data
        self.current_position = {
            'latitude': 0.0,
            'longitude': 0.0,
            'altitude': 0.0,
            'timestamp': None,
            'fix_quality': 0,
            'satellites': 0,
            'hdop': 0.0,
            'speed': 0.0,
            'course': 0.0
        }
        
        self.position_history = []
        self.waypoints = []
        
        logger.info(f"Initialized GPSTracker on {port} at {baudrate} baud")
    
    async def start(self):
        """Start GPS tracking."""
        try:
            if self.mock_mode:
                await self._start_mock_mode()
            else:
                await self._start_serial_connection()
            
            self.running = True
            
            # Start GPS reading loop
            asyncio.create_task(self._gps_loop())
            
        except Exception as e:
            logger.error(f"Failed to start GPS tracker: {e}")
            self.mock_mode = True
            await self._start_mock_mode()
    
    async def _start_serial_connection(self):
        """Start serial connection to GPS module."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            if self.serial_connection.is_open:
                logger.info(f"GPS serial connection established on {self.port}")
            else:
                raise Exception("Failed to open GPS serial connection")
                
        except Exception as e:
            logger.error(f"GPS serial connection failed: {e}")
            raise
    
    async def _start_mock_mode(self):
        """Start mock GPS mode for testing."""
        logger.info("Starting GPS tracker in mock mode")
        # Set mock position (Islamabad, Pakistan)
        self.current_position.update({
            'latitude': 33.6844,
            'longitude': 73.0479,
            'altitude': 500.0,
            'fix_quality': 1,
            'satellites': 8,
            'hdop': 1.2,
            'speed': 0.0,
            'course': 0.0
        })
    
    async def _gps_loop(self):
        """Main GPS reading loop."""
        while self.running:
            try:
                if self.mock_mode:
                    await self._update_mock_gps()
                else:
                    await self._read_nmea_data()
                
                await asyncio.sleep(0.1)  # 10Hz GPS updates
                
            except Exception as e:
                logger.error(f"Error in GPS loop: {e}")
                await asyncio.sleep(1)
    
    async def _update_mock_gps(self):
        """Update mock GPS data with simulated movement."""
        import random
        
        # Simulate small movements
        lat_offset = random.uniform(-0.0001, 0.0001)  # ~11m
        lng_offset = random.uniform(-0.0001, 0.0001)  # ~11m
        alt_offset = random.uniform(-1, 1)  # 1m
        
        base_lat = 33.6844
        base_lng = 73.0479
        base_alt = 500.0
        
        self.current_position.update({
            'latitude': base_lat + lat_offset,
            'longitude': base_lng + lng_offset,
            'altitude': base_alt + alt_offset,
            'timestamp': datetime.now(),
            'satellites': random.randint(6, 12),
            'hdop': random.uniform(0.8, 2.0),
            'speed': random.uniform(0, 5),  # m/s
            'course': random.uniform(0, 360)
        })
        
        # Add to history
        self._add_to_history()
    
    async def _read_nmea_data(self):
        """Read and parse NMEA data from GPS module."""
        if not self.serial_connection or not self.serial_connection.is_open:
            return
        
        try:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('ascii', errors='ignore')
                
                if line.startswith('$'):
                    msg = pynmea2.parse(line)
                    await self._process_nmea_message(msg)
                    
        except Exception as e:
            logger.error(f"Error reading NMEA data: {e}")
    
    async def _process_nmea_message(self, msg):
        """Process parsed NMEA message.
        
        Args:
            msg: Parsed NMEA message
        """
        try:
            if isinstance(msg, pynmea2.GGA):  # GPS Fix Data
                if msg.latitude and msg.longitude:
                    self.current_position.update({
                        'latitude': float(msg.latitude),
                        'longitude': float(msg.longitude),
                        'altitude': float(msg.altitude) if msg.altitude else 0.0,
                        'timestamp': datetime.now(),
                        'fix_quality': int(msg.gps_qual) if msg.gps_qual else 0,
                        'satellites': int(msg.num_sats) if msg.num_sats else 0,
                        'hdop': float(msg.horizontal_dil) if msg.horizontal_dil else 0.0
                    })
                    self._add_to_history()
            
            elif isinstance(msg, pynmea2.RMC):  # Recommended Minimum
                if msg.latitude and msg.longitude:
                    self.current_position.update({
                        'latitude': float(msg.latitude),
                        'longitude': float(msg.longitude),
                        'speed': float(msg.spd_over_grnd) * 0.514444 if msg.spd_over_grnd else 0.0,  # knots to m/s
                        'course': float(msg.true_course) if msg.true_course else 0.0,
                        'timestamp': datetime.now()
                    })
            
            elif isinstance(msg, pynmea2.GSA):  # GPS DOP and active satellites
                pass  # Additional satellite info if needed
                
        except Exception as e:
            logger.error(f"Error processing NMEA message: {e}")
    
    def _add_to_history(self):
        """Add current position to history."""
        position_entry = self.current_position.copy()
        self.position_history.append(position_entry)
        
        # Keep history limited to last 1000 points
        if len(self.position_history) > 1000:
            self.position_history.pop(0)
    
    async def get_position(self) -> Dict:
        """Get current GPS position.
        
        Returns:
            Dict: Current position data
        """
        return self.current_position.copy()
    
    def has_fix(self) -> bool:
        """Check if GPS has a valid fix.
        
        Returns:
            bool: True if GPS has valid fix
        """
        return (self.current_position['fix_quality'] > 0 or 
                (self.current_position['latitude'] != 0.0 and 
                 self.current_position['longitude'] != 0.0))
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two GPS coordinates using Haversine formula.
        
        Args:
            lat1, lng1: First coordinate
            lat2, lng2: Second coordinate
            
        Returns:
            float: Distance in meters
        """
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in meters
        r = 6371000
        
        return c * r
    
    def calculate_bearing(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate bearing between two GPS coordinates.
        
        Args:
            lat1, lng1: Starting coordinate
            lat2, lng2: Target coordinate
            
        Returns:
            float: Bearing in degrees (0-360)
        """
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        dlng = lng2 - lng1
        
        y = math.sin(dlng) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlng)
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        
        # Normalize to 0-360
        bearing = (bearing + 360) % 360
        
        return bearing
    
    async def add_waypoint(self, name: str, lat: float, lng: float, alt: float = 0) -> bool:
        """Add a waypoint.
        
        Args:
            name: Waypoint name
            lat: Latitude
            lng: Longitude
            alt: Altitude (optional)
            
        Returns:
            bool: Success status
        """
        try:
            waypoint = {
                'name': name,
                'latitude': lat,
                'longitude': lng,
                'altitude': alt,
                'timestamp': datetime.now()
            }
            
            self.waypoints.append(waypoint)
            logger.info(f"Added waypoint '{name}' at {lat}, {lng}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add waypoint: {e}")
            return False
    
    async def get_waypoints(self) -> list:
        """Get all waypoints.
        
        Returns:
            list: List of waypoints
        """
        return self.waypoints.copy()
    
    async def navigate_to_waypoint(self, waypoint_name: str) -> Optional[Dict]:
        """Get navigation info to a waypoint.
        
        Args:
            waypoint_name: Name of the waypoint
            
        Returns:
            Optional[Dict]: Navigation information
        """
        waypoint = next((wp for wp in self.waypoints if wp['name'] == waypoint_name), None)
        
        if not waypoint:
            logger.error(f"Waypoint '{waypoint_name}' not found")
            return None
        
        if not self.has_fix():
            logger.error("No GPS fix available for navigation")
            return None
        
        current_lat = self.current_position['latitude']
        current_lng = self.current_position['longitude']
        target_lat = waypoint['latitude']
        target_lng = waypoint['longitude']
        
        distance = self.calculate_distance(current_lat, current_lng, target_lat, target_lng)
        bearing = self.calculate_bearing(current_lat, current_lng, target_lat, target_lng)
        
        return {
            'waypoint': waypoint,
            'distance': distance,
            'bearing': bearing,
            'current_position': self.current_position.copy()
        }
    
    async def get_position_history(self, limit: int = 100) -> list:
        """Get position history.
        
        Args:
            limit: Maximum number of positions to return
            
        Returns:
            list: List of historical positions
        """
        return self.position_history[-limit:] if self.position_history else []
    
    async def get_gps_stats(self) -> Dict:
        """Get GPS statistics and health information.
        
        Returns:
            Dict: GPS statistics
        """
        return {
            'has_fix': self.has_fix(),
            'fix_quality': self.current_position['fix_quality'],
            'satellites': self.current_position['satellites'],
            'hdop': self.current_position['hdop'],
            'last_update': self.current_position['timestamp'].isoformat() if self.current_position['timestamp'] else None,
            'position_history_count': len(self.position_history),
            'waypoints_count': len(self.waypoints),
            'mock_mode': self.mock_mode
        }
    
    async def is_healthy(self) -> bool:
        """Check if GPS tracker is healthy.
        
        Returns:
            bool: Health status
        """
        if self.mock_mode:
            return True
        
        return (self.serial_connection and 
                self.serial_connection.is_open and 
                self.has_fix())
    
    async def stop(self):
        """Stop GPS tracker and cleanup resources."""
        try:
            self.running = False
            
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            
            logger.info("GPS tracker stopped")
            
        except Exception as e:
            logger.error(f"Error stopping GPS tracker: {e}")
