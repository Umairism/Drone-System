"""
Flight Controller Module
Handles communication with the flight controller via MAVLink protocol.
"""

import asyncio
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
import math

try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
except ImportError:
    MAVLINK_AVAILABLE = False
    logging.warning("PyMAVLink not available. Using mock implementation.")

logger = logging.getLogger(__name__)

class DroneController:
    """Flight controller interface using MAVLink protocol."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 57600):
        """Initialize the drone controller.
        
        Args:
            port: Serial port for MAVLink communication
            baudrate: Communication baudrate
        """
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.armed = False
        self.flying = False
        self.home_position = None
        self.current_position = {"lat": 0, "lng": 0, "alt": 0}
        self.telemetry_data = {}
        self.mock_mode = not MAVLINK_AVAILABLE
        
        logger.info(f"Initialized DroneController on {port} at {baudrate} baud")
    
    async def start(self):
        """Start the flight controller connection."""
        try:
            if self.mock_mode:
                await self._start_mock_mode()
            else:
                await self._start_mavlink_connection()
            
            # Start telemetry update loop
            asyncio.create_task(self._telemetry_loop())
            
        except Exception as e:
            logger.error(f"Failed to start flight controller: {e}")
            raise
    
    async def _start_mavlink_connection(self):
        """Start MAVLink connection to flight controller."""
        try:
            self.connection = mavutil.mavlink_connection(
                self.port, baud=self.baudrate, timeout=10
            )
            
            # Wait for heartbeat
            logger.info("Waiting for heartbeat...")
            self.connection.wait_heartbeat()
            logger.info("Heartbeat received - connected to flight controller")
            
            # Request data streams
            self.connection.mav.request_data_stream_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10,  # 10 Hz
                1    # Enable
            )
            
        except Exception as e:
            logger.error(f"Failed to connect to flight controller: {e}")
            self.mock_mode = True
            await self._start_mock_mode()
    
    async def _start_mock_mode(self):
        """Start in mock mode for testing without hardware."""
        logger.info("Starting in mock mode - no hardware required")
        self.current_position = {
            "lat": 33.6844,
            "lng": 73.0479,
            "alt": 10
        }
        self.home_position = self.current_position.copy()
    
    async def _telemetry_loop(self):
        """Continuous telemetry update loop."""
        while True:
            try:
                await self._update_telemetry()
                await asyncio.sleep(0.1)  # 10 Hz updates
            except Exception as e:
                logger.error(f"Error in telemetry loop: {e}")
                await asyncio.sleep(1)
    
    async def _update_telemetry(self):
        """Update telemetry data from flight controller."""
        if self.mock_mode:
            await self._update_mock_telemetry()
        else:
            await self._update_mavlink_telemetry()
    
    async def _update_mock_telemetry(self):
        """Update mock telemetry data for testing."""
        import random
        
        self.telemetry_data = {
            "timestamp": datetime.now().isoformat(),
            "armed": self.armed,
            "flying": self.flying,
            "position": self.current_position,
            "attitude": {
                "roll": random.uniform(-5, 5),
                "pitch": random.uniform(-5, 5),
                "yaw": random.uniform(0, 360)
            },
            "velocity": {
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-2, 2),
                "vz": random.uniform(-1, 1)
            },
            "battery": {
                "voltage": random.uniform(11.0, 12.6),
                "current": random.uniform(0, 30),
                "remaining": random.uniform(20, 100)
            },
            "gps": {
                "fix_type": 3,
                "satellites": random.randint(8, 12),
                "hdop": random.uniform(0.8, 1.5)
            },
            "mode": "GUIDED" if self.armed else "STABILIZE"
        }
    
    async def _update_mavlink_telemetry(self):
        """Update telemetry from MAVLink messages."""
        if not self.connection:
            return
        
        try:
            # Process available messages
            msg = self.connection.recv_match(blocking=False)
            if msg:
                msg_type = msg.get_type()
                
                if msg_type == 'HEARTBEAT':
                    self.armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                    
                elif msg_type == 'GLOBAL_POSITION_INT':
                    self.current_position = {
                        "lat": msg.lat / 1e7,
                        "lng": msg.lon / 1e7,
                        "alt": msg.alt / 1000.0
                    }
                    
                elif msg_type == 'ATTITUDE':
                    self.telemetry_data.update({
                        "attitude": {
                            "roll": math.degrees(msg.roll),
                            "pitch": math.degrees(msg.pitch),
                            "yaw": math.degrees(msg.yaw)
                        }
                    })
                
                elif msg_type == 'VFR_HUD':
                    self.telemetry_data.update({
                        "velocity": {
                            "ground_speed": msg.groundspeed,
                            "air_speed": msg.airspeed,
                            "climb_rate": msg.climb
                        }
                    })
                
                elif msg_type == 'SYS_STATUS':
                    self.telemetry_data.update({
                        "battery": {
                            "voltage": msg.voltage_battery / 1000.0,
                            "current": msg.current_battery / 100.0,
                            "remaining": msg.battery_remaining
                        }
                    })
                
        except Exception as e:
            logger.error(f"Error updating MAVLink telemetry: {e}")
    
    async def arm(self) -> bool:
        """Arm the drone motors.
        
        Returns:
            bool: Success status
        """
        try:
            if self.mock_mode:
                self.armed = True
                logger.info("Drone armed (mock mode)")
                return True
            
            # Send arm command
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 1, 0, 0, 0, 0, 0, 0
            )
            
            # Wait for confirmation
            await asyncio.sleep(2)
            return self.armed
            
        except Exception as e:
            logger.error(f"Failed to arm drone: {e}")
            return False
    
    async def disarm(self) -> bool:
        """Disarm the drone motors.
        
        Returns:
            bool: Success status
        """
        try:
            if self.mock_mode:
                self.armed = False
                self.flying = False
                logger.info("Drone disarmed (mock mode)")
                return True
            
            # Send disarm command
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 0, 0, 0, 0, 0, 0, 0
            )
            
            await asyncio.sleep(2)
            return not self.armed
            
        except Exception as e:
            logger.error(f"Failed to disarm drone: {e}")
            return False
    
    async def takeoff(self, altitude: float = 10.0) -> bool:
        """Take off to specified altitude.
        
        Args:
            altitude: Target altitude in meters
            
        Returns:
            bool: Success status
        """
        try:
            if not self.armed:
                logger.error("Cannot takeoff - drone not armed")
                return False
            
            if self.mock_mode:
                self.flying = True
                self.current_position["alt"] = altitude
                logger.info(f"Taking off to {altitude}m (mock mode)")
                return True
            
            # Send takeoff command
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                0, 0, 0, 0, 0, 0, 0, altitude
            )
            
            self.flying = True
            logger.info(f"Taking off to {altitude}m")
            return True
            
        except Exception as e:
            logger.error(f"Failed to takeoff: {e}")
            return False
    
    async def land(self) -> bool:
        """Land the drone.
        
        Returns:
            bool: Success status
        """
        try:
            if self.mock_mode:
                self.flying = False
                self.current_position["alt"] = 0
                logger.info("Landing (mock mode)")
                return True
            
            # Send land command
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0, 0, 0, 0, 0, 0, 0, 0
            )
            
            logger.info("Landing initiated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to land: {e}")
            return False
    
    async def goto_position(self, lat: float, lng: float, alt: float = None) -> bool:
        """Go to specified GPS position.
        
        Args:
            lat: Target latitude
            lng: Target longitude  
            alt: Target altitude (optional)
            
        Returns:
            bool: Success status
        """
        try:
            if alt is None:
                alt = self.current_position["alt"]
            
            if self.mock_mode:
                self.current_position = {"lat": lat, "lng": lng, "alt": alt}
                logger.info(f"Going to position: {lat}, {lng}, {alt}m (mock mode)")
                return True
            
            # Send goto command
            self.connection.mav.mission_item_send(
                self.connection.target_system,
                self.connection.target_component,
                0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                2, 1, 0, 0, 0, 0, lat, lng, alt
            )
            
            logger.info(f"Going to position: {lat}, {lng}, {alt}m")
            return True
            
        except Exception as e:
            logger.error(f"Failed to go to position: {e}")
            return False
    
    async def set_home_position(self, lat: float = None, lng: float = None, alt: float = None):
        """Set home position for return-to-home functionality.
        
        Args:
            lat: Home latitude (current position if None)
            lng: Home longitude (current position if None)
            alt: Home altitude (current position if None)
        """
        if lat is None:
            lat = self.current_position["lat"]
        if lng is None:
            lng = self.current_position["lng"]
        if alt is None:
            alt = self.current_position["alt"]
        
        self.home_position = {"lat": lat, "lng": lng, "alt": alt}
        logger.info(f"Home position set to: {lat}, {lng}, {alt}m")
    
    async def return_to_home(self) -> bool:
        """Return to home position.
        
        Returns:
            bool: Success status
        """
        if not self.home_position:
            logger.error("Home position not set")
            return False
        
        return await self.goto_position(
            self.home_position["lat"],
            self.home_position["lng"],
            self.home_position["alt"]
        )
    
    async def get_telemetry(self) -> Dict:
        """Get current telemetry data.
        
        Returns:
            Dict: Current telemetry data
        """
        return self.telemetry_data.copy()
    
    async def update_position(self, gps_data: Dict):
        """Update position from GPS data.
        
        Args:
            gps_data: GPS data dictionary
        """
        if gps_data and 'latitude' in gps_data and 'longitude' in gps_data:
            self.current_position.update({
                "lat": gps_data['latitude'],
                "lng": gps_data['longitude']
            })
            if 'altitude' in gps_data:
                self.current_position["alt"] = gps_data['altitude']
    
    async def is_healthy(self) -> bool:
        """Check if the flight controller is healthy.
        
        Returns:
            bool: Health status
        """
        try:
            if self.mock_mode:
                return True
            
            # Check connection and recent telemetry
            return (self.connection is not None and 
                    self.telemetry_data and
                    'timestamp' in self.telemetry_data)
                    
        except Exception:
            return False
    
    async def stop(self):
        """Stop the flight controller and close connections."""
        try:
            if self.connection:
                self.connection.close()
            logger.info("Flight controller stopped")
        except Exception as e:
            logger.error(f"Error stopping flight controller: {e}")
