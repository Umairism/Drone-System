#!/usr/bin/env python3
"""
Pre-flight Check Script
Performs comprehensive system checks before flight operations.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PreflightChecker:
    """Performs comprehensive pre-flight system checks."""
    
    def __init__(self):
        """Initialize preflight checker."""
        self.checks = []
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'checks': []
        }
    
    async def run_all_checks(self):
        """Run all preflight checks."""
        logger.info("Starting pre-flight system checks...")
        
        # System checks
        await self.check_system_requirements()
        await self.check_environment_variables()
        await self.check_file_structure()
        await self.check_permissions()
        
        # Hardware checks
        await self.check_hardware_connections()
        await self.check_camera()
        await self.check_gps()
        
        # Software checks
        await self.check_dependencies()
        await self.check_configuration()
        await self.check_database()
        
        # Safety checks
        await self.check_flight_safety()
        await self.check_geofence()
        
        # Generate report
        self.generate_report()
        
        return self.results
    
    async def check_system_requirements(self):
        """Check system requirements."""
        await self.run_check(
            "System Requirements",
            self._check_system_requirements,
            "Verify minimum system requirements are met"
        )
    
    async def _check_system_requirements(self):
        """Check if system meets minimum requirements."""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check available disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(PROJECT_ROOT)
            free_gb = free // (1024**3)
            if free_gb < 5:
                issues.append(f"Low disk space: {free_gb}GB available (5GB+ recommended)")
        except Exception as e:
            issues.append(f"Could not check disk space: {e}")
        
        # Check memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.total < 4 * 1024**3:  # 4GB
                issues.append(f"Low RAM: {memory.total // 1024**3}GB (4GB+ recommended)")
        except ImportError:
            issues.append("Could not check system memory (psutil not installed)")
        
        return issues
    
    async def check_environment_variables(self):
        """Check required environment variables."""
        await self.run_check(
            "Environment Variables",
            self._check_environment_variables,
            "Verify all required environment variables are set"
        )
    
    async def _check_environment_variables(self):
        """Check if required environment variables are set."""
        required_vars = [
            'SECRET_KEY',
            'MAVLINK_PORT',
            'GPS_PORT',
            'CAMERA_DEVICE'
        ]
        
        issues = []
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Missing environment variable: {var}")
        
        return issues
    
    async def check_file_structure(self):
        """Check project file structure."""
        await self.run_check(
            "File Structure",
            self._check_file_structure,
            "Verify all required files and directories exist"
        )
    
    async def _check_file_structure(self):
        """Check if required files and directories exist."""
        required_items = [
            'dronecore/main.py',
            'dronecore/flight_controller.py',
            'dronecore/video_stream.py',
            'dronecore/object_detection.py',
            'dronecore/gps_tracker.py',
            'dronecore/config/',
            'logs/',
            'data/',
            'requirements.txt'
        ]
        
        issues = []
        for item in required_items:
            path = PROJECT_ROOT / item
            if not path.exists():
                issues.append(f"Missing required item: {item}")
        
        return issues
    
    async def check_permissions(self):
        """Check file permissions."""
        await self.run_check(
            "Permissions",
            self._check_permissions,
            "Verify required file and directory permissions"
        )
    
    async def _check_permissions(self):
        """Check file and directory permissions."""
        issues = []
        
        # Check write permissions for important directories
        write_dirs = ['logs', 'data', 'data/recordings']
        
        for dir_name in write_dirs:
            dir_path = PROJECT_ROOT / dir_name
            if dir_path.exists():
                if not os.access(dir_path, os.W_OK):
                    issues.append(f"No write permission for directory: {dir_name}")
            else:
                # Try to create the directory
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    issues.append(f"Cannot create directory: {dir_name}")
        
        # Check execute permission for scripts
        script_files = ['scripts/init_db.py']
        for script in script_files:
            script_path = PROJECT_ROOT / script
            if script_path.exists() and not os.access(script_path, os.X_OK):
                issues.append(f"No execute permission for script: {script}")
        
        return issues
    
    async def check_hardware_connections(self):
        """Check hardware connections."""
        await self.run_check(
            "Hardware Connections",
            self._check_hardware_connections,
            "Test connections to hardware components"
        )
    
    async def _check_hardware_connections(self):
        """Check hardware device connections."""
        issues = []
        
        # Check serial ports
        mavlink_port = os.getenv('MAVLINK_PORT', '/dev/ttyUSB0')
        gps_port = os.getenv('GPS_PORT', '/dev/ttyACM0')
        
        for port_name, port_path in [('MAVLink', mavlink_port), ('GPS', gps_port)]:
            if not Path(port_path).exists():
                issues.append(f"{port_name} port not found: {port_path}")
        
        # Check GPIO availability (Raspberry Pi)
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.cleanup()
        except ImportError:
            issues.append("RPi.GPIO not available (not running on Raspberry Pi)")
        except Exception as e:
            issues.append(f"GPIO check failed: {e}")
        
        return issues
    
    async def check_camera(self):
        """Check camera functionality."""
        await self.run_check(
            "Camera",
            self._check_camera,
            "Test camera initialization and functionality"
        )
    
    async def _check_camera(self):
        """Check camera device."""
        issues = []
        
        try:
            import cv2
            camera_id = int(os.getenv('CAMERA_DEVICE', 0))
            
            # Try to open camera
            cap = cv2.VideoCapture(camera_id)
            if not cap.isOpened():
                issues.append(f"Cannot open camera device: {camera_id}")
            else:
                # Test frame capture
                ret, frame = cap.read()
                if not ret:
                    issues.append("Camera opened but cannot capture frames")
                cap.release()
                
        except ImportError:
            issues.append("OpenCV not available for camera testing")
        except Exception as e:
            issues.append(f"Camera check failed: {e}")
        
        return issues
    
    async def check_gps(self):
        """Check GPS functionality."""
        await self.run_check(
            "GPS Module",
            self._check_gps,
            "Test GPS module communication"
        )
    
    async def _check_gps(self):
        """Check GPS module."""
        issues = []
        
        try:
            import serial
            gps_port = os.getenv('GPS_PORT', '/dev/ttyACM0')
            gps_baudrate = int(os.getenv('GPS_BAUDRATE', 9600))
            
            # Try to open GPS serial connection
            ser = serial.Serial(gps_port, gps_baudrate, timeout=2)
            
            # Read a few lines to test communication
            for _ in range(5):
                line = ser.readline().decode('ascii', errors='ignore')
                if line.startswith('$'):
                    break
            else:
                issues.append("GPS module not responding with NMEA data")
            
            ser.close()
            
        except ImportError:
            issues.append("pyserial not available for GPS testing")
        except serial.SerialException as e:
            issues.append(f"GPS serial connection failed: {e}")
        except Exception as e:
            issues.append(f"GPS check failed: {e}")
        
        return issues
    
    async def check_dependencies(self):
        """Check Python dependencies."""
        await self.run_check(
            "Dependencies",
            self._check_dependencies,
            "Verify all required Python packages are installed"
        )
    
    async def _check_dependencies(self):
        """Check Python package dependencies."""
        issues = []
        
        required_packages = [
            'opencv-python',
            'numpy',
            'flask',
            'flask-socketio',
            'pyserial',
            'pyyaml',
            'asyncio'
        ]
        
        for package in required_packages:
            try:
                if package == 'opencv-python':
                    import cv2
                elif package == 'flask-socketio':
                    import socketio
                else:
                    __import__(package.replace('-', '_'))
            except ImportError:
                issues.append(f"Missing required package: {package}")
        
        return issues
    
    async def check_configuration(self):
        """Check configuration files."""
        await self.run_check(
            "Configuration",
            self._check_configuration,
            "Validate configuration files and settings"
        )
    
    async def _check_configuration(self):
        """Check configuration files."""
        issues = []
        
        config_files = [
            'dronecore/config/drone_config.yaml',
            'dronecore/config/camera_config.yaml'
        ]
        
        for config_file in config_files:
            config_path = PROJECT_ROOT / config_file
            if not config_path.exists():
                issues.append(f"Missing configuration file: {config_file}")
            else:
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    issues.append(f"Invalid YAML in {config_file}: {e}")
                except Exception as e:
                    issues.append(f"Cannot read {config_file}: {e}")
        
        return issues
    
    async def check_database(self):
        """Check database connectivity."""
        await self.run_check(
            "Database",
            self._check_database,
            "Test database connection and schema"
        )
    
    async def _check_database(self):
        """Check database setup."""
        issues = []
        
        try:
            import sqlite3
            db_path = PROJECT_ROOT / "data" / "drone_data.db"
            
            if not db_path.exists():
                issues.append("Database file not found. Run 'python scripts/init_db.py' first.")
            else:
                # Test database connection
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['flight_logs', 'telemetry', 'detections', 'missions']
                for table in required_tables:
                    if table not in tables:
                        issues.append(f"Missing database table: {table}")
                
                conn.close()
                
        except Exception as e:
            issues.append(f"Database check failed: {e}")
        
        return issues
    
    async def check_flight_safety(self):
        """Check flight safety parameters."""
        await self.run_check(
            "Flight Safety",
            self._check_flight_safety,
            "Verify flight safety parameters and limits"
        )
    
    async def _check_flight_safety(self):
        """Check flight safety configuration."""
        issues = []
        
        # Check altitude limits
        max_altitude = int(os.getenv('MAX_ALTITUDE', 120))
        if max_altitude > 400:  # FAA limit in many countries
            issues.append(f"Max altitude {max_altitude}m exceeds recommended limit (120m)")
        
        # Check speed limits
        max_speed = int(os.getenv('MAX_SPEED', 15))
        if max_speed > 25:  # Reasonable safety limit
            issues.append(f"Max speed {max_speed}m/s may be unsafe")
        
        # Check failsafe settings
        if not os.getenv('FAILSAFE_ENABLED', 'true').lower() == 'true':
            issues.append("Failsafe is disabled - this is unsafe")
        
        return issues
    
    async def check_geofence(self):
        """Check geofence configuration."""
        await self.run_check(
            "Geofence",
            self._check_geofence,
            "Verify geofence boundaries and safety zones"
        )
    
    async def _check_geofence(self):
        """Check geofence settings."""
        issues = []
        
        if not os.getenv('GEOFENCE_ENABLED', 'true').lower() == 'true':
            issues.append("Geofence is disabled - this is unsafe")
        
        geofence_radius = int(os.getenv('GEOFENCE_RADIUS', 1000))
        if geofence_radius > 5000:  # 5km
            issues.append(f"Geofence radius {geofence_radius}m is very large")
        
        # Check home position is set
        home_lat = os.getenv('HOME_LATITUDE')
        home_lng = os.getenv('HOME_LONGITUDE')
        
        if not home_lat or not home_lng:
            issues.append("Home position not configured")
        else:
            try:
                lat = float(home_lat)
                lng = float(home_lng)
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    issues.append("Invalid home position coordinates")
            except ValueError:
                issues.append("Invalid home position format")
        
        return issues
    
    async def run_check(self, name: str, check_func, description: str):
        """Run a single check and record results."""
        logger.info(f"Running check: {name}")
        
        start_time = datetime.now()
        try:
            issues = await check_func()
            duration = (datetime.now() - start_time).total_seconds()
            
            if not issues:
                status = "PASS"
                self.results['passed'] += 1
                logger.info(f"✓ {name}: PASSED")
            else:
                # Determine if issues are warnings or failures
                critical_keywords = ['failed', 'missing', 'cannot', 'not found', 'error']
                has_critical = any(any(keyword in issue.lower() for keyword in critical_keywords) 
                                 for issue in issues)
                
                if has_critical:
                    status = "FAIL"
                    self.results['failed'] += 1
                    logger.error(f"✗ {name}: FAILED")
                else:
                    status = "WARN"
                    self.results['warnings'] += 1
                    logger.warning(f"⚠ {name}: WARNING")
                
                for issue in issues:
                    logger.warning(f"  - {issue}")
            
            self.results['checks'].append({
                'name': name,
                'description': description,
                'status': status,
                'issues': issues,
                'duration': duration,
                'timestamp': start_time.isoformat()
            })
            
        except Exception as e:
            logger.error(f"✗ {name}: ERROR - {e}")
            self.results['failed'] += 1
            self.results['checks'].append({
                'name': name,
                'description': description,
                'status': 'ERROR',
                'issues': [f"Check failed with exception: {e}"],
                'duration': (datetime.now() - start_time).total_seconds(),
                'timestamp': start_time.isoformat()
            })
    
    def generate_report(self):
        """Generate and save preflight check report."""
        total_checks = self.results['passed'] + self.results['failed'] + self.results['warnings']
        
        # Console summary
        print("\n" + "="*60)
        print("PRE-FLIGHT CHECK SUMMARY")
        print("="*60)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {self.results['passed']}")
        print(f"Warnings: {self.results['warnings']}")
        print(f"Failed: {self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n⚠️  FLIGHT NOT RECOMMENDED - Critical issues found")
            print("Please resolve all failed checks before flight operations.")
        elif self.results['warnings'] > 0:
            print("\n⚠️  FLIGHT POSSIBLE WITH CAUTION - Warnings present")
            print("Review warnings and proceed with caution.")
        else:
            print("\n✅ FLIGHT CLEARED - All checks passed")
        
        # Save detailed report
        report_path = PROJECT_ROOT / "logs" / f"preflight_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")

async def main():
    """Main function."""
    checker = PreflightChecker()
    results = await checker.run_all_checks()
    
    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)  # Critical failures
    elif results['warnings'] > 0:
        sys.exit(2)  # Warnings present
    else:
        sys.exit(0)  # All clear

if __name__ == "__main__":
    asyncio.run(main())
