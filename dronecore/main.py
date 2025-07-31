# Surveillance Drone System - Core Module
"""
Main entry point for the surveillance drone system.
Initializes all subsystems and starts the main control loop.
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from flight_controller import DroneController
from video_stream import VideoStreamer
from object_detection import ObjectDetector
from gps_tracker import GPSTracker
from sensor_manager import SensorManager  
from communication import CommunicationManager
from config.config_manager import ConfigManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/drone_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DroneSystem:
    """Main drone system coordinator."""
    
    def __init__(self):
        """Initialize all system components."""
        logger.info("Initializing Surveillance Drone System...")
        
        self.config = ConfigManager()
        self.running = False
        self.components = {}
        
        # Initialize system components
        self._init_components()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _init_components(self):
        """Initialize all drone system components."""
        try:
            # Flight controller
            self.components['flight_controller'] = DroneController(
                port=os.getenv('MAVLINK_PORT', '/dev/ttyUSB0'),
                baudrate=int(os.getenv('MAVLINK_BAUDRATE', 57600))
            )
            
            # GPS tracker
            self.components['gps_tracker'] = GPSTracker(
                port=os.getenv('GPS_PORT', '/dev/ttyACM0'),
                baudrate=int(os.getenv('GPS_BAUDRATE', 9600))
            )
            
            # Video streaming
            self.components['video_streamer'] = VideoStreamer(
                camera_id=int(os.getenv('CAMERA_DEVICE', 0)),
                resolution=tuple(map(int, os.getenv('CAMERA_RESOLUTION', '1920x1080').split('x'))),
                fps=int(os.getenv('CAMERA_FPS', 30))
            )
            
            # Object detection
            self.components['object_detector'] = ObjectDetector(
                model_name=os.getenv('DETECTION_MODEL', 'yolov8n'),
                confidence_threshold=float(os.getenv('CONFIDENCE_THRESHOLD', 0.5)),
                device=os.getenv('DETECTION_DEVICE', 'cpu')
            )
            
            # Sensor manager
            self.components['sensor_manager'] = SensorManager()
            
            # Communication manager
            self.components['communication'] = CommunicationManager(
                port=int(os.getenv('SOCKET_PORT', 5001))
            )
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def start(self):
        """Start the drone system."""
        logger.info("Starting Surveillance Drone System...")
        self.running = True
        
        try:
            # Start all components
            tasks = []
            for name, component in self.components.items():
                if hasattr(component, 'start'):
                    task = asyncio.create_task(component.start())
                    tasks.append(task)
                    logger.info(f"Started {name}")
            
            # Main control loop
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Error in main system: {e}")
            await self.stop()
            
    async def _main_loop(self):
        """Main system control loop."""
        logger.info("Entering main control loop...")
        
        while self.running:
            try:
                # System health check
                await self._health_check()
                
                # Process sensor data
                await self._process_sensor_data()
                
                # Handle object detection
                await self._process_object_detection()
                
                # Update telemetry
                await self._update_telemetry()
                
                # Sleep to prevent excessive CPU usage
                await asyncio.sleep(0.1)  # 10Hz main loop
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)  # Prevent rapid error loops
    
    async def _health_check(self):
        """Perform system health checks."""
        # Check component status
        for name, component in self.components.items():
            if hasattr(component, 'is_healthy'):
                if not await component.is_healthy():
                    logger.warning(f"Component {name} is not healthy")
    
    async def _process_sensor_data(self):
        """Process data from all sensors."""
        sensor_data = await self.components['sensor_manager'].get_latest_data()
        
        # Process GPS data
        if 'gps' in sensor_data:
            gps_data = sensor_data['gps']
            await self.components['flight_controller'].update_position(gps_data)
        
        # Process other sensor data as needed
        
    async def _process_object_detection(self):
        """Process object detection from video stream."""
        if self.components['video_streamer'].has_new_frame():
            frame = await self.components['video_streamer'].get_latest_frame()
            detections = await self.components['object_detector'].detect(frame)
            
            if detections:
                logger.info(f"Detected {len(detections)} objects")
                # Send detections to communication manager
                await self.components['communication'].broadcast_detections(detections)
    
    async def _update_telemetry(self):
        """Update and broadcast telemetry data."""
        telemetry = {
            'timestamp': datetime.now().isoformat(),
            'flight_data': await self.components['flight_controller'].get_telemetry(),
            'gps_data': await self.components['gps_tracker'].get_position(),
            'sensor_data': await self.components['sensor_manager'].get_latest_data(),
            'system_status': self._get_system_status()
        }
        
        await self.components['communication'].broadcast_telemetry(telemetry)
    
    def _get_system_status(self):
        """Get overall system status."""
        return {
            'running': self.running,
            'uptime': self._get_uptime(),
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'temperature': self._get_system_temperature()
        }
    
    def _get_uptime(self):
        """Get system uptime."""
        # Implementation depends on system
        return "00:00:00"
    
    def _get_cpu_usage(self):
        """Get CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0
    
    def _get_memory_usage(self):
        """Get memory usage percentage."""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0
    
    def _get_system_temperature(self):
        """Get system temperature."""
        try:
            # For Raspberry Pi
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000.0
                return temp
        except:
            return 0
    
    async def stop(self):
        """Stop the drone system gracefully."""
        logger.info("Stopping Surveillance Drone System...")
        self.running = False
        
        # Stop all components
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                try:
                    await component.stop()
                    logger.info(f"Stopped {name}")
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")
        
        logger.info("System stopped successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.stop())

async def main():
    """Main entry point."""
    try:
        # Create and start the drone system
        drone_system = DroneSystem()
        await drone_system.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/recordings", exist_ok=True)
    
    # Run the main system
    asyncio.run(main())
