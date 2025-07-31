"""
Sensor Manager Module
Manages various sensors (ultrasonic, IMU, etc.) for the drone system.
"""

import asyncio
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime

# Try to import GPIO for Raspberry Pi
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available. Using mock sensor implementation.")

logger = logging.getLogger(__name__)

class SensorManager:
    """Manages all drone sensors."""
    
    def __init__(self):
        """Initialize sensor manager."""
        self.sensors = {}
        self.sensor_data = {}
        self.mock_mode = not GPIO_AVAILABLE
        self.running = False
        
        if not self.mock_mode:
            GPIO.setmode(GPIO.BCM)
        
        # Initialize sensors
        self._init_sensors()
        
        logger.info("Initialized SensorManager")
    
    def _init_sensors(self):
        """Initialize all sensors."""
        # Ultrasonic sensors for obstacle detection
        self.sensors['ultrasonic_front'] = {
            'type': 'ultrasonic',
            'trigger_pin': 18,
            'echo_pin': 24,
            'max_distance': 400  # cm
        }
        
        self.sensors['ultrasonic_back'] = {
            'type': 'ultrasonic', 
            'trigger_pin': 23,
            'echo_pin': 25,
            'max_distance': 400
        }
        
        # Temperature sensor
        self.sensors['temperature'] = {
            'type': 'temperature',
            'pin': 4,
            'sensor_type': 'DHT22'
        }
        
        # Battery voltage sensor (ADC)
        self.sensors['battery_voltage'] = {
            'type': 'voltage',
            'channel': 0,
            'voltage_divider_ratio': 11.0  # 10k/1k voltage divider
        }
        
        if not self.mock_mode:
            self._setup_gpio_pins()
    
    def _setup_gpio_pins(self):
        """Setup GPIO pins for sensors."""
        try:
            for sensor_name, sensor_config in self.sensors.items():
                if sensor_config['type'] == 'ultrasonic':
                    GPIO.setup(sensor_config['trigger_pin'], GPIO.OUT)
                    GPIO.setup(sensor_config['echo_pin'], GPIO.IN)
                    GPIO.output(sensor_config['trigger_pin'], False)
                    
            logger.info("GPIO pins configured for sensors")
            
        except Exception as e:
            logger.error(f"Failed to setup GPIO pins: {e}")
            self.mock_mode = True
    
    async def start(self):
        """Start sensor monitoring."""
        self.running = True
        
        # Start sensor reading loop
        asyncio.create_task(self._sensor_loop())
        
        logger.info("Sensor monitoring started")
    
    async def _sensor_loop(self):
        """Main sensor reading loop."""
        while self.running:
            try:
                # Read all sensors
                await self._read_all_sensors()
                
                # Control reading frequency
                await asyncio.sleep(0.1)  # 10Hz sensor updates
                
            except Exception as e:
                logger.error(f"Error in sensor loop: {e}")
                await asyncio.sleep(1)
    
    async def _read_all_sensors(self):
        """Read data from all sensors."""
        for sensor_name, sensor_config in self.sensors.items():
            try:
                if sensor_config['type'] == 'ultrasonic':
                    distance = await self._read_ultrasonic(sensor_config)
                    self.sensor_data[sensor_name] = {
                        'distance': distance,
                        'timestamp': datetime.now(),
                        'unit': 'cm'
                    }
                
                elif sensor_config['type'] == 'temperature':
                    temp, humidity = await self._read_temperature(sensor_config)
                    self.sensor_data[sensor_name] = {
                        'temperature': temp,
                        'humidity': humidity,
                        'timestamp': datetime.now(),
                        'unit': 'celsius'
                    }
                
                elif sensor_config['type'] == 'voltage':
                    voltage = await self._read_voltage(sensor_config)
                    self.sensor_data[sensor_name] = {
                        'voltage': voltage,
                        'timestamp': datetime.now(),
                        'unit': 'volts'
                    }
                    
            except Exception as e:
                logger.error(f"Error reading sensor {sensor_name}: {e}")
    
    async def _read_ultrasonic(self, sensor_config: Dict) -> float:
        """Read ultrasonic sensor distance.
        
        Args:
            sensor_config: Sensor configuration
            
        Returns:
            float: Distance in centimeters
        """
        if self.mock_mode:
            import random
            return random.uniform(10, 200)  # Mock distance
        
        try:
            import time
            
            trigger_pin = sensor_config['trigger_pin']
            echo_pin = sensor_config['echo_pin']
            
            # Send trigger pulse
            GPIO.output(trigger_pin, True)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(trigger_pin, False)
            
            # Wait for echo start
            pulse_start = time.time()
            while GPIO.input(echo_pin) == 0:
                pulse_start = time.time()
                if time.time() - pulse_start > 0.1:  # Timeout
                    return sensor_config['max_distance']
            
            # Wait for echo end
            pulse_end = time.time()
            while GPIO.input(echo_pin) == 1:
                pulse_end = time.time()
                if pulse_end - pulse_start > 0.1:  # Timeout
                    return sensor_config['max_distance']
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound calculation
            
            return min(distance, sensor_config['max_distance'])
            
        except Exception as e:
            logger.error(f"Error reading ultrasonic sensor: {e}")
            return sensor_config['max_distance']
    
    async def _read_temperature(self, sensor_config: Dict) -> tuple:
        """Read temperature and humidity sensor.
        
        Args:
            sensor_config: Sensor configuration
            
        Returns:
            tuple: (temperature, humidity)
        """
        if self.mock_mode:
            import random
            return random.uniform(20, 35), random.uniform(40, 80)
        
        try:
            # For DHT22 sensor (requires Adafruit library)
            # This is a placeholder - actual implementation would use Adafruit_DHT
            temperature = 25.0  # Placeholder
            humidity = 60.0     # Placeholder
            
            return temperature, humidity
            
        except Exception as e:
            logger.error(f"Error reading temperature sensor: {e}")
            return 0.0, 0.0
    
    async def _read_voltage(self, sensor_config: Dict) -> float:
        """Read voltage sensor (battery monitoring).
        
        Args:
            sensor_config: Sensor configuration
            
        Returns:
            float: Voltage reading
        """
        if self.mock_mode:
            import random
            return random.uniform(11.0, 12.6)  # Mock battery voltage
        
        try:
            # For MCP3008 ADC or similar
            # This is a placeholder - actual implementation would use SPI/ADC library
            raw_value = 512  # Placeholder ADC reading (0-1023)
            voltage = (raw_value / 1023.0) * 3.3 * sensor_config['voltage_divider_ratio']
            
            return voltage
            
        except Exception as e:
            logger.error(f"Error reading voltage sensor: {e}")
            return 0.0
    
    async def get_latest_data(self) -> Dict:
        """Get latest sensor data.
        
        Returns:
            Dict: Latest sensor readings
        """
        return self.sensor_data.copy()
    
    async def get_sensor_by_name(self, sensor_name: str) -> Optional[Dict]:
        """Get data from specific sensor.
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            Optional[Dict]: Sensor data or None
        """
        return self.sensor_data.get(sensor_name)
    
    async def get_obstacle_distances(self) -> Dict:
        """Get obstacle detection distances.
        
        Returns:
            Dict: Distances from ultrasonic sensors
        """
        obstacles = {}
        
        for sensor_name, data in self.sensor_data.items():
            if 'ultrasonic' in sensor_name and 'distance' in data:
                direction = sensor_name.replace('ultrasonic_', '')
                obstacles[direction] = data['distance']
        
        return obstacles
    
    async def check_obstacles(self, safe_distance: float = 50.0) -> Dict:
        """Check for obstacles within safe distance.
        
        Args:
            safe_distance: Safe distance threshold in cm
            
        Returns:
            Dict: Obstacle warning information
        """
        obstacles = await self.get_obstacle_distances()
        warnings = {}
        
        for direction, distance in obstacles.items():
            if distance < safe_distance:
                warnings[direction] = {
                    'distance': distance,
                    'safe_distance': safe_distance,
                    'warning': True
                }
        
        return warnings
    
    async def get_system_temperature(self) -> Optional[float]:
        """Get system temperature.
        
        Returns:
            Optional[float]: Temperature in Celsius
        """
        temp_data = self.sensor_data.get('temperature')
        if temp_data and 'temperature' in temp_data:
            return temp_data['temperature']
        return None
    
    async def get_battery_voltage(self) -> Optional[float]:
        """Get battery voltage.
        
        Returns:
            Optional[float]: Battery voltage
        """
        voltage_data = self.sensor_data.get('battery_voltage')
        if voltage_data and 'voltage' in voltage_data:
            return voltage_data['voltage']
        return None
    
    async def get_battery_percentage(self) -> Optional[float]:
        """Estimate battery percentage from voltage.
        
        Returns:
            Optional[float]: Battery percentage (0-100)
        """
        voltage = await self.get_battery_voltage()
        if voltage is None:
            return None
        
        # LiPo battery voltage to percentage mapping (approximate)
        voltage_map = {
            12.6: 100,  # 4.2V per cell * 3 cells
            12.0: 80,
            11.4: 60,
            11.1: 40,
            10.8: 20,
            10.5: 0
        }
        
        # Linear interpolation
        voltages = sorted(voltage_map.keys())
        
        if voltage >= voltages[-1]:
            return 100.0
        if voltage <= voltages[0]:
            return 0.0
        
        for i in range(len(voltages) - 1):
            if voltages[i] <= voltage <= voltages[i + 1]:
                v1, v2 = voltages[i], voltages[i + 1]
                p1, p2 = voltage_map[v1], voltage_map[v2]
                
                # Linear interpolation
                percentage = p1 + (voltage - v1) * (p2 - p1) / (v2 - v1)
                return max(0, min(100, percentage))
        
        return 50.0  # Default fallback
    
    async def get_sensor_health(self) -> Dict:
        """Get health status of all sensors.
        
        Returns:
            Dict: Health status for each sensor
        """
        health = {}
        current_time = datetime.now()
        
        for sensor_name, data in self.sensor_data.items():
            if 'timestamp' in data:
                time_diff = (current_time - data['timestamp']).total_seconds()
                health[sensor_name] = {
                    'healthy': time_diff < 5.0,  # Data less than 5 seconds old
                    'last_update': data['timestamp'].isoformat(),
                    'time_since_update': time_diff
                }
            else:
                health[sensor_name] = {
                    'healthy': False,
                    'last_update': None,
                    'time_since_update': float('inf')
                }
        
        return health
    
    async def calibrate_sensors(self) -> Dict:
        """Calibrate sensors if needed.
        
        Returns:
            Dict: Calibration results
        """
        results = {}
        
        # Calibrate ultrasonic sensors (zero distance check)
        for sensor_name, sensor_config in self.sensors.items():
            if sensor_config['type'] == 'ultrasonic':
                try:
                    distances = []
                    for _ in range(10):  # Take 10 readings
                        distance = await self._read_ultrasonic(sensor_config)
                        distances.append(distance)
                        await asyncio.sleep(0.1)
                    
                    avg_distance = sum(distances) / len(distances)
                    std_dev = (sum((d - avg_distance) ** 2 for d in distances) / len(distances)) ** 0.5
                    
                    results[sensor_name] = {
                        'average_distance': avg_distance,
                        'standard_deviation': std_dev,
                        'readings': distances,
                        'calibrated': std_dev < 5.0  # Good if std dev < 5cm
                    }
                    
                except Exception as e:
                    results[sensor_name] = {
                        'error': str(e),
                        'calibrated': False
                    }
        
        return results
    
    async def is_healthy(self) -> bool:
        """Check if sensor manager is healthy.
        
        Returns:
            bool: Health status
        """
        if not self.sensor_data:
            return False
        
        # Check if at least some sensors are providing recent data
        current_time = datetime.now()
        healthy_sensors = 0
        
        for data in self.sensor_data.values():
            if 'timestamp' in data:
                time_diff = (current_time - data['timestamp']).total_seconds()
                if time_diff < 10.0:  # Data less than 10 seconds old
                    healthy_sensors += 1
        
        return healthy_sensors > 0
    
    async def stop(self):
        """Stop sensor manager and cleanup resources."""
        try:
            self.running = False
            
            if not self.mock_mode and GPIO_AVAILABLE:
                GPIO.cleanup()
            
            logger.info("Sensor manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping sensor manager: {e}")
