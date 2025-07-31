"""
Advanced Logging System for Surveillance Drone
Provides comprehensive logging with different log types and structured formats.
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum
import traceback


class LogType(Enum):
    """Log types for different system components."""
    SYSTEM = "system"
    FLIGHT = "flight"
    MISSION = "mission"
    ERROR = "error"
    SECURITY = "security"
    PERFORMANCE = "performance"
    API = "api"
    TELEMETRY = "telemetry"
    VIDEO = "video"
    GPS = "gps"
    DETECTION = "detection"
    USER = "user"


class DroneLogger:
    """Advanced logging system for the surveillance drone."""
    
    def __init__(self, app=None):
        self.app = app
        self.logs_dir = Path("logs")
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_directories()
        self.loggers = {}
        self.setup_loggers()
    
    def setup_directories(self):
        """Create all necessary log directories."""
        directories = [
            self.logs_dir,
            self.logs_dir / "flight_logs",
            self.logs_dir / "error_logs",
            self.logs_dir / "mission_logs",
            self.logs_dir / "performance_logs",
            self.logs_dir / "security_logs",
            self.logs_dir / "api_logs",
            self.logs_dir / "telemetry_logs",
            self.logs_dir / "achievements"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def setup_loggers(self):
        """Setup specialized loggers for different components."""
        for log_type in LogType:
            logger = logging.getLogger(f"drone.{log_type.value}")
            logger.setLevel(logging.DEBUG)
            
            # Remove existing handlers
            logger.handlers.clear()
            
            # Create directory for this log type if it doesn't exist
            log_dir = self.logs_dir / f"{log_type.value}_logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # File handler for each log type
            log_file = log_dir / f"{log_type.value}_{self.session_id}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            # JSON formatter for structured logging
            formatter = JsonFormatter()
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Console handler for development
            if self.app and self.app.debug:
                console_handler = logging.StreamHandler()
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)
            
            self.loggers[log_type] = logger
    
    def log(self, log_type: LogType, level: str, message: str, 
           extra_data: Dict[str, Any] = None, user_id: str = None):
        """Log a message with structured data."""
        logger = self.loggers.get(log_type)
        if not logger:
            return
        
        # Prepare log data
        log_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "log_type": log_type.value,
            "message": message,
            "user_id": user_id,
            "extra_data": extra_data or {}
        }
        
        # Log based on level
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, json.dumps(log_data))
    
    def log_flight_event(self, event: str, drone_status: Dict[str, Any], 
                        user_id: str = None):
        """Log flight-related events."""
        self.log(
            LogType.FLIGHT,
            "INFO",
            f"Flight Event: {event}",
            extra_data={
                "event": event,
                "drone_status": drone_status,
                "flight_time": drone_status.get("flight_time", 0),
                "battery_level": drone_status.get("battery_level"),
                "altitude": drone_status.get("altitude"),
                "location": drone_status.get("location")
            },
            user_id=user_id
        )
    
    def log_mission_event(self, mission_id: str, event: str, 
                         mission_data: Dict[str, Any], user_id: str = None):
        """Log mission-related events."""
        self.log(
            LogType.MISSION,
            "INFO",
            f"Mission {mission_id}: {event}",
            extra_data={
                "mission_id": mission_id,
                "event": event,
                "mission_data": mission_data
            },
            user_id=user_id
        )
    
    def log_error(self, error: Exception, context: str = None, 
                  user_id: str = None):
        """Log errors with full traceback."""
        self.log(
            LogType.ERROR,
            "ERROR",
            f"Error in {context}: {str(error)}",
            extra_data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context
            },
            user_id=user_id
        )
    
    def log_api_request(self, method: str, endpoint: str, 
                       user_id: str = None, response_code: int = None,
                       response_time: float = None):
        """Log API requests."""
        self.log(
            LogType.API,
            "INFO",
            f"{method} {endpoint}",
            extra_data={
                "method": method,
                "endpoint": endpoint,
                "response_code": response_code,
                "response_time_ms": response_time
            },
            user_id=user_id
        )
    
    def log_telemetry(self, telemetry_data: Dict[str, Any]):
        """Log telemetry data."""
        self.log(
            LogType.TELEMETRY,
            "DEBUG",
            "Telemetry Update",
            extra_data=telemetry_data
        )
    
    def log_detection(self, detection_data: Dict[str, Any]):
        """Log object detection events."""
        self.log(
            LogType.DETECTION,
            "INFO",
            f"Objects detected: {len(detection_data.get('objects', []))}",
            extra_data=detection_data
        )
    
    def log_security_event(self, event: str, severity: str = "medium",
                          details: Dict[str, Any] = None, user_id: str = None):
        """Log security-related events."""
        self.log(
            LogType.SECURITY,
            "WARNING" if severity == "high" else "INFO",
            f"Security Event: {event}",
            extra_data={
                "event": event,
                "severity": severity,
                "details": details or {}
            },
            user_id=user_id
        )
    
    def log_performance(self, metric: str, value: float, unit: str = "ms"):
        """Log performance metrics."""
        self.log(
            LogType.PERFORMANCE,
            "INFO",
            f"Performance: {metric} = {value}{unit}",
            extra_data={
                "metric": metric,
                "value": value,
                "unit": unit
            }
        )
    
    def get_logs(self, log_type: LogType = None, 
                start_time: datetime = None, end_time: datetime = None,
                limit: int = 100):
        """Retrieve logs with filtering."""
        logs = []
        
        if log_type:
            log_types = [log_type]
        else:
            log_types = list(LogType)
        
        for lt in log_types:
            log_dir = self.logs_dir / f"{lt.value}_logs"
            if not log_dir.exists():
                continue
                
            for log_file in log_dir.glob(f"{lt.value}_*.log"):
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                log_time = datetime.fromisoformat(
                                    log_entry.get('timestamp', '').replace('Z', '+00:00')
                                )
                                
                                # Filter by time range
                                if start_time and log_time < start_time:
                                    continue
                                if end_time and log_time > end_time:
                                    continue
                                
                                logs.append(log_entry)
                                
                                if len(logs) >= limit:
                                    break
                            except (json.JSONDecodeError, ValueError):
                                continue
                except Exception:
                    continue
        
        # Sort by timestamp
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return logs[:limit]
    
    def get_log_summary(self):
        """Get summary statistics of logs."""
        summary = {
            "session_id": self.session_id,
            "total_logs": 0,
            "log_types": {},
            "error_count": 0,
            "recent_errors": []
        }
        
        for log_type in LogType:
            log_dir = self.logs_dir / f"{log_type.value}_logs"
            if not log_dir.exists():
                continue
            
            count = 0
            for log_file in log_dir.glob(f"{log_type.value}_*.log"):
                try:
                    with open(log_file, 'r') as f:
                        file_count = sum(1 for _ in f)
                        count += file_count
                except Exception:
                    continue
            
            summary["log_types"][log_type.value] = count
            summary["total_logs"] += count
            
            if log_type == LogType.ERROR:
                summary["error_count"] = count
                # Get recent errors
                recent_errors = self.get_logs(LogType.ERROR, limit=5)
                summary["recent_errors"] = [
                    {
                        "timestamp": err.get("timestamp"),
                        "message": err.get("message"),
                        "context": err.get("extra_data", {}).get("context")
                    }
                    for err in recent_errors
                ]
        
        return summary


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        try:
            # Try to parse message as JSON
            log_data = json.loads(record.getMessage())
        except (json.JSONDecodeError, ValueError):
            # If not JSON, create structured format
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
        
        return json.dumps(log_data, ensure_ascii=False)


# Global logger instance
drone_logger = None

def init_logger(app=None):
    """Initialize the global logger."""
    global drone_logger
    drone_logger = DroneLogger(app)
    return drone_logger

def get_logger():
    """Get the global logger instance."""
    return drone_logger
