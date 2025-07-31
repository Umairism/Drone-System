"""
Configuration Manager
Handles loading and managing system configuration.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages system configuration from YAML files and environment variables."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files and environment variables."""
        try:
            # Load main drone configuration
            drone_config_path = self.config_dir / "drone_config.yaml"
            if drone_config_path.exists():
                with open(drone_config_path, 'r') as f:
                    self.config['drone'] = yaml.safe_load(f)
            else:
                self.config['drone'] = self._get_default_drone_config()
                self._save_default_config(drone_config_path, self.config['drone'])
            
            # Load camera configuration
            camera_config_path = self.config_dir / "camera_config.yaml"
            if camera_config_path.exists():
                with open(camera_config_path, 'r') as f:
                    self.config['camera'] = yaml.safe_load(f)
            else:
                self.config['camera'] = self._get_default_camera_config()
                self._save_default_config(camera_config_path, self.config['camera'])
            
            # Override with environment variables
            self._load_env_overrides()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_drone_config(self) -> Dict[str, Any]:
        """Get default drone configuration."""
        return {
            'drone': {
                'name': 'SurvDrone-001',
                'type': 'quadcopter',
                'max_altitude': 120,
                'max_speed': 15,
                'battery_capacity': 5000
            },
            'flight_controller': {
                'type': 'pixhawk4',
                'firmware': 'arducopter',
                'failsafe_enabled': True,
                'return_to_home': True
            },
            'sensors': {
                'gps': {
                    'enabled': True,
                    'update_rate': 10
                },
                'camera': {
                    'enabled': True,
                    'resolution': [1920, 1080],
                    'fps': 30
                },
                'ultrasonic': {
                    'enabled': True,
                    'max_range': 400
                }
            },
            'geofence': {
                'enabled': True,
                'radius': 1000,
                'max_altitude': 120
            }
        }
    
    def _get_default_camera_config(self) -> Dict[str, Any]:
        """Get default camera configuration."""
        return {
            'camera': {
                'device_id': 0,
                'resolution': {
                    'width': 1920,
                    'height': 1080
                },
                'fps': 30,
                'quality': 'high',
                'auto_exposure': True,
                'auto_white_balance': True
            },
            'streaming': {
                'enabled': True,
                'format': 'mjpeg',
                'quality': 85,
                'bitrate': 2500000
            },
            'recording': {
                'enabled': True,
                'format': 'mp4',
                'codec': 'h264',
                'path': 'data/recordings/'
            }
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get complete default configuration."""
        config = {}
        config.update(self._get_default_drone_config())
        config.update(self._get_default_camera_config())
        return config
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        # Drone settings
        if os.getenv('DRONE_MAX_ALTITUDE'):
            self.config['drone']['drone']['max_altitude'] = int(os.getenv('DRONE_MAX_ALTITUDE'))
        
        if os.getenv('DRONE_MAX_SPEED'):
            self.config['drone']['drone']['max_speed'] = int(os.getenv('DRONE_MAX_SPEED'))
        
        # Camera settings
        if os.getenv('CAMERA_RESOLUTION'):
            width, height = map(int, os.getenv('CAMERA_RESOLUTION').split('x'))
            self.config['camera']['camera']['resolution'] = {'width': width, 'height': height}
        
        if os.getenv('CAMERA_FPS'):
            self.config['camera']['camera']['fps'] = int(os.getenv('CAMERA_FPS'))
        
        # GPS settings
        if os.getenv('GPS_UPDATE_RATE'):
            self.config['drone']['sensors']['gps']['update_rate'] = int(os.getenv('GPS_UPDATE_RATE'))
    
    def _save_default_config(self, file_path: Path, config_data: Dict):
        """Save default configuration to file.
        
        Args:
            file_path: Path to save configuration file
            config_data: Configuration data to save
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            logger.info(f"Default configuration saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save default configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (dot-separated for nested values)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested values)
            value: Value to set
        """
        keys = key.split('.')
        config_dict = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config_dict:
                config_dict[k] = {}
            config_dict = config_dict[k]
        
        # Set the value
        config_dict[keys[-1]] = value
    
    def get_drone_config(self) -> Dict[str, Any]:
        """Get drone configuration.
        
        Returns:
            Dict: Drone configuration
        """
        return self.config.get('drone', {})
    
    def get_camera_config(self) -> Dict[str, Any]:
        """Get camera configuration.
        
        Returns:
            Dict: Camera configuration
        """
        return self.config.get('camera', {})
    
    def get_flight_limits(self) -> Dict[str, Any]:
        """Get flight limitation settings.
        
        Returns:
            Dict: Flight limits
        """
        drone_config = self.get_drone_config()
        geofence = drone_config.get('geofence', {})
        
        return {
            'max_altitude': drone_config.get('drone', {}).get('max_altitude', 120),
            'max_speed': drone_config.get('drone', {}).get('max_speed', 15),
            'geofence_enabled': geofence.get('enabled', True),
            'geofence_radius': geofence.get('radius', 1000),
            'geofence_max_altitude': geofence.get('max_altitude', 120)
        }
    
    def reload(self):
        """Reload configuration from files."""
        logger.info("Reloading configuration...")
        self._load_config()
    
    def save_config(self, config_name: str):
        """Save current configuration to file.
        
        Args:
            config_name: Name of configuration section to save
        """
        try:
            if config_name in self.config:
                file_path = self.config_dir / f"{config_name}_config.yaml"
                self._save_default_config(file_path, self.config[config_name])
                logger.info(f"Configuration '{config_name}' saved to {file_path}")
            else:
                logger.error(f"Configuration section '{config_name}' not found")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
